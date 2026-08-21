# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge / request-boundary active+allocator reclamation
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000K_ALLOCATOR_CACHE_RECLAMATION_PASS`
Next: `CAPABILITY_000L_FULL_SEQUENCE_BOUNDARY_RECLAMATION`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory, speed and capability.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.

ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical baseline

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- context 4096
- `prefill_step_size=512`
- built-in M1 `qmv_fast`
- raw weights `3,583,928,320 B`

REALGEN 001: 13.184615357 tok/s real generation; 12.046861457 tok/s E2E. REALGEN 002 custom M1 qmv transfer exact but -9.178832%; closed.

## Capability findings

### 000C — prefill frontier

Step 512 dominates canonical 2048 on the exact Pi prefill in both memory and speed while remaining bit-exact. Step 256 saves more peak memory but is slower and not bit-exact.

### 000D–000G — bridge / host lifecycle

A genuine Pi tool turn works. Later failures are not caused by intrinsic ~1500–1800-token request size. Scientific-process teardown is healthy and macOS naturally recovers >=60% free within ~3–5 s.

### 000H — sequential accumulation limit

All exact captured R1-R6 requests pass fresh. Sequential R2 fails because R1 leaves +468.30 MiB MLX active request-boundary state. Later prompt size, KV-capacity jumps and host variability are not primary causes.

### 000I — targeted request-local reclamation PASS

`ResponseGenerator._generate` retains a completed `GenerationBatch.Response`; its `prompt_cache` keeps finished-request KVCache objects alive after HTTP completion.

Targeted detach of only the stale completed response's `prompt_cache`:
- recovers 252.00 MiB MLX active;
- lowers R2 peak by 98.50 MiB;
- preserves response/tool behavior;
- uses no `gc.collect()` or global allocator cleanup.

Released storage largely moves into MLX allocator cache.

### 000J — full-sequence detach-only validation incomplete

The same targeted detach again recovers 252 MiB active after R1, but allocator cache rises ~231 -> 483 MiB and reaches ~713 MiB during R2. R2 still crosses 4% system free. This proved detach-only is insufficient for system headroom.

Report: `research/capability/capability-000j-full-sequence-reclamation-result.md`.

### 000K — ALLOCATOR CACHE RECLAMATION PASS

Report: `research/capability/capability-000k-allocator-cache-reclamation-result.md`.

One new factor was tested after the proven 000I detach: `mlx.core.clear_cache()` (`mx.clear_cache()`) exactly once at the completed-request boundary.

Measured boundary cost: **3.900 ms**.

After R1 targeted detach:
- active 3634.20 MiB
- allocator cache 486.23 MiB
- active+cache 4120.43 MiB

After one `mx.clear_cache()`:
- active unchanged 3634.20 MiB
- allocator cache **0.00 MiB**
- active+cache 3634.20 MiB
- recorded system free rises from 12% to 17%, then 19% before R2

R2:
- CONTROL detach-only minimum free **5%**
- TREATMENT detach + clear-cache minimum free **11%**
- gain **+6 percentage points**
- R2 completes in both arms
- semantic/tool equivalence PASS
- R2 intrinsic MLX peak remains ~4095.95 MiB; treatment improves system headroom rather than intrinsic request peak
- generation speed effectively unchanged in available measurement

Important telemetry caveat: 000K reported ~0.01 s prefill timing and a derived -24.45% delta. Those numbers are not comparable with the established ~20+ second canonical prefill measurements and are **not accepted as performance evidence**. Only the 3.900 ms cache-clear latency, memory/headroom result and semantic equivalence are promoted.

Interpretation: 000I releases stale completed-request live ownership; 000K returns the resulting allocator cache to system headroom. The combined boundary mechanism is now evidence-backed for R1->R2, but not yet promoted to real Pi until a full R1->R6 sequence validates bounded behavior.

## Exact next step

Run **CAPABILITY 000L — full-sequence request-boundary reclamation** from:
`research/capability/capability-000l-full-sequence-boundary-reclamation-plan.md`.

Compare two fresh processes using exact R1-R6:
1. CONTROL: natural sequential execution with no treatment;
2. TREATMENT: after every fully completed response, detach only its proven stale `prompt_cache`, then call `mx.clear_cache()` exactly once.

Primary questions:
- can treatment complete all R1-R6 without crossing <5% free;
- does active+cache remain bounded at request boundaries;
- does each cache clear remain low-cost;
- are response/tool semantics unchanged.

Actual M/prefill/generation instrumentation is optional and must not gate 000L unless measured correctly; the 000K ~0.01 s prefill values are not canonical.

Still forbidden: `gc.collect()`, model reload/restart between requests, model/context/KV/prompt/tool/prefill changes or host-memory manipulation.

If 000L passes, next is real Pi-loop reproducibility with the combined boundary mechanism, then CAPABILITY 001.

## Local-only implementation warning

Recent scripts/evidence remain local unless explicitly synchronized, including CAPABILITY 000A–000K scripts and raw `results-local/capability/...` evidence. Do not assume these files exist on GitHub until explicitly published.

## Later

1. CAPABILITY 000L full-sequence boundary reclamation
2. real Pi-loop reproducibility with promoted boundary mechanism if justified
3. CAPABILITY 001 frozen 12-task capability baseline
4. MEMORY-FRONTIER 001 real M1 RAM/tok/s partial-residency curve
5. async prefetch/buffering/direct range I/O
6. OUTCORE-BLOCK 001
7. scale toward 27B/32B
