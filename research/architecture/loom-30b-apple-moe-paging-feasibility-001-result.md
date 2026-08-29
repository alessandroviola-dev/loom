# LOOM 30B Apple MoE Paging Feasibility 001 — Result

Date: 2026-08-29
Classification: **LOOM_30B_APPLE_MOE_PAGING_FEASIBILITY_GO**

## Result

The base Apple M1 8 GiB host passed the frozen no-model feasibility gate for the Apple-Silicon MoE expert-residency PoC.

Evidence: `results-local/research/30b-apple-moe-paging-feasibility-001/20260829T130414Z/report.json`
Harness: `scripts/loom_30b_apple_moe_paging_feasibility_001.py`
Harness SHA256: `c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844` is the built llama-cli binary SHA reported by the run; the harness itself must remain identifiable from local evidence. No Git commit/push was performed locally.

## Host

- Apple M1, arm64
- 8 GiB unified RAM
- macOS 26.5 (25F71)
- Xcode 26.6
- Apple clang 21.0.0
- CMake 4.4.2
- ~30 GiB free storage at probe time

## Frozen source/build

Source: `kisasexypantera94/llama.cpp`, branch `moe-expert-residency`, exact commit `41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Native Metal configure/build succeeded without source patching or package installation. Configure ~7.354 s; build ~138.304 s. Built `llama-cli` SHA256: `c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844`.

`--list-devices` exposed `MTL0: Apple M1 (5461 MiB, 5460 MiB free)`.

Required flags were present: `--moe-n-slots`, `--moe-n-layers`, `--no-mmap`, `--no-warmup`.

## Mechanism confirmed

Source inspection confirmed:
- bounded per-layer expert slots and LRU eviction in `src/llama-moe-offloader.{h,cpp}`;
- direct expert disk reads using `pread(...)` in `src/llama-moe-offloader.cpp`;
- Apple/Metal gating in `src/llama-context.cpp`;
- Metal interceptor path in `ggml-metal-ops.cpp` / `ggml-metal.metal`;
- backend/Metal synchronization required by the paging path.

## Local storage diagnostic

Existing `fullbank/experts.bin` (~15.4 GB) was sampled read-only using `os.pread`/`O_RDONLY`. A 512 MiB sample measured ~2579.51 MiB/s. This is diagnostic only, not an inference throughput claim.

## Frozen memory projection

Projection includes 1 GiB KV reserve, 1.5 GiB runtime/Metal reserve and 2 GiB OS headroom.

| Expert slots | Q3_K_S-3.25 total | IQ3_S-3.29 total |
|---:|---:|---:|
| 8 | 6.304 GiB | 6.319 GiB |
| 16 | 6.954 GiB | 6.974 GiB |
| 24 | 7.604 GiB | 7.629 GiB |
| 32 | 8.253 GiB | 8.283 GiB |

8/16/24 are plausible under the frozen estimate; 32 is not.

## Candidate decision

Both frozen ByteShape candidates were classified `COMPATIBLE_FOR_STAGE1`.

Selected single Stage-1 candidate:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Published size ~12.4 GB and normalized quality 97.97%. Frozen expected SHA256: `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

The alternative IQ3_S-3.29bpw is not authorized for Stage 1.

## Scientific boundary

This GO proves host/build/mechanism feasibility only. It makes no speed, TTFT, quality or stability claim for M1 8GB inference. Stage 1 must perform the first real model download and bounded generation test before the DEEP runtime direction can change.