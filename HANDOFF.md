# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge / host-recovery attribution
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000F_REPRODUCIBILITY_INCOMPLETE_AFTER_ONE_RESOURCE_ABORT`
Next: `CAPABILITY_000G_HOST_RECOVERY_ATTRIBUTION`

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

Canonical Qwen3-8B successfully emitted a genuine Pi `read(numbers.txt)` tool call. Exactly one model instance; no duplication. Pi RSS ~45.55 MB. The first integrated smoke crossed the <5% free-memory floor during real Pi prefill.

### CAPABILITY 000B

Exact first Pi request: **1504 tokens** = system 608 + user 65 + tools 814 + other 17.

- prefill M `[1430,70,3]` at step 2048
- full-sequence logits not materially retained
- BF16 KV logical 1504, capacity 1536
- exact replay min free 6%
- peak MLX 4180.1 MB
- prefill wall 20.61 s
- ~216 MiB persistent KV
- ~546 MiB transient prefill peak

qmm/prefill temporaries and the long agent/tool prompt are supported pressure sources; Pi RSS and full-sequence logits are not.

### CAPABILITY 000C — COMPLETE

Exact 1504-token prefill frontier:

- `512`: 23.74 s, 63.36 tok/s, peak 4089.8 MB, transient 455.6 MB, bit-exact
- `2048`: 27.91 s, 53.88 tok/s, peak 4180.1 MB, transient 545.9 MB, bit-exact
- `256`: 28.24 s, peak 3980.7 MB, top1 same but logits not bit-exact

`512` dominates 2048 on this workload (~17.6% faster prefill and ~90.3 MB lower peak) and remains the admitted multi-turn candidate, not a global runtime default.

### CAPABILITY 000D / Fix1 — infrastructure only

Original 000D and Fix1 were harness/instrumentation failures before valid science. They do not count against the 512 treatment.

### CAPABILITY 000D Fix2 — VALID SCIENTIFIC RESOURCE ABORT

First scientific Pi turn completed:
- input 1521
- M `512,512,425,68,3`
- prefill 23.091 s
- generated 35 tokens at 11.690 tok/s
- KV 1555 / 1792
- peak MLX 4075.12 MB
- min free 6%
- action `read numbers.txt`

Second request:
- input 1576
- peak MLX 4146.45 MB observed
- free memory crossed hard gate at 4%
- abort before second tool action

Classification: `CAPABILITY_000D_FIX2_RESOURCE_ABORT`.

### CAPABILITY 000E — COMPLETE / NO REPRODUCTION

Report: `research/capability/capability-000e-fresh-vs-sequential-result.md`.

Exact captured requests:
- R1 = 1521 tokens
- R2 = 1576 tokens

Fresh R2 completes:
- peak MLX 4095.65 MB
- post active 3922.20 MB
- post cache 4.79 MB
- min free 6%

Fresh-process sequential R1 -> R2 with no cleanup also completes:
- post-R1 active 3886.20 MB = +468.30 MB over loaded idle
- post-R1 allocator cache 229.07 MB
- sequential R2 peak 4194.45 MB
- fresh R2 peak 4095.65 MB
- sequential delta +98.80 MB
- request KV weakrefs dead; no request KV retained
- no evidence justifying the label `memory leak`

Classification: `CAPABILITY_000E_NO_REPRODUCTION`.

Interpretation: request size 1576 is not intrinsically outside the step-512 envelope. Host/system state materially affects the system-free gate.

### CAPABILITY 000F — REPRODUCIBILITY STUDY INCOMPLETE

Report: `research/capability/capability-000f-host-recovery-incomplete-result.md`.

Frozen goal was three independent real-Pi attempts, each admitted only when pre-load free >=60% and swap <=5600 MB.

Admission:
- Attempt 1: free 65%, swap 1174.38 MB -> admitted
- Attempt 2 launch sample: free 6%, swap 1848.25 MB -> not admitted
- Attempt 3: not run

Attempt 1 is valid science:
- functional FAIL / strict FAIL
- 2 model turns
- tool sequence `read -> bash`
- largest input 1576
- max KV 1621 / 1792
- peak MLX 4194.45 MB
- min free 4%
- peak swap 1860.94 MB
- elapsed 53.144 s
- resource abort
- `answer.txt` absent
- `numbers.txt` byte-identical
- telemetry errors 0

Important interpretation:

The user-facing run label `CAPABILITY_000F_HOST_NOT_READY` must **not** be read as 0/3 model reliability. Only one scientific attempt was admitted. Attempt 1 is one valid resource-abort result; attempts 2–3 provide no model reliability evidence.

The immediate new issue is lifecycle/host recovery: before attempt 1 free memory was 65%; after terminating the first scientific attempt, the next pre-load sample was only 6% free. We do not yet know whether the prior server/model process or child remained alive, Metal/MLX resources did not fully teardown, macOS was still naturally reclaiming/compressing memory, unrelated host pressure changed, or sampling was too early.

## Exact next step

Run **CAPABILITY 000G — scientific process teardown / natural host recovery attribution**.

Goals:
1. use one fresh scientific model/server process with the same canonical configuration;
2. run one bounded workload sufficient to load/use the model;
3. terminate the server normally;
4. prove parent/child PIDs and listeners are dead;
5. passively sample free memory, swap, compressor/process tree for a bounded recovery window;
6. no purge, `mx.clear_cache`, scripted kills, artificial allocations or swap manipulation;
7. determine whether the >=60% launch gate naturally returns after process death and how long it takes;
8. distinguish process-lifecycle retention from delayed OS recovery.

Do not change step 512, model, KV, prompt/tool surface or representation yet.

If host naturally recovers after a bounded delay, rerun 000F with an explicit passive recovery wait/gate between attempts. If process/resources remain live, repair teardown before further capability benchmarking.

## Local-only files known from Pi

Recent implementation/evidence remain local unless explicitly synchronized:

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
- raw `results-local/capability/...` evidence

Do not assume these exist on GitHub until synchronized.

## Later

1. CAPABILITY 000G host recovery attribution
2. corrected CAPABILITY 000F reproducibility
3. CAPABILITY 001 frozen 12-task baseline
4. MEMORY-FRONTIER 001 real M1 partial-residency RAM/tok/s curve
5. async prefetch / buffering / direct range I/O
6. M>1 out-of-core weight-I/O amortization
7. scale toward 27B/32B
