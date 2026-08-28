# LOOM Roadmap

Last updated: 2026-08-28
Current: `LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`
Immediate next: `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_REPAIR_001`
Canonical context: `/AGENTS.md` v3.47.

## 1. Frozen 30B research baseline

Qwen3-30B-A3B exact-Q4/top-8:
- backend commit `96958de`;
- sustained 3×32 `1.115874`, `1.229233`, `1.254611 tok/s`;
- research median `1.229233 tok/s`;
- exactness/safety PASS.

Closed/non-productive current-verifier paths:
- routing sparsity: no acceptable gain;
- Q2/Q3 expert requantization from deployed Q4: fidelity fail;
- DFlash: closed;
- real speculative drafter: not justified because perfect-oracle K=4 verifier ceiling is only `1.792925 tok/s` median.

Do not treat `5 tok/s` on this verifier as the immediate product goal.

## 2. Qwen3.8 research status — parked

Metadata-only readiness: `QWEN38_BOTH_PORTABLE`.

Qwen3.8-27B dense projected external traffic: `13.702 GB/token`.
Qwen3.8-Flash-Next projected external baseline: `3.858 GB/token`; native MTP metadata covered but runtime integration pending; ~105.434 GiB payload.

Do not spend large downloads now. Revisit after practical size/architecture bake-off or a materially new mechanism.

## 3. Interactive Runtime v1 — functionally proven

Result: `research/architecture/loom-30b-interactive-runtime-v1-001-result.md`.

Validated functionality:
- semantic parity PASS;
- live streaming PASS;
- exact multi-turn state reuse PASS;
- three-turn and five-turn memory/stability PASS;
- zero SOURCE fallback/cache;
- peak RSS ~1.35 GiB;
- swap safe.

Long-form:
- TTFT `47.832 s`;
- decode `1.116 tok/s`;
- end-to-end `0.921 tok/s`.

Classification `FUNCTIONAL_SLOW` is solely because TTFT exceeds frozen 30 s READY threshold.

## 4. Exact source review — repair required before commit

Reviewed candidate SHA:
`25607adf29b8bd045a938b6bd32afa2322d95ebaa5e156da5f86010a4101bcfa`.

Canonicalization blockers:
1. CLI depends on two untracked research Python helpers, so a clean checkout cannot run it;
2. per-token standalone decode is not a robust streaming detokenizer path;
3. stop/EOS may be printed before termination;
4. next-turn suffix discovery scans full transcript for second-last EOS and is fragile to special-token-looking content.

These findings do not invalidate prior runtime evidence; they require a bounded production-code repair.

## 5. Current — Interactive v1 Canonicalization Repair 001

Preregistration:
`research/architecture/loom-30b-interactive-v1-canonicalization-repair-001-preregistration.md`.

Repair objectives:
- create minimal tracked runtime core `scripts/loom_30b_runtime_core_v1_001.py` from only the validated helper functionality needed by the CLI;
- repaired CLI imports no untracked research modules;
- canonical expert-major backend unchanged;
- use mlx-lm stateful `tokenizer.detokenizer`;
- never emit EOS/control stop markers;
- robust canonical turn suffix preserving exact generated token IDs/KV;
- startup stop-token/template compatibility check;
- exact 16-position parity and state-reuse regression;
- special-token-looking input smoke;
- Unicode streaming equivalence;
- 3-turn memory + bounded live generation regression;
- recursively verify production imports are tracked/runtime-safe.

Expected files after GO:
- `scripts/loom_30b_runtime_core_v1_001.py`;
- `scripts/loom_30b_interactive_v1_001.py`.

Pi does not commit. ChatGPT reviews final diffs/SHAs, then user commits approved files only.

## 6. Manual LOOM 30B v1 session

After canonicalization GO and commit:
- user launches the committed CLI;
- holds a real free-form multi-turn conversation;
- records practical observations separately from benchmark numbers.

If acceptable, freeze **LOOM 30B v1 FUNCTIONAL_SLOW** as the large practical comparator.

A later dedicated TTFT/prefill optimization checkpoint may be opened if manual use shows first-token latency is the main usability issue.

## 7. Next scientific decision — 30B vs 8B vs 4B

Run one matched Qwen-family 8B and 4B baseline on the same M1/8GB.

Primary question: **how much correct/useful work is produced per unit of waiting time and memory?**

Matched outputs:
- TTFT;
- sustained decode tok/s;
- RAM/swap;
- disk footprint;
- end-to-end task time;
- fixed practical intelligence across reasoning/math, coding, debugging, Italian technical explanation, structured instructions, supplied-context reasoning and planning/tool-use decisions.

Possible architecture decisions:
- 30B primary/deep;
- 8B fast primary + 30B escalation;
- 4B/8B skill/tool/protocol-centric primary, 30B only where measured benefit justifies latency.

## 8. Small-model intelligence amplification

After size bake-off:
- dynamically retrieved skills/protocols;
- planner -> executor -> verifier workflows;
- Python/calculator/filesystem/Git/web/RAG tools;
- persistent/retrieved memory;
- test-time retries/candidate verification;
- task-specific LoRA/distillation with frozen eval gates;
- optional routing from fast small model to 30B deep mode.

Measure all gains on the same practical eval set.

## 9. Behavioral/refusal editing

Use `LOOM_HERETIC_TECHNICAL_PAPER.md` only after runtime roles are selected.

Separate preregistration must freeze contrastive prompt construction, layer/component selection, refusal/steerability metrics, capability preservation and rollback criteria.

Report measured refusal rate/steerability rather than an unmeasured absolute `guardrail-free` label.

## 10. Separate 30B speed R&D

Do not block product work.

Materially new hypotheses:
1. direct higher-precision -> mixed-bit expert quantization;
2. fused Metal packed-Q4 expert kernel;
3. vectored/grouped expert reads and bounded multi-expert dispatch;
4. offline trace simulation of small bounded expert caches;
5. TTFT/prefill optimization after manual-use evidence;
6. a materially new verifier architecture only if it changes oracle-ceiling economics.

Final project architecture is chosen from measured practical utility, not novelty or nominal parameter count.