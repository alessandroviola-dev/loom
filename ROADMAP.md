# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000C_PREFILL_FRONTIER_COMPLETE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately pushing toward ~27B/32B-class models.

Every major direction is judged on three axes:

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

REALGEN 002 M1 custom-qmv transfer: exact but **-9.178832%**; closed.

Pure full-model layer streaming is already known to save RAM and destroy throughput. Do not treat it as the destination.

## A — Capability baseline — ACTIVE

Goal: benchmark the practical intelligence of the current Qwen3-8B through Pi before future representation changes.

### CAPABILITY 000 — bridge

Canonical Qwen3-8B successfully emitted a real Pi tool call, but integrated execution hit the <5% free-memory floor.

### CAPABILITY 000A — COMPLETE

- one model instance
- no duplication
- Pi RSS negligible relative to model
- dynamic failure occurs during first real Pi prefill

### CAPABILITY 000B — COMPLETE

Exact Pi request = **1504 tokens**: system 608 / user 65 / tools 814 / other 17.

At step 2048, prefill segmentation is `[1430,70,3]`; exact direct replay reached 4180.1 MB MLX peak with ~546 MiB transient above post-prefill active.

Full-sequence logits are not the cause. Weights/KV are proven contributors; qmm/prefill transient allocation plus large agent/tool context are the first justified target.

### CAPABILITY 000C — COMPLETE

Report: `research/capability/capability-000c-prefill-frontier-result.md`.

Exact same 1504-token request; sole factor = `prefill_step_size`.

Key points:

| step | wall s | effective tok/s | peak MLX MB | bit exact |
|---:|---:|---:|---:|---|
| 2048 | 27.91 | 53.88 | 4180.1 | yes |
| 512 | **23.74** | **63.36** | 4089.8 | **yes** |
| 256 | 28.24 | 53.26 | **3980.7** | no |

Pareto frontier: **512 and 256**.

`512` is the operational candidate because it simultaneously improves prefill speed and peak MLX memory versus the 2048 control while preserving bit-exact final logits. Relative to 2048: ~14.94% lower prefill wall, ~17.59% higher effective prefill throughput, and 90.3 MB lower peak MLX.

### CAPABILITY 000D — NEXT

Frozen plan: `research/capability/capability-000d-pi-loop-admission-plan.md`.

Run the real multi-turn Pi smoke with `prefill_step_size=512` and everything else unchanged:

- context 4096
- max output 2048
- BF16 KV
- full read/write/edit/bash tool surface
- same system/tool semantics
- same Qwen3-8B 3-bit model

The purpose is to verify that 512 remains safe as context grows through actual tool turns (`read -> write -> bash -> final answer`).

Track input tokens, prefill segments/wall, generation, KV length/capacity, MLX peak, min free/swap and tool result size for every turn.

### CAPABILITY 001 — BLOCKED pending 000D admission

Frozen 12-task suite: coding + Git safety + experiment/result reasoning.

If 000D functionally passes with safe resource trajectory, run CAPABILITY 001 using the same 512 prefill setting.

This becomes the capability reference for future representation changes.

## B — RAM/speed frontier

After CAPABILITY 001, run MEMORY-FRONTIER 001 on real M1 generation.

Measure controlled partial residency rather than all-or-nothing streaming:

- resident bytes
- MLX peak
- system free/swap
- SSD bytes/token
- real tok/s
- TTFT
- correctness

Output is a RAM <-> tok/s Pareto curve.

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

The resident-8B M5 ceiling does not close this direction because SSD traffic changes the economics.

## E — Representation without shrinking parameter count

Potential later factors:

- mixed/selective precision
- compressed cold weights
- quantized KV
- storage formats designed for out-of-core execution

Judge every representation by:
`memory + speed + capability`.

## F — Scale beyond 8B

1. solve architecture on the well-characterized 8B
2. apply it to a model whose weights exceed comfortable physical RAM
3. first major checkpoint: **27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM**
4. then optimize its speed toward interactivity

## Immediate order

1. CAPABILITY 000D — integrated Pi multi-turn smoke at step 512
2. CAPABILITY 001
3. MEMORY-FRONTIER 001
4. prefetch/buffering/range-I/O work
5. OUTCORE-BLOCK 001
6. scale toward 27B/32B

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
