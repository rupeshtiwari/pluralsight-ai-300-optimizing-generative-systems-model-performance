# Demo: Train a LoRA adapter in Azure ML

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 2, clip 5 · Reference placeholder: `m2-demo3-after`

## Your scenario

You are improving an Azure support assistant and need evidence that retrieval, model behavior or a release decision meets its stated goal. This demo covers the actions below; actual results are not available yet.

## Your learning goals

- **TO2** — Implement advanced fine-tuning and model customization
- **EO2a** — Design and implement advanced fine-tuning methods
- **EO2c** — Monitor and optimize fine-tuned model performance

## Prerequisites and starting state

See the [course prerequisites](../../setup/README.md). Azure assets, data/model dependencies, credentials, quota, actual costs and reset procedures remain to be verified. The reference branch is a placeholder; it does not supply a completed environment.

## Planned steps

| Step | Planned action |
|---|---|
| [Step 1](#step-1) | Configure Qwen3-0.6B supervised training with Transformers and PEFT, choosing LoRA rank, target layers, learning rate, batch size, and response-only loss. |
| [Step 2](#step-2) | Submit the CPU command job and inspect a completed run with matching inputs; track training and validation loss in Azure ML through MLflow. |
| [Step 3](#step-3) | Diagnose divergence between training and validation loss, then inspect base and adapted validation responses for memorization and task errors before further tuning. |

<a id="step-1"></a>

## Step 1

Configure Qwen3-0.6B supervised training with Transformers and PEFT, choosing LoRA rank, target layers, learning rate, batch size, and response-only loss.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Submit the CPU command job and inspect a completed run with matching inputs; track training and validation loss in Azure ML through MLflow.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Diagnose divergence between training and validation loss, then inspect base and adapted validation responses for memorization and task errors before further tuning.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Qwen3 supervised LoRA configuration including response-only loss
- Genuine Azure ML completed CPU run and MLflow training/validation loss
- Base/adapted validation responses and diagnosed memorization or task errors

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
