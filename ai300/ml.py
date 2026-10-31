"""Version-bound Azure ML submissions and completed-output checks."""
import json, os, re, shutil, tempfile, time
from pathlib import Path
from .core import ROOT, Hold, require, read, write, digest, object_hash, uid

def submit(a,kind,config,data=None,adapter=None,adapter2=None):
    from azure.ai.ml import command, Input, Output
    from azure.ai.ml.entities import JobResourceConfiguration, CommandJobLimits, AmlCompute
    compute=a.ml.compute.get(a.c['cpu_compute']); require(isinstance(compute,AmlCompute),'Use an AmlCompute CPU cluster, not an unknown compute type.'); size=compute.size.upper()
    require(not any(x in size for x in ('STANDARD_N','GPU')),'CPU-only course: GPU compute is not permitted.')
    require(compute.min_instances==0 and compute.max_instances==1 and compute.idle_time_before_scale_down is not None and 0<compute.idle_time_before_scale_down<=120,'Use a CPU cluster with min=0, max=1 and idle timeout 1..120 seconds.')
    from .azure import resolve_environment
    environment_identity=resolve_environment(a.ml,a.c['training_environment'],'train-conda.yml')
    environment=type('ResolvedEnvironment',(),environment_identity)()
    config={**config,'environment':environment.id,'model_revisions':a.c['model_revisions'],'base_revision':a.c['model_revisions']['Qwen/Qwen3-0.6B']}
    bundle=a.run.attempt/'job-source'; stage_job_source(bundle,config)
    inputs={}; arguments=''
    if data:
        inputs['data']=Input(type='uri_folder',path=data,mode='ro_mount'); arguments+=' --data ${{inputs.data}}'
    if adapter:
        inputs['adapter']=Input(type='uri_folder',path=adapter,mode='ro_mount'); arguments+=' --adapter ${{inputs.adapter}}'
    if adapter2:
        inputs['adapter2']=Input(type='uri_folder',path=adapter2,mode='ro_mount'); arguments+=' --adapter2 ${{inputs.adapter2}}'
    name='ai300-'+kind+'-'+uid().lower()
    cmd=command(name=name,display_name=name,experiment_name='ai300-'+kind,code=str(bundle),command=f'python -m jobs.{kind} --config job-config.json --output ${{{{outputs.result}}}}'+arguments,inputs=inputs,outputs={'result':Output(type='uri_folder',mode='rw_mount')},environment=environment.id,compute=a.c['cpu_compute'],resources=JobResourceConfiguration(instance_count=1),environment_variables={'OMP_NUM_THREADS':'4','MKL_NUM_THREADS':'4','HF_HUB_DOWNLOAD_TIMEOUT':'90'},limits=CommandJobLimits(timeout=7200),tags={'course':'ai300','config_hash':object_hash(config),'source_hash':object_hash(read(a.run.path/'manifest.json')['source_hashes'])})
    job=a.ml.jobs.create_or_update(cmd)
    result={'job_name':job.name,'job_id':job.id,'studio_url':job.studio_url,'status':job.status,'config':config,'config_sha256':object_hash(config),'source_sha256':cmd.tags['source_hash'],'environment_id':environment.id,'environment_identity':environment_identity,'compute':a.c['cpu_compute'],'inputs':{k:v.path for k,v in inputs.items()}}
    a.run.state['resources'].setdefault('jobs',[]).append(job.name); a.run.save(); a.run.raw('submitted-job',result)
    return result

def completed(a,submission):
    job=a.ml.jobs.get(submission['job_name']); a.run.raw('job-status',{'name':job.name,'id':job.id,'status':job.status,'tags':job.tags,'environment':str(job.environment)})
    require(job.status=='Completed',f"Job {job.name} is {job.status}. Inspect Azure ML; rerun this step only after genuine completion.")
    require(job.tags.get('config_hash')==submission['config_sha256'] and job.tags.get('source_hash')==submission['source_sha256'],'Job input/config/source identity mismatch.')
    target=a.run.attempt/'downloaded'; a.ml.jobs.download(job.name,download_path=str(target),output_name='result')
    manifests=list(target.rglob('result.json')); require(len(manifests)==1,'Expected exactly one genuine job result manifest.')
    result=read(manifests[0]); require(object_hash(result['config'])==submission['config_sha256'],'Downloaded job configuration mismatch.')
    require(result.get('job_name')==job.name,'Downloaded result is not from the submitted Azure job.')
    return {'job_name':job.name,'job_id':job.id,'status':job.status,'output_path':str(manifests[0].parent),'output_uri':f'azureml://jobs/{job.name}/outputs/result/paths/','result':result,'result_sha256':digest(manifests[0]),'config_sha256':submission['config_sha256']}


def stage_job_source(bundle,config):
    """Allowlist code and train/validation records; final-test labels never enter job inputs."""
    from .core import jsonl, write_jsonl
    bundle=Path(bundle); bundle.mkdir()
    for folder in ('ai300','jobs'):
        shutil.copytree(ROOT/folder,bundle/folder,ignore=shutil.ignore_patterns('__pycache__'))
    (bundle/'data').mkdir()
    for filename in ('corpus.jsonl','queries.jsonl'):
        write_jsonl(bundle/'data'/filename,[r for r in jsonl(ROOT/'data'/filename) if r['split'] in ('train','validation')])
    shutil.copy2(ROOT/'data/embedding-pairs.jsonl',bundle/'data/embedding-pairs.jsonl')
    write(bundle/'job-config.json',config)
