# Demo: Monitor Azure traffic and verify rollback

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 3, clip 5 · Reference placeholder: `m3-demo4-after`

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
| [Step 1](#step-1) | Configure an Azure Monitor alert on Request Latency P95; inspect latency by deployment, Requests Per Minute by deployment and status-code class, and each deployment’s CPU and memory utilization. |
| [Step 2](#step-2) | Allocate 90 percent of managed endpoint traffic to the baseline and 10 percent to the candidate; send labeled test traffic and retain deployment identities in the evidence. |
| [Step 3](#step-3) | Inspect a failed operational or labeled-quality gate and stop promotion; distinguish the test workload from real production-user outcomes. |
| [Step 4](#step-4) | Restore 100 percent traffic to the baseline, then verify the routed model identity, responses, and recovered operational behavior. |

<a id="step-1"></a>

## Step 1

Configure an Azure Monitor alert on Request Latency P95; inspect latency by deployment, Requests Per Minute by deployment and status-code class, and each deployment’s CPU and memory utilization.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Allocate 90 percent of managed endpoint traffic to the baseline and 10 percent to the candidate; send labeled test traffic and retain deployment identities in the evidence.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Inspect a failed operational or labeled-quality gate and stop promotion; distinguish the test workload from real production-user outcomes.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-4"></a>

## Step 4

Restore 100 percent traffic to the baseline, then verify the routed model identity, responses, and recovered operational behavior.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Latency, request/status-class, CPU/memory metrics and Request Latency P95 alert
- 90/10 traffic configuration and labeled test responses with deployment identities
- Failed operational or labeled-quality gate and stopped promotion
- 100/0 restored traffic with routed identity, response and recovery checks

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
