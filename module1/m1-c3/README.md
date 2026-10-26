# Demo: Run hybrid search and semantic reranking in Azure

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 1, clip 3 · Reference placeholder: `m1-demo2-after`

## Your scenario

You are improving an Azure support assistant and need evidence that retrieval, model behavior or a release decision meets its stated goal. This demo covers the actions below; actual results are not available yet.

## Your learning goals

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1c** — Implement and optimize hybrid search approaches combining semantic and keyword-based retrieval

## Prerequisites and starting state

See the [course prerequisites](../../setup/README.md). Azure assets, data/model dependencies, credentials, quota, actual costs and reset procedures remain to be verified. The reference branch is a placeholder; it does not supply a completed environment.

## Planned steps

| Step | Planned action |
|---|---|
| [Step 1](#step-1) | Send text and vector queries together to Azure AI Search; compare its reciprocal rank fusion results with separate keyword and vector searches. |
| [Step 2](#step-2) | Vary vector weight and candidate depth, then enable semantic reranking with 50 vector candidates and inspect search and reranker scores separately. |
| [Step 3](#step-3) | Compare exact identifiers and paraphrased questions on the same validation set; keep relevance gains without hiding query-type regressions. |

<a id="step-1"></a>

## Step 1

Send text and vector queries together to Azure AI Search; compare its reciprocal rank fusion results with separate keyword and vector searches.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Vary vector weight and candidate depth, then enable semantic reranking with 50 vector candidates and inspect search and reranker scores separately.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Compare exact identifiers and paraphrased questions on the same validation set; keep relevance gains without hiding query-type regressions.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Keyword, vector and reciprocal-rank-fused result comparisons
- Vector-weight, candidate-depth and semantic reranker response fields
- Exact-identifier and paraphrase validation results

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
