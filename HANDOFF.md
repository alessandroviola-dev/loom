# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — Apple Metal MoE paging S24 is canonical `loom-deep`. Prompt Cache R2 completed GO and is now a validated canonical prefill/E2E optimization for stable-prefix workloads. Current checkpoint is Paging/I/O Attribution Preflight 001, which must prove a non-mutating observation path before the real decode attribution run.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_001`
Pi context: `/AGENTS.md` v3.76.

## Canonical DEEP

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Runtime:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
with `llama-completion -no-cnv` SHA256 `38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

Profile: S24.
Validated decode baseline: ~4.39–4.40 tok/s.

Stage2 product result:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.
Apple S24 is canonical DEEP.

## Prompt Cache 001 — historical MECHANICAL_NO_GO

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/`

Diagnostic cache acceleration was observed but the frozen functional validator invalidated all invocations. Do not promote its ratios as scientific results.

## Prompt Cache R1 — historical MECHANICAL_NO_GO before inference

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-r1-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-r1-001/20260830T105237Z/`

R1 stopped correctly because its wrapper-freeze contract was internally incompatible with its authorized recovery deltas. No inference and no performance evidence occurred.

## Prompt Cache R2 — GO

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-r2-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-r2-001/20260830T105738Z/`

Preflight:
- parent wrapper SHA verified/preserved: `1c62f4ab53e0c31bf3c725991d1f87a3f81cd75ab91d6da2e1b05bf8a499ba5e`;
- derived R2 wrapper frozen before inference: `3550d56e0fee1adcf08ae95fcb1ae8fcf50c740147bae036745ab28f0db68ccd`;
- 13 synthetic validator/harness checks passed without GGUF access.

Validated measurements:
- 9/9 cleaned outputs passed the frozen semantic validator;
- prompt-eval C/B ratios: `0.04013`, `0.04031`, `0.04025`; median **`0.04025`**;
- E2E C/B ratios: `0.10193`, `0.10932`, `0.10751`; median **`0.10751`**;
- median B/C generation: `3.49 / 3.47 tok/s`;
- decode preservation: **`99.43%`**;
- every W created and every C reused its round cache;
- cache size `26,449,272` bytes;
- cache SHA256 `f96f9fb61f6e2302fb206932a4ca497c8a1ccbe7346c22b20bc0678094dd5a99`;
- C loaded 269-token sessions and matched 262/269 prompt tokens;
- peak RSS `2948.83 MiB`;
- peak swap `1267.56 MiB`;
- all 14 frozen gates passed.

Classification:
**`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`**.

Scientific interpretation:
prompt cache is now validated for canonical DEEP stable-prefix prompt/prefill and E2E acceleration. It is not a decode-throughput optimization and does not change the canonical ~4.39–4.40 tok/s decode baseline.

## Exact next action — Paging/I/O Attribution Preflight 001

Preregistration:
`research/architecture/loom-30b-accel-paging-io-attribution-preflight-001-preregistration.md`

Purpose:
validate a non-mutating observation path before spending a model run on paging/I/O attribution.

Pinned-source facts:
- `llama_moe_offloader::resolve(...)` tracks LRU hits/misses;
- an expert miss schedules one `pread_pool(...)` task for each bound pool;
- `pread_pool(...)` performs synchronous `pread(...)` until the expert-pool stride is fully read;
- multiple tasks may run through `dispatch_apply`;
- sidecar completion is signaled only after `resolve(...)` completes;
- `total_hits` / `total_misses` exist internally but are not exposed by the inspected public interface.

Preflight requirements:
- do not open the GGUF;
- do not run inference;
- inspect already-installed native macOS instrumentation only;
- use a frozen deterministic synthetic `os.pread` process to validate candidate tracing;
- require per-process isolation, durable raw evidence and deterministic parsing;
- at least one high-value observable among direct read count/bytes/timing/offset must validate against synthetic ground truth;
- freeze one selected observation method for the later actual attribution run;
- no source patch, rebuild, package install, dynamic interposition or security-setting change.

## After preflight

If GO:
preregister the actual canonical S24 paging/I/O inference attribution using the validated method.

If NO_GO:
preregister a separate instrumentation strategy before any source-level measurement patch/rebuild is permitted.

Only after actual attribution demonstrates a meaningful expert-I/O bottleneck should LOOM preregister expert prefetch/overlap work.

Acceleration target remains: 5+ decode tok/s first, then investigate 6–9 tok/s. Caveman-style context packing remains later end-to-end work.
