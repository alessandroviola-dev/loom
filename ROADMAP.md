# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000J_INFRASTRUCTURE_INCOMPLETE_WITH_ALLOCATOR_CACHE_PRESSURE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## Canonical 8B baseline

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2. REALGEN 001 = 13.184615357 tok/s real generation and 12.046861457 tok/s E2E.

## A — Capability baseline — ACTIVE

### 000C — prefill frontier

Step 512 dominates canonical 2048 on the exact Pi prefill and remains the active integrated-agent candidate.

### 000H — sequential accumulation

All captured R1-R6 requests pass fresh. Sequential R2 fails because R1 leaves +468.30 MiB active request-boundary MLX state.

### 000I — targeted request-local reclamation PASS

The stale completed `GenerationBatch.Response.prompt_cache` retains finished-request KV. Targeted detach recovers 252.00 MiB active MLX and lowers R2 peak by 98.50 MiB without semantic/tool changes or global cleanup.

### 000J — full-sequence validation incomplete

The same detach again recovers 252.00 MiB active after R1, but allocator cache rises from ~231 to ~483 MiB and reaches ~713 MiB during R2. R2 still crosses the 4% free-memory gate. Therefore the request-local fix is valid but not sufficient by itself.

Report: `research/capability/capability-000j-full-sequence-reclamation-result.md`.

### 000K — NEXT

Frozen plan: `research/capability/capability-000k-allocator-cache-boundary-plan.md`.

One new factor only: after the already-proven 000I targeted stale-response detach, explicitly clear MLX allocator cache at the completed-request boundary using the documented installed API.

Compare detach-only control vs detach + allocator-cache clear on exact R1->R2. Measure:
- active/cache/system-free change;
- cache-clear boundary latency;
- R2 peak/completion;
- response/tool equivalence.

No `gc.collect()`, restart/model reload, host manipulation, or model/context/KV/prompt/tool/prefill changes.

If 000K passes, validate the mechanism across R1-R6 before integrated Pi reproducibility. If it fails, choose the next memory factor from the measured residual rather than changing model size by default.

### CAPABILITY 001 — BLOCKED

Frozen 12-task coding + Git safety + experimental-reasoning baseline. Run only after reproducible multi-turn headroom exists.

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

1. CAPABILITY 000K allocator-cache boundary test
2. full-sequence validation if 000K passes
3. real Pi-loop reproducibility
4. CAPABILITY 001
5. MEMORY-FRONTIER 001
6. prefetch/buffering/range-I/O
7. OUTCORE-BLOCK 001
8. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence currently exist only in the local worktree and `results-local/` unless explicitly synchronized.
