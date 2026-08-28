# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Qwen3-30B-A3B has a functionally validated interactive runtime (`FUNCTIONAL_SLOW`), but exact source review found reproducibility/streaming/boundary blockers before production canonicalization. Current checkpoint is a bounded canonicalization repair.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_REPAIR_001`
Pi context: `/AGENTS.md` v3.47.

## Frozen 30B comparator

Canonical backend: `scripts/loom_30b_moe_expert_major_backend_001.py`.
Commit `96958de`.
Research median `1.229233 tok/s` from 3×32 exact Q4/top-8 runs.
Backend SHA `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

Closed speed paths: routing sparsity no acceptable gain; Q2/Q3 fidelity fail; DFlash closed; perfect-oracle K=4 verifier ceiling only `1.792925 tok/s`, so real drafter is not justified.

Qwen3.8-27B and Flash-Next are both statically portable but execution/downloads are parked until after practical size comparison.

## Interactive Runtime v1 001 — FUNCTIONAL_SLOW

Result: `research/architecture/loom-30b-interactive-runtime-v1-001-result.md`.
Evidence: `results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`.

Environment:
- `.venvs/stretch030-mlx0320-fix1/bin/python`;
- Python `3.13.0`;
- MLX `0.32.0`;
- mlx-lm `0.31.3`.

Functional gates PASS:
- 16/16 semantic parity;
- live streaming;
- exact incremental multi-turn KV/recurrent reuse;
- `7319` three-turn memory smoke;
- five-turn stability with `ALFA-482` recovered;
- zero SOURCE fallback/cache;
- peak RSS `1,447,067,648 B`;
- swap safe.

Long-form: TTFT `47.832 s`; decode `1.116 tok/s`; end-to-end `0.921 tok/s`; p50/p95 `0.869 / 1.276 s`.
Only READY-gate miss was TTFT >30 s.

## Exact source review findings

Reviewed candidate: `scripts/loom_30b_interactive_v1_001.py`.
Reviewed SHA-256: `25607adf29b8bd045a938b6bd32afa2322d95ebaa5e156da5f86010a4101bcfa`.

Blockers before commit:
1. production CLI imports two untracked research helpers: `loom_30b_moe_first_greedy_generation_001` and `loom_30b_moe_shared_backbone_residency_001`; both are absent from the remote branch, so committing only the CLI would break reproducibility;
2. live streaming uses `tokenizer.decode([token])` independently per token instead of the installed mlx-lm stateful streaming detokenizer;
3. EOS/stop token is decoded/emitted before the stop test and can become visible;
4. incremental turn boundary is located by scanning the whole re-tokenized transcript for the second-last hard-coded EOS, which is fragile to special-token-looking content.

These are code-productization issues, not evidence that the validated model/runtime semantics are wrong.

## Current repair

Preregistration:
`research/architecture/loom-30b-interactive-v1-canonicalization-repair-001-preregistration.md`.

Frozen repair scope:
- promote minimal tracked `scripts/loom_30b_runtime_core_v1_001.py` containing only validated helper functionality required by interactive runtime;
- repaired `scripts/loom_30b_interactive_v1_001.py` imports only tracked runtime code + frozen installed packages;
- canonical backend has zero diff;
- use `tokenizer.detokenizer` for incremental text;
- test stop/EOS before emission;
- robust canonical next-turn suffix, preserving exact generated token IDs in KV;
- literal `<|im_end|>` user-input smoke;
- Unicode/multi-token streaming equivalence;
- 16-position semantic parity + exact state-reuse regression;
- 3-turn memory + bounded live interactive regression;
- recursive tracked dependency audit.

Pi must not commit/push. Expected intended production file set after GO:
- `scripts/loom_30b_runtime_core_v1_001.py`;
- `scripts/loom_30b_interactive_v1_001.py`.

After Pi result: ChatGPT reviews exact diffs/SHAs. If PASS, user stages only those files, runs `git diff --cached --check`, commits/pushes, then manually chats with the committed runtime.

Only after that manual session: freeze LOOM 30B v1 practical comparator and start matched 30B vs 8B vs 4B bake-off.

Later: decide large/deep vs small/fast roles, then Heretic-paper-informed refusal/steerability editing; keep TTFT/prefill and new 30B speed mechanisms as separate R&D.