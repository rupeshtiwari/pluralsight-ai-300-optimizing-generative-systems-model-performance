# Demo: Evaluate RAG variants with Azure services

[Previous: Run hybrid search and semantic reranking in Azure](../m1-c3/README.md) · [Course index](../../README.md) · [Next: Fine-tune domain embeddings in Azure ML](../../module2/m2-c2/README.md)

Module 1, clip 5 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

Your retrieval change looks better, but the generated answer may still miss the supported fact. Compare fixed variants and declare a bounded synthetic-session experiment.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1d** — Evaluate and improve RAG system performance by using relevance metrics and A/B testing frameworks

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

This exercise has no earlier demo dependency. Its own setup establishes the index or job from the supplied corpus and labels, using your configured Azure resources.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m1-demo3-after
source .venv/bin/activate
./module1/m1-c5/scripts/preflight_check.sh
./module1/m1-c5/scripts/lab-up.sh
```

Read [`configs/m1-demo3.json`](../../configs/m1-demo3.json) and [`ai300/azure.py`](../../ai300/azure.py), [`ai300/core.py`](../../ai300/core.py), [`data/queries.jsonl`](../../data/queries.jsonl). The shared implementation is [`rag_ab`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run.

`lab-up` prints your unique `evidence/m1-demo3/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

After step 1, fill `rag-variants-review.jsonl` in the run folder before step 2. During step 3 the runner retains fresh A/B observations and creates `rag-ab-review.jsonl`; complete it, then repeat step 3 to log the same observations. Every review binds the exact response hash and requires Boolean `correct`/`supported`, a reason and reviewer. The primary A/B metric is `manual_answer_support`; uncertainty is not estimated from repeated synthetic questions.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Run the Python experiment runner against two configurations of the same Azure AI Search index and the same gpt-5.6-luna deployment in Microsoft Foundry, holding the prompt and generation settings fixed. |
| [2](#step-2) | Compare Recall@k, nDCG@k, manually reviewed answer support, and latency using real retrieval and generated responses; inspect a response against its source and check for regressions. |
| [3](#step-3) | Assign synthetic sessions consistently to A or B, retain exposure and outcome logs in Azure ML with MLflow, and analyze the declared primary metric and stop rule. |


<a id="step-1"></a>

### Step 1: Run the Python experiment runner against two configurations of the same Azure AI Search index and the same gpt-5.6-luna deployment in Microsoft Foundry, holding the prompt and generation settings fixed.

**Learning Goal:** Run the Python experiment runner against two configurations of the same Azure AI Search index and the same gpt-5.6-luna deployment in Microsoft Foundry, holding the prompt and generation settings fixed.

**Demo Workspace:** VS Code, repository root; inspect `rag_ab` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module1/m1-c5/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `fixed_generation`, `rows`, `variants`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Both variants use the same index, deployment, prompt and generation settings. Only the declared retrieval configuration changes. Keep raw responses as well as aggregate metrics.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Compare Recall@k, nDCG@k, manually reviewed answer support, and latency using real retrieval and generated responses; inspect a response against its source and check for regressions.

**Learning Goal:** Compare Recall@k, nDCG@k, manually reviewed answer support, and latency using real retrieval and generated responses; inspect a response against its source and check for regressions.

**Demo Workspace:** VS Code, repository root; inspect `rag_ab` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module1/m1-c5/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `comparison`, `regressions`, `regression_observed`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** The automatic support proxy checks labeled facts and citations. Read actual failures; do not invent a regression if both variants happen to tie.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Assign synthetic sessions consistently to A or B, retain exposure and outcome logs in Azure ML with MLflow, and analyze the declared primary metric and stop rule.

**Learning Goal:** Assign synthetic sessions consistently to A or B, retain exposure and outcome logs in Azure ML with MLflow, and analyze the declared primary metric and stop rule.

**Demo Workspace:** VS Code, repository root; inspect `rag_ab` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module1/m1-c5/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `primary_metric`, `stop_rule`, `arm_summary`, `difference_B_minus_A`, `uncertainty`, `mlflow_run_id`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Session hashing stabilizes assignment. Exposures and outcomes come from fresh assigned Azure requests and are logged to Azure ML. Repeated synthetic questions are correlated; uncertainty is explicitly unestimated and the decision remains collect more evidence.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

Your retrieval change looks better, but the generated answer may still miss the supported fact. Compare fixed variants and declare a bounded synthetic-session experiment. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module1/m1-c5/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m1-demo3-after` reference using `git diff m1-demo3-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Run hybrid search and semantic reranking in Azure](../m1-c3/README.md) · [Course index](../../README.md) · [Next: Fine-tune domain embeddings in Azure ML](../../module2/m2-c2/README.md)
