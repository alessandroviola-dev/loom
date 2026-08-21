# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge / request-boundary memory reclamation
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000H_SEQUENTIAL_ACCUMULATION_LIMIT`
Next: `CAPABILITY_000I_REQUEST_LOCAL_RECLAMATION`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory, speed and capability.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.

ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical baseline

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- context 4096 for capability bridge
- built-in M1 `qmv_fast`
- raw weights `3,583,928,320 B`

REALGEN 001 practical baseline: 13.184615357 tok/s real generation, 12.046861457 tok/s E2E. REALGEN 002 custom M1 qmv transfer was exact but -9.178832%; closed.

## Capability findings

### 000 / 000A / 000B

Canonical Qwen3-8B generated a real Pi `read(numbers.txt)` tool call. Exactly one model instance; no duplication. Pi RSS ~45.55 MB. First Pi request is ~1500 tokens. Dynamic pressure is from prefill temporaries + BF16 KV, not full-sequence logits or Pi RSS.

### 000C — prefill frontier

Exact Pi prefill:
- step 512: 23.74 s, 63.36 tok/s, 4089.8 MB peak, bit-exact
- step 2048: 27.91 s, 53.88 tok/s, 4180.1 MB peak, bit-exact
- step 256: 28.24 s, 3980.7 MB peak, top1 same but not bit-exact

Step 512 remains the active integrated-agent candidate.

### 000D Fix2 / 000E

A real Pi turn succeeded, then a later resource abort occurred. Exact fresh and R1->R2 replay showed 1576 tokens are not intrinsically outside the step-512 envelope. Request KV was not shown to leak.

### 000F / 000G — host lifecycle resolved

000F reliability study was incomplete after one admitted resource abort because attempt 2 sampled host memory too early after process exit.

000G proved normal teardown is healthy:
- all scientific PIDs/listeners die immediately;
- free memory 6% at exit, 5% at 1 s, 70% at 3 s, 71% at 5 s;
- no lifecycle leak.

### CAPABILITY 000H — SEQUENTIAL ACCUMULATION LIMIT

Report: `research/capability/capability-000h-sequential-accumulation-result.md`.

Exact integrated capture contained six HTTP model POSTs:
- R1 1518 tokens
- R2 1573
- R3 1634
- R4 1682
- R5 1765
- R6 1820

Every R1-R6 request passes when run fresh as the first request in a fresh model process. Fresh peak MLX stays ~4069.62-4132.34 MB; fresh minimum free 7-10%.

Sequentially:
- R1 completes, peak 4069.62 MB;
- after R1, MLX active = 3886.20 MB versus 3417.90 MB loaded-idle: **+468.30 MB active boundary state**;
- post-R1 allocator cache ~226.57 MB;
- R2 fresh peak 4095.65 MB, min free 9%;
- R2 sequential observed peak 4182.45 MB, **+86.80 MB** over fresh, min free 4%;
- R2 aborts at the hard system-free gate;
- R3-R6 are not reached sequentially but all pass fresh.

Classification: `CAPABILITY_000H_SEQUENTIAL_ACCUMULATION_LIMIT`.

Supported attribution:
- retained sequential MLX active/cache state: PROVEN;
- intrinsic later request size/history: NOT SUPPORTED as primary cause;
- KV-capacity jumps: NOT SUPPORTED as primary cause;
- host variability: NOT SUPPORTED.

Do not call this a memory leak yet. The proven fact is request-boundary live/allocator state sufficient to make the next request unsafe.

## Exact next step

Run **CAPABILITY 000I — request-local state reclamation** from:
`research/capability/capability-000i-request-local-reclamation-plan.md`.

Phase A must identify the exact server object/tensor lifecycle owning the retained request-boundary active memory after R1. Trace API handler, streaming response/generator, BatchGenerator, PromptProcessingBatch, pending/finished request state, request KV and output arrays.

Only if a precise stale owner/intended lifecycle transition is identified may Phase B test one targeted request-local release after R1 response completion.

Forbidden as treatment: `mx.clear_cache()`, `gc.collect()`, model reload, process restart between R1/R2, prefill step change, KV/context/prompt/tool/model changes, or global cleanup.

Control and treatment use exact captured R1/R2 bodies. Primary success is recovery of boundary active memory plus sequential R2 completion while preserving output/tool behavior.

## Local-only implementation warning

Recent scripts/evidence remain local unless explicitly synchronized, including:
- `scripts/loom_pi_mlx_bridge.py`
- `scripts/capability_000a_memory_attribution.py`
- `scripts/capability_000b_pi_prefill_attribution.py`
- `scripts/capability_000c_prefill_frontier.py`
- `scripts/capability_000d_pi_loop.py`
- `scripts/capability_000d_fix1_pi_loop.py`
- `scripts/capability_000d_fix2_pi_loop.py`
- `scripts/capability_000e_turn_memory_attribution.py`
- `scripts/capability_000f_integrated_pi_reproducibility.py`
- `scripts/capability_000f_server.py`
- `scripts/capability_000g_host_recovery.py`
- `scripts/capability_000h_request_envelope_attribution.py`
- raw `results-local/capability/...` evidence

Do not assume these exist on GitHub until explicitly synchronized.

## Later

1. CAPABILITY 000I targeted request-local reclamation
2. integrated Pi-loop admission/reproducibility
3. CAPABILITY 001 frozen 12-task capability baseline
4. MEMORY-FRONTIER 001 real M1 RAM/tok/s partial-residency curve
5. async prefetch/buffering/direct range I/O
6. OUTCORE-BLOCK 001
7. scale toward 27B/32B
