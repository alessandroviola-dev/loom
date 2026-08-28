# LOOM — Pi Agent Protocol

Version: 3.45
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
24. user-facing runtime claims require real end-to-end generation evidence, not only token-like microbenchmarks.

External root: `<external-archive>/`

## Mission

**Big models. Small machines.** Build a practical local AI system on Apple M1/8GB, measuring not only whether large models can execute but whether they are useful relative to smaller local models and tool/skill-enhanced systems.

## Frozen Qwen3-30B-A3B production comparator

Canonical backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Production baseline commit:
`96958de` — persistent PACKED fd.

Exact-Q4/top-8 sustained benchmark:
`1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Validated backend SHA-256:
`6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

Settled mechanisms:
- expert-major physical I/O/runtime/canonicalization: ACCEPTED;
- routing sparsity: NO ACCEPTABLE GAIN;
- Q2/Q3 from deployed Q4: fidelity FAIL;
- DFlash: CLOSED;
- oracle K=4 speculative verifier ceiling: `1.792925 tok/s` median, NOT PROMISING for a real drafter.

Do not reopen these exact mechanisms absent a materially new hypothesis.

## Qwen3.8 readiness — BOTH PORTABLE, EXECUTION PARKED

`LOOM_QWEN38_PORTABILITY_READINESS_001 = QWEN38_BOTH_PORTABLE`.

Result:
`research/architecture/loom-qwen38-portability-readiness-001-result.md`
Evidence:
`results-local/research/qwen38-portability-readiness-001/20260828T112000Z/`

Qwen3.8-27B static dense streaming:
- 64 layers;
- projected external weight traffic `13,702,468,608 B/token`;
- resident `1,587,312,640 B`;
- static portability PASS but naive decode is structurally much more bandwidth-heavy than current sparse 30B.

Qwen3.8-Flash-Next static streaming:
- 48 layers;
- 512 routed experts, top-10 + shared;
- routed expert `3,072,000 B`;
- projected external `3,858,155,864 B/token` baseline;
- native MTP metadata covered, runtime adapter not ready;
- ~105.434 GiB payload needs external storage.

Both remain research candidates, but large downloads/execution are PARKED until the current 30B is productized and compared against smaller local baselines. Do not execute the previously preregistered 27B first-token checkpoint unless ChatGPT/user explicitly reactivates it.

## Current checkpoint — LOOM 30B INTERACTIVE RUNTIME V1 001

`LOOM_30B_INTERACTIVE_RUNTIME_V1_001`

Preregistration:
`research/architecture/loom-30b-interactive-runtime-v1-001-preregistration.md`

Purpose: convert the canonical benchmark/runtime into a real local text-chat CLI without changing model semantics.

Required v1 capabilities:
- terminal chat;
- canonical Qwen chat-template semantics;
- greedy output streaming token-by-token;
- configurable max tokens;
- canonical EOS/stop;
- multi-turn conversation;
- exact KV/recurrent state reuse when current architecture permits it;
- `/reset` and `/exit`;
- clean teardown and persistent PACKED fd close;
- zero SOURCE fallback and zero persistent expert payload cache.

Frozen validation:
1. recover exact accepted Python/MLX environment;
2. implement local candidate `scripts/loom_30b_interactive_v1_001.py` without Git operations;
3. first-16-position semantic parity vs canonical greedy path;
4. streaming + state-reuse mechanics;
5. fixed 3-turn memory smoke ending with `7319`;
6. real ~180-word Italian MoE answer with live streaming and usability metrics;
7. five-turn stability/context-memory session.

`READY` requires semantic parity, incremental state reuse, safe multi-turn execution, long-form decode >=`1.00 tok/s`, TTFT <=30s, peak RSS <=6.5 GiB and cumulative swap <=512 MiB.

A fully correct runtime that must re-prefill history or falls below the usability thresholds may be `FUNCTIONAL_SLOW` rather than silently optimized.

No network, model changes, Qwen3.8, Heretic/refusal editing, 8B/4B bake-off, speculative decoding, or new speed experiments inside this checkpoint.

## Strategic sequence after Interactive v1

1. Review/persist accepted **LOOM 30B v1** and perform manual real use.
2. Run a matched practical **30B vs Qwen-family 8B vs 4B** bake-off on the same M1/8GB: quality, TTFT, tok/s, RAM/swap and time-to-correct-task.
3. Decide architecture role:
   - 30B primary/deep mode;
   - 8B/4B fast primary + 30B deep mode;
   - skill/tool/protocol-centric small-model system.
4. Apply the existing Heretic technical paper as input to a separate preregistered behavioral/refusal-direction editing checkpoint on the selected runtime(s), with quality-preservation gates. Do not call the result absolutely `guardrail-free`; measure refusal rate and steerability.
5. Maintain a separate 30B R&D branch for materially new speed mechanisms: direct-from-higher-precision mixed-bit quantization, fused Metal expert kernels, vectored expert I/O, and trace-driven bounded cache simulation.

The project priority is now practical utility, not pursuing `5 tok/s` on the current verifier at any cost.