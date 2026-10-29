"""Public lab CLI. Missing Azure proof produces HOLD and a nonzero exit."""
import argparse, importlib.util, json, os, re, signal, sys, traceback
from pathlib import Path
from .core import ROOT, Hold, Run, require, read, write, digest, source_hashes, validate_splits, now, consumed_config
from .demos import HANDLERS

def check_config(demo):
    path=ROOT/'config.local.json'; require(path.exists(),'Copy config.example.json to config.local.json, configure existing Azure resources and pin model commits; see setup/README.md.')
    c=read(path)
    fields=consumed_config(c,demo)
    missing=[key for key,value in fields.items() if key!='model_revisions' and (not isinstance(value,str) or not value or 'REPLACE' in value)]
    require(not missing,'Configure: '+', '.join(missing))
    for model,revision in fields.get('model_revisions',{}).items(): require(isinstance(revision,str) and re.fullmatch('[0-9a-f]{40}',revision),f'Immutable model commit missing: {model}. Run python -m ai300.setup freeze-models.')
    for name in ('azure.ai.ml','azure.identity','sentence_transformers','openai','mlflow'):
        try: found=importlib.util.find_spec(name)
        except ModuleNotFoundError: found=None
        require(found is not None,f'Missing dependency {name}; install the pinned client environment.')
    from .versioning import client_versions
    client_versions()
    return c

def cleanup(run):
    from .azure import Azure
    a=Azure(run); config=run.config.get('cleanup',{}); actions=[]
    from azure.core.exceptions import ResourceNotFoundError
    endpoint_applicable=run.demo in ('m3-demo2','m3-demo3','m3-demo4')
    endpoint=None
    if endpoint_applicable:
        try:
            endpoint=a.ml.online_endpoints.get(run.config['endpoint'])
            from .azure import require_course_endpoint
            require_course_endpoint(endpoint,run.config['endpoint'])
        except ResourceNotFoundError: actions.append({'endpoint_already_absent':run.config['endpoint']})
    # Canary cleanup restores baseline only when the owned endpoint still exists.
    if run.demo=='m3-demo4' and endpoint is not None:
        from .demos import set_traffic
        actions.append({'restore_traffic':set_traffic(a,100,0)})
    resources=run.state['resources']
    for name in resources.get('jobs',[]):
        job=a.ml.jobs.get(name)
        if job.status not in ('Completed','Failed','Canceled','CancelRequested'):
            a.ml.jobs.cancel(name); actions.append({'cancel_job':name})
    if config.get('delete_candidate') and endpoint_applicable and endpoint is not None:
        name=run.config['candidate_deployment']; endpoint=run.config['endpoint']
        deployments={d.name:d for d in a.ml.online_deployments.list(endpoint)}
        if name in deployments:
            require(name!=run.config['baseline_deployment'] and deployments[name].tags.get('course')=='ai300','Refusing to delete an unrelated deployment.')
            state=a.ml.online_endpoints.get(endpoint)
            if state.traffic.get(name,0):
                from .demos import set_traffic
                set_traffic(a,100,0)
            a.ml.online_deployments.begin_delete(name,endpoint).result(timeout=300); actions.append({'deleted_candidate':name})
    if config.get('delete_alert') and resources.get('alert_id'):
        try:
            a.arm('DELETE',resources['alert_id'],version='2018-03-01'); actions.append({'deleted_alert':resources['alert_id']})
        except Hold as exc:
            from urllib.error import HTTPError
            if isinstance(exc.__cause__,HTTPError) and exc.__cause__.code==404: actions.append({'alert_already_absent':resources['alert_id']})
            else: raise
    if config.get('delete_search_index') and resources.get('search_index'):
        require(resources['search_index'].startswith('ai300-'),'Refusing to remove a non-course index.')
        try:
            a.search('indexes/'+resources['search_index'],method='DELETE'); actions.append({'deleted_index':resources['search_index']})
        except Hold as exc:
            from urllib.error import HTTPError
            if isinstance(exc.__cause__,HTTPError) and exc.__cause__.code==404: actions.append({'index_already_absent':resources['search_index']})
            else: raise
    if config.get('delete_endpoint') and endpoint_applicable and endpoint is not None:
        endpoint=a.ml.online_endpoints.get(run.config['endpoint']); require(endpoint.tags.get('course')=='ai300' and endpoint.tags.get('purpose')=='disposable-course-lab','Only the dedicated course endpoint may be removed.')
        a.ml.online_endpoints.begin_delete(endpoint.name).result(timeout=300); actions.append({'deleted_endpoint':endpoint.name})
    compute_info={'status':'NOT_USED_BY_THIS_RUN'}
    if resources.get('jobs'):
        compute=a.ml.compute.get(run.config['cpu_compute'])
        from azure.ai.ml.entities import AmlCompute
        require(isinstance(compute,AmlCompute) and compute.min_instances==0 and compute.max_instances==1 and compute.idle_time_before_scale_down is not None and 0<compute.idle_time_before_scale_down<=120,'CPU cluster scaling is unknown or not min=0/max=1/idle<=120; inspect it in Azure ML.')
        compute_info={'name':compute.name,'min_instances':compute.min_instances,'idle_time_before_scale_down':compute.idle_time_before_scale_down}
    return {'cleanup_actions':actions,'compute':compute_info,'retained':'Training/evaluation artifacts, data/model/environment versions, workspace storage and baseline endpoint unless delete_endpoint=true. Storage/monitoring and retained endpoints may continue incurring charges.','verify_next':'Azure ML Compute for submitted jobs: confirm scale-down after configured idle timeout. Azure portal: verify deleted deployment/endpoint and alert are absent.'}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--demo',choices=HANDLERS,required=True); p.add_argument('action',choices=['up','step','check','down']); p.add_argument('number',type=int,nargs='?'); p.add_argument('--offline',action='store_true'); p.add_argument('--live',action='store_true'); args=p.parse_args(); require(not(args.offline and args.live),'Choose either --offline or --live.')
    run=None
    try:
        def request_recovery(signum,frame):
            # A normal stop becomes an exception so the canary's rollback guards execute.
            if hasattr(signal,'SIGALRM'): signal.alarm(0)
            signal.signal(signal.SIGTERM,signal.SIG_IGN); signal.signal(signal.SIGINT,signal.SIG_IGN)
            raise Hold(f'Stop signal {signum} received; entering bounded resource recovery.')
        signal.signal(signal.SIGTERM,request_recovery); signal.signal(signal.SIGINT,request_recovery)
        if hasattr(signal,'SIGALRM'):
            signal.signal(signal.SIGALRM,request_recovery); signal.alarm(1800)
        if args.action=='check':
            result={'mode':'OFFLINE_LOGIC_CHECKS_NOT_AZURE_PROOF','data':validate_splits(),'source_files':len(source_hashes()),'runtime':'NOT RUN'}
            if not args.offline:
                check_config(args.demo)
                from .versioning import client_versions
                result['effective_client_versions']=client_versions()
                result['runtime']='NOT RUN: exact installed versions checked; integration remains unverified'
            if args.live:
                from .preflight import live_checks
                result=live_checks(args.demo,read(ROOT/'config.local.json'))
            print(json.dumps(result,indent=2)); return 0
        if args.action!='down': check_config(args.demo)
        if args.action=='up':
            run=Run(args.demo,create=True); print('Initialized:',run.path); print('Azure runtime: NOT RUN. Execute the numbered steps; inspect real responses.'); return 0
        run=Run(args.demo,cleanup_only=args.action=='down'); count=len(next(x for x in read(ROOT/'course-contract.json')['demos'] if x['stem']==args.demo)['steps'])
        if args.action=='down':
            run.attempt=run.path/('cleanup-'+__import__('uuid').uuid4().hex[:8]); run.attempt.mkdir(); report=cleanup(run); write(run.attempt/'report.json',report); print(json.dumps(report,indent=2)); return 0
        require(args.number is not None and 1<=args.number<=count,f'Choose a step from 1 to {count}.')
        run.begin(args.number); print(f'START {args.demo} step {args.number}; evidence: {run.attempt}',flush=True)
        report=HANDLERS[args.demo](run,args.number); run.complete(args.number,report)
        if report.get('decision')=='REJECT' or report.get('release_decision')=='REJECT':
            print('HOLD: quality gate rejected the candidate; report retained. Keep the baseline.',file=sys.stderr); return 2
        return 0
    except Exception as exc:
        if run is None and args.demo=='m3-demo4' and args.action=='step':
            try:
                run=Run(args.demo,cleanup_only=True); run.attempt=run.path/('failure-recovery-'+__import__('uuid').uuid4().hex[:8]); run.attempt.mkdir()
            except Exception: run=None
        if run and run.demo=='m3-demo4' and run.state.get('canary_started_at') and not run.state.get('baseline_safety_restored') and run.attempt:
            try:
                from .azure import Azure
                from .demos import set_traffic
                traffic=set_traffic(Azure(run),100,0); run.raw('failure-safety-restore',{'original_error':str(exc),'traffic':traffic})
            except Exception as restore_error:
                run.raw('failure-safety-restore-failed',{'original_error':str(exc),'restore_error':str(restore_error),'traffic':'UNKNOWN','action':'Restore baseline in Azure ML immediately; retry lab-down.'})
                print('HOLD: safety restore failed; endpoint traffic is UNKNOWN. Inspect raw diagnostics and restore baseline in Azure ML.',file=sys.stderr)
        if run and run.attempt:
            write(run.attempt/'failure.json',{'status':'HOLD','error_type':type(exc).__name__,'message':str(exc),'at':now(),'traceback':traceback.format_exc()})
        print(f'HOLD: {type(exc).__name__}: {exc}',file=sys.stderr)
        if run: print('Retained evidence:',run.path,file=sys.stderr)
        return 2
    finally:
        if hasattr(signal,'SIGALRM'): signal.alarm(0)


def supervise(command,env=None,timeout=1800,recovery_grace=600,heartbeat=10):
    """Stop the owned child gracefully before a bounded hard stop; never claim recovery on kill."""
    import subprocess, time
    child=subprocess.Popen(command,env=env,start_new_session=os.name!='nt'); started=time.monotonic()
    def parent_stop(signum,frame): raise KeyboardInterrupt('Stop requested')
    original_handlers={signum:signal.getsignal(signum) for signum in (signal.SIGTERM,signal.SIGINT)}
    for signum in original_handlers: signal.signal(signum,parent_stop)
    try:
        try:
            while True:
                remaining=timeout-(time.monotonic()-started)
                if remaining<=0: raise Hold('Command deadline exceeded; requesting bounded recovery.')
                try: return child.wait(timeout=min(heartbeat,remaining))
                except subprocess.TimeoutExpired: print(f'WORKING: {time.monotonic()-started:.0f}s elapsed; command deadline {timeout}s',flush=True)
        except (KeyboardInterrupt,Hold) as exc:
            print('HOLD:',exc,file=sys.stderr)
            # Repeated normal stop signals must not kill a child already restoring baseline.
            for signum in original_handlers: signal.signal(signum,signal.SIG_IGN)
            if child.poll() is None:
                child.send_signal(signal.SIGTERM)
            recovery_started=time.monotonic()
            while child.poll() is None and time.monotonic()-recovery_started<recovery_grace:
                try: child.wait(timeout=min(heartbeat,recovery_grace-(time.monotonic()-recovery_started)))
                except subprocess.TimeoutExpired: print(f'RECOVERY: {time.monotonic()-recovery_started:.0f}s elapsed; allowing resource restoration up to {recovery_grace}s',flush=True)
            if child.poll() is None:
                print('HOLD: recovery grace expired; forced stop. Azure traffic/resource state is UNKNOWN. Restore baseline in Azure ML and run lab-down.',file=sys.stderr)
                if os.name!='nt': os.killpg(child.pid,signal.SIGKILL)
                else: child.kill()
                child.wait(timeout=10)
            else: print(f'STOPPED: child exited {child.returncode}; inspect retained recovery report. No Azure recovery is assumed from exit alone.',file=sys.stderr)
            return 124
    finally:
        for signum,handler in original_handlers.items(): signal.signal(signum,handler)

def bounded_entrypoint():
    if os.getenv('AI300_DEADLINE_CHILD')=='1': return main()
    env={**os.environ,'AI300_DEADLINE_CHILD':'1','PYTHONUNBUFFERED':'1','MLFLOW_HTTP_REQUEST_TIMEOUT':'90','MLFLOW_HTTP_REQUEST_MAX_RETRIES':'2','HF_HUB_DOWNLOAD_TIMEOUT':'90','HF_HUB_ETAG_TIMEOUT':'30'}
    return supervise([sys.executable,'-m','ai300.cli',*sys.argv[1:]],env=env)
if __name__=='__main__': sys.exit(bounded_entrypoint())
