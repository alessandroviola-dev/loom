# LOOM — Pi Agent Protocol

Version: 3.76
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

## Prompt Cache R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-r2-001-result.md`

Classification:
**`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`**.

Evidence:
`results-local/research/30b-accel-prompt-cache-r2-001/20260830T105738Z/`

Validated stable-prefix prompt-cache result:
- 9/9 functionally valid invocations;
- median C/B prompt-eval ratio `0.04025`;
- median C/B E2E ratio `0.10751`;
- median B/C generation `3.49 / 3.47 tok/s`;
- decode preservation `99.43%`;
- cache size `26,449,272` bytes;
- cache SHA256 `f96f9fb61f6e2302fb206932a4ca497c8a1ccbe7346c22b20bc0678094dd5a99`;
- C loaded 269-token sessions and matched 262/269 prompt tokens;
- peak RSS `2948.83 MiB`;
- peak swap `1267.56 MiB`;
- all 14 frozen gates passed.

Prompt cache is now a validated canonical DEEP **prefill/E2E optimization for stable-prefix workloads**.
It is not direct decode acceleration and does not replace the ~4.39–4.40 tok/s canonical decode baseline.

Historical Prompt Cache 001 and R1 remain closed MECHANICAL_NO_GO and must not be promoted as scientific performance results.

## Current checkpoint — Paging/I/O Attribution Preflight 001

Preregistration:
`research/architecture/loom-30b-accel-paging-io-attribution-preflight-001-preregistration.md`

Purpose:
prove a non-mutating observation method before the real S24 paging/I/O attribution run.

Pinned-source facts already established:
- Apple MoE offloader tracks LRU hits/misses internally;
- misses create expert-pool `pread(...)` tasks;
- pool reads are synchronous within `pread_pool(...)` and may be parallelized across tasks with `dispatch_apply`;
- sidecar completion is signaled only after `resolve(...)` completes;
- internal hit/miss counters are present but not exposed by the inspected interface.

This preflight must:
- NOT open the GGUF;
- NOT run inference;
- inventory already-installed macOS observation tools;
- validate candidate tracing against a frozen synthetic `os.pread` process;
- require durable raw output and deterministic parsing;
- select one non-mutating method only if a high-value per-process read observable is validated;
- make no performance claim.

Forbidden in this checkpoint:
- source patch/rebuild;
- dynamic interposition;
- package install;
- SIP/security changes;
- runtime/model mutation;
- prefetch/overlap implementation;
- Git commit/push by Pi.

## After attribution preflight

If GO: preregister the actual canonical S24 inference paging/I/O attribution using the validated observation method.

If NO_GO: preregister a separate instrumentation strategy before any source-level measurement patch is allowed.

Only after actual attribution supports an I/O bottleneck may LOOM preregister expert-prefetch/overlap intervention.

Acceleration goal remains: protect ~4.39–4.40 tok/s, reach 5+ first, then investigate 6–9 tok/s without unacceptable quality/memory cost.
