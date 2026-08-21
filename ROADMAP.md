# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000E_NO_REPRODUCTION`
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

512 remains the admitted integrated-agent candidate, not a universal runtime default.

### CAPABILITY 000D Fix2 — VALID SCIENTIFIC RESOURCE ABORT

First real Pi turn completed and issued `read numbers.txt`; second request at 1576 tokens crossed the <5% free-memory gate. This was real science but did not prove an intrinsic request-size limit.

### CAPABILITY 000E — COMPLETE / NO REPRODUCTION

Report: `research/capability/capability-000e-fresh-vs-sequential-result.md`.

Exact R2 (1576 tokens) succeeds as a fresh first request.

Exact R1 (1521) then R2 (1576) also both succeed sequentially without cleanup in a fresh direct-replay process.

Evidence:
- fresh R2 peak MLX **4095.65 MB**
- sequential R2 peak **4194.45 MB**
- sequential delta **+98.80 MB**
- post-R1 residual active **+468.30 MB** over loaded idle
- post-R1 allocator cache **229.07 MB**
- request KV objects are not retained
- no evidence supports calling this a leak

Therefore the Fix2 abort is not reproduced as an intrinsic 1576-token/step-512 limit. Host/system state materially influences the system-free gate.

### CAPABILITY 000F — NEXT

Integrated Pi-loop reproducibility under controlled passive host launch state.

Keep frozen:
- Qwen3-8B 3-bit
- BF16 KV
- context 4096
- step 512
- full Pi tools
- same numbers.txt task

Protocol:
1. use real Pi, not direct replay;
2. fresh scientific model/server process for every attempt;
3. no preflight inference in the same process;
4. host launch gate before model load: free >=60%, swap <=5600 MB;
5. no purge, scripted process kills or artificial memory manipulation;
6. three independent fresh-process attempts;
7. each task attempt is one Pi session with no prompt rescue/retry;
8. report success rate and full resource trajectory.

If host launch gate is not met, classify host-not-ready and consume no scientific attempt. Normal manual closure of unrelated user apps is allowed as passive host preparation before a later launch sample.

If the integrated loop is reproducibly successful, admit step 512 bridge and run CAPABILITY 001. If repeated admitted runs still resource-abort, select a new isolated memory treatment from evidence.

### CAPABILITY 001 — BLOCKED pending 000F admission

Frozen 12-task suite: coding + Git safety + experiment/result reasoning.

This becomes the capability reference for future representation changes.

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

1. CAPABILITY 000F — integrated Pi reproducibility
2. CAPABILITY 001
3. MEMORY-FRONTIER 001
4. prefetch/buffering/range-I/O work
5. OUTCORE-BLOCK 001
6. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence currently exist only in the local worktree and `results-local/`. HANDOFF.md lists known paths. Do not assume they have been committed until explicitly synchronized.

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
