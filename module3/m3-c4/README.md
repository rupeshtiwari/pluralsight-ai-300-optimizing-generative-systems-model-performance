# Demo: Optimize and test the Azure model endpoint

[Course index](../../README.md) · [Setup](../../setup/README.md) · [Run guide](../../docs/run-demos.md)

**Module 3 · Clip 4 · 4 minutes · CPU Azure lab**

## What you will learn

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2c** — Monitor and optimize fine-tuned model performance
- **EO2d** — Manage a fine-tuned model from development through production deployment

You operate the support-assistant project and make a decision from real retained evidence. Source is supplied; offline tests are not successful Azure execution.

## Prerequisites and Starting State

Complete [the shared setup](../../setup/README.md), authenticate your permitted Azure identity, configure existing course-owned resources, and inspect the declared controls in [`configs/m3-demo3.json`](../../configs/m3-demo3.json). Preserve your own changes before switching branches.

Required retained runs: `m3-demo2`. Enter their actual run folders in `config.local.json` → `runs` before initializing this exercise. Their source/config/artifact hashes must match.

The dedicated baseline endpoint must already exist. If cleanup removed deployments, use `python -m ai300.setup restore-endpoint --from-run YOUR_RETAINED_RUN` with exact saved versions; do not replay a consumed final test.

## Open and Check

From the cloned repository root:

```bash
git switch m3-demo3-after
# Activate .venv (Windows Git Bash: source .venv/Scripts/activate)
source .venv/bin/activate
./module3/m3-c4/scripts/preflight_check.sh --offline
./module3/m3-c4/scripts/preflight_check.sh --live
./module3/m3-c4/scripts/lab-up.sh
```

The offline command needs only Python standard-library source. Live checks use your actual resources; provisioning/inference/jobs can incur charges. `lab-up` prints a unique `evidence/m3-demo3/<UTC-uuid>/` folder. Stay at the repo root.

## Source to Inspect

Open `ai300/demos.py:endpoint_test` in VS Code (file and named function). Related source: `ai300/demos.py`, `ai300/core.py`, `ai300/azure.py`, `configs/m3-demo3.json`, `serving/score.py`.

## Numbered Steps

<a id="step-1"></a>

### Step 1 — Benchmark the candidate deployment directly with a fixed validation workload; compare output-length limits using latency, output tokens, CPU and memory utilization, and answer quality

```bash
./module3/m3-c4/scripts/lab-step.sh 1
```

**Result:** the terminal prints the exact retained report path. Open `step-1-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `benchmarks`, `utilization_evidence`, `selected_max_new_tokens`. These are contracts, not promised values.

**Decision and failure action:** Compare output limits using separate workload time windows and Azure Monitor samples. Before step3, complete final-test-review.jsonl for BOTH baseline and candidate. The final test is consumed once; a rejection needs a new untouched test set after tuning. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-2"></a>

### Step 2 — Freeze the selected model, environment, and inference settings (output-length limit and request timeout), then run the untouched domain and general-capability test set against the candidate and baseline deployments

```bash
./module3/m3-c4/scripts/lab-step.sh 2
```

**Result:** the terminal prints the exact retained report path. Open `step-2-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `frozen_release`, `frozen_release_sha256`, `final_test`, `manual_review_path`. These are contracts, not promised values.

**Decision and failure action:** Compare output limits using separate workload time windows and Azure Monitor samples. Before step3, complete final-test-review.jsonl for BOTH baseline and candidate. The final test is consumed once; a rejection needs a new untouched test set after tuning. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-3"></a>

### Step 3 — Store the final test report and release configuration with the model version in Azure ML

```bash
./module3/m3-c4/scripts/lab-step.sh 3
```

**Result:** the terminal prints the exact retained report path. Open `step-3-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `release_decision`, `gate_checks`, `baseline_comparison`, `mlflow_run_id`. These are contracts, not promised values.

**Decision and failure action:** Compare output limits using separate workload time windows and Azure Monitor samples. Before step3, complete final-test-review.jsonl for BOTH baseline and candidate. The final test is consumed once; a rejection needs a new untouched test set after tuning. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.

## Interpretation and Next Action

Compare output limits using separate workload time windows and Azure Monitor samples. Before step3, complete final-test-review.jsonl for BOTH baseline and candidate. The final test is consumed once; a rejection needs a new untouched test set after tuning.

A source check, completed job, passing validation gate, frozen final test and rollback proof are distinct states. If a gate rejects a candidate, retain the baseline and inspect individual failures. Canary step3 can stop promotion; still run step4 to exercise baseline restoration.

## Cleanup and Evidence Retention

```bash
./module3/m3-c4/scripts/lab-down.sh
```

Cleanup uses the retained resource/config snapshot. It only deletes candidate deployments created by the owning run; it leaves unrelated/name-collision deployments in place. Keep dependency artifacts, manual reviews and consumed-test ledgers. Do not clean up a live prerequisite endpoint until its dependent exercises are complete; retained endpoints/storage can remain billable. See [cleanup options](../../setup/README.md#troubleshooting-and-cleanup).

## What You Achieved

You followed the stated objective actions, retained actual response identities and made an evidence-based decision. Azure runtime is NOT RUN in this source revision; validate it in your own authorized lab.

[Previous exercise](../../module3/m3-c3/README.md) · [Next exercise](../../module3/m3-c5/README.md)
