# LOOM — Pi Agent Protocol

Version: 3.77
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
- Historical custom MLX ~1.4 tok/s is historical comparison/fallback only.
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
Validated fresh-process decode baseline: ~4.39–4.40 tok/s.

## Prompt Cache R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-r2-001-result.md`

Classification:
**`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`**.

Validated stable-prefix result:
- median C/B prompt-eval ratio `0.04025`;
- median C/B E2E ratio `0.10751`;
- decode preservation `99.43%`;
- all 14 frozen gates passed.

Prompt cache is canonical for stable-prefix prefill/E2E optimization only. It does not replace the decode baseline.

## Paging/I/O Attribution Preflight 001 — COMPLETE / NO_GO

Canonical result:
`research/architecture/loom-30b-accel-paging-io-attribution-preflight-001-result.md`

Evidence:
`results-local/research/30b-accel-paging-io-attribution-preflight-001/20260830T111709Z/`

Classification:
**`LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_NO_GO`**.

The frozen deterministic `os.pread` probe executed successfully, but the tested native tracing path yielded no usable read observations under the current session constraints. No high-value observable A-C was validated and no observation method was selected.

No GGUF/model access, inference, source/runtime/package/security mutation, rebuild, or Pi Git action occurred.

This NO_GO makes no claim about whether expert paging is a decode bottleneck.

## Current checkpoint — Paging/I/O Instrumentation Design 001

Preregistration:
`research/architecture/loom-30b-accel-paging-io-instrumentation-design-001-preregistration.md`

Purpose:
freeze the minimum source-level measurement design before any patch/build is authorized.

Pinned source facts:
- `moe_layer` already has `total_hits` / `total_misses`;
- `resolve(...)` handles LRU hits/misses;
- misses schedule `pread_pool(...)` tasks per bound pool;
- `pread_pool(...)` performs the actual `pread(...)` loop;
- tasks may run concurrently through `dispatch_apply`;
- sidecar completion follows `resolve(...)` completion.

This checkpoint must define only:
- exact source locations;
- exact counters/timers and semantics;
- atomic vs single-thread update requirements;
- final non-hot-path emission point;
- machine-parseable output schema;
- direct claims vs forbidden interpretations;
- later overhead-validation policy.

Forbidden in this checkpoint:
- GGUF/model access;
- inference;
- source patch/edit;
- build/rebuild;
- package install;
- runtime mutation;
- security changes;
- prefetch/overlap implementation;
- Pi Git commit/push.

## After instrumentation design

If GO:
1. preregister measurement-only instrumentation implementation/build;
2. freeze exact diff and instrumented binary SHA;
3. separately preregister canonical-vs-instrumented overhead calibration;
4. only after acceptable perturbation, run instrumented canonical S24 paging/I/O attribution;
5. only if attribution supports an I/O bottleneck with overlap headroom, preregister expert-prefetch/overlap.

Acceleration goal remains: protect ~4.39–4.40 tok/s, reach 5+ first, then investigate 6–9 tok/s without unacceptable quality/memory cost.
