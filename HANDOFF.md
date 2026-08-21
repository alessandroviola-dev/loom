# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge / multi-turn memory frontier
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `CAPABILITY_000D_FIX2_RESOURCE_ABORT`
Next: `CAPABILITY_000E_FRESH_VS_SEQUENTIAL_TURN_ATTRIBUTION`

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

### CAPABILITY 000D / Fix1 — HARNESS FAILURES / NO SCIENCE

Original 000D failed before prefill because instrumentation used `.shape` on a list. Fix1 repaired that issue but finalized telemetry on the wrong `mlx_lm.server` lifecycle hook, so the scientific task still did not start. These runs consumed no scientific attempt.

### CAPABILITY 000D Fix2 — VALID SCIENTIFIC RESOURCE RESULT

Report: `research/capability/capability-000d-fix2-resource-abort-result.md`.

Fix2 repaired telemetry lifecycle and passed preflight. Telemetry errors: 0.

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

- input 1576 tokens, only +55 vs first
- first 512 prefill segment began
- peak MLX observed 4146.45 MB
- free memory crossed hard gate at 4%
- resource abort before second tool action

`answer.txt` absent; `numbers.txt` byte-identical. No provider fallback.

Classification: `CAPABILITY_000D_FIX2_RESOURCE_ABORT`.

This proves step 512 can execute one real Pi tool turn but is not yet sustainable across the next turn under the observed state.

## Exact unresolved question

The second request had only 55 more input tokens but peak MLX increased by ~71.33 MB. We do not yet know whether:

1. a fresh 1576-token request intrinsically exceeds the safe envelope; or
2. request 1 leaves allocator cache / Python references / MLX state / other residual memory that makes request 2 fail.

Do not jump directly to step 256, KV quantization, prompt compression or context reduction before resolving this distinction.

## Exact next step

Run **CAPABILITY 000E — fresh-vs-sequential turn attribution** using the exact captured 1521-token and 1576-token request bodies from Fix2.

Required comparison:

- fresh server/model -> exact request 2 alone;
- fresh server/model -> exact request 1 then exact request 2 sequentially, with no cleanup treatment;
- measure model-idle, post-request active/cache, Python/RSS/system memory, KV lifetime, allocator/cache retention and second-request peak.

Sole purpose: determine whether the failure is intrinsic prompt-length pressure or inter-request accumulation. No production cleanup treatment yet.

## Local-only files known from Pi

Recent implementation/evidence remain local unless explicitly synchronized:

- `scripts/loom_pi_mlx_bridge.py`
- `scripts/capability_000a_memory_attribution.py`
- `scripts/capability_000b_pi_prefill_attribution.py`
- `scripts/capability_000c_prefill_frontier.py`
- `scripts/capability_000d_pi_loop.py`
- `scripts/capability_000d_fix1_pi_loop.py`
- `scripts/capability_000d_fix2_pi_loop.py`
- raw `results-local/capability/...` evidence

Do not assume these exist on GitHub until synchronized.

## Later

1. resolve multi-turn bridge memory
2. CAPABILITY 001 frozen 12-task baseline
3. MEMORY-FRONTIER 001 real M1 partial-residency RAM/tok/s curve
4. async prefetch / buffering / direct range I/O
5. M>1 out-of-core weight-I/O amortization
6. scale toward 27B/32B
