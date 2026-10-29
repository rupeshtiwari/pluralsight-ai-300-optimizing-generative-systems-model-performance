# Demo: Monitor Azure traffic and verify rollback

[Previous: Optimize and test the Azure model endpoint](../m3-c4/README.md) · [Course index](../../README.md) · [Next: course index](../../README.md)

Module 3, clip 5 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

A validation-qualified model can fail under routed traffic. Observe a real failed gate, stop promotion and prove that baseline service recovers.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2c** — Monitor and optimize fine-tuned model performance
- **EO2d** — Manage a fine-tuned model from development through production deployment

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

Retain completed prerequisite runs: `m3-demo3`. Put their actual run-folder paths in `config.local.json` → `runs` before starting. Follow each linked prerequisite page from the course index; missing completed artifacts block this exercise.

Use a dedicated baseline endpoint created by `python -m ai300.setup create-baseline`. For a continuation after cleanup, restore the exact saved baseline/candidate versions with `python -m ai300.setup restore-endpoint --from-run "YOUR_RETAINED_DEPLOYMENT_OR_FINAL_TEST_RUN"`; keep the original dependency run. Keep baseline at 100% before the release exercise.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m3-demo4-after
source .venv/bin/activate
./module3/m3-c5/scripts/preflight_check.sh
./module3/m3-c5/scripts/lab-up.sh
```

Read [`configs/m3-demo4.json`](../../configs/m3-demo4.json) and [`serving/score.py`](../../serving/score.py), [`ai300/azure.py`](../../ai300/azure.py). The shared implementation is [`canary_rollback`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run.

`lab-up` prints your unique `evidence/m3-demo4/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

## Your Four Steps

| Step | Action |
|---|---|
| [1](#step-1) | Configure an Azure Monitor alert on Request Latency P95; inspect latency by deployment, Requests Per Minute by deployment and status-code class, and each deployment’s CPU and memory utilization. |
| [2](#step-2) | Allocate 90 percent of managed endpoint traffic to the baseline and 10 percent to the candidate; send labeled test traffic and retain deployment identities in the evidence. |
| [3](#step-3) | Inspect a real candidate gate failure from a predeclared, controlled rollback test and stop promotion; keep the baseline’s normal gate unchanged and distinguish the exercise from production-user outcomes. |
| [4](#step-4) | Restore 100 percent traffic to the baseline, then verify the routed model identity, responses, and recovered operational behavior. |


<a id="step-1"></a>

### Step 1: Configure an Azure Monitor alert on Request Latency P95; inspect latency by deployment, Requests Per Minute by deployment and status-code class, and each deployment’s CPU and memory utilization.

**Learning Goal:** Configure an Azure Monitor alert on Request Latency P95; inspect latency by deployment, Requests Per Minute by deployment and status-code class, and each deployment’s CPU and memory utilization.

**Demo Workspace:** VS Code, repository root; inspect `canary_rollback` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c5/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `alert_id`, `alert`, `metric_snapshot`, `telemetry_status`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Before traffic, inspect `rollback_test` in `configs/m3-demo4.json`. Its isolated test-only trigger is frozen in step 1 and used by the RequestLatency_P95 alert; baseline recovery keeps the normal budget. Endpoint metrics split latency by deployment and request rate by deployment/status class; deployment metrics use CpuUtilizationPercentage and CpuMemoryUtilizationPercentage. Missing telemetry remains pending. A failed inspection attempts baseline restoration immediately; the historical canary window is retained for a retry.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Allocate 90 percent of managed endpoint traffic to the baseline and 10 percent to the candidate; send labeled test traffic and retain deployment identities in the evidence.

**Learning Goal:** Allocate 90 percent of managed endpoint traffic to the baseline and 10 percent to the candidate; send labeled test traffic and retain deployment identities in the evidence.

**Demo Workspace:** VS Code, repository root; inspect `canary_rollback` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c5/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `traffic`, `rows`, `by_deployment`, `population`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Set baseline/candidate traffic to 90/10, send bounded labeled requests and record the identity returned by each. Thirty requests need not produce exactly three candidate responses. Both deployments must be observed.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Inspect a real candidate gate failure from a predeclared, controlled rollback test and stop promotion; keep the baseline’s normal gate unchanged and distinguish the exercise from production-user outcomes.

**Learning Goal:** Inspect a real candidate gate failure from a predeclared, controlled rollback test and stop promotion; keep the baseline’s normal gate unchanged and distinguish the exercise from production-user outcomes.

**Demo Workspace:** VS Code, repository root; inspect `canary_rollback` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c5/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `promotion`, `failed_gates`, `metric_snapshot`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Read the actual canary window and verified failures. `canary-review.jsonl` can establish human semantic failures; an unreviewed proxy mismatch is advisory only. The objective schema gate and actual operational test trigger can stop promotion without a semantic judgment. The default configuration predeclares a 1 ms candidate P95 threshold solely for this isolated rollback exercise; it is explicitly not a production SLO. The failed gate must still come from a real Azure Monitor measurement above that threshold. Normal baseline recovery uses the separate 30,000 ms budget. If no gate fails, restore baseline and retain the trigger as unobserved. Never fabricate a value or change a threshold after traffic.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-4"></a>

### Step 4: Restore 100 percent traffic to the baseline, then verify the routed model identity, responses, and recovered operational behavior.

**Learning Goal:** Restore 100 percent traffic to the baseline, then verify the routed model identity, responses, and recovered operational behavior.

**Demo Workspace:** VS Code, repository root; inspect `canary_rollback` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module3/m3-c5/scripts/lab-step.sh 4
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-4-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `traffic`, `routed_model_identities`, `routed_responses`, `recovery_metrics`, `rollback_verified`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Restore 100/0, verify routed baseline identity and responses, then wait for the genuine recovery metric window. Routing success and operational recovery are separate evidence requirements.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

A validation-qualified model can fail under routed traffic. Observe a real failed gate, stop promotion and prove that baseline service recovers. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module3/m3-c5/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m3-demo4-after` reference using `git diff m3-demo4-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Optimize and test the Azure model endpoint](../m3-c4/README.md) · [Course index](../../README.md) · [Next: course index](../../README.md)
