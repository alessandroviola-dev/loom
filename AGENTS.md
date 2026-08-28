# LOOM — Pi Agent Protocol

Version: 3.47
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue or post-hoc gate relaxation;
3. comparison invalid if more than intended treatment factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. do not advance from stale canonical docs except inside a fully preregistered compound funnel;
8. required gate instrumentation must persist before evidence is accepted;
9. failed frozen methods are not silently modified/rerun under the same checkpoint;
10. control/API semantics affecting validity must be established locally;
11. Integration Readiness Protocol v1 is mandatory before integration coding/model forward;
12. producer/consumer compatibility must be proven mechanically before adapter coding;
13. static adapter dry-run with zero unresolved accesses and forbidden fallback must PASS before model forward;
14. benchmark artifacts are not implicitly promoted to production runtime artifacts;
15. metadata/provenance checks use deterministic scripts/JSON where possible;
16. settled mechanisms are not reopened absent regression/materially different hypothesis;
17. production regressions require a bounded preregistered repair;
18. validation-only metadata stays out of hot runtime when representable by a smaller contract;
19. accepted production code is canonical only after review and Git persistence;
20. quality-trading work freezes fidelity gates before candidate results;
21. oracle verifier ceilings are upper bounds only and never production speed;
22. large new-model downloads require metadata-only readiness first;
23. environment conflicts are reconciled against the exact accepted interpreter/venv before package changes;
24. user-facing runtime claims require real end-to-end generation evidence, not only token-like microbenchmarks;
25. a local candidate proven by evidence remains non-canonical until exact source review and commit/push;
26. production/user-facing Python must not depend on untracked research helper modules;
27. token streaming must use tokenizer-compatible stateful detokenization and stop/control tokens must not be emitted to the user.

External root: `<external-archive>/`

## Mission

**Big models. Small machines.** Build a practical local AI system on Apple M1/8GB and compare large-model utility against smaller skill/tool-enhanced local systems.

## Frozen Qwen3-30B-A3B research comparator

Canonical backend: `scripts/loom_30b_moe_expert_major_backend_001.py`.
Production baseline commit: `96958de`.
Validated backend SHA-256: `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.
Exact-Q4/top-8 sustained 3×32: `1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Settled speed mechanisms:
- expert-major accepted/canonical;
- routing sparsity no acceptable gain;
- Q2/Q3 from deployed Q4 fidelity fail;
- DFlash closed;
- exact K=4 oracle verifier ceiling `1.792925 tok/s`, not promising for a real drafter.

Do not reopen these exact mechanisms absent a materially new hypothesis.

## Qwen3.8 readiness — BOTH PORTABLE, EXECUTION PARKED

`QWEN38_BOTH_PORTABLE` from metadata-only readiness.
Qwen3.8-27B projected dense-streamed external traffic: `13,702,468,608 B/token`.
Qwen3.8-Flash-Next projected external baseline: `3,858,155,864 B/token`.
Both large executions remain parked until after practical 30B/8B/4B comparison unless explicitly reactivated.

## Interactive Runtime v1 001 — FUNCTIONAL_SLOW

`LOOM_30B_INTERACTIVE_RUNTIME_V1_001 = LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`.

Result: `research/architecture/loom-30b-interactive-runtime-v1-001-result.md`.
Evidence: `results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`.

Validated environment:
- `.venvs/stretch030-mlx0320-fix1/bin/python`;
- Python `3.13.0`;
- MLX `0.32.0`;
- mlx-lm `0.31.3`.

Functional evidence:
- 16-position semantic parity PASS;
- live streaming PASS;
- exact incremental KV/recurrent reuse PASS;
- 3-turn memory smoke PASS (`7319`);
- 5-turn stability PASS (`ALFA-482` recovered);
- peak RSS `1,447,067,648 B`;
- swap safe;
- zero SOURCE fallback/persistent expert cache.

Long-form: TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`, p50/p95 `0.869 / 1.276 s`.
Only frozen READY miss: TTFT >30 s.

## Exact code review — candidate not yet canonical

Reviewed uploaded candidate:
`scripts/loom_30b_interactive_v1_001.py`

Reviewed SHA-256:
`25607adf29b8bd045a938b6bd32afa2322d95ebaa5e156da5f86010a4101bcfa`.

Material findings:
1. imports `loom_30b_moe_first_greedy_generation_001` and `loom_30b_moe_shared_backbone_residency_001`, which are local research helpers not tracked on the current branch; committing only the CLI would not reproduce on a clean checkout;
2. streaming calls standalone `tokenizer.decode([token])` per generated token instead of mlx-lm's stateful streaming detokenizer, risking incomplete multi-token UTF-8/BPE rendering;
3. stop/EOS is decoded/emitted before the stop check, so a special stop marker can become visible;
4. next-turn boundary extraction scans the full re-tokenized transcript for the second-last hard-coded EOS and is fragile to special-token-looking content.

These findings do not invalidate the functional evidence; they block production canonicalization only.

## Current checkpoint — INTERACTIVE V1 CANONICALIZATION REPAIR 001

`LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_REPAIR_001`

Preregistration:
`research/architecture/loom-30b-interactive-v1-canonicalization-repair-001-preregistration.md`

Required repair:
- promote one minimal tracked runtime core containing only the exact validated helper functionality needed by the CLI;
- remove imports of untracked research helpers from production runtime;
- preserve canonical expert-major backend unchanged;
- use frozen mlx-lm `tokenizer.detokenizer` stateful streaming;
- test EOS before emission and never print stop/control markers;
- robustly derive canonical assistant-close/new-user/generation suffix without full-transcript EOS scanning;
- preserve original generated token IDs in KV history;
- startup-validate expected chat terminator against tokenizer stop semantics;
- re-run exact semantic parity/state reuse;
- add Unicode streaming equivalence and literal `<|im_end|>` boundary smoke;
- recursively prove all production Python imports are tracked/runtime-safe.

Expected intended production files after GO:
- `scripts/loom_30b_runtime_core_v1_001.py`;
- `scripts/loom_30b_interactive_v1_001.py`.

Pi must not commit/push. After GO, ChatGPT reviews exact diffs/SHAs and the user commits only approved files.

## Strategic sequence after GO

1. Manual real terminal conversation with canonical LOOM 30B v1.
2. Matched practical 30B vs Qwen-family 8B vs 4B bake-off: quality, TTFT, tok/s, RAM/swap, time-to-correct-task.
3. Decide roles: 30B deep/primary, small fast primary + 30B escalation, or skill/tool/protocol-centric small model.
4. Heretic-paper-informed behavioral/refusal editing only after runtime roles are selected, with quality-preservation gates.
5. Separate 30B speed R&D: higher-precision mixed-bit quantization, fused Metal expert kernels, vectored expert I/O, trace-driven bounded cache simulation, and later TTFT/prefill work if justified by manual use.

Project priority remains practical utility.