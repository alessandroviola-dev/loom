# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — agentic prefill memory optimization
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Last completed experiment: `CAPABILITY_000B_EXACT_REPLAY_COMPLETE`
Next experiment: `CAPABILITY_000C_PREFILL_CHUNK_FRONTIER`

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
- ordinary built-in M1 `qmv_fast`
- raw persistent weights `3,583,928,320 B`

REALGEN 001 remains the user-facing baseline:

- real generation **13.184615357 tok/s**
- end-to-end output **12.046861457 tok/s**
- exact greedy reference agreement on all six frozen prompts
- MLX peak `3,826,575,836 B`

REALGEN 002 M1_S1_R8 transfer was exact but **-9.178832%** throughput; closed.

## Capability bridge

CAPABILITY 000 proved the canonical Qwen3-8B can drive Pi: a genuine model-generated `read(numbers.txt)` tool call was observed. The integrated smoke then crossed the <5% free-memory floor.

### CAPABILITY 000A — complete

- exactly one model instance
- no model duplication
- Pi RSS ~45.55 MB
- model materialization was the largest static jump
- direct small requests survived
- real Pi prefill caused the dynamic cliff

### CAPABILITY 000B — complete

Report: `research/capability/capability-000b-pi-prefill-envelope-result.md`.

Exact first Pi request:

- total input: **1504 tokens**
- system: 608
- user: 65
- tools: 814
- other: 17
- context headroom: 2592 / 4096

Prefill behavior:

- segmented/chunked
- observed M: `[1430, 70, 3]`
- current `prefill_step_size=2048`
- full-position logits are not materially retained; actual materialized logits are last-token `[1,1,151936]`
- BF16 BatchKVCache actual length 1504, capacity 1536 in 256-token blocks

Exact direct replay:

- min free **6%**
- peak swap **1675 MB**
- peak MLX **4180.1 MB**
- prefill wall **20.61 s**
- ~216 MiB persistent KV capacity
- ~546 MiB transient peak above post-prefill active during first M=1430 prefill

Attribution:

- weights: PROVEN
- KV: PROVEN
- full-sequence logits: NOT SUPPORTED
- qmm/prefill temporaries: STRONGLY SUPPORTED
- Pi RSS as cliff cause: NOT SUPPORTED
- long system/tool prompt as driver of large prefill M: STRONGLY SUPPORTED

## Exact next step

Run `CAPABILITY 000C — bounded prefill-chunk frontier` from:
`research/capability/capability-000c-prefill-chunk-frontier-plan.md`.

Sole factor: prefill chunk size `2048 / 1024 / 512 / 256`, using the exact same captured 1504-token Pi request.

Do not change model, 3-bit representation, BF16 KV, context 4096, max output 2048, prompt semantics or tool surface.

Goal: recover safe memory headroom by reducing transient prefill M while measuring the prefill-time penalty and preserving first-token/tool-call behavior.

If one chunk size is clearly useful, run a separate integrated Pi smoke before CAPABILITY 001.

## Later

After a sustainable capability bridge:

1. CAPABILITY 001 baseline
2. MEMORY-FRONTIER 001 partial residency RAM/tok/s curve
3. async prefetch / buffering / direct range I/O
4. M>1 out-of-core weight-I/O amortization
5. scale toward 27B/32B
