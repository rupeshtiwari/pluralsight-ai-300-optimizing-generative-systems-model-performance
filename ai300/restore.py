"""Restore exact existing baseline/candidate asset versions after independent cleanup."""
from pathlib import Path
from .core import ROOT, Hold, require, read, write, digest, source_hashes, consumed_config, verify_artifacts, uid
from .azure import Azure, deployment_snapshot, resolve_environment
from .preflight import ReadOnlyContext

def restore_endpoint(folder,config):
    from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, CodeConfiguration, OnlineRequestSettings
    folder=Path(folder); folder=folder if folder.is_absolute() else ROOT/folder
    state=read(folder/'state.json'); require(state['demo'] in ('m3-demo2','m3-demo3'),'Restore from a completed deployment or final-test run.')
    require(read(folder/'manifest.json')['source_hashes']==source_hashes(),'Restore source is stale; review source changes before restoring the release.')
    require(consumed_config(read(folder/'config-snapshot.json'),state['demo'])==consumed_config(config,state['demo']),'Restore resource/model/environment configuration differs from retained proof.')
    require('3' in state['steps'],'Step3 proof is required before exact restoration.'); record=state['steps']['3']; require(digest(record['report'])==record['sha256'],'Retained report hash mismatch.')
    report=read(record['report']); verify_artifacts(report)
    frozen=report['frozen_release'] if state['demo']=='m3-demo3' else report
    require(all(key in frozen for key in ('deployment_snapshot','baseline_deployment_snapshot','baseline_model_identity')),'Both baseline and candidate snapshots are required.')
    run=ReadOnlyContext('m3-demo2',config); a=Azure(run); resolve_environment(a.ml,config['serving_environment'],'serve-conda.yml')
    endpoint_name=config['endpoint']; require(endpoint_name.startswith('ai300-'),'Restore only a dedicated ai300- course endpoint.')
    existing={e.name:e for e in a.ml.online_endpoints.list()}
    if endpoint_name not in existing:
        endpoint=ManagedOnlineEndpoint(name=endpoint_name,auth_mode=frozen.get('endpoint_auth_mode','key'),tags={'course':'ai300','purpose':'disposable-course-lab'})
        a.ml.online_endpoints.begin_create_or_update(endpoint).result(timeout=600)
    else:
        endpoint=a.ml.online_endpoints.get(endpoint_name)
        require(endpoint.tags.get('course')=='ai300' and endpoint.tags.get('purpose')=='disposable-course-lab','Refusing to alter an unrelated endpoint.')
        require(endpoint.auth_mode==frozen.get('endpoint_auth_mode','key'),'Endpoint authentication changed.')
        require(endpoint.traffic.get(config['candidate_deployment'],0)==0,'Restore requires candidate traffic at zero; restore baseline traffic first.')
    for snapshot in (frozen['baseline_deployment_snapshot'],frozen['deployment_snapshot']):
        name=snapshot['deployment']; deployments={d.name for d in a.ml.online_deployments.list(endpoint_name)}
        if name not in deployments:
            # Reuse registered code/model/environment IDs. No model re-registration or test replay.
            definition=ManagedOnlineDeployment(name=name,endpoint_name=endpoint_name,model=snapshot['model_id'],environment=snapshot['environment_id'],code_configuration=CodeConfiguration(code=snapshot['code_id'],scoring_script=snapshot['scoring_script']),instance_type=snapshot['instance_type'],instance_count=snapshot['instance_count'],environment_variables=snapshot['environment_variables'],request_settings=OnlineRequestSettings(request_timeout_ms=snapshot['request_timeout_ms'],max_concurrent_requests_per_instance=snapshot['max_concurrent_requests_per_instance']),tags={'course':'ai300','restored_from_run':state['run_id']})
            write(run.path/(name+'-restore-intent.json'),{'endpoint':endpoint_name,'definition':snapshot,'status':'SUBMITTING'})
            a.ml.online_deployments.begin_create_or_update(definition).result(timeout=1200)
        require(deployment_snapshot(a,name)==snapshot,'Restored deployment readback differs from retained immutable definition.')
    endpoint=a.ml.online_endpoints.get(endpoint_name); endpoint.traffic={config['baseline_deployment']:100,config['candidate_deployment']:0}; a.ml.online_endpoints.begin_create_or_update(endpoint).result(timeout=180)
    from .demos import endpoint_payload, validation
    question=validation()[0]; responses={}
    for name,identity in [(config['baseline_deployment'],frozen['baseline_model_identity']),(config['candidate_deployment'],frozen['model_identity'])]:
        response,latency=a.invoke(endpoint_payload(question,96),name); require(response['model_identity']==identity,'Restored response identity differs from retained model.'); responses[name]={'response':response,'latency_ms':latency}
    routed,_=a.invoke(endpoint_payload(question,96)); require(routed['deployment']==config['baseline_deployment'],'Restored endpoint does not route to baseline.')
    result={'status':'RESTORED_EXACT_REGISTERED_VERSIONS','source_run':str(folder),'source_report_sha256':record['sha256'],'traffic':a.ml.online_endpoints.get(endpoint_name).traffic,'baseline':frozen['baseline_deployment_snapshot'],'candidate':frozen['deployment_snapshot'],'direct_responses':responses,'routed_response':routed,'final_test_reused':False,'evidence_path':str(run.path)}
    write(run.path/'restore-report.json',result); return result
