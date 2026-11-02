# Demo: Evaluate RAG variants with Azure services

[Course index](../../README.md) · [Setup](../../setup/README.md) · [Run guide](../../docs/run-demos.md)

**Module 1 · Clip 5 · 6 minutes · CPU Azure lab**

## What you will learn

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1d** — Evaluate and improve RAG system performance by using relevance metrics and A/B testing frameworks

You operate the support-assistant project and make a decision from real retained evidence. Source is supplied; offline tests are not successful Azure execution.

## Prerequisites and Starting State

Complete [the shared setup](../../setup/README.md), authenticate your permitted Azure identity, configure existing course-owned resources, and inspect the declared controls in [`configs/m1-demo3.json`](../../configs/m1-demo3.json). Preserve your own changes before switching branches.

## Open and Check

From the cloned repository root:

```bash
git switch m1-demo3-after
# Activate .venv (Windows Git Bash: source .venv/Scripts/activate)
source .venv/bin/activate
./module1/m1-c5/scripts/preflight_check.sh --offline
./module1/m1-c5/scripts/preflight_check.sh --live
./module1/m1-c5/scripts/lab-up.sh
```

The offline command needs only Python standard-library source. Live checks use your actual resources; provisioning/inference/jobs can incur charges. `lab-up` prints a unique `evidence/m1-demo3/<UTC-uuid>/` folder. Stay at the repo root.

## Source to Inspect

Open `ai300/demos.py:rag_ab` in VS Code (file and named function). Related source: `ai300/demos.py`, `ai300/core.py`, `ai300/azure.py`, `configs/m1-demo3.json`, `data/queries.jsonl`.

## Numbered Steps

<a id="step-1"></a>

### Step 1 — Run the Python experiment runner against two configurations of the same Azure AI Search index and the same gpt-5.6-luna deployment in Microsoft Foundry, holding the prompt and generation settings fixed

```bash
./module1/m1-c5/scripts/lab-step.sh 1
```

**Result:** the terminal prints the exact retained report path. Open `step-1-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `fixed_generation`, `rows`, `variants`, `manual_review_path`. These are contracts, not promised values.

**Decision and failure action:** Review both per-example variants and all synthetic-session outcomes manually. The fixed session count and response settings are declared before the run; repeated questions cannot establish real-user improvement. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-2"></a>

### Step 2 — Compare Recall@k, nDCG@k, manually reviewed answer support, and latency; inspect a response against its source and check for regressions

```bash
./module1/m1-c5/scripts/lab-step.sh 2
```

**Result:** the terminal prints the exact retained report path. Open `step-2-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `comparison`, `regressions`, `regression_observed`, `manual_semantic_review`. These are contracts, not promised values.

**Decision and failure action:** Review both per-example variants and all synthetic-session outcomes manually. The fixed session count and response settings are declared before the run; repeated questions cannot establish real-user improvement. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-3"></a>

### Step 3 — Assign synthetic sessions consistently to A or B, log exposures and outcomes to Azure ML with MLflow, and check the primary metric, declared before the run, against its stop rule

```bash
./module1/m1-c5/scripts/lab-step.sh 3
```

**Result:** the terminal prints the exact retained report path. Open `step-3-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `primary_metric`, `stop_rule`, `arm_summary`, `difference_B_minus_A`, `uncertainty`, `mlflow_run_id`, `manual_semantic_review`, `assigned_sessions`, `completed_outcomes`, `failed_outcomes`. These are contracts, not promised values.

**Decision and failure action:** Review both per-example variants and all synthetic-session outcomes manually. The fixed session count and response settings are declared before the run; repeated questions cannot establish real-user improvement. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.

## Interpretation and Next Action

Review both per-example variants and all synthetic-session outcomes manually. The fixed session count and response settings are declared before the run; repeated questions cannot establish real-user improvement.

A source check, completed job, passing validation gate, frozen final test and rollback proof are distinct states. If a gate rejects a candidate, retain the baseline and inspect individual failures. Canary step3 can stop promotion; still run step4 to exercise baseline restoration.

## Cleanup and Evidence Retention

```bash
./module1/m1-c5/scripts/lab-down.sh
```

Cleanup uses the retained resource/config snapshot. It only deletes candidate deployments created by the owning run; it leaves unrelated/name-collision deployments in place. Keep dependency artifacts, manual reviews and consumed-test ledgers. Do not clean up a live prerequisite endpoint until its dependent exercises are complete; retained endpoints/storage can remain billable. See [cleanup options](../../setup/README.md#troubleshooting-and-cleanup).

## What You Achieved

You followed the stated objective actions, retained actual response identities and made an evidence-based decision. Azure runtime is NOT RUN in this source revision; validate it in your own authorized lab.

[Previous exercise](../../module1/m1-c3/README.md) · [Next exercise](../../module2/m2-c2/README.md)
