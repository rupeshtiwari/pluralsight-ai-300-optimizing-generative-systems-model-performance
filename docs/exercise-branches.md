# Before and After Demo Branches

[Course index](../README.md) · [Full run guide](run-demos.md) · [Azure setup](../setup/README.md)

Main is the complete, ready-to-configure course project. Every demo has a before/after pair. Before is a genuine source starter: only that demo's orchestration function in `ai300/demos.py` is replaced with the action checklist and a `STARTER` stop. After contains the complete implementation, including every shared helper and earlier dependency. The canary starter omits `_canary_step`; its `canary_rollback` safety wrapper, traffic-restoration helper and CLI cleanup remain intact.

A source branch does not create Azure resources, training artifacts or a successful release. All live prerequisites, reviewed responses and dependency run folders in the learner page remain required. Branches share ignored local configuration and evidence; source edits invalidate matching hashes, and switching never resets consumed final-test history.

## Choose Your Demo

| Demo | Before: coding starter | After: completed source | Function to implement | Prior live runs |
|---|---|---|---|---|
| [m1-demo1](../module1/m1-c2/README.md) | `m1-demo1-before` | `m1-demo1-after` | `retrieval_chunks` | None; shared Azure setup still required |
| [m1-demo2](../module1/m1-c3/README.md) | `m1-demo2-before` | `m1-demo2-after` | `hybrid_search` | None; shared Azure setup still required |
| [m1-demo3](../module1/m1-c5/README.md) | `m1-demo3-before` | `m1-demo3-after` | `rag_ab` | None; shared Azure setup still required |
| [m2-demo1](../module2/m2-c2/README.md) | `m2-demo1-before` | `m2-demo1-after` | `embedding_train` | None; shared Azure setup still required |
| [m2-demo2](../module2/m2-c4/README.md) | `m2-demo2-before` | `m2-demo2-after` | `synthetic_data` | None; shared Azure setup still required |
| [m2-demo3](../module2/m2-c5/README.md) | `m2-demo3-before` | `m2-demo3-after` | `lora_train` | `m2-demo2` |
| [m2-demo4](../module2/m2-c6/README.md) | `m2-demo4-before` | `m2-demo4-after` | `lora_select` | `m2-demo3`, `m2-demo2` |
| [m3-demo1](../module3/m3-c2/README.md) | `m3-demo1-before` | `m3-demo1-after` | `model_evaluate` | `m2-demo4` |
| [m3-demo2](../module3/m3-c3/README.md) | `m3-demo2-before` | `m3-demo2-after` | `model_deploy` | `m3-demo1` |
| [m3-demo3](../module3/m3-c4/README.md) | `m3-demo3-before` | `m3-demo3-after` | `endpoint_test` | `m3-demo2` |
| [m3-demo4](../module3/m3-c5/README.md) | `m3-demo4-before` | `m3-demo4-after` | `_canary_step` | `m3-demo3` |

The prior-runs column identifies required evidence, not code omitted from the starter. Each exercise page explains the exact accepted/completed dependency reports and `runs` configuration.

## Start from Before

Commit your own edits before switching. Run `git status --short` first; stop and preserve any changes it lists. From a clean clone:

```bash
git fetch origin
git switch m1-demo1-before
python scripts/check_source.py
```

The starter check validates compilation, contracts, data splits, all eleven offline preflights and starter/cleanup guards. It explicitly reports that completed-solution tests are NOT RUN. Open `ai300/demos.py` in VS Code, find `retrieval_chunks`, and replace its placeholder with the implementation described by the three numbered learner steps. Keep function signatures, shared helpers and the evidence interfaces unchanged.

Compare with the solution without changing your work:

```bash
git diff HEAD origin/m1-demo1-after -- ai300/demos.py
```

To use the supplied solution, first commit your edits, then restore only the solution file:

```bash
git restore --source=origin/m1-demo1-after -- ai300/demos.py
python scripts/check_source.py
```

The restore replaces local edits to this file. The checker now runs the full completed-source test suite. A removed placeholder alone does not prove correct implementation; the full tests and actual live steps remain required.

## Run Complete Source from Main or After

From a clean working tree:

```bash
git switch main
git pull --ff-only origin main
# Or: git switch m1-demo1-after
python scripts/check_source.py
```

Complete the shared setup and local configuration, then run:

```bash
./module1/m1-c2/scripts/preflight_check.sh --live
./module1/m1-c2/scripts/lab-up.sh
./module1/m1-c2/scripts/lab-step.sh 1
./module1/m1-c2/scripts/lab-step.sh 2
./module1/m1-c2/scripts/lab-step.sh 3
./module1/m1-c2/scripts/lab-down.sh
```

Use the exact folder and three/four steps from the selected learner page. Before and after use the same wrappers; no private repository is required. Cleanup remains available even with unfinished source. Keep prerequisite artifacts/resources until their dependent demos finish.

## Preserve Dependency Evidence

The evidence manifest conservatively hashes the complete engine and source set, including `ai300/demos.py`. A custom implementation or even a source-text edit changes that identity and makes earlier dependency runs stale. To reuse retained prerequisite proof, use main/after source or restore the exact after file before starting each live demo; completed sources are identical across those references. If you keep a custom implementation, rerun the required prerequisite chain under that exact unchanged source tree and update `config.local.json` → `runs`. Follow the prior-runs column recursively. Never edit a manifest to bypass a stale-source error or reuse a consumed final test for tuning.

## Maintaining the Branches

Merge updated main into each existing branch normally and preserve its exercise state. Never reset a before branch to main or fill its placeholder merely to make solution tests pass. Each `exercise-state.json` records its demo, omitted function, reviewed main SHA and completed-function hash. Main/after omit this starter-state file. `scripts/exercise_branches.py` prepares an offline starter package from an exact source commit; it does not push branches or contact Azure.

Main and after share the full solution. Different before branches omit different functions; they are not eleven aliases for main. Hosted source CI runs on main; starter/source checks are also runnable locally and through the existing manual workflow. No source check establishes Azure runtime, model quality or recorded-media readiness.
