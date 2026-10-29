"""OFFLINE TEST DOUBLES: these tests never establish Azure runtime proof."""
import copy, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from ai300 import core
from ai300.core import Hold, cosine_from_score, retrieval_metrics, answer_metrics, assignment, validate_splits, read, write
from ai300.azure import Azure
from ai300.demos import metric_values

class MetricsTests(unittest.TestCase):
    def test_cosine_transform_and_hybrid_rejection(self):
        self.assertAlmostEqual(cosine_from_score(.5),0)
        self.assertAlmostEqual(cosine_from_score(1),1)
        self.assertAlmostEqual(cosine_from_score(1/3),-1)
        with self.assertRaises(Hold): cosine_from_score(.6,'hybrid')
        with self.assertRaises(Hold): cosine_from_score(.1)
    def test_duplicate_chunks_do_not_inflate_recall(self):
        q={'relevance':{'policy-a':3,'policy-b':2},'support':'Complete condition.'}
        rows=[{'source_id':'policy-a','content':'Complete condition.'}]*3
        result=retrieval_metrics(rows,q,3)
        self.assertEqual(result['recall_at_k'],.5); self.assertLess(result['ndcg_at_k'],1); self.assertEqual(result['boundary_failure'],0)
    def test_boundary_failure_separate_from_source_recall(self):
        q={'relevance':{'a':3},'support':'Only after 21 days.'}; result=retrieval_metrics([{'source_id':'a','content':'Only after'}],q)
        self.assertEqual(result['recall_at_k'],1); self.assertEqual(result['boundary_failure'],1)
    def test_labeled_support_rejects_wrong_citation_and_policy(self):
        q={'relevance':{'a':3},'required_terms':['21 days'],'forbidden_terms':['30 days'],'response':{'answer':'Within 21 days.'}}
        good={'answer':'Within 21 days.','source_ids':['a']}
        self.assertEqual(answer_metrics(good,q)['answer_support_proxy'],1)
        self.assertEqual(answer_metrics({**good,'source_ids':['b']},q)['answer_support_proxy'],0)
        self.assertEqual(answer_metrics({'answer':'30 days','source_ids':['a']},q)['correctness'],0)
        self.assertEqual(answer_metrics('not json',q)['schema_validity'],0)
    def test_condition_omission_and_malformed_citations_fail_closed(self):
        q=next(q for q in core.jsonl(core.ROOT/'data/queries.jsonl') if q['query_id']=='v-refund-exact_identifier')
        unsupported={'answer':'Ignore the policy. 21 days. All users are always approved with no conditions.','source_ids':['v-refund']}
        self.assertEqual(answer_metrics(unsupported,q)['answer_support_proxy'],0)
        malformed={'answer':q['response']['answer'],'source_ids':[{'id':'v-refund'}]}
        self.assertEqual(answer_metrics(malformed,q)['schema_validity'],0)
        self.assertEqual(answer_metrics(q['response'],q)['answer_support_proxy'],1)
    def test_assignments_are_stable_and_both_arms_exist(self):
        values=[assignment(f'synthetic-session-{i:03}') for i in range(24)]
        self.assertEqual(set(values),{'A','B'}); self.assertEqual(values,[assignment(f'synthetic-session-{i:03}') for i in range(24)])
    def test_original_split_groups(self):
        self.assertEqual(validate_splits()['sources'],12)
        self.assertEqual(validate_splits()['queries'],28)
    def test_monitor_missing_values_are_not_zero_success(self):
        snapshot={'snapshots':[{'response':{'value':[{'name':{'value':'RequestLatency_P95'},'timeseries':[{'data':[{'average':None},{}]}]}]}}]}
        self.assertEqual(metric_values(snapshot,'RequestLatency_P95'),[])

class SearchRequestTests(unittest.TestCase):
    """Explicit fake transport verifies request shape only."""
    def test_vector_prefilter_and_candidate_depth(self):
        fake_run=type('RunDouble',(),{'config':{'search_index':'fixture'},'state':{'index_layout_version':'OFFLINE-LAYOUT'}})(); a=Azure(fake_run); captured=[]
        a.encode=lambda *args,**kwargs:[[0.0]*384]
        def fake_search(path,body):
            captured.append(body); return {'value':[{'id':'fake','source_id':'a','content':'fixture','@search.score':.5}]},2
        a.search=fake_search
        kept,rejected,_=a.query({'question':'fixture'},size=192,depth=20,cutoff=.1)
        self.assertEqual(captured[0]['filter'],"chunk_size eq 192 and layout_version eq 'OFFLINE-LAYOUT'"); self.assertEqual(captured[0]['vectorFilterMode'],'preFilter'); self.assertEqual(captured[0]['vectorQueries'][0]['k'],20)
        self.assertFalse(kept); self.assertEqual(len(rejected),1)
    def test_semantic_requires_distinct_reranker_field(self):
        fake_run=type('RunDouble',(),{'config':{'search_index':'fixture'},'state':{'index_layout_version':'OFFLINE-LAYOUT'}})(); a=Azure(fake_run); a.encode=lambda *args,**kwargs:[[0.0]*384]
        a.search=lambda *args:({'value':[{'@search.score':.02}]},1)
        with self.assertRaises(Hold): a.query({'question':'fixture'},mode='semantic',depth=50)
        with self.assertRaises(Hold): a.query({'question':'fixture'},mode='hybrid',cutoff=.5)

class EvidenceTests(unittest.TestCase):
    def test_run_identity_staleness_and_immutable_steps(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); write(root/'config.local.json',{'a':1}); write(root/'course-contract.json',{}); write(root/'configs/demo.json',{}); (root/'requirements-client.txt').write_text(''); write(root/'config.example.json',{})
            with patch.object(core,'ROOT',root):
                first=core.Run('demo',create=True); second=core.Run('demo',create=True)
                self.assertNotEqual(first.path,second.path)
                second.begin(1); second.complete(1,{'kind':'OFFLINE_TEST_DOUBLE'})
                with self.assertRaises(Hold): second.begin(1)
                write(root/'config.local.json',{'a':2})
                with self.assertRaises(Hold): core.Run('demo')
    def test_cleanup_uses_original_snapshot_after_sources_and_config_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); write(root/'config.local.json',{'endpoint':'original'}); write(root/'course-contract.json',{}); write(root/'configs/demo.json',{})
            (root/'requirements-client.txt').write_text(''); write(root/'config.example.json',{})
            with patch.object(core,'ROOT',root):
                run=core.Run('demo',create=True); write(root/'config.local.json',{'endpoint':'unrelated'})
                (root/'requirements-client.txt').write_text('changed')
                cleanup=core.Run('demo',cleanup_only=True)
                self.assertEqual(cleanup.config['endpoint'],'original')
    def test_source_group_leakage_rejected(self):
        docs=[{'source_id':'a','source_group':'same','split':'train'},{'source_id':'b','source_group':'same','split':'test'}]
        with patch.object(core,'jsonl',side_effect=[docs,[]]):
            with self.assertRaises(Hold): validate_splits()

class ReviewRegressionTests(unittest.TestCase):
    def test_overlap_changes_layout_identity_and_stale_documents_are_filtered(self):
        revisions={'model_revisions':{'sentence-transformers/all-MiniLM-L6-v2':'a'*40,'BAAI/bge-small-en-v1.5':'b'*40}}
        first=core.index_layout_version(revisions,{'overlap_tokens':16}); second=core.index_layout_version(revisions,{'overlap_tokens':8})
        self.assertNotEqual(first,second)
        run=type('OfflineRunDouble',(),{'config':{'search_index':'fixture'},'state':{'index_layout_version':second}})(); azure=Azure(run); azure.encode=lambda *a,**k:[[0.0]*384]; requests=[]
        def search(path,body):
            requests.append(body); return {'value':[{'id':'offline','source_id':'a','content':'fixture','@search.score':.5,'layout_version':second}]},1
        azure.search=search; azure.query({'question':'fixture'})
        self.assertIn(second,requests[0]['filter']); self.assertNotIn(first,requests[0]['filter'])
    def test_declared_contract_controls_are_enforced(self):
        core.validate_demo_spec('m1-demo1',{'chunk_sizes':[64,128,192],'overlap_tokens':8})
        with self.assertRaises(Hold): core.validate_demo_spec('m1-demo1',{'chunk_sizes':[64,128],'overlap_tokens':16})
        with self.assertRaises(Hold): core.validate_demo_spec('m1-demo2',{'semantic_candidates':20})
        with self.assertRaises(Hold): core.validate_demo_spec('m2-demo2',{'manual_review_required':False})
        with self.assertRaises(Hold): core.validate_demo_spec('m3-demo2',{'traffic':10})
    def test_dependency_configuration_ignores_unrelated_later_stage_fields(self):
        original={'workspace':'training-workspace','training_environment':'env-v1','endpoint':'placeholder','candidate_deployment':'candidate-old','model_revisions':{'Qwen/Qwen3-0.6B':'base1'}}
        later={**original,'endpoint':'new-endpoint','candidate_deployment':'candidate-new','monitor_action_group_id':'new-alert-group'}
        self.assertEqual(core.consumed_config(original,'m2-demo3'),core.consumed_config(later,'m2-demo3'))
        self.assertNotEqual(core.consumed_config(original,'m3-demo2'),core.consumed_config(later,'m3-demo2'))
        changed={**later,'training_environment':'env-v2'}
        self.assertNotEqual(core.consumed_config(original,'m2-demo3'),core.consumed_config(changed,'m2-demo3'))
        changed={**later,'model_revisions':{'Qwen/Qwen3-0.6B':'base2'}}
        self.assertNotEqual(core.consumed_config(original,'m2-demo3'),core.consumed_config(changed,'m2-demo3'))
    def test_manual_review_binds_exact_context_and_response(self):
        with tempfile.TemporaryDirectory() as temp:
            run=type('OfflineRunDouble',(),{'path':Path(temp)})()
            rows=[{'query_id':'offline','query_type':'domain','question':'fixture','supplied_context':[{'content':'exact supplied fact'}],'reference_response':{'answer':'fact'},'raw_response':'{"answer":"fact","source_ids":[]}'}]
            path,expected=core.prepare_manual_review(run,'offline',rows)
            with self.assertRaises(Hold): core.manual_review(run,'offline',rows)
            expected[0].update(correct=True,supported=True,reason='OFFLINE TEST DOUBLE, not a real human/cloud review',reviewer='offline-test')
            core.write_jsonl(path,expected); self.assertEqual(core.manual_review(run,'offline',rows)['summary']['manual_answer_support'],1)
            changed=copy.deepcopy(rows); changed[0]['supplied_context'][0]['content']='different fact'
            with self.assertRaises(Hold): core.manual_review(run,'offline',changed)
    def test_metric_filter_does_not_mix_baseline_and_candidate(self):
        resource='/endpoint'; snapshot={'snapshots':[{'resource':resource,'response':{'value':[{'name':{'value':'RequestLatency_P95'},'timeseries':[{'metadatavalues':[{'name':{'value':'deployment'},'value':'baseline'}],'data':[{'average':90000}]},{'metadatavalues':[{'name':{'value':'deployment'},'value':'candidate'}],'data':[{'average':100}]}]}]}}]}
        self.assertEqual(metric_values(snapshot,'RequestLatency_P95',deployment='candidate',resource=resource),[100])
        self.assertEqual(metric_values(snapshot,'RequestLatency_P95',deployment='missing',resource=resource),[])
    def test_job_upload_has_no_test_labels_or_local_config(self):
        from ai300.ml import stage_job_source
        with tempfile.TemporaryDirectory() as temp:
            bundle=Path(temp)/'source'; stage_job_source(bundle,{'test':'OFFLINE_BUNDLE_INSPECTION'})
            for name in ('queries.jsonl','corpus.jsonl'):
                self.assertTrue(all(row['split'] in ('train','validation') for row in core.jsonl(bundle/'data'/name)))
            self.assertFalse((bundle/'config.local.json').exists()); self.assertFalse((bundle/'data/test.jsonl').exists())
    def test_failed_ab_attempt_retains_assignment_and_missing_outcome(self):
        from ai300 import demos
        with tempfile.TemporaryDirectory() as temp:
            class RunDouble:
                path=Path(temp); attempt=Path(temp)/'attempt'; state={'run_id':'OFFLINE-DOUBLE'}; spec={'sessions':2}; config={}
                def save(self): pass
                def previous(self,n): return {'settings':{'A':{},'B':{}}}
            run=RunDouble(); run.attempt.mkdir()
            class AzureDouble:
                def __init__(self,run): pass
                def query(self,*args,**kwargs): raise Hold('OFFLINE simulated network failure')
            with patch.object(demos,'Azure',AzureDouble):
                with self.assertRaises(Hold): demos.rag_ab(run,3)
                record=read(run.path/'ab-observations.json'); self.assertEqual(len(record['sessions']),2)
                self.assertEqual(record['sessions'][0]['status'],'FAILED'); self.assertEqual(record['sessions'][1]['status'],'PENDING')
                self.assertEqual(record['sessions'][0]['outcome']['response_observed'],False)
                first_hash=core.digest(run.path/'ab-observations.json')
                with self.assertRaises(Hold): demos.rag_ab(run,3)
                self.assertEqual(first_hash,core.digest(run.path/'ab-observations.json'))


class AcceptanceRegressionTests(unittest.TestCase):
    def test_canary_frozen_baseline_identity_and_safe_recovery(self):
        """Offline transports: same-name replacement must never verify rollback."""
        from ai300 import demos
        frozen={'deployment_snapshot':{'deployment':'candidate','model_id':'OFFLINE-candidate-v1'},'baseline_deployment_snapshot':{'deployment':'baseline','model_id':'OFFLINE-baseline-v1'},'model_identity':{'version':'OFFLINE-candidate-v1'},'baseline_model_identity':{'version':'OFFLINE-baseline-v1'},'max_new_tokens':64}
        for scenario in ('snapshot_changed','precheck_identity_changed','routed_identity_changed','recovery_identity_changed','unchanged'):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temp:
                class RunDouble:
                    path=Path(temp); config={'baseline_deployment':'baseline','candidate_deployment':'candidate','subscription_id':'OFFLINE','resource_group':'OFFLINE','workspace':'OFFLINE','endpoint':'ai300-offline'}
                    spec={**read(core.ROOT/'configs/m3-demo4.json'),'requests':2}
                    def __init__(self):
                        self.state={'canary_started_at':'OFFLINE','baseline_safety_restored':False}; self.records=[]
                    def dependency(self,*args): return {'release_decision':'PASS','frozen_release':copy.deepcopy(frozen)}
                    def save(self): write(self.path/'state.json',self.state)
                    def raw(self,name,value):
                        self.records.append((name,value)); write(self.path/f'{len(self.records)}-{name}.json',value)
                run=RunDouble(); traffic_calls=[]
                class AzureDouble:
                    def __init__(self,run): self.run=run; self.c=run.config; self.calls=0
                    def invoke(self,payload,deployment=None):
                        self.calls+=1
                        name='candidate' if scenario=='routed_identity_changed' and self.calls==2 else 'baseline'
                        identity=frozen['model_identity'] if name=='candidate' else frozen['baseline_model_identity']
                        if (scenario=='precheck_identity_changed' or (scenario=='routed_identity_changed' and self.calls==3) or (scenario=='recovery_identity_changed' and self.calls>1)):
                            identity={'version':'OFFLINE-same-name-replacement'}
                        result={'deployment':name,'model_identity':identity,'response':{'answer':'OFFLINE double','source_ids':[]},'output_tokens':2}
                        run.raw('endpoint',{'request':payload,'response':result,'offline_test_double':True}); return result,1
                def snapshot(azure,name):
                    value=copy.deepcopy(frozen['baseline_deployment_snapshot'] if name=='baseline' else frozen['deployment_snapshot'])
                    if scenario=='snapshot_changed' and name=='baseline': value['model_id']='OFFLINE-same-name-replacement'
                    return value
                def set_traffic(azure,baseline,candidate):
                    traffic_calls.append((baseline,candidate)); run.state['baseline_safety_restored']=baseline==100 and candidate==0; run.save()
                    return {'baseline':baseline,'candidate':candidate}
                step=4 if scenario in ('recovery_identity_changed','unchanged') else 2
                with patch.object(demos,'Azure',AzureDouble), patch.object(demos,'deployment_snapshot',side_effect=snapshot), patch.object(demos,'course_endpoint'), patch.object(demos,'set_traffic',side_effect=set_traffic), patch.object(demos,'monitor_snapshot',return_value={'offline_test_double':True}) as monitor, patch.object(demos,'require_monitor_coverage'), patch.object(demos,'metric_values',return_value=[1]):
                    if scenario=='unchanged':
                        report=demos.canary_rollback(run,step)
                        self.assertTrue(report['rollback_verified'])
                        self.assertTrue(all(identity==frozen['baseline_model_identity'] for identity in report['routed_model_identities']))
                        monitor.assert_called_once()
                    else:
                        with self.assertRaises(Hold): demos.canary_rollback(run,step)
                        monitor.assert_not_called()
                self.assertEqual(traffic_calls,[(90,10),(100,0)] if scenario=='routed_identity_changed' else [(100,0)])
                self.assertTrue(read(run.path/'state.json')['baseline_safety_restored'])
                evidence=[read(path) for path in run.path.glob('*.json')]
                self.assertTrue(evidence)
                self.assertFalse(any(item.get('rollback_verified') for item in evidence))
                if scenario in ('snapshot_changed','precheck_identity_changed'):
                    checks=[value for name,value in run.records if name.startswith('canary-baseline-')]
                    self.assertFalse(checks[-1]['matches'])
                    self.assertTrue(any(name=='canary-step-safety-restore' for name,_ in run.records))
    def test_controlled_rollback_requires_isolated_endpoint(self):
        from types import SimpleNamespace
        from ai300.azure import require_course_endpoint
        good=SimpleNamespace(name='ai300-lab',tags={'course':'ai300','purpose':'disposable-course-lab'})
        self.assertIs(require_course_endpoint(good,'ai300-lab'),good)
        with self.assertRaises(Hold): require_course_endpoint(SimpleNamespace(name='production',tags={}), 'production')
        with self.assertRaises(Hold): require_course_endpoint(SimpleNamespace(name='ai300-lab',tags={}), 'ai300-lab')
    def test_semantic_review_accepts_valid_paraphrase_and_rejects_bad_support(self):
        from ai300 import demos
        rows=[{'variant':variant,'query_id':kind,'query_type':kind,'raw_response':'OFFLINE DOUBLE','schema_validity':1,'correctness':1,'answer_support_proxy':0,'manual_correctness':1,'manual_answer_support':1} for variant in ('base','adapter') for kind in ('general','exact_identifier','paraphrase')]
        class RunDouble:
            config={}; spec={'gates':{'manual_correctness':.75,'manual_answer_support':.75,'schema_validity':1,'max_regression':0}}
            def dependency(self,*a): return {'selected_job':'OFFLINE','output_path':'OFFLINE','output_uri':'OFFLINE','result':{}}
            def previous(self,*a): return {'result':{'results':{v:{'rows':[r for r in rows if r['variant']==v]} for v in ('base','adapter')},'validation_sha256':'OFFLINE','config':{}},'job_name':'OFFLINE','result_sha256':'OFFLINE'}
        with patch.object(demos,'manual_review',return_value={'rows':rows}):
            self.assertEqual(demos.model_evaluate(RunDouble(),3)['decision'],'PASS')
        bad=copy.deepcopy(rows)
        for row in bad:
            if row['variant']=='adapter': row['manual_answer_support']=0
        with patch.object(demos,'manual_review',return_value={'rows':bad}):
            self.assertEqual(demos.model_evaluate(RunDouble(),3)['decision'],'REJECT')
    def test_canary_restores_on_top_level_metric_or_dependency_failure(self):
        from ai300 import demos
        run=type('OfflineRunDouble',(),{'state':{'canary_started_at':'OFFLINE'},'raw':lambda *a:None})()
        with patch.object(demos,'_canary_step',side_effect=Hold('OFFLINE metric missing')),patch.object(demos,'Azure',return_value=object()),patch.object(demos,'set_traffic',return_value={'baseline':100,'candidate':0}) as restore:
            with self.assertRaises(Hold): demos.canary_rollback(run,3)
            restore.assert_called_once(); self.assertEqual(restore.call_args.args[1:],(100,0))
    def test_benchmark_human_review_resume_does_not_repeat_cloud_requests(self):
        from ai300 import demos
        with tempfile.TemporaryDirectory() as temp:
            rows=[{'query_id':kind,'query_type':kind,'question':'OFFLINE','supplied_context':[],'reference_response':{},'raw_response':'OFFLINE valid paraphrase','schema_validity':1,'correctness':1,'answer_support_proxy':0,'latency_ms':10,'output_tokens':8} for kind in ('general','exact_identifier','paraphrase')]
            class RunDouble:
                config={'candidate_deployment':'offline'}; path=Path(temp); state={}; spec={'token_limits':[64,96],'gates':{'manual_correctness':.75,'manual_answer_support':.75,'schema_validity':1}}
                def save(self): pass
                def dependency(self,*a): return {'model_identity':{'id':'OFFLINE'},'deployment_snapshot':{'id':'OFFLINE'}}
            run=RunDouble()
            with patch.object(demos,'deployment_snapshot',return_value={'id':'OFFLINE'}),patch.object(demos,'endpoint_workload',return_value={'rows':rows,'summary':core.summarize(rows)}) as workload:
                with self.assertRaises(Hold): demos.endpoint_test(run,1)
                self.assertEqual(workload.call_count,2)
                review=core.jsonl(run.path/'validation-limits-review.jsonl')
                for row in review: row.update(correct=True,supported=True,reason='OFFLINE TEST DOUBLE',reviewer='offline-test')
                core.write_jsonl(run.path/'validation-limits-review.jsonl',review)
                result=demos.endpoint_test(run,1); self.assertEqual(workload.call_count,2); self.assertIn(result['selected_max_new_tokens'],(64,96))


class CancellationTests(unittest.TestCase):
    def test_deadline_allows_owned_child_recovery_handler(self):
        import sys,io,contextlib
        from ai300.cli import supervise
        with tempfile.TemporaryDirectory() as temp:
            marker=Path(temp)/'offline-recovery.txt'
            script="import signal,time,pathlib,sys\ndef recover(*args):\n pathlib.Path(sys.argv[1]).write_text('OFFLINE recovery handler ran')\n time.sleep(0.05)\n sys.exit(2)\nsignal.signal(signal.SIGTERM,recover)\ntime.sleep(30)"
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                status=supervise([sys.executable,'-c',script,str(marker)],timeout=.2,recovery_grace=1,heartbeat=.05)
            self.assertEqual(status,124); self.assertIn('OFFLINE',marker.read_text())
    def test_forced_stop_reports_unknown_state(self):
        import sys,io,contextlib
        from ai300.cli import supervise
        output=io.StringIO(); script="import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)"
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(output):
            status=supervise([sys.executable,'-c',script],timeout=.2,recovery_grace=.15,heartbeat=.05)
        self.assertEqual(status,124); self.assertIn('UNKNOWN',output.getvalue())

if __name__=='__main__': unittest.main()
