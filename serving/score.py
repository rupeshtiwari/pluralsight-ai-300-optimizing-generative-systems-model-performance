"""Versioned CPU FP32 scorer with observable identity on every response."""
import json, os, time
from pathlib import Path

def init():
    global model, tokenizer, identity, runtime_versions
    import torch, sys
    from importlib.metadata import version
    if sys.version_info[:3]!=(3,12,16): raise RuntimeError('Serving requires Python 3.12.16')
    expected={'torch':'2.14.1+cpu','transformers':'5.20.2','peft':'0.21.2','accelerate':'1.15.0','azureml-inference-server-http':'1.5.1'}
    runtime_versions={name:version(name) for name in expected}
    if runtime_versions!=expected: raise RuntimeError('Serving package versions differ from pinned CPU environment')
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    root=Path(os.environ['AZUREML_MODEL_DIR']); candidates=list(root.rglob('identity.json'))
    if len(candidates)!=1: raise RuntimeError('Expected exactly one model identity manifest.')
    root=candidates[0].parent; identity=json.loads(candidates[0].read_text()); torch.set_num_threads(4)
    tokenizer=AutoTokenizer.from_pretrained(root/'tokenizer',local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(root/'base',torch_dtype=torch.float32,local_files_only=True)
    if (root/'adapter').exists(): model=PeftModel.from_pretrained(model,root/'adapter',local_files_only=True)
    model.to('cpu'); model.eval()

def run(raw_data):
    import torch
    payload=json.loads(raw_data) if isinstance(raw_data,str) else raw_data
    limit=int(payload.get('max_new_tokens',96))
    if not 16<=limit<=192: raise ValueError('max_new_tokens must be 16..192')
    question=payload['question']; context=payload.get('evidence',[])
    if len(question)>1000 or len(json.dumps(context))>12000: raise ValueError('Request too large.')
    prompt=[{'role':'system','content':'Return only JSON with answer (string) and source_ids (array). Use supplied evidence for support questions. Preserve all policy conditions. Answer general questions directly.'},{'role':'user','content':json.dumps({'question':question,'evidence':context})}]
    text=tokenizer.apply_chat_template(prompt,tokenize=False,add_generation_prompt=True,enable_thinking=False); inputs=tokenizer(text,return_tensors='pt'); started=time.perf_counter()
    with torch.no_grad(): output=model.generate(**inputs,max_new_tokens=limit,do_sample=False,pad_token_id=tokenizer.eos_token_id)
    new=output[0,inputs['input_ids'].shape[1]:]
    return {'runtime_versions':runtime_versions,'model_identity':identity,'deployment':os.getenv('DEPLOYMENT_NAME','unknown'),'response':tokenizer.decode(new,skip_special_tokens=True),'output_tokens':len(new),'generation_ms':(time.perf_counter()-started)*1000,'max_new_tokens':limit}
