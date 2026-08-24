# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — 30B MoE external-expert runtime / traffic-reduction research
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL`
Next core checkpoint: `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001`
Parallel next: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Every final promoted LOOM-produced model must eventually pass validated decensoring/behavioral-freedom preservation using Heretic or a LOOM-native independent equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.
ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical dense baseline

Qwen3-8B full parameter count; affine 3-bit/group64; BF16 KV; MLX/mlx-metal 0.31.2; mlx-lm 0.31.3; thinking disabled.

REALGEN001 historical real M1 generation: 13.184615357 tok/s; E2E 12.046861457 tok/s.
CAPABILITY001: practical-agent 1/11 = 9.09%; Coding Benchmark 45/100; critical failures 0.

Dense partial-residency research remains a controlled implementation laboratory. Naive synchronous dense streaming is too slow; current cleanup/binding micro-axes are exhausted absent new evidence.

## 30B target

Local model:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Exact static anatomy:
- Qwen3MoeForCausalLM;
- 48 MoE layers;
- hidden 2048;
- 128 routed experts/layer;
- top-k 8;
- MoE intermediate 768;
- MLX 4-bit/group128;
- total tensor payload 16,220,499,968 B;
- mandatory/non-routed 819,015,680 B (0.763 GiB);
- routed expert bank 15,401,484,288 B (14.344 GiB);
- one expert 2,506,752 B;
- top-k/layer 20,054,016 B;
- zero-cache expert traffic/token 962,592,768 B (918 MiB).

Static result: `LOOM_30B_MOE_FEASIBILITY_001_STATIC_CONDITIONAL`.

## EXPERT-PACK-001 — PASS

Raw evidence: `results-local/moe/expert-pack-001/20260823T204053Z/`.

Validated on layers 0 and 15:
- 256 experts;
- 641,728,512 B;
- 2,304 components;
- zero hash/byte/metadata mismatches;
- source 9 ranges/expert -> packed 1 contiguous range/expert;
- top-k=8 reads 72 -> 8;
- byte amplification remains 1.0x;
- packed useful/span efficiency 100%.

Lossless expert-major storage is proven. Full 14.344 GiB repack remains conditional until runtime evidence shows it is worth materializing.

## PHYSICAL-IO-001 — INVALID METHOD, CLOSED

Run: `results-local/moe/physical-io-001/20260823T204945Z/`.
Classification: `LOOM_30B_MOE_PHYSICAL_IO_001_CACHE_CONTROL_INVALID`.

Warm and nominal cache-minimized results both appeared memory-like (~14 GB/s), so no physical SSD number was promoted.

## PHYSICAL-IO-002 — CONDITIONAL / DEVICE VERIFIED

Report: `research/moe/loom-30b-moe-physical-io-002-result.md`.
Raw evidence: `results-local/moe/physical-io-002/20260824T062607Z/`.
Classification: `LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL`.

Physical backing device: internal APPLE SSD AP0256Q (`disk0`). Device-level `iostat` evidence passed the sanity gate: a 12.53 GB cache-minimized workload produced ~10.97 GB conservative net device transfer (87.55% coverage); downstream sequential/random/top-k/token-like workloads had ~94.7–101.5% device-byte coverage.

Canonical physical results:
- sequential: 2,391.9 MB/s;
- random expert physical: 1,890.4 MB/s;
- one expert latency P50/P90/P95/P99: 1.197 / 1.509 / 1.643 / 2.019 ms;
- top-k=8 physical: 1,823.1 MB/s;
- top-k latency P50/P90/P95/P99: 9.839 / 12.622 / 13.159 / 14.783 ms;
- token-like 384-read latency P50: 460.074 ms;
- token-like physical: 1,998.8 MB/s.

Zero-cache storage-only lower bound:
- 0.4816 s/token;
- 2.076 tok/s maximum before any model compute.

Necessary external-traffic reduction from storage alone:
- 1 tok/s: 0%;
- 2 tok/s: 0%;
- 5 tok/s: 58.47%;
- 10 tok/s: 79.24%.

Interpretation: SSD bandwidth is not a structural NO-GO, but zero-cache execution cannot deliver the target usability. Cache/reuse and/or multi-token block amortization are now PRIMARY REQUIREMENTS rather than optional optimizations. Because compute adds additional latency, practical 5/10 tok/s operation will require more than the I/O-only reduction figures above.

## DFlash / block speculative branch

Source ingestion complete for the supplied Qwen3.8-27B/DFlash2/Harness video. The video does not demonstrate 27B viability on 8 GB; it used M4 Pro/24 GB and an external M5 Max DFlash benchmark.

Independent research found an exact-target draft model:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash` for `Qwen/Qwen3-30B-A3B`.

Published metadata indicates roughly ~0.7B draft parameters, 5 draft layers, target hidden-state taps at layers 1/12/23/34/45, and average acceptance length ~2.46–3.77 depending on workload.

DFlash is not a memory-fit solution. Its possible LOOM value is amortizing target/expert work across multiple verified positions. The relevant metric is per-layer UNION of routed experts across the verification block divided by accepted tokens. Routing overlap must be measured; no benefit is assumed.

Canonical research note:
`research/architecture/dflash-qwen3-30b-a3b-relevance-001.md`.

## Exact next steps

### Core — `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001`

Prove correct one-layer Qwen3-30B-A3B execution while keeping routed experts external:
1. use layer 0 packed expert-major prototype;
2. keep only the required attention/norm/router/shared tensors resident;
3. route a controlled real activation to top-k experts;
4. load only selected packed experts;
5. reconstruct/apply quantized expert projections exactly;
6. compare output against canonical full-layer execution for parity/tolerance;
7. measure real peak memory, expert-load bytes, I/O latency and total layer latency;
8. no full-model generation yet.

### Parallel — `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

Audit exact draft tensor bytes, architecture, quantization options and 8 GB budget impact before integration.

### After exact execution exists

`LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001`:
- collect real per-position routing choices;
- evaluate blocks 2–8 positions;
- measure unique expert union/layer and expert bytes per accepted token;
- compare with 918 MiB/token baseline and with required 58.47% / 79.24% reductions.

## Storage state

Historical Qwen3-4B-GGUF, Qwen3-8B-GGUF and Qwen3-8B-4bit MLX are archived externally. Qwen3-8B-3bit and Qwen3-30B-A3B-MLX-4bit remain local. Expert-pack prototype uses ~612 MiB plus metadata. Latest observed free internal space was ~63 GiB before subsequent small evidence files.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
