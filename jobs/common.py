"""Functions shared by real CPU command jobs and managed CPU serving."""
import json, os, random, time
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from ai300.core import ROOT, read, write, jsonl, answer_metrics, summarize, object_hash
PROMPT_VERSION='support-json-v1'
def seed(value=17):
    random.seed(value); torch.manual_seed(value); torch.set_num_threads(int(os.getenv('OMP_NUM_THREADS','4')))
def messages(q, corpus):
    context=[{'source_id':sid,'text':corpus[sid]['text']} for sid in q.get('relevance',{})]
    return [{'role':'system','content':'Return only JSON with answer (string) and source_ids (array). Use supplied evidence for support questions. Preserve all policy conditions. Answer general questions directly.'},{'role':'user','content':json.dumps({'question':q['question'],'evidence':context})}]
def load_base(config):
    name='Qwen/Qwen3-0.6B'; rev=config['model_revisions'][name]
    tokenizer=AutoTokenizer.from_pretrained(name,revision=rev)
    model=AutoModelForCausalLM.from_pretrained(name,revision=rev,torch_dtype=torch.float32)
    model.to('cpu'); tokenizer.pad_token=tokenizer.eos_token
    return model,tokenizer

def response_features(tokenizer,prompt,answer,max_length=512):
    prefix=tokenizer.apply_chat_template(prompt,tokenize=True,add_generation_prompt=True,enable_thinking=False)
    target=tokenizer.encode(json.dumps(answer)+tokenizer.eos_token,add_special_tokens=False)
    # Never silently train on truncated answers or an all-masked target.
    if len(prefix)+len(target)>max_length: raise ValueError('Training example exceeds the fixed token budget; revise the data.')
    return {'input_ids':torch.tensor([prefix+target]),'attention_mask':torch.ones((1,len(prefix)+len(target)),dtype=torch.long),'labels':torch.tensor([[-100]*len(prefix)+target])}

def generate(model,tokenizer,prompt,max_new_tokens=96):
    text=tokenizer.apply_chat_template(prompt,tokenize=False,add_generation_prompt=True,enable_thinking=False)
    inputs=tokenizer(text,return_tensors='pt'); start=time.perf_counter()
    with torch.no_grad(): ids=model.generate(**inputs,max_new_tokens=max_new_tokens,do_sample=False,pad_token_id=tokenizer.eos_token_id)
    new=ids[0,inputs['input_ids'].shape[1]:]
    return tokenizer.decode(new,skip_special_tokens=True),(time.perf_counter()-start)*1000,len(new)

def evaluate(model,tokenizer,questions,corpus,max_new_tokens=96):
    model.eval(); rows=[]
    for q in questions:
        raw,elapsed,tokens=generate(model,tokenizer,messages(q,corpus),max_new_tokens)
        rows.append({'query_id':q['query_id'],'query_type':q['query_type'],'question':q['question'],'supplied_context':json.loads(messages(q,corpus)[-1]['content'])['evidence'],'reference_response':q['response'],'raw_response':raw,'latency_ms':elapsed,'output_tokens':tokens,**answer_metrics(raw,q)})
    return {'summary':summarize(rows),'rows':rows}
