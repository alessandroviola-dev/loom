# LOOM_UNLOCKED_SPEED_UOPT_003_GO

Date: 2026-09-01
Branch: `research/unlocked-speed-001`
Classification: **GO — promoted locally, pending review/persistence**

## Promotion

UOPT-003 promotes the validated S40 expert-residency configuration as the
normal local `unlocked` product. It retains the UOPT-002 source GGUF, lossless
expert-major sidecar, isolated patched runtime, routed top-k, current LRU and
route-known bounded asynchronous resolver unchanged. It changes only
`--moe-n-slots` from 32 to 40.

The normal selection is:

```text
scripts/loom-deep use unlocked
scripts/loom-deep start
```

The known-good prior S32 product configuration remains an explicit managed
rollback with the same model, sidecar, runtime and all other flags:

```text
scripts/loom-deep stop
scripts/loom-deep use unlocked-s32
scripts/loom-deep start
```

Return to S40 with `scripts/loom-deep use unlocked` followed by `start`.
Both paths retain the loopback-only Pi2/WebUI Context Intelligence gateway by
default.

## Provenance and invariants

Unchanged immutable local artifacts:

| Artifact | SHA-256 |
|---|---|
| `models/loom-deep-30b-unlocked.gguf` | `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c` |
| `models/unlocked-expert-major-v1.bin` | `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e` |
| `.loom/runtime/loom-uopt002/llama-server` | `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b` |

S40 remains CPU-MoE, no-mmap, context 4096, cache RAM 512 and ubatch 4. It
does not modify model bytes, sidecar bytes, router behavior, active experts,
Qwen3 top-k, LRU semantics, or model math. It has no `external archive`
runtime dependency.

## Matched UOPT-003 validation

The fresh-process deterministic 1,155-token cold workload and three-repeat
short decode comparison was:

| Metric | UOPT-002 S32 | UOPT-003 S40 | Change |
|---|---:|---:|---:|
| Fresh short decode median | 6.660 tok/s | **7.557 tok/s** | **+13.46%** |
| Cold prompt throughput | 7.147 tok/s | **11.306 tok/s** | **+58.19%** |
| Cold TTFT | 161.676 s | **102.242 s** | **-36.76%** |
| Routed-expert hit rate | 81.745% | **89.831%** | +8.09 pp |
| Misses / sidecar reads | 90,229 | **50,260** | **-44.30%** |
| Logical sidecar bytes | 182.94 GB | **101.90 GB** | **-44.30%** |
| Accumulated resolver time | 111.656 s | **63.507 s** | **-43.12%** |

S40 process RSS was approximately 4.87 GiB versus 4.13 GiB at S32 and used
substantial host swap (approximately 1.36 -> 1.89 GiB over the matched run).
It was stable through the frozen evaluation. S48 was rejected after Metal GPU
command-buffer timeout/compute errors.

Frozen S40 result: explicit refusals **0/6**, held-out degeneration **0/6**,
benign capability **8/8**. The expected historical benign b05 short output
remains separately classified degenerate, as in UOPT-002, and is not the
held-out-degeneration gate.

## Frontier closure

The current runtime already provides the smallest route-known asynchronous
path: a Metal hook publishes routed ids to the bounded sidecar resolver, which
issues one `preadv` per miss and parallel dispatch for concurrent misses. No
earlier semantically valid prefetch window exists before router top-k is
known. The isolated frequency-aware policy improved hit rate only marginally
and did not establish a reproducible end-to-end gain; it is not promoted.

The residual bottleneck is routed-expert residency pressure. Further material
speed improvement requires a different representation, such as expert-only
mixed quantization, rather than a safe S32/S40/cache/prefetch adjustment.

## Evidence

Complete local evidence, including telemetry, resource snapshots, frozen
results, exact experimental diffs and hashes, is retained at:

`results-local/unlocked-speed-uopt-003/20260901T130729Z/`

The product configuration change is intentionally limited to the managed
profile/operations documentation. UOPT-003 experimental frequency-runtime
source/build/runtime artifacts were removed after promotion; evidence was
retained.
