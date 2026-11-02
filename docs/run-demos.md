# Run the Support-Assistant Demos

[Course index](../README.md) · [Installation, Azure setup and cleanup](../setup/README.md)

The supplied project drives all eleven exercises: retrieve policy evidence, adapt embeddings, create/review synthetic support data, compare LoRA adapters, then evaluate and release a versioned endpoint. Source checks use no Azure credentials. Live workloads use real services and can incur charges; no cloud run is bundled as successful evidence.

## 1. Prepare Once

Clone the repository and complete the shared setup. It covers Python3.12.16, the pinned dependencies, CPU environments on the digest-pinned Ubuntu24.04 image, a Free Search service, a permitted Foundry deployment, and the dedicated Azure ML endpoint. Keep secrets in environment variables, never tracked JSON.

```bash
git clone https://github.com/rupeshtiwari/pluralsight-ai-300-optimizing-generative-systems-model-performance.git
cd pluralsight-ai-300-optimizing-generative-systems-model-performance
# Follow setup/README.md to create/activate .venv and install the platform-specific CPU dependencies.
cp config.example.json config.local.json
python -m ai300.setup plan
```

Open `config.local.json` in VS Code. Use actual resource IDs, immutable model commits, reviewed retrieval settings, and the completed dependency run folders. `plan` is read-only and does not provision Azure resources. Environment registration, model freezing and baseline creation are explicit setup actions in the shared setup guide.

## 2. Check the Source Without Azure

```bash
python -m compileall -q ai300 jobs serving
python -m unittest discover -s tests -v
python scripts/check_contract.py
python scripts/check_all.py
```

The all-demo check validates every declared specification and invokes all eleven offline preflights. These source checks do not establish model downloads, environment builds, cloud permissions, costs or runtime success.

## 3. Follow the Exercise Order

Each linked page contains exact prerequisites, source paths/functions, commands, expected field names, decisions, recovery and cleanup. Keep dependency evidence and live resources until dependent exercises finish.

| Order | Exercise | Run steps |
|---|---|---|
| 1 | [Demo: Tune chunk sizes and similarity cutoffs on Azure AI Search results](../module1/m1-c2/README.md) | 1, 2, 3 |
| 2 | [Demo: Run hybrid search and semantic reranking in Azure](../module1/m1-c3/README.md) | 1, 2, 3 |
| 3 | [Demo: Evaluate RAG variants with Azure services](../module1/m1-c5/README.md) | 1, 2, 3 |
| 4 | [Demo: Fine-tune domain embeddings in Azure ML](../module2/m2-c2/README.md) | 1, 2, 3 |
| 5 | [Demo: Generate and version synthetic data with Foundry](../module2/m2-c4/README.md) | 1, 2, 3 |
| 6 | [Demo: Train a LoRA adapter in Azure ML](../module2/m2-c5/README.md) | 1, 2, 3 |
| 7 | [Demo: Tune LoRA rank and select checkpoints in Azure ML](../module2/m2-c6/README.md) | 1, 2, 3 |
| 8 | [Demo: Evaluate fine-tuned candidates in Azure ML](../module3/m3-c2/README.md) | 1, 2, 3 |
| 9 | [Demo: Deploy a versioned model to Azure ML](../module3/m3-c3/README.md) | 1, 2, 3 |
| 10 | [Demo: Optimize and test the Azure model endpoint](../module3/m3-c4/README.md) | 1, 2, 3 |
| 11 | [Demo: Monitor canary traffic and verify rollback in Azure ML](../module3/m3-c5/README.md) | 1, 2, 3, 4 |

## 4. Run One Exercise

Example, from the repository root:

```bash
./module1/m1-c2/scripts/preflight_check.sh --offline
./module1/m1-c2/scripts/preflight_check.sh --live
./module1/m1-c2/scripts/lab-up.sh
./module1/m1-c2/scripts/lab-step.sh 1
./module1/m1-c2/scripts/lab-step.sh 2
./module1/m1-c2/scripts/lab-step.sh 3
```

`lab-up` initializes an evidence run; it does not execute the exercise. Each step prints its exact report location. Missing jobs, unfilled reviews, rejected quality and pending telemetry fail closed. Read failure.json and raw responses. Retry only incomplete steps after correcting the actual cause; completed reports cannot be overwritten.

## 5. Keep Manual Reviews and Dependencies Explicit

| Exercise | Human action between commands |
|---|---|
| RAG variants | Review `rag-variants-review.jsonl` before step2 and `rag-ab-review.jsonl` before completing step3 |
| Synthetic data | Review `review.jsonl` against original training sources after step1 |
| Model evaluation | Review `model-validation-review.jsonl` for the base and both adapters before step3 |
| Endpoint benchmark/final test | Review `validation-limits-review.jsonl` during step1, then `final-test-review.jsonl` for baseline AND candidate before step3 |
| Canary | After step1, review `canary-review.jsonl` against the retained question/context; step2 reads metric/alert evidence; step3 checks gates; step4 always restores and verifies baseline |

Review templates bind exact response/context hashes. Fill judgments and reasons; do not change identity fields. A source change invalidates prior dependent proof. The final-test ledger is dataset-global; a new run cannot reopen a consumed test set. If tuning resumes, provide a new untouched test set through the documented source-data workflow.

For a tuned embedding adoption, set `adopted_retrieval.field` to `tuned_vector` and retain the successful `m2-demo1` step3 run in `runs`. The engine restores its exact checkpoint, indexes that field and encodes queries with the matching BGE instruction. It never silently substitutes a baseline encoder.

## 6. Clean Up Deliberately

Run the exercise's `lab-down.sh` after its dependencies are no longer needed. Choose candidate/endpoint/Search retention in `config.local.json` before lab-up. Endpoint and storage retention can remain billable. The canary always offers step4 baseline restoration, even after a passing gate; failed gates and exceptions attempt an immediate safety restore. Never assume a killed process proves Azure recovery.
