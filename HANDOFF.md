# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge / sustained multi-turn memory frontier
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000G_NATURAL_HOST_RECOVERY_PASS`
Next: `CAPABILITY_000H_MULTI_TURN_REQUEST_ENVELOPE`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

**Big models. Small machines.**

LOOM aims to run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Success requires memory fit, useful speed and retained capability.

## Operating split

Pi: local code, runtime inspection, tests, concise raw evidence.

ChatGPT: research direction, experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and checkpoint continuity.

## Canonical model/runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- Apple M1 / 8 GB
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- built-in M1 `qmv_fast`
- raw persistent weights `3,583,928,320 B`

REALGEN 001:
- real generation **13.184615357 tok/s**
- end-to-end output **12.046861457 tok/s**
- exact greedy-reference agreement on all six frozen prompts
- MLX peak `3,826,575,836 B`

REALGEN 002 M1_S1_R8 transfer: exact but **-9.178832%** throughput; closed.

## Capability bridge findings

### CAPABILITY 000 / 000A

Canonical Qwen3-8B successfully emitted a genuine Pi `read(numbers.txt)` tool call. Exactly one model instance; no duplication. Pi RSS ~45.55 MB.

### CAPABILITY 000B

Exact first Pi request: 1504 tokens. Large prefill qmm/transient allocation plus BF16 KV are the supported dynamic pressure sources; Pi RSS and full-sequence logits are not.

### CAPABILITY 000C — COMPLETE

Exact 1504-token prefill frontier:
- step 512: 23.74 s, 63.36 tok/s, peak 4089.8 MB, bit-exact
- step 2048: 27.91 s, 53.88 tok/s, peak 4180.1 MB, bit-exact
- step 256: 28.24 s, peak 3980.7 MB, top1 same but logits not bit-exact

Step 512 dominates 2048 on this workload and remains the active integrated-agent candidate.

### CAPABILITY 000D Fix2 — VALID RESOURCE ABORT

First real Pi turn completed (`read numbers.txt`). Second request at 1576 tokens crossed the <5% system-free gate.

### CAPABILITY 000E — COMPLETE / NO REPRODUCTION

Exact R2 at 1576 tokens succeeds fresh. Exact R1->R2 also succeeds sequentially without cleanup.

- fresh R2 peak MLX 4095.65 MB
- sequential R2 peak 4194.45 MB
- post-R1 residual active +468.30 MB
- allocator cache 229.07 MB
- request KV objects not retained
- no evidence of a leak

Therefore 1576 tokens are not intrinsically outside the step-512 envelope.

### CAPABILITY 000F — REPRODUCIBILITY STUDY INCOMPLETE

Only attempt 1 was scientifically admitted. It resource-aborted at 4% free after two Pi/model turns (`read -> bash`). Attempt 2 sampled the host too soon after teardown and was not admitted; attempt 3 did not run. Do not interpret 000F as 0/3 model reliability.

### CAPABILITY 000G — NATURAL HOST RECOVERY PASS

Report: `research/capability/capability-000g-natural-host-recovery-result.md`.

Initial host: 70% free, swap 1594.44 MB.

Bounded integrated workload:
- 5 model requests
- peak MLX 4212.45 MB
- minimum free 4%
- peak swap 2020 MB
- resource abort

Normal teardown:
- Pi, bridge and server all exited
- no captured scientific child survived
- both localhost listeners disappeared immediately

Passive recovery:
- t=0 s: 6% free
- t=1 s: 5% free
- t=3 s: 70% free
- t=5 s: 71% free
- >=60% for two consecutive scheduled samples by 5 s

Interpretation: the low 000F post-run launch sample was transient natural macOS recovery, not surviving scientific processes or a memory leak.

The more important remaining issue is sustained multi-turn memory pressure: even from 70% pre-load free, the 000G integrated workload reached five model requests and eventually crossed the 5% gate.

## Exact next step

Run **CAPABILITY 000H — multi-turn request envelope attribution**.

Use the exact captured request bodies from CAPABILITY 000G (R1 through the final request/abort request). Do not reconstruct prompts manually when captured bodies exist.

Required science:
1. recover canonical token counts and message/tool growth per captured request;
2. replay each captured request individually as the first request in a fresh model process to measure its intrinsic memory envelope;
3. separately replay the same request series sequentially in one fresh process with no cleanup treatment;
4. compare fresh-vs-sequential peak MLX, min free, active/cache state, KV length/capacity and prefill M segments per turn;
5. identify the first turn that fails fresh, if any, and the first turn whose sequential overhead becomes material;
6. do not yet change step 512, model, BF16 KV, context, prompts or tools.

This extends 000E from R1/R2 to the full integrated multi-turn trajectory and determines the first justified treatment.

## Local-only files known from Pi

Recent implementation/evidence remain local unless explicitly synchronized, including:
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
- raw `results-local/capability/...` evidence

Do not assume these exist on GitHub until explicitly synchronized.

## Later

1. CAPABILITY 000H full multi-turn envelope attribution
2. choose one justified memory treatment
3. integrated Pi-loop admission/reproducibility
4. CAPABILITY 001 frozen 12-task baseline
5. MEMORY-FRONTIER 001 real M1 partial-residency RAM/tok/s curve
6. async prefetch / buffering / direct range I/O
7. M>1 out-of-core weight-I/O amortization
8. scale toward 27B/32B
