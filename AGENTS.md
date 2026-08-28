# LOOM — Pi Agent Protocol

Version: 3.48
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
24. user-facing runtime claims require real end-to-end generation evidence;
25. a local candidate proven by evidence remains non-canonical until exact source review and commit/push;
26. production/user-facing Python must not depend on untracked research helper modules;
27. token streaming must use tokenizer-compatible stateful detokenization and stop/control tokens must not be emitted.

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

Validated environment: `.venvs/stretch030-mlx0320-fix1/bin/python`, Python `3.13.0`, MLX `0.32.0`, mlx-lm `0.31.3`.

Functional evidence:
- 16-position semantic parity PASS;
- exact incremental state reuse PASS;
- 3-turn/5-turn memory stability PASS;
- zero SOURCE fallback/persistent expert cache;
- long-form TTFT `47.832 s`;
- decode `1.116 tok/s`;
- end-to-end `0.921 tok/s`;
- peak RSS `1,447,067,648 B`.

Only frozen READY miss: TTFT >30 s. Do not relax this historical threshold.

## Canonicalization Repair 001 — GO

`LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_REPAIR_001 = LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_GO`.

Result:
`research/architecture/loom-30b-interactive-v1-canonicalization-repair-001-result.md`
Evidence:
`results-local/research/30b-interactive-v1-canonicalization-repair-001/20260828T131045Z/`

Frozen original reviewed candidate SHA verified:
`25607adf29b8bd045a938b6bd32afa2322d95ebaa5e156da5f86010a4101bcfa`.

Repair produced only two intended local files:
- `scripts/loom_30b_runtime_core_v1_001.py` SHA-256 `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` SHA-256 `08e84d1b19afdd4bad757db29d0d804783a35ee41db17696c14c56c8913488cb`.

Gates PASS:
- production dependency audit;
- canonical backend unchanged at SHA `6bb4...`;
- 16-position IDs/routing/float32-logit SHA parity;
- exact incremental state reuse/no full re-prefill;
- Unicode stateful streaming equivalence;
- EOS/control marker suppressed before emission;
- literal `<|im_end|>` user-content boundary smoke;
- frozen `7319` memory smoke;
- PACKED-only, SOURCE fallback 0, no persistent expert cache, deterministic fd close.

Bounded regression generation: `1.449028 tok/s`, TTFT `18.288247 s`, 5 output tokens under a 32-token bound. This does not replace the historical long-form metrics.

Observed system swap during the bounded repair run was `1471.06 MiB`; no critical memory pressure. The repair preregistration imposed no new swap threshold, so this does not override historical v1 safety evidence.

## Current checkpoint — FINAL SOURCE REVIEW / PERSISTENCE

The repair GO authorizes review, not automatic canonical status.

Before commit:
1. inspect the exact local contents of both reported files;
2. verify both SHAs exactly;
3. verify canonical backend has zero diff;
4. verify no unintended tracked/staged files;
5. stage only the two approved runtime files;
6. `git diff --cached --check`;
7. commit/push;
8. verify remote commit/content.

Pi must not do Git operations. User/ChatGPT own persistence.

After persistence:
- user launches committed CLI and conducts a real free-form multi-turn conversation;
- if acceptable, freeze **LOOM 30B v1 FUNCTIONAL_SLOW** as the large practical comparator;
- then run matched Qwen-family 30B vs 8B vs 4B bake-off.

## Strategic sequence after manual v1

1. Practical 30B vs 8B vs 4B: TTFT, tok/s, RAM/swap, time-to-correct-task, fixed intelligence tasks.
2. Decide 30B deep/primary vs small fast primary + 30B escalation vs skill/tool/protocol-centric small model.
3. Use `LOOM_HERETIC_TECHNICAL_PAPER.md` only after role selection, with frozen refusal/steerability and capability-preservation gates.
4. Separate R&D may study higher-precision mixed-bit quantization, fused Metal expert kernels, vectored expert I/O, trace-driven bounded caches and later TTFT/prefill optimization.

Project priority remains practical utility.