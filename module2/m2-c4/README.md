# Demo: Generate and version synthetic data with Foundry

[Course index](../../README.md) · [Setup](../../setup/README.md) · [Run guide](../../docs/run-demos.md)

**Module 2 · Clip 4 · 4 minutes · CPU Azure lab**

## What you will learn

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2b** — Create and manage synthetic data for fine-tuning

You operate the support-assistant project and make a decision from real retained evidence. Source is supplied; offline tests are not successful Azure execution.

## Prerequisites and Starting State

Complete [the shared setup](../../setup/README.md), authenticate your permitted Azure identity, configure existing course-owned resources, and inspect the declared controls in [`configs/m2-demo2.json`](../../configs/m2-demo2.json). Preserve your own changes before switching branches.

## Open and Check

From the cloned repository root:

```bash
git switch m2-demo2-after
# Activate .venv (Windows Git Bash: source .venv/Scripts/activate)
source .venv/bin/activate
./module2/m2-c4/scripts/preflight_check.sh --offline
./module2/m2-c4/scripts/preflight_check.sh --live
./module2/m2-c4/scripts/lab-up.sh
```

The offline command needs only Python standard-library source. Live checks use your actual resources; provisioning/inference/jobs can incur charges. `lab-up` prints a unique `evidence/m2-demo2/<UTC-uuid>/` folder. Stay at the repo root.

## Source to Inspect

Open `ai300/demos.py:synthetic_data` in VS Code (file and named function). Related source: `ai300/demos.py`, `ai300/core.py`, `ai300/azure.py`, `configs/m2-demo2.json`, `data/corpus.jsonl`.

## Numbered Steps

<a id="step-1"></a>

### Step 1 — Call the gpt-5.6-luna deployment in Microsoft Foundry to generate support-response examples from training-source documents, logging source, prompt, and generator versions

```bash
./module2/m2-c4/scripts/lab-step.sh 1
```

**Result:** the terminal prints the exact retained report path. Open `step-1-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `generated_path`, `review_path`, `examples`. These are contracts, not promised values.

**Decision and failure action:** After step1, open review.jsonl in VS Code. Compare every example with its exact training-source document; fill ACCEPT or REJECT, a reason and reviewer. Do not alter hashes or auto-approve. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-2"></a>

### Step 2 — Check JSONL structure, duplicate prompts, source references, and split leakage with Python; manually accept or reject examples by checking their claims against the source

```bash
./module2/m2-c4/scripts/lab-step.sh 2
```

**Result:** the terminal prints the exact retained report path. Open `step-2-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `accepted`, `rejected`, `data_path`, `hashes`. These are contracts, not promised values.

**Decision and failure action:** After step1, open review.jsonl in VS Code. Compare every example with its exact training-source document; fill ACCEPT or REJECT, a reason and reviewer. Do not alter hashes or auto-approve. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-3"></a>

### Step 3 — Register accepted examples, rejection reasons, hashes, and separate validation and test files as versioned Azure ML data assets

```bash
./module2/m2-c4/scripts/lab-step.sh 3
```

**Result:** the terminal prints the exact retained report path. Open `step-3-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `data_assets`, `version`, `final_test_separate`. These are contracts, not promised values.

**Decision and failure action:** After step1, open review.jsonl in VS Code. Compare every example with its exact training-source document; fill ACCEPT or REJECT, a reason and reviewer. Do not alter hashes or auto-approve. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.

## Interpretation and Next Action

After step1, open review.jsonl in VS Code. Compare every example with its exact training-source document; fill ACCEPT or REJECT, a reason and reviewer. Do not alter hashes or auto-approve.

A source check, completed job, passing validation gate, frozen final test and rollback proof are distinct states. If a gate rejects a candidate, retain the baseline and inspect individual failures. Canary step3 can stop promotion; still run step4 to exercise baseline restoration.

## Cleanup and Evidence Retention

```bash
./module2/m2-c4/scripts/lab-down.sh
```

Cleanup uses the retained resource/config snapshot. It only deletes candidate deployments created by the owning run; it leaves unrelated/name-collision deployments in place. Keep dependency artifacts, manual reviews and consumed-test ledgers. Do not clean up a live prerequisite endpoint until its dependent exercises are complete; retained endpoints/storage can remain billable. See [cleanup options](../../setup/README.md#troubleshooting-and-cleanup).

## What You Achieved

You followed the stated objective actions, retained actual response identities and made an evidence-based decision. Azure runtime is NOT RUN in this source revision; validate it in your own authorized lab.

[Previous exercise](../../module2/m2-c2/README.md) · [Next exercise](../../module2/m2-c5/README.md)
