# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Qwen3-30B-A3B has a functionally validated interactive runtime (`FUNCTIONAL_SLOW`) and the bounded canonicalization repair is now `GO`. The only remaining blocker before canonical LOOM 30B v1 is exact review/persistence of the two repaired local runtime files, followed by one manual user conversation.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_INTERACTIVE_V1_FINAL_SOURCE_REVIEW_PERSISTENCE`
Pi context: `/AGENTS.md` v3.48.

## Frozen 30B comparator

Canonical backend: `scripts/loom_30b_moe_expert_major_backend_001.py`.
Commit `96958de`.
Research median `1.229233 tok/s` from 3×32 exact Q4/top-8 runs.
Backend SHA `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

Closed speed paths: routing sparsity no acceptable gain; Q2/Q3 fidelity fail; DFlash closed; perfect-oracle K=4 verifier ceiling only `1.792925 tok/s`, so real drafter is not justified.

Qwen3.8-27B and Flash-Next are both statically portable but execution/downloads remain parked until after practical size comparison.

## Interactive Runtime v1 001 — FUNCTIONAL_SLOW

Result: `research/architecture/loom-30b-interactive-runtime-v1-001-result.md`.
Evidence: `results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`.

Validated environment:
- `.venvs/stretch030-mlx0320-fix1/bin/python`;
- Python `3.13.0`;
- MLX `0.32.0`;
- mlx-lm `0.31.3`.

Functional gates PASS:
- 16/16 semantic parity;
- live streaming;
- exact incremental multi-turn state reuse;
- `7319` three-turn memory smoke;
- five-turn stability with `ALFA-482` recovered;
- zero SOURCE fallback/cache.

Long-form: TTFT `47.832 s`; decode `1.116 tok/s`; end-to-end `0.921 tok/s`. Classification is `FUNCTIONAL_SLOW` solely because TTFT exceeded the frozen 30 s READY threshold.

## Canonicalization Repair 001 — GO

Result:
`research/architecture/loom-30b-interactive-v1-canonicalization-repair-001-result.md`
Evidence:
`results-local/research/30b-interactive-v1-canonicalization-repair-001/20260828T131045Z/`

Original reviewed CLI SHA verified:
`25607adf29b8bd045a938b6bd32afa2322d95ebaa5e156da5f86010a4101bcfa`.

Repair produced exactly two intended local files:
- `scripts/loom_30b_runtime_core_v1_001.py` — SHA `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` — SHA `08e84d1b19afdd4bad757db29d0d804783a35ee41db17696c14c56c8913488cb`.

Validated repair gates:
- no production imports of untracked research helpers;
- canonical expert-major backend unchanged;
- exact 16-position token/routing/logit parity;
- exact multi-turn state reuse/no history re-prefill;
- stateful Unicode streaming equivalence;
- stop/EOS suppressed before user emission;
- literal `<|im_end|>` user content does not corrupt turn boundary;
- `7319` smoke PASS;
- PACKED-only, fallback 0, no expert cache, deterministic fd close.

Bounded regression run: 5 output tokens under 32-token cap, `1.449028 tok/s`, TTFT `18.288247 s`, peak RSS `964,984,832 B`. Observed system swap `1471.06 MiB` with no critical pressure; no new swap threshold existed in this repair, so historical v1 safety evidence remains the user-facing baseline.

## Immediate action — exact source review/persistence

Do not begin 8B/4B yet.

Need exact local source of both repaired files, matching the reported SHAs. ChatGPT reviews them before persistence.

If review PASS:
1. stage only the two approved runtime files;
2. `git diff --cached --check`;
3. verify no unrelated staged content;
4. commit/push;
5. verify remote content/SHA;
6. user launches committed CLI and holds a real free-form conversation.

After manual use: freeze **LOOM 30B v1 FUNCTIONAL_SLOW** practical comparator and open the matched 30B vs 8B vs 4B bake-off.

Later: role selection, then Heretic-paper-informed refusal/steerability editing; TTFT/prefill and materially new 30B speed work remain separate R&D.