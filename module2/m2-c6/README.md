# Demo: Tune LoRA rank and select a checkpoint in Azure ML

> **Scaffold only — NOT IMPLEMENTED.** This page preserves the planned learner actions. It is not yet a runnable exercise.

Module 2, clip 6 · Reference placeholder: `m2-demo4-after`

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
| [Step 1](#step-1) | Configure a second CPU command job with a different LoRA rank and learning rate; keep the base model, data splits, seed, target layers, and training budget fixed. |
| [Step 2](#step-2) | Compare both genuine completed runs in MLflow using validation loss, elapsed time, and task outputs; interpret the combined configuration change rather than attributing the result to rank alone. |
| [Step 3](#step-3) | Select a checkpoint using validation quality and CPU cost, then save its adapter with the exact base-model revision, tokenizer, data, and environment versions. |

<a id="step-1"></a>

## Step 1

Configure a second CPU command job with a different LoRA rank and learning rate; keep the base model, data splits, seed, target layers, and training budget fixed.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-2"></a>

## Step 2

Compare both genuine completed runs in MLflow using validation loss, elapsed time, and task outputs; interpret the combined configuration change rather than attributing the result to rank alone.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

<a id="step-3"></a>

## Step 3

Select a checkpoint using validation quality and CPU cost, then save its adapter with the exact base-model revision, tokenizer, data, and environment versions.

**Implementation status:** NOT IMPLEMENTED. Exact learner commands and verified expected output will be added with the lab.

## Evidence to inspect when implemented

- Second CPU training configuration with declared controlled factors
- Genuine completed-run comparison including validation loss, elapsed time and task outputs
- Selected adapter/checkpoint with exact base revision, tokenizer, data and environment identities

These are required observations, not results already collected. The implementation must show expected and observed values, their limits and the decision they support.

## Cleanup

Cleanup is NOT IMPLEMENTED. The scaffold creates no Azure resources. The completed exercise must retain needed evidence, delete its managed endpoint deployments and endpoints as appropriate, stop idle compute, and identify any retained billable resources. Until then, do not treat the cleanup stub as a resource-deletion command.
