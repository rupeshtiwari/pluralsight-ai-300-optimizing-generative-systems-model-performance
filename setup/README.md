# Course prerequisites

> **Scaffold only.** Setup is NOT IMPLEMENTED and no Azure readiness has been verified.

The course expects:

- Python, JSONL, embeddings, RAG, evaluation, and training, validation, and test splits
- Familiarity with Azure AI Search, Microsoft Foundry, and Azure Machine Learning
- An Azure subscription with permissions for Search, Foundry inference, Azure ML jobs, assets, endpoints, and Azure Monitor alerts
- Semantic ranker in a supported region, Foundry model access, and CPU compute and managed endpoint quota
- A macOS, Windows, or Linux Python client and browser; Azure hosts training and serving

## Implementation still required

The completed setup must check the actual client and Azure environments, permissions, service/model availability, regional quotas, configuration and bounded cost/cleanup behavior. Exact install commands and supported package versions are pending verification.

No credentials, subscriptions, resource names or environment secrets are committed here. The entrypoint stubs perform no Azure operations. Do not provision infrastructure from this scaffold.

## Expected cost model

The course plans to use Azure AI Search Free tier where available. Foundry generation, Azure ML compute/endpoints, storage and monitoring may incur charges. Availability, quota, pricing and cleanup steps must be checked for the chosen subscription and region before the real labs run.
