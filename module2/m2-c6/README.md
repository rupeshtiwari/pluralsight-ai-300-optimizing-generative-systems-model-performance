# Demo: Tune LoRA rank and select checkpoints in Azure ML

[Course index](../../README.md) · [Setup](../../setup/README.md) · [Run guide](../../docs/run-demos.md)

**Module 2 · Clip 6 · 5 minutes · CPU Azure lab**

## What you will learn

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2a** — Design and implement advanced fine-tuning methods
- **EO2c** — Monitor and optimize fine-tuned model performance

You operate the support-assistant project and make a decision from real retained evidence. Source is supplied; offline tests are not successful Azure execution.

## Prerequisites and Starting State

Complete [the shared setup](../../setup/README.md), authenticate your permitted Azure identity, configure existing course-owned resources, and inspect the declared controls in [`configs/m2-demo4.json`](../../configs/m2-demo4.json). Preserve your own changes before switching branches.

Required retained runs: `m2-demo3`, `m2-demo2`. Enter their actual run folders in `config.local.json` → `runs` before initializing this exercise. Their source/config/artifact hashes must match.

## Open and Check

From the cloned repository root:

```bash
git switch m2-demo4-before
# Activate .venv (Windows Git Bash: source .venv/Scripts/activate)
source .venv/bin/activate
./module2/m2-c6/scripts/preflight_check.sh --offline
```

The offline command needs only Python standard-library source. Live checks use your actual resources; provisioning/inference/jobs can incur charges. `lab-up` prints a unique `evidence/m2-demo4/<UTC-uuid>/` folder. Stay at the repo root.

## Complete the Starter

The before branch intentionally leaves `ai300/demos.py:lora_select` unfinished. Open that function in VS Code and implement the numbered actions below using the supplied helpers and configuration. Shared infrastructure, earlier demo implementations and cleanup stay available. Live startup/steps stop with `STARTER` until the placeholder is replaced. An offline preflight checks prerequisites and reports the source state; it does not certify an unfinished solution.

Inspect the complete reference without switching or losing edits:

```bash
git fetch origin
git diff HEAD origin/m2-demo4-after -- ai300/demos.py
```

To run the supplied complete source instead of authoring the function, restore the reference file into this starter checkout, then run the full source checks:

```bash
git restore --source=origin/m2-demo4-after -- ai300/demos.py
python scripts/check_source.py
```

This restore replaces local edits to that file; commit your work first. [All before/after branches](../../docs/exercise-branches.md) explains safe switching and dependency evidence.

## Prepare Dependencies Under the Same Source

The evidence checks hash the complete engine, including `ai300/demos.py`. To reuse prior proof, restore the exact after source as shown above; the completed source matches main and every after reference. If you keep your own implementation, finish all source edits first, then rerun these prerequisite exercises in this order under that same unchanged working tree:

1. [m2-demo2](../../module2/m2-c4/README.md): complete its setup and numbered steps, retain its run folder, and set `config.local.json` → `runs.m2-demo2` to that folder.
2. [m2-demo3](../../module2/m2-c5/README.md): complete its setup and numbered steps, retain its run folder, and set `config.local.json` → `runs.m2-demo3` to that folder.

Stay on this source tree while running prerequisite wrappers; do not switch to their starter branches or edit source between runs. After all accepted/completed dependency reports are available, initialize this demo. Configuration must also match each dependency’s consumed settings. A mismatch means rerun the affected proof, never rewrite its manifest. [Dependency evidence rules](../../docs/exercise-branches.md#preserve-dependency-evidence).

## Initialize the Live Run

Finish the source and prerequisite runs, then initialize from the repository root:

```bash
./module2/m2-c6/scripts/preflight_check.sh --live
./module2/m2-c6/scripts/lab-up.sh
```

## Source to Inspect

Open `ai300/demos.py:lora_select` in VS Code (file and named function). Related source: `ai300/demos.py`, `ai300/core.py`, `ai300/azure.py`, `configs/m2-demo4.json`, `jobs/train_lora.py`, `ai300/ml.py`.

## Jump to a Step

| Step | Action |
|---|---|
| [Step 1](#step-1) | Configure a second CPU command job that changes only the LoRA rank, with the alpha-to-rank ratio, base model, data splits, seed, learning rate, target modules, and training budget held fixed |
| [Step 2](#step-2) | Compare both completed runs in MLflow using validation loss, elapsed time, and task outputs, and judge whether the higher rank earns its extra CPU cost |
| [Step 3](#step-3) | Shortlist the best checkpoint from each run by validation loss, then save each adapter with the exact base-model revision, tokenizer, data, and environment versions |

## Numbered Steps

<a id="step-1"></a>

### Step 1 — Configure a second CPU command job that changes only the LoRA rank, with the alpha-to-rank ratio, base model, data splits, seed, learning rate, target modules, and training budget held fixed

```bash
./module2/m2-c6/scripts/lab-step.sh 1
```

**Result:** the terminal prints the exact retained report path. Open `step-1-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `job_name`, `config`, `inputs`. These are contracts, not promised values.

**Decision and failure action:** Change only rank4 to rank8. The learning rate, seed, data, training budget and targets stay fixed; alpha/rank stays2. Both best-validation adapters are shortlisted for module3. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-2"></a>

### Step 2 — Compare both completed runs in MLflow using validation loss, elapsed time, and task outputs, and judge whether the higher rank earns its extra CPU cost

```bash
./module2/m2-c6/scripts/lab-step.sh 2
```

**Result:** the terminal prints the exact retained report path. Open `step-2-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `first`, `second`, `controlled_factors`. These are contracts, not promised values.

**Decision and failure action:** Change only rank4 to rank8. The learning rate, seed, data, training budget and targets stay fixed; alpha/rank stays2. Both best-validation adapters are shortlisted for module3. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-3"></a>

### Step 3 — Shortlist the best checkpoint from each run by validation loss, then save each adapter with the exact base-model revision, tokenizer, data, and environment versions

```bash
./module2/m2-c6/scripts/lab-step.sh 3
```

**Result:** the terminal prints the exact retained report path. Open `step-3-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `selected_job`, `candidate_versions`, `selection_rule`, `result`. These are contracts, not promised values.

**Decision and failure action:** Change only rank4 to rank8. The learning rate, seed, data, training budget and targets stay fixed; alpha/rank stays2. Both best-validation adapters are shortlisted for module3. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.

## Interpretation and Next Action

Change only rank4 to rank8. The learning rate, seed, data, training budget and targets stay fixed; alpha/rank stays2. Both best-validation adapters are shortlisted for module3.

A source check, completed job, passing validation gate, frozen final test and rollback proof are distinct states. If a gate rejects a candidate, retain the baseline and inspect individual failures. Canary step3 can stop promotion; still run step4 to exercise baseline restoration.

## Cleanup and Evidence Retention

```bash
./module2/m2-c6/scripts/lab-down.sh
```

Cleanup uses the retained resource/config snapshot. It only deletes candidate deployments created by the owning run; it leaves unrelated/name-collision deployments in place. Keep dependency artifacts, manual reviews and consumed-test ledgers. Do not clean up a live prerequisite endpoint until its dependent exercises are complete; retained endpoints/storage can remain billable. See [cleanup options](../../setup/README.md#troubleshooting-and-cleanup).

## What You Achieved

You followed the stated objective actions, retained actual response identities and made an evidence-based decision. Azure runtime is NOT RUN in this source revision; validate it in your own authorized lab.

[Previous exercise](../../module2/m2-c5/README.md) · [Next exercise](../../module3/m3-c2/README.md)
