"""Offline failure regressions: test doubles cannot prove Azure operation."""
import copy,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from ai300 import core,demos,cli
from ai300.gates import quality_checks,sample_counts

def row(kind,score=1):
    return {'query_type':kind,'manual_correctness':score,'manual_answer_support':score,'schema_validity':1,'latency_ms':10}

class DeclaredGatesTests(unittest.TestCase):
    def test_candidate_absolute_pass_cannot_hide_baseline_regression(self):
        candidate=[row(kind,.75) for kind in ('general','exact_identifier','paraphrase')]
        baseline=[row(kind,1) for kind in ('general','exact_identifier','paraphrase')]
        gates={'manual_correctness':.75,'manual_answer_support':.75,'schema_validity':1,'max_regression':0}
        checks=quality_checks(candidate,gates,{k:1 for k in ('general','exact_identifier','paraphrase')},baseline)
        self.assertFalse(checks['manual_correctness']); self.assertFalse(checks['general_manual_answer_support'])
        self.assertTrue(all(quality_checks(baseline,gates,{k:1 for k in ('general','exact_identifier','paraphrase')},baseline).values()))
    def test_missing_query_type_samples_cannot_pass(self):
        checks=quality_checks([row('general')],{'schema_validity':1},{'general':2,'exact_identifier':2})
        self.assertFalse(checks['samples_general']);self.assertFalse(checks['samples_exact_identifier'])
        self.assertFalse(checks['exact_identifier_schema_validity'])
    def test_routing_observation_of_both_deployments_is_not_sufficient(self):
        rows=[{'deployment':d,'query_type':'general'} for d in ('base','candidate')]
        counts,enough=sample_counts(rows,('base','candidate'),{'general':2,'paraphrase':1})
        self.assertFalse(enough);self.assertEqual(counts['candidate']['paraphrase'],0)
    def test_resource_presence_is_not_resource_acceptance(self):
        run=SimpleNamespace(spec={'resource_gates':{'CpuUtilizationPercentage':90}},config={'subscription_id':'s','resource_group':'r','workspace':'w','endpoint':'e'})
        with patch.object(demos,'metric_values',return_value=[91]):self.assertFalse(all(demos.resource_checks({},run,['candidate']).values()))
        with patch.object(demos,'metric_values',return_value=[]):self.assertFalse(all(demos.resource_checks({},run,['candidate']).values()))
        with patch.object(demos,'metric_values',return_value=[80]):self.assertTrue(all(demos.resource_checks({},run,['candidate']).values()))
    def test_tuned_adoption_restores_the_retained_checkpoint(self):
        proof={'decision':'ADOPT','checkpoint_artifact':{'job_name':'OFFLINE','output_path':'OFFLINE'}}
        run=SimpleNamespace(dependency=Mock(return_value=proof));a=SimpleNamespace(c={'adopted_retrieval':{'field':'tuned_vector','size':64}},run=run,prepare_index=Mock())
        with patch.object(demos,'index_tuned_checkpoint',return_value='OFFLINE-ENCODER') as restore:
            settings,encoder=demos.prepare_retrieval(a)
            self.assertEqual((settings['size'],encoder),(64,'OFFLINE-ENCODER'));restore.assert_called_once_with(a,proof['checkpoint_artifact'])
        run.dependency.return_value={'decision':'REJECT'}
        with self.assertRaises(core.Hold):demos.prepare_retrieval(a)
    def test_embedding_proof_survives_baseline_to_tuned_adoption_at_same_chunk_size(self):
        original={'adopted_retrieval':{'field':'mini_vector','mode':'vector','size':128}}
        adopted={'adopted_retrieval':{'field':'tuned_vector','mode':'hybrid','size':128}}
        self.assertEqual(core.consumed_config(original,'m2-demo1'),core.consumed_config(adopted,'m2-demo1'))
        changed={'adopted_retrieval':{'field':'tuned_vector','size':64}}
        self.assertNotEqual(core.consumed_config(original,'m2-demo1'),core.consumed_config(changed,'m2-demo1'))

    def test_endpoint_payload_never_injects_relevance_labels_as_context(self):
        q={'question':'Q','relevance':{'oracle':3}}
        self.assertEqual(demos.endpoint_payload(q,64)['evidence'],[])
        actual=[{'source_id':'retrieved','content':'Real query result'}]
        self.assertEqual(demos.endpoint_payload({**q,'retrieved_context':actual},64)['evidence'],actual)
    def test_prepare_alert_cli_passes_adapter_and_retains_setup_attempt(self):
        with tempfile.TemporaryDirectory() as temp:
            run=SimpleNamespace(path=Path(temp),attempt=None,config={},demo='m3-demo4',state={})
            with patch.object(sys,'argv',['ai300.cli','--demo','m3-demo4','prepare-alert']),patch.object(cli,'check_config'),patch.object(cli,'Run',return_value=run),patch.object(demos,'prepare_canary_alert',return_value={'status':'OFFLINE'}) as prepare:
                self.assertEqual(cli.main(),0)
            self.assertIs(prepare.call_args.args[0].run,run);self.assertTrue(run.attempt.is_dir())
    def test_cleanup_does_not_delete_a_collision_from_another_run(self):
        class NotFound(Exception):pass
        endpoint=SimpleNamespace(name='ai300-test',tags={'course':'ai300','purpose':'disposable-course-lab'},traffic={'baseline':100})
        a=Mock();a.ml.online_endpoints.get.return_value=endpoint
        a.ml.online_deployments.list.return_value=[SimpleNamespace(name='candidate',tags={'course':'ai300','run_id':'OTHER'})]
        run=SimpleNamespace(demo='m3-demo2',config={'endpoint':'ai300-test','candidate_deployment':'candidate','baseline_deployment':'baseline','cleanup':{'delete_candidate':True}},state={'resources':{},'run_id':'CURRENT'})
        with patch.dict(sys.modules,{'azure.core.exceptions':SimpleNamespace(ResourceNotFoundError=NotFound)}),patch('ai300.azure.Azure',return_value=a):
            report=cli.cleanup(run)
        a.ml.online_deployments.begin_delete.assert_not_called()
        self.assertIn('retained_unowned_candidate',report['cleanup_actions'][0])

    def test_passing_canary_is_eligible_and_failed_canary_restores_immediately(self):
        config={'subscription_id':'s','resource_group':'r','workspace':'w','endpoint':'ai300-offline','candidate_deployment':'candidate','baseline_deployment':'baseline'}
        frozen={'model_identity':{'id':'c'},'baseline_model_identity':{'id':'b'},'deployment_snapshot':{},'baseline_deployment_snapshot':{},'max_new_tokens':64}
        for score in (1,.5):
            rows=[{**row(kind,score if d=='candidate' else 1),'deployment':d} for d in ('candidate','baseline') for kind in ('general','exact_identifier','paraphrase')]
            run=SimpleNamespace(config=config,spec={'latency_budget_ms':30000,'minimum_by_query_type':{k:1 for k in ('general','exact_identifier','paraphrase')},'quality_gates':{'manual_correctness':.75,'manual_answer_support':.75,'schema_validity':1}},raw=Mock(),dependency=lambda *a:{'release_decision':'PASS','frozen_release':frozen},previous=lambda n:{'rows':rows} if n==1 else {'metric_snapshot':{}},state={})
            adapter=SimpleNamespace(c=config,run=run,invoke=Mock(return_value=({'deployment':'baseline','model_identity':{'id':'b'}},1)))
            with patch.object(demos,'Azure',return_value=adapter),patch.object(demos,'deployment_snapshot',return_value={}),patch.object(demos,'course_endpoint'),patch.object(demos,'manual_review',return_value={'rows':rows}),patch.object(demos,'resource_checks',return_value={'cpu':True}),patch.object(demos,'metric_values',return_value=[10]),patch.object(demos,'set_traffic') as restore:
                result=demos._canary_step(run,3)
                if score==1:
                    self.assertEqual(result['decision'],'ELIGIBLE_PENDING_ROLLBACK');restore.assert_not_called()
                else:
                    self.assertEqual(result['decision'],'STOP_PROMOTION');restore.assert_called_once_with(adapter,100,0)

    def test_only_complete_metric_buckets_inside_the_workload_can_qualify(self):
        snapshot={'window_start':'2026-11-02T12:00:20+00:00','window_end':'2026-11-02T12:02:40+00:00','snapshots':[{'resource':'/x','response':{'value':[{'name':{'value':'CpuUtilizationPercentage'},'timeseries':[{'data':[{'timeStamp':t,'average':v} for t,v in [('2026-11-02T12:00:00Z',1),('2026-11-02T12:01:00Z',2),('2026-11-02T12:02:00Z',3),('2026-11-02T12:03:00Z',4)]]}]}]}}]}
        self.assertEqual(demos.metric_values(snapshot,'CpuUtilizationPercentage',resource='/x'),[2])
        snapshot['window_end']='2026-11-02T12:00:40+00:00'
        self.assertEqual(demos.metric_values(snapshot,'CpuUtilizationPercentage',resource='/x'),[])

    def test_recovery_retry_preserves_observed_workload_and_metric_window(self):
        config={'subscription_id':'s','resource_group':'r','workspace':'w','endpoint':'ai300-offline','baseline_deployment':'baseline','candidate_deployment':'candidate'}
        frozen={'deployment_snapshot':{},'baseline_deployment_snapshot':{},'baseline_model_identity':{'id':'b'},'model_identity':{'id':'c'},'max_new_tokens':64}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp);record=path/'rollback-recovery-observations.json'
            recovery={'window_start':'2026-11-02T12:00:00+00:00','window_end':'2026-11-02T12:02:00+00:00','rows':[{'model_identity':{'id':'b'},'deployment':'baseline'}]}
            core.write(record,recovery)
            run=SimpleNamespace(path=path,config=config,state={'recovery_observations':{'path':str(record),'sha256':core.digest(record)}},spec={'latency_budget_ms':30000},raw=Mock(),dependency=lambda *a:{'release_decision':'PASS','frozen_release':frozen},previous=lambda *a:{'decision':'ELIGIBLE_PENDING_ROLLBACK'})
            adapter=SimpleNamespace(run=run,c=config,invoke=Mock(return_value=({'deployment':'baseline','model_identity':{'id':'b'}},1)))
            with patch.object(demos,'Azure',return_value=adapter),patch.object(demos,'deployment_snapshot',return_value={}),patch.object(demos,'course_endpoint'),patch.object(demos,'set_traffic',return_value={'baseline':100,'candidate':0}),patch.object(demos,'endpoint_workload') as workload,patch.object(demos,'questions_with_context') as retrieve,patch.object(demos,'monitor_snapshot',return_value={}) as monitor,patch.object(demos,'require_monitor_coverage',side_effect=[core.Hold('Telemetry pending'),None]),patch.object(demos,'metric_values',return_value=[1]):
                with self.assertRaises(core.Hold):demos._canary_step(run,4)
                result=demos._canary_step(run,4)
            self.assertTrue(result['rollback_verified']);workload.assert_not_called();retrieve.assert_not_called()
            self.assertEqual([c.args[1:] for c in monitor.call_args_list],[(recovery['window_start'],recovery['window_end'])]*2)

if __name__=='__main__':unittest.main()
