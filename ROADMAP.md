# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000D_INFRASTRUCTURE_FAILURE_NO_SCIENCE`
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

The local MLX bridge works and a genuine Qwen-generated Pi tool call was observed. There is one model instance, no duplication. The real first Pi request is 1504 tokens and the main dynamic pressure comes from large prefill qmm/transient allocation plus BF16 KV, not Pi RSS or full-sequence logits.

### CAPABILITY 000C — COMPLETE

`prefill_step_size=512` dominates the canonical 2048 setting on the exact Pi prefill:

- 512: **23.74 s**, **63.36 tok/s**, **4089.8 MB peak**, bit-exact
- 2048: **27.91 s**, **53.88 tok/s**, **4180.1 MB peak**, bit-exact

This is an integrated-agent candidate, not yet a universal runtime default.

### CAPABILITY 000D — HARNESS FAILURE / NO SCIENCE

The first integrated Pi-loop attempt failed in server instrumentation before prefill/tool execution:

- 1518 input tokens
- 0 generated tokens
- no tool execution
- min free 17%
- peak MLX 3417.901 MB (weights only)

Therefore no scientific result exists for step 512 in the multi-turn Pi loop.

Next: **CAPABILITY 000D Fix1**. Repair instrumentation only, preflight it, then rerun the identical frozen task.

### CAPABILITY 001 — BLOCKED pending successful 000D admission

Frozen 12-task suite: coding + Git safety + experiment/result reasoning.

This becomes the capability reference for future changes.

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

1. CAPABILITY 000D Fix1 — instrumentation repair + identical Pi-loop rerun
2. CAPABILITY 001
3. MEMORY-FRONTIER 001
4. prefetch/buffering/range-I/O work
5. OUTCORE-BLOCK 001
6. scale toward 27B/32B

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
