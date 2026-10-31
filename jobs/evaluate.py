"""Validation-only evaluation; final test is reserved for the deployed candidate."""
import argparse, os
from pathlib import Path
import mlflow
from peft import PeftModel
from ai300.core import read, write, jsonl, object_hash
from jobs.common import load_base, evaluate, seed

def main():
    from ai300.versioning import require_versions, TRAIN
    runtime_versions=require_versions(TRAIN)
    p=argparse.ArgumentParser(); p.add_argument('--config',required=True); p.add_argument('--adapter',required=True); p.add_argument('--adapter2',required=True); p.add_argument('--output',required=True); a=p.parse_args(); c=read(a.config); out=Path(a.output); out.mkdir(parents=True,exist_ok=True); seed(c['seed'])
    corpus={r['source_id']:r for r in jsonl('data/corpus.jsonl')}; queries=[r for r in jsonl('data/queries.jsonl') if r['split']=='validation']; results={}
    with mlflow.start_run():
        assert object_hash(c['retrieved_context'])==c['retrieved_context_sha256'], 'Retrieved context hash mismatch'
        queries=[{**q,'retrieved_context':c['retrieved_context'][q['query_id']]} for q in queries]
        for candidate in ('base','adapter','adapter2'):
            model,tokenizer=load_base(c)
            if candidate!='base': model=PeftModel.from_pretrained(model,Path(getattr(a,candidate))/'adapter')
            result=evaluate(model,tokenizer,queries,corpus,c['max_new_tokens']); results[candidate]=result
            for k,v in result['summary'].items():
                if isinstance(v,(int,float)): mlflow.log_metric(candidate+'_'+k,v)
            for query_type,metrics in result['summary']['by_query_type'].items():
                for metric,value in metrics.items():
                    if isinstance(value,(int,float)): mlflow.log_metric(candidate+'_'+query_type+'_'+metric,value)
            del model
        write(out/'result.json',{'kind':'evaluation','runtime_versions':runtime_versions,'job_name':os.getenv('AZUREML_RUN_ID'),'config':c,'validation_sha256':object_hash(queries),'results':results}); mlflow.log_artifacts(str(out))
if __name__=='__main__': main()
