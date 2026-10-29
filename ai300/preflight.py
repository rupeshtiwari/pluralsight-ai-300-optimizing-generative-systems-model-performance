"""Bounded read-only Azure prerequisite checks. Never an all-steps runtime PASS."""
from pathlib import Path
from .core import ROOT, Run, require, read, write, uid, now, consumed_config, validate_demo_spec
from .azure import Azure, resolve_environment, deployment_snapshot, course_endpoint
DEPENDENCIES={'m2-demo3':[('m2-demo2',3)],'m2-demo4':[('m2-demo3',3),('m2-demo2',3)],'m3-demo1':[('m2-demo4',3)],'m3-demo2':[('m3-demo1',3)],'m3-demo3':[('m3-demo2',3)],'m3-demo4':[('m3-demo3',3)]}
class ReadOnlyContext:
    dependency=Run.dependency
    def __init__(self,demo,config):
        self.demo=demo; self.config=config; self.spec=read(ROOT/'configs'/f'{demo}.json'); validate_demo_spec(demo,self.spec)
        self.path=ROOT/'evidence'/'preflight'/demo/uid(); self.path.mkdir(parents=True); self.attempt=self.path
        self.state={'run_id':self.path.name,'started_at':now()}
    def raw(self,name,value):
        path=self.path/'raw'/f'{name}-{uid()}.json'; write(path,value); return str(path)

def live_checks(demo,config):
    run=ReadOnlyContext(demo,config); a=Azure(run); checks=[]
    try:
        a.credential.get_token('https://management.azure.com/.default'); checks.append({'check':'management_identity','status':'OBSERVED'})
        fields=consumed_config(config,demo)
        if 'search_endpoint' in fields:
            service=a.arm('GET',config['search_resource_id'],version='2025-05-01'); require(service['sku']['name'].lower()=='free','Search service must use the approved Free tier.')
            indexes,_=a.search('indexes',method='GET'); present=any(i['name']==config['search_index'] for i in indexes['value'])
            require(present or len(indexes['value'])<3,'Free service has no free index slot. Free only the course-owned slot through your normal cleanup.')
            checks.append({'check':'search_read_access_free_sku','status':'OBSERVED','location':service['location'],'existing_indexes':len(indexes['value']),'course_index_present':present,'semantic_plan':service.get('properties',{}).get('semanticSearch'),'semantic_region_action':'Confirm explicit Free-tier semantic support in official region table; a real semantic query still must return reranker evidence.'})
        if 'foundry_deployment' in fields:
            deployment=a.arm('GET',config['foundry_resource_id']+'/deployments/'+config['foundry_deployment'],version='2024-10-01'); model=deployment['properties']['model']
            require(model['name']==config['foundry_model'] and model['version']==config['foundry_version'],'Foundry model/version mismatch.')
            checks.append({'check':'foundry_deployment_readback','status':'OBSERVED','model':model,'inference_permission':'NOT PROVED by management-plane read'})
        if 'training_environment' in fields:
            from azure.ai.ml.entities import AmlCompute
            compute=a.ml.compute.get(config['cpu_compute']); require(isinstance(compute,AmlCompute),'AmlCompute CPU cluster required.')
            require(compute.size and not any(x in compute.size.upper() for x in ('STANDARD_N','GPU')),'CPU cluster required.')
            require(compute.min_instances==0 and compute.max_instances==1 and compute.idle_time_before_scale_down is not None and 0<compute.idle_time_before_scale_down<=120,'CPU scaling must be min0/max1/idle<=120sec.')
            environment=resolve_environment(a.ml,config['training_environment'],'train-conda.yml')
            checks.append({'check':'cpu_and_training_environment_readback','status':'OBSERVED','compute':compute.name,'size':compute.size,'environment':environment,'quota_and_build':'NOT PROVED until an actual job starts and completes'})
        if 'workspace' in fields:
            workspace=a.ml.workspaces.get(config['workspace']); checks.append({'check':'workspace_read_access','status':'OBSERVED','id':workspace.id,'mlflow_tracking_uri':workspace.mlflow_tracking_uri})
        for dependency,step in DEPENDENCIES.get(demo,[]):
            proof=run.dependency(dependency,step)
            if dependency=='m3-demo1': require(proof['decision']=='PASS','Candidate validation was rejected.')
            if dependency=='m3-demo3': require(proof['release_decision']=='PASS','Final-test release gate was rejected.')
            checks.append({'check':'dependency_'+dependency,'status':'HASHES_AND_CONSUMED_CONFIGURATION_MATCH','run_id':proof['run_id']})
        if 'serving_environment' in fields:
            environment=resolve_environment(a.ml,config['serving_environment'],'serve-conda.yml'); baseline=deployment_snapshot(a,config['baseline_deployment']); endpoint=course_endpoint(a)
            require(endpoint.traffic.get(config['baseline_deployment'])==100,'Preflight must start with baseline at100 percent.')
            checks.append({'check':'baseline_and_serving_environment','status':'OBSERVED','environment':environment,'baseline':baseline,'traffic':endpoint.traffic})
            if demo in ('m3-demo3','m3-demo4'):
                candidate=deployment_snapshot(a,config['candidate_deployment']); expected=run.dependency('m3-demo2',3)['deployment_snapshot'] if demo=='m3-demo3' else run.dependency('m3-demo3',3)['frozen_release']['deployment_snapshot']
                require(candidate==expected,'Candidate differs from retained deployment/release proof. Restore the exact version first.')
                checks.append({'check':'candidate_readback_matches_frozen_proof','status':'OBSERVED','candidate':candidate})
        if demo=='m3-demo4':
            group=a.arm('GET',config['monitor_action_group_id'],version='2023-01-01'); require(group.get('properties',{}).get('enabled') is True,'Monitoring action group must be enabled.')
            checks.append({'check':'monitor_action_group_readback','status':'OBSERVED','id':group['id'],'metric_windows':'NOT PROVED until actual workload telemetry arrives'})
        report={'status':'READ_ONLY_PREREQUISITES_CHECKED','demo':demo,'checks':checks,'runtime':'NOT RUN','all_steps_pass':False,'not_proved':['Service write permissions','Foundry inference permission/output','CPU job environment build, quota and completion','Actual evaluation gates','Deployment/scoring execution','Live metric windows and rollback recovery'],'next_action':'Execute all numbered learner steps through the same engine and retain every real report. A source/readiness check never replaces those operations.','evidence_path':str(run.path)}
        write(run.path/'report.json',report); return report
    except Exception as exc:
        write(run.path/'failure.json',{'status':'HOLD','checks_completed':checks,'error_type':type(exc).__name__,'message':str(exc),'runtime':'NOT RUN'}); raise
