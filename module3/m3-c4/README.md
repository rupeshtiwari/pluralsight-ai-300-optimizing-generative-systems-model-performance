# Demo: Optimize and test the Azure model endpoint

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 3, clip 4 · Reference placeholder: `m3-demo3-after`

## Your scenario

You are improving an Azure support assistant and need evidence that retrieval, model behavior or a release decision meets its stated goal. This demo covers the actions below; actual results are not available yet.

## Your learning goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2c** — Monitor and optimize fine-tuned model performance
- **EO2d** — Manage a fine-tuned model from development through production deployment

## Prerequisites and starting state

See the [course prerequisites](../../setup/README.md). Azure assets, data/model dependencies, credentials, quota, actual costs and reset procedures remain to be verified. The reference branch is a placeholder; it does not supply a completed environment.

## Planned steps

| Step | Planned action |
|---|---|
| [Step 1](#step-1) | Benchmark the candidate deployment directly with a fixed validation workload; compare output-length limits using latency, output tokens, and answer quality. |
| [Step 2](#step-2) | Freeze the selected model, environment, and request settings, then run the untouched domain and general-capability test set against that deployment. |
| [Step 3](#step-3) | Retain the final test report and release configuration with the model version; reject a failed gate and require a new untouched test set after further tuning. |

<a id="step-1"></a>

## Step 1

Benchmark the candidate deployment directly with a fixed validation workload; compare output-length limits using latency, output tokens, and answer quality.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Freeze the selected model, environment, and request settings, then run the untouched domain and general-capability test set against that deployment.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Retain the final test report and release configuration with the model version; reject a failed gate and require a new untouched test set after further tuning.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Fixed validation benchmark across output-length limits
- Frozen candidate and inference settings with untouched final-test results
- Retained release configuration/report and gate decision

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
