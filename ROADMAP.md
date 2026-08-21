# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000B_EXACT_REPLAY_COMPLETE`
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

Report: `research/capability/capability-000b-pi-prefill-envelope-result.md`.

Exact Pi request = **1504 tokens**:

- system 608
- user 65
- tools 814
- other 17

Current prefill uses M `[1430,70,3]` with `prefill_step_size=2048`.

Exact direct replay:

- minimum free **6%**
- peak MLX **4180.1 MB**
- prefill wall **20.61 s**
- persistent KV capacity ~216 MiB
- transient first-prefill peak ~546 MiB

Full-sequence logits are not the cause. qmm/prefill transient allocation plus the large system/tool prompt are the first justified target.

### CAPABILITY 000C — NEXT

Frozen plan: `research/capability/capability-000c-prefill-chunk-frontier-plan.md`.

Sole factor:

- control 2048
- 1024
- 512
- 256

Everything else frozen, including the exact 1504-token request, tool surface, context 4096, BF16 KV and model.

Primary output:

`chunk size -> peak memory/headroom -> prefill wall penalty -> first-token/tool-call agreement`

If a useful chunk size is found, run one separate integrated Pi smoke. Only then run CAPABILITY 001.

### CAPABILITY 001 — BLOCKED pending sustainable bridge

Frozen 12-task suite: coding + Git safety + experiment/result reasoning.

This becomes the capability reference for future changes.

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

1. CAPABILITY 000C — prefill chunk frontier
2. integrated Pi smoke with selected chunk size
3. CAPABILITY 001
4. MEMORY-FRONTIER 001
5. prefetch/buffering/range-I/O work
6. OUTCORE-BLOCK 001
7. scale toward 27B/32B

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
