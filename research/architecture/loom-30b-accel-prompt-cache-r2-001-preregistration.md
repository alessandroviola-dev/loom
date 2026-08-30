# LOOM 30B Acceleration Prompt Cache R2 001 — Preregistration

Date: 2026-08-30
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Recover `LOOM_30B_ACCEL_PROMPT_CACHE_R1_001`, which stopped before inference because its contract required reuse of the frozen Prompt Cache 001 wrapper unchanged even though that wrapper hard-coded the exact mechanical conditions R1 was created to replace.

R2 does not change the scientific factor, prompts, model, runtime, profile, ordering, metrics, thresholds or interpretation.

R2 only repairs the research harness contract by authorizing creation of a separate derived R2 wrapper before inference, then freezing that derived wrapper.

No prior diagnostic timing result is used to relax any gate.

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

## Frozen functional validator

Validation operates only on retained generated answer text after removing runtime/session-save diagnostics and surrounding whitespace.

Warm W is valid iff:
- answer contains case-insensitive standalone word `ambra`.

Target B/C is valid iff:
- answer contains standalone decimal token `4317`.

Additional prose is allowed.
A truncated `4`, `43`, or `431` is invalid.
Any explicit contradictory answer for the requested fact is invalid.

These rules are frozen before execution and must not be changed after any model result.

## R2 wrapper derivation — explicitly authorized mechanical repair

Frozen parent wrapper:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/prompt_cache_runner.py`

Required parent SHA256:
`1c62f4ab53e0c31bf3c725991d1f87a3f81cd75ab91d6da2e1b05bf8a499ba5e`

Before any inference:
1. verify the parent wrapper exists and its observed SHA256 exactly matches the required parent SHA256;
2. preserve the parent file unchanged;
3. create a separate R2 research wrapper derived from that verified parent;
4. only the changes listed below are authorized;
5. synthetic-test the derived wrapper without opening the GGUF;
6. compute and persist the derived wrapper SHA256;
7. freeze the derived wrapper before the first model invocation;
8. after the first model invocation begins, any wrapper edit invalidates R2 mechanically.

Authorized derived-wrapper changes only:
- generation budget from `-n 8` to `-n 24`;
- exact-string validator replaced by the frozen semantic validator above;
- generated-answer cleaning needed to remove runtime/session-save diagnostics before semantic validation;
- experiment/evidence identifiers and paths changed from Prompt Cache 001/R1 to R2 so evidence is isolated under the R2 root;
- classifications/messages updated only as required to report R2 GO/NO_GO/MECHANICAL_NO_GO consistently;
- synthetic-test fixtures/assertions needed to validate those mechanical changes before inference.

Forbidden wrapper changes include:
- prompt text or prompt construction;
- B/W/C order;
- number of rounds;
- cache-file reuse semantics;
- common model/runtime/profile flags other than the preregistered `-n 24` recovery delta;
- timing definitions;
- telemetry definitions;
- scientific metrics or thresholds;
- retry policy;
- model/source/runtime/package behavior.

If the parent SHA cannot be verified, or a valid derived wrapper cannot be frozen before inference, STOP mechanically.

## Required synthetic validator checks before inference

Without opening the GGUF, demonstrate at minimum that the frozen validator:
- accepts `ambra`;
- accepts explanatory prose containing standalone `ambra`;
- accepts case variation of `ambra`;
- rejects a warm answer that does not contain standalone `ambra`;
- accepts `4317`;
- accepts explanatory prose containing standalone `4317`;
- rejects `4`, `43`, and `431` as target answers;
- rejects a number that merely contains `4317` as a non-standalone substring;
- rejects an explicit contradictory answer for the requested fact;
- validates retained generated answer text rather than runtime/session diagnostics.

Persist synthetic-test results and the frozen derived-wrapper SHA before inference.

## Experiment design

Run three independent rounds. Use a fresh prompt-cache file per round.

Each round, exact order:
1. **B** — cache-disabled target, fresh process, no `--prompt-cache`;
2. **W** — warm prompt, fresh process, fresh `--prompt-cache <round-file>`;
3. **C** — target prompt, fresh process, exact same round cache file.

Do not reuse cache files across rounds.
Do not retry a scientifically valid invocation.

## Instrumentation

Fresh evidence root:
`results-local/research/30b-accel-prompt-cache-r2-001/<timestamp>/`

Persist before each child launch:
- round/condition;
- exact command;
- prompt hash and byte length;
- model/source/frontend/parent-wrapper/derived-wrapper provenance;
- derived-wrapper SHA256;
- cache path and pre-launch existence/size;
- RUNNING state/start time.

Persist after each invocation:
- exit state;
- bounded complete output;
- cleaned generated answer used by validator;
- functional validator result;
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

`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO` only if all are true:

1. exact model/source/frontend provenance verified;
2. frozen parent wrapper SHA verified and parent preserved unchanged;
3. derived R2 wrapper contains only authorized changes, passes synthetic tests and is frozen with recorded SHA before inference;
4. 3/3 B, W and C invocations complete and pass the frozen semantic validator;
5. cache file created by each W and reused by corresponding C;
6. direct runtime evidence computes prompt-eval wall for every B and C;
7. median `C_prompt_eval_wall / B_prompt_eval_wall <= 0.70`;
8. median target E2E C/B `< 1.00`;
9. median C generation tok/s >=90% of median B generation tok/s;
10. no critical memory pressure/OOM/output runaway/corruption;
11. peak swap every invocation <=3.5 GiB;
12. complete durable evidence;
13. zero model/source/runtime/package mutation;
14. no derived-wrapper mutation after inference begins.

Valid complete measurements failing an acceleration/product gate:
`LOOM_30B_ACCEL_PROMPT_CACHE_R2_NO_GO`.

Provenance/instrumentation/cache/wrapper incompatibility preventing valid comparison:
`LOOM_30B_ACCEL_PROMPT_CACHE_R2_MECHANICAL_NO_GO`.

## Interpretation

A GO establishes prompt-cache reuse as a canonical DEEP prefill/E2E optimization under this stable-prefix workload.

It does not establish higher decode throughput than the ~4.39–4.40 tok/s canonical baseline.

After R2, regardless of scientific GO/NO_GO, proceed to paging/I/O attribution unless another mechanical defect prevents a valid run.

## Boundaries

Forbidden:
- model download/copy/requantization;
- source/runtime patch;
- binary build/rebuild;
- package install;
- alternate slot count;
- changing `-ub 1`;
- prompt modification;
- validator modification after inference begins;
- derived-wrapper modification after inference begins;
- valid-run retry;
- expert-prefetch implementation;
- mini-SGLang source port;
- Caveman integration;
- production/provider/UI work;
- Pi Git commit/push.
