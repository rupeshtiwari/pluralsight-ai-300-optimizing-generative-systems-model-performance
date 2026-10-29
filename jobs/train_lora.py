"""CPU FP32 LoRA with response-only supervised loss and validation checkpoints."""
import argparse, json, time
from pathlib import Path
import torch, mlflow
from peft import LoraConfig, get_peft_model, TaskType
from ai300.core import read, write, jsonl, digest
from jobs.common import seed, load_base, messages, response_features, evaluate

def main():
    from ai300.versioning import require_versions, TRAIN
    runtime_versions=require_versions(TRAIN)
    p=argparse.ArgumentParser(); p.add_argument('--config',required=True); p.add_argument('--data',required=True); p.add_argument('--output',required=True); a=p.parse_args()
    c=read(a.config); data=Path(a.data); out=Path(a.output); out.mkdir(parents=True,exist_ok=True); seed(c['seed'])
    rows=jsonl(data/'accepted.jsonl'); corpus={r['source_id']:r for r in jsonl('data/corpus.jsonl')}; validation=jsonl(data/'validation.jsonl')
    assert c['batch_size']==1, 'This bounded CPU loop implements batch_size=1 only.'
    assert rows and all(corpus[r['source_ids'][0]]['split']=='train' for r in rows)
    assert all(q['split']=='validation' for q in validation)
    model,tokenizer=load_base(c)
    base=evaluate(model,tokenizer,validation,corpus,c['max_new_tokens']); write(out/'base-validation.json',base)
    model=get_peft_model(model,LoraConfig(r=c['rank'],lora_alpha=c['rank']*2,lora_dropout=0.05,target_modules=c['target_modules'],task_type=TaskType.CAUSAL_LM,bias='none'))
    parameters=[p for p in model.parameters() if p.requires_grad]; optimizer=torch.optim.AdamW(parameters,lr=c['learning_rate'])
    train=[]
    for r in rows:
        q={'question':r['question'],'relevance':{s:3 for s in r['source_ids']}}
        train.append(response_features(tokenizer,messages(q,corpus),{'answer':r['answer'],'source_ids':r['source_ids']},c['max_length']))
    val=[response_features(tokenizer,messages(q,corpus),q['response'],c['max_length']) for q in validation]
    history=[]; best=float('inf'); started=time.perf_counter(); selected=None
    with mlflow.start_run():
        mlflow.log_params({k:c[k] for k in ('rank','learning_rate','seed','epochs','max_length','base_revision')}); mlflow.log_param('data_sha256',digest(data/'accepted.jsonl'))
        for epoch in range(c['epochs']):
            model.train(); total=0
            for batch in train:
                optimizer.zero_grad(); loss=model(**batch).loss; loss.backward(); torch.nn.utils.clip_grad_norm_(parameters,1.0); optimizer.step(); total+=loss.item()
            model.eval()
            with torch.no_grad(): val_loss=sum(model(**b).loss.item() for b in val)/len(val)
            row={'epoch':epoch+1,'training_loss':total/len(train),'validation_loss':val_loss,'elapsed_seconds':time.perf_counter()-started}; history.append(row)
            for k,v in row.items(): mlflow.log_metric(k,v,step=epoch+1)
            if val_loss<best:
                best=val_loss; selected=epoch+1; model.save_pretrained(out/'adapter'); tokenizer.save_pretrained(out/'tokenizer')
        # Reload the selected checkpoint: final-epoch output is not the selected checkpoint's proof.
        from peft import PeftModel
        del model
        base_model,tokenizer=load_base(c); selected_model=PeftModel.from_pretrained(base_model,out/'adapter')
        adapted=evaluate(selected_model,tokenizer,validation,corpus,c['max_new_tokens']); write(out/'adapted-validation.json',adapted)
        manifest={'kind':'lora','runtime_versions':runtime_versions,'job_name':__import__('os').getenv('AZUREML_RUN_ID'),'selected_epoch':selected,'validation_loss':best,'elapsed_seconds':time.perf_counter()-started,'config':c,'data_sha256':digest(data/'accepted.jsonl'),'validation_sha256':digest(data/'validation.jsonl'),'history':history,'adapter_path':'adapter','tokenizer_path':'tokenizer','base_revision':c['base_revision'],'environment':c['environment'],'prompt_version':'support-json-v1'}
        write(out/'result.json',manifest); mlflow.log_artifacts(str(out))
if __name__=='__main__': main()
