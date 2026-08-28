# LOOM Roadmap

Last updated: 2026-08-28
Current: `LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`
Immediate next: review/persist the validated interactive CLI, then manual user session
Canonical context: `/AGENTS.md` v3.46.

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

Conclusion: stop treating `5 tok/s` on this verifier as the immediate product goal. Preserve the 30B as the large-model comparator while separate R&D investigates materially different mechanisms.

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
- native MTP potentially interesting but local runtime integration not ready;
- ~105.434 GiB artifact needs external storage.

Decision: do not spend ~16 GB / ~105 GiB downloads now. Revisit after practical size/architecture bake-off or a materially new mechanism.

## 3. LOOM 30B Interactive Runtime v1 — FUNCTIONAL_SLOW

Result:
`research/architecture/loom-30b-interactive-runtime-v1-001-result.md`.

Evidence:
`results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`.

Validated local candidate:
`scripts/loom_30b_interactive_v1_001.py`

Functional evidence:
- 16-position semantic parity PASS;
- token streaming PASS;
- exact incremental multi-turn state reuse PASS;
- 3-turn memory smoke PASS;
- 5-turn stability/memory PASS;
- zero SOURCE fallback / zero persistent expert cache;
- peak RSS ~1.35 GiB;
- swap safe.

Real long-form performance:
- TTFT `47.832 s`;
- decode-only `1.116 tok/s`;
- end-to-end `0.921 tok/s`;
- p50/p95 `0.869 / 1.276 s`.

Classification is `FUNCTIONAL_SLOW` only because long-form TTFT exceeds the frozen `<=30 s` READY gate.

The candidate remains local/untracked and is not yet canonical.

## 4. Immediate — code review, persistence, manual use

Before any 8B/4B comparison:
1. inspect exact source/SHA of `scripts/loom_30b_interactive_v1_001.py`;
2. verify no hidden model/runtime changes or test shortcuts;
3. if review PASS, stage only that file and commit/push;
4. user launches the committed CLI and holds a real conversation;
5. record manual usability observations without replacing objective benchmark numbers.

If manual use is acceptable, freeze as **LOOM 30B v1 FUNCTIONAL_SLOW**.

A separate TTFT/prefill optimization checkpoint may be opened later if the manual session shows first-token latency is the dominant practical problem. Do not repair it inside the already-closed v1 checkpoint.

## 5. Next scientific decision — 30B vs 8B vs 4B

After manual 30B v1, acquire/run one matched Qwen-family 8B and one 4B baseline on the same M1/8GB.

Question:
**How much correct/useful work is produced per unit of waiting time and memory?**

Matched outputs:
- TTFT;
- sustained decode tok/s;
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

## 6. Small-model intelligence amplification

After size bake-off, optimize selected 4B/8B path as a system:
- dynamically retrieved skills/protocols;
- planner -> executor -> verifier workflows;
- Python/calculator/filesystem/Git/web/RAG tools;
- persistent/retrieved memory;
- test-time retries/candidate verification;
- task-specific LoRA/distillation only with frozen eval gates;
- optional routing from fast small model to 30B deep mode.

Measure improvement on the same practical eval set.

## 7. Behavioral/refusal editing

Use `LOOM_HERETIC_TECHNICAL_PAPER.md` only after runtime roles are selected.

Goal: experimentally reduce refusal behavior / increase steerability while preserving capability.

A separate preregistration must freeze:
- contrastive prompt construction;
- layer/component selection protocol;
- refusal/steerability metrics;
- intelligence/quality preservation metrics;
- rollback criteria.

Report measured refusal rate and steerability rather than an unmeasured absolute `guardrail-free` label.

## 8. Separate 30B speed R&D

Do not block product work on this branch.

High-value materially new hypotheses:
1. direct-from-higher-precision mixed-bit expert quantization;
2. fused Metal kernel for packed-Q4 expert load/QMV path;
3. vectored/grouped expert reads and bounded multi-expert dispatch;
4. offline trace simulation of small bounded expert caches before runtime implementation;
5. dedicated TTFT/prefill optimization if manual use justifies it;
6. materially new verifier architecture only if it changes the oracle-ceiling economics.

Each mechanism gets a separate preregistered test.

## 9. Qwen3.8 later

Revisit Qwen3.8-Flash-Next before dense 27B if storage/runtime conditions permit and expected benefit becomes compelling, especially once native MTP/n-gram runtime support can be evaluated meaningfully.

Final project architecture is chosen from measured practical utility, not novelty or nominal parameter count.