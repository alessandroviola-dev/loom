# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000I_TARGETED_RECLAMATION_PASS`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## Canonical 8B baseline

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2.

REALGEN 001: 13.184615357 tok/s real generation, 12.046861457 tok/s E2E, raw weights 3,583,928,320 B.

REALGEN 002 custom M1 qmv transfer: exact but -9.178832%; closed.

Pure full-model layer streaming saves RAM and destroys throughput; it is not the endpoint.

## A — Capability baseline — ACTIVE

### CAPABILITY 000C — prefill frontier

Step 512 dominates canonical 2048 on the exact Pi prefill:
- 512: 23.74 s, 63.36 tok/s, 4089.8 MB peak, bit-exact
- 2048: 27.91 s, 53.88 tok/s, 4180.1 MB peak, bit-exact
- 256: 28.24 s, 3980.7 MB peak, top1 same but not bit-exact

512 remains the active integrated-agent candidate.

### 000D–000G — bridge + host lifecycle

A genuine Pi tool turn works. Later failures are not caused by intrinsic ~1500-1800-token request size. Host/process teardown is healthy and macOS naturally recovers launch headroom within ~3-5 s.

### CAPABILITY 000H — sequential accumulation

All captured R1-R6 requests pass fresh. Sequential R2 fails only because R1 leaves +468.30 MB MLX active boundary state. This rules out later prompt size, KV-capacity jumps and host admission variability as the primary cause.

### CAPABILITY 000I — TARGETED RECLAMATION PASS

Report: `research/capability/capability-000i-targeted-reclamation-result.md`.

Precise cause:
`ResponseGenerator._generate` retains the finished local `gen_responses`; its completed `GenerationBatch.Response.prompt_cache` keeps 36 request KVCache objects alive after HTTP completion.

Targeted post-response detach of only this stale `prompt_cache`:
- recovers **252.00 MiB active MLX** (53.81% of the observed +468.30 MiB residual);
- lowers R2 peak by **98.50 MiB** (4194.45 -> 4095.95 MiB);
- preserves R1 response/tool behavior and R2 first tool call;
- uses no `mx.clear_cache()`, `gc.collect()` or global cleanup.

Caveat: allocator cache rises when active memory is released, and the two-turn system-free percentage did not improve. Full-sequence validation is required before integrated promotion.

### CAPABILITY 000J — NEXT

Frozen plan: `research/capability/capability-000j-full-sequence-reclamation-plan.md`.

Use exact captured R1-R6 bodies and compare:

1. CONTROL sequential R1->R6 with natural server behavior.
2. TREATMENT sequential R1->R6 with only the 000I stale-response `prompt_cache` detach after each completed response.

Measure per-turn active/cache boundaries, peak MLX, system free/swap and semantic/tool-call equivalence.

No global cleanup or model/context/KV/prompt/tool/prefill-step changes.

Full PASS requires all six treatment requests to complete safely. Partial GO is allowed if the exact treatment materially extends the safe sequence but later still hits the resource floor.

### CAPABILITY 001 — BLOCKED

Frozen 12-task suite: coding + Git safety + experiment/result reasoning. Run only after the integrated bridge has reproducible multi-turn headroom.

## B — RAM/speed frontier

After CAPABILITY 001, run MEMORY-FRONTIER 001 with controlled partial residency and measure resident bytes, MLX peak, system free/swap, SSD bytes/token, real tok/s, TTFT and correctness.

## C — Hide SSD cost

Then isolate:
1. asynchronous prefetch
2. double/triple buffering
3. transfer/super-layer chunk sizing
4. direct safetensors range I/O / mmap / pread
5. macOS page-cache behavior
6. resident-hotset selection

## D — Amortize I/O across tokens

OUTCORE-BLOCK 001 revisits M>1 specifically for out-of-core models, where one weight load may serve several token positions.

## E — Representation without shrinking parameter count

Potential later factors: mixed/selective precision, compressed cold weights, quantized KV and out-of-core storage formats. Judge every representation by memory + speed + capability.

## F — Scale beyond 8B

1. solve architecture on well-characterized 8B
2. apply it to a model whose weights exceed comfortable physical RAM
3. first major checkpoint: 27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
4. optimize toward interactive speed

## Immediate order

1. CAPABILITY 000J — full-sequence targeted reclamation
2. integrated Pi-loop admission/reproducibility if 000J justifies promotion
3. CAPABILITY 001
4. MEMORY-FRONTIER 001
5. prefetch/buffering/range-I/O work
6. OUTCORE-BLOCK 001
7. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence currently exist only in the local worktree and `results-local/`. HANDOFF.md lists known paths. Do not assume they have been committed until explicitly synchronized.

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
