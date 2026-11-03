# Original Northstar support data

This fictional corpus was authored for this course. It contains no customer records. Fourteen policy source groups divide into four training, six validation and four final-test groups. Fifteen source documents include both versions of the E17 policy. The 26 domain queries contain exact-identifier and paraphrase pairs. Four additional general-capability queries split between validation and final test.

`corpus.jsonl` contains policy text and immutable source IDs. `queries.jsonl` contains source relevance grades, a support span, required/forbidden answer terms and a reference JSON response. `embedding-pairs.jsonl` contains original reviewed positive pairs and hard negatives from training groups only.

Run `python -m ai300.cli --demo m1-demo1 check --offline` to validate group separation and support-span references. This checks data structure; it does not measure Azure retrieval or training.

Source groups, rather than individual paraphrases, determine splits. Synthetic generation consumes training sources only. Training jobs receive accepted training examples and validation labels; final-test assets remain separate. Validation selects checkpoints and request settings. The final-test ledger prevents the same dataset from being reused after its first deployed release evaluation.

Do not inspect final-test labels to tune prompts, weights or gates. If you revise anything after a failed final test, author new source groups and independently reviewed labels for a new untouched test set. Record its new hash; never delete the consumed-test ledger to make old data appear untouched.

The labeled answer checks are intentionally narrow: required facts, forbidden contradictions, JSON schema and source citations. They are not a general factuality judge. Manually read concrete failures and all synthetic examples before accepting them. Tiny repeated query sets cannot establish real-user benefit or robust general-capability preservation.

## Metric conventions

Retrieval uses **source-level** labels. `recall_at_k` counts distinct relevant policy source IDs among the first `k` returned chunks. `ndcg_at_k` deduplicates source IDs in their first-occurrence order within those same chunks, then uses graded source relevance; it does not fetch extra chunks to fill `k` distinct sources. `boundary_failure` means no retained top-k chunk contains the full labeled support span. These are not chunk-level relevance labels.

`answer_support_proxy` requires a normalized full reference-answer match and exactly the expected source citations. It is intentionally conservative and may reject correct paraphrases. Human review checks every claim against the exact supplied context and reference; it is mandatory for semantic acceptance in RAG/model/release evidence. Keep the automatic proxy and human judgment separate.

## Exact error and outdated policy fixture

`v-e17-v1` is the original fictional obsolete E17 policy (30 minutes); `v-e17-v2` is its current replacement (15 minutes unless access is restored). `v-e18-v1` is a different error requiring an owner to restore access. Both E17 versions belong to the same validation source group. Two E17 queries label only version 2 as relevant. These authored policies are source fixtures, not observed Azure outputs or real customer incidents. Existing NS-101 remains unchanged; its forbidden `30 minutes` term was never historical-policy evidence.

The original twelve single-version documents omit `is_current` and `error_code`: by this dataset contract they are current, with no modeled error code. Indexing explicitly maps them to `is_current=true`, an empty error code, and their declared version. New versioned error policies require explicit boolean `is_current`; each error code has exactly one current version. Current means the current version of that policy, never globally version 2.

The existing `configs/m1-demo1.json`, `m1-demo2.json` and `m1-demo3.json` declare `policy_filter: "all"`. This leaves obsolete documents eligible, so retrieval can be inspected without presupposing a failure. Setting it to `"current"` adds an Azure Search `is_current eq true` prefilter; it does not change keyword/vector/ranking settings or any CLI command. Compare separate complete runs with one mode changed, keeping all other settings fixed. Never edit source/config halfway through a retained run: source hashes deliberately reject stale evidence. Sweep reports identify the selected filter; retained results expose error code, policy version and current status. The filter cannot guarantee the right error or answer.

Reindex after this dataset/schema change. Existing evidence is historical, not proof for the new source. Offline tests validate schema, metadata, request filters and labels only. Whether Azure actually returns an obsolete policy, whether filtering improves results, and whether the generated answer preserves the exception all remain unmeasured until real runs and manual review. No successful comparison is fabricated.
