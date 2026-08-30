# LOOM — Pi Agent Protocol

Version: 3.75
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not commit/push/PR/edit project decision docs unless explicitly authorized.
GitHub is canonical. Active clone: `<repository-root>`.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue/post-hoc gate relaxation;
3. fail closed before expensive execution;
4. invalid/inconclusive runs support no performance claim;
5. production code requires exact review + Git persistence;
6. do not tune on exposed evaluation examples;
7. hidden ground truth/spec metadata must never enter model repair/judge inputs unless explicitly preregistered as public input;
8. expensive model downloads require an explicit preregistered checkpoint.

## Product direction

**Big models. Small machines.**
- BALANCED: Qwen3-8B 3-bit/group64 Direct MLX, ~13 tok/s, provisional primary.
- DEEP: **Apple Metal MoE paging is canonical**. Model Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw, S24.
- Historical custom MLX ~1.4 tok/s is retained as historical comparison/fallback only.
- FAST: concept retained; legacy 4B parked.
- LOOM AUTO validator-first remains PAUSED during 30B acceleration.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## Canonical DEEP baseline

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Frontend:
`llama-completion -no-cnv`
SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Profile: S24.
Validated decode baseline: ~4.39–4.40 tok/s.

## Stage2 product validation — COMPLETE / GO

`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.
Apple S24 is canonical DEEP on product-utility grounds.

## Persistent/cache feasibility — COMPLETE / GO

`LOOM_30B_ACCEL_PERSISTENT_CACHE_FEASIBILITY_GO`.
No built `llama-server`; canonical `llama-completion` supports explicit `--prompt-cache`.

## Prompt Cache 001 — CLOSED MECHANICALLY

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-001-result.md`

Classification:
**`LOOM_30B_ACCEL_PROMPT_CACHE_MECHANICAL_NO_GO`**.

Evidence:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/`

Diagnostic observations only:
- median C/B prompt-eval ratio 0.04174;
- median C/B E2E ratio 0.08973;
- decode preservation 96.98%;
- cache creation/reuse mechanically proven.

Do not promote those ratios as a scientific GO because all nine invocations failed the frozen functional-validity rule.

Mechanical cause:
- frozen `-n 8` truncated target answer `4317` to `...porta 4`;
- warm answer contained correct `ambra` but exact-string validator rejected explanatory prose.

## Prompt Cache R1 001 — CLOSED MECHANICALLY BEFORE INFERENCE

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-r1-001-result.md`

Classification:
**`LOOM_30B_ACCEL_PROMPT_CACHE_R1_MECHANICAL_NO_GO`**.

Evidence:
`results-local/research/30b-accel-prompt-cache-r1-001/20260830T105237Z/`

R1 correctly stopped before inference.

Verified parent wrapper:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/prompt_cache_runner.py`
SHA256:
`1c62f4ab53e0c31bf3c725991d1f87a3f81cd75ab91d6da2e1b05bf8a499ba5e`

Mechanical defect:
- R1 required that wrapper unchanged;
- the wrapper hard-coded `-n 8`, exact-string validation and Prompt Cache 001 evidence/classification handling;
- therefore it could not implement the preregistered R1 mechanical deltas without violating its own freeze rule.

No inference and no new performance evidence occurred.

## Current checkpoint — Prompt Cache R2 001

Preregistration:
`research/architecture/loom-30b-accel-prompt-cache-r2-001-preregistration.md`

Scientific design remains frozen:
- canonical model/runtime/S24;
- exact stable prefix and suffixes;
- `-n 24`;
- frozen semantic validator: W contains standalone `ambra`, B/C contain standalone `4317`;
- 3 rounds B -> W -> C;
- fresh cache per round;
- only scientific factor is prompt-cache reuse;
- same primary threshold: median C/B prompt-eval wall <=0.70;
- E2E lower, decode >=90%, safe memory, complete evidence.

R2 harness repair only:
- verify frozen parent wrapper SHA above;
- preserve parent unchanged;
- derive a separate R2 wrapper before inference;
- only preregistered mechanical wrapper changes are allowed;
- synthetic-test without opening GGUF;
- freeze and persist derived-wrapper SHA before inference;
- no wrapper edits after inference begins.

## After Prompt Cache R2

Next decode-focused checkpoint: paging/I/O attribution. Measure expert paging cost before source-level prefetch/overlap work inspired by mini-SGLang.

Acceleration goal: protect ~4.39–4.40 tok/s, reach 5+ first, then investigate 6–9 tok/s without unacceptable quality/memory cost.
