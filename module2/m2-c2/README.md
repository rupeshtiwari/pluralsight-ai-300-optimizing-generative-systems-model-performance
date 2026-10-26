# Demo: Fine-tune domain embeddings in Azure ML

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 2, clip 2 · Reference placeholder: `m2-demo1-after`

## Your scenario

You are improving an Azure support assistant and need evidence that retrieval, model behavior or a release decision meets its stated goal. This demo covers the actions below; actual results are not available yet.

## Your learning goals

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1b** — Select and fine-tune embedding models for domain-specific use cases and accuracy improvements

## Prerequisites and starting state

See the [course prerequisites](../../setup/README.md). Azure assets, data/model dependencies, credentials, quota, actual costs and reset procedures remain to be verified. The reference branch is a placeholder; it does not supply a completed environment.

## Planned steps

| Step | Planned action |
|---|---|
| [Step 1](#step-1) | Configure a Sentence Transformers contrastive training script with reviewed positive pairs and hard negatives, then submit an Azure ML CPU command job. |
| [Step 2](#step-2) | Inspect a completed job with matching code, environment, and data versions; select its checkpoint from validation metrics and retain the job output. |
| [Step 3](#step-3) | Encode corpus and queries with the selected checkpoint; populate its dedicated vector field in the same index, filter to the same chunk_size, and compare held-out relevance with the baseline fields. |

<a id="step-1"></a>

## Step 1

Configure a Sentence Transformers contrastive training script with reviewed positive pairs and hard negatives, then submit an Azure ML CPU command job.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Inspect a completed job with matching code, environment, and data versions; select its checkpoint from validation metrics and retain the job output.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Encode corpus and queries with the selected checkpoint; populate its dedicated vector field in the same index, filter to the same chunk_size, and compare held-out relevance with the baseline fields.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Azure ML CPU job configuration with reviewed positive pairs and hard negatives
- Matching completed training job, input versions, validation metrics and selected checkpoint
- Checkpoint-aligned corpus/query vectors and held-out baseline comparison

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
