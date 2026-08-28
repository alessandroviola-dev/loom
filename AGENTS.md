# LOOM — Pi Agent Protocol

Version: 3.46
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

A fully preregistered compound funnel may traverse internal stages without intermediate Git/pull only when question, outcomes, branches, gates, workload/fallback order, resource bounds and fail-closed behavior are frozen before execution.

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
25. a local candidate proven by evidence remains non-canonical until exact source review and commit/push.

External root: `<external-archive>/`

## Mission

**Big models. Small machines.** Build a practical local AI system on Apple M1/8GB, measuring not only whether large models can execute but whether they are useful relative to smaller local models and tool/skill-enhanced systems.

## Frozen Qwen3-30B-A3B research comparator

Canonical backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Production baseline commit:
`96958de` — persistent PACKED fd.

Exact-Q4/top-8 sustained benchmark:
`1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Validated backend SHA-256:
`6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

Settled speed mechanisms:
- expert-major physical I/O/runtime/canonicalization: ACCEPTED;
- routing sparsity: NO ACCEPTABLE GAIN;
- Q2/Q3 from deployed Q4: fidelity FAIL;
- DFlash: CLOSED;
- oracle K=4 speculative verifier ceiling: `1.792925 tok/s` median, NOT PROMISING for a real drafter.

Do not reopen these exact mechanisms absent a materially new hypothesis.

## Qwen3.8 readiness — BOTH PORTABLE, EXECUTION PARKED

`LOOM_QWEN38_PORTABILITY_READINESS_001 = QWEN38_BOTH_PORTABLE`.

Qwen3.8-27B static dense streaming:
- 64 layers;
- projected external weight traffic `13,702,468,608 B/token`;
- resident `1,587,312,640 B`;
- static portability PASS but naive decode is structurally much more bandwidth-heavy than current sparse 30B.

Qwen3.8-Flash-Next static streaming:
- 48 layers;
- 512 routed experts, top-10 + shared;
- projected external `3,858,155,864 B/token` baseline;
- native MTP metadata covered, runtime adapter not ready;
- ~105.434 GiB payload needs external storage.

Both remain research candidates; large downloads/execution are PARKED until after the practical 30B/8B/4B comparison unless explicitly reactivated.

## LOOM 30B Interactive Runtime v1 001 — FUNCTIONAL_SLOW

`LOOM_30B_INTERACTIVE_RUNTIME_V1_001 = LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`.

Result:
`research/architecture/loom-30b-interactive-runtime-v1-001-result.md`
Evidence:
`results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`

Accepted execution environment:
- `.venvs/stretch030-mlx0320-fix1/bin/python`;
- Python `3.13.0`;
- MLX `0.32.0`;
- mlx-lm `0.31.3`.

Local candidate:
`scripts/loom_30b_interactive_v1_001.py`

Candidate status: FUNCTIONALLY VALID BUT NOT YET CANONICAL.
Exact source review and Git persistence are required before calling it LOOM 30B v1.

Validated behavior:
- 16/16 semantic parity with canonical greedy path;
- live token streaming PASS, flush p95 `0.000075 s`;
- exact multi-turn KV/recurrent state reuse PASS;
- fixed 3-turn memory smoke PASS: `PRONTO`, `MEMORIZZATO`, `7319`;
- five-turn stability/memory PASS; turn-2 fact `ALFA-482` recovered on turn 5;
- zero SOURCE fallback;
- no persistent expert-payload cache;
- peak RSS `1,447,067,648 B` (~1.35 GiB);
- swap safe.

Long-form real-generation performance:
- TTFT `47.832 s`;
- decode-only `1.116 tok/s`;
- end-to-end `0.921 tok/s`;
- token-wall p50/p95 `0.869 / 1.276 s`.

READY failed only because TTFT exceeded the frozen `<=30 s` gate. Do not relax the gate post hoc.

## Current checkpoint — INTERACTIVE V1 CODE REVIEW / PERSISTENCE

Immediate task:
1. inspect exact local source of `scripts/loom_30b_interactive_v1_001.py` and SHA;
2. prove it contains only the validated PACKED-only interactive wrapper behavior and no hidden model/runtime changes;
3. if review PASS, stage/commit/push only the intended script;
4. user manually launches and chats with the committed runtime;
5. freeze it as **LOOM 30B v1 FUNCTIONAL_SLOW** practical comparator.

Do not begin the 8B/4B bake-off until the interactive candidate is reviewed/persisted and one manual session is completed.

## Strategic sequence after persistence/manual use

1. Matched practical **30B vs Qwen-family 8B vs 4B** bake-off on the same M1/8GB: quality, TTFT, tok/s, RAM/swap and time-to-correct-task.
2. Decide architecture role:
   - 30B primary/deep mode;
   - 8B/4B fast primary + 30B deep mode;
   - skill/tool/protocol-centric small-model system.
3. Apply `LOOM_HERETIC_TECHNICAL_PAPER.md` as design input to a separate behavioral/refusal-direction editing checkpoint on selected runtime(s), with quality-preservation gates. Measure refusal rate and steerability rather than claiming absolute `guardrail-free` status.
4. Maintain separate 30B R&D for materially new speed mechanisms: direct-from-higher-precision mixed-bit quantization, fused Metal expert kernels, vectored expert I/O and trace-driven bounded cache simulation.
5. A dedicated TTFT/prefill repair may be opened later if manual use shows latency is worth prioritizing; do not mix it into the current persistence step.

Current project priority: make the validated 30B runtime canonical and manually usable, then determine whether 30B, 8B or 4B gives the best practical system.