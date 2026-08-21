# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000G_NATURAL_HOST_RECOVERY_PASS`
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

Pure full-model layer streaming is known to save RAM and destroy throughput. It is not the endpoint.

## A — Capability baseline — ACTIVE

### CAPABILITY 000C — prefill frontier

Step 512 dominates canonical 2048 on the exact Pi prefill:
- 512: 23.74 s, 63.36 tok/s, 4089.8 MB peak, bit-exact
- 2048: 27.91 s, 53.88 tok/s, 4180.1 MB peak, bit-exact
- 256: 28.24 s, 3980.7 MB peak, top1 same but not bit-exact

512 remains the active integrated-agent candidate.

### CAPABILITY 000D / 000E

A real Pi tool turn succeeds. A later resource abort occurred, but exact fresh and sequential replay established that 1576 tokens are not intrinsically outside the 512 envelope. Request KV is not retained and no leak is demonstrated.

### CAPABILITY 000F — incomplete reproducibility

Only one attempt was scientifically admitted; it resource-aborted. The next launch sample was taken too early after teardown, so the intended 3-run reliability result was not obtained.

### CAPABILITY 000G — COMPLETE

Report: `research/capability/capability-000g-natural-host-recovery-result.md`.

Natural host recovery after normal scientific-process teardown:
- all scientific PIDs/listeners dead immediately
- free memory 6% at exit, 5% at 1 s
- free memory 70% at 3 s
- 71% at 5 s
- two consecutive >=60% samples by 5 s

Therefore the post-run low-free state is transient macOS recovery, not a process-lifecycle leak.

Important additional evidence: from a 70% pre-load host, the integrated workload executed five model requests but still reached peak MLX 4212.45 MB and 4% free. Sustained multi-turn memory pressure remains unresolved.

### CAPABILITY 000H — NEXT

Full multi-turn request-envelope attribution.

Use exact captured request bodies from the 000G workload.

For each captured turn:
1. recover exact token count and conversation/tool growth;
2. replay it fresh as the first request of a fresh model process;
3. replay the whole series sequentially with no cleanup;
4. compare fresh vs sequential peak MLX, min free, active/cache state, KV and prefill M geometry;
5. identify first intrinsically unsafe request, if any;
6. identify sequential overhead and its growth by turn.

No treatment yet: keep Qwen3-8B 3-bit, BF16 KV, context 4096, step 512 and full Pi tool surface frozen.

### CAPABILITY 001 — BLOCKED

Frozen 12-task suite: coding + Git safety + experiment/result reasoning.

Run only after integrated multi-turn execution has enough reproducible memory headroom.

## B — RAM/speed frontier

After CAPABILITY 001, run MEMORY-FRONTIER 001 with controlled partial residency and measure resident bytes, MLX peak, system free/swap, SSD bytes/token, real tok/s, TTFT and correctness.

## C — Hide SSD cost

Then test one factor at a time:
1. asynchronous prefetch
2. double/triple buffering
3. transfer/super-layer chunk sizing
4. direct safetensors range I/O / mmap / pread
5. macOS page-cache behavior
6. resident-hotset selection

## D — Amortize I/O across tokens

OUTCORE-BLOCK 001 revisits M>1 specifically for out-of-core models, where one weight load may serve several token positions.

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
3. first major checkpoint: 27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
4. then optimize speed toward interactivity

## Immediate order

1. CAPABILITY 000H — full multi-turn request envelope
2. select one evidence-backed memory treatment
3. integrated Pi-loop admission/reproducibility
4. CAPABILITY 001
5. MEMORY-FRONTIER 001
6. prefetch/buffering/range-I/O work
7. OUTCORE-BLOCK 001
8. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence currently exist only in the local worktree and `results-local/`. HANDOFF.md lists known paths. Do not assume they have been committed until explicitly synchronized.

## Final objective

LOOM becomes an execution system that treats RAM + SSD + Apple unified memory + scheduling as one managed hierarchy, allowing models larger than physical RAM to remain genuinely useful.
