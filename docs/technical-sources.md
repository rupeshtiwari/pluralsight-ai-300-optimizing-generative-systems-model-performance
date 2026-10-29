# Technical sources and version status

Checked 2026-10-29. These primary sources support the implementation choices. Documentation and package availability do not establish that a subscription has quota or that a live workload passed.

| Contract | Primary source |
|---|---|
| Search REST 2026-04-01 | [Stable Search API versions](https://learn.microsoft.com/rest/api/searchservice/search-service-api-versions) |
| Single-vector score conversion | [Vector ranking](https://learn.microsoft.com/azure/search/vector-search-ranking) |
| RRF and separate semantic score | [Hybrid ranking](https://learn.microsoft.com/azure/search/hybrid-search-ranking) |
| Foundry model/version | [Models sold by Azure](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure) |
| Fixed nonreasoning generation | [Azure reasoning model parameters](https://learn.microsoft.com/azure/foundry/openai/how-to/reasoning) |
| Azure ML tracking | [Configure MLflow](https://learn.microsoft.com/azure/machine-learning/how-to-use-mlflow-configure-tracking?view=azureml-api-2) |
| Endpoint and deployment metric names | [Azure ML monitoring reference](https://learn.microsoft.com/azure/machine-learning/monitor-resource-reference?view=azureml-api-2) |
| Free semantic regions | [Region table, explicit Free-tier semantic support](https://learn.microsoft.com/azure/search/search-region-support) |
| CPU base image and patches | [Microsoft AzureML-Containers](https://github.com/Azure/AzureML-Containers) |
| CPU PyTorch wheels | [PyTorch prior releases](https://pytorch.org/get-started/previous-versions/) |
| Qwen model and nonthinking chat template | [Qwen3-0.6B model card](https://huggingface.co/Qwen/Qwen3-0.6B) |
| LoRA model loading | [PEFT package documentation](https://pypi.org/project/peft/0.21.2/) |
| Python 3.12.16 | [Python release](https://www.python.org/downloads/release/python-31216/) |

The prescribed versions are available on PyPI: azure-ai-ml 1.35.2, azure-identity 1.26.0, azure-search-documents 12.0.0, openai 3.37.0, torch 2.14.1, transformers 5.20.2, peft 0.21.2, accelerate 1.15.0, sentence-transformers 6.2.0, mlflow-skinny 3.15.0, azureml-mlflow 1.62.0.post6 and azureml-inference-server-http 1.5.1. The Azure ML MLflow bridge's package metadata caps mlflow-skinny at 3.15.0; the pin preserves that cap. The Linux CPU environment uses the published `2.14.1+cpu` wheel.

The full client requirements and separate CPU training/serving requirement sets resolved successfully with pip on Python 3.12.14 in the source-editing environment. Conda-forge package metadata also lists Python 3.12.16. Training pins azure-identity 1.26.0 explicitly to avoid a moving transitive identity dependency. That is dependency-resolution evidence, not an installed-package import test or the approved Python 3.12.16 runtime. Azure environment builds, training, serving and end-to-end integration still require live validation. No alternate model, GPU training or paid Search tier is substituted.

Model revisions and container images must be immutable commits/digests. `freeze-models` resolves the three approved model repositories to current commits and records them in your ignored local configuration. Do not use a moving `main` revision for recorded runs.
