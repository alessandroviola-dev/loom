# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000K_ALLOCATOR_CACHE_RECLAMATION_PASS`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## Canonical 8B baseline

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2. REALGEN 001 = 13.184615357 tok/s real generation and 12.046861457 tok/s E2E.

## A — Capability baseline — ACTIVE

### 000C — prefill frontier

`prefill_step_size=512` dominates canonical 2048 on the exact Pi prefill and remains the active integrated-agent candidate.

### 000H — sequential accumulation

All captured R1-R6 requests pass fresh. Sequential R2 fails because R1 leaves +468.30 MiB active request-boundary MLX state.

### 000I — targeted request-local reclamation PASS

The stale completed `GenerationBatch.Response.prompt_cache` retains finished-request KV. Targeted detach recovers 252.00 MiB active MLX and preserves model/tool behavior.

### 000J — detach-only insufficient

Full-sequence attempt shows active memory recovery largely moves into MLX allocator cache. R2 still hits the system-free floor. This directly justifies allocator-cache treatment as the next isolated factor.

### 000K — ALLOCATOR CACHE RECLAMATION PASS

Report: `research/capability/capability-000k-allocator-cache-reclamation-result.md`.

After the proven stale-response detach, one `mx.clear_cache()` call:
- reclaims **486.23 MiB** allocator cache;
- leaves active MLX unchanged;
- raises R2 minimum system free from **5% to 11%** (+6 pp);
- costs **3.900 ms** at the measured boundary;
- preserves R1/R2 response/tool semantics;
- does not alter the intrinsic R2 MLX peak (~4095.95 MiB).

The reported ~0.01 s prefill timings in 000K are not comparable to canonical ~20+ s prefill measurements and are not promoted as performance evidence. The valid promoted results are memory/headroom, semantic equivalence and cache-clear boundary latency.

### 000L — NEXT

Frozen plan: `research/capability/capability-000l-full-sequence-boundary-reclamation-plan.md`.

Validate exact R1->R6 with two fresh processes:
1. control = natural sequential execution;
2. treatment = after each completed response, detach only the proven stale `prompt_cache` and call `mx.clear_cache()` exactly once.

Measure per-turn active/cache/active+cache boundaries, system-free floor, swap, cache-clear latency and semantic/tool equivalence.

Full PASS requires all R1-R6 treatment requests to complete without crossing the resource gate and without semantic/lifecycle regression.

No `gc.collect()`, model reload/restart between requests, host manipulation, or model/context/KV/prompt/tool/prefill changes.

### CAPABILITY 001 — BLOCKED

Frozen 12-task coding + Git safety + experimental-reasoning baseline. Run only after real Pi multi-turn execution has reproducible headroom.

## B — RAM/speed frontier

After CAPABILITY 001, run MEMORY-FRONTIER 001 with controlled partial residency and measure resident bytes, MLX peak, system free/swap, SSD bytes/token, real tok/s, TTFT and correctness.

## C — Hide SSD cost

Then isolate async prefetch, double/triple buffering, transfer chunk sizing, direct safetensors range I/O, macOS page-cache behavior and resident-hotset selection.

## D — Amortize I/O across tokens

OUTCORE-BLOCK 001 revisits M>1 for out-of-core execution where one weight load can serve multiple positions.

## E — Representation without shrinking parameter count

Later candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core storage formats. Judge each by memory + speed + capability.

## F — Scale beyond 8B

1. solve architecture on well-characterized 8B;
2. transfer to models exceeding comfortable physical RAM;
3. reach 27B/32B-class full-parameter generation on M1 8 GB without OOM;
4. optimize toward interactive speed.

## Immediate order

1. CAPABILITY 000L full-sequence boundary reclamation
2. real Pi-loop reproducibility with combined detach + allocator-cache clear if 000L passes
3. CAPABILITY 001
4. MEMORY-FRONTIER 001
5. prefetch/buffering/range-I/O
6. OUTCORE-BLOCK 001
7. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence currently exist only in the local worktree and `results-local/` unless explicitly synchronized.
