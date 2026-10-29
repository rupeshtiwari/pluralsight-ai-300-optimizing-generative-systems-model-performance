"""Real CPU contrastive fitting with explicit reviewed hard negatives."""
import argparse, os, time
from pathlib import Path
import torch, mlflow
from sentence_transformers import SentenceTransformer
from ai300.core import read, write, jsonl, object_hash, retrieval_metrics, summarize

def main():
    from ai300.versioning import require_versions, TRAIN
    runtime_versions=require_versions(TRAIN)
    p=argparse.ArgumentParser(); p.add_argument('--config',required=True); p.add_argument('--output',required=True); a=p.parse_args(); c=read(a.config); out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
    torch.manual_seed(c['seed']); torch.set_num_threads(4)
    name='sentence-transformers/all-MiniLM-L6-v2'; model=SentenceTransformer(name,revision=c['model_revisions'][name],device='cpu')
    pairs=jsonl('data/embedding-pairs.jsonl'); assert all(r['reviewed'] for r in pairs)
    docs=[r for r in jsonl('data/corpus.jsonl') if r['split']=='validation']; queries=[r for r in jsonl('data/queries.jsonl') if r['split']=='validation' and r['relevance']]
    optimizer=torch.optim.AdamW(model.parameters(),lr=c['learning_rate']); history=[]; best=-1; started=time.perf_counter()
    def embed(text): return model(model.tokenize([text]))['sentence_embedding']
    with mlflow.start_run():
        for epoch in range(c['epochs']):
            model.train(); total=0
            for pair in pairs:
                optimizer.zero_grad(); q=embed(pair['query']); positive=embed(pair['positive']); negative=embed(pair['negative'])
                # Pairwise margin contrastive objective: pull the positive above the reviewed hard negative.
                loss=torch.relu(c['margin']-torch.nn.functional.cosine_similarity(q,positive)+torch.nn.functional.cosine_similarity(q,negative)).mean()
                loss.backward(); optimizer.step(); total+=loss.item()
            model.eval(); vectors=model.encode([d['text'] for d in docs],normalize_embeddings=True,convert_to_tensor=True); rows=[]
            for q in queries:
                v=model.encode(q['question'],normalize_embeddings=True,convert_to_tensor=True); order=torch.argsort(vectors@v,descending=True).tolist()
                results=[{'source_id':docs[i]['source_id'],'content':docs[i]['text']} for i in order]; rows.append({'query_type':q['query_type'],**retrieval_metrics(results,q,k=3)})
            metrics=summarize(rows); history.append({'epoch':epoch+1,'loss':total/len(pairs),'validation_ndcg':metrics['ndcg_at_k']})
            mlflow.log_metrics(history[-1],step=epoch+1)
            if metrics['ndcg_at_k']>best: best=metrics['ndcg_at_k']; selected=epoch+1; model.save(str(out/'checkpoint'))
        result={'kind':'embedding','runtime_versions':runtime_versions,'job_name':os.getenv('AZUREML_RUN_ID'),'selected_epoch':selected,'validation_ndcg':best,'history':history,'elapsed_seconds':time.perf_counter()-started,'config':c,'pairs_sha256':object_hash(pairs),'environment':c['environment']}
        write(out/'result.json',result); mlflow.log_artifacts(str(out))
if __name__=='__main__': main()
