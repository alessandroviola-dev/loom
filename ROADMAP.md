# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000H_SEQUENTIAL_ACCUMULATION_LIMIT`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models.

Every major direction is judged on memory, speed and capability. Pi is reserved for code/tests; ChatGPT owns research direction and repository/project synchronization.

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

### 000D–000G — bridge and host lifecycle

A real Pi tool turn succeeds. Later resource aborts are not explained by intrinsic 1576-token request size. Host teardown is healthy: all scientific processes die and macOS naturally recovers >=60% free within ~3-5 s.

### CAPABILITY 000H — COMPLETE

Report: `research/capability/capability-000h-sequential-accumulation-result.md`.

Exact captured requests R1-R6 span 1518 -> 1820 input tokens. **All six pass fresh.**

Sequentially:
- R1 passes;
- after R1, active MLX remains 3886.20 MB versus 3417.90 MB loaded-idle: +468.30 MB request-boundary state;
- allocator cache ~226.57 MB;
- R2 fresh peak 4095.65 MB / min free 9%;
- R2 sequential peak 4182.45 MB / min free 4%;
- sequential R2 aborts.

Classification: `CAPABILITY_000H_SEQUENTIAL_ACCUMULATION_LIMIT`.

Therefore the primary current bottleneck is request-boundary active/cache retention, not later prompt size, KV-capacity jumps or host admission variability.

### CAPABILITY 000I — NEXT

Request-local state reclamation.

Frozen plan: `research/capability/capability-000i-request-local-reclamation-plan.md`.

Phase A: identify the exact completed-request owner/lifecycle retaining MLX active memory after R1 using source inspection, weakrefs/object graph and metadata-only tensor accounting.

Phase B is allowed only if the stale owner/intended missing lifecycle transition is identified. Test one targeted request-local release versus natural control on exact R1->R2.

Forbidden: `mx.clear_cache()`, `gc.collect()`, global cleanup, process restart between R1/R2, model/context/KV/prompt/tool/prefill-step changes.

Promotion requires materially lower post-R1 active memory, sequential R2 completion above the resource gate, and preserved output/tool behavior.

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

Potential later factors: mixed/selective precision, compressed cold weights, quantized KV, and out-of-core storage formats. Judge every representation by memory + speed + capability.

## F — Scale beyond 8B

1. solve architecture on well-characterized 8B
2. apply it to a model whose weights exceed comfortable physical RAM
3. first major checkpoint: 27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
4. optimize toward interactive speed

## Immediate order

1. CAPABILITY 000I — targeted request-local reclamation
2. integrated Pi-loop admission/reproducibility
3. CAPABILITY 001
4. MEMORY-FRONTIER 001
5. prefetch/buffering/range-I/O work
6. OUTCORE-BLOCK 001
7. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence currently exist only in the local worktree and `results-local/`. HANDOFF.md lists known paths. Do not assume they have been committed until explicitly synchronized.

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
