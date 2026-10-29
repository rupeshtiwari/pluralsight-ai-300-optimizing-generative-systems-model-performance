# Demo: Run hybrid search and semantic reranking in Azure

[Previous: Tune chunks and similarity cutoffs in Azure AI Search](../m1-c2/README.md) · [Course index](../../README.md) · [Next: Evaluate RAG variants with Azure services](../m1-c5/README.md)

Module 1, clip 3 · Intermediate · Course video: pending publication.

Source implementation is available. Actual Azure runtime has not been run in the source-editing environment; all values below are expected field contracts, not precollected results.

## Your Scenario

Your assistant finds paraphrases but misses an exact policy identifier. Compare BM25, vector retrieval, fusion and semantic reranking on identical labels.

Your success condition is a retained real Azure report for every step, including any rejected gate or missing evidence. A valid rejection is a decision; it is not a successful deployment or release.

## Your Learning Goals

- **TO1** — Optimize retrieval-augmented generation (RAG) performance and accuracy
- **EO1c** — Implement and optimize hybrid search approaches combining semantic and keyword-based retrieval

## Start Your Lab

Complete [one-time setup](../../setup/README.md). Open this repository in VS Code with an integrated terminal. All code and original source labels are supplied; your work is to configure the named controls, run the real operation and interpret its evidence.

This exercise has no earlier demo dependency. Its own setup establishes the index or job from the supplied corpus and labels, using your configured Azure resources.

From the parent folder containing your clone, use the following setup. Commit or preserve your own changes before switching branches; do not discard them.

```bash
cd "pluralsight-ai-300-optimizing-generative-systems-model-performance"
git switch m1-demo2-after
source .venv/bin/activate
./module1/m1-c3/scripts/preflight_check.sh
./module1/m1-c3/scripts/lab-up.sh
```

Read [`configs/m1-demo2.json`](../../configs/m1-demo2.json) and [`ai300/azure.py`](../../ai300/azure.py), [`data/queries.jsonl`](../../data/queries.jsonl). The shared implementation is [`hybrid_search`](../../ai300/demos.py). Save configuration edits before `lab-up`; source/config changes invalidate an active run. The approved chunk-size list, semantic candidate depth 50, required manual review and zero-traffic deployment are checked contract constants where applicable; edits that violate them return HOLD. Chunk overlap is consumed by the tokenizer loop, while the named sweep settings are visible in the demo function.

`lab-up` prints your unique `evidence/m1-demo2/<UTC-uuid>/` folder. It initializes evidence; it does not claim Azure success. Keep the same terminal at the repository root for all steps. On Windows Git Bash, activate with `source .venv/Scripts/activate` instead of `.venv/bin/activate`.

## Your Three Steps

| Step | Action |
|---|---|
| [1](#step-1) | Send text and vector queries together to Azure AI Search; compare its reciprocal rank fusion results with separate keyword and vector searches. |
| [2](#step-2) | Vary vector weight and candidate depth, then enable semantic reranking with 50 vector candidates and inspect search and reranker scores separately. |
| [3](#step-3) | Compare exact identifiers and paraphrased questions on the same validation set; keep relevance gains without hiding query-type regressions. |


<a id="step-1"></a>

### Step 1: Send text and vector queries together to Azure AI Search; compare its reciprocal rank fusion results with separate keyword and vector searches.

**Learning Goal:** Send text and vector queries together to Azure AI Search; compare its reciprocal rank fusion results with separate keyword and vector searches.

**Demo Workspace:** VS Code, repository root; inspect `hybrid_search` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module1/m1-c3/scripts/lab-step.sh 1
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-1-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `rows`, `variants`, `@search.score`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Keyword and vector score magnitudes are not directly comparable. Azure fuses ranks for the hybrid query; it does not average cosine and BM25 scores.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-2"></a>

### Step 2: Vary vector weight and candidate depth, then enable semantic reranking with 50 vector candidates and inspect search and reranker scores separately.

**Learning Goal:** Vary vector weight and candidate depth, then enable semantic reranking with 50 vector candidates and inspect search and reranker scores separately.

**Demo Workspace:** VS Code, repository root; inspect `hybrid_search` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module1/m1-c3/scripts/lab-step.sh 2
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-2-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `settings`, `@search.score`, `@search.rerankerScore`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Weight and depth change candidate contributions. Semantic requests up to 50 vector candidates; the tiny filtered corpus may return fewer and emits a distinct reranker score. An absent reranker field is a failure, not a zero.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

<a id="step-3"></a>

### Step 3: Compare exact identifiers and paraphrased questions on the same validation set; keep relevance gains without hiding query-type regressions.

**Learning Goal:** Compare exact identifiers and paraphrased questions on the same validation set; keep relevance gains without hiding query-type regressions.

**Demo Workspace:** VS Code, repository root; inspect `hybrid_search` in `ai300/demos.py` and the step's configuration before running.

**Run Command:**

```bash
./module1/m1-c3/scripts/lab-step.sh 3
```

**Result Location:** The same terminal prints observed JSON and the exact report path. Open `step-3-<attempt>/report.json` in the run folder, with `raw/` beside it. A failed attempt instead retains `failure.json`; do not treat its absence of a report as success.

**Expected Results:** `query_type_regressions`, `score_types`, `example_rows`. These are field names; counts, timings, IDs, quality values and gate decisions come from your actual run.

**Interpret Results:** Inspect exact identifiers separately from paraphrases. Retain a gain only after reading any regression; an empty regression list means none was observed.

**If it fails:** Read the retained error and raw response. Fix missing prerequisites or wait for the named asynchronous operation; repeat only the failed step. Never replace output with a fixture or expected success. A quality rejection requires the corrective action in the report.

## What You Achieved

Your assistant finds paraphrases but misses an exact policy identifier. Compare BM25, vector retrieval, fusion and semantic reranking on identical labels. You now have the actual inputs, response fields and decision record needed to explain that change. Verify every numbered report includes the current run ID and inspect at least one underlying raw response or genuine completed job. The terminal report does not replace Azure portal/Studio inspection.

## Finish Your Lab

```bash
./module1/m1-c3/scripts/lab-down.sh
```

The [cleanup contract](../../setup/README.md#troubleshooting-and-cleanup) explains retained assets and billable resources. For a fully independent endpoint exercise, choose `cleanup.delete_endpoint=true` before `lab-up`; then use `restore-endpoint --from-run` for exact version restoration before continuation. Preserve evidence and the final-test consumption ledger. Verify cluster scale-down and resource removal in Azure.

Compare your source with this exercise's `m1-demo2-after` reference using `git diff m1-demo2-after -- ai300 jobs serving configs data`; this does not move your checkout or overwrite your work. A matching tree does not prove matching cloud state.

[Previous: Tune chunks and similarity cutoffs in Azure AI Search](../m1-c2/README.md) · [Course index](../../README.md) · [Next: Evaluate RAG variants with Azure services](../m1-c5/README.md)
