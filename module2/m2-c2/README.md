# Demo: Fine-tune domain embeddings in Azure ML

[Course index](../../README.md) · [Setup](../../setup/README.md) · [Run guide](../../docs/run-demos.md)

**Module 2 · Clip 2 · 5 minutes · CPU Azure lab**

## What you will learn

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1b** — Select and fine-tune embedding models for domain-specific use cases and accuracy improvements

You operate the support-assistant project and make a decision from real retained evidence. Source is supplied; offline tests are not successful Azure execution.

## Prerequisites and Starting State

Complete [the shared setup](../../setup/README.md), authenticate your permitted Azure identity, configure existing course-owned resources, and inspect the declared controls in [`configs/m2-demo1.json`](../../configs/m2-demo1.json). Preserve your own changes before switching branches.

## Open and Check

From the cloned repository root:

```bash
git switch m2-demo1-before
# Activate .venv (Windows Git Bash: source .venv/Scripts/activate)
source .venv/bin/activate
./module2/m2-c2/scripts/preflight_check.sh --offline
```

The offline command needs only Python standard-library source. Live checks use your actual resources; provisioning/inference/jobs can incur charges. `lab-up` prints a unique `evidence/m2-demo1/<UTC-uuid>/` folder. Stay at the repo root.

## Complete the Starter

The before branch intentionally leaves `ai300/demos.py:embedding_train` unfinished. Open that function in VS Code and implement the numbered actions below using the supplied helpers and configuration. Shared infrastructure, earlier demo implementations and cleanup stay available. Live startup/steps stop with `STARTER` until the placeholder is replaced. An offline preflight checks prerequisites and reports the source state; it does not certify an unfinished solution.

Inspect the complete reference without switching or losing edits:

```bash
git fetch origin
git diff HEAD origin/m2-demo1-after -- ai300/demos.py
```

To run the supplied complete source instead of authoring the function, restore the reference file into this starter checkout, then run the full source checks:

```bash
git restore --source=origin/m2-demo1-after -- ai300/demos.py
python scripts/check_source.py
```

This restore replaces local edits to that file; commit your work first. [All before/after branches](../../docs/exercise-branches.md) explains safe switching and dependency evidence.

## Initialize the Live Run

Finish the source and prerequisite runs, then initialize from the repository root:

```bash
./module2/m2-c2/scripts/preflight_check.sh --live
./module2/m2-c2/scripts/lab-up.sh
```

## Source to Inspect

Open `ai300/demos.py:embedding_train` in VS Code (file and named function). Related source: `ai300/demos.py`, `ai300/core.py`, `ai300/azure.py`, `configs/m2-demo1.json`, `jobs/train_embedding.py`, `ai300/ml.py`, `data/embedding-pairs.jsonl`.

## Numbered Steps

<a id="step-1"></a>

### Step 1 — Configure a Sentence Transformers contrastive training script for the selected bge-small-en-v1.5 model with reviewed positive pairs and hard negatives, then submit an Azure ML CPU command job

```bash
./module2/m2-c2/scripts/lab-step.sh 1
```

**Result:** the terminal prints the exact retained report path. Open `step-1-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `job_name`, `job_id`, `config`, `environment_id`, `studio_url`. These are contracts, not promised values.

**Decision and failure action:** Use the same chunk_size for both base fields and the tuned field. A tuned checkpoint must beat both baselines. Its retained checkpoint identity is required if later retrieval uses tuned_vector. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-2"></a>

### Step 2 — Inspect the completed job and confirm its code, environment, and data versions; select the checkpoint with the best validation metrics and keep the job output

```bash
./module2/m2-c2/scripts/lab-step.sh 2
```

**Result:** the terminal prints the exact retained report path. Open `step-2-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `status`, `result`, `output_path`, `result_sha256`. These are contracts, not promised values.

**Decision and failure action:** Use the same chunk_size for both base fields and the tuned field. A tuned checkpoint must beat both baselines. Its retained checkpoint identity is required if later retrieval uses tuned_vector. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.
<a id="step-3"></a>

### Step 3 — Encode corpus and queries with the selected checkpoint; populate its dedicated vector field in the same index, filter to the same chunk_size, and keep the tuned field only if its held-out relevance beats both the all-MiniLM-L6-v2 and base bge-small-en-v1.5 fields

```bash
./module2/m2-c2/scripts/lab-step.sh 3
```

**Result:** the terminal prints the exact retained report path. Open `step-3-<attempt>/report.json` in your run folder; inspect `raw/` beside it. Expected field names: `baseline`, `tuned`, `checkpoint_job`, `query_and_document_encoder_identical`. These are contracts, not promised values.

**Decision and failure action:** Use the same chunk_size for both base fields and the tuned field. A tuned checkpoint must beat both baselines. Its retained checkpoint identity is required if later retrieval uses tuned_vector. Missing permissions, incomplete jobs, unfilled manual reviews or delayed telemetry produce HOLD. Correct the named prerequisite and retry only the incomplete step. Completed steps are immutable; preserve every failed attempt.

## Interpretation and Next Action

Use the same chunk_size for both base fields and the tuned field. A tuned checkpoint must beat both baselines. Its retained checkpoint identity is required if later retrieval uses tuned_vector.

A source check, completed job, passing validation gate, frozen final test and rollback proof are distinct states. If a gate rejects a candidate, retain the baseline and inspect individual failures. Canary step3 can stop promotion; still run step4 to exercise baseline restoration.

## Cleanup and Evidence Retention

```bash
./module2/m2-c2/scripts/lab-down.sh
```

Cleanup uses the retained resource/config snapshot. It only deletes candidate deployments created by the owning run; it leaves unrelated/name-collision deployments in place. Keep dependency artifacts, manual reviews and consumed-test ledgers. Do not clean up a live prerequisite endpoint until its dependent exercises are complete; retained endpoints/storage can remain billable. See [cleanup options](../../setup/README.md#troubleshooting-and-cleanup).

## What You Achieved

You followed the stated objective actions, retained actual response identities and made an evidence-based decision. Azure runtime is NOT RUN in this source revision; validate it in your own authorized lab.

[Previous exercise](../../module1/m1-c5/README.md) · [Next exercise](../../module2/m2-c4/README.md)
