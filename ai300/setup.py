"""Explicit one-time preparation against the learner's own Azure workspace."""
import argparse, json, re, shutil, tempfile
from pathlib import Path
from .core import ROOT, read, write, require, object_hash, uid

def main():
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['plan','prepare','freeze-models','register-environments','create-baseline','restore-endpoint']); p.add_argument('--image',help='Exact CPU Azure ML base image URI including @sha256 digest'); p.add_argument('--from-run',help='Retained completed m3-demo2 or m3-demo3 run folder'); p.add_argument('--include-baseline',action='store_true',help='Create the dedicated billable baseline as part of prepare'); args=p.parse_args()
    if args.action=='plan':
        print(json.dumps({'action':'PLAN_ONLY_NO_AZURE_CALLS','human_before_execution':['Provide dedicated Azure resource IDs in config.local.json; do not add secrets','Authenticate an identity authorized for these resources','Confirm Free-tier semantic regional support, exact Foundry model access, CPU and endpoint quota','Supply an enabled Monitor action group and choose cleanup retention'], 'automated_prepare':['Resolve immutable commits for the three approved models','Resolve Microsoft CPU base-image tag to a digest','Register pinned separate training and serving environment definitions','Optionally create the dedicated baseline (--include-baseline)'], 'human_before_acceptance':['Review every generated synthetic example against the original policy','Review actual RAG, validation and final-test responses against exact supplied context','Wait for genuine job/deployment completion and telemetry windows when required'], 'commands':['python -m ai300.setup prepare','python -m ai300.setup prepare --include-baseline','./module1/m1-c2/scripts/preflight_check.sh --live','python -m ai300.setup restore-endpoint --from-run YOUR_RETAINED_RUN']},indent=2)); return
    from .versioning import client_versions
    client_versions()
    c=read(ROOT/'config.local.json')
    if args.action=='restore-endpoint':
        require(args.from_run,'Pass --from-run with retained deployment or final-test evidence.')
        from .restore import restore_endpoint
        print(json.dumps(restore_endpoint(args.from_run,c),indent=2)); return
    if args.action=='prepare':
        import subprocess,sys
        subprocess.run([sys.executable,'-m','ai300.setup','freeze-models'],check=True,timeout=180)
        image=args.image or subprocess.check_output([sys.executable,str(ROOT/'scripts/resolve_cpu_image.py')],text=True,timeout=45).strip()
        subprocess.run([sys.executable,'-m','ai300.setup','register-environments','--image',image],check=True,timeout=300)
        if args.include_baseline: subprocess.run([sys.executable,'-m','ai300.setup','create-baseline'],check=True,timeout=1800)
        print('Preparation definitions created. Environment builds, inference and every live demo still require actual evidence.'); return
    if args.action=='freeze-models':
        from huggingface_hub import HfApi
        api=HfApi()
        for name in c['model_revisions']:
            revision=api.model_info(name,timeout=30).sha; require(re.fullmatch('[0-9a-f]{40}',revision),'Expected immutable commit.'); c['model_revisions'][name]=revision
        write(ROOT/'config.local.json',c); print(json.dumps(c['model_revisions'],indent=2)); return
    from azure.ai.ml import MLClient
    from azure.ai.ml.entities import Environment
    from azure.identity import DefaultAzureCredential
    client=MLClient(DefaultAzureCredential(exclude_interactive_browser_credential=True),c['subscription_id'],c['resource_group'],c['workspace'],connection_timeout=15,read_timeout=90,retry_total=2)
    if args.action=='create-baseline':
        create_baseline(client,c); return
    require(args.image and '@sha256:' in args.image,'Pass the current approved CPU base image by immutable sha256 digest; no rolling tag.')
    for kind,field in [('train','training_environment'),('serve','serving_environment')]:
        definition=ROOT/'environments'/f'{kind}-conda.yml'; version=object_hash({'image':args.image,'conda':definition.read_text()})[:16]
        env=client.environments.create_or_update(Environment(name='ai300-cpu-'+kind,version=version,image=args.image,conda_file=str(definition),description='Pinned CPU environment; build/run still require verification'))
        c[field]=env.id
    write(ROOT/'config.local.json',c); print('Environment definitions registered. Builds and dependency compatibility remain unverified until jobs complete.')

def create_baseline(client,c):
    from azure.ai.ml.entities import Model, ManagedOnlineEndpoint, ManagedOnlineDeployment, CodeConfiguration, OnlineRequestSettings
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    require(c['endpoint'].startswith('ai300-'),'Use a dedicated ai300- endpoint; do not create a course baseline in a production endpoint.')
    require(c['endpoint'] not in {e.name for e in client.online_endpoints.list()},'Endpoint already exists; inspect it instead of overwriting.')
    require(not any(x in c['endpoint_instance_type'].upper() for x in ('STANDARD_N','GPU')),'CPU instance required.')
    path=ROOT/'evidence'/'setup'/uid(); path.mkdir(parents=True); bundle=path/'baseline'; bundle.mkdir()
    revision=c['model_revisions']['Qwen/Qwen3-0.6B']; require(re.fullmatch('[0-9a-f]{40}',revision),'Pin base revision first.')
    base=snapshot_download('Qwen/Qwen3-0.6B',revision=revision,allow_patterns=['*.json','*.safetensors','*.txt','*.model','*.jinja']); shutil.copytree(base,bundle/'base')
    AutoTokenizer.from_pretrained('Qwen/Qwen3-0.6B',revision=revision).save_pretrained(bundle/'tokenizer')
    version=path.name.replace('-',''); identity={'model_name':'ai300-support-base','model_version':version,'base_model':'Qwen/Qwen3-0.6B','base_revision':revision,'adapter':None,'prompt_version':'support-json-v1'}; write(bundle/'identity.json',identity)
    model=client.models.create_or_update(Model(name=identity['model_name'],version=version,path=str(bundle),type='custom_model',tags={'course':'ai300'}))
    endpoint=ManagedOnlineEndpoint(name=c['endpoint'],auth_mode='key',tags={'course':'ai300','purpose':'disposable-course-lab'})
    client.online_endpoints.begin_create_or_update(endpoint).result(timeout=600)
    write(path/'resources.json',{'endpoint':c['endpoint'],'model_id':model.id,'identity':identity,'status':'ENDPOINT_CREATED_DEPLOYMENT_PENDING'})
    from .azure import resolve_environment
    serving_environment=resolve_environment(client,c['serving_environment'],'serve-conda.yml')
    deployment=ManagedOnlineDeployment(name=c['baseline_deployment'],endpoint_name=c['endpoint'],model=model.id,environment=serving_environment['id'],code_configuration=CodeConfiguration(code=str(ROOT/'serving'),scoring_script='score.py'),instance_type=c['endpoint_instance_type'],instance_count=1,environment_variables={'DEPLOYMENT_NAME':c['baseline_deployment'],'OMP_NUM_THREADS':'4','HF_HUB_OFFLINE':'1'},request_settings=OnlineRequestSettings(request_timeout_ms=180000,max_concurrent_requests_per_instance=1),tags={'course':'ai300'})
    client.online_deployments.begin_create_or_update(deployment).result(timeout=1200)
    endpoint=client.online_endpoints.get(c['endpoint']); endpoint.traffic={c['baseline_deployment']:100}; client.online_endpoints.begin_create_or_update(endpoint).result(timeout=180)
    write(path/'resources.json',{'endpoint':c['endpoint'],'model_id':model.id,'identity':identity,'status':'DEPLOYED','traffic':client.online_endpoints.get(c['endpoint']).traffic})
    print('Baseline deployed; billable until deleted. Evidence:',path)

if __name__=='__main__': main()

