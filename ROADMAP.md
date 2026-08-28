# LOOM Roadmap

Last updated: 2026-08-28
Current: `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_GO`
Immediate next: exact review/persist the two repaired runtime files, then manual terminal use
Canonical context: `/AGENTS.md` v3.48.

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
- zero SOURCE fallback/cache.

Long-form:
- TTFT `47.832 s`;
- decode `1.116 tok/s`;
- end-to-end `0.921 tok/s`.

Classification `FUNCTIONAL_SLOW` remains because TTFT exceeds the frozen 30 s READY threshold.

## 4. Canonicalization Repair 001 — GO

Result:
`research/architecture/loom-30b-interactive-v1-canonicalization-repair-001-result.md`.

The source-review defects were repaired without touching the canonical expert-major backend.

Intended local production files:
- `scripts/loom_30b_runtime_core_v1_001.py` — SHA `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` — SHA `08e84d1b19afdd4bad757db29d0d804783a35ee41db17696c14c56c8913488cb`.

Repair gates PASS:
- tracked-ready dependency graph;
- 16-position exact token/routing/logit parity;
- exact incremental state reuse;
- Unicode streaming equivalence;
- stop/EOS not emitted;
- literal `<|im_end|>` boundary smoke;
- `7319` conversation smoke;
- PACKED-only, fallback 0, no persistent expert cache, deterministic fd close.

Bounded regression performance was `1.449028 tok/s`, TTFT `18.288247 s`, but historical long-form v1 performance remains the comparator.

## 5. Immediate — final source review, Git persistence, manual use

The repair GO is not yet canonical status.

Before commit:
1. ChatGPT inspects exact contents of both repaired local files and verifies reported SHAs;
2. canonical backend must remain zero-diff;
3. user stages only those two files;
4. `git diff --cached --check` and staged-file review;
5. commit/push;
6. remote content verification.

Then user launches the committed CLI for a real free-form multi-turn conversation. If acceptable, freeze **LOOM 30B v1 FUNCTIONAL_SLOW** as the large practical comparator.

## 6. Next scientific decision — 30B vs 8B vs 4B

After manual 30B v1, run one matched Qwen-family 8B and 4B baseline on the same M1/8GB.

Question:
**How much correct/useful work is produced per unit of waiting time and memory?**

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

## 7. Small-model intelligence amplification

After size bake-off:
- dynamically retrieved skills/protocols;
- planner -> executor -> verifier workflows;
- Python/calculator/filesystem/Git/web/RAG tools;
- persistent/retrieved memory;
- test-time retries/candidate verification;
- task-specific LoRA/distillation with frozen eval gates;
- optional routing from fast small model to 30B deep mode.

Measure all gains on the same practical eval set.

## 8. Behavioral/refusal editing

Use `LOOM_HERETIC_TECHNICAL_PAPER.md` only after runtime roles are selected.

Separate preregistration must freeze contrastive prompt construction, layer/component selection, refusal/steerability metrics, capability preservation and rollback criteria.

Report measured refusal rate/steerability rather than an unmeasured absolute `guardrail-free` label.

## 9. Separate 30B speed R&D

Do not block product work.

Materially new hypotheses:
1. direct higher-precision -> mixed-bit expert quantization;
2. fused Metal packed-Q4 expert kernel;
3. vectored/grouped expert reads and bounded multi-expert dispatch;
4. offline trace simulation of small bounded expert caches;
5. TTFT/prefill optimization after manual-use evidence;
6. materially new verifier architecture only if it changes oracle-ceiling economics.

Final project architecture is chosen from measured practical utility, not novelty or nominal parameter count.