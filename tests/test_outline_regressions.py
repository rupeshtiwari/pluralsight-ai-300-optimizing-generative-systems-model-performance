"""Offline doubles verify final-outline behavior; never Azure execution proof."""
import ast
import argparse
import os
import sys
import time
import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, MagicMock, patch
from ai300 import demos, core
from ai300.azure import Azure


class OutlineRegressionTests(unittest.TestCase):
    def test_embedding_training_and_validation_use_bge_query_instruction(self):
        tree=ast.parse((core.ROOT/'jobs/train_embedding.py').read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        model=MagicMock(); model.return_value={'sentence_embedding':MagicMock()}
        torch=MagicMock(); torch.relu.return_value.mean.return_value.item.return_value=1.0
        torch.argsort.return_value.tolist.return_value=[0]
        constructor=Mock(return_value=model)
        config={'seed':17,'model_revisions':{'BAAI/bge-small-en-v1.5':'immutable'},'learning_rate':0.00002,'epochs':1,'margin':.2,'environment':'env'}
        records={'data/embedding-pairs.jsonl':[{'reviewed':True,'query':'Training query','positive':'Positive document','negative':'Negative document'}],'data/corpus.jsonl':[{'split':'validation','source_id':'doc','text':'Validation document'}],'data/queries.jsonl':[{'split':'validation','question':'Validation query','relevance':{'doc':3},'query_type':'domain'}]}
        namespace={'argparse':argparse,'Path':Path,'os':os,'time':time,'torch':torch,'mlflow':MagicMock(),'SentenceTransformer':constructor,'read':lambda p:config,'write':Mock(),'jsonl':lambda p:records[str(p)],'object_hash':core.object_hash,'retrieval_metrics':lambda *a,**k:{'ndcg_at_k':1},'summarize':lambda rows:{'ndcg_at_k':1}}
        exec(compile(ast.Module(body=[function],type_ignores=[]),'train_embedding','exec'),namespace)
        with tempfile.TemporaryDirectory() as temp,patch.object(sys,'argv',['train','--config','config','--output',temp]),patch('ai300.versioning.require_versions',return_value={}):
            namespace['main']()
        constructor.assert_called_once_with('BAAI/bge-small-en-v1.5',revision='immutable',device='cpu')
        self.assertEqual([call.args[0] for call in model.tokenize.call_args_list],[['Represent this sentence for searching relevant passages: Training query'],['Positive document'],['Negative document']])
        self.assertEqual([call.args[0] for call in model.encode.call_args_list],[['Validation document'],'Represent this sentence for searching relevant passages: Validation query'])

    def test_rank_comparison_rejects_learning_rate_drift(self):
        config={key:1 for key in ('learning_rate','batch_size','seed','epochs','target_modules','max_length','max_new_tokens','base_revision','model_revisions','environment')}
        first={'result':{'config':config,'data_sha256':'data','validation_sha256':'validation'}}
        second={'output_path':'offline','result':{'config':{**config,'learning_rate':2},'data_sha256':'data','validation_sha256':'validation'}}
        run=SimpleNamespace(config={},dependency=lambda *a:first,previous=lambda n:{})
        with patch.object(demos,'completed',return_value=second),patch.object(demos,'read',return_value={}):
            with self.assertRaisesRegex(core.Hold,'Controlled factor drift'): demos.lora_select(run,2)

    def test_evaluate_job_runs_base_and_both_adapters_with_identical_context(self):
        tree=ast.parse((core.ROOT/'jobs/evaluate.py').read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        contexts={'q':[{'source_id':'retrieved','content':'Actual retrieval'}]}
        config={'seed':17,'max_new_tokens':64,'retrieved_context':contexts,'retrieved_context_sha256':core.object_hash(contexts)}
        evaluate=Mock(return_value={'summary':{'score':1,'by_query_type':{'domain':{'score':1}}},'rows':[]})
        load_base=Mock(side_effect=[('base','tokenizer'),('base','tokenizer'),('base','tokenizer')]); peft=Mock(); peft.from_pretrained.side_effect=['one','two']; write=Mock(); mlflow=MagicMock()
        namespace={'argparse':argparse,'os':os,'Path':Path,'mlflow':mlflow,'PeftModel':peft,'read':lambda p:config,'write':write,'jsonl':lambda p:[{'source_id':'oracle','text':'Label'}] if 'corpus' in str(p) else [{'split':'validation','query_id':'q','relevance':{'oracle':3}}],'object_hash':core.object_hash,'load_base':load_base,'evaluate':evaluate,'seed':Mock()}
        exec(compile(ast.Module(body=[function],type_ignores=[]),'evaluate','exec'),namespace)
        with tempfile.TemporaryDirectory() as temp,patch.object(sys,'argv',['evaluate','--config','c','--adapter','first','--adapter2','second','--output',temp]),patch('ai300.versioning.require_versions',return_value={}): namespace['main']()
        self.assertEqual([call.args[0] for call in evaluate.call_args_list],['base','one','two'])
        self.assertTrue(all(call.args[2][0]['retrieved_context']==contexts['q'] for call in evaluate.call_args_list))
        self.assertEqual(set(write.call_args.args[1]['results']),{'base','adapter','adapter2'})
        mlflow.log_metric.assert_any_call('adapter2_domain_score',1)

    def test_second_adapter_winner_preserves_second_checkpoint_identity(self):
        rows=[{'variant':variant,'query_id':kind,'query_type':kind,'schema_validity':1,'manual_correctness':0 if variant=='adapter' else 1,'manual_answer_support':1} for variant in ('base','adapter','adapter2') for kind in ('general','exact_identifier','paraphrase')]
        checkpoints=[{'job_name':name,'output_path':name+'-path','output_uri':name+'-uri','result':{'identity':name}} for name in ('first','second')]
        report={'result':{'results':{v:{'rows':[r for r in rows if r['variant']==v]} for v in ('base','adapter','adapter2')},'validation_sha256':'hash','config':{}},'job_name':'eval','result_sha256':'hash'}
        run=SimpleNamespace(config={},spec={'gates':{'manual_correctness':.75,'manual_answer_support':.75,'schema_validity':1,'max_regression':0}},dependency=lambda *a:{'shortlisted_checkpoints':checkpoints},previous=lambda n:report)
        with patch.object(demos,'manual_review',return_value={'rows':rows}): result=demos.model_evaluate(run,3)
        self.assertEqual(result['decision'],'PASS'); self.assertEqual(result['selected_job'],'second'); self.assertEqual(result['selected_output_uri'],'second-uri'); self.assertEqual(result['selected_result'],{'identity':'second'})

    def test_tuned_query_has_bge_instruction_but_search_evidence_is_unchanged(self):
        run=SimpleNamespace(config={'search_index':'offline-index'}, state={'index_layout_version':'layout','tuned_checkpoint_job':'job'})
        azure=Azure(run)
        encoder=Mock(); encoder.encode.return_value.tolist.return_value=[[1,0]]
        evidence={'source_id':'wrong-document','content':'Actual retrieved text','@search.score':1}
        azure.search=Mock(return_value=({'value':[evidence]},1))
        rows,_,_=azure.query({'question':'Refund policy?'},field='tuned_vector',encoder=encoder)
        encoder.encode.assert_called_once_with(['Represent this sentence for searching relevant passages: Refund policy?'],normalize_embeddings=True)
        self.assertEqual(rows[0]['content'],'Actual retrieved text')
        self.assertIn("tuned_checkpoint_job eq 'job'",azure.search.call_args.args[1]['filter'])

    def test_rank_submission_preserves_every_other_control_and_shortlists_both(self):
        original={'rank':4,'learning_rate':0.0002,'seed':17,'target_modules':['q_proj'],'batch_size':1,'epochs':2}
        first={'job_name':'first','output_path':'first-path','output_uri':'first-uri','result':{'config':original,'validation_loss':.4,'elapsed_seconds':10},'adapted':{'summary':{}}}
        second={**first,'job_name':'second','output_uri':'second-uri','result':{**first['result'],'validation_loss':.3,'elapsed_seconds':20}}
        run=SimpleNamespace(config={},spec={'rank':8,'learning_rate':99},dependency=lambda demo,n:first if demo=='m2-demo3' else {'data_assets':{'training_bundle':'data'}},previous=lambda n:{'first':first,'second':second})
        with patch.object(demos,'submit',return_value={}) as submit:
            demos.lora_select(run,1)
        config=submit.call_args.args[2]
        self.assertEqual({k:v for k,v in config.items() if k!='rank'},{k:v for k,v in original.items() if k!='rank'})
        self.assertEqual(config['rank'],8)
        shortlisted=demos.lora_select(run,3)['shortlisted_checkpoints']
        self.assertEqual([r['output_uri'] for r in shortlisted],['first-uri','second-uri'])

    def test_evaluation_submits_actual_context_identically_for_both_adapters(self):
        questions=[{'query_id':'q','question':'Refund?','relevance':{'oracle':3}}]
        actual=[{'source_id':'wrong-document','content':'Retrieved, not oracle'}]
        azure=Mock(); azure.query.return_value=(actual,[],1)
        run=SimpleNamespace(config={'adopted_retrieval':{'field':'bge_vector','size':128}},spec={},dependency=lambda *args:{'shortlisted_checkpoints':[{'output_uri':'one'},{'output_uri':'two'}]})
        with patch.object(demos,'Azure',return_value=azure),patch.object(demos,'validation',return_value=questions),patch.object(demos,'submit',return_value={}) as submit:
            demos.model_evaluate(run,1)
        config=submit.call_args.args[2]
        self.assertEqual(config['retrieved_context'],{'q':actual})
        self.assertEqual(config['retrieved_context_sha256'],core.object_hash({'q':actual}))
        self.assertEqual(submit.call_args.kwargs,{'adapter':'one','adapter2':'two'})
        azure.prepare_index.assert_called_once()
        # Execute the real prompt constructor without importing optional training libraries.
        module=ast.parse((core.ROOT/'jobs/common.py').read_text())
        function=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='messages')
        namespace={'json':json}; exec(compile(ast.Module(body=[function],type_ignores=[]),'messages','exec'),namespace)
        prompt=namespace['messages']({**questions[0],'retrieved_context':actual},{'oracle':{'text':'Never supply this label document'}})
        self.assertEqual(json.loads(prompt[-1]['content'])['evidence'],actual)
        prompt=namespace['messages']({**questions[0],'retrieved_context':[]},{'oracle':{'text':'Never supply this'}})
        self.assertEqual(json.loads(prompt[-1]['content'])['evidence'],[])

    def test_final_test_runs_baseline_and_candidate_once_with_same_settings(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); path=root/'run'; path.mkdir()
            snap={'request_timeout_ms':180000}
            dep={'model_identity':{'id':'candidate'},'baseline_model_identity':{'id':'baseline'},'deployment_snapshot':snap,'baseline_deployment_snapshot':snap,'endpoint_auth_mode':'key','environment_identity':{},'model_id':'model','environment':'env','scoring_sha256':'hash'}
            questions=[{'split':'test','query_id':'q','question':'Q'}]
            run=SimpleNamespace(config={'candidate_deployment':'candidate','baseline_deployment':'baseline'},state={},path=path,dependency=lambda *args:dep,previous=lambda n:{'selected_max_new_tokens':64})
            with patch.object(demos,'ROOT',root),patch.object(demos,'jsonl',return_value=questions),patch.object(demos,'deployment_snapshot',return_value=snap),patch.object(demos,'endpoint_workload',side_effect=[{'rows':[]},{'rows':[]}]) as workload,patch.object(demos,'prepare_manual_review',return_value=('review',{})):
                result=demos.endpoint_test(run,2)
                self.assertEqual(workload.call_count,2)
                self.assertEqual([call.args[3] for call in workload.call_args_list],['baseline','candidate'])
                self.assertEqual([call.args[1:3] for call in workload.call_args_list],[(questions,64),(questions,64)])
                self.assertIn('baseline_comparison',result['final_test'])
                with self.assertRaises(core.Hold): demos.endpoint_test(run,2)
                self.assertEqual(workload.call_count,2)

    def test_release_report_links_exact_model_version_and_preserves_tags(self):
        rows=[{'query_id':'q','query_type':'domain','schema_validity':1,'manual_correctness':1,'manual_answer_support':1,'latency_ms':10}]
        previous={'final_test':{'rows':rows,'baseline_comparison':{'rows':rows}},'frozen_release':{'model':'frozen'},'frozen_release_sha256':'frozen-hash'}
        identity={'model_name':'exact-model','model_version':'17'}
        with tempfile.TemporaryDirectory() as temp:
            run=SimpleNamespace(config={'candidate_deployment':'candidate','baseline_deployment':'baseline'},attempt=Path(temp),spec={'gates':{'schema_validity':1,'manual_correctness':.75,'manual_answer_support':.75},'latency_budget_ms':30000},dependency=lambda *args:{'model_identity':identity,'deployment_snapshot':{}},previous=lambda n:previous)
            azure=Mock(); azure.track.return_value={'mlflow_run_id':'real-run-reference'}; model=SimpleNamespace(tags={'training':'retained'}); azure.ml.models.get.return_value=model
            with patch.object(demos,'Azure',return_value=azure),patch.object(demos,'deployment_snapshot',return_value={}),patch.object(demos,'monitor_snapshot',return_value={'snapshots':[]}),patch.object(demos,'require_monitor_coverage'),patch.object(demos,'manual_review',return_value={'rows':rows}):
                result=demos.endpoint_test(run,3)
            self.assertEqual(result['release_decision'],'PASS')
            azure.ml.models.get.assert_called_once_with(name='exact-model',version='17')
            azure.ml.models.create_or_update.assert_called_once_with(model)
            self.assertEqual(model.tags['training'],'retained')
            self.assertEqual(model.tags['release_mlflow_run_id'],'real-run-reference')
            self.assertEqual(model.tags['release_evidence_sha256'],core.digest(run.attempt/'release-evidence.json'))
            self.assertEqual(model.tags['frozen_release_sha256'],'frozen-hash')

    def test_missing_utilization_blocks_final_gate_without_replaying_workload(self):
        run=SimpleNamespace(config={'candidate_deployment':'candidate','baseline_deployment':'baseline'},dependency=lambda *args:{'model_identity':{},'deployment_snapshot':{}},previous=lambda n:{'final_test':{'rows':[]}})
        with patch.object(demos,'deployment_snapshot',return_value={}),patch.object(demos,'monitor_snapshot',return_value={'snapshots':[]}),patch.object(demos,'endpoint_resource',return_value='/offline'),patch.object(demos,'endpoint_workload') as workload:
            with self.assertRaises(core.Hold): demos.endpoint_test(run,3)
            workload.assert_not_called()

    def test_demo_inspects_prepared_alert_and_rejects_mismatched_rule(self):
        config={'subscription_id':'s','resource_group':'rg','workspace':'w','endpoint':'ai300-offline','baseline_deployment':'baseline','candidate_deployment':'candidate','monitor_action_group_id':'action'}
        frozen={'model_identity':{'id':'candidate'},'baseline_model_identity':{'id':'baseline'},'deployment_snapshot':{},'baseline_deployment_snapshot':{},'max_new_tokens':64}
        run=SimpleNamespace(config=config,spec={'rollback_test':{'enabled':False},'latency_budget_ms':30000},state={'run_id':'OFFLINE','resources':{}},save=lambda:None,raw=lambda *args:None,dependency=lambda *args:{'release_decision':'PASS','frozen_release':frozen})
        azure=Mock(); azure.run=run; azure.c=config
        demos.prepare_canary_alert(azure)
        prepared=copy.deepcopy(azure.arm.call_args.args[2]); azure.arm.reset_mock(); azure.arm.return_value=prepared
        azure.invoke.return_value=({'deployment':'baseline','model_identity':{'id':'baseline'}},1)
        with patch.object(demos,'Azure',return_value=azure),patch.object(demos,'deployment_snapshot',return_value={}),patch.object(demos,'course_endpoint'),patch.object(demos,'endpoint_payload',return_value={}),patch.object(demos,'endpoint_workload',return_value={}),patch.object(demos,'monitor_snapshot',return_value={'snapshots':[]}):
            demos._canary_step(run,1)
            self.assertEqual([c.args[0] for c in azure.arm.call_args_list],['GET'])
            mutations=[('enabled',False),('scopes',['/wrong']),('actions',[{'actionGroupId':'wrong'}])]
            for field,value in mutations:
                azure.arm.return_value=copy.deepcopy(prepared); azure.arm.return_value['properties'][field]=value
                with self.subTest(field=field),self.assertRaises(core.Hold): demos._canary_step(run,1)
            for field,value in [('metricName','WrongMetric'),('threshold',1),('dimensions',[{'name':'deployment','operator':'Include','values':['wrong']}])]:
                azure.arm.return_value=copy.deepcopy(prepared); azure.arm.return_value['properties']['criteria']['allOf'][0][field]=value
                with self.subTest(field=field),self.assertRaises(core.Hold): demos._canary_step(run,1)
            self.assertTrue(all(c.args[0]=='GET' for c in azure.arm.call_args_list))

if __name__=='__main__': unittest.main()
