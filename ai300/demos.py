"""The eleven outline-aligned demos, one implementation per conceptual step."""
from __future__ import annotations
import json, math, os, shutil, statistics, time, urllib.parse
from datetime import datetime,timedelta
from pathlib import Path
from .core import ROOT, Hold, require, read, write, jsonl, write_jsonl, digest, object_hash, uid, now, retrieval_metrics, answer_metrics, summarize, assignment, prepare_manual_review, manual_review
from .azure import Azure, resolve_environment, deployment_snapshot, course_endpoint
from .ml import submit, completed
from .gates import quality_checks, sample_counts

def validation(domain=True): return [q for q in jsonl(ROOT/'data/queries.jsonl') if q['split']=='validation' and (q['relevance'] or not domain)]
def sweep(a,variants,questions=None,encoder=None):
    rows=[]
    for label,settings in variants.items():
        for q in questions or validation():
            kept,rejected,elapsed=a.query(q,encoder=encoder,**settings)
            rows.append({'variant':label,'query_id':q['query_id'],'query_type':q['query_type'],'settings':settings,'latency_ms':elapsed,'retained':kept,'rejected':rejected,**retrieval_metrics(kept,q)})
    return {'rows':rows,'variants':{v:summarize([x for x in rows if x['variant']==v]) for v in variants},'split':'validation','measurement':'live Azure Search responses'}

def retrieval_chunks(run,n):
    a=Azure(run)
    if n==1:
        count=a.prepare_index(); result=sweep(a,{str(s):{'size':s,'depth':10} for s in run.spec['chunk_sizes']}); result['indexed_chunks']=count
    elif n==2:
        result=sweep(a,{'depth10-cut0':{'size':128,'depth':10,'cutoff':0.0},'depth20-cut0':{'size':128,'depth':20,'cutoff':0.0},'depth20-cut05':{'size':128,'depth':20,'cutoff':0.5}})
        result['score_contract']='cosine_similarity = 2 - 1/@search.score; one vector query only'
    else:
        reports=[run.previous(i) for i in (1,2)]; variants={str(i)+'-'+k:v for i,r in enumerate(reports,1) for k,v in r['variants'].items()}
        eligible=[k for k,v in variants.items() if v['p95_latency_ms']<=run.spec['latency_budget_ms']]
        require(eligible,'No retrieval variant fits the predeclared latency budget; retain the baseline.')
        winner=max(eligible,key=lambda k:(variants[k]['recall_at_k'],-variants[k]['boundary_failure'],-variants[k]['latency_ms']))
        settings={str(i)+'-'+r['variant']:r['settings'] for i,report in enumerate(reports,1) for r in report['rows']}
        result={'comparison':variants,'selected_variant':winner,'selected_settings':settings[winner],'latency_budget_ms':run.spec['latency_budget_ms'],'selection_rule':'maximize recall, minimize boundary failures, then latency','limitations':'Eight domain validation queries; not statistical proof of general improvement. Cutoff changes retained evidence, not server retrieval.'}
    return result

def hybrid_search(run,n):
    a=Azure(run)
    if n==1:
        a.prepare_index(); return sweep(a,{mode:{'mode':mode,'depth':10} for mode in ('keyword','vector','hybrid')})
    if n==2:
        return sweep(a,{'hybrid-w1-k10':{'mode':'hybrid','weight':1.,'depth':10},'hybrid-w2-k10':{'mode':'hybrid','weight':2.,'depth':10},'hybrid-w2-k50':{'mode':'hybrid','weight':2.,'depth':run.spec['semantic_candidates']},'semantic-w2-k50':{'mode':'semantic','weight':2.,'depth':run.spec['semantic_candidates']}})
    baseline=run.previous(1)['variants']['hybrid']; variants=run.previous(2)['variants']; rows=run.previous(2)['rows']
    regressions=[]
    for name,metrics in variants.items():
        for kind,reference in baseline['by_query_type'].items():
            observed=metrics['by_query_type'].get(kind)
            require(observed is not None,f'Missing query-type evidence: {name}/{kind}.')
            deltas={metric:observed[metric]-reference[metric] for metric in ('recall_at_k','ndcg_at_k')}
            if any(delta<0 for delta in deltas.values()):
                regressions.append({'variant':name,'query_type':kind,'recall_delta':deltas['recall_at_k'],'ndcg_delta':deltas['ndcg_at_k'],'regressed_metrics':[metric for metric,delta in deltas.items() if delta<0]})
    eligible=[name for name,metrics in variants.items() if metrics['p95_latency_ms']<=run.spec['latency_budget_ms'] and not any(r['variant']==name for r in regressions) and metrics['ndcg_at_k']>baseline['ndcg_at_k']]
    winner=max(eligible,key=lambda name:variants[name]['ndcg_at_k']) if eligible else None
    settings={r['variant']:r['settings'] for r in rows}
    return {'baseline':baseline,'variants':variants,'query_type_regressions':regressions,'score_types':{'keyword':'BM25','vector':'transformed cosine','hybrid':'RRF','semantic':'RRF plus separate @search.rerankerScore'},'decision':'ADOPT' if winner else 'RETAIN_BASELINE','selected_variant':winner,'selected_settings':settings[winner] if winner else {'mode':'hybrid','depth':10},'latency_budget_ms':run.spec['latency_budget_ms'],'example_rows':rows[:2]}

def ab_experiment_contract(run):
    """Persist the predeclared experiment before the first retrieval or assignment."""
    require(run.spec.get('primary_metric')=='manual_answer_support','Declare manual_answer_support as the primary metric before starting this experiment.')
    require(run.spec.get('stop_rule')=='fixed_sessions_no_early_efficacy','Declare the fixed-session stop rule before starting this experiment.')
    require(type(run.spec.get('sessions')) is int and run.spec['sessions']>0,'Declare a positive fixed session count.')
    contract={'run_id':run.state['run_id'],'primary_metric':run.spec['primary_metric'],'stop_rule':f"fixed {run.spec['sessions']} sessions; no early efficacy stopping",'session_count':run.spec['sessions'],'variants':{'A':{'mode':'vector','size':64,'depth':10},'B':{'mode':'semantic','size':128,'depth':50}},'fixed_generation':{'deployment':run.config.get('foundry_deployment'),'model_version':run.config.get('foundry_version'),'max_completion_tokens':512,'reasoning_effort':'none','prompt_version':'rag-json-v1'}}
    path=run.path/'ab-experiment-contract.json'; record=run.state.get('ab_experiment_contract')
    if path.exists():
        require(record is not None and record.get('path')==str(path) and digest(path)==record.get('sha256'),'Predeclared A/B contract changed or its run identity is missing.')
        saved=read(path)
        require({k:saved.get(k) for k in contract}==contract,'A/B metric, stop rule, assignment count or response settings changed after predeclaration. Start a new run.')
    else:
        require(record is None and not (run.path/'ab-observations.json').exists(),'A/B assignments exist without their predeclared contract; retain this run and start a new experiment.')
        write(path,{**contract,'declared_at':now()})
        run.state['ab_experiment_contract']={'path':str(path),'sha256':digest(path)}; run.save()
    return {**read(path),'path':str(path),'sha256':digest(path)}

def rag_ab(run,n):
    experiment=ab_experiment_contract(run)
    a=Azure(run)
    if n==1:
        a.prepare_index(); rows=[]; settings=experiment['variants']
        for variant,params in settings.items():
            for q in validation():
                kept,_,elapsed=a.query(q,**params); response,gen_ms,tokens=a.generate(q['question'],kept,trace={'query_id':q['query_id'],'variant':variant})
                rows.append({'variant':variant,'query_id':q['query_id'],'query_type':q['query_type'],'question':q['question'],'supplied_context':kept,'reference_response':q['response'],'generation_evidence':a.last_generation_evidence,'raw_response':response,'retrieved_source_ids':[r['source_id'] for r in kept],'latency_ms':elapsed+gen_ms,'output_tokens':tokens,**retrieval_metrics(kept,q),**answer_metrics(response,q)})
        write_jsonl(run.attempt/'outcomes.jsonl',rows)
        review_path,_=prepare_manual_review(run,'rag-variants',rows)
        return {'experiment_contract':experiment,'manual_review_path':str(review_path),'rows':rows,'settings':settings,'fixed_generation':experiment['fixed_generation'],'variants':{v:summarize([r for r in rows if r['variant']==v]) for v in settings}}
    if n==2:
        rows=run.previous(1)['rows']; reviewed=manual_review(run,'rag-variants',rows); lookup={(r['variant'],r['query_id']):r for r in reviewed['rows']}
        regressions=[{'query_id':q['query_id'],'A':lookup['A',q['query_id']],'B':lookup['B',q['query_id']]} for q in validation() if any(lookup['B',q['query_id']][k]<lookup['A',q['query_id']][k] for k in ('recall_at_k','ndcg_at_k','manual_correctness','manual_answer_support'))]
        return {'manual_semantic_review':reviewed,'comparison':run.previous(1)['variants'],'regressions':regressions,'regression_observed':bool(regressions),'automatic_proxy_mismatches':[{'query_id':q['query_id'],'A':lookup['A',q['query_id']]['answer_support_proxy'],'B':lookup['B',q['query_id']]['answer_support_proxy']} for q in validation() if lookup['B',q['query_id']]['answer_support_proxy']<lookup['A',q['query_id']]['answer_support_proxy']],'interpretation':'Regressions use retrieval metrics and reviewed semantic correctness/support. Automatic proxy mismatches are diagnostics only. If no real regression is observed, do not invent one.'}
    observed_path=run.path/'ab-observations.json'
    if not observed_path.exists():
        sessions=[]
        for i in range(run.spec['sessions']):
            session=f'synthetic-session-{i:03}'; arm=assignment(session); q=validation()[i%len(validation())]; settings=run.previous(1)['settings'][arm]
            sessions.append({'session_id':session,'arm':arm,'query_id':q['query_id'],'query_type':q['query_type'],'settings':settings,'settings_hash':object_hash(settings),'assigned_at':now(),'status':'PENDING','exposures':[],'outcome':None,'population':'synthetic sessions'})
        write(observed_path,{'run_id':run.state['run_id'],'experiment_contract_sha256':experiment['sha256'],'sessions':sessions})
        run.state['ab_observations']={'path':str(observed_path),'sha256':digest(observed_path)}; run.save()
    observed=run.state['ab_observations']; require(digest(observed_path)==observed['sha256'],'A/B observations changed outside the runner.')
    observations=read(observed_path)
    require(observations.get('experiment_contract_sha256')==experiment['sha256'],'A/B assignments reference a different predeclared experiment.')
    def persist():
        write(observed_path,observations); run.state['ab_observations']['sha256']=digest(observed_path); run.save()
        write_jsonl(run.path/'ab-exposures.jsonl',[{k:v for k,v in row.items() if k!='outcome'} for row in observations['sessions']])
        write_jsonl(run.path/'ab-outcomes.jsonl',[row['outcome'] for row in observations['sessions'] if row['outcome'] is not None])
    require(all(row['status'] in ('PENDING','COMPLETED') for row in observations['sessions']),'A/B experiment has failed or interrupted attempts. They remain in the denominator; analysis is HOLD. Start a new run for a new experiment, never erase or replay these assignments as fresh observations.')
    questions={q['query_id']:q for q in validation()}
    for row in observations['sessions']:
        if row['status']=='COMPLETED': continue
        q=questions[row['query_id']]; row['status']='STARTED'; row['exposures'].append({'event':'retrieval_dispatched','at':now(),'delivery':'unconfirmed until response'}); persist(); started=time.perf_counter()
        try:
            kept,_,elapsed=a.query(q,**row['settings']); row['exposures'].append({'event':'retrieval_response_observed','at':now(),'source_ids':[r['source_id'] for r in kept]}); row['exposures'].append({'event':'generation_dispatched','at':now()}); persist()
            response,gen_ms,tokens=a.generate(q['question'],kept,trace={'query_id':q['query_id'],'session_id':row['session_id'],'variant':row['arm']})
            row['outcome']={'session_id':row['session_id'],'arm':row['arm'],'query_id':q['query_id'],'query_type':q['query_type'],'settings_hash':row['settings_hash'],'status':'COMPLETED','question':q['question'],'supplied_context':kept,'reference_response':q['response'],'generation_evidence':a.last_generation_evidence,'latency_ms':elapsed+gen_ms,'output_tokens':tokens,'raw_response':response,**answer_metrics(response,q)}; row['status']='COMPLETED'; persist()
        except BaseException as exc:
            row['status']='FAILED' if isinstance(exc,Exception) else 'INTERRUPTED'; row['outcome']={'session_id':row['session_id'],'arm':row['arm'],'query_id':q['query_id'],'settings_hash':row['settings_hash'],'status':row['status'],'error_type':type(exc).__name__,'error':str(exc),'latency_ms':(time.perf_counter()-started)*1000,'response_observed':False}; persist(); raise
    outcomes=[row['outcome'] for row in observations['sessions']]; require(len(outcomes)==run.spec['sessions'] and all(row['status']=='COMPLETED' for row in outcomes),'Missing A/B outcomes remain HOLD.')
    reviewed=manual_review(run,'rag-ab',outcomes); outcomes=reviewed['rows']
    for file in ('ab-experiment-contract.json','ab-observations.json','ab-exposures.jsonl','ab-outcomes.jsonl','rag-ab-review.jsonl'): shutil.copy2(run.path/file,run.attempt/file)
    summaries={v:summarize([r for r in outcomes if r['arm']==v]) for v in ('A','B')}
    delta=reviewed['by_variant']['B']['manual_answer_support']-reviewed['by_variant']['A']['manual_answer_support']
    report={'experiment_contract':experiment,'manual_semantic_review':reviewed,'primary_metric':experiment['primary_metric'],'stop_rule':experiment['stop_rule'],'arm_summary':summaries,'assigned_sessions':len(observations['sessions']),'completed_outcomes':len(outcomes),'failed_outcomes':0,'difference_B_minus_A':delta,'uncertainty':'Not estimated: synthetic sessions repeat eight correlated questions; no inferential confidence interval is justified. Collect independent sessions and more source groups.','decision':'COLLECT_MORE_EVIDENCE','limitations':'No claim about production users or statistical significance.'}
    report.update(a.track('rag-ab',{'support_delta':delta},run.attempt)); return report

def index_tuned_checkpoint(a,artifact):
    from sentence_transformers import SentenceTransformer
    checkpoint=Path(artifact['output_path'])/'checkpoint'; require(checkpoint.is_dir(),'Selected embedding checkpoint missing.')
    model=SentenceTransformer(str(checkpoint),device='cpu'); require(model.get_sentence_embedding_dimension()==384,'Embedding dimensions changed; do not mix fields.')
    a.run.state['tuned_checkpoint_job']=artifact['job_name']; a.run.save()
    chunks=a.run.state['chunks']; vectors=model.encode([r['content'] for r in chunks],normalize_embeddings=True).tolist()
    records=[{'@search.action':'merge','id':r['id'],'tuned_vector':v,'tuned_checkpoint_job':artifact['job_name']} for r,v in zip(chunks,vectors)]
    for i in range(0,len(records),100):
        response,_=a.search(f"indexes/{a.c['search_index']}/docs/index",{'value':records[i:i+100]}); require(all(x['status'] for x in response['value']),'Tuned-vector indexing failed.')
    return model

def prepare_retrieval(a):
    settings=a.c.get('adopted_retrieval'); require(isinstance(settings,dict) and settings,'Declare the reviewed adopted_retrieval settings in config.local.json.')
    a.prepare_index(); encoder=None
    if settings.get('field')=='tuned_vector':
        proof=a.run.dependency('m2-demo1',3); require(proof['decision']=='ADOPT','Tuned embedding was not adopted against both baselines.')
        encoder=index_tuned_checkpoint(a,proof['checkpoint_artifact'])
    return settings,encoder

def questions_with_context(a,questions):
    settings,encoder=prepare_retrieval(a)
    return [{**q,'retrieved_context':a.query(q,encoder=encoder,**settings)[0] if q['relevance'] else []} for q in questions]

def embedding_train(run,n):
    a=Azure(run)
    if n==1: return submit(a,'train_embedding',run.spec)
    if n==2: return completed(a,run.previous(1))
    artifact=run.previous(2); a.prepare_index(); model=index_tuned_checkpoint(a,artifact)
    size=run.config.get('adopted_retrieval',{}).get('size',128)
    baseline=sweep(a,{'minilm':{'field':'mini_vector','size':size},'bge':{'field':'bge_vector','size':size}})
    tuned=sweep(a,{'tuned':{'field':'tuned_vector','size':size}},encoder=model)
    beats=all(tuned['variants']['tuned']['ndcg_at_k']>metrics['ndcg_at_k'] for metrics in baseline['variants'].values())
    return {'decision':'ADOPT' if beats else 'REJECT','selection_metric':'ndcg_at_k','baseline':baseline,'tuned':tuned,'checkpoint_job':artifact['job_name'],'checkpoint_artifact':artifact,'checkpoint_manifest_sha256':artifact['result_sha256'],'query_and_document_encoder_identical':True,'held_out_split':'validation; final test remains unused for selection'}

def synthetic_data(run,n):
    a=Azure(run)
    if n==1:
        rows=[]
        for doc in [d for d in jsonl(ROOT/'data/corpus.jsonl') if d['split']=='train']:
            raw,elapsed,tokens=a.generate('Generate one example.',[doc],synthetic=True,trace={'source_id':doc['source_id']}); parsed=json.loads(raw)
            rows.append({'example_id':uid(),'source_group':doc['source_group'],'source_ids':parsed['source_ids'],'question':parsed['question'],'answer':parsed['answer'],'source_sha256':object_hash(doc),'prompt_version':'synthetic-json-v1','generator':run.config['foundry_model'],'generator_version':run.config['foundry_version'],'generation_evidence':a.last_generation_evidence,'raw_response':raw})
        write_jsonl(run.path/'generated.jsonl',rows)
        write_jsonl(run.path/'review.jsonl',[{'example_id':r['example_id'],'example_sha256':object_hash(r),'decision':'PENDING','reason':'','reviewer':''} for r in rows])
        return {'generated_path':str(run.path/'generated.jsonl'),'review_path':str(run.path/'review.jsonl'),'examples':len(rows),'next_action':'In VS Code compare each generated claim and condition against data/corpus.jsonl. Edit review.jsonl: ACCEPT or REJECT, reason, reviewer. Do not auto-approve.'}
    rows=jsonl(run.path/'generated.jsonl'); docs={r['source_id']:r for r in jsonl(ROOT/'data/corpus.jsonl')}
    require(len({r['question'].strip().casefold() for r in rows})==len(rows),'Duplicate generated prompt.')
    for row in rows:
        require(isinstance(row['question'],str) and isinstance(row['answer'],str) and row['source_ids'],'Invalid synthetic schema.')
        require(all(isinstance(s,str) and s in docs and docs[s]['split']=='train' and docs[s]['source_group']==row['source_group'] for s in row['source_ids']),'Synthetic source reference or group leakage.')
        require(len(row['source_ids'])==1 and row['source_sha256']==object_hash(docs[row['source_ids'][0]]),'Synthetic source identity/hash changed.')
    reviews=jsonl(run.path/'review.jsonl'); by_id={r['example_id']:r for r in reviews}
    require(len(reviews)==len(rows) and len(by_id)==len(rows) and set(by_id)=={r['example_id'] for r in rows},'Review coverage must exactly match generated examples.')
    require(all(by_id[row['example_id']].get('example_sha256')==object_hash(row) for row in rows),'Generated example changed after manual review was prepared.')
    require(all(r['decision'] in ('ACCEPT','REJECT') and r['reason'].strip() and r['reviewer'].strip() for r in reviews),'Manual review is incomplete. Fill decision, reason and reviewer for every row.')
    accepted=[r for r in rows if by_id[r['example_id']]['decision']=='ACCEPT']; require(accepted,'At least one supported example must be accepted.')
    if n==2:
        folder=run.path/'reviewed-data'; folder.mkdir(exist_ok=False); write_jsonl(folder/'accepted.jsonl',accepted); write_jsonl(folder/'review-decisions.jsonl',reviews)
        write_jsonl(folder/'rejected.jsonl',[{**r,'review':by_id[r['example_id']]} for r in rows if by_id[r['example_id']]['decision']=='REJECT'])
        for split in ('validation','test'): write_jsonl(folder/f'{split}.jsonl',[r for r in jsonl(ROOT/'data/queries.jsonl') if r['split']==split])
        hashes={p.name:digest(p) for p in folder.iterdir()}; write(folder/'hashes.json',hashes)
        return {'accepted':len(accepted),'rejected':len(rows)-len(accepted),'data_path':str(folder),'hashes':hashes,'review_scope':'human factual support against original source plus automated structural/split checks'}
    from azure.ai.ml.entities import Data
    folder=Path(run.previous(2)['data_path']); require(all(digest(folder/name)==sha for name,sha in run.previous(2)['hashes'].items()),'Reviewed data changed after approval.')
    version=run.state['run_id'].replace('-',''); assets={}
    # Separate train/validation/test assets avoid accidental final-test mount during training.
    for name in ('accepted','review-decisions','rejected','validation','test','hashes'):
        path=folder/(name+'.json' if name=='hashes' else name+'.jsonl')
        asset=a.ml.data.create_or_update(Data(name='ai300-'+name,version=version,type='uri_file',path=str(path),description='Original support data; reviewed example and split lineage',tags={'sha256':digest(path),'course':'ai300'})); assets[name]=asset.id
    train_bundle=run.attempt/'training-data'; train_bundle.mkdir()
    for name in ('accepted.jsonl','validation.jsonl','hashes.json'): shutil.copy2(folder/name,train_bundle/name)
    asset=a.ml.data.create_or_update(Data(name='ai300-training-bundle',version=version,type='uri_folder',path=str(train_bundle),tags={'train_hash':digest(folder/'accepted.jsonl'),'validation_hash':digest(folder/'validation.jsonl')})); assets['training_bundle']=asset.id
    return {'data_assets':assets,'version':version,'hashes':run.previous(2)['hashes'],'final_test_separate':True}

def lora_train(run,n):
    a=Azure(run)
    if n==1:
        synthetic=run.dependency('m2-demo2',3); return {'configuration':run.spec,'data_assets':synthetic['data_assets'],'response_only_loss':'Prompt labels are -100; only JSON response and EOS contribute to loss.','source':'jobs/train_lora.py'}
    if n==2:
        # Submission is idempotent across attempts: retain job identity before inspection.
        if 'training_submission' not in run.state:
            run.state['training_submission']=submit(a,'train_lora',run.spec,data=run.previous(1)['data_assets']['training_bundle']); run.save()
        return completed(a,run.state['training_submission'])
    job=run.previous(2); result=job['result']; path=Path(job['output_path']); history=result['history']
    divergence=len(history)>1 and history[-1]['training_loss']<history[0]['training_loss'] and history[-1]['validation_loss']>history[0]['validation_loss']
    return {'job_name':job['job_name'],'history':history,'divergence_observed':divergence,'base':read(path/'base-validation.json'),'adapted':read(path/'adapted-validation.json'),'diagnosis':'Training/validation divergence observed; inspect the failure rows.' if divergence else 'No loss divergence in this run; inspect actual task failures before tuning.','selected_epoch':result['selected_epoch'],'output_path':job['output_path'],'output_uri':job['output_uri'],'result':result}

def lora_select(run,n):
    """Implement Demo: Tune LoRA rank and select checkpoints in Azure ML using the numbered learner steps."""
    # Step 1: Configure a second CPU command job that changes only the LoRA rank, with the alpha-to-rank ratio, base model, data splits, seed, learning rate, target modules, and training budget held fixed
    # Step 2: Compare both completed runs in MLflow using validation loss, elapsed time, and task outputs, and judge whether the higher rank earns its extra CPU cost
    # Step 3: Shortlist the best checkpoint from each run by validation loss, then save each adapter with the exact base-model revision, tokenizer, data, and environment versions
    raise Hold("STARTER: Implement lora_select; compare origin/m2-demo4-after.")

def model_evaluate(run,n):
    a=Azure(run); selected=run.dependency('m2-demo4',3)
    if n==1:
        settings,encoder=prepare_retrieval(a)
        contexts={q['query_id']:a.query(q,encoder=encoder,**settings)[0] if q['relevance'] else [] for q in validation(domain=False)}
        candidates=selected['shortlisted_checkpoints']; require(len(candidates)==2,'Both shortlisted checkpoints are required.')
        config={**run.spec,'retrieved_context':contexts,'retrieval_settings':settings,'retrieved_context_sha256':object_hash(contexts)}
        return submit(a,'evaluate',config,adapter=candidates[0]['output_uri'],adapter2=candidates[1]['output_uri'])
    if n==2:
        job=completed(a,run.previous(1)); review_path,_=prepare_manual_review(run,'model-validation',[{**r,'variant':name} for name,value in job['result']['results'].items() for r in value['rows']]); return {**job,'manual_review_path':str(review_path),'failure_rows':{name:[r for r in report['rows'] if not all(r[k] for k in ('correctness','answer_support_proxy','schema_validity'))] for name,report in job['result']['results'].items()}}
    report=run.previous(2); results=report['result']['results']; reviewed=manual_review(run,'model-validation',[{**r,'variant':name} for name,value in results.items() for r in value['rows']])
    base=summarize([r for r in reviewed['rows'] if r['variant']=='base']); candidates={name:summarize([r for r in reviewed['rows'] if r['variant']==name]) for name in ('adapter','adapter2')}; gates=run.spec['gates']
    eligible=[name for name,metrics in candidates.items() if all(metrics[key]>=floor and metrics[key]>=base[key]-gates['max_regression'] and all(group[key]>=floor and group[key]>=base['by_query_type'][kind][key]-gates['max_regression'] for kind,group in metrics['by_query_type'].items()) for key,floor in gates.items() if key!='max_regression')]
    winner=max(eligible or list(candidates),key=lambda name:candidates[name]['manual_correctness']); candidate=candidates[winner]
    checkpoint=selected['shortlisted_checkpoints'][0 if winner=='adapter' else 1]
    selected={**selected,'selected_job':checkpoint['job_name'],'output_path':checkpoint['output_path'],'output_uri':checkpoint['output_uri'],'result':checkpoint['result']}
    checks={key:candidate[key]>=floor and candidate[key]>=base[key]-gates['max_regression'] for key,floor in gates.items() if key!='max_regression'}
    for kind in ('general','exact_identifier','paraphrase'):
        for key,floor in gates.items():
            if key=='max_regression': continue
            checks[kind+'_'+key]=candidate['by_query_type'][kind][key]>=floor and candidate['by_query_type'][kind][key]>=base['by_query_type'][kind][key]-gates['max_regression']
    checks.update(quality_checks([r for r in reviewed['rows'] if r['variant']==winner],gates,run.spec.get('minimum_by_query_type',{}),[r for r in reviewed['rows'] if r['variant']=='base']))
    return {'manual_semantic_review':reviewed,'automatic_proxy_use':'diagnostics only; never acceptance','decision':'PASS' if all(checks.values()) else 'REJECT','gate_checks':checks,'base':base,'candidate':candidate,'selected_job':selected['selected_job'],'selected_output_path':selected['output_path'],'selected_output_uri':selected['output_uri'],'selected_result':selected['result'],'evaluation_job':report['job_name'],'evaluation_hash':report['result_sha256'],'validation_hash':report['result']['validation_sha256'],'config':report['result']['config']}


def model_deploy(run,n):
    a=Azure(run)
    if n==1:
        from azure.ai.ml.entities import Model
        from huggingface_hub import snapshot_download
        evaluation=run.dependency('m3-demo1',3); require(evaluation['decision']=='PASS','Validation gates rejected candidate; registration/deployment blocked.')
        selected=Path(evaluation['selected_output_path']); bundle=run.attempt/'model-bundle'; bundle.mkdir()
        revision=evaluation['selected_result']['base_revision']; require(revision==run.config['model_revisions']['Qwen/Qwen3-0.6B'],'Selected base revision differs from requested deployment.')
        base=snapshot_download('Qwen/Qwen3-0.6B',revision=revision,allow_patterns=['*.json','*.safetensors','*.txt','*.model','*.jinja']); shutil.copytree(base,bundle/'base')
        for folder in ('adapter','tokenizer'): shutil.copytree(selected/folder,bundle/folder)
        version=run.state['run_id'].replace('-',''); identity={'model_name':'ai300-support-lora','model_version':version,'base_model':'Qwen/Qwen3-0.6B','base_revision':revision,'training_job':evaluation['selected_job'],'training_data_sha256':evaluation['selected_result']['data_sha256'],'validation_job':evaluation['evaluation_job'],'validation_sha256':evaluation['validation_hash'],'validation_report_sha256':evaluation['evaluation_hash'],'tokenizer_sha256':object_hash({p.name:digest(p) for p in (bundle/'tokenizer').iterdir() if p.is_file()}),'prompt_version':'support-json-v1'}
        write(bundle/'identity.json',identity); write(bundle/'validation-evidence.json',evaluation)
        model=a.ml.models.create_or_update(Model(name=identity['model_name'],version=version,path=str(bundle),type='custom_model',description='CPU Qwen3 model, LoRA adapter, tokenizer and validation lineage',tags={'course':'ai300','training_job':identity['training_job'],'validation_job':identity['validation_job']}))
        return {'model_id':model.id,'model_identity':identity,'bundle_path':str(bundle),'bundle_hashes':{str(p.relative_to(bundle)):digest(p) for p in bundle.rglob('*') if p.is_file()}}
    if n==2:
        from azure.ai.ml.entities import ManagedOnlineDeployment, CodeConfiguration, OnlineRequestSettings
        baseline=a.ml.online_deployments.get(run.config['baseline_deployment'],run.config['endpoint']); endpoint=course_endpoint(a)
        require(baseline.provisioning_state=='Succeeded','Existing baseline must be genuinely deployed first.')
        require(endpoint.traffic.get(run.config['baseline_deployment'])==100,'Start with baseline at 100 percent.')
        require(run.config['candidate_deployment']!=run.config['baseline_deployment'],'Candidate and baseline must differ.')
        # Never overwrite an existing deployment with this short course name.
        existing={d.name for d in a.ml.online_deployments.list(run.config['endpoint'])}
        require(run.config['candidate_deployment'] not in existing,'Candidate name already exists; clean up or choose a fresh name.')
        serving_environment=resolve_environment(a.ml,run.config['serving_environment'],'serve-conda.yml')
        deployment=ManagedOnlineDeployment(name=run.config['candidate_deployment'],endpoint_name=run.config['endpoint'],model=run.previous(1)['model_id'],environment=serving_environment['id'],code_configuration=CodeConfiguration(code=str(ROOT/'serving'),scoring_script='score.py'),instance_type=run.config['endpoint_instance_type'],instance_count=1,environment_variables={'DEPLOYMENT_NAME':run.config['candidate_deployment'],'OMP_NUM_THREADS':'4','HF_HUB_OFFLINE':'1'},request_settings=OnlineRequestSettings(request_timeout_ms=180000,max_concurrent_requests_per_instance=1),tags={'course':'ai300','run_id':run.state['run_id']})
        require(not any(x in run.config['endpoint_instance_type'].upper() for x in ('STANDARD_N','GPU')),'CPU instance required.')
        # Submit without blocking for deployment completion; step 3 reads genuine completed state.
        run.state['resources']['candidate_deployment']=deployment.name; run.state['resources']['endpoint']=run.config['endpoint']; run.save()
        poller=a.ml.online_deployments.begin_create_or_update(deployment)
        return {'endpoint':endpoint.name,'candidate_deployment':deployment.name,'model_id':run.previous(1)['model_id'],'environment':serving_environment['id'],'environment_identity':serving_environment,'scoring_sha256':digest(ROOT/'serving/score.py'),'traffic_before':endpoint.traffic,'status':'SUBMITTED','continuation_token':poller.continuation_token()}
    candidate=a.ml.online_deployments.get(run.config['candidate_deployment'],run.config['endpoint']); endpoint=course_endpoint(a)
    require(candidate.provisioning_state=='Succeeded',f'Deployment is {candidate.provisioning_state}; inspect Azure ML and retry after success.')
    require(endpoint.traffic.get(run.config['baseline_deployment'])==100 and endpoint.traffic.get(run.config['candidate_deployment'],0)==0,'Candidate must remain at zero traffic.')
    q=validation()[0]; response,elapsed=a.invoke(endpoint_payload(q,96),run.config['candidate_deployment'])
    require(response['model_identity']==run.previous(1)['model_identity'],'Direct candidate identity does not match registered asset.')
    baseline,base_ms=a.invoke(endpoint_payload(q,96))
    require(baseline['deployment']==run.config['baseline_deployment'],'Baseline is not serving routed requests.')
    snapshot=deployment_snapshot(a,run.config['candidate_deployment']); require(snapshot['environment_id']==run.previous(2)['environment'] and snapshot['model_id']==run.previous(1)['model_id'],'Deployed assets differ from registered model/environment.')
    baseline_snapshot=deployment_snapshot(a,run.config['baseline_deployment'])
    return {'baseline_deployment_snapshot':baseline_snapshot,'baseline_model_identity':baseline['model_identity'],'endpoint_auth_mode':endpoint.auth_mode,'deployment_snapshot':snapshot,'environment_identity':run.previous(2)['environment_identity'],'provisioning_state':candidate.provisioning_state,'traffic':endpoint.traffic,'model_identity':response['model_identity'],'smoke_response':response,'smoke_metrics':answer_metrics(response['response'],q),'latency_ms':elapsed,'baseline_response':baseline,'model_id':run.previous(1)['model_id'],'environment':run.previous(2)['environment'],'scoring_sha256':run.previous(2)['scoring_sha256']}

def endpoint_payload(q,limit):
    return {'question':q['question'],'evidence':q.get('retrieved_context',[]),'max_new_tokens':limit}

def endpoint_workload(a,questions,limit,deployment,expected_identity=None,minimum_seconds=0,max_requests=None):
    rows=[]; started=now(); clock=time.monotonic(); maximum=max_requests or len(questions)
    for i in range(maximum):
        q=questions[i%len(questions)]; response,elapsed=a.invoke(endpoint_payload(q,limit),deployment)
        if expected_identity is not None: require(response['model_identity']==expected_identity,'Model identity changed during workload.')
        rows.append({'query_id':q['query_id'],'query_type':q['query_type'],'question':q['question'],'supplied_context':endpoint_payload(q,limit)['evidence'],'reference_response':q['response'],'model_identity':response['model_identity'],'deployment':response['deployment'],'raw_response':response['response'],'latency_ms':elapsed,'output_tokens':response['output_tokens'],**answer_metrics(response['response'],q)})
        if i+1>=len(questions) and time.monotonic()-clock>=minimum_seconds: break
    elapsed=time.monotonic()-clock
    return {'rows':rows,'summary':summarize(rows),'max_new_tokens':limit,'window_start':started,'window_end':now(),'window_complete':elapsed>=minimum_seconds,'observation_seconds':elapsed,'population':'controlled repeated questions; not independent users'}

def endpoint_test(run,n):
    a=Azure(run); deployment=run.dependency('m3-demo2',3); identity=deployment['model_identity']
    current=deployment_snapshot(a,run.config['candidate_deployment']); require(current==deployment['deployment_snapshot'],'Candidate deployment model/environment/code/runtime settings changed after smoke evidence.')
    if n==1:
        observations=run.path/'validation-benchmarks.json'
        if 'benchmark_observations' not in run.state:
            questions=questions_with_context(a,validation(domain=False))
            results={str(limit):endpoint_workload(a,questions,limit,run.config['candidate_deployment'],identity,minimum_seconds=run.spec.get('minimum_observation_seconds',0),max_requests=run.spec.get('max_observation_requests')) for limit in run.spec['token_limits']}
            write(observations,results); run.state['benchmark_observations']={'path':str(observations),'sha256':digest(observations)}; run.save()
        require(digest(observations)==run.state['benchmark_observations']['sha256'],'Validation benchmark observations changed.')
        results=read(observations)
        if run.spec.get('minimum_observation_seconds',0): require(all(v.get('window_complete') for v in results.values()),'Bounded benchmark did not sustain the declared observation window; do not attribute partial-minute telemetry. Review the request budget and start a new run.')
        snapshots={limit:monitor_snapshot(a,value['window_start'],value['window_end']) for limit,value in results.items()}
        for snapshot in snapshots.values(): require_monitor_coverage(snapshot,run,[run.config['candidate_deployment']])
        reviewed=manual_review(run,'validation-limits',[{**r,'variant':limit} for limit,value in results.items() for r in value['rows']])
        semantic={limit:summarize([r for r in reviewed['rows'] if r['variant']==limit]) for limit in results}
        eligible=[]
        for limit,summary in semantic.items():
            rows=[r for r in reviewed['rows'] if r['variant']==limit]
            checks=quality_checks(rows,run.spec['gates'],run.spec.get('minimum_by_query_type',{}))
            checks.update(resource_checks(snapshots[limit],run,[run.config['candidate_deployment']]))
            checks['latency']=summary['p95_latency_ms']<=run.spec['latency_budget_ms']
            if all(checks.values()): eligible.append(limit)
        require(eligible,'No validation output-length setting passes human semantic and schema gates; final test remains unopened.')
        selected=min(eligible,key=lambda key:semantic[key]['p95_latency_ms'])
        return {'manual_semantic_review':reviewed,'benchmarks':results,'utilization_evidence':snapshots,'semantic_quality_by_limit':semantic,'automatic_proxy_use':'diagnostics only; never acceptance','selected_max_new_tokens':int(selected),'selection_rule':'minimum validation p95 latency among settings passing human correctness/support and schema floors in every query type','model_identity':identity}
    require(current['request_timeout_ms']==run.spec['request_timeout_ms'],'Deployment timeout differs from the declared frozen choice.')
    if n==2:
        # The test ledger is dataset-global, not run-local. A new run cannot erase prior consumption.
        questions=[q for q in jsonl(ROOT/'data/queries.jsonl') if q['split']=='test']; dataset_hash=object_hash(questions)
        ledger=ROOT/'.state'/'consumed-final-tests'/f'{dataset_hash}.json'
        require(not ledger.exists(),'This final-test set has already been opened. After tuning, obtain a new untouched test set; do not delete its ledger.')
        require(deployment_snapshot(a,run.config['baseline_deployment'])==deployment['baseline_deployment_snapshot'],'Baseline changed before final test.')
        frozen={'baseline_deployment_snapshot':deployment['baseline_deployment_snapshot'],'baseline_model_identity':deployment['baseline_model_identity'],'endpoint_auth_mode':deployment['endpoint_auth_mode'],'deployment_snapshot':current,'environment_identity':deployment['environment_identity'],'model_id':deployment['model_id'],'model_identity':identity,'environment':deployment['environment'],'scoring_sha256':deployment['scoring_sha256'],'request_timeout_ms':current['request_timeout_ms'],'max_new_tokens':run.previous(1)['selected_max_new_tokens'],'do_sample':False,'test_sha256':dataset_hash,'retrieval_settings':run.config['adopted_retrieval']}
        write(run.path/'frozen-release.json',frozen); ledger.parent.mkdir(parents=True,exist_ok=True)
        with ledger.open('x') as handle: json.dump({'opened_at':now(),'run':str(run.path),'release_hash':object_hash(frozen),'status':'OPENED_NO_RERUN'},handle)
        questions=questions_with_context(a,questions)
        frozen['retrieved_test_context_sha256']=object_hash({q['query_id']:q['retrieved_context'] for q in questions})
        write(run.path/'frozen-release.json',frozen)
        write(ledger,{'opened_at':now(),'run':str(run.path),'release_hash':object_hash(frozen),'status':'OPENED_NO_RERUN'})
        baseline=endpoint_workload(a,questions,frozen['max_new_tokens'],run.config['baseline_deployment'],deployment['baseline_model_identity'],minimum_seconds=run.spec.get('minimum_observation_seconds',0),max_requests=run.spec.get('max_observation_requests'))
        result=endpoint_workload(a,questions,frozen['max_new_tokens'],run.config['candidate_deployment'],identity,minimum_seconds=run.spec.get('minimum_observation_seconds',0),max_requests=run.spec.get('max_observation_requests'))
        result['baseline_comparison']=baseline
        review_path,_=prepare_manual_review(run,'final-test',[{**r,'variant':name} for name,value in [('baseline',baseline),('candidate',result)] for r in value['rows']])
        return {'manual_review_path':str(review_path),'frozen_release':frozen,'frozen_release_sha256':object_hash(frozen),'final_test':result,'test_ledger':str(ledger)}
    previous=run.previous(2)
    if run.spec.get('minimum_observation_seconds',0): require(previous['final_test'].get('window_complete') and previous['final_test']['baseline_comparison'].get('window_complete'),'Final-test observation windows incomplete; retain baseline and preserve consumed-test evidence.')
    snapshot=monitor_snapshot(a,previous['final_test']['baseline_comparison']['window_start'],previous['final_test']['window_end']); require_monitor_coverage(snapshot,run,[run.config['baseline_deployment'],run.config['candidate_deployment']])
    final=previous['final_test']; baseline=final['baseline_comparison']
    reviewed=manual_review(run,'final-test',[{**r,'variant':name} for name,value in [('baseline',baseline),('candidate',final)] for r in value['rows']])
    candidate_rows=[r for r in reviewed['rows'] if r['variant']=='candidate']; baseline_rows=[r for r in reviewed['rows'] if r['variant']=='baseline']
    summary=summarize(candidate_rows); checks=quality_checks(candidate_rows,run.spec['gates'],run.spec.get('minimum_by_query_type',{}),baseline_rows)
    checks['p95_latency_ms']=summary['p95_latency_ms']<=run.spec['latency_budget_ms']
    checks.update(resource_checks(snapshot,run,[run.config['candidate_deployment']]))
    decision='PASS' if all(checks.values()) else 'REJECT'; result={'manual_semantic_review':reviewed,'semantic_quality_summary':summary,'automatic_proxy_use':'diagnostics only; never acceptance','release_decision':decision,'utilization_evidence':snapshot,'baseline_comparison':previous['final_test']['baseline_comparison'],'gate_checks':checks,'final_test':previous['final_test'],'frozen_release':previous['frozen_release'],'frozen_release_sha256':previous['frozen_release_sha256'],'next_action':'Proceed to controlled canary.' if decision=='PASS' else 'Retain baseline. Further tuning requires a new untouched test set.'}
    write(run.attempt/'release-evidence.json',result)
    result.update(a.track('final-test',{'release_pass':int(decision=='PASS')},run.attempt))
    model=a.ml.models.get(name=identity['model_name'],version=identity['model_version'])
    model.tags={**(model.tags or {}),'release_mlflow_run_id':result['mlflow_run_id'],'release_evidence_sha256':digest(run.attempt/'release-evidence.json'),'frozen_release_sha256':previous['frozen_release_sha256']}
    a.ml.models.create_or_update(model)
    return result


def endpoint_resource(run): return f"/subscriptions/{run.config['subscription_id']}/resourceGroups/{run.config['resource_group']}/providers/Microsoft.MachineLearningServices/workspaces/{run.config['workspace']}/onlineEndpoints/{run.config['endpoint']}"

def monitor_snapshot(a,start=None,end=None):
    resource=endpoint_resource(a.run); end=end or now(); start=start or a.run.state['started_at']
    groups=[(resource,['RequestLatency_P95'],'deployment eq \u0027*\u0027'),(resource,['RequestsPerMinute'],"deployment eq '*' and statusCodeClass eq '*'")]
    for deployment in (a.c['baseline_deployment'],a.c['candidate_deployment']):
        groups.append((resource+'/deployments/'+deployment,['CpuUtilizationPercentage','CpuMemoryUtilizationPercentage'],None))
    snapshots=[]
    for scope,names,dimension in groups:
        # Metric definitions are the authority for exact names and supported dimensions.
        definitions=a.arm('GET',scope+'/providers/microsoft.insights/metricDefinitions',version='2018-01-01')
        available={d['name']['value'] for d in definitions['value']}; require(set(names)<=available,f'Required Azure Monitor metrics unavailable: {set(names)-available}')
        params={'api-version':'2018-01-01','metricnames':','.join(names),'timespan':start+'/'+end,'interval':'PT1M','aggregation':'Average'}
        if dimension: params['$filter']=dimension
        response,_=a.request('GET','https://management.azure.com'+scope+'/providers/microsoft.insights/metrics?'+urllib.parse.urlencode(params))
        snapshots.append({'resource':scope,'response':response})
    return {'window_start':start,'window_end':end,'snapshots':snapshots}

def metric_values(snapshot,name,deployment=None,resource=None):
    values=[]
    for group in snapshot['snapshots']:
        if resource is not None and group['resource'].lower()!=resource.lower(): continue
        for metric in group['response'].get('value',[]):
            if metric['name']['value']!=name: continue
            for series in metric.get('timeseries',[]):
                dimensions={m['name']['value'].lower():m['value'] for m in series.get('metadatavalues',[])}
                if deployment is not None and dimensions.get('deployment')!=deployment: continue
                for point in series.get('data',[]):
                    value=point.get('average')
                    if value is None: continue
                    if snapshot.get('window_start') and snapshot.get('window_end'):
                        # PT1M Azure points describe whole buckets, not instantaneous samples.
                        stamp=point.get('timeStamp')
                        if not stamp: continue
                        bucket=datetime.fromisoformat(stamp.replace('Z','+00:00'))
                        start=datetime.fromisoformat(snapshot['window_start'].replace('Z','+00:00')); end=datetime.fromisoformat(snapshot['window_end'].replace('Z','+00:00'))
                        if bucket<start or bucket+timedelta(minutes=1)>end: continue
                    values.append(value)
    return values

def require_monitor_coverage(snapshot,run,deployments):
    resource=endpoint_resource(run)
    for deployment in deployments:
        for name in ('RequestLatency_P95','RequestsPerMinute'):
            require(metric_values(snapshot,name,deployment=deployment,resource=resource),f'Missing {name} for deployment {deployment}; genuine telemetry is pending.')
        for name in ('CpuUtilizationPercentage','CpuMemoryUtilizationPercentage'):
            require(metric_values(snapshot,name,resource=resource+'/deployments/'+deployment),f'Missing {name} for deployment {deployment}.')


def set_traffic(a,baseline,candidate):
    endpoint=course_endpoint(a); endpoint.traffic={a.c['baseline_deployment']:baseline,a.c['candidate_deployment']:candidate}
    a.ml.online_endpoints.begin_create_or_update(endpoint).result(timeout=180)
    observed=a.ml.online_endpoints.get(a.c['endpoint']).traffic
    require(observed.get(a.c['baseline_deployment'])==baseline and observed.get(a.c['candidate_deployment'],0)==candidate,'Traffic read-back mismatch.')
    if a.run.state.get('canary_started_at'):
        a.run.state['baseline_safety_restored']=baseline==100 and candidate==0; a.run.save()
    return observed

def resource_checks(snapshot,run,deployments):
    checks={}
    for deployment in deployments:
        for name,ceiling in run.spec.get('resource_gates',{}).items():
            values=metric_values(snapshot,name,resource=endpoint_resource(run)+'/deployments/'+deployment)
            checks[deployment+'_'+name]=bool(values) and max(values)<=ceiling
    return checks

def canary_alert_spec(a):
    run=a.run; resource=endpoint_resource(run)
    name='ai300-p95-'+a.c['endpoint']+'-'+run.state['run_id'][-8:].lower(); alert=f"/subscriptions/{a.c['subscription_id']}/resourceGroups/{a.c['resource_group']}/providers/Microsoft.Insights/metricAlerts/{name}"
    spec={'location':'global','tags':{'course':'ai300','run_id':run.state['run_id']},'properties':{'description':'Predeclared course latency gate','severity':2,'enabled':True,'scopes':[resource],'evaluationFrequency':'PT1M','windowSize':'PT5M','criteria':{'odata.type':'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria','allOf':[{'criterionType':'StaticThresholdCriterion','name':'candidate-p95','metricNamespace':'Microsoft.MachineLearningServices/workspaces/onlineEndpoints','metricName':'RequestLatency_P95','operator':'GreaterThan','threshold':run.spec['latency_budget_ms'],'timeAggregation':'Average','dimensions':[{'name':'deployment','operator':'Include','values':[a.c['candidate_deployment']]}]}]},'actions':[{'actionGroupId':a.c['monitor_action_group_id']}]}}
    return alert,spec

def prepare_canary_alert(a):
    alert,spec=canary_alert_spec(a)
    # Only an owned alert can be updated; preserve unrelated resources with the same name.
    try:
        existing=a.arm('GET',alert,version='2018-03-01'); require(existing.get('tags',{}).get('course')=='ai300' and existing.get('tags',{}).get('run_id')==a.run.state['run_id'],'Alert name collides with an unrelated resource.')
    except Hold as exc:
        from urllib.error import HTTPError
        if not isinstance(exc.__cause__,HTTPError) or exc.__cause__.code!=404: raise
    a.run.state['resources']['alert_id']=alert; a.run.save(); a.arm('PUT',alert,spec,version='2018-03-01')
    return {'alert_id':alert,'status':'CONFIGURED_NOT_REHEARSED'}

def _canary_step(run,n):
    a=Azure(run); release=run.dependency('m3-demo3',3); require(release['release_decision']=='PASS','Final-test release gate failed; canary is blocked.')
    frozen=release['frozen_release']; resource=endpoint_resource(run)
    require(deployment_snapshot(a,run.config['candidate_deployment'])==frozen['deployment_snapshot'],'Candidate changed after frozen final test.')
    baseline_snapshot=deployment_snapshot(a,run.config['baseline_deployment'])
    run.raw('canary-baseline-snapshot-check',{'expected':frozen['baseline_deployment_snapshot'],'observed':baseline_snapshot,'matches':baseline_snapshot==frozen['baseline_deployment_snapshot']})
    require(baseline_snapshot==frozen['baseline_deployment_snapshot'],'Baseline changed after frozen final test.')
    course_endpoint(a)
    response,_=a.invoke(endpoint_payload(validation(domain=False)[0],frozen['max_new_tokens']),run.config['baseline_deployment'])
    matches=response['deployment']==a.c['baseline_deployment'] and response['model_identity']==frozen['baseline_model_identity']
    run.raw('canary-baseline-model-check',{'expected':frozen['baseline_model_identity'],'observed_response':response,'matches':matches})
    require(matches,'Baseline model identity differs from frozen release.')
    if n==1:
        questions=questions_with_context(a,validation(domain=False)); rows=[]
        run.state['canary_started_at']=now(); run.state['baseline_safety_restored']=False; run.save()
        traffic=set_traffic(a,90,10); workload_clock=time.monotonic()
        for i in range(run.spec['max_requests']):
            q=questions[i%len(questions)]; response,elapsed=a.invoke(endpoint_payload(q,frozen['max_new_tokens']))
            expected={a.c['baseline_deployment']:frozen['baseline_model_identity'],a.c['candidate_deployment']:frozen['model_identity']}
            require(response['deployment'] in expected and response['model_identity']==expected[response['deployment']],'Canary routed identity mismatch.')
            rows.append({'request':i,'query_id':q['query_id'],'query_type':q['query_type'],'question':q['question'],'supplied_context':q['retrieved_context'],'reference_response':q['response'],'deployment':response['deployment'],'model_identity':response['model_identity'],'latency_ms':elapsed,'output_tokens':response['output_tokens'],'raw_response':response['response'],**answer_metrics(response['response'],q)})
            counts,enough=sample_counts(rows,expected,run.spec['minimum_by_query_type'])
            if i+1>=run.spec['requests'] and enough and time.monotonic()-workload_clock>=run.spec.get('minimum_observation_seconds',0): break
        require(enough and time.monotonic()-workload_clock>=run.spec.get('minimum_observation_seconds',0),'Maximum canary workload exhausted before every deployment/query-type sample minimum; baseline will be restored.')
        run.state['canary_finished_at']=now(); run.save(); review_path,_=prepare_manual_review(run,'canary',rows)
        return {'traffic':traffic,'rows':rows,'sample_counts':counts,'manual_review_path':str(review_path),'population':'labeled synthetic traffic; repeated questions are not independent user evidence','canary_started_at':run.state['canary_started_at'],'canary_finished_at':run.state['canary_finished_at']}
    if n==2:
        alert,spec=canary_alert_spec(a); actual=a.arm('GET',alert,version='2018-03-01')
        require(all(actual.get('properties',{}).get(k)==v for k,v in spec['properties'].items()),'Prepared alert differs from declared scope, metric, threshold, deployment or action group.')
        snapshot=monitor_snapshot(a,run.state['canary_started_at'],run.state['canary_finished_at']); require_monitor_coverage(snapshot,run,[a.c['baseline_deployment'],a.c['candidate_deployment']])
        return {'alert_id':alert,'alert':actual,'metric_snapshot':snapshot,'telemetry_status':'AVAILABLE','next_action':'Review every canary answer against its retained supplied context before step3.'}
    if n==3:
        previous=run.previous(1); reviewed=manual_review(run,'canary',previous['rows'])
        candidate=[r for r in reviewed['rows'] if r['deployment']==a.c['candidate_deployment']]; baseline=[r for r in reviewed['rows'] if r['deployment']==a.c['baseline_deployment']]
        checks=quality_checks(candidate,run.spec['quality_gates'],run.spec['minimum_by_query_type'],baseline)
        snapshot=run.previous(2)['metric_snapshot']; checks.update(resource_checks(snapshot,run,[a.c['candidate_deployment']]))
        latency=metric_values(snapshot,'RequestLatency_P95',deployment=a.c['candidate_deployment'],resource=resource); checks['operational_p95']=bool(latency) and max(latency)<=run.spec['latency_budget_ms']
        failed=[key for key,value in checks.items() if not value]
        if failed: set_traffic(a,100,0)
        return {'decision':'STOP_PROMOTION' if failed else 'ELIGIBLE_PENDING_ROLLBACK','promotion':'STOPPED' if failed else 'PENDING_DECISION','failed_gates':failed,'gate_checks':checks,'manual_semantic_review':reviewed,'metric_snapshot':snapshot,'next_action':'Always exercise rollback in step4, even when every gate passed.'}
    traffic=set_traffic(a,100,0)
    record=run.path/'rollback-recovery-observations.json'
    if 'recovery_observations' not in run.state:
        questions=questions_with_context(a,validation(domain=False))
        recovery=endpoint_workload(a,questions,frozen['max_new_tokens'],None,frozen['baseline_model_identity'],minimum_seconds=run.spec.get('minimum_observation_seconds',0),max_requests=run.spec.get('max_observation_requests'))
        write(record,recovery); run.state['recovery_observations']={'path':str(record),'sha256':digest(record)}; run.save()
    require(digest(record)==run.state['recovery_observations']['sha256'],'Retained recovery workload changed; never replace its telemetry window.')
    recovery=read(record)
    if run.spec.get('minimum_observation_seconds',0): require(recovery.get('window_complete'),'Recovery observation window incomplete; retain baseline and inspect request budget.')
    require(all(r['deployment']==a.c['baseline_deployment'] for r in recovery['rows']),'Routed response did not return baseline after rollback.')
    snapshot=monitor_snapshot(a,recovery['window_start'],recovery['window_end']); require_monitor_coverage(snapshot,run,[a.c['baseline_deployment']])
    latency=metric_values(snapshot,'RequestLatency_P95',deployment=a.c['baseline_deployment'],resource=resource); require(max(latency)<=run.spec['latency_budget_ms'],'Baseline operational recovery gate still fails.')
    return {'traffic':traffic,'routed_model_identities':[r['model_identity'] for r in recovery['rows']],'routed_responses':recovery,'recovery_metrics':snapshot,'rollback_verified':True,'canary_decision':run.previous(3)['decision'],'population':'controlled course workload'}

def canary_rollback(run,n):
    try: return _canary_step(run,n)
    except BaseException as original:
        if run.state.get('canary_started_at') and not run.state.get('baseline_safety_restored'):
            try:
                traffic=set_traffic(Azure(run),100,0); run.raw('canary-step-safety-restore',{'step':n,'original_error':str(original),'traffic':traffic})
            except Exception as restore_error:
                run.raw('canary-step-restore-failed',{'step':n,'original_error':str(original),'restore_error':str(restore_error),'traffic':'UNKNOWN','action':'Restore baseline in Azure ML immediately.'})
                raise Hold('Canary step failed and baseline restoration could not be verified. Traffic is UNKNOWN; inspect retained diagnostics and restore baseline.') from original
        raise

HANDLERS={'m1-demo1':retrieval_chunks,'m1-demo2':hybrid_search,'m1-demo3':rag_ab,'m2-demo1':embedding_train,'m2-demo2':synthetic_data,'m2-demo3':lora_train,'m2-demo4':lora_select,'m3-demo1':model_evaluate,'m3-demo2':model_deploy,'m3-demo3':endpoint_test,'m3-demo4':canary_rollback}
