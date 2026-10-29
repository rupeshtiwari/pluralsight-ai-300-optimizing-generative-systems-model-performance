# Demo: Train a LoRA adapter in Azure ML

[Previous: Generate and version synthetic data with Foundry](../m2-c4/README.md) · [Course index](../../README.md) · [Next: Tune LoRA rank and select a checkpoint in Azure ML](../m2-c6/README.md)

Module 2, clip 5 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

Lower training loss is useful only if the model follows the support task on unseen source groups. Fit a small Qwen adapter and compare actual responses.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2a** — Design and implement advanced fine-tuning methods
- **EO2c** — Monitor and optimize fine-tuned model performance

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

Retain completed prerequisite runs: `m2-demo2`. Put their actual run-folder paths in `config.local.json` → `runs` before starting. Follow each linked prerequisite page from the course index; missing completed artifacts block this exercise.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m2-demo3-after
source .venv/bin/activate
./module2/m2-c5/scripts/preflight_check.sh
./module2/m2-c5/scripts/lab-up.sh
```

Read [`configs/m2-demo3.json`](../../configs/m2-demo3.json) and [`jobs/train_lora.py`](../../jobs/train_lora.py), [`jobs/common.py`](../../jobs/common.py), [`environments/train-conda.yml`](../../environments/train-conda.yml). The shared implementation is [`lora_train`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run.

`lab-up` prints your unique `evidence/m2-demo3/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Configure Qwen3-0.6B supervised training with Transformers and PEFT, choosing LoRA rank, target layers, learning rate, batch size, and response-only loss. |
| [2](#step-2) | Submit the CPU command job and inspect a completed run with matching inputs; track training and validation loss in Azure ML through MLflow. |
| [3](#step-3) | Diagnose divergence between training and validation loss, then inspect base and adapted validation responses for memorization and task errors before further tuning. |


<a id="step-1"></a>

### Step 1: Configure Qwen3-0.6B supervised training with Transformers and PEFT, choosing LoRA rank, target layers, learning rate, batch size, and response-only loss.

**Learning Goal:** Configure Qwen3-0.6B supervised training with Transformers and PEFT, choosing LoRA rank, target layers, learning rate, batch size, and response-only loss.

**Demo Workspace:** VS Code, repository root; inspect `lora_train` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c5/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `configuration`, `data_assets`, `response_only_loss`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Read rank, q_proj/v_proj targets, learning rate, batch size 1 and two-epoch CPU budget. Prompt labels are -100, so only response tokens and EOS contribute to loss.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Submit the CPU command job and inspect a completed run with matching inputs; track training and validation loss in Azure ML through MLflow.

**Learning Goal:** Submit the CPU command job and inspect a completed run with matching inputs; track training and validation loss in Azure ML through MLflow.

**Demo Workspace:** VS Code, repository root; inspect `lora_train` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c5/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `job_name`, `status`, `output_path`, `result`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** This step submits once, retains its job identity, and inspects it. A pending job returns HOLD; rerun the same command after Azure ML reports Completed. Do not submit another run just to replace a failed observation.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Diagnose divergence between training and validation loss, then inspect base and adapted validation responses for memorization and task errors before further tuning.

**Learning Goal:** Diagnose divergence between training and validation loss, then inspect base and adapted validation responses for memorization and task errors before further tuning.

**Demo Workspace:** VS Code, repository root; inspect `lora_train` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c5/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `history`, `divergence_observed`, `base`, `adapted`, `selected_epoch`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Compare selected-checkpoint output with the base on identical validation questions. Falling training loss plus rising validation loss signals divergence; if absent, say so and inspect task errors instead.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

Lower training loss is useful only if the model follows the support task on unseen source groups. Fit a small Qwen adapter and compare actual responses. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module2/m2-c5/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m2-demo3-after` reference using `git diff m2-demo3-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Generate and version synthetic data with Foundry](../m2-c4/README.md) · [Course index](../../README.md) · [Next: Tune LoRA rank and select a checkpoint in Azure ML](../m2-c6/README.md)
