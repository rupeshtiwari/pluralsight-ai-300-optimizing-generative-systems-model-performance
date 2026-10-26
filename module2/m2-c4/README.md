# Demo: Generate and version synthetic data with Foundry

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 2, clip 4 · Reference placeholder: `m2-demo2-after`

## Your scenario

You are improving an Azure support assistant and need evidence that retrieval, model behavior or a release decision meets its stated goal. This demo covers the actions below; actual results are not available yet.

## Your learning goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2b** — Create and manage synthetic data for fine-tuning

## Prerequisites and starting state

See the [course prerequisites](../../setup/README.md). Azure assets, data/model dependencies, credentials, quota, actual costs and reset procedures remain to be verified. The reference branch is a placeholder; it does not supply a completed environment.

## Planned steps

| Step | Planned action |
|---|---|
| [Step 1](#step-1) | Call the gpt-5.6-luna deployment in Microsoft Foundry to generate support-response examples from training-source documents, retaining source, prompt, and generator versions. |
| [Step 2](#step-2) | Check JSONL structure, duplicate prompts, source references, and split leakage with Python; manually accept or reject examples by checking their claims against the source. |
| [Step 3](#step-3) | Register accepted examples, rejection reasons, hashes, and separate validation and test files as versioned Azure ML data assets. |

<a id="step-1"></a>

## Step 1

Call the gpt-5.6-luna deployment in Microsoft Foundry to generate support-response examples from training-source documents, retaining source, prompt, and generator versions.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Check JSONL structure, duplicate prompts, source references, and split leakage with Python; manually accept or reject examples by checking their claims against the source.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Register accepted examples, rejection reasons, hashes, and separate validation and test files as versioned Azure ML data assets.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Foundry examples with source, prompt and generator identities
- JSONL, duplicate, source-reference and split-leakage checks with manual acceptance/rejection
- Versioned Azure ML accepted-data, rejection, hash, validation and test assets

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
