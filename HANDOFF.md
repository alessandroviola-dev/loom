# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Qwen3-30B-A3B now has a validated end-to-end interactive local runtime candidate. Classification is `LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`: all correctness/streaming/state/stability gates pass, but long-form TTFT `47.832 s` exceeds the frozen READY limit. Candidate source is still local/untracked and awaits exact code review + Git persistence.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_INTERACTIVE_V1_CODE_REVIEW_PERSISTENCE`
Pi context: `/AGENTS.md` v3.46.

## Frozen 30B research comparator

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

Closed current-verifier speed paths:
- expert-major accepted/canonical;
- persistent PACKED fd retained;
- routing sparsity no acceptable gain;
- Q2/Q3 from Q4 fidelity fail;
- DFlash closed;
- perfect-oracle K=4 verifier ceiling only `1.792925 tok/s`, so real speculative drafter is not justified.

## Qwen3.8 status — both statically portable, execution parked

`QWEN38_BOTH_PORTABLE` from metadata-only readiness.

Qwen3.8-27B projected external streaming traffic:
`13,702,468,608 B/token`.

Qwen3.8-Flash-Next projected external baseline:
`3,858,155,864 B/token`.

Do not download/execute either now. Revisit after practical 30B-vs-8B-vs-4B comparison unless explicitly reactivated.

## Interactive Runtime v1 001 — FUNCTIONAL_SLOW

Result:
`research/architecture/loom-30b-interactive-runtime-v1-001-result.md`
Evidence:
`results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`

Environment:
- `.venvs/stretch030-mlx0320-fix1/bin/python`;
- Python `3.13.0`;
- MLX `0.32.0`;
- mlx-lm `0.31.3`.

Local candidate:
`scripts/loom_30b_interactive_v1_001.py`

Current source status:
- untracked/local;
- not yet reviewed by ChatGPT;
- not yet committed/pushed;
- therefore not canonical yet.

Validated gates:
- semantic parity: PASS, 16/16 positions;
- streaming: PASS; flush p95 `0.000075 s`;
- exact incremental state reuse: PASS;
- 3-turn memory test: PASS (`7319` recovered);
- 5-turn stability/memory: PASS (`ALFA-482` recovered);
- no model reload between turns;
- SOURCE fallback `0`;
- persistent expert cache `false`;
- peak RSS `1,447,067,648 B`;
- swap safety PASS.

Real long-form metrics:
- TTFT `47.832 s`;
- decode-only `1.116 tok/s`;
- end-to-end `0.921 tok/s`;
- p50/p95 token wall `0.869 / 1.276 s`.

Five-turn TTFT / decode:
- T1 `29.013 s` / `0.789 tok/s`;
- T2 `48.049 s` / `1.226 tok/s`;
- T3 `21.830 s` / `1.426 tok/s`;
- T4 `20.699 s` / `1.305 tok/s`;
- T5 `26.003 s` / `1.331 tok/s`.

Final classification:
`LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`.

Only frozen READY-gate failure: long-form TTFT >30 s. Do not modify the threshold after the result.

## Immediate action

Review exact local source before any commit.

Need from local machine:
- SHA-256 of `scripts/loom_30b_interactive_v1_001.py`;
- complete source or exact new-file diff;
- `git status --short` to verify no accidental tracked changes.

Review goals:
- canonical backend remains imported/used without hidden mutation;
- PACKED only / zero SOURCE fallback;
- no payload cache;
- deterministic state/KV semantics;
- chat template and EOS handling correct;
- `/reset`, `/exit`, Ctrl-C/EOF teardown correct;
- persistent fd always closes;
- no test-only shortcuts leaking into CLI;
- no unrelated code.

If review PASS:
1. stage only interactive script;
2. `git diff --cached --check`;
3. commit/push;
4. pull canonical docs if updated;
5. user launches committed CLI for a real manual conversation.

Only after the manual session should this be frozen as **LOOM 30B v1 FUNCTIONAL_SLOW** practical comparator.

## After manual v1

Run matched practical 30B vs Qwen-family 8B vs 4B comparison measuring:
- TTFT;
- decode tok/s;
- RAM/swap;
- end-to-end time-to-correct-task;
- fixed practical intelligence across reasoning/math, coding/debugging, Italian explanation, structured instructions, supplied-context reasoning and planning/tool-use decisions.

Then decide between:
- 30B primary/deep;
- 8B/4B fast primary + 30B deep;
- skill/tool/protocol-centric small-model architecture.

Only after role selection open the Heretic-inspired refusal/steerability editing checkpoint. Separate R&D can later study TTFT/prefill optimization and materially new 30B speed mechanisms.