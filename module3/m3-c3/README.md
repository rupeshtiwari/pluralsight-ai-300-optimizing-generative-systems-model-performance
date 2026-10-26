# Demo: Deploy a versioned model to Azure ML

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 3, clip 3 · Reference placeholder: `m3-demo2-after`

## Your scenario

You are improving an Azure support assistant and need evidence that retrieval, model behavior or a release decision meets its stated goal. This demo covers the actions below; actual results are not available yet.

## Your learning goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2d** — Manage a fine-tuned model from development through production deployment

## Prerequisites and starting state

See the [course prerequisites](../../setup/README.md). Azure assets, data/model dependencies, credentials, quota, actual costs and reset procedures remain to be verified. The reference branch is a placeholder; it does not supply a completed environment.

## Planned steps

| Step | Planned action |
|---|---|
| [Step 1](#step-1) | Register a custom model asset containing the base-model revision, adapter, and tokenizer, linked to training data and validation evidence. |
| [Step 2](#step-2) | Deploy the candidate with versioned scoring code and an Azure ML CPU inference environment to an existing managed online endpoint at zero traffic. |
| [Step 3](#step-3) | Inspect the completed deployment and invoke it directly; verify the model identity and smoke-test responses while the baseline deployment continues serving. |

<a id="step-1"></a>

## Step 1

Register a custom model asset containing the base-model revision, adapter, and tokenizer, linked to training data and validation evidence.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Deploy the candidate with versioned scoring code and an Azure ML CPU inference environment to an existing managed online endpoint at zero traffic.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Inspect the completed deployment and invoke it directly; verify the model identity and smoke-test responses while the baseline deployment continues serving.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Registered custom model identity linked to training and validation evidence
- Candidate zero-traffic deployment with versioned scoring and CPU environment
- Direct candidate invocation and identity/smoke-test responses while baseline serves

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
