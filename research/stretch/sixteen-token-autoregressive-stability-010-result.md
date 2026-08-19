# Stretch 010 — Sixteen-Token Autoregressive Stability — Result

Date: 2026-08-19
Valid run: `20260819-183844`
Classification: **SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS**

## Provenance

Plan:
`research/stretch/sixteen-token-autoregressive-stability-010-plan.md`

Runner:
`scripts/stretch_sixteen_token_autoregressive_stability_010.py`

Frozen runner blob:
`ff3dc83abc6388113fca15594eef6b3ec00ebe50`

Frozen source:
Stretch 009 blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`.

Environment/model remained frozen:
- Apple M1 / 8 GB reference machine
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- Qwen3-8B 3-bit/group64
- 36 transformer layers
- prompt token IDs `[[1,42,2048,151935]]`
- ordinary BF16 per-layer `KVCache`
- deterministic argmax
- official resident control
- phase-streamed embedding -> 36 layers -> final norm -> LM head
- no tokenizer, sampling, KV quantization, prefetch, model download, or optimization.

Single scientific change vs Stretch 009: continuation depth **4 -> 16 generated/feedback tokens**.

## PASS: numerical/token stability

Prompt parity:
- pass true
- max absolute difference **0.0**
- mean absolute difference **0.0**
- first-token equality true.

All 16 autoregressive feedback steps:
- numerical parity pass true at every step
- max absolute difference **0.0** at every step
- mean absolute difference **0.0** at every step
- top-1 equality true at every step.

Resident generated sequence:
`[1, 374, 264, 4647, 1483, 304, 279, 1809, 315, 5994, 320, 1654, 23740, 285, 8, 311]`

Streamed generated sequence:
`[1, 374, 264, 4647, 1483, 304, 279, 1809, 315, 5994, 320, 1654, 23740, 285, 8, 311]`

Generated-sequence equality: **true**.

## KV state

Expected progression:
- prompt offset 4
- final offset 20 after 16 feedback passes.

Observed final resident offsets: all **20**.
Observed final streamed offsets: all **20**.

Final KV bytes:
- resident **37,748,736 B**
- streamed **37,748,736 B**.

No new ordinary KVCache capacity block was required because offset 20 remains below the initial 256-position allocation boundary.

## Weight residency

Resident full-model materialized delta:
**3,583,928,320 B**.

Maximum streamed raw-weight-stage delta:
**272,269,312 B**.

Resident / max-streamed-stage ratio:
**13.16317396798652x**.

Persistent KV memory remains accounted separately from the raw-weight-stage ratio.

## Per-token timing

36-layer materialization wall seconds for the 16 streamed feedback passes:
`[0.212377, 0.190494, 0.18926, 0.187676, 0.464371, 1.359481, 0.519632, 1.396424, 1.413411, 1.425179, 1.425537, 1.442005, 1.412515, 1.404428, 1.41408, 1.397497]`

Mean layer materialization:
**0.990898 s/token**.

36-layer forward wall seconds:
`[0.192415, 0.189752, 0.193819, 0.193034, 0.19967, 0.194331, 0.193464, 0.191153, 0.189529, 0.185873, 0.192811, 0.189646, 0.191889, 0.192203, 0.198905, 0.191275]`

Mean layer forward:
**0.192486 s/token**.

The forward compute remains approximately stable while the layer-materialization wall changes regime during the run.

Full streamed pass wall seconds:
`[1.863135, 1.838579, 1.849972, 1.833425, 2.366761, 3.336781, 2.38608, 3.34347, 3.425303, 3.465824, 3.485435, 3.454962, 3.358077, 3.369774, 3.487604, 3.358349]`

Mean full streamed pass:
**2.888971 s/token**.

Median full streamed pass:
**3.350773 s/token**.

Logical streamed throughput under this run's host/cache state:
**0.346144 token/s**.

This is a logical end-to-end runtime measurement for the current implementation. It is **not** physical SSD throughput and does not establish physical storage bytes/token because repeated safetensors accesses can be served partly or fully by macOS page cache.

## Materialization regime change

A reproducible-looking transition appears in the timing series:
- tokens 1–4: layer materialization ~0.19–0.21 s
- token 5: 0.464371 s
- token 6: 1.359481 s
- token 7: 0.519632 s
- tokens 8–16: approximately 1.40–1.44 s.

At the same time, transformer forward remains approximately 0.19 s/token.

Therefore the observed late-run slowdown is associated with the materialization path, not with increasing transformer compute cost over offsets 5..20. The present data **do not identify the cause**. Candidate mechanisms include a change in page-cache hit rate / physical I/O behavior or another materialization/allocator effect. No causal claim is made from timing alone.

## Host/resource telemetry

Launch gate:
- 71% free / 1129.94 MB swap
- 72% free / 1129.94 MB swap
- 72% free / 1129.94 MB swap.

Whole run:
- minimum free memory **24%**
- peak swap **1563.31 MB**
- peak child RSS **764.844 MB**
- disk **36.272 -> 36.270 GiB**.

Phase buckets:
- resident: min free **24%**, peak swap **1563.31 MB**, peak child RSS **493.75 MB**
- stream prompt: min free **70%**, peak swap **1507.31 MB**, peak child RSS **175.016 MB**
- stream tokens: min free **66%**, peak swap **1499.31 MB**, peak child RSS **354.938 MB**.

Whole-run minima/maxima include the resident control; phase buckets are diagnostic and polling-based.

## Canonical interpretation

Stretch 010 establishes that the phase-streamed Qwen3-8B path sustains **16 consecutive deterministic autoregressive feedback passes** with persistent KV state and exact official-resident parity at every step, while maximum raw-weight stage residency remains ~272.27 MB.

It also establishes the first unoptimized end-to-end logical latency baseline and reveals a substantial late-run increase in **weight materialization wall time** while transformer forward time remains stable.

The cause of that materialization regime change is unresolved. It must be instrumented before attributing the slowdown to physical SSD bandwidth, page-cache eviction, MLX allocation, or another mechanism.

## Decision

Before tokenizer/text integration or optimization, run an instrumentation-only replication of the same 16-token workload with per-process Darwin resource accounting around streamed weight materialization. Measure cumulative `proc_pid_rusage` disk-read bytes and page-ins at sufficiently fine boundaries to test whether the timing transition coincides with a storage/page-in transition. Preserve the scientific workload, parity gates, cache policy and guardrails unchanged.