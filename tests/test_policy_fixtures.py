"""Offline request/data contracts only; no Azure result is claimed."""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from ai300 import core
from ai300.azure import Azure

class PolicyFixtures(unittest.TestCase):
    def setUp(self):
        self.docs=core.jsonl(core.ROOT/'data/corpus.jsonl')
        self.queries=core.jsonl(core.ROOT/'data/queries.jsonl')
    def test_fixture_labels_and_reference_answer(self):
        self.assertEqual(core.validate_splits()['sources'],15)
        versions=[d for d in self.docs if d.get('error_code')=='E17']
        self.assertEqual({(d['version'],d['is_current']) for d in versions},{('1',False),('2',True)})
        self.assertEqual({d['source_group'] for d in versions},{'v-e17'})
        q=next(q for q in self.queries if q['query_id']=='v-e17-exact_identifier')
        self.assertEqual(set(q['relevance']),{'v-e17-v2'})
        self.assertTrue(core.answer_metrics(q['response'],q)['correctness'])
        old={'answer':q['support'].replace('15 minutes','30 minutes'),'source_ids':['v-e17-v1']}
        self.assertFalse(core.answer_metrics(old,q)['correctness'])
        self.assertEqual(core.retrieval_metrics([{'source_id':'v-e17-v1','content':old['answer']}],q)['recall_at_k'],0)
    def test_rejects_ambiguous_current_policy(self):
        for mutation in ('two_current','bad_type','split_group'):
            docs=copy.deepcopy(self.docs); old=next(d for d in docs if d['source_id']=='v-e17-v1')
            if mutation=='two_current': old['is_current']=True
            elif mutation=='bad_type':old['is_current']='false'
            else:old['source_group']='different'
            with patch.object(core,'jsonl',side_effect=[docs,self.queries]),self.assertRaises(core.Hold):core.validate_splits()
    def test_filter_composition_in_every_search_mode(self):
        for mode in ('vector','keyword','hybrid','semantic'):
            for policy_filter in ('all','current'):
                run=SimpleNamespace(config={'search_index':'offline'},state={'index_layout_version':'OFFLINE','tuned_checkpoint_job':'OFFLINE-JOB'},spec={'policy_filter':policy_filter})
                a=Azure(run);a.encode=lambda *args,**kwargs:[[0.]*384];requests=[]
                def search(path,body):
                    requests.append(body);return {'value':[{'source_id':'v-e17-v2','content':'OFFLINE TEST','@search.score':.75,'@search.rerankerScore':1}]},1
                a.search=search;a.query({'question':'E17'},mode=mode,depth=50,field='tuned_vector')
                expected="chunk_size eq 128 and layout_version eq 'OFFLINE'"
                if policy_filter=='current':expected+=' and is_current eq true'
                expected+=" and tuned_checkpoint_job eq 'OFFLINE-JOB'"
                self.assertEqual(requests[0]['filter'],expected)
                self.assertIn('policy_version',requests[0]['select'])
    def test_retained_hybrid_baseline_keeps_observed_filter(self):
        from ai300 import demos
        metric={'ndcg_at_k':1.,'p95_latency_ms':1,'by_query_type':{'exact_identifier':{'recall_at_k':1.,'ndcg_at_k':1.}}}
        actual={'mode':'hybrid','depth':10,'policy_filter':'current'}
        reports={1:{'variants':{'hybrid':metric},'rows':[{'variant':'hybrid','settings':actual}]},2:{'variants':{'candidate':metric},'rows':[{'variant':'candidate','settings':{'mode':'semantic','policy_filter':'current'}}]}}
        run=SimpleNamespace(spec={'latency_budget_ms':1000,'policy_filter':'all'},previous=reports.__getitem__)
        with patch.object(demos,'Azure'): result=demos.hybrid_search(run,3)
        self.assertEqual(result['decision'],'RETAIN_BASELINE')
        self.assertEqual(result['selected_settings'],actual)
        reports[1]['rows']=[]
        with patch.object(demos,'Azure'),self.assertRaisesRegex(core.Hold,'baseline settings'):demos.hybrid_search(run,3)

    def test_explicit_filter_override_and_rejection(self):
        run=SimpleNamespace(config={'search_index':'offline'},state={'index_layout_version':'OFFLINE'},spec={'policy_filter':'current'})
        a=Azure(run);a.encode=lambda *args,**kwargs:[[0.]*384];requests=[]
        a.search=lambda path,body:(requests.append(body) or {'value':[{'@search.score':.75}]},1)
        a.query({'question':'E17'},policy_filter='all')
        self.assertNotIn('is_current eq',requests[0]['filter'])
        with self.assertRaises(core.Hold):a.query({'question':'E17'},policy_filter='latest')
    def test_index_preserves_metadata_on_all_chunks(self):
        run=SimpleNamespace(config={'search_index':'offline','search_resource_id':'/offline','model_revisions':{}},state={'resources':{}},spec={'chunk_sizes':[64],'overlap_tokens':16},save=lambda:None,raw=lambda *a:None)
        a=Azure(run);a.arm=lambda *a,**k:{'sku':{'name':'free'}}
        def tokenize(text,**kwargs):return {'input_ids':list(range(len(text))),'offset_mapping':[(i,i+1) for i in range(len(text))]}
        a.model=lambda *a:SimpleNamespace(tokenizer=tokenize)
        a.encode=lambda texts,*a,**k:[[0.]*384 for _ in texts]
        requests=[]
        def search(path,body,method='POST'):
            requests.append((path,body));return {'value':[{'status':True} for _ in body.get('value',[])]},1
        a.search=search
        with patch('ai300.azure.index_layout_version',return_value='OFFLINE-LAYOUT'):a.prepare_index()
        fields={f['name']:f for f in requests[0][1]['fields']}
        self.assertTrue(fields['is_current']['filterable']);self.assertEqual(fields['is_current']['type'],'Edm.Boolean')
        for chunk in run.state['chunks']:
            source=next(d for d in self.docs if d['source_id']==chunk['source_id'])
            self.assertEqual(chunk['policy_version'],source['version'])
            self.assertEqual(chunk['is_current'],source.get('is_current',True))
        self.assertTrue(any(not c['is_current'] for c in run.state['chunks']))
if __name__=='__main__':unittest.main()
