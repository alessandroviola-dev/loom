# LOOM — Active Handoff

Last updated: 2026-08-23
Status: ACTIVE — 30B MoE external-expert storage/runtime research
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_PHYSICAL_IO_001_CACHE_CONTROL_INVALID`
Active side research: `VIDEO_RESEARCH_INGEST_001` (Qwen3.8-27B / DFlash2 / Harness)
Next core checkpoint: `LOOM_30B_MOE_PHYSICAL_IO_002_DEVICE_VERIFIED`

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

Exact local static audit:
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
Core finding: sparse external-expert research is structurally justified because almost all model storage lives in routed experts while mandatory non-expert weights are <1 GiB.

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

This proves a lossless expert-major representation and independent expert addressing.

The same run's ~14–15 GB/s throughput and ~66 ms 48-layer extrapolation remain NON-CANONICAL because the data could have been served from memory/page cache.

## PHYSICAL-IO-001 — CACHE CONTROL INVALID

Run: `results-local/moe/physical-io-001/20260823T204945Z/`.
Classification: `LOOM_30B_MOE_PHYSICAL_IO_001_CACHE_CONTROL_INVALID`.

Verified:
- `F_NOCACHE=48` recovered from local SDK and accepted;
- `F_RDAHEAD=45` recovered from local SDK and accepted;
- 1,002,700,800 B control region;
- warm control ~14,439 MB/s;
- nominal cache-minimized path ~13,800 MB/s;
- only ~1.046x separation.

Interpretation: the method did not defensibly isolate physical SSD service. The run correctly stopped at the sanity gate before >RAM, random expert, top-k or token-like measurements.

Therefore:
- physical SSD throughput: UNKNOWN;
- physical expert-read latency: UNKNOWN;
- zero-cache seconds/token: NOT DERIVED;
- cache/reuse requirement: NOT YET QUANTIFIED;
- external-expert architecture: NOT INVALIDATED.

## Next core checkpoint

`LOOM_30B_MOE_PHYSICAL_IO_002_DEVICE_VERIFIED`

Improve instrumentation rather than merely repeating `F_NOCACHE`:
1. identify the actual internal physical disk backing the LOOM volume;
2. use macOS `iostat` device counters/rates before, during and after test reads;
3. require actual device MB transferred to materially track requested bytes before accepting a result as physical-storage evidence;
4. keep deterministic 2,506,752 B expert-sized reads;
5. use >RAM unique working set across the model shards;
6. retain `F_NOCACHE` + disabled read-ahead where supported;
7. measure sequential, random expert, top-k=8 and 384-read token-like workloads only after the device-I/O sanity gate passes;
8. no generation/full model load/full pack.

This should distinguish page-cache service from real block-device activity without requiring `sudo`.

## Active source ingestion

Pi is currently transcribing/analyzing the supplied video `Qwen3.8 27B + Harness Il Coding Agent LOCALE Definitivo.mp4` with faster-whisper under `VIDEO_RESEARCH_INGEST_001`.

The video appears potentially relevant to LOOM through DFlash2/block speculative decoding and multi-token amortization, but no roadmap promotion should occur until the transcript and visual claims are reviewed.

## Storage state

Historical Qwen3-4B-GGUF, Qwen3-8B-GGUF and Qwen3-8B-4bit MLX are archived externally. Qwen3-8B-3bit and Qwen3-30B-A3B-MLX-4bit remain local. Expert-pack prototype uses ~612 MiB plus metadata. Latest physical-I/O run observed ~63.1 GiB free.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
