# Demo: Evaluate fine-tuned candidates in Azure ML

[Course index](../../README.md) · [Setup](../../setup/README.md) · [Run guide](../../docs/run-demos.md)

**Module 3 · Clip 2 · 5 minutes · CPU Azure lab**

## What you will learn

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2c** — Monitor and optimize fine-tuned model performance

You operate the support-assistant project and make a decision from real retained evidence. Source is supplied; offline tests are not successful Azure execution.

## Prerequisites and Starting State

Complete [the shared setup](../../setup/README.md), authenticate your permitted Azure identity, configure existing course-owned resources, and inspect the declared controls in [`configs/m3-demo1.json`](../../configs/m3-demo1.json). Preserve your own changes before switching branches.

Required retained runs: `m2-demo4`. Enter their actual run folders in `config.local.json` → `runs` before initializing this exercise. Their source/config/artifact hashes must match.

The dedicated baseline endpoint must already exist. If cleanup removed deployments, use `python -m ai300.setup restore-endpoint --from-run YOUR_RETAINED_RUN` with exact saved versions; do not replay a consumed final test.

## Open and Check

From the cloned repository root:

```bash
git switch m3-demo1-before
# Activate .venv (Windows Git Bash: source .venv/Scripts/activate)
source .venv/bin/activate
./module3/m3-c2/scripts/preflight_check.sh --offline
```

The offline command needs only Python standard-library source. Live checks use your actual resources; provisioning/inference/jobs can incur charges. `lab-up` prints a unique `evidence/m3-demo1/<UTC-uuid>/` folder. Stay at the repo root.

## Complete the Starter

The before branch intentionally leaves `ai300/demos.py:model_evaluate` unfinished. Open that function in VS Code and implement the numbered actions below using the supplied helpers and configuration. Shared infrastructure, earlier demo implementations and cleanup stay available. Live startup/steps stop with `STARTER` until the placeholder is replaced. An offline preflight checks prerequisites and reports the source state; it does not certify an unfinished solution.

Inspect the complete reference without switching or losing edits:

```bash
git fetch origin
git diff HEAD origin/m3-demo1-after -- ai300/demos.py
```

To run the supplied complete source instead of authoring the function, restore the reference file into this starter checkout, then run the full source checks:

```bash
git restore --source=origin/m3-demo1-after -- ai300/demos.py
python scripts/check_source.py
```

This restore replaces local edits to that file; commit your work first. [All before/after branches](../../docs/exercise-branches.md) explains safe switching and dependency evidence.

## Prepare Dependencies Under the Same Source

The evidence checks hash the complete engine, including `ai300/demos.py`. To reuse prior proof, restore the exact after source as shown above; the completed source matches main and every after reference. If you keep your own implementation, finish all source edits first, then rerun these prerequisite exercises in this order under that same unchanged working tree:

1. [m2-demo2](../../module2/m2-c4/README.md): complete its setup and numbered steps, retain its run folder, and set `config.local.json` → `runs.m2-demo2` to that folder.
2. [m2-demo3](../../module2/m2-c5/README.md): complete its setup and numbered steps, retain its run folder, and set `config.local.json` → `runs.m2-demo3` to that folder.
3. [m2-demo4](../../module2/m2-c6/README.md): complete its setup and numbered steps, retain its run folder, and set `config.local.json` → `runs.m2-demo4` to that folder.

Stay on this source tree while running prerequisite wrappers; do not switch to their starter branches or edit source between runs. After all accepted/completed dependency reports are available, initialize this demo. Configuration must also match each dependency’s consumed settings. A mismatch means rerun the affected proof, never rewrite its manifest. [Dependency evidence rules](../../docs/exercise-branches.md#preserve-dependency-evidence).

## Initialize the Live Run

Finish the source and prerequisite runs, then initialize from the repository root:

```bash
./module3/m3-c2/scripts/preflight_check.sh --live
./module3/m3-c2/scripts/lab-up.sh
```

## Source to Inspect

Open `ai300/demos.py:model_evaluate` in VS Code (file and named function). Related source: `ai300/demos.py`, `ai300/core.py`, `ai300/azure.py`, `configs/m3-demo1.json`, `jobs/evaluate.py`, `jobs/common.py`.

## Numbered Steps

<a id="step-1"></a>

### Step 1 — Submit an Azure ML evaluation job for the base model and both shortlisted adapters using the same domain and general-capability validation questions, retrieved context from the adopted search configuration, and generation settings

```bash
./module3/m3-c2/scripts/lab-step.sh 1
```

**Result:** the terminal prints the exact retained report path. Open `step-1-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `job_name`, `config`, `inputs`. These are contracts, not promised values.

**Decision and failure action:** Before step3, complete model-validation-review.jsonl for base and both adapters. The evaluation uses the adopted retrieval output, including the exact retained tuned checkpoint when selected. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-2"></a>

### Step 2 — Inspect the completed job in MLflow, comparing task correctness, answer support, and schema validity by query type and reading concrete failures

```bash
./module3/m3-c2/scripts/lab-step.sh 2
```

**Result:** the terminal prints the exact retained report path. Open `step-2-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `status`, `failure_rows`, `result`, `manual_review_path`. These are contracts, not promised values.

**Decision and failure action:** Before step3, complete model-validation-review.jsonl for base and both adapters. The evaluation uses the adopted retrieval output, including the exact retained tuned checkpoint when selected. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-3"></a>

### Step 3 — Select the candidate against the validation gates and record the job, dataset, configuration, and per-example results

```bash
./module3/m3-c2/scripts/lab-step.sh 3
```

**Result:** the terminal prints the exact retained report path. Open `step-3-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `decision`, `gate_checks`, `base`, `candidate`, `evaluation_job`, `validation_hash`, `manual_semantic_review`. These are contracts, not promised values.

**Decision and failure action:** Before step3, complete model-validation-review.jsonl for base and both adapters. The evaluation uses the adopted retrieval output, including the exact retained tuned checkpoint when selected. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.

## Interpretation and Next Action

Before step3, complete model-validation-review.jsonl for base and both adapters. The evaluation uses the adopted retrieval output, including the exact retained tuned checkpoint when selected.

A source check, completed job, passing validation gate, frozen final test and rollback proof are distinct states. If a gate rejects a candidate, retain the baseline and inspect individual failures. Canary step3 can stop promotion; still run step4 to exercise baseline restoration.

## Cleanup and Evidence Retention

```bash
./module3/m3-c2/scripts/lab-down.sh
```

Cleanup uses the retained resource/config snapshot. It only deletes candidate deployments created by the owning run; it leaves unrelated/name-collision deployments in place. Keep dependency artifacts, manual reviews and consumed-test ledgers. Do not clean up a live prerequisite endpoint until its dependent exercises are complete; retained endpoints/storage can remain billable. See [cleanup options](../../setup/README.md#troubleshooting-and-cleanup).

## What You Achieved

You followed the stated objective actions, retained actual response identities and made an evidence-based decision. Azure runtime is NOT RUN in this source revision; validate it in your own authorized lab.

[Previous exercise](../../module2/m2-c6/README.md) · [Next exercise](../../module3/m3-c3/README.md)
