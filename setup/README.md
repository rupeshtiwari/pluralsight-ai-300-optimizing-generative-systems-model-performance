# Set up the CPU Azure labs

[Course index](../README.md) · [First exercise](../module1/m1-c2/README.md)

You need Python/JSONL/RAG knowledge, an Azure subscription, and access to Azure AI Search, Microsoft Foundry and Azure ML. Training and serving run on Azure CPU compute; your laptop does not need a GPU. These sources have offline checks; Azure runtime proof is not included.

## Your Azure starting state

Use a dedicated lab resource group. Create or obtain these resources through your organization's normal approved Azure workflow before running the labs:

- One Azure AI Search **Free** service, with semantic ranker available on Free in a region marked with an explicit Free-tier semantic-support footnote in the [official region table](https://learn.microsoft.com/azure/search/search-region-support) and its free semantic allowance enabled. Set one index name beginning `ai300-`; all chunk variants and embedding fields share it. The engine reads the service SKU and rejects a paid tier.
- A Foundry Azure OpenAI endpoint and a deployment of **gpt-5.6-luna, version 2026-07-09**. Copy the deployment name, not just the model name. The engine checks the management-plane model/version before generation.
- An Azure ML workspace with its storage and registry, a CPU AmlCompute cluster (for example `Standard_D8s_v3`, subject to regional quota), minimum nodes **0**, maximum **1**, and idle scale-down **120 seconds**. CPU jobs have a two-hour timeout; completion is inspected rather than simulated.
- For module 3, quota for two `Standard_DS3_v2` managed online deployments and a dedicated endpoint beginning `ai300-`. An Azure Monitor action group is required for the final alert exercise.

Search is free within its limits. Foundry calls, CPU jobs, online endpoints, workspace storage and monitoring can incur charges. The small workload is not a promise of a fixed cost. Check current regional pricing and quota in your Azure portal. No setup script creates a subscription, resource group, Search service, Foundry deployment or CPU cluster.

## Install and authenticate

In a terminal, clone this repository, enter it and use Python **3.12.16**. Its Python.org release is source-only; install it through your approved Python distribution or version manager. Do not silently treat another patch release as the recorded environment.

```bash
git clone https://github.com/rupeshtiwari/pluralsight-ai-300-optimizing-generative-systems-model-performance.git
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-client.txt
python -m pip check
```

On Windows use Git Bash for the wrappers and `source .venv/Scripts/activate`. On macOS install `torch==2.14.1` from the normal PyPI index instead of the CPU index command. All model calls still use `device='cpu'` and FP32 serving.

Use your organization's supported `DefaultAzureCredential` identity: an existing Azure CLI login (`az login`), managed identity on an authorized Azure host, or a service principal supplied through `AZURE_TENANT_ID`, `AZURE_CLIENT_ID` and `AZURE_CLIENT_SECRET` in your terminal. Never put secrets in JSON or tracked files. The runtime does not open an interactive sign-in window. Search and Foundry keys are optional environment variables (`AZURE_SEARCH_KEY`, `AZURE_OPENAI_API_KEY`); management-plane reads still require the Azure identity.

Your identity needs Search index/query permissions plus service read, Foundry inference plus deployment read, Azure ML job/data/model/environment/endpoint permissions, and metric/alert permissions. Scope access to your lab resources. A 403 is a missing role or scope; do not make resources public to bypass it.

## Configure exact identities

```bash
cp config.example.json config.local.json
```

Open `config.local.json` in VS Code and replace each relevant `REPLACE` value. Use full Azure resource IDs from each resource's JSON view. Keep the single Search index name stable. Record resource names, environment IDs and model commits, never keys. The file is ignored by Git.

```bash
python -m ai300.setup freeze-models
python -m ai300.setup register-environments --image "YOUR_APPROVED_CPU_IMAGE@sha256:YOUR_DIGEST"
```

For `--image`, use Microsoft's CPU `azureml/openmpi4.1.0-ubuntu22.04` base image, listed in [AzureML-Containers](https://github.com/Azure/AzureML-Containers) and used for CPU managed deployments in [Microsoft's deployment guide](https://learn.microsoft.com/azure/machine-learning/how-to-deploy-managed-online-endpoints?view=azureml-api-2). Training and serving use separate conda environments on this CPU base; serving adds the pinned inference server. Availability is not proof that these two environments build successfully.

Resolve its current tag to an immutable registry digest without Docker:

```bash
python scripts/resolve_cpu_image.py --tag latest
```

Copy the complete printed URI into `--image` above after confirming it meets your workspace policy. The resolver only reads Microsoft's registry, rejects a missing digest, and does not register or deploy anything. Keep the printed digest with your setup evidence; do not record the mutable `latest` tag as the frozen image. These commands pin the approved model commits and register separate training/serving environments from [the environment definitions](../environments/). Registration is not proof that the environment builds. Check the first real job's environment-build log and retain its exact version.

Before the deployment demo, create the disposable baseline once:

```bash
python -m ai300.setup create-baseline
```

This downloads the exact Qwen base revision, registers it with its tokenizer and identity, creates the dedicated endpoint, deploys the baseline, and routes 100% to it. It is billable until deleted. It refuses to overwrite an existing endpoint and writes `evidence/setup/<run>/resources.json`. Endpoint basics are covered in **AI-300: Implementing Machine Learning Model Lifecycle and Operations**; here you use those basics to establish a versioned baseline for fine-tuned release decisions.

## Run and connect the exercises

From the repository root, each exercise has three conceptual step commands (the canary has four). Setup and cleanup sit outside those steps:

```bash
./module1/m1-c2/scripts/preflight_check.sh
./module1/m1-c2/scripts/lab-up.sh
./module1/m1-c2/scripts/lab-step.sh 1
./module1/m1-c2/scripts/lab-step.sh 2
./module1/m1-c2/scripts/lab-step.sh 3
./module1/m1-c2/scripts/lab-down.sh
```

`lab-up` prints the unique run folder. `.state/<demo>.json` points to that folder. Every attempted step has its own folder, `report.json` on success, `failure.json` on failure and `raw/` Azure responses. A completed step cannot be overwritten. Failed asynchronous inspection steps can be repeated after the actual Azure job/deployment finishes. Changing source/config during a run requires a new `lab-up`.

Later exercises name genuine retained dependencies in the `runs` object of `config.local.json`, before their `lab-up`. Example shape only:

```json
"runs": {
  "m2-demo2": "evidence/m2-demo2/YOUR_ACTUAL_RUN_FOLDER",
  "m2-demo3": "evidence/m2-demo3/YOUR_ACTUAL_RUN_FOLDER",
  "m2-demo4": "evidence/m2-demo4/YOUR_ACTUAL_RUN_FOLDER"
}
```

Copy actual paths from the prerequisite runs; never copy these placeholders. Required report hashes and steps are checked. When continuing after endpoint cleanup, restore the exact registered baseline and candidate without re-registering a model or replaying final test:

```bash
python -m ai300.setup restore-endpoint --from-run "evidence/m3-demo3/YOUR_COMPLETED_FINAL_TEST_RUN"
```

You can also restore from a completed `m3-demo2` deployment run before final test. The command reads the retained baseline/candidate model, environment, code and request-setting snapshots, recreates missing resources, restores 100/0 traffic and verifies both identities. It refuses unrelated or mismatching existing resources. Keep the original dependency run path; restoration does not create a replacement quality/test report. Source code alone does not establish cloud starting state.

## Troubleshooting and cleanup

| Observation | Action |
|---|---|
| `HOLD` and exit 2 before any Azure call | Complete configuration/dependencies. The offline check can run with `preflight_check.sh --offline`. |
| Job is Queued/Running | Open the printed Azure ML Studio URL. Check cluster quota/environment build; rerun the inspection step after Completed. |
| Training fails or generation is malformed | Read raw output and genuine job logs. Do not replace it with an expected answer. |
| Search results empty after indexing | Allow indexing to become queryable and rerun the failed step; inspect the exact `chunk_size` filter. |
| Manual review pending | Edit the generated `review.jsonl` in VS Code: ACCEPT/REJECT, reason and reviewer for every example. |
| Quality gate rejects a model | Retain baseline; use validation failures to revise data/training. Never loosen a frozen gate after seeing final-test results. |
| Monitor metrics missing | Inspect actual Azure Monitor time windows and wait for ingestion. No local latency substitution or fabricated zeroes. |
| No failed canary gate | Baseline is restored; failed-gate rollback proof remains unobserved. Do not invent a regression. |

Run the current exercise's `lab-down.sh` even after a failed step. It cancels this run's unfinished jobs, restores baseline traffic for a canary, deletes the course candidate where applicable, and deletes this run's alert. For this run's submitted jobs it checks cluster minimum nodes are zero; confirm the cluster scales down after its idle timeout.

For the end of an independent endpoint exercise, set `cleanup.delete_endpoint=true` **before lab-up** to remove the dedicated baseline and endpoint as well. `cleanup.delete_search_index=true` removes the course index when you are finished with retrieval. The default retains the baseline and index for immediate continuation; retained endpoints remain billable. The cleanup report lists retained model/data/environment versions and workspace storage. Verify resource removal and compute scale-down in the portal, then remove the dedicated resource group through your normal Azure process when all evidence is retained.

The final-test ledger under `.state/consumed-final-tests/` is part of the evidence. Preserve it with the reports. It is not disposable cache.

## Human support review before acceptance

`answer_support_proxy` is an automatic conservative reference-match check. It verifies normalized answer text and citations; valid paraphrases can receive zero. It cannot approve semantic quality. RAG variant/A/B reports, model validation and final-test reports create separate hash-bound review files. Open the exact response, supplied context and reference in VS Code and fill Boolean `correct` and `supported`, plus a factual reason and reviewer identity. Model and release gates use human correctness/support plus objective JSON-schema validity; exact-reference proxy mismatches remain diagnostic and cannot override a supported paraphrase. An unanswered review returns HOLD.

## Advance preparation and preflight modes

Before any live preflight, obtain resource IDs and your authorized login, confirm exact model/region/quota availability, choose cleanup retention, and complete the prerequisite human reviews listed in the demo page. These decisions cannot be inferred from a successful package install.

```bash
python -m ai300.setup plan
python -m ai300.setup prepare
# Add --include-baseline only when ready to create the billable dedicated endpoint.
./module1/m1-c2/scripts/preflight_check.sh --offline
./module1/m1-c2/scripts/preflight_check.sh --live
```

`plan` makes no network calls. `prepare` combines immutable model-commit resolution, CPU image-digest resolution and environment registration for your already supplied Azure resources. `--include-baseline` adds the real dedicated baseline deployment. It does not create your subscription, resource group, Search service, Foundry deployment, workspace, cluster, quota, roles or action group.

`--offline` validates original source-group data without credentials. With no flag, preflight checks local configuration and exact effective Python/package versions. `--live` additionally reads actual Azure resource/model/environment/dependency identities, baseline/candidate definitions and relevant monitoring setup. Its successful status is `READ_ONLY_PREREQUISITES_CHECKED`, with `runtime: NOT RUN` and `all_steps_pass: false`; read permission cannot prove write permission, inference, environment builds, quality gates or delayed telemetry. Only executing every numbered step on Azure can establish the corresponding runtime evidence.

All **11 complete demos require Azure**. Without Azure you can read/edit source, validate the data contract, run the labeled offline unit tests, inspect CPU job/scorer code and create a setup plan. Those activities are useful preparation and are never reported as a completed demo.

## Stopping an active command

The runner converts normal Ctrl+C, termination and its 30-minute deadline into a bounded recovery attempt. It allows up to ten additional minutes for owned Azure operations to restore baseline before forcing its child to stop. Heartbeats continue during recovery. A forced kill reports traffic/resource state as **UNKNOWN**; use Azure ML to restore baseline and run `lab-down.sh`. An outer automation must allow this recovery grace instead of killing the process group immediately. No local process exit is treated as proof of Azure recovery.

Only endpoints named `ai300-...` with `course=ai300` and `purpose=disposable-course-lab` tags can receive course mutations or test traffic. The deliberately strict rollback-test threshold cannot be applied to an ordinary configured endpoint.
