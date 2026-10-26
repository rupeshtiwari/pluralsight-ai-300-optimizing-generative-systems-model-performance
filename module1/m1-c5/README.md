# Demo: Evaluate RAG variants with Azure services

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 1, clip 5 · Reference placeholder: `m1-demo3-after`

## Your scenario

You are improving an Azure support assistant and need evidence that retrieval, model behavior or a release decision meets its stated goal. This demo covers the actions below; actual results are not available yet.

## Your learning goals

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1d** — Evaluate and improve RAG system performance by using relevance metrics and A/B testing frameworks

## Prerequisites and starting state

See the [course prerequisites](../../setup/README.md). Azure assets, data/model dependencies, credentials, quota, actual costs and reset procedures remain to be verified. The reference branch is a placeholder; it does not supply a completed environment.

## Planned steps

| Step | Planned action |
|---|---|
| [Step 1](#step-1) | Run the Python experiment runner against two configurations of the same Azure AI Search index and the same gpt-5.6-luna deployment in Microsoft Foundry, holding the prompt and generation settings fixed. |
| [Step 2](#step-2) | Compare Recall@k, nDCG@k, labeled answer support, and latency using real retrieval and generated responses; inspect a concrete regression. |
| [Step 3](#step-3) | Assign synthetic sessions consistently to A or B, retain exposure and outcome logs in Azure ML with MLflow, and analyze the declared primary metric and stop rule. |

<a id="step-1"></a>

## Step 1

Run the Python experiment runner against two configurations of the same Azure AI Search index and the same gpt-5.6-luna deployment in Microsoft Foundry, holding the prompt and generation settings fixed.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Compare Recall@k, nDCG@k, labeled answer support, and latency using real retrieval and generated responses; inspect a concrete regression.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Assign synthetic sessions consistently to A or B, retain exposure and outcome logs in Azure ML with MLflow, and analyze the declared primary metric and stop rule.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Assignments to fixed retrieval variants and matching Foundry generation settings
- Recall@k, nDCG@k, labeled support, latency and concrete regression examples
- MLflow exposure/outcome logs, primary metric and stop-rule analysis

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
