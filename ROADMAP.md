# LOOM Roadmap

Last updated: 2026-08-28
Current: Qwen3-30B-A3B speed research frozen; Qwen3.8 execution parked after static portability PASS
Immediate next: `LOOM_30B_INTERACTIVE_RUNTIME_V1_001`
Canonical context: `/AGENTS.md` v3.45.

## 1. Frozen 30B research baseline

Qwen3-30B-A3B exact-Q4/top-8:
- backend commit `96958de`;
- sustained 3×32 `1.115874`, `1.229233`, `1.254611 tok/s`;
- research median `1.229233 tok/s`;
- exactness/safety PASS.

Closed or non-productive current-verifier paths:
- routing sparsity: no acceptable gain;
- Q2/Q3 expert requantization from deployed Q4: fidelity fail;
- DFlash: closed;
- real speculative drafter: not justified because perfect-oracle K=4 verifier ceiling is only `1.792925 tok/s` median;
- K=8 oracle experiment invalid and not current priority.

Conclusion: stop treating `5 tok/s` on this verifier as the immediate product goal. Preserve current runtime as the large-model comparator while separate R&D investigates materially different mechanisms.

## 2. Qwen3.8 research status — parked

Metadata-only readiness:
`QWEN38_BOTH_PORTABLE`.

Qwen3.8-27B dense:
- static layer streaming fits active memory;
- projected external weight traffic `13.702 GB/token`;
- likely significantly worse naive decode economics than current sparse 30B.

Qwen3.8-Flash-Next:
- static LOOM decomposition feasible;
- projected external baseline `3.858 GB/token`;
- native MTP is potentially interesting but local runtime integration is not ready;
- ~105.434 GiB artifact needs external storage.

Decision: do not spend ~16 GB / ~105 GiB downloads now. Revisit after practical size/architecture bake-off or a new mechanism changes expected economics.

## 3. Current — LOOM 30B Interactive Runtime v1

Preregistration:
`research/architecture/loom-30b-interactive-runtime-v1-001-preregistration.md`.

Objective: turn the accepted 30B research engine into a real user-facing terminal chat runtime.

Required capabilities:
- token-streamed text output;
- canonical greedy semantics;
- multi-turn conversation;
- KV/recurrent state reuse;
- `/reset` and `/exit`;
- deterministic teardown;
- TTFT/tok/s/RSS/swap instrumentation.

Validation:
- semantic parity vs canonical path;
- streaming mechanics;
- fixed 3-turn memory test;
- long real answer;
- five-turn stability test.

Ready target:
- semantic parity and state reuse PASS;
- long-form decode >=1.00 tok/s;
- TTFT <=30 s;
- peak RSS <=6.5 GiB;
- cumulative swap <=512 MiB.

If accepted, review and persist as **LOOM 30B v1**, then perform a manual user session before broader architecture work.

## 4. Next scientific decision — 30B vs 8B vs 4B

After 30B v1 is usable, acquire/run one matched Qwen-family 8B and one 4B baseline on the same M1/8GB.

The comparison must answer not `which has more parameters?` but:

**How much correct/useful work is produced per unit of waiting time and memory?**

Matched outputs:
- TTFT;
- sustained tok/s;
- RAM/swap;
- disk footprint;
- end-to-end task time;
- fixed practical intelligence score across:
  - reasoning/math;
  - coding;
  - debugging;
  - Italian technical explanation;
  - structured instruction following;
  - supplied-context/document reasoning;
  - planning/tool-use decisions.

Possible decisions:

### A. 30B advantage is large
Use 30B as primary/deep runtime and continue targeted speed R&D.

### B. 8B is near 30B quality but much faster
Use 8B as fast default, escalate difficult work to 30B.

### C. 4B/8B practical quality is competitive
Prioritize a skill/tool/protocol-centric small-model architecture; retain 30B only where measured benefit justifies latency.

## 5. Small-model intelligence amplification

After the size bake-off, optimize the selected 4B/8B path as a system rather than pretending prompts change parameter capacity.

Candidate mechanisms:
- dynamically retrieved skills/protocols;
- planner -> executor -> verifier workflows;
- Python/calculator/filesystem/Git/web/RAG tools;
- persistent/retrieved memory;
- test-time retries/candidate verification;
- task-specific LoRA/distillation only with frozen eval gates;
- optional routing from fast small model to 30B deep mode.

Measure improvement on the same practical eval set so gains are attributable to the system, not subjective impressions.

## 6. Behavioral/refusal editing

Use the project file `LOOM_HERETIC_TECHNICAL_PAPER.md` after runtime roles are selected.

Goal: experimentally reduce refusal behavior / increase steerability while preserving useful capability.

A separate preregistration must freeze:
- contrastive prompt construction;
- layer/component selection protocol;
- refusal/steerability metrics;
- intelligence/quality preservation metrics;
- rollback criteria.

Do not promise or label absolute `guardrail-free` behavior without measurement. Report observed refusal rate, steerability and quality effects.

## 7. Separate 30B speed R&D branch

Do not block product work on this branch.

High-value materially new hypotheses:
1. direct-from-higher-precision mixed-bit expert quantization rather than Q4->Q3/Q2 cascading;
2. fused Metal kernel for packed-Q4 expert load/dequantized QMV path;
3. vectored/grouped expert reads and bounded multi-expert dispatch;
4. offline trace simulation of small bounded expert caches before runtime implementation;
5. materially new verifier architecture only if it changes the oracle ceiling economics.

Each mechanism gets a separate preregistered test; no reopening settled failures by adjacent parameter search.

## 8. Qwen3.8 later

Revisit Qwen3.8-Flash-Next before dense 27B if future local storage/runtime conditions permit and the expected benefit becomes compelling, especially once native MTP/n-gram runtime support can be evaluated meaningfully.

Final project architecture should be chosen from measured practical utility, not novelty or nominal parameter count.