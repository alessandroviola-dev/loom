# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — Apple Metal MoE paging S24 is canonical `loom-deep`. Prompt Cache R2 is validated GO for stable-prefix prefill/E2E. External non-mutating paging/I/O tracing preflight completed scientific NO_GO because the current macOS session could not validate a high-value per-process read observable. Current checkpoint is source-level paging/I/O instrumentation design only; no source patch/build/model run is yet authorized.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_ACCEL_PAGING_IO_INSTRUMENTATION_DESIGN_001`
Pi context: `/AGENTS.md` v3.77.

## Canonical DEEP

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Runtime:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
with `llama-completion -no-cnv` SHA256 `38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

Profile: S24.
Validated fresh-process decode baseline: ~4.39–4.40 tok/s.

Stage2 product result:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.
Apple S24 is canonical DEEP.

## Prompt Cache R2 — GO

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-r2-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-r2-001/20260830T105738Z/`

Validated measurements:
- all 14 frozen gates passed;
- 9/9 functionally valid invocations;
- median C/B prompt-eval ratio `0.04025`;
- median C/B E2E ratio `0.10751`;
- median B/C generation `3.49 / 3.47 tok/s`;
- decode preservation `99.43%`;
- cache reuse directly confirmed;
- peak RSS `2948.83 MiB`;
- peak swap `1267.56 MiB`.

Scientific interpretation:
prompt cache is a validated canonical DEEP prefill/E2E optimization for stable-prefix workloads. It is not direct decode acceleration and does not change the canonical ~4.39–4.40 tok/s decode baseline.

Historical Prompt Cache 001 and R1 remain MECHANICAL_NO_GO and must not be promoted as scientific results.

## Paging/I/O Attribution Preflight 001 — NO_GO

Canonical result:
`research/architecture/loom-30b-accel-paging-io-attribution-preflight-001-result.md`

Evidence:
`results-local/research/30b-accel-paging-io-attribution-preflight-001/20260830T111709Z/`

Classification:
**`LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_NO_GO`**.

Frozen synthetic probe:
- 5 deterministic `os.pread` reads;
- offsets `0`, `4096`, `16384`, `32768`, `49152`;
- aggregate requested/returned bytes `15,872`;
- probe SHA256 `0ee66ce40e5865c6288a9ea259b02d7e46d58d3086ca4cc99dd6253c623e095d`;
- deterministic parser SHA256 `46e996b911b177a0695b8d70edd816b7b606ec1c3c5fef5bb37bf5ff0883797c`.

Result:
- provenance/no-GGUF/no-mutation/evidence/cleanup gates passed;
- tested native tracers did not yield usable read observations under the current session constraints;
- no high-value direct read observable A-C was validated;
- no method was selected for inference attribution.

Scientific meaning:
external non-mutating tracing is not sufficient in the current environment. This result makes no claim about whether expert paging is a decode bottleneck.

## Current — Paging/I/O Instrumentation Design 001

Preregistration:
`research/architecture/loom-30b-accel-paging-io-instrumentation-design-001-preregistration.md`

Purpose:
design, without implementing, the minimum source-level measurement instrumentation needed for later canonical S24 paging/I/O attribution.

Pinned source facts:
- `moe_layer` already contains `total_hits` / `total_misses`;
- `resolve(...)` updates LRU hit/miss state;
- misses schedule one `pread_pool(...)` task per bound expert pool;
- `pread_pool(...)` loops on `pread(...)` until the pool stride is transferred;
- read tasks may execute concurrently via `dispatch_apply`;
- sidecar completion is signaled after `resolve(...)` completes.

The design checkpoint must freeze:
- exact minimal source locations;
- exact direct counters and timing semantics;
- race-free atomic/non-atomic update policy;
- one final non-hot-path statistics emission point;
- deterministic machine-readable output schema;
- exact direct claims vs forbidden interpretations;
- overhead-validation policy for a later instrumented binary.

No GGUF, inference, source edit, rebuild, package install, runtime mutation or prefetch implementation is allowed in this checkpoint.

## Planned sequence after design

If instrumentation design GO:
1. preregister measurement-only instrumentation implementation/build;
2. produce a separate instrumented binary with frozen diff and SHA;
3. preregister canonical-vs-instrumented overhead calibration;
4. only if perturbation is acceptable, run instrumented canonical S24 paging/I/O attribution;
5. only if attribution demonstrates a material I/O bottleneck with overlap headroom, preregister expert-prefetch/overlap intervention.

Acceleration target remains: protect ~4.39–4.40 tok/s, reach 5+ first, then investigate 6–9 tok/s. Caveman context packing remains later work.
