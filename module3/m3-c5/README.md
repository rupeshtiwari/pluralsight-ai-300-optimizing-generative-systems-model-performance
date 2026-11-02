# Demo: Monitor canary traffic and verify rollback in Azure ML

[Course index](../../README.md) · [Setup](../../setup/README.md) · [Run guide](../../docs/run-demos.md)

**Module 3 · Clip 5 · 5 minutes · CPU Azure lab**

## What you will learn

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2c** — Monitor and optimize fine-tuned model performance
- **EO2d** — Manage a fine-tuned model from development through production deployment

You operate the support-assistant project and make a decision from real retained evidence. Source is supplied; offline tests are not successful Azure execution.

## Prerequisites and Starting State

Complete [the shared setup](../../setup/README.md), authenticate your permitted Azure identity, configure existing course-owned resources, and inspect the declared controls in [`configs/m3-demo4.json`](../../configs/m3-demo4.json). Preserve your own changes before switching branches.

Required retained runs: `m3-demo3`. Enter their actual run folders in `config.local.json` → `runs` before initializing this exercise. Their source/config/artifact hashes must match.

The dedicated baseline endpoint must already exist. If cleanup removed deployments, use `python -m ai300.setup restore-endpoint --from-run YOUR_RETAINED_RUN` with exact saved versions; do not replay a consumed final test.

## Open and Check

From the cloned repository root:

```bash
git switch m3-demo4-after
# Activate .venv (Windows Git Bash: source .venv/Scripts/activate)
source .venv/bin/activate
./module3/m3-c5/scripts/preflight_check.sh --offline
./module3/m3-c5/scripts/preflight_check.sh --live
./module3/m3-c5/scripts/lab-up.sh
```

The offline command needs only Python standard-library source. Live checks use your actual resources; provisioning/inference/jobs can incur charges. `lab-up` prints a unique `evidence/m3-demo4/<UTC-uuid>/` folder. Stay at the repo root.

Prepare the normal latency alert once after `lab-up`, before numbered steps:

```bash
python -m ai300.cli --demo m3-demo4 prepare-alert
```

This is explicit setup. The numbered metric-inspection step reads the prepared rule; it does not create a forced failure.

## Source to Inspect

Open `ai300/demos.py:canary_rollback` in VS Code (file and named function). Related source: `ai300/demos.py`, `ai300/core.py`, `ai300/azure.py`, `configs/m3-demo4.json`, `serving/score.py`.

## Numbered Steps

<a id="step-1"></a>

### Step 1 — Allocate 90 percent of managed endpoint traffic to the baseline and 10 percent to the candidate; send enough labeled test traffic to meet each gate’s minimum sample size, and record which deployment served each response

```bash
./module3/m3-c5/scripts/lab-step.sh 1
```

**Result:** the terminal prints the exact retained report path. Open `step-1-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `traffic`, `rows`, `sample_counts`, `manual_review_path`. These are contracts, not promised values.

**Decision and failure action:** Step1 sends bounded90/10 routed traffic until each deployment/query type meets its declared sample minimum, or restores baseline on failure. Step2 only reads the prepared alert and actual metric window. Before step3, complete canary-review.jsonl. Step4 always restores100percent baseline, even when every gate passes. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-2"></a>

### Step 2 — Inspect Request Latency P95 split by deployment, Requests Per Minute split by deployment and status-code class, and the prepared Azure Monitor alert rule on Request Latency P95

```bash
./module3/m3-c5/scripts/lab-step.sh 2
```

**Result:** the terminal prints the exact retained report path. Open `step-2-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `alert_id`, `alert`, `metric_snapshot`, `telemetry_status`. These are contracts, not promised values.

**Decision and failure action:** Step1 sends bounded90/10 routed traffic until each deployment/query type meets its declared sample minimum, or restores baseline on failure. Step2 only reads the prepared alert and actual metric window. Before step3, complete canary-review.jsonl. Step4 always restores100percent baseline, even when every gate passes. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-3"></a>

### Step 3 — Check the candidate’s canary responses and serving metrics against the predeclared gates, and stop promotion on any failure

```bash
./module3/m3-c5/scripts/lab-step.sh 3
```

**Result:** the terminal prints the exact retained report path. Open `step-3-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `decision`, `failed_gates`, `gate_checks`, `manual_semantic_review`. These are contracts, not promised values.

**Decision and failure action:** Step1 sends bounded90/10 routed traffic until each deployment/query type meets its declared sample minimum, or restores baseline on failure. Step2 only reads the prepared alert and actual metric window. Before step3, complete canary-review.jsonl. Step4 always restores100percent baseline, even when every gate passes. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-4"></a>

### Step 4 — Exercise the rollback path by restoring 100 percent traffic to the baseline, then verify the routed model identity and responses before the promotion decision

```bash
./module3/m3-c5/scripts/lab-step.sh 4
```

**Result:** the terminal prints the exact retained report path. Open `step-4-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `traffic`, `rollback_verified`, `routed_responses`, `recovery_metrics`. These are contracts, not promised values.

**Decision and failure action:** Step1 sends bounded90/10 routed traffic until each deployment/query type meets its declared sample minimum, or restores baseline on failure. Step2 only reads the prepared alert and actual metric window. Before step3, complete canary-review.jsonl. Step4 always restores100percent baseline, even when every gate passes. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.

## Interpretation and Next Action

Step1 sends bounded90/10 routed traffic until each deployment/query type meets its declared sample minimum, or restores baseline on failure. Step2 only reads the prepared alert and actual metric window. Before step3, complete canary-review.jsonl. Step4 always restores100percent baseline, even when every gate passes.

A source check, completed job, passing validation gate, frozen final test and rollback proof are distinct states. If a gate rejects a candidate, retain the baseline and inspect individual failures. Canary step3 can stop promotion; still run step4 to exercise baseline restoration.

## Cleanup and Evidence Retention

```bash
./module3/m3-c5/scripts/lab-down.sh
```

Cleanup uses the retained resource/config snapshot. It only deletes candidate deployments created by the owning run; it leaves unrelated/name-collision deployments in place. Keep dependency artifacts, manual reviews and consumed-test ledgers. Do not clean up a live prerequisite endpoint until its dependent exercises are complete; retained endpoints/storage can remain billable. See [cleanup options](../../setup/README.md#troubleshooting-and-cleanup).

## What You Achieved

You followed the stated objective actions, retained actual response identities and made an evidence-based decision. Azure runtime is NOT RUN in this source revision; validate it in your own authorized lab.

[Previous exercise](../../module3/m3-c4/README.md) · [Next exercise](../../README.md)
