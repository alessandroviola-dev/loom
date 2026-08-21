# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge admission / instrumentation repair
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000D_FIX1_PREFLIGHT_FAIL_NO_SCIENCE`
Next: `CAPABILITY_000D_FIX2_MINIMAL_HARNESS_REPAIR`

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

`512` dominates the canonical 2048 step on this workload: ~17.6% higher prefill throughput and ~90.3 MB lower peak, with bit-exact final logits. It remains the admitted candidate for integrated Pi-loop testing, not yet a globally promoted runtime default.

### CAPABILITY 000D — first integrated attempt — HARNESS FAILURE / NO SCIENCE

The first integrated Pi-loop attempt with step 512 failed inside server instrumentation before model prefill/tool execution.

- request length 1518 tokens
- generated tokens 0
- tools none
- min free 17%
- peak swap 2288.25 MB
- peak MLX 3417.901 MB (weights only)
- no provider fallback

Root cause later recovered in Fix1:

`AttributeError: 'list' object has no attribute 'shape'`

at `scripts/capability_000d_pi_loop.py`, function `watched_prompt`, line 114.

Report: `research/capability/capability-000d-infrastructure-failure.md`.

### CAPABILITY 000D Fix1 — PREFLIGHT FAILURE / NO SCIENCE

Fix1 created a list-safe observer using `len(sequence)`, exception-contained observation callbacks and disabled Pi retry settings.

The repaired bridge reached actual model inference in preflight and the canonical local model returned `OK.` to the tiny `Reply exactly OK` request. This proves the original `.shape` server-thread crash was repaired far enough for inference to execute.

However no completed turn-metrics record was produced. Therefore the instrumentation lifecycle remained incomplete and the frozen scientific Pi loop was not started.

The `OK.` vs `OK` punctuation mismatch is **not** treated as a science failure; preflight exists to prove harness health. The real remaining blocker is incomplete/non-closing telemetry.

Preflight only:
- initial free 57%
- initial swap 977.44 MB
- peak MLX 3502.438 MB
- provider/model identity PASS
- no fallback observed

Report: `research/capability/capability-000d-fix1-preflight-failure.md`.

Local-only files currently known from Pi and not yet published to GitHub:

- `scripts/loom_pi_mlx_bridge.py`
- `scripts/capability_000a_memory_attribution.py`
- `scripts/capability_000b_pi_prefill_attribution.py`
- `scripts/capability_000c_prefill_frontier.py`
- `scripts/capability_000d_pi_loop.py`
- `scripts/capability_000d_fix1_pi_loop.py`
- raw evidence under corresponding `results-local/capability/...` directories

Do not assume these local files exist on GitHub until explicitly synchronized.

## Exact next step

Run **CAPABILITY 000D Fix2 — minimal harness repair** only:

1. retain the now-correct list-safe prompt handling;
2. make all telemetry observational/non-fatal;
3. ensure request/turn records close successfully in preflight;
4. preflight PASS criterion is a valid local-model response + complete non-crashing instrumentation, not exact response punctuation;
5. then rerun the identical frozen numbers.txt Pi loop with `prefill_step_size=512`;
6. no prompt/model/context/KV/tool/runtime changes.

If functional Pi-loop admission passes, proceed to frozen CAPABILITY 001. If resource failure occurs only after actual model execution, that becomes valid scientific evidence.

## Later

1. CAPABILITY 001
2. MEMORY-FRONTIER 001 real M1 partial-residency RAM/tok/s curve
3. async prefetch / buffering / direct range I/O
4. M>1 out-of-core weight-I/O amortization
5. scale toward 27B/32B
