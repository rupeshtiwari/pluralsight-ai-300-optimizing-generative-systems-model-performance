# Demo: Fine-tune domain embeddings in Azure ML

[Previous: Evaluate RAG variants with Azure services](../../module1/m1-c5/README.md) · [Course index](../../README.md) · [Next: Generate and version synthetic data with Foundry](../m2-c4/README.md)

Module 2, clip 2 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

Domain phrases still retrieve weak evidence. Train a small CPU embedding checkpoint using reviewed pairs, then compare it without mixing vector versions.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1b** — Select and fine-tune embedding models for domain-specific use cases and accuracy improvements

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

This exercise has no earlier demo dependency. Its own setup establishes the index or job from the supplied corpus and labels, using your configured Azure resources.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m2-demo1-after
source .venv/bin/activate
./module2/m2-c2/scripts/preflight_check.sh
./module2/m2-c2/scripts/lab-up.sh
```

Read [`configs/m2-demo1.json`](../../configs/m2-demo1.json) and [`jobs/train_embedding.py`](../../jobs/train_embedding.py), [`ai300/ml.py`](../../ai300/ml.py), [`data/embedding-pairs.jsonl`](../../data/embedding-pairs.jsonl). The shared implementation is [`embedding_train`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run.

`lab-up` prints your unique `evidence/m2-demo1/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Configure a Sentence Transformers contrastive training script with reviewed positive pairs and hard negatives, then submit an Azure ML CPU command job. |
| [2](#step-2) | Inspect a completed job with matching code, environment, and data versions; select its checkpoint from validation metrics and retain the job output. |
| [3](#step-3) | Encode corpus and queries with the selected checkpoint; populate its dedicated vector field in the same index, filter to the same chunk_size, and compare held-out relevance with the baseline fields. |


<a id="step-1"></a>

### Step 1: Configure a Sentence Transformers contrastive training script with reviewed positive pairs and hard negatives, then submit an Azure ML CPU command job.

**Learning Goal:** Configure a Sentence Transformers contrastive training script with reviewed positive pairs and hard negatives, then submit an Azure ML CPU command job.

**Demo Workspace:** VS Code, repository root; inspect `embedding_train` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c2/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `job_name`, `job_id`, `config`, `environment_id`, `studio_url`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** The pairwise contrastive loss raises each positive above a reviewed hard negative. The CPU job uses training-source groups only; validation selects the epoch.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Inspect a completed job with matching code, environment, and data versions; select its checkpoint from validation metrics and retain the job output.

**Learning Goal:** Inspect a completed job with matching code, environment, and data versions; select its checkpoint from validation metrics and retain the job output.

**Demo Workspace:** VS Code, repository root; inspect `embedding_train` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c2/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `status`, `result`, `output_path`, `result_sha256`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Open the printed Studio URL. Inspect actual Completed state, input/config hashes, selected epoch, validation nDCG and environment version. Retry the same step after completion; Queued or Running is HOLD.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Encode corpus and queries with the selected checkpoint; populate its dedicated vector field in the same index, filter to the same chunk_size, and compare held-out relevance with the baseline fields.

**Learning Goal:** Encode corpus and queries with the selected checkpoint; populate its dedicated vector field in the same index, filter to the same chunk_size, and compare held-out relevance with the baseline fields.

**Demo Workspace:** VS Code, repository root; inspect `embedding_train` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c2/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `baseline`, `tuned`, `checkpoint_job`, `query_and_document_encoder_identical`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** The selected checkpoint encodes both documents and questions into tuned_vector. Baselines use separate mini_vector and bge_vector fields in the same chunk-filtered index; all three have 384 dimensions.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

Domain phrases still retrieve weak evidence. Train a small CPU embedding checkpoint using reviewed pairs, then compare it without mixing vector versions. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module2/m2-c2/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m2-demo1-after` reference using `git diff m2-demo1-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Evaluate RAG variants with Azure services](../../module1/m1-c5/README.md) · [Course index](../../README.md) · [Next: Generate and version synthetic data with Foundry](../m2-c4/README.md)

## Final-outline execution contract

Train BAAI/bge-small-en-v1.5. Prefix training, validation and inference queries with `Represent this sentence for searching relevant passages: `; do not prefix corpus documents. Compare held-out nDCG@k against both baseline fields. A REJECT result retains evidence and does not adopt tuned vectors.

Offline regression tests are not Azure execution evidence.
