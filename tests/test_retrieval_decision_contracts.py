"""Offline behavior regressions, not Azure execution or statistical evidence."""
import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from ai300 import core, demos


class RetrievalDecisionContractTests(unittest.TestCase):
    def test_aggregate_gain_cannot_hide_ndcg_slice_regression(self):
        baseline={'ndcg_at_k':.6,'p95_latency_ms':100,'by_query_type':{'exact_identifier':{'recall_at_k':1.,'ndcg_at_k':.8},'paraphrase':{'recall_at_k':1.,'ndcg_at_k':.4}}}
        candidate={'ndcg_at_k':.7,'p95_latency_ms':100,'by_query_type':{'exact_identifier':{'recall_at_k':1.,'ndcg_at_k':.6},'paraphrase':{'recall_at_k':1.,'ndcg_at_k':.8}}}
        reports={1:{'variants':{'hybrid':baseline},'rows':[{'variant':'hybrid','settings':{'mode':'hybrid','depth':10,'policy_filter':'all'}}]},2:{'variants':{'candidate':candidate},'rows':[{'variant':'candidate','settings':{'mode':'semantic'}}]}}
        run=SimpleNamespace(spec={'latency_budget_ms':1000},previous=reports.__getitem__)
        with patch.object(demos,'Azure'):
            report=demos.hybrid_search(run,3)
        self.assertEqual(report['decision'],'RETAIN_BASELINE')
        self.assertIsNone(report['selected_variant'])
        self.assertEqual(len(report['query_type_regressions']),1)
        regression=report['query_type_regressions'][0]
        self.assertEqual(regression['query_type'],'exact_identifier')
        self.assertEqual(regression['recall_delta'],0)
        self.assertLess(regression['ndcg_delta'],0)
        self.assertEqual(regression['regressed_metrics'],['ndcg_at_k'])

    def test_missing_query_type_evidence_cannot_pass(self):
        baseline={'ndcg_at_k':.6,'by_query_type':{'exact_identifier':{'recall_at_k':1.,'ndcg_at_k':.8}}}
        run=SimpleNamespace(spec={'latency_budget_ms':1000},previous=lambda n:{'variants':{'hybrid':baseline}} if n==1 else {'variants':{'candidate':{'by_query_type':{}}},'rows':[]})
        with patch.object(demos,'Azure'),self.assertRaisesRegex(core.Hold,'Missing query-type evidence'):
            demos.hybrid_search(run,3)

    def make_run(self, path):
        return SimpleNamespace(path=Path(path),attempt=Path(path)/'attempt',state={'run_id':'OFFLINE-TEST'},spec={'sessions':24,'primary_metric':'manual_answer_support','stop_rule':'fixed_sessions_no_early_efficacy'},config={'foundry_deployment':'offline-fixture','foundry_version':'fixture-version'},save=Mock())

    def test_predeclaration_precedes_first_retrieval_and_binds_settings(self):
        with tempfile.TemporaryDirectory() as temp:
            run=self.make_run(temp)
            azure=Mock()
            def inspect_before_dispatch():
                saved=core.read(run.path/'ab-experiment-contract.json')
                self.assertEqual(saved['primary_metric'],'manual_answer_support')
                self.assertEqual(saved['session_count'],24)
                self.assertEqual(saved['fixed_generation']['deployment'],'offline-fixture')
                self.assertEqual(run.state['ab_experiment_contract']['sha256'],core.digest(run.path/'ab-experiment-contract.json'))
                self.assertFalse((run.path/'ab-observations.json').exists())
                raise core.Hold('OFFLINE stop before service dispatch')
            azure.prepare_index.side_effect=inspect_before_dispatch
            with patch.object(demos,'Azure',return_value=azure),self.assertRaisesRegex(core.Hold,'OFFLINE stop'):
                demos.rag_ab(run,1)
            azure.query.assert_not_called()
            first=demos.ab_experiment_contract(run)
            second=demos.ab_experiment_contract(run)
            self.assertEqual(first,second)

    def test_contract_cannot_change_after_predeclaration(self):
        for field in ('sessions','primary_metric','stop_rule','generation','file'):
            with self.subTest(field=field),tempfile.TemporaryDirectory() as temp:
                run=self.make_run(temp); demos.ab_experiment_contract(run)
                original=core.digest(run.path/'ab-experiment-contract.json')
                if field=='sessions': run.spec['sessions']=25
                elif field=='primary_metric': run.spec['primary_metric']='ndcg_at_k'
                elif field=='stop_rule': run.spec['stop_rule']='stop_when_winning'
                elif field=='generation': run.config['foundry_version']='different-version'
                else:
                    saved=core.read(run.path/'ab-experiment-contract.json'); saved['session_count']=25; core.write(run.path/'ab-experiment-contract.json',saved)
                with patch.object(demos,'Azure') as azure,self.assertRaises(core.Hold):
                    demos.rag_ab(run,3)
                azure.assert_not_called()
                if field!='file':self.assertEqual(original,core.digest(run.path/'ab-experiment-contract.json'))

    def test_existing_assignments_cannot_be_retroactively_predeclared(self):
        with tempfile.TemporaryDirectory() as temp:
            run=self.make_run(temp); core.write(run.path/'ab-observations.json',{'sessions':[]})
            with self.assertRaisesRegex(core.Hold,'assignments exist without'):
                demos.ab_experiment_contract(run)
            self.assertFalse((run.path/'ab-experiment-contract.json').exists())

    def test_ab_uncertainty_counts_actual_retained_questions(self):
        # Exercise the real report path with completed offline observations.
        # The subset case prevents substituting the full validation-set size.
        questions=demos.validation()
        self.assertEqual(len(questions),10)
        for session_count,question_count in ((24,10),(6,3)):
            with self.subTest(sessions=session_count),tempfile.TemporaryDirectory() as temp:
                run=self.make_run(temp);run.spec['sessions']=session_count;run.attempt.mkdir()
                experiment=demos.ab_experiment_contract(run)
                sessions=[]
                for i in range(session_count):
                    q=questions[i%question_count]
                    outcome={'status':'COMPLETED','query_id':q['query_id'],'arm':'A' if i%2==0 else 'B'}
                    sessions.append({'status':'COMPLETED','query_id':q['query_id'],'outcome':outcome})
                observed=run.path/'ab-observations.json'
                core.write(observed,{'experiment_contract_sha256':experiment['sha256'],'sessions':sessions})
                run.state['ab_observations']={'path':str(observed),'sha256':core.digest(observed)}
                for name in ('ab-exposures.jsonl','ab-outcomes.jsonl','rag-ab-review.jsonl'):
                    (run.path/name).write_text('')
                reviewed={'rows':[row['outcome'] for row in sessions],
                          'by_variant':{'A':{'manual_answer_support':.5},'B':{'manual_answer_support':.5}}}
                azure=Mock();azure.track.return_value={}
                with patch.object(demos,'Azure',return_value=azure),patch.object(demos,'manual_review',return_value=reviewed),patch.object(demos,'summarize',return_value={}):
                    report=demos.rag_ab(run,3)
                self.assertIn(f'cover {question_count} distinct questions',report['uncertainty'])
                self.assertIn('No inferential confidence interval is justified',report['uncertainty'])
                self.assertEqual(report['decision'],'COLLECT_MORE_EVIDENCE')
                self.assertEqual(report['assigned_sessions'],session_count)
                self.assertEqual(report['completed_outcomes'],session_count)
                azure.query.assert_not_called()
                azure.generate.assert_not_called()

    def test_invalid_experiment_config_fails_before_live_preflight(self):
        valid={'sessions':24,'primary_metric':'manual_answer_support','stop_rule':'fixed_sessions_no_early_efficacy'}
        core.validate_demo_spec('m1-demo3',valid)
        for patch_value in ({'sessions':0},{'sessions':True},{'primary_metric':'answer_support_proxy'},{'stop_rule':'optional_stopping'}):
            with self.subTest(patch_value=patch_value),self.assertRaises(core.Hold):
                core.validate_demo_spec('m1-demo3',{**valid,**patch_value})

if __name__=='__main__':unittest.main()
