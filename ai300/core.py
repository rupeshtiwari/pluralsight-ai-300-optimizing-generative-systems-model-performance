"""Small, dependency-free evidence, split and metric primitives."""
from __future__ import annotations
import hashlib, json, math, os, statistics, time, uuid
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class Hold(RuntimeError):
    """A missing prerequisite or failed gate; never a successful observation."""
def require(condition, message):
    if not condition: raise Hold(message)
def read(path): return json.loads(Path(path).read_text())
def write(path, value):
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str)+'\n')
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def object_hash(value): return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def uid(): return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'-'+uuid.uuid4().hex[:8]
def jsonl(path): return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
def write_jsonl(path, rows):
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
def source_hashes():
    paths=[ROOT/'course-contract.json']
    for name in ('requirements-client.txt','config.example.json'):
        paths.append(ROOT/name)
    for folder in ('ai300','jobs','serving','configs','data','environments','scripts'):
        paths += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p)]
    paths += list(ROOT.glob('module*/m*-c*/scripts/*.sh'))
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(set(paths))}
def cosine_from_score(score, mode='vector'):
    require(mode=='vector', 'Cosine conversion applies only to one pure cosine vector query, never BM25/RRF/semantic scores.')
    require(1/3-1e-6 <= score <= 1+1e-6, 'Invalid transformed cosine score.')
    return 2-1/score

def retrieval_metrics(rows, query, k=5):
    # Multiple chunks of one source must not earn repeated relevance credit.
    sources=list(dict.fromkeys(x['source_id'] for x in rows[:k])); grades=query['relevance']
    relevant={s for s,g in grades.items() if g>0}
    dcg=sum((2**grades.get(s,0)-1)/math.log2(i+2) for i,s in enumerate(sources))
    ideal=sum((2**g-1)/math.log2(i+2) for i,g in enumerate(sorted(grades.values(),reverse=True)[:k]))
    support=query['support'].casefold()
    return {'recall_at_k':len(relevant.intersection(sources))/len(relevant),
            'ndcg_at_k':dcg/ideal if ideal else 0,
            'boundary_failure':int(not any(support in x['content'].casefold() for x in rows[:k])),
            'k':k}

def answer_metrics(raw, q):
    # Narrow labeled checks, not an LLM judge or universal groundedness measure.
    try: response=json.loads(raw) if isinstance(raw,str) else raw
    except (ValueError, TypeError): response={}
    valid=isinstance(response,dict) and isinstance(response.get('answer'),str) and isinstance(response.get('source_ids'),list) and all(isinstance(s,str) and s for s in response.get('source_ids',[]))
    answer=response.get('answer','').casefold() if valid else ''
    correctness=valid and all(x.casefold() in answer for x in q['required_terms']) and not any(x.casefold() in answer for x in q.get('forbidden_terms',[]))
    citations=set(response.get('source_ids',[])) if valid else set()
    expected=set(q.get('relevance',{}))
    # Conservative proxy: all reference conditions must survive verbatim normalization.
    # This can reject valid paraphrases; a separate human semantic gate handles support.
    import re
    normalize=lambda t:' '.join(re.findall(r'\w+',t.casefold()))
    reference=q.get('response',{}).get('answer',q.get('support',''))
    supported=correctness and bool(reference) and normalize(answer)==normalize(reference) and citations==expected
    return {'correctness':int(correctness),'answer_support_proxy':int(supported),'schema_validity':int(valid)}

def summarize(rows):
    require(bool(rows),'Empty results cannot establish quality.')
    keys=('recall_at_k','ndcg_at_k','boundary_failure','correctness','answer_support_proxy','manual_correctness','manual_answer_support','schema_validity','latency_ms','output_tokens')
    out={'n':len(rows)}
    for k in keys:
        vals=[r[k] for r in rows if k in r]
        if vals: out[k]=statistics.mean(vals)
    times=sorted(r['latency_ms'] for r in rows if 'latency_ms' in r)
    if times: out['p95_latency_ms']=times[max(0,math.ceil(.95*len(times))-1)]
    out['by_query_type']={t:{k:statistics.mean([r[k] for r in rows if r.get('query_type')==t and k in r]) for k in keys if any(r.get('query_type')==t and k in r for r in rows)} for t in sorted({r.get('query_type','unknown') for r in rows})}
    return out

def assignment(session, salt='ai300-ab-v1'):
    return 'A' if int(hashlib.sha256((salt+session).encode()).hexdigest(),16)%2==0 else 'B'
def validate_splits():
    docs=jsonl(ROOT/'data/corpus.jsonl'); queries=jsonl(ROOT/'data/queries.jsonl')
    by_id={d['source_id']:d for d in docs}; groups={}
    require(len(by_id)==len(docs),'Duplicate source IDs.')
    for d in docs:
        group=d['source_group']; require(group not in groups or groups[group]==d['split'],'Source-group leakage.')
        groups[group]=d['split']
    for q in queries:
        require(q['split'] in ('train','validation','test'),'Unknown split.')
        for source in q['relevance']:
            require(source in by_id and by_id[source]['split']==q['split'],'Query/source split leakage.')
            require(q['support'].casefold() in by_id[source]['text'].casefold(),'Support label not found in source.')
    return {'sources':len(docs),'queries':len(queries),'source_groups':len(groups),'split_hashes':{s:object_hash([q for q in queries if q['split']==s]) for s in ('train','validation','test')}}

class Run:
    def __init__(self, demo, create=False, cleanup_only=False):
        self.demo=demo; pointer=ROOT/'.state'/f'{demo}.json'
        if create:
            self.path=ROOT/'evidence'/demo/uid(); self.path.mkdir(parents=True,exist_ok=False)
            self.state={'demo':demo,'run_id':self.path.name,'started_at':now(),'steps':{},'resources':{}}
            write(self.path/'manifest.json',{'kind':'LIVE_AZURE_RUN_NOT_YET_EXECUTED','source_hashes':source_hashes(),'config_sha256':digest(ROOT/'config.local.json'),'created_at':now()})
            write(self.path/'config-snapshot.json',read(ROOT/'config.local.json')); self.save(); write(pointer,{'path':str(self.path)})
        else:
            require(pointer.exists(),f'Run {demo} lab-up.sh first.'); self.path=Path(read(pointer)['path']); self.state=read(self.path/'state.json')
            manifest=read(self.path/'manifest.json')
            if not cleanup_only: require(manifest['source_hashes']==source_hashes(),'Sources changed: start a new run; old proof is stale.')
            if not cleanup_only: require(manifest['config_sha256']==digest(ROOT/'config.local.json'),'Config changed: start a new run.')
        self.config=read(self.path/'config-snapshot.json'); self.spec=read(ROOT/'configs'/f'{demo}.json'); self.attempt=None
        if not cleanup_only: validate_demo_spec(demo,self.spec)
    def save(self): write(self.path/'state.json',self.state)
    def begin(self, n):
        require(str(n) not in self.state['steps'],'Completed steps are immutable: start a new lab run to repeat.')
        for prior in range(1,n): require(str(prior) in self.state['steps'],f'Complete step {prior} first.')
        self.attempt=self.path/f'step-{n}-{uuid.uuid4().hex[:8]}'; self.attempt.mkdir()
        return self.attempt
    def complete(self,n,report):
        report={'run_id':self.state['run_id'],'demo':self.demo,'step':n,'observed_at':now(),**report}
        report['artifact_hashes']=artifact_hashes(report)
        write(self.attempt/'report.json',report); self.state['steps'][str(n)]={'report':str(self.attempt/'report.json'),'sha256':digest(self.attempt/'report.json')}; self.save()
        print(json.dumps(report,indent=2,default=str)); print('Report:',self.attempt/'report.json')
    def previous(self,n):
        record=self.state['steps'][str(n)]; require(digest(record['report'])==record['sha256'],'Step report changed after capture.')
        result=read(record['report']); verify_artifacts(result); return result
    def raw(self,name,value):
        p=self.attempt/'raw'/f'{name}-{uuid.uuid4().hex[:6]}.json'; write(p,value); return str(p)
    def dependency(self, demo, step):
        path=self.config.get('runs',{}).get(demo)
        require(path,f'config.local.json runs.{demo} must name a retained genuine run folder.')
        folder=Path(path); folder=folder if folder.is_absolute() else ROOT/folder
        state=read(folder/'state.json'); require(state['demo']==demo,'Wrong dependency demo.')
        manifest=read(folder/'manifest.json'); require(manifest['source_hashes']==source_hashes(),'Dependency sources are stale; rerun affected Azure proof.')
        original=read(folder/'config-snapshot.json')
        require(consumed_config(original,demo)==consumed_config(self.config,demo),'Dependency consumed model/resource/environment configuration differs from this run.')
        require(str(step) in state['steps'],f'Dependency {demo} step {step} incomplete.')
        record=state['steps'][str(step)]; require(digest(record['report'])==record['sha256'],'Dependency report hash mismatch.')
        result=read(record['report']); verify_artifacts(result); return result


def artifact_hashes(value):
    found={}
    def visit(node):
        if isinstance(node,dict):
            for key,item in node.items():
                if (key in ('output_path','selected_output_path','bundle_path','data_path','generated_path','evidence_path') or (key=='review_path' and node.get('review_sha256'))) and isinstance(item,str):
                    path=Path(item)
                    if path.is_file(): found[str(path)]=digest(path)
                    elif path.is_dir():
                        for file in path.rglob('*'):
                            if file.is_file(): found[str(file)]=digest(file)
                elif key!='artifact_hashes': visit(item)
        elif isinstance(node,list):
            for item in node: visit(item)
    visit(value); return found

def verify_artifacts(report):
    for path,sha in report.get('artifact_hashes',{}).items():
        require(Path(path).is_file() and digest(path)==sha,'Required retained artifact changed or is missing: '+path)

def prepare_manual_review(run,name,rows):
    """Create a human rubric; never infer a reviewer's acceptance from automatic checks."""
    path=run.path/(name+'-review.jsonl')
    expected=[]
    for i,row in enumerate(rows):
        expected.append({'review_id':f"{row.get('variant',row.get('arm','candidate'))}:{row['query_id']}:{i}",'query_id':row['query_id'],'query_type':row['query_type'],'variant':row.get('variant',row.get('arm','candidate')),'response_sha256':object_hash(row['raw_response']),'raw_response':row['raw_response'],'question':row.get('question'),'supplied_context':row.get('supplied_context'),'reference_response':row.get('reference_response'),'generation_evidence':row.get('generation_evidence'),'review_evidence_sha256':object_hash({k:row.get(k) for k in ('raw_response','question','supplied_context','reference_response','generation_evidence')}),'correct':None,'supported':None,'reason':'','reviewer':''})
    if not path.exists(): write_jsonl(path,expected)
    return path,expected

def manual_review(run,name,rows):
    path,expected=prepare_manual_review(run,name,rows); reviews=jsonl(path)
    require(len(reviews)==len(expected),f'Manual review coverage differs: {path}')
    merged=[]
    for row,review,contract in zip(rows,reviews,expected):
        for key in ('review_id','query_id','query_type','variant','response_sha256','raw_response','question','supplied_context','reference_response','generation_evidence','review_evidence_sha256'):
            require(review.get(key)==contract[key],f'Manual review identity mismatch: {path}')
        require(isinstance(review.get('correct'),bool) and isinstance(review.get('supported'),bool) and review.get('reason','').strip() and review.get('reviewer','').strip(),f'Manual semantic review required in {path}: compare every answer and condition with its exact supplied_context/reference; fill correct, supported, reason, reviewer.')
        merged.append({**row,'manual_correctness':int(review['correct']),'manual_answer_support':int(review['supported'])})
    return {'review_path':str(path),'review_sha256':digest(path),'rows':merged,'summary':{key:statistics.mean(r[key] for r in merged) for key in ('manual_correctness','manual_answer_support')},'by_variant':{v:{key:statistics.mean(r[key] for r in merged if r.get('variant',r.get('arm','candidate'))==v) for key in ('manual_correctness','manual_answer_support')} for v in {r.get('variant',r.get('arm','candidate')) for r in merged}},'by_query_type':{t:{key:statistics.mean(r[key] for r in merged if r['query_type']==t) for key in ('manual_correctness','manual_answer_support')} for t in {r['query_type'] for r in merged}}}


def consumed_config(config,demo):
    """Compare only configuration actually consumed by the prerequisite exercise."""
    workspace=['subscription_id','resource_group','workspace']
    search=['search_endpoint','search_index','search_resource_id']
    foundry=['foundry_endpoint','foundry_resource_id','foundry_deployment','foundry_model','foundry_version']
    training=['cpu_compute','training_environment']
    endpoint=['endpoint','baseline_deployment','candidate_deployment','serving_environment','endpoint_instance_type']
    names={'m1-demo1':workspace+search,'m1-demo2':workspace+search,'m1-demo3':workspace+search+foundry,'m2-demo1':workspace+training+search,'m2-demo2':workspace+foundry,'m2-demo3':workspace+training,'m2-demo4':workspace+training,'m3-demo1':workspace+training+search+['adopted_retrieval'],'m3-demo2':workspace+endpoint,'m3-demo3':workspace+endpoint,'m3-demo4':workspace+endpoint+['monitor_action_group_id']}[demo]
    result={key:config.get(key) for key in names}
    if demo!='m2-demo2':
        models=['sentence-transformers/all-MiniLM-L6-v2','BAAI/bge-small-en-v1.5'] if demo.startswith('m1') or demo in ('m2-demo1','m3-demo1') else ['Qwen/Qwen3-0.6B']
        if demo=='m3-demo1': models=models+['Qwen/Qwen3-0.6B']
        result['model_revisions']={model:config.get('model_revisions',{}).get(model) for model in models}
    return result


def validate_demo_spec(demo,spec):
    if demo=='m1-demo1':
        require(spec.get('chunk_sizes')==[64,128,192],'The approved comparison requires chunk_sizes [64,128,192].')
        require(isinstance(spec.get('overlap_tokens'),int) and 0<=spec['overlap_tokens']<64,'Overlap must be an integer from 0 to 63 tokens.')
    if demo=='m1-demo2': require(spec.get('semantic_candidates')==50,'The approved semantic comparison requests 50 vector candidates.')
    if demo=='m2-demo2': require(spec.get('manual_review_required') is True,'Manual acceptance of synthetic examples is a required gate.')
    if demo=='m3-demo2': require(type(spec.get('traffic')) is int and spec['traffic']==0,'A newly deployed candidate must receive zero routed traffic.')
    if demo=='m2-demo3': require(spec.get('batch_size')==1,'The bounded CPU loop implements batch_size=1; revise code and its evidence before changing it.')

    if demo=='m3-demo4':
        test=spec.get('rollback_test',{})
        require(isinstance(test.get('enabled'),bool),'Declare whether the isolated rollback test is enabled before traffic.')
        if test['enabled']:
            require(test.get('label')=='ISOLATED_COURSE_ROLLBACK_TEST_NOT_PRODUCTION_SLO','An isolated rollback-test trigger must be explicitly labeled test-only.')
            require(isinstance(test.get('candidate_p95_threshold_ms'),(int,float)) and 0<test['candidate_p95_threshold_ms']<spec['latency_budget_ms'],'Test candidate threshold must be positive and stricter than normal baseline recovery budget.')


def index_layout_version(config,spec):
    return object_hash({'corpus':jsonl(ROOT/'data/corpus.jsonl'),'chunk_sizes':spec.get('chunk_sizes',[64,128,192]),'overlap_tokens':spec.get('overlap_tokens',16),'encoder_revisions':{name:config['model_revisions'][name] for name in ('sentence-transformers/all-MiniLM-L6-v2','BAAI/bge-small-en-v1.5')}})
