# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000D_FIX2_RESOURCE_ABORT`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models.

Every major direction is judged on:
1. memory
2. speed
3. capability

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## Canonical 8B baseline

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2.

REALGEN 001:
- real generation **13.184615357 tok/s**
- end-to-end **12.046861457 tok/s**
- raw weights **3,583,928,320 B**
- MLX peak **3,826,575,836 B**

REALGEN 002 custom M1 qmv transfer: exact but **-9.178832%**; closed.

Pure full-model layer streaming is already known to save RAM and destroy throughput. It is not the endpoint.

## A — Capability baseline — ACTIVE

Goal: benchmark the practical intelligence of the current Qwen3-8B through Pi before future representation changes.

### CAPABILITY 000–000B

The local MLX bridge works and a genuine Qwen-generated Pi tool call was observed. There is one model instance, no duplication. The first real Pi request is ~1500 tokens; dynamic pressure is dominated by prefill temporaries plus BF16 KV, not Pi RSS or full-sequence logits.

### CAPABILITY 000C — COMPLETE

On the exact 1504-token Pi prefill:

- step 512: **23.74 s**, **63.36 tok/s**, **4089.8 MB peak**, bit-exact
- step 2048: **27.91 s**, **53.88 tok/s**, **4180.1 MB peak**, bit-exact
- step 256: **28.24 s**, **3980.7 MB peak**, top1 same but not bit-exact

512 is the admitted integrated-agent candidate, not a universal default.

### CAPABILITY 000D / Fix1 — infrastructure only

Two harness/instrumentation failures occurred before a valid scientific loop. They are preserved as no-science infrastructure results.

### CAPABILITY 000D Fix2 — SCIENTIFIC RESOURCE ABORT

Report: `research/capability/capability-000d-fix2-resource-abort-result.md`.

The repaired harness passed preflight and produced the first valid multi-turn evidence.

Turn 1:
- 1521 input tokens
- step 512 segments `512,512,425,68,3`
- prefill 23.091 s
- 35 generated tokens at 11.690 tok/s
- KV 1555 / 1792
- peak MLX 4075.12 MB
- minimum free 6%
- action: `read numbers.txt`

Turn 2:
- 1576 input tokens
- first 512 segment began
- peak MLX 4146.45 MB
- free memory fell to 4%
- hard resource abort

Therefore 512 enables one genuine Pi tool turn but does not yet sustain the next turn.

### CAPABILITY 000E — NEXT

Fresh-vs-sequential turn attribution.

Use the exact request bodies captured by Fix2 and distinguish:

A. **Intrinsic request-size limit**: request 2 (~1576 tokens) fails even as the first request after fresh model load.

B. **Inter-request accumulation**: request 2 survives fresh but fails after request 1 because allocator cache, references, request lifecycle or other state persists.

Frozen comparison:

1. fresh model/server -> request 2 alone;
2. fresh model/server -> request 1 then request 2 sequentially;
3. no cleanup treatment in either scientific path;
4. record MLX active/cache/peak, RSS, system free/swap and object/KV lifetime around request boundaries.

Do not yet change chunk size, model, BF16 KV, context, prompt, tool schema or introduce cleanup as a treatment.

### CAPABILITY 001 — BLOCKED

Frozen 12-task suite: coding + Git safety + experiment/result reasoning.

Run only after the multi-turn bridge has safe memory headroom.

## B — RAM/speed frontier

After CAPABILITY 001, run MEMORY-FRONTIER 001 on real M1 generation with controlled partial residency.

Measure together:
- resident bytes
- MLX peak
- system free/swap
- SSD bytes/token
- real tok/s
- TTFT
- correctness

Output: RAM <-> tok/s Pareto curve.

## C — Hide SSD cost

Then test one factor at a time:
1. asynchronous prefetch
2. double/triple buffering
3. transfer/super-layer chunk sizing
4. direct safetensors range I/O / mmap / pread
5. macOS page-cache behavior
6. resident-hotset selection

## D — Amortize I/O across tokens

OUTCORE-BLOCK 001 will revisit M>1 execution specifically for out-of-core models, where one weight load may serve several token positions.

## E — Representation without shrinking parameter count

Potential later factors:
- mixed/selective precision
- compressed cold weights
- quantized KV
- storage formats designed for out-of-core execution

Judge every representation by `memory + speed + capability`.

## F — Scale beyond 8B

1. solve architecture on the well-characterized 8B
2. apply it to a model whose weights exceed comfortable physical RAM
3. first major checkpoint: **27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM**
4. then optimize speed toward interactivity

## Immediate order

1. CAPABILITY 000E — fresh vs sequential request attribution
2. choose one justified memory treatment from that result
3. integrated Pi-loop admission
4. CAPABILITY 001
5. MEMORY-FRONTIER 001
6. prefetch/buffering/range-I/O work
7. OUTCORE-BLOCK 001
8. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence currently exist only in the local worktree and `results-local/`. HANDOFF.md lists known paths. Do not assume they have been committed until explicitly synchronized.

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
