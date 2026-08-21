# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge / allocator-cache boundary pressure
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000J_INFRASTRUCTURE_INCOMPLETE_WITH_ALLOCATOR_CACHE_PRESSURE`
Next: `CAPABILITY_000K_ALLOCATOR_CACHE_BOUNDARY_RECLAMATION`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual reports.

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
- capability context 4096
- `prefill_step_size=512`
- built-in M1 `qmv_fast`
- raw weights `3,583,928,320 B`

REALGEN 001 practical baseline: 13.184615357 tok/s real generation, 12.046861457 tok/s E2E. REALGEN 002 custom M1 qmv transfer was exact but -9.178832%; closed.

## Capability findings

### 000C — prefill frontier

On the exact Pi prefill, step 512 beats canonical 2048 in both speed and memory and remains bit-exact. Step 256 saves more peak memory but is slower and not bit-exact.

### 000D–000G — bridge and host lifecycle

A genuine Pi tool turn works. Later request failures are not explained by intrinsic ~1500-1800-token request size. Host/process teardown is healthy and macOS naturally recovers launch headroom within ~3-5 s.

### 000H — sequential accumulation limit

Exact captured R1-R6 span 1518 -> 1820 tokens. All pass fresh. Sequential R2 fails because R1 leaves +468.30 MiB active MLX request-boundary state. Later request size, KV-capacity jumps and host variability are not the primary cause.

### 000I — targeted request-local reclamation PASS

`mlx_lm.server.ResponseGenerator._generate` retains the completed local `GenerationBatch.Response`, whose `prompt_cache` keeps the finished request's 36 KVCache objects alive after HTTP completion.

Targeted detach of only this stale completed-response `prompt_cache` after R1:
- recovers 252.00 MiB active MLX;
- reduces R2 peak by 98.50 MiB;
- preserves R1 response/tool behavior and R2 first tool call;
- uses no global cleanup.

However released active storage largely moves into MLX allocator cache, so system-free headroom did not improve in the two-turn test.

### 000J — full-sequence validation incomplete

Report: `research/capability/capability-000j-full-sequence-reclamation-result.md`.

CONTROL:
- R1 completed;
- R2 resource-aborted at 4% free;
- peak MLX 4194.45 MiB.

TREATMENT (000I detach after R1):
- R1 completed;
- active 3886.20 -> 3634.20 MiB: 252.00 MiB recovered;
- allocator cache 231.07 -> 483.07 MiB;
- R2 still resource-aborted at 4% free;
- allocator cache reached ~712.95 MiB during the aborted R2;
- no global cleanup;
- R1 semantic/tool equivalence passed.

Classification: `CAPABILITY_000J_INFRASTRUCTURE_INCOMPLETE` because R2 did not complete and required actual-M/prefill/generation timing instrumentation was unavailable.

Scientific interpretation: the 000I lifecycle fix is real and lowers live/peak pressure, but by itself does not extend the safe sequence because allocator cache remains charged against system memory. This is now the first justified next factor.

## Exact next step

Run **CAPABILITY 000K — allocator-cache boundary reclamation** from:
`research/capability/capability-000k-allocator-cache-boundary-plan.md`.

Use exact captured R1/R2. Compare:
1. CONTROL = proven 000I stale-response `prompt_cache` detach only;
2. TREATMENT = same detach + one explicit documented MLX allocator-cache clear at the completed-request boundary.

Measure active/cache/system-free before and after the cache clear, boundary latency, R2 peak/completion and semantic/tool equivalence.

This is now an allowed isolated factor because 000J directly demonstrated allocator-cache growth as the remaining pressure source.

Still forbidden: `gc.collect()`, model reload/restart between R1/R2, model/context/KV/prompt/tool/prefill changes or host-memory manipulation.

Only if 000K passes should a full R1-R6 cache-boundary validation or real Pi-loop reproducibility run be considered.

## Local-only implementation warning

Recent scripts/evidence remain local unless explicitly synchronized, including all CAPABILITY 000A–000J scripts and raw `results-local/capability/...` evidence. Do not assume local scripts exist on GitHub until explicitly published.

## Later

1. CAPABILITY 000K allocator-cache boundary test
2. full-sequence / integrated Pi validation if justified
3. CAPABILITY 001 frozen 12-task capability baseline
4. MEMORY-FRONTIER 001 real M1 RAM/tok/s partial-residency curve
5. async prefetch/buffering/direct range I/O
6. OUTCORE-BLOCK 001
7. scale toward 27B/32B
