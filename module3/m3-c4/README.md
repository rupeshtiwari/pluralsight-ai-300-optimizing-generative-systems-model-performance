# Demo: Optimize and test the Azure model endpoint

[Previous: Deploy a versioned model to Azure ML](../m3-c3/README.md) · [Course index](../../README.md) · [Next: Monitor Azure traffic and verify rollback](../m3-c5/README.md)

Module 3, clip 4 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

The adapter is deployed, but output length changes CPU latency and answer completeness. Select on validation, freeze settings, and open the final test once.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2c** — Monitor and optimize fine-tuned model performance
- **EO2d** — Manage a fine-tuned model from development through production deployment

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

Retain completed prerequisite runs: `m3-demo2`. Put their actual run-folder paths in `config.local.json` → `runs` before starting. Follow each linked prerequisite page from the course index; missing completed artifacts block this exercise.

Use a dedicated baseline endpoint created by `python -m ai300.setup create-baseline`. For a continuation after cleanup, restore the exact saved baseline/candidate versions with `python -m ai300.setup restore-endpoint --from-run "YOUR_RETAINED_DEPLOYMENT_OR_FINAL_TEST_RUN"`; keep the original dependency run. Keep baseline at 100% before the release exercise.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m3-demo3-after
source .venv/bin/activate
./module3/m3-c4/scripts/preflight_check.sh
./module3/m3-c4/scripts/lab-up.sh
```

Read [`configs/m3-demo3.json`](../../configs/m3-demo3.json) and [`serving/score.py`](../../serving/score.py), [`ai300/core.py`](../../ai300/core.py). The shared implementation is [`endpoint_test`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run.

`lab-up` prints your unique `evidence/m3-demo3/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

Step 1 first captures each validation output-length workload in `validation-benchmarks.json` and creates `validation-limits-review.jsonl`. Review each exact response/context, fill Boolean `correct`/`supported`, reason and reviewer, then rerun step 1. It reuses the same captured observations and selects only a setting passing human semantic and schema floors by query type.

After step 2, complete `final-test-review.jsonl` against the exact supplied context and the now-opened final-test references. Set Boolean `correct`/`supported`, a reason and reviewer. Step 3 requires the retained semantic review and JSON-schema/latency gates; the exact-reference proxy is diagnostic only. Do not regenerate test responses or edit their hashes.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Benchmark the candidate deployment directly with a fixed validation workload; compare output-length limits using latency, output tokens, and answer quality. |
| [2](#step-2) | Freeze the selected model, environment, and request settings, then run the untouched domain and general-capability test set against that deployment. |
| [3](#step-3) | Retain the final test report and release configuration with the model version; reject a failed gate and require a new untouched test set after further tuning. |


<a id="step-1"></a>

### Step 1: Benchmark the candidate deployment directly with a fixed validation workload; compare output-length limits using latency, output tokens, and answer quality.

**Learning Goal:** Benchmark the candidate deployment directly with a fixed validation workload; compare output-length limits using latency, output tokens, and answer quality.

**Demo Workspace:** VS Code, repository root; inspect `endpoint_test` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c4/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `benchmarks`, `selected_max_new_tokens`, `selection_rule`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Compare 64 and 96 new-token limits on the same validation workload. Only settings passing all quality floors can compete on p95 client latency; output-token counts explain the tradeoff.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Freeze the selected model, environment, and request settings, then run the untouched domain and general-capability test set against that deployment.

**Learning Goal:** Freeze the selected model, environment, and request settings, then run the untouched domain and general-capability test set against that deployment.

**Demo Workspace:** VS Code, repository root; inspect `endpoint_test` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c4/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `frozen_release`, `frozen_release_sha256`, `final_test`, `test_ledger`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Freeze model, environment, scorer hash, generation settings and final-test hash before the first test call. Opening the test consumes it even if a later request fails.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Retain the final test report and release configuration with the model version; reject a failed gate and require a new untouched test set after further tuning.

**Learning Goal:** Retain the final test report and release configuration with the model version; reject a failed gate and require a new untouched test set after further tuning.

**Demo Workspace:** VS Code, repository root; inspect `endpoint_test` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c4/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `release_decision`, `gate_checks`, `frozen_release`, `mlflow_run_id`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Retain PASS or REJECT with every per-example result. A failed test means keep baseline. Further tuning requires a new untouched source-group test set, not a reset ledger.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

The adapter is deployed, but output length changes CPU latency and answer completeness. Select on validation, freeze settings, and open the final test once. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module3/m3-c4/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m3-demo3-after` reference using `git diff m3-demo3-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Deploy a versioned model to Azure ML](../m3-c3/README.md) · [Course index](../../README.md) · [Next: Monitor Azure traffic and verify rollback](../m3-c5/README.md)
