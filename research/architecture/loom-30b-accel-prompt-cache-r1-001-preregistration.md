# LOOM 30B Acceleration Prompt Cache R1 001 — Preregistration

Date: 2026-08-30
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Recover `LOOM_30B_ACCEL_PROMPT_CACHE_001`, which closed `MECHANICAL_NO_GO` because the frozen `-n 8` output budget truncated the target answer and the exact-string validator rejected a semantically correct warm answer.

The scientific factor remains unchanged: explicit `llama-completion --prompt-cache` reuse of an exact stable prefix versus cache-disabled baseline.

The only recovery deltas are mechanical:
1. generation budget increases from `-n 8` to `-n 24` to prevent answer truncation;
2. functional validation checks frozen semantic answer content rather than exact surface form.

No inference from the invalid prior run is used to relax the acceleration thresholds.

## Frozen canonical DEEP

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Existing verified local artifact:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Required size:
`12,424,439,872` bytes

Required SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Frontend:
`llama-completion`

Required SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Profile:
S24 only.

Common flags:
`-n 24 -c 1024 --temp 0 --moe-n-slots 24 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -ub 1 -no-cnv`

No model/runtime/source/package mutation is authorized.

## Frozen prompts

Reuse byte-for-byte the exact stable prefix, warm suffix and target suffix from:
`research/architecture/loom-30b-accel-prompt-cache-001-preregistration.md`.

Do not edit prompt text.

Expected semantic facts:
- warm question: Atlas color = `ambra`;
- target question: Vega port = `4317`.

## Functional validator

Validation operates only on retained generated answer text after removing runtime/session-save diagnostics and surrounding whitespace.

Warm W is valid iff:
- answer contains case-insensitive standalone word `ambra`.

Target B/C is valid iff:
- answer contains standalone decimal token `4317`.

Additional prose is allowed.
A truncated `4`, `43`, or `431` is invalid.
Any explicit contradictory answer for the requested fact is invalid.

The validator rules are frozen before execution and must not be changed after any model result.

## Experiment design

Run three independent rounds. Use a fresh prompt-cache file per round.

Each round, exact order:
1. **B** — cache-disabled target, fresh process, no `--prompt-cache`;
2. **W** — warm prompt, fresh process, fresh `--prompt-cache <round-file>`;
3. **C** — target prompt, fresh process, exact same round cache file.

Do not reuse cache files across rounds.
Do not retry a scientifically valid invocation.

## Instrumentation

Reuse the already-frozen research orchestration wrapper from Prompt Cache 001 if its exact SHA256 is available and unchanged. If unavailable or modified, STOP mechanically; do not create a new wrapper during R1.

Fresh evidence root:
`results-local/research/30b-accel-prompt-cache-r1-001/<timestamp>/`

Persist before each child launch:
- round/condition;
- exact command;
- prompt hash and byte length;
- model/source/frontend/wrapper provenance;
- cache path and pre-launch existence/size;
- RUNNING state/start time.

Persist after each invocation:
- exit state;
- bounded complete output;
- cleaned generated answer used by validator;
- runtime timing rows;
- prompt token count where observable;
- generated tokens;
- generation tok/s;
- prompt/prefill wall and tok/s where observable;
- load time separately;
- E2E wall;
- cache post-run existence/size/hash;
- cache reuse/hit evidence;
- RSS/wired/compressed/swap/pressure;
- cleanup proof.

## Primary metric

For each round:
`C_prompt_eval_wall / B_prompt_eval_wall`

Aggregate by median across three rounds.

Direct trustworthy runtime prompt-eval wall is required. No post-hoc substitute metric.

## Secondary metrics

- target E2E C/B;
- prompt tokens evaluated/reused where observable;
- cache size/load behavior;
- generation tok/s C/B;
- memory/swap.

## Frozen GO gate

`LOOM_30B_ACCEL_PROMPT_CACHE_R1_GO` only if all are true:

1. exact model/source/frontend/wrapper provenance verified;
2. 3/3 B, W and C invocations complete and pass the frozen semantic validator;
3. cache file created by each W and reused by corresponding C;
4. direct runtime evidence computes prompt-eval wall for every B and C;
5. median `C_prompt_eval_wall / B_prompt_eval_wall <= 0.70`;
6. median target E2E C/B `< 1.00`;
7. median C generation tok/s >=90% of median B generation tok/s;
8. no critical memory pressure/OOM/output runaway/corruption;
9. peak swap every invocation <=3.5 GiB;
10. complete durable evidence;
11. zero model/source/runtime/package mutation.

Valid complete measurements failing an acceleration/product gate:
`LOOM_30B_ACCEL_PROMPT_CACHE_R1_NO_GO`.

Provenance/instrumentation/cache compatibility preventing valid comparison:
`LOOM_30B_ACCEL_PROMPT_CACHE_R1_MECHANICAL_NO_GO`.

## Interpretation

A GO establishes prompt-cache reuse as a canonical DEEP prefill/E2E optimization under a stable-prefix workload.
It does not establish higher decode throughput than the ~4.39–4.40 tok/s canonical baseline.

After R1, regardless of scientific GO/NO_GO, proceed to paging/I/O attribution unless another mechanical repair is required.

## Boundaries

Forbidden:
- model download/copy/requantization;
- source/runtime patch;
- binary build/rebuild;
- package install;
- alternate slot count;
- changing `-ub 1`;
- prompt modification;
- validator modification after results begin;
- valid-run retry;
- expert-prefetch implementation;
- mini-SGLang source port;
- Caveman integration;
- production/provider/UI work;
- Pi Git commit/push.
