# Original Northstar support data

This fictional corpus was authored for this course. It contains no customer records. Twelve policy source groups divide into four training, four validation and four final-test groups. The 24 domain queries contain exact-identifier and paraphrase pairs. Four additional general-capability queries split between validation and final test.

`corpus.jsonl` contains policy text and immutable source IDs. `queries.jsonl` contains source relevance grades, a support span, required/forbidden answer terms and a reference JSON response. `embedding-pairs.jsonl` contains original reviewed positive pairs and hard negatives from training groups only.

Run `python -m ai300.cli --demo m1-demo1 check --offline` to validate group separation and support-span references. This checks data structure; it does not measure Azure retrieval or training.

Source groups, rather than individual paraphrases, determine splits. Synthetic generation consumes training sources only. Training jobs receive accepted training examples and validation labels; final-test assets remain separate. Validation selects checkpoints and request settings. The final-test ledger prevents the same dataset from being reused after its first deployed release evaluation.

Do not inspect final-test labels to tune prompts, weights or gates. If you revise anything after a failed final test, author new source groups and independently reviewed labels for a new untouched test set. Record its new hash; never delete the consumed-test ledger to make old data appear untouched.

The labeled answer checks are intentionally narrow: required facts, forbidden contradictions, JSON schema and source citations. They are not a general factuality judge. Manually read concrete failures and all synthetic examples before accepting them. Tiny repeated query sets cannot establish real-user benefit or robust general-capability preservation.

## Metric conventions

Retrieval uses **source-level** labels. `recall_at_k` counts distinct relevant policy source IDs among the first `k` returned chunks. `ndcg_at_k` deduplicates source IDs in their first-occurrence order within those same chunks, then uses graded source relevance; it does not fetch extra chunks to fill `k` distinct sources. `boundary_failure` means no retained top-k chunk contains the full labeled support span. These are not chunk-level relevance labels.

`answer_support_proxy` requires a normalized full reference-answer match and exactly the expected source citations. It is intentionally conservative and may reject correct paraphrases. Human review checks every claim against the exact supplied context and reference; it is mandatory for semantic acceptance in RAG/model/release evidence. Keep the automatic proxy and human judgment separate.
