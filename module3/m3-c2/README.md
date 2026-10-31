# Demo: Evaluate fine-tuned candidates in Azure ML

[Previous: Tune LoRA rank and select a checkpoint in Azure ML](../../module2/m2-c6/README.md) · [Course index](../../README.md) · [Next: Deploy a versioned model to Azure ML](../m3-c3/README.md)

Module 3, clip 2 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

The chosen adapter may improve domain responses while harming simple general questions. Evaluate both kinds with fixed generation before registration.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2c** — Monitor and optimize fine-tuned model performance

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

Retain completed prerequisite runs: `m2-demo4`. Put their actual run-folder paths in `config.local.json` → `runs` before starting. Follow each linked prerequisite page from the course index; missing completed artifacts block this exercise.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m3-demo1-after
source .venv/bin/activate
./module3/m3-c2/scripts/preflight_check.sh
./module3/m3-c2/scripts/lab-up.sh
```

Read [`configs/m3-demo1.json`](../../configs/m3-demo1.json) and [`jobs/evaluate.py`](../../jobs/evaluate.py), [`jobs/common.py`](../../jobs/common.py). The shared implementation is [`model_evaluate`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run.

`lab-up` prints your unique `evidence/m3-demo1/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

After step 2, open `model-validation-review.jsonl` in the run folder. Check each base and adapter response against the exact supplied context and every policy condition (or the general-question reference). Set Boolean `correct`/`supported`, a reason and reviewer. Step 3 requires these hash-bound judgments and JSON-schema gates; keyword presence and exact-reference proxy scores cannot approve or reject semantic quality.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Submit an Azure ML evaluation job for the base model and selected adapters using the same domain and general-capability validation questions and generation settings. |
| [2](#step-2) | Inspect the completed job in MLflow, comparing task correctness, answer support, and schema validity by query type and reading concrete failures. |
| [3](#step-3) | Select the candidate against the validation gates and retain the job, dataset, configuration, and per-example evidence. |


<a id="step-1"></a>

### Step 1: Submit an Azure ML evaluation job for the base model and selected adapters using the same domain and general-capability validation questions and generation settings.

**Learning Goal:** Submit an Azure ML evaluation job for the base model and selected adapters using the same domain and general-capability validation questions and generation settings.

**Demo Workspace:** VS Code, repository root; inspect `model_evaluate` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c2/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `job_name`, `config`, `inputs`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** The base and adapter share the same domain/general validation questions, generation budget and prompt. The final-test set does not choose the candidate.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Inspect the completed job in MLflow, comparing task correctness, answer support, and schema validity by query type and reading concrete failures.

**Learning Goal:** Inspect the completed job in MLflow, comparing task correctness, answer support, and schema validity by query type and reading concrete failures.

**Demo Workspace:** VS Code, repository root; inspect `model_evaluate` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c2/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `status`, `failure_rows`, `result`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Inspect the actual per-example outputs alongside MLflow correctness, labeled support and JSON-schema validity, separated by exact identifiers, paraphrases and general questions.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Select the candidate against the validation gates and retain the job, dataset, configuration, and per-example evidence.

**Learning Goal:** Select the candidate against the validation gates and retain the job, dataset, configuration, and per-example evidence.

**Demo Workspace:** VS Code, repository root; inspect `model_evaluate` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c2/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `decision`, `gate_checks`, `base`, `candidate`, `evaluation_job`, `validation_hash`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** A PASS requires the declared quality floors and no query-type regression against the base. REJECT blocks deployment; a completed evaluation job alone is not a passing model.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

The chosen adapter may improve domain responses while harming simple general questions. Evaluate both kinds with fixed generation before registration. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module3/m3-c2/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m3-demo1-after` reference using `git diff m3-demo1-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Tune LoRA rank and select a checkpoint in Azure ML](../../module2/m2-c6/README.md) · [Course index](../../README.md) · [Next: Deploy a versioned model to Azure ML](../m3-c3/README.md)

## Final-outline execution contract

Record the measured, manually adopted retrieval settings as `adopted_retrieval` in config.local.json before starting this run (for example the actual selected mode, size, depth, field and weight). Use a measured baseline vector field; tuned-field adoption currently fails closed pending checkpoint restoration. The runner prepares that index layout, captures actual retrieved contexts and their hash once, then evaluates base plus both shortlisted adapters with exactly that context. Relevance labels remain scoring labels, never substitute context.

Offline regression tests are not Azure execution evidence.
