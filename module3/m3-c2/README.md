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
git switch m3-demo1-after
# Activate .venv (Windows Git Bash: source .venv/Scripts/activate)
source .venv/bin/activate
./module3/m3-c2/scripts/preflight_check.sh --offline
./module3/m3-c2/scripts/preflight_check.sh --live
./module3/m3-c2/scripts/lab-up.sh
```

The offline command needs only Python standard-library source. Live checks use your actual resources; provisioning/inference/jobs can incur charges. `lab-up` prints a unique `evidence/m3-demo1/<UTC-uuid>/` folder. Stay at the repo root.

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
