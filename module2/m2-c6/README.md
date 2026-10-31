# Demo: Tune LoRA rank and select a checkpoint in Azure ML

[Previous: Train a LoRA adapter in Azure ML](../m2-c5/README.md) · [Course index](../../README.md) · [Next: Evaluate fine-tuned candidates in Azure ML](../../module3/m3-c2/README.md)

Module 2, clip 6 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

A larger adapter may cost more without improving useful answers. Compare a second rank/learning-rate configuration while holding other factors fixed.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2a** — Design and implement advanced fine-tuning methods
- **EO2c** — Monitor and optimize fine-tuned model performance

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

Retain completed prerequisite runs: `m2-demo3`, `m2-demo2`. Put their actual run-folder paths in `config.local.json` → `runs` before starting. Follow each linked prerequisite page from the course index; missing completed artifacts block this exercise.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m2-demo4-after
source .venv/bin/activate
./module2/m2-c6/scripts/preflight_check.sh
./module2/m2-c6/scripts/lab-up.sh
```

Read [`configs/m2-demo4.json`](../../configs/m2-demo4.json) and [`jobs/train_lora.py`](../../jobs/train_lora.py), [`ai300/ml.py`](../../ai300/ml.py). The shared implementation is [`lora_select`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run.

`lab-up` prints your unique `evidence/m2-demo4/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Configure a second CPU command job with a different LoRA rank and learning rate; keep the base model, data splits, seed, target layers, and training budget fixed. |
| [2](#step-2) | Compare both genuine completed runs in MLflow using validation loss, elapsed time, and task outputs; interpret the combined configuration change rather than attributing the result to rank alone. |
| [3](#step-3) | Select a checkpoint using validation quality and CPU cost, then save its adapter with the exact base-model revision, tokenizer, data, and environment versions. |


<a id="step-1"></a>

### Step 1: Configure a second CPU command job with a different LoRA rank and learning rate; keep the base model, data splits, seed, target layers, and training budget fixed.

**Learning Goal:** Configure a second CPU command job with a different LoRA rank and learning rate; keep the base model, data splits, seed, target layers, and training budget fixed.

**Demo Workspace:** VS Code, repository root; inspect `lora_select` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c6/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `job_name`, `config`, `inputs`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** The second job changes rank 4 to 8 and learning rate 0.0002 to 0.0001 together. Both changes are declared; this is not a rank-only causal experiment.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Compare both genuine completed runs in MLflow using validation loss, elapsed time, and task outputs; interpret the combined configuration change rather than attributing the result to rank alone.

**Learning Goal:** Compare both genuine completed runs in MLflow using validation loss, elapsed time, and task outputs; interpret the combined configuration change rather than attributing the result to rank alone.

**Demo Workspace:** VS Code, repository root; inspect `lora_select` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c6/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `first`, `second`, `controlled_factors`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Completed runs must match source, data, base revision, tokenizer, seed, target modules and budget. Compare validation loss, CPU elapsed time and the saved task-output files.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Select a checkpoint using validation quality and CPU cost, then save its adapter with the exact base-model revision, tokenizer, data, and environment versions.

**Learning Goal:** Select a checkpoint using validation quality and CPU cost, then save its adapter with the exact base-model revision, tokenizer, data, and environment versions.

**Demo Workspace:** VS Code, repository root; inspect `lora_select` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c6/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `selected_job`, `candidate_versions`, `selection_rule`, `result`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Select by validation loss with elapsed time as a tie-breaker, then retain the adapter, tokenizer and exact lineage. Selection is provisional until the next model-quality gates pass.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

A larger adapter may cost more without improving useful answers. Compare a second rank/learning-rate configuration while holding other factors fixed. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module2/m2-c6/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m2-demo4-after` reference using `git diff m2-demo4-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Train a LoRA adapter in Azure ML](../m2-c5/README.md) · [Course index](../../README.md) · [Next: Evaluate fine-tuned candidates in Azure ML](../../module3/m3-c2/README.md)

## Final-outline execution contract

Change rank only. Learning rate, batch size, seed, data, target modules, versions and budget stay fixed; alpha is derived as 2 × rank. Retain `shortlisted_checkpoints` (both selected adapters and lineage) for evaluation.

Offline regression tests are not Azure execution evidence.
