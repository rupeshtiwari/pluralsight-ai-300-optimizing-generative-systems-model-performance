"""Live Azure adapters. No offline/fake transport is exposed by the learner CLI."""
from __future__ import annotations
import json, os, re, time, urllib.request, urllib.error, urllib.parse, uuid
from pathlib import Path
from .core import ROOT, Hold, require, read, write, digest, object_hash, jsonl, now, index_layout_version
SEARCH_API='2026-04-01'
class Azure:
    def __init__(self, run): self.run=run; self.c=run.config; self._credential=None; self._ml=None; self.encoders={}
    @property
    def credential(self):
        if self._credential is None:
            from azure.identity import DefaultAzureCredential
            self._credential=DefaultAzureCredential(exclude_interactive_browser_credential=True,process_timeout=15)
        return self._credential
    @property
    def ml(self):
        if self._ml is None:
            from azure.ai.ml import MLClient
            self._ml=MLClient(self.credential,self.c['subscription_id'],self.c['resource_group'],self.c['workspace'],connection_timeout=15,read_timeout=90,retry_total=2)
        return self._ml
    def request(self, method, url, body=None, scope='https://management.azure.com/.default', key=None):
        require(url.startswith('https://'),'Only HTTPS Azure calls are allowed.')
        headers={'Content-Type':'application/json','x-ms-client-request-id':str(uuid.uuid4())}
        if key: headers['api-key']=os.environ[key]
        else: headers['Authorization']='Bearer '+self.credential.get_token(scope).token
        request=urllib.request.Request(url,data=None if body is None else json.dumps(body).encode(),headers=headers,method=method)
        started=time.perf_counter()
        try:
            with urllib.request.urlopen(request,timeout=90) as response:
                raw=response.read(); status=response.status; response_id=response.headers.get('x-ms-request-id')
        except urllib.error.HTTPError as exc:
            error=exc.read().decode(errors='replace'); self.run.raw('azure-error',{'status':exc.code,'body':error,'url':url}); raise Hold(f'Azure HTTP {exc.code}; see raw azure-error evidence.') from exc
        result=json.loads(raw) if raw else {}
        proof={'method':method,'url':url,'request':body,'response':result,'http_status':status,'request_id':response_id,'client_request_id':headers['x-ms-client-request-id'],'latency_ms':(time.perf_counter()-started)*1000,'observed_at':now()}
        self.run.raw('azure',proof)
        return result,proof['latency_ms']
    def arm(self,method,path,body=None,version='2024-04-01'):
        return self.request(method,'https://management.azure.com'+path+('?api-version='+version),body)[0]
    def search(self,path,body=None,method='POST'):
        return self.request(method,self.c['search_endpoint'].rstrip('/')+'/'+path+'?api-version='+SEARCH_API,body,scope='https://search.azure.com/.default',key='AZURE_SEARCH_KEY' if os.getenv('AZURE_SEARCH_KEY') else None)
    def model(self,name):
        if name not in self.encoders:
            from sentence_transformers import SentenceTransformer
            revision=self.c['model_revisions'][name]; require(re.fullmatch('[0-9a-f]{40}',revision),'Pin model revision to its immutable 40-character commit, not main.')
            self.encoders[name]=SentenceTransformer(name,revision=revision,device='cpu')
        return self.encoders[name]
    def encode(self,texts,name='sentence-transformers/all-MiniLM-L6-v2',query=False):
        if query and name=='BAAI/bge-small-en-v1.5': texts=['Represent this sentence for searching relevant passages: '+x for x in texts]
        return self.model(name).encode(texts,normalize_embeddings=True,show_progress_bar=False).tolist()
    def prepare_index(self):
        # Read the management-plane SKU: a small index does not prove Free tier.
        service=self.arm('GET',self.c['search_resource_id'],version='2025-05-01')
        require(service['sku']['name'].lower()=='free','Use the approved Search Free tier.')
        fields=[{'name':'id','type':'Edm.String','key':True,'filterable':True}]
        for n in ('source_id','source_group','split','layout_version','tuned_checkpoint_job','title','content'):
            fields.append({'name':n,'type':'Edm.String','searchable':n in ('title','content'),'filterable':n not in ('title','content'),'retrievable':True})
        fields += [{'name':'chunk_size','type':'Edm.Int32','filterable':True},{'name':'token_start','type':'Edm.Int32','retrievable':True},{'name':'token_end','type':'Edm.Int32','retrievable':True}]
        for n in ('mini_vector','bge_vector','tuned_vector'):
            fields.append({'name':n,'type':'Collection(Edm.Single)','searchable':True,'dimensions':384,'vectorSearchProfile':'cpu-cosine'})
        index={'name':self.c['search_index'],'fields':fields,'vectorSearch':{'algorithms':[{'name':'hnsw-cosine','kind':'hnsw','hnswParameters':{'metric':'cosine'}}],'profiles':[{'name':'cpu-cosine','algorithm':'hnsw-cosine'}]},'semantic':{'configurations':[{'name':'support-semantic','prioritizedFields':{'titleField':{'fieldName':'title'},'prioritizedContentFields':[{'fieldName':'content'}]}}]}}
        # PUT is idempotent and never deletes an existing index. Incompatible fields fail.
        self.search('indexes/'+self.c['search_index'],index,'PUT')
        self.run.state['resources']['search_index']=self.c['search_index']; self.run.save()
        layout=index_layout_version(self.c,self.run.spec); self.run.state['index_layout_version']=layout; self.run.save()
        tokenizer=self.model('sentence-transformers/all-MiniLM-L6-v2').tokenizer
        chunks=[]
        for d in jsonl(ROOT/'data/corpus.jsonl'):
            tokens=tokenizer.encode(d['text'],add_special_tokens=False)
            for size in self.run.spec.get('chunk_sizes',[64,128,192]):
                for start in range(0,len(tokens),size-self.run.spec.get('overlap_tokens',16)):
                    part=tokens[start:start+size]
                    chunks.append({'@search.action':'mergeOrUpload','id':f"{layout[:12]}-{d['source_id']}-{size}-{start}",'layout_version':layout,'source_id':d['source_id'],'source_group':d['source_group'],'split':d['split'],'title':d['title'],'content':tokenizer.decode(part),'chunk_size':size,'token_start':start,'token_end':start+len(part)})
        for field,name in [('mini_vector','sentence-transformers/all-MiniLM-L6-v2'),('bge_vector','BAAI/bge-small-en-v1.5')]:
            vectors=self.encode([x['content'] for x in chunks],name)
            for chunk,vector in zip(chunks,vectors): chunk[field]=vector
        require(len(json.dumps(chunks).encode())<10_000_000,'Tiny course corpus unexpectedly exceeds 10 MB.')
        for i in range(0,len(chunks),100):
            result,_=self.search(f"indexes/{self.c['search_index']}/docs/index",{'value':chunks[i:i+100]})
            require(all(x['status'] for x in result['value']),'Partial indexing failure.')
        self.run.raw('index-layout',{'index':index,'chunk_count':len(chunks),'model_revisions':self.c['model_revisions']})
        self.run.state['chunks']=chunks; self.run.save()
        return len(chunks)
    def query(self,q,*,mode='vector',size=128,depth=10,cutoff=None,weight=1.,field='mini_vector',encoder=None,k=5):
        require(cutoff is None or mode=='vector','Cannot convert or cutoff a hybrid/semantic score.')
        layout=self.run.state.get('index_layout_version'); require(layout,"Prepare this run's versioned index layout first.")
        body={'select':'id,source_id,content,chunk_size,token_start,token_end,layout_version','filter':f"chunk_size eq {size} and layout_version eq '{layout}'",'top':depth if cutoff is not None else k}
        if field=='tuned_vector':
            checkpoint=self.run.state.get('tuned_checkpoint_job'); require(checkpoint,'Selected embedding checkpoint identity is missing.'); body['filter']+=f" and tuned_checkpoint_job eq '{checkpoint}'"
        if mode in ('keyword','hybrid','semantic'): body['search']=q['question']
        if mode!='keyword':
            vector=encoder.encode([q['question']],normalize_embeddings=True).tolist()[0] if encoder else self.encode([q['question']],name='BAAI/bge-small-en-v1.5' if field=='bge_vector' else 'sentence-transformers/all-MiniLM-L6-v2',query=True)[0]
            body['vectorQueries']=[{'kind':'vector','vector':vector,'fields':field,'k':depth,'weight':weight}]; body['vectorFilterMode']='preFilter'
        if mode=='semantic':
            require(depth>=50,'Semantic ranking needs the approved 50 vector candidates.'); body.update(queryType='semantic',semanticConfiguration='support-semantic')
        result,elapsed=self.search(f"indexes/{self.c['search_index']}/docs/search",body)
        rows=result['value']; require(bool(rows),'No retrieval results: wait for indexing or inspect the filter.')
        if mode=='semantic': require(all('@search.rerankerScore' in x for x in rows),'Semantic reranker evidence missing.')
        from .core import cosine_from_score
        rejected=[]
        if mode=='vector':
            for row in rows: row['cosine_similarity']=cosine_from_score(row['@search.score'])
        if cutoff is not None:
            rejected=[r for r in rows if r['cosine_similarity']<cutoff]; rows=[r for r in rows if r['cosine_similarity']>=cutoff]
        return rows[:k],rejected,elapsed
    def generate(self,question,contexts,synthetic=False,trace=None):
        from openai import OpenAI
        from azure.identity import get_bearer_token_provider
        deployment=self.arm('GET',self.c['foundry_resource_id']+'/deployments/'+self.c['foundry_deployment'],version='2024-10-01')
        actual=deployment['properties']['model']; require(actual['name']==self.c['foundry_model'] and actual['version']==self.c['foundry_version'],'Foundry deployment does not match frozen model/version.')
        key=os.getenv('AZURE_OPENAI_API_KEY') or get_bearer_token_provider(self.credential,'https://cognitiveservices.azure.com/.default')
        client=OpenAI(base_url=self.c['foundry_endpoint'],api_key=key,timeout=90,max_retries=1)
        instructions='Return only JSON with answer (string) and source_ids (array of source IDs). Answer using only the supplied policy evidence; if absent say insufficient evidence. Preserve every policy condition.'
        if synthetic: instructions='Return only JSON with question (string), answer (string), source_ids (array). Write one support training example answerable from the supplied source. Preserve every condition.'
        started=time.perf_counter()
        request={'model':self.c['foundry_deployment'],'messages':[{'role':'system','content':instructions},{'role':'user','content':json.dumps({'question':question,'evidence':contexts})}],'max_completion_tokens':512,'reasoning_effort':'none','response_format':{'type':'json_object'}}
        response=client.chat.completions.create(**request)
        record={'trace':trace,'request':request,'deployment_readback':deployment,'response':response.model_dump(),'observed_at':now()}
        evidence_path=self.run.raw('foundry',record); self.last_generation_evidence={'evidence_path':evidence_path,'sha256':digest(evidence_path),'response_id':response.id}
        require(response.choices[0].finish_reason=='stop' and response.choices[0].message.content,'Foundry output incomplete/refused; inspect raw response, do not score it as success.')
        return response.choices[0].message.content,(time.perf_counter()-started)*1000,response.usage.completion_tokens
    def track(self,name,report,folder):
        import mlflow
        uri=self.ml.workspaces.get(self.c['workspace']).mlflow_tracking_uri
        require(uri.startswith('azureml://'),'MLflow must point to genuine Azure ML, not local tracking.')
        mlflow.set_tracking_uri(uri); mlflow.set_experiment('ai300-'+name)
        with mlflow.start_run(run_name=self.run.state['run_id']) as active:
            mlflow.log_params({'demo':self.run.demo,'source_hash':object_hash(read(self.run.path/'manifest.json')['source_hashes'])})
            for key,value in report.items():
                if isinstance(value,(int,float)): mlflow.log_metric(key,value)
            mlflow.log_artifacts(str(folder)); rid=active.info.run_id
        return {'mlflow_run_id':rid,'tracking_uri':uri}
    def invoke(self,payload,deployment=None):
        endpoint=course_endpoint(self)
        headers={}
        if deployment: headers['azureml-model-deployment']=deployment
        token=self.ml.online_endpoints.get_keys(self.c['endpoint'])
        # Scoring uses endpoint authentication, not management-plane authorization.
        auth=token.primary_key if endpoint.auth_mode=='key' else token.access_token
        request=urllib.request.Request(endpoint.scoring_uri,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+auth,'Content-Type':'application/json',**headers},method='POST')
        started=time.perf_counter()
        with urllib.request.urlopen(request,timeout=120) as response: result=json.loads(response.read())
        require(isinstance(result,dict) and 'model_identity' in result,'Scoring response lacks model identity.')
        elapsed=(time.perf_counter()-started)*1000; self.run.raw('endpoint',{'deployment_override':deployment,'request':payload,'response':result,'latency_ms':elapsed,'at':now()})
        return result,elapsed

def resolve_environment(client,reference,definition):
    """Resolve only immutable workspace versions and compare declared CPU dependencies."""
    import yaml
    if reference.startswith('azureml:'):
        parts=reference.split(':'); require(len(parts)==3 and parts[2]!='latest','Environment must use an exact version.'); _,name,version=parts
    else:
        match=re.search(r'/environments/([^/]+)/versions/([^/]+)$',reference); require(match is not None,'Environment reference must be an exact registered version.'); name,version=match.groups()
    environment=client.environments.get(name=name,version=version)
    require('@sha256:' in (environment.image or ''),'Environment image must be pinned by digest.')
    actual=environment.conda_file
    if isinstance(actual,str):
        # SDK readback can return serialized YAML. Never treat Azure strings as arbitrary local filenames.
        actual=yaml.safe_load(actual)
    expected=yaml.safe_load((ROOT/'environments'/definition).read_text())
    require(actual==expected,'Registered environment dependencies do not match the versioned CPU definition.')
    return {'id':environment.id,'image':environment.image,'conda_sha256':object_hash(actual)}

def deployment_snapshot(a,name):
    deployment=a.ml.online_deployments.get(name,a.c['endpoint'])
    require(deployment.provisioning_state=='Succeeded','Deployment is not Succeeded.')
    ref=lambda x: str(getattr(x,'id',x))
    code=deployment.code_configuration; require(code is not None and code.code,'Deployment has no versioned code identity.')
    result={'deployment':name,'model_id':ref(deployment.model),'environment_id':ref(deployment.environment),'code_id':ref(code.code),'scoring_script':code.scoring_script,'instance_type':deployment.instance_type,'instance_count':deployment.instance_count,'environment_variables':deployment.environment_variables,'request_timeout_ms':deployment.request_settings.request_timeout_ms,'max_concurrent_requests_per_instance':deployment.request_settings.max_concurrent_requests_per_instance}
    a.run.raw('deployment-identity',result); return result

def require_course_endpoint(endpoint,configured_name):
    require(configured_name.startswith('ai300-') and endpoint.name==configured_name,'Only the named dedicated ai300- endpoint is allowed.')
    tags=endpoint.tags or {}
    require(tags.get('course')=='ai300' and tags.get('purpose')=='disposable-course-lab','Endpoint must be explicitly tagged course=ai300 and purpose=disposable-course-lab. Refusing ordinary endpoint mutation or test traffic.')
    return endpoint

def course_endpoint(a):
    return require_course_endpoint(a.ml.online_endpoints.get(a.c['endpoint']),a.c['endpoint'])
