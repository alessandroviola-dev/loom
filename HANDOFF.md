# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge / integrated reproducibility
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000E_NO_REPRODUCTION`
Next: `CAPABILITY_000F_INTEGRATED_PI_REPRODUCIBILITY`

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

- input 1521 tokens
- M `512,512,425,68,3`
- prefill 23.091 s
- generated 35 tokens at 11.690 tok/s
- KV 1555 / 1792
- peak MLX 4075.12 MB
- min free 6%
- peak swap 2284.25 MB
- genuine action: `read numbers.txt`

Second request:

- input 1576 tokens
- first 512 prefill segment began
- peak MLX 4146.45 MB
- free memory crossed hard gate at 4%
- resource abort before second tool action

Classification: `CAPABILITY_000D_FIX2_RESOURCE_ABORT`.

This proved step 512 can execute a real Pi tool turn but left ambiguity about whether request 2 itself or prior-turn state caused the abort.

### CAPABILITY 000E — COMPLETE / NO REPRODUCTION

Report: `research/capability/capability-000e-fresh-vs-sequential-result.md`.

Exact captured requests:
- R1 = **1521 tokens**
- R2 = **1576 tokens**

Fresh R2:
- completes
- M `512,512,512,39`
- peak MLX **4095.65 MB**
- post active **3922.20 MB**
- post cache **4.79 MB**
- min free **6%**
- peak swap **2108.94 MB**

Sequential fresh-process R1 -> R2 with NO cleanup:
- both complete
- loaded-idle active **3417.90 MB**
- post-R1 active **3886.20 MB** = **+468.30 MB** residual
- post-R1 allocator cache **229.07 MB**
- sequential R2 peak **4194.45 MB**
- fresh R2 peak **4095.65 MB**
- sequential R2 peak delta **+98.80 MB**
- final observed free at B8 **12%**

Lifetime audit:
- request object not retained
- 180 BatchKVCache weakrefs dead; request KV not retained
- one PromptProcessingBatch remained live through BatchGenerator, without retained KV
- telemetry scalar-only
- no evidence justifying the label `memory leak`

Classification: `CAPABILITY_000E_NO_REPRODUCTION`.

Interpretation: R2 is **not intrinsically too large**, and R1->R2 also succeeds under controlled direct replay. Inter-request active/cache state exists, but it did not reproduce the Fix2 abort. Host/system memory state therefore materially affects the <5% system-free gate.

## Exact next step

Run **CAPABILITY 000F — integrated Pi-loop reproducibility** before changing chunk size, KV, prompt or model.

Purpose:

1. use the real Pi process, not direct replay;
2. keep `prefill_step_size=512` and all model/tool/context settings unchanged;
3. use a fresh scientific server process with no preflight inference in that same process;
4. apply the established passive host launch gate before model load: free memory >=60%, swap <=5600 MB; no scripted process kills, purge or memory manipulation;
5. run three independent fresh-process attempts of the same frozen numbers.txt task;
6. measure task success and resource trajectory, not just one favorable run.

If the launch gate is not met, classify host-not-ready and do not consume a scientific attempt. The user may normally close unrelated applications before a later launch sample.

If repeated integrated runs pass, admit the 512 bridge for CAPABILITY 001. If they repeatedly resource-abort despite admitted host state, then choose the next memory treatment from evidence (likely chunk 256 or another isolated factor).

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
- raw `results-local/capability/...` evidence

Do not assume these exist on GitHub until synchronized.

## Later

1. CAPABILITY 000F integrated reproducibility
2. CAPABILITY 001 frozen 12-task baseline
3. MEMORY-FRONTIER 001 real M1 partial-residency RAM/tok/s curve
4. async prefetch / buffering / direct range I/O
5. M>1 out-of-core weight-I/O amortization
6. scale toward 27B/32B
