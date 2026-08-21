# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge / targeted request-boundary reclamation
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000I_TARGETED_RECLAMATION_PASS`
Next: `CAPABILITY_000J_FULL_SEQUENCE_RECLAMATION`

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
- capability context 4096
- built-in M1 `qmv_fast`
- raw weights `3,583,928,320 B`

REALGEN 001 practical baseline: 13.184615357 tok/s real generation, 12.046861457 tok/s E2E. REALGEN 002 custom M1 qmv transfer was exact but -9.178832%; closed.

## Capability findings

### 000C — prefill frontier

Exact Pi prefill:
- step 512: 23.74 s, 63.36 tok/s, 4089.8 MB peak, bit-exact
- step 2048: 27.91 s, 53.88 tok/s, 4180.1 MB peak, bit-exact
- step 256: 28.24 s, 3980.7 MB peak, top1 same but not bit-exact

Step 512 remains the active integrated-agent candidate.

### 000D–000G — bridge/host lifecycle

A real Pi tool turn succeeds. Later request failures are not explained by intrinsic ~1500-1800 token request size. Host teardown is healthy: all scientific processes die and macOS naturally returns >=60% free within ~3-5 s.

### CAPABILITY 000H — SEQUENTIAL ACCUMULATION LIMIT

Report: `research/capability/capability-000h-sequential-accumulation-result.md`.

Captured R1-R6 span 1518 -> 1820 input tokens. All six pass fresh.

Sequentially:
- R1 passes;
- loaded-idle active 3417.90 MB;
- post-R1 active 3886.20 MB = **+468.30 MB** request-boundary state;
- post-R1 allocator cache ~226-234 MB;
- R2 fresh peak 4095.65 MB / min free 9%;
- R2 sequential peak 4182.45 MB / min free 4%;
- R2 aborts.

Therefore the current bottleneck is request-boundary MLX state, not later request size, KV-capacity jumps or host admission variability.

### CAPABILITY 000I — TARGETED RECLAMATION PASS

Report: `research/capability/capability-000i-targeted-reclamation-result.md`.

Precise retained owner recovered:

`mlx_lm.server.ResponseGenerator._generate` leaves the finished local `gen_responses` reachable while the thread returns to its idle loop. The completed `GenerationBatch.Response` retains `prompt_cache`, which retains the finished request's 36 KVCache objects.

Observed after R1 HTTP completion:
- retained `GenerationBatch.Response`: ~218.39 MiB KV + ~0.29 MiB logits metadata;
- 36 retained `KVCache`: ~218.39 MiB;
- metadata-accounted request-local state ~218.68 MiB;
- observed post-R1 active delta over loaded idle: +468.30 MiB.

Single targeted treatment: after the response is fully complete, detach only the stale completed `GenerationBatch.Response.prompt_cache`.

No `mx.clear_cache()`, `gc.collect()`, allocator/global reset, model reload or model/context/KV/prompt/tool/prefill changes.

Control:
- post-R1 active/cache 3886.20 / 234.07 MiB;
- active residual +468.30 MiB;
- R2 peak 4194.45 MiB;
- R2 min free 5%; PASS.

Treatment:
- before detach 3886.20 / 234.07 MiB;
- after detach 3634.20 / 486.07 MiB;
- **252.00 MiB active recovered** = 53.81% of observed residual;
- R2 peak 4095.95 MiB = **98.50 MiB reduction**;
- R2 min free 5%; PASS.

R1 response/tool call is identical control vs treatment; R2 first tool call is also identical. Global cleanup used: NO.

Important nuance: recovered active memory moved largely into allocator cache, so system free headroom did not improve in this two-turn run. The treatment is therefore scientifically valid but not yet promoted to the integrated bridge until full-sequence behavior is measured.

## Exact next step

Run **CAPABILITY 000J — full-sequence targeted reclamation validation** from:
`research/capability/capability-000j-full-sequence-reclamation-plan.md`.

Use exact captured R1-R6 bodies.

Compare two fresh processes:
1. CONTROL R1->R6 with natural server behavior;
2. TREATMENT R1->R6, applying only the 000I stale-response `prompt_cache` detach after every completed response.

Measure per-turn active/cache boundaries, peak MLX, system free/swap and response/tool equivalence. No global cleanup or other model/runtime changes.

Only after 000J should the treatment be considered for a real Pi-loop reproducibility run.

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
- `scripts/capability_000i_request_local_reclamation.py`
- `scripts/capability_000i_targeted_reclamation_phase_b.py`
- raw `results-local/capability/...` evidence

Do not assume these exist on GitHub until explicitly synchronized.

## Later

1. CAPABILITY 000J full-sequence targeted reclamation
2. integrated Pi-loop admission/reproducibility with promoted treatment if justified
3. CAPABILITY 001 frozen 12-task capability baseline
4. MEMORY-FRONTIER 001 real M1 RAM/tok/s partial-residency curve
5. async prefetch/buffering/direct range I/O
6. OUTCORE-BLOCK 001
7. scale toward 27B/32B
