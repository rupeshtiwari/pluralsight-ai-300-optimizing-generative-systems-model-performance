# Demo: Tune chunks and similarity cutoffs in Azure AI Search

[Previous: course index](../../README.md) · [Course index](../../README.md) · [Next: Run hybrid search and semantic reranking in Azure](../m1-c3/README.md)

Module 1, clip 2 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

A support answer cites the right policy but omits its condition. Compare token windows and retained vector candidates before changing generation.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1a** — Optimize retrieval performance by tuning similarity thresholds, chunk sizes, and retrieval strategies

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

This exercise has no earlier demo dependency. Its own setup establishes the index or job from the supplied corpus and labels, using your configured Azure resources.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m1-demo1-after
source .venv/bin/activate
./module1/m1-c2/scripts/preflight_check.sh
./module1/m1-c2/scripts/lab-up.sh
```

Read [`configs/m1-demo1.json`](../../configs/m1-demo1.json) and [`ai300/azure.py`](../../ai300/azure.py), [`data/corpus.jsonl`](../../data/corpus.jsonl), [`data/queries.jsonl`](../../data/queries.jsonl). The shared implementation is [`retrieval_chunks`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run. The approved chunk-size list, semantic candidate depth 50, required manual review and zero-traffic deployment are checked contract constants where applicable; edits that violate them return HOLD. Chunk overlap is consumed by the tokenizer loop, while the named sweep settings are visible in the demo function.

`lab-up` prints your unique `evidence/m1-demo1/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Query one Azure AI Search Free-tier index with a chunk_size pre-filter to select 64-, 128-, or 192-token chunks of the same corpus, encoded with all-MiniLM-L6-v2. |
| [2](#step-2) | Vary vector candidate depth and apply a cosine cutoff in the Python client after converting a pure single-vector search score; inspect retained and rejected results. |
| [3](#step-3) | Compare Recall@k, boundary failures, and latency while changing one control at a time; retain the configuration that supplies useful evidence. |


<a id="step-1"></a>

### Step 1: Query one Azure AI Search Free-tier index with a chunk_size pre-filter to select 64-, 128-, or 192-token chunks of the same corpus, encoded with all-MiniLM-L6-v2.

**Learning Goal:** Query one Azure AI Search Free-tier index with a chunk_size pre-filter to select 64-, 128-, or 192-token chunks of the same corpus, encoded with all-MiniLM-L6-v2.

**Demo Workspace:** VS Code, repository root; inspect `retrieval_chunks` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module1/m1-c2/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `indexed_chunks`, `rows`, `variants`, `chunk_size`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Compare the same policy sources across 64, 128 and 192 MiniLM tokenizer tokens, with fixed 16-token overlap. A higher source recall can still hide a boundary failure.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Vary vector candidate depth and apply a cosine cutoff in the Python client after converting a pure single-vector search score; inspect retained and rejected results.

**Learning Goal:** Vary vector candidate depth and apply a cosine cutoff in the Python client after converting a pure single-vector search score; inspect retained and rejected results.

**Demo Workspace:** VS Code, repository root; inspect `retrieval_chunks` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module1/m1-c2/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `retained`, `rejected`, `cosine_similarity`, `settings`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Depth changes the server candidate pool; the client cutoff only discards returned pure-vector candidates. Do not transfer this cutoff to RRF or semantic scores.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Compare Recall@k, boundary failures, and latency while changing one control at a time; retain the configuration that supplies useful evidence.

**Learning Goal:** Compare Recall@k, boundary failures, and latency while changing one control at a time; retain the configuration that supplies useful evidence.

**Demo Workspace:** VS Code, repository root; inspect `retrieval_chunks` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module1/m1-c2/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `comparison`, `selected_variant`, `selection_rule`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Read the boundary failures next to recall and latency. The selected setting is a small validation-set decision, not a proven global optimum.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

A support answer cites the right policy but omits its condition. Compare token windows and retained vector candidates before changing generation. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module1/m1-c2/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m1-demo1-after` reference using `git diff m1-demo1-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: course index](../../README.md) · [Course index](../../README.md) · [Next: Run hybrid search and semantic reranking in Azure](../m1-c3/README.md)
