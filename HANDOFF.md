# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Qwen3-30B-A3B research runtime is frozen at exact-Q4 benchmark median `1.229233 tok/s`; Qwen3.8 metadata readiness says both newer candidates are statically portable but their execution is parked. Current work is converting the accepted 30B into a real interactive local runtime.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_INTERACTIVE_RUNTIME_V1_001`
Pi context: `/AGENTS.md` v3.45.

## Frozen current 30B baseline

Canonical backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Commit:
`96958de`.

Exact-Q4/top-8 benchmark 3×32:
- `1.115874`;
- `1.229233`;
- `1.254611 tok/s`;
median `1.229233 tok/s`.

Validated backend SHA-256:
`6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

Settled/closed current-verifier speed paths:
- expert-major accepted/canonical;
- persistent PACKED fd retained;
- routing sparsity no acceptable gain;
- Q2/Q3 from Q4 fidelity fail;
- DFlash closed;
- perfect-oracle K=4 verifier ceiling only `1.792925 tok/s`, therefore real speculative drafter not justified.

These numbers are research evidence. The current checkpoint must establish actual end-to-end chat usability before the runtime is called LOOM 30B v1.

## Qwen3.8 status — readiness complete, execution parked

`QWEN38_BOTH_PORTABLE` from metadata-only readiness.

Qwen3.8-27B:
- dense 64-layer streaming feasible;
- projected `13,702,468,608 B/token` external weights;
- resident `1,587,312,640 B`;
- likely poor naive decode economics relative to sparse 30B.

Qwen3.8-Flash-Next:
- streaming/expert-major architecture feasible;
- 512 routed experts, top-10 + shared;
- projected `3,858,155,864 B/token` external baseline;
- native MTP metadata covered but runtime adapter pending;
- ~105.434 GiB artifact needs external storage.

Do not download/execute either candidate now. Revisit after the 30B-vs-8B-vs-4B practical comparison or if a materially new architecture hypothesis justifies it.

## Current — LOOM 30B Interactive Runtime v1 001

Preregistration:
`research/architecture/loom-30b-interactive-runtime-v1-001-preregistration.md`.

Goal: produce a real terminal chat runtime on the existing canonical 30B without changing its model semantics.

Required flow:
1. recover/freeze the exact accepted Python/MLX execution environment;
2. create local candidate `scripts/loom_30b_interactive_v1_001.py`;
3. require 16-position greedy semantic parity against canonical runtime;
4. prove token-by-token stdout streaming and measure TTFT/flush overhead;
5. prove exact incremental conversation-state reuse where supported;
6. fixed 3-turn conversation state smoke, final answer `7319`;
7. real long-form Italian MoE explanation (~180 words target) with live streaming and end-to-end metrics;
8. five-turn stability/memory test.

READY gates:
- semantic parity PASS;
- streaming PASS;
- incremental KV/recurrent reuse PASS;
- 3-turn and 5-turn sessions PASS;
- long-form decode >=`1.00 tok/s`;
- TTFT <=30 s;
- peak RSS <=6.5 GiB;
- cumulative swap <=512 MiB;
- zero SOURCE fallback/persistent expert cache.

If multi-turn only works through deterministic full re-prefill or performance misses the user-facing thresholds, classification may be `LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`; do not hide this with post-hoc optimization.

Pi may create/edit the interactive script locally but must not commit/push or edit project decision docs. If the canonical backend itself appears to require modification, Pi must record the defect and stop for review before acceptance.

## Planned sequence after v1

### A. Practical model-size bake-off

Compare the accepted 30B v1 against one matched Qwen-family 8B and one 4B on identical M1/8GB constraints.

Measure per model:
- TTFT;
- sustained tok/s;
- RAM/swap;
- time to complete fixed tasks;
- fixed practical intelligence set: reasoning/math, coding/debugging, Italian explanation, structured instructions, document/context use and simple agent/tool-oriented planning.

Primary question: how much practical correctness does the 30B buy for its latency?

### B. Architecture decision

Depending on bake-off:
- 30B primary/deep mode;
- smaller fast primary + 30B deep escalation;
- small-model-first system enhanced by skills/tools/protocols/verifiers.

### C. Behavioral/refusal editing

Use `LOOM_HERETIC_TECHNICAL_PAPER.md` as design input only after selecting runtime roles. Build a separate frozen behavioral-editing checkpoint measuring refusal/steerability and quality preservation. Avoid unmeasured claims of absolute `no guardrails`.

### D. 30B R&D speed branch

Separate from productization:
- direct higher-precision -> mixed-bit expert quantization;
- fused Metal expert kernel;
- vectored/grouped expert I/O;
- trace-driven bounded cache simulation before runtime implementation.

Current priority: finish a model the user can actually chat with, then determine whether 30B, 8B or 4B gives the best practical system.