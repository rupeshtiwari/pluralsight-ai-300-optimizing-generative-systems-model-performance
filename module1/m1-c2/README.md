# Demo: Tune chunks and similarity cutoffs in Azure AI Search

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 1, clip 2 · Reference placeholder: `m1-demo1-after`

## Your scenario

You are improving an Azure support assistant and need evidence that retrieval, model behavior or a release decision meets its stated goal. This demo covers the actions below; actual results are not available yet.

## Your learning goals

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1a** — Optimize retrieval performance by tuning similarity thresholds, chunk sizes, and retrieval strategies

## Prerequisites and starting state

See the [course prerequisites](../../setup/README.md). Azure assets, data/model dependencies, credentials, quota, actual costs and reset procedures remain to be verified. The reference branch is a placeholder; it does not supply a completed environment.

## Planned steps

| Step | Planned action |
|---|---|
| [Step 1](#step-1) | Query one Azure AI Search Free-tier index with a chunk_size pre-filter to select 64-, 128-, or 192-token chunks of the same corpus, encoded with all-MiniLM-L6-v2. |
| [Step 2](#step-2) | Vary vector candidate depth and apply a cosine cutoff in the Python client after converting a pure single-vector search score; inspect retained and rejected results. |
| [Step 3](#step-3) | Compare Recall@k, boundary failures, and latency while changing one control at a time; retain the configuration that supplies useful evidence. |

<a id="step-1"></a>

## Step 1

Query one Azure AI Search Free-tier index with a chunk_size pre-filter to select 64-, 128-, or 192-token chunks of the same corpus, encoded with all-MiniLM-L6-v2.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Vary vector candidate depth and apply a cosine cutoff in the Python client after converting a pure single-vector search score; inspect retained and rejected results.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Compare Recall@k, boundary failures, and latency while changing one control at a time; retain the configuration that supplies useful evidence.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Chunk-size-controlled Azure search responses
- Retained and rejected single-vector candidates with converted cosine values
- Recall@k, boundary-failure and latency comparison

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
