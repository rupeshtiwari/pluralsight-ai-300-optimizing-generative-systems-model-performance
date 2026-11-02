# Demo: Tune chunk sizes and similarity cutoffs on Azure AI Search results

[Course index](../../README.md) · [Setup](../../setup/README.md) · [Run guide](../../docs/run-demos.md)

**Module 1 · Clip 2 · 5 minutes · CPU Azure lab**

## What you will learn

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1a** — Optimize retrieval performance by tuning similarity thresholds, chunk sizes, and retrieval strategies

You operate the support-assistant project and make a decision from real retained evidence. Source is supplied; offline tests are not successful Azure execution.

## Prerequisites and Starting State

Complete [the shared setup](../../setup/README.md), authenticate your permitted Azure identity, configure existing course-owned resources, and inspect the declared controls in [`configs/m1-demo1.json`](../../configs/m1-demo1.json). Preserve your own changes before switching branches.

## Open and Check

From the cloned repository root:

```bash
git switch m1-demo1-after
# Activate .venv (Windows Git Bash: source .venv/Scripts/activate)
source .venv/bin/activate
./module1/m1-c2/scripts/preflight_check.sh --offline
./module1/m1-c2/scripts/preflight_check.sh --live
./module1/m1-c2/scripts/lab-up.sh
```

The offline command needs only Python standard-library source. Live checks use your actual resources; provisioning/inference/jobs can incur charges. `lab-up` prints a unique `evidence/m1-demo1/<UTC-uuid>/` folder. Stay at the repo root.

## Source to Inspect

Open `ai300/demos.py:retrieval_chunks` in VS Code (file and named function). Related source: `ai300/demos.py`, `ai300/core.py`, `ai300/azure.py`, `configs/m1-demo1.json`, `data/corpus.jsonl`, `data/queries.jsonl`.

## Numbered Steps

<a id="step-1"></a>

### Step 1 — Query one Azure AI Search Free-tier index with a chunk_size pre-filter to select 64-, 128-, or 192-token chunks of the same corpus, encoded with all-MiniLM-L6-v2

```bash
./module1/m1-c2/scripts/lab-step.sh 1
```

**Result:** the terminal prints the exact retained report path. Open `step-1-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `indexed_chunks`, `rows`, `variants`, `chunk_size`. These are contracts, not promised values.

**Decision and failure action:** The selection must fit the declared p95 latency budget. Chunk size, candidate depth and cutoff comparisons retain their exact settings; a rejected cutoff cannot be disguised as server-side filtering. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-2"></a>

### Step 2 — Vary vector candidate depth, convert single-vector query scores back to cosine similarity in the Python client, and apply a cutoff; inspect retained and rejected results

```bash
./module1/m1-c2/scripts/lab-step.sh 2
```

**Result:** the terminal prints the exact retained report path. Open `step-2-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `retained`, `rejected`, `cosine_similarity`, `settings`. These are contracts, not promised values.

**Decision and failure action:** The selection must fit the declared p95 latency budget. Chunk size, candidate depth and cutoff comparisons retain their exact settings; a rejected cutoff cannot be disguised as server-side filtering. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-3"></a>

### Step 3 — Compare Recall@k, boundary failures, and latency while changing one control at a time; keep the configuration with the best recall within the latency budget

```bash
./module1/m1-c2/scripts/lab-step.sh 3
```

**Result:** the terminal prints the exact retained report path. Open `step-3-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `comparison`, `selected_variant`, `selected_settings`, `latency_budget_ms`. These are contracts, not promised values.

**Decision and failure action:** The selection must fit the declared p95 latency budget. Chunk size, candidate depth and cutoff comparisons retain their exact settings; a rejected cutoff cannot be disguised as server-side filtering. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.

## Interpretation and Next Action

The selection must fit the declared p95 latency budget. Chunk size, candidate depth and cutoff comparisons retain their exact settings; a rejected cutoff cannot be disguised as server-side filtering.

A source check, completed job, passing validation gate, frozen final test and rollback proof are distinct states. If a gate rejects a candidate, retain the baseline and inspect individual failures. Canary step3 can stop promotion; still run step4 to exercise baseline restoration.

## Cleanup and Evidence Retention

```bash
./module1/m1-c2/scripts/lab-down.sh
```

Cleanup uses the retained resource/config snapshot. It only deletes candidate deployments created by the owning run; it leaves unrelated/name-collision deployments in place. Keep dependency artifacts, manual reviews and consumed-test ledgers. Do not clean up a live prerequisite endpoint until its dependent exercises are complete; retained endpoints/storage can remain billable. See [cleanup options](../../setup/README.md#troubleshooting-and-cleanup).

## What You Achieved

You followed the stated objective actions, retained actual response identities and made an evidence-based decision. Azure runtime is NOT RUN in this source revision; validate it in your own authorized lab.

[Previous exercise](../../README.md) · [Next exercise](../../module1/m1-c3/README.md)
