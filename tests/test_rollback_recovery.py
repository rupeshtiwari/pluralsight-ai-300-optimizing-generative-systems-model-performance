"""Offline recovery gates and retained-window checks; never live Azure proof."""
from contextlib import contextmanager, ExitStack
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from ai300 import core, demos

class RollbackRecoveryTests(unittest.TestCase):
    @contextmanager
    def fixture(self, *, cpu=40, memory=50, status_class='2xx', schema=1, count=2, reviewed=True):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            root=Path(temp)
            config={'subscription_id':'offline','resource_group':'offline','workspace':'offline','endpoint':'ai300-offline','baseline_deployment':'baseline','candidate_deployment':'candidate'}
            spec={**core.read(core.ROOT/'configs/m3-demo4.json'),'minimum_observation_seconds':0};identity={'model':'baseline-version'}
            frozen={'deployment_snapshot':{},'baseline_deployment_snapshot':{},'baseline_model_identity':identity,'model_identity':{'model':'candidate-version'},'max_new_tokens':64}
            rows=[{'query_id':kind+str(i),'query_type':kind,'question':'Offline question','supplied_context':[],'reference_response':{'answer':'Offline answer','source_ids':[]},'raw_response':{'answer':'Offline answer','source_ids':[]},'schema_validity':schema,'latency_ms':10,'output_tokens':2,'deployment':'baseline','model_identity':identity} for kind in ('general','exact_identifier','paraphrase') for i in range(count)]
            workload={'rows':rows,'window_start':'2026-11-02T12:00:00+00:00','window_end':'2026-11-02T12:02:00+00:00','window_complete':True}
            run=SimpleNamespace(path=root,state={'canary_started_at':'OFFLINE','baseline_safety_restored':False},config=config,spec=spec,save=Mock(),raw=Mock(),dependency=lambda *a:{'release_decision':'PASS','frozen_release':frozen},previous=lambda n:{'decision':'ELIGIBLE_PENDING_ROLLBACK'})
            adapter=SimpleNamespace(run=run,c=config,invoke=Mock(return_value=({'deployment':'baseline','model_identity':identity},1)));resource=demos.endpoint_resource(run)
            def metric(name,value,dimensions=None):
                return {'name':{'value':name},'timeseries':[{'metadatavalues':[{'name':{'value':key},'value':v} for key,v in (dimensions or {}).items()],'data':[{'timeStamp':'2026-11-02T12:00:00Z','average':value}]}]}
            snapshot={**{k:workload[k] for k in ('window_start','window_end')},'snapshots':[{'resource':resource,'response':{'value':[metric('RequestLatency_P95',10,{'deployment':'baseline'}),metric('RequestsPerMinute',10,{'deployment':'baseline','statusCodeClass':status_class})]}},{'resource':resource+'/deployments/baseline','response':{'value':[metric('CpuUtilizationPercentage',cpu),metric('CpuMemoryUtilizationPercentage',memory)]}}]}
            def restore(adapter,baseline,candidate):
                run.state['baseline_safety_restored']=baseline==100 and candidate==0
                return {'baseline':baseline,'candidate':candidate}
            stack.enter_context(patch.object(demos,'Azure',return_value=adapter));stack.enter_context(patch.object(demos,'deployment_snapshot',return_value={}));stack.enter_context(patch.object(demos,'course_endpoint'))
            traffic=stack.enter_context(patch.object(demos,'set_traffic',side_effect=restore));observed=stack.enter_context(patch.object(demos,'endpoint_workload',return_value=workload))
            stack.enter_context(patch.object(demos,'questions_with_context',return_value=[]));monitor=stack.enter_context(patch.object(demos,'monitor_snapshot',return_value=snapshot));final_test=stack.enter_context(patch.object(demos,'endpoint_test'))
            if reviewed:core.prepare_manual_review(run,'rollback-recovery',rows);self.complete_review(root)
            yield run,observed,traffic,monitor,final_test

    def complete_review(self,root):
        path=root/'rollback-recovery-review.jsonl';reviews=core.jsonl(path)
        for row in reviews:row.update(correct=True,supported=True,reason='OFFLINE test review fixture',reviewer='Offline test double')
        core.write_jsonl(path,reviews)

    def test_high_cpu_or_memory_cannot_verify_recovery(self):
        for metric,options in [('CpuUtilizationPercentage',{'cpu':95}),('CpuMemoryUtilizationPercentage',{'memory':95})]:
            with self.subTest(metric=metric),self.fixture(**options) as (run,workload,traffic,monitor,final_test):
                with self.assertRaisesRegex(core.Hold,metric):demos.canary_rollback(run,4)
                self.assertTrue(run.state['baseline_safety_restored']);self.assertEqual(traffic.call_args.args[1:],(100,0))
                evidence=run.raw.call_args.args[1];self.assertFalse(evidence['gate_checks']['baseline_'+metric]);self.assertIn('baseline_'+metric,evidence['failed_gates']);final_test.assert_not_called()

    def test_request_errors_cannot_verify_recovery(self):
        for status in ('4xx','5xx'):
            with self.subTest(status=status),self.fixture(status_class=status) as (run,*_):
                with self.assertRaisesRegex(core.Hold,'request'):demos.canary_rollback(run,4)
                self.assertTrue(run.state['baseline_safety_restored'])

    def test_schema_or_query_type_sample_failures_cannot_verify_recovery(self):
        for options in ({'schema':0},{'count':1}):
            with self.subTest(options=options),self.fixture(**options) as (run,*_):
                with self.assertRaisesRegex(core.Hold,'recovery gates failed'):demos.canary_rollback(run,4)
                self.assertTrue(run.state['baseline_safety_restored'])

    def test_completed_review_resumes_same_recovery_window_without_replay(self):
        with self.fixture(reviewed=False) as (run,workload,traffic,monitor,final_test):
            with self.assertRaisesRegex(core.Hold,'Manual semantic review required'):demos.canary_rollback(run,4)
            self.assertTrue(run.state['baseline_safety_restored']);retained_hash=core.digest(run.path/'rollback-recovery-observations.json');self.complete_review(run.path)
            result=demos.canary_rollback(run,4);self.assertTrue(result['rollback_verified']);self.assertTrue(all(result['gate_checks'].values()));self.assertEqual(result['failed_gates'],[])
            for key in ('baseline_CpuUtilizationPercentage','baseline_CpuMemoryUtilizationPercentage','no_server_request_errors'):self.assertIn(key,result['gate_checks'])
            self.assertEqual(workload.call_count,1);self.assertEqual(retained_hash,core.digest(run.path/'rollback-recovery-observations.json'))
            self.assertEqual([call.args[1:] for call in monitor.call_args_list],[('2026-11-02T12:00:00+00:00','2026-11-02T12:02:00+00:00')]*2);final_test.assert_not_called()

    def test_all_learner_step_navigation_targets_match_contract(self):
        for demo in core.read(core.ROOT/'course-contract.json')['demos']:
            text=(core.ROOT/demo['folder']/'README.md').read_text();menu=text.split('## Jump to a Step\n',1)[1].split('## Numbered Steps',1)[0]
            self.assertLess(text.index('## Jump to a Step'),text.index('## Numbered Steps'))
            for step in demo['steps']:
                n=step['n'];self.assertIn(f'[Step {n}](#step-{n})',menu);self.assertEqual(text.count(f'<a id="step-{n}"></a>'),1);self.assertIn(step['command'],text)

if __name__=='__main__':unittest.main()
