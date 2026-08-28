# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Qwen3-30B-A3B now has a reviewed, repaired and Git-persisted interactive runtime. Historical classification remains `FUNCTIONAL_SLOW` because long-form TTFT is above the frozen READY threshold. Current checkpoint is the user's first real manual conversation with canonical LOOM 30B v1.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_V1_MANUAL_USER_SESSION`
Pi context: `/AGENTS.md` v3.49.

## Frozen research comparator

Canonical expert backend: `scripts/loom_30b_moe_expert_major_backend_001.py`.
Backend commit `96958de`.
Backend SHA `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.
Exact Q4/top-8 3×32: `1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Closed speed paths: routing sparsity no acceptable gain; Q2/Q3 fidelity fail; DFlash closed; perfect-oracle K=4 verifier ceiling `1.792925 tok/s`, so real drafter is not justified.

Qwen3.8-27B and Flash-Next are both statically portable but execution/downloads remain parked until after practical size comparison.

## Interactive Runtime v1 — FUNCTIONAL_SLOW

Result: `research/architecture/loom-30b-interactive-runtime-v1-001-result.md`.
Evidence: `results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`.

Validated environment:
- `.venvs/stretch030-mlx0320-fix1/bin/python`;
- Python `3.13.0`;
- MLX `0.32.0`;
- mlx-lm `0.31.3`.

Historical long-form:
- TTFT `47.832 s`;
- decode `1.116 tok/s`;
- end-to-end `0.921 tok/s`;
- peak RSS `1,447,067,648 B`.

Functional gates PASS:
- semantic parity;
- streaming;
- exact incremental state reuse;
- 3-turn and 5-turn memory/stability;
- zero SOURCE fallback/cache.

Classification is `FUNCTIONAL_SLOW` only because TTFT exceeded the frozen `<=30 s` READY threshold.

## Canonical production runtime — PERSISTED

Canonicalization repair: GO.
EOS-finalize repair: GO.

Production commit:
`d3691b765004849abb01a7675e5a6e7c5d0edd4c` — `feat: add canonical LOOM 30B interactive runtime`.

Files:
- `scripts/loom_30b_runtime_core_v1_001.py` — SHA-256 `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` — SHA-256 `44b89ba34d597a3c9798c7ad1c081aa0eeff865cc5320e27213b3c6ebe4a5322`.

Remote verification: `d3691b7` is exactly one commit after the prior checkpoint and adds only those two runtime files.

Validated production properties:
- no untracked research-helper imports;
- canonical backend unchanged;
- exact token/routing/logit parity;
- exact incremental KV/state reuse/no history re-prefill;
- stateful Unicode streaming;
- stop/EOS suppressed before emission;
- detokenizer finalized for both EOS and length termination;
- literal `<|im_end|>` user content does not corrupt turn boundary;
- PACKED-only, fallback 0, no persistent expert cache, deterministic fd close.

## Exact next step — manual real use

No Pi prompt.

User launches the committed CLI with:
`.venvs/stretch030-mlx0320-fix1/bin/python scripts/loom_30b_interactive_v1_001.py`

Manual session should include:
1. at least two normal free-form questions;
2. one follow-up that requires remembering a fact/context from an earlier turn;
3. `/reset`, followed by a question confirming prior conversational state is no longer available;
4. `/exit` for clean teardown.

Record practical observations: startup/TTFT feel, streaming smoothness, coherence, memory, latency tolerance and any runtime error. Do not replace historical benchmark values with subjective estimates.

If manual use is acceptable, freeze **LOOM 30B v1 FUNCTIONAL_SLOW** as the large practical comparator.

## After manual v1

Open matched Qwen-family 30B vs 8B vs 4B practical bake-off on M1/8GB: TTFT, sustained decode, RAM/swap, disk, time-to-correct-task, and frozen practical intelligence tasks.

Then decide runtime roles: 30B deep/primary, small fast primary + 30B escalation, or skill/tool/protocol-centric small model. Only after role selection use `LOOM_HERETIC_TECHNICAL_PAPER.md` for a separate refusal/steerability-editing checkpoint. TTFT/prefill and materially new 30B speed work remain separate R&D.