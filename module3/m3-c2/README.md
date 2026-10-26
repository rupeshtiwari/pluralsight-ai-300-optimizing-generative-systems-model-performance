# Demo: Evaluate fine-tuned candidates in Azure ML

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 3, clip 2 · Reference placeholder: `m3-demo1-after`

## Your scenario

You are improving an Azure support assistant and need evidence that retrieval, model behavior or a release decision meets its stated goal. This demo covers the actions below; actual results are not available yet.

## Your learning goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2c** — Monitor and optimize fine-tuned model performance

## Prerequisites and starting state

See the [course prerequisites](../../setup/README.md). Azure assets, data/model dependencies, credentials, quota, actual costs and reset procedures remain to be verified. The reference branch is a placeholder; it does not supply a completed environment.

## Planned steps

| Step | Planned action |
|---|---|
| [Step 1](#step-1) | Submit an Azure ML evaluation job for the base model and selected adapters using the same domain and general-capability validation questions and generation settings. |
| [Step 2](#step-2) | Inspect the completed job in MLflow, comparing task correctness, answer support, and schema validity by query type and reading concrete failures. |
| [Step 3](#step-3) | Select the candidate against the validation gates and retain the job, dataset, configuration, and per-example evidence. |

<a id="step-1"></a>

## Step 1

Submit an Azure ML evaluation job for the base model and selected adapters using the same domain and general-capability validation questions and generation settings.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Inspect the completed job in MLflow, comparing task correctness, answer support, and schema validity by query type and reading concrete failures.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Select the candidate against the validation gates and retain the job, dataset, configuration, and per-example evidence.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Base and adapter evaluation-job inputs and common generation settings
- Completed MLflow evaluation and per-query-type correctness/support/schema failures
- Validation-gate decision with job, dataset, configuration and per-example evidence

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
