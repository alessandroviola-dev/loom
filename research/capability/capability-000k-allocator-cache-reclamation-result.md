# CAPABILITY 000K — Allocator-cache boundary reclamation result

Date: 2026-08-21
Classification: `CAPABILITY_000K_ALLOCATOR_CACHE_RECLAMATION_PASS`

## Question

After the proven CAPABILITY 000I targeted detach of the completed response's stale `prompt_cache`, does explicitly releasing MLX allocator cache at the completed-request boundary recover useful system-memory headroom without changing model semantics?

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- `prefill_step_size=512`
- exact captured R1/R2 request bodies

## Treatment

CONTROL: proven 000I stale completed-response `prompt_cache` detach only.

TREATMENT: identical targeted detach followed by exactly one `mlx.core.clear_cache()` / `mx.clear_cache()` call at the completed-request boundary.

No `gc.collect()`, model reload, process restart between R1/R2, host-memory manipulation, or model/context/KV/prompt/tool/prefill changes.

## Result

Installed allocator-cache API used: `mlx.core.clear_cache()` (`mx.clear_cache()`).

Measured cache-release wall time: **3.900 ms**.

### Control boundary

After R1, detaching stale request-local KV moves storage from active to allocator cache rather than immediately returning it to the system:

- active after detach: **3634.20 MiB**
- allocator cache: **486.23 MiB**
- active + cache: **4120.43 MiB**
- system free: **13%** at the recorded boundary

R2 completes, but reaches only **5% minimum free memory**.

### Treatment boundary

After the same targeted detach and one `mx.clear_cache()`:

- active: **3634.20 MiB**
- allocator cache: **0.00 MiB**
- active + cache: **3634.20 MiB**
- system free rises from **12% to 17%** immediately after clear and to **19%** before R2 in the recorded trajectory

R2 completes with **11% minimum free memory**, versus 5% in control.

The explicit cache clear reclaims **486.23 MiB** allocator cache and improves R2 system-free headroom by **+6 percentage points**.

R2 MLX peak remains essentially unchanged at **4095.95 MiB**; the benefit is system-memory headroom, not lower intrinsic request peak.

## Semantic safety

PASS.

R1/R2 exact response text bytes, finish reason, tool names and tool arguments matched control. Raw SSE envelopes differed only in independently generated request IDs.

No semantic regression was observed.

## Timing nuance

The reported cache-clear boundary cost of 3.900 ms is valid and directly measured.

The harness also reported very small prefill wall values (~0.01 s) and a derived -24.45% treatment-vs-control prefill change. These values are not comparable to the established ~20+ second full-prefill measurements from earlier CAPABILITY experiments and are therefore **not promoted as scientific performance evidence**. CAPABILITY 000K supports the memory/headroom result and semantic equivalence; it does not establish a prefill speed improvement.

Generation speed was effectively unchanged in the available measurements (~+0.23%).

## Interpretation

CAPABILITY 000I fixed stale completed-request live ownership. CAPABILITY 000K shows why that fix alone did not improve system free memory: released storage remained in MLX allocator cache. Clearing allocator cache after the targeted detach converts the reclaimed request-local memory into real system-memory headroom at negligible measured boundary cost.

The combined boundary policy is now evidence-backed for R1->R2:

1. detach only the completed stale response's `prompt_cache`;
2. call `mx.clear_cache()` once after that request-local detach.

This combination is **not yet promoted to the real Pi bridge** until validated over the full captured R1->R6 sequence.

## Local evidence

`results-local/capability/capability-000k/20260821-192613/`

Local implementation:
- `scripts/capability_000k_allocator_cache_boundary.py`

These local files/evidence are not assumed to exist on GitHub until explicitly synchronized.
