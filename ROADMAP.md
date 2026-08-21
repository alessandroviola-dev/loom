# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000F_REPRODUCIBILITY_INCOMPLETE_AFTER_ONE_RESOURCE_ABORT`
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

### CAPABILITY 000–000C

The local MLX bridge works and a genuine Qwen-generated Pi tool call was observed. There is one model instance, no duplication. Dynamic pressure is dominated by prefill temporaries plus BF16 KV, not Pi RSS or full-sequence logits.

`prefill_step_size=512` dominates canonical 2048 on the exact 1504-token Pi prefill:
- 512: **23.74 s**, **63.36 tok/s**, **4089.8 MB peak**, bit-exact
- 2048: **27.91 s**, **53.88 tok/s**, **4180.1 MB peak**, bit-exact
- 256: **28.24 s**, **3980.7 MB peak**, top1 same but not bit-exact

512 remains the admitted integrated-agent candidate, not a universal runtime default.

### CAPABILITY 000D Fix2 — VALID RESOURCE ABORT

First real Pi turn completed. Second request at 1576 tokens crossed the <5% free-memory gate.

### CAPABILITY 000E — COMPLETE / NO REPRODUCTION

Fresh R2 at 1576 tokens completes. Fresh-process sequential R1->R2 also completes without cleanup.

Evidence:
- fresh R2 peak MLX 4095.65 MB
- sequential R2 peak 4194.45 MB
- sequential delta +98.80 MB
- post-R1 residual active +468.30 MB
- allocator cache 229.07 MB
- request KV not retained
- no evidence of a leak

Therefore R2 is not intrinsically outside the step-512 envelope. Host/system state materially affects the resource gate.

### CAPABILITY 000F — REPRODUCIBILITY STUDY INCOMPLETE

Report: `research/capability/capability-000f-host-recovery-incomplete-result.md`.

Frozen target was three independently admitted real-Pi attempts.

Observed:
- attempt 1 pre-load: free 65%, swap 1174.38 MB -> admitted
- attempt 1: 2 turns, `read -> bash`, peak MLX 4194.45 MB, min free 4%, resource abort
- attempt 2 launch sample: free 6%, swap 1848.25 MB -> not admitted
- attempt 3 not run

Do **not** interpret this as 0/3 model reliability. Only one scientific attempt was admitted.

The new unresolved problem is why the host did not recover from 65% pre-load free to another >=60% launch-ready state after the fresh scientific server/model process was terminated.

### CAPABILITY 000G — NEXT

Scientific-process teardown and natural host-recovery attribution.

Frozen principle:
- do not change model, step 512, BF16 KV, context or tools;
- use one fresh model/server process;
- execute one bounded workload;
- terminate normally;
- prove server/child PIDs and listening socket are gone;
- passively sample host free memory, swap, compressor and process state after exit;
- no purge, forced kills, `mx.clear_cache`, artificial allocations or swap manipulation.

Primary question:

Does the host naturally recover to the >=60% launch gate after process death within a bounded interval?

If yes, rerun CAPABILITY 000F with a passive recovery wait/gate between attempts.

If no and processes/resources remain alive, repair lifecycle first.

If all processes are dead but host memory remains depressed for a long interval, characterize OS recovery before changing model/runtime factors.

### CAPABILITY 001 — BLOCKED

Frozen 12-task suite: coding + Git safety + experiment/result reasoning.

Run only after integrated Pi execution can be repeated under a reproducible host lifecycle.

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

1. CAPABILITY 000G — process teardown / natural host recovery
2. corrected CAPABILITY 000F — three admitted independent attempts
3. CAPABILITY 001
4. MEMORY-FRONTIER 001
5. prefetch/buffering/range-I/O work
6. OUTCORE-BLOCK 001
7. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence currently exist only in the local worktree and `results-local/`. HANDOFF.md lists known paths. Do not assume they have been committed until explicitly synchronized.

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
