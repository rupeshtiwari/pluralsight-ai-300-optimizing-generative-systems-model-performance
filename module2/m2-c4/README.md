# Demo: Generate and version synthetic data with Foundry

[Previous: Fine-tune domain embeddings in Azure ML](../m2-c2/README.md) · [Course index](../../README.md) · [Next: Train a LoRA adapter in Azure ML](../m2-c5/README.md)

Module 2, clip 4 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

You need support examples without importing customer data. Generate from training policies, verify every claim manually, then register traceable assets.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2b** — Create and manage synthetic data for fine-tuning

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

This exercise has no earlier demo dependency. Its own setup establishes the index or job from the supplied corpus and labels, using your configured Azure resources.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m2-demo2-after
source .venv/bin/activate
./module2/m2-c4/scripts/preflight_check.sh
./module2/m2-c4/scripts/lab-up.sh
```

Read [`configs/m2-demo2.json`](../../configs/m2-demo2.json) and [`ai300/azure.py`](../../ai300/azure.py), [`data/corpus.jsonl`](../../data/corpus.jsonl). The shared implementation is [`synthetic_data`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run. The approved chunk-size list, semantic candidate depth 50, required manual review and zero-traffic deployment are checked contract constants where applicable; edits that violate them return HOLD. Chunk overlap is consumed by the tokenizer loop, while the named sweep settings are visible in the demo function.

`lab-up` prints your unique `evidence/m2-demo2/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Call the gpt-5.6-luna deployment in Microsoft Foundry to generate support-response examples from training-source documents, retaining source, prompt, and generator versions. |
| [2](#step-2) | Check JSONL structure, duplicate prompts, source references, and split leakage with Python; manually accept or reject examples by checking their claims against the source. |
| [3](#step-3) | Register accepted examples, rejection reasons, hashes, and separate validation and test files as versioned Azure ML data assets. |


<a id="step-1"></a>

### Step 1: Call the gpt-5.6-luna deployment in Microsoft Foundry to generate support-response examples from training-source documents, retaining source, prompt, and generator versions.

**Learning Goal:** Call the gpt-5.6-luna deployment in Microsoft Foundry to generate support-response examples from training-source documents, retaining source, prompt, and generator versions.

**Demo Workspace:** VS Code, repository root; inspect `synthetic_data` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c4/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `generated_path`, `review_path`, `examples`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Generation uses training sources only and retains the source hash, prompt version and Foundry identity. Generated content has no automatic acceptance.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Check JSONL structure, duplicate prompts, source references, and split leakage with Python; manually accept or reject examples by checking their claims against the source.

**Learning Goal:** Check JSONL structure, duplicate prompts, source references, and split leakage with Python; manually accept or reject examples by checking their claims against the source.

**Demo Workspace:** VS Code, repository root; inspect `synthetic_data` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c4/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `accepted`, `rejected`, `data_path`, `hashes`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Before this command, open generated.jsonl and review.jsonl in VS Code. Check each claim and condition against its exact source; fill ACCEPT/REJECT, reason and reviewer for every row. Duplicates, missing references and split leakage fail closed.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Register accepted examples, rejection reasons, hashes, and separate validation and test files as versioned Azure ML data assets.

**Learning Goal:** Register accepted examples, rejection reasons, hashes, and separate validation and test files as versioned Azure ML data assets.

**Demo Workspace:** VS Code, repository root; inspect `synthetic_data` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module2/m2-c4/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `data_assets`, `version`, `final_test_separate`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Register accepted examples, all decisions, rejected examples, hashes, validation and final-test assets separately. The training bundle mounts accepted data plus validation only.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

You need support examples without importing customer data. Generate from training policies, verify every claim manually, then register traceable assets. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module2/m2-c4/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m2-demo2-after` reference using `git diff m2-demo2-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Fine-tune domain embeddings in Azure ML](../m2-c2/README.md) · [Course index](../../README.md) · [Next: Train a LoRA adapter in Azure ML](../m2-c5/README.md)
