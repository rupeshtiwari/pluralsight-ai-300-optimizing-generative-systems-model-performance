# Demo: Deploy a versioned model to Azure ML

[Previous: Evaluate fine-tuned candidates in Azure ML](../m3-c2/README.md) · [Course index](../../README.md) · [Next: Optimize and test the Azure model endpoint](../m3-c4/README.md)

Module 3, clip 3 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

You need a deployable model identity that can be traced back to accepted data and validation, while the existing baseline continues serving.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2d** — Manage a fine-tuned model from development through production deployment

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

Retain completed prerequisite runs: `m3-demo1`. Put their actual run-folder paths in `config.local.json` → `runs` before starting. Follow each linked prerequisite page from the course index; missing completed artifacts block this exercise.

Use a dedicated baseline endpoint created by `python -m ai300.setup create-baseline`. For a continuation after cleanup, restore the exact saved baseline/candidate versions with `python -m ai300.setup restore-endpoint --from-run "YOUR_RETAINED_DEPLOYMENT_OR_FINAL_TEST_RUN"`; keep the original dependency run. Keep baseline at 100% before the release exercise.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m3-demo2-after
source .venv/bin/activate
./module3/m3-c3/scripts/preflight_check.sh
./module3/m3-c3/scripts/lab-up.sh
```

Read [`configs/m3-demo2.json`](../../configs/m3-demo2.json) and [`serving/score.py`](../../serving/score.py), [`environments/serve-conda.yml`](../../environments/serve-conda.yml). The shared implementation is [`model_deploy`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run. The approved chunk-size list, semantic candidate depth 50, required manual review and zero-traffic deployment are checked contract constants where applicable; edits that violate them return HOLD. Chunk overlap is consumed by the tokenizer loop, while the named sweep settings are visible in the demo function.

`lab-up` prints your unique `evidence/m3-demo2/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Register a custom model asset containing the base-model revision, adapter, and tokenizer, linked to training data and validation evidence. |
| [2](#step-2) | Deploy the candidate with versioned scoring code and an Azure ML CPU inference environment to an existing managed online endpoint at zero traffic. |
| [3](#step-3) | Inspect the completed deployment and invoke it directly; verify the model identity and smoke-test responses while the baseline deployment continues serving. |


<a id="step-1"></a>

### Step 1: Register a custom model asset containing the base-model revision, adapter, and tokenizer, linked to training data and validation evidence.

**Learning Goal:** Register a custom model asset containing the base-model revision, adapter, and tokenizer, linked to training data and validation evidence.

**Demo Workspace:** VS Code, repository root; inspect `model_deploy` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c3/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `model_id`, `model_identity`, `bundle_hashes`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Registration packages exact base weights, adapter, tokenizer and lineage. It requires a genuine passing validation report. The model revision must match the selected checkpoint.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Deploy the candidate with versioned scoring code and an Azure ML CPU inference environment to an existing managed online endpoint at zero traffic.

**Learning Goal:** Deploy the candidate with versioned scoring code and an Azure ML CPU inference environment to an existing managed online endpoint at zero traffic.

**Demo Workspace:** VS Code, repository root; inspect `model_deploy` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c3/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `candidate_deployment`, `environment`, `scoring_sha256`, `traffic_before`, `status`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** The candidate is created without changing endpoint traffic. The scoring code runs FP32 on CPU and returns its model and deployment identity with each response.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Inspect the completed deployment and invoke it directly; verify the model identity and smoke-test responses while the baseline deployment continues serving.

**Learning Goal:** Inspect the completed deployment and invoke it directly; verify the model identity and smoke-test responses while the baseline deployment continues serving.

**Demo Workspace:** VS Code, repository root; inspect `model_deploy` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c3/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `provisioning_state`, `traffic`, `model_identity`, `smoke_response`, `baseline_response`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Wait for Succeeded, invoke the candidate directly, then invoke the routed endpoint. Candidate identity must match registration and routed requests must still reach baseline at 100%.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

You need a deployable model identity that can be traced back to accepted data and validation, while the existing baseline continues serving. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module3/m3-c3/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m3-demo2-after` reference using `git diff m3-demo2-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Evaluate fine-tuned candidates in Azure ML](../m3-c2/README.md) · [Course index](../../README.md) · [Next: Optimize and test the Azure model endpoint](../m3-c4/README.md)
