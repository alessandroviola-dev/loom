# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge admission
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000D_INFRASTRUCTURE_FAILURE_NO_SCIENCE`
Next: `CAPABILITY_000D_FIX1`

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

Canonical Qwen3-8B successfully emitted a genuine Pi `read(numbers.txt)` tool call. There is exactly one model instance; no duplication. Pi RSS is only ~45.55 MB. The original integrated smoke crossed the <5% free-memory floor during real Pi prefill.

### CAPABILITY 000B

Exact first Pi request: **1504 tokens** = system 608 + user 65 + tools 814 + other 17.

- prefill M `[1430,70,3]` with step 2048
- full-sequence logits not materially retained
- BF16 KV logical 1504, capacity 1536
- exact replay min free 6%
- peak MLX 4180.1 MB
- prefill wall 20.61 s
- ~216 MiB persistent KV
- ~546 MiB transient prefill peak

qmm/prefill temporaries and long agent/tool prompt are supported causes; Pi process and full-sequence logits are not.

### CAPABILITY 000C — COMPLETE

Exact 1504-token prefill frontier:

- `512`: 23.74 s, 63.36 tok/s, peak 4089.8 MB, transient 455.6 MB, bit-exact
- `2048`: 27.91 s, 53.88 tok/s, peak 4180.1 MB, transient 545.9 MB, bit-exact
- `256`: 28.24 s, peak 3980.7 MB, top1 exact but logits not bit-exact

`512` dominates the canonical 2048 step on this workload: ~17.6% higher prefill throughput and ~90.3 MB lower peak, with bit-exact final logits. It is the admitted candidate for integrated Pi-loop testing, not yet a globally promoted runtime default.

### CAPABILITY 000D — HARNESS FAILURE / NO SCIENCE

First integrated Pi-loop attempt with step 512 failed inside server instrumentation before model prefill/tool execution.

- request length 1518 tokens
- generated tokens 0
- tools none
- min free 17%
- peak swap 2288.25 MB
- peak MLX 3417.901 MB (weights only)
- no provider fallback
- Pi automatic retries also failed before model execution

Report: `research/capability/capability-000d-infrastructure-failure.md`.

Interpretation: `prefill_step_size=512` was never exercised. This run consumes no scientific attempt.

## Exact next step

Run **CAPABILITY 000D Fix1**:

1. diagnose the exact server-thread instrumentation exception;
2. fix only instrumentation/harness code;
3. preflight the instrumentation without model science where possible;
4. rerun the identical frozen numbers.txt Pi loop with step 512;
5. no prompt/model/context/KV/tool/runtime changes.

If functional Pi-loop admission passes, proceed to frozen CAPABILITY 001. If resource failure occurs after actual model execution, treat that as scientific evidence.

## Later

1. CAPABILITY 001
2. MEMORY-FRONTIER 001 real M1 partial-residency RAM/tok/s curve
3. async prefetch / buffering / direct range I/O
4. M>1 out-of-core weight-I/O amortization
5. scale toward 27B/32B
