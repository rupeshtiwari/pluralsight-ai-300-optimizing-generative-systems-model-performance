# AI-300: Optimizing Generative AI Systems and Model Performance

> **Scaffold only.** Content and commands still require implementation and validation.

Better answers require better evidence and measured tuning. This course will teach you to optimize Azure RAG retrieval, adapt embeddings, fine-tune models, and use quality and performance evidence to deploy, monitor, and roll back model versions.

> **Authorization and scope.** Scaffold only: the planned Azure labs are not implemented or validated. No Azure resources are provisioned by this repository foundation.

## Who this is for

**Level:** Intermediate

AI engineers and machine learning engineers who already build RAG applications in Azure and need to improve retrieval, customize model behavior, and make evidence-based release decisions for the AI-300 certification path.

**You should already know:**

- Python, JSONL, embeddings, RAG, evaluation, and training, validation, and test splits
- Familiarity with Azure AI Search, Microsoft Foundry, and Azure Machine Learning
- An Azure subscription with permissions for Search, Foundry inference, Azure ML jobs, assets, endpoints, and Azure Monitor alerts
- Semantic ranker in a supported region, Foundry model access, and CPU compute and managed endpoint quota
- A macOS, Windows, or Linux Python client and browser; Azure hosts training and serving

## Learning objectives

- **TO1**, Optimize retrieval-augmented generation (RAG) performance and accuracy
  - **EO1a**, Optimize retrieval performance by tuning similarity thresholds, chunk sizes, and retrieval strategies
  - **EO1b**, Select and fine-tune embedding models for domain-specific use cases and accuracy improvements
  - **EO1c**, Implement and optimize hybrid search approaches combining semantic and keyword-based retrieval
  - **EO1d**, Evaluate and improve RAG system performance by using relevance metrics and A/B testing frameworks
- **TO2**, Implement advanced fine-tuning and model customization
  - **EO2a**, Design and implement advanced fine-tuning methods
  - **EO2b**, Create and manage synthetic data for fine-tuning
  - **EO2c**, Monitor and optimize fine-tuned model performance
  - **EO2d**, Manage a fine-tuned model from development through production deployment

## Set up your machine (once)

Follow [setup/README.md](setup/README.md).

## Labs

The eleven planned demos are unimplemented. Each folder contains a learner-facing action outline and four entrypoint stubs. Every stub prints `NOT IMPLEMENTED` and exits with status 3; no stub provisions, calls or cleans up Azure resources.

| Planned demo | Module · clip | Folder | Reference placeholder |
|---|---|---|---|
| [Demo: Tune chunks and similarity cutoffs in Azure AI Search](module1/m1-c2/README.md) | 1 · 2 | `module1/m1-c2` | `m1-demo1-after` |
| [Demo: Run hybrid search and semantic reranking in Azure](module1/m1-c3/README.md) | 1 · 3 | `module1/m1-c3` | `m1-demo2-after` |
| [Demo: Evaluate RAG variants with Azure services](module1/m1-c5/README.md) | 1 · 5 | `module1/m1-c5` | `m1-demo3-after` |
| [Demo: Fine-tune domain embeddings in Azure ML](module2/m2-c2/README.md) | 2 · 2 | `module2/m2-c2` | `m2-demo1-after` |
| [Demo: Generate and version synthetic data with Foundry](module2/m2-c4/README.md) | 2 · 4 | `module2/m2-c4` | `m2-demo2-after` |
| [Demo: Train a LoRA adapter in Azure ML](module2/m2-c5/README.md) | 2 · 5 | `module2/m2-c5` | `m2-demo3-after` |
| [Demo: Tune LoRA rank and select a checkpoint in Azure ML](module2/m2-c6/README.md) | 2 · 6 | `module2/m2-c6` | `m2-demo4-after` |
| [Demo: Evaluate fine-tuned candidates in Azure ML](module3/m3-c2/README.md) | 3 · 2 | `module3/m3-c2` | `m3-demo1-after` |
| [Demo: Deploy a versioned model to Azure ML](module3/m3-c3/README.md) | 3 · 3 | `module3/m3-c3` | `m3-demo2-after` |
| [Demo: Optimize and test the Azure model endpoint](module3/m3-c4/README.md) | 3 · 4 | `module3/m3-c4` | `m3-demo3-after` |
| [Demo: Monitor Azure traffic and verify rollback](module3/m3-c5/README.md) | 3 · 5 | `module3/m3-c5` | `m3-demo4-after` |

## How the branches work

`main` is the shared foundation. All eleven `m<module>-demo<n>-after` branches are scaffold placeholders with the same foundation content. The `after` suffix reserves the future operational reference state; it does not mean the lab is complete.

The outline defines operational demonstrations without an approved source-file authoring contract, so this scaffold uses one reference branch per demo. Each lab's real starting environment and prerequisites must be implemented and verified before learner use.

## Repository layout

```text
setup/                    one-time machine setup
module<M>/m<M>-c<clip>/   one folder per demo: README + scripts
course-contract.json      objectives, demos, branches and commands (machine-readable)
```
