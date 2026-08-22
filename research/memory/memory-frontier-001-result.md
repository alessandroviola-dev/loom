# MEMORY-FRONTIER 001 — real-M1 residency / RAM / speed result

Date: 2026-08-22
Classification: `MEMORY_FRONTIER_001_COMPLETE`

## Purpose

Measure the real greedy M1 trade-off between persistent Qwen3-8B weight residency, unified-memory headroom, streamed-weight traffic and generation throughput on Apple M1 / 8 GB.

Canonical model/runtime remained Qwen3-8B full parameter count, affine 3-bit/group64, BF16 KV, MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, thinking disabled.

Raw local evidence:
`results-local/memory/memory-frontier-001/20260822-141554/`

## Correctness

All partial-residency configurations passed the real-M1 parity preflight. All ten constituent scientific runs produced exact complete token-ID parity against corresponding F0 outputs for all three prompts. No resource abort occurred.

This establishes that the measured speed/memory differences are system-execution effects, not model-output changes.

## Residency frontier

| Config | Persistent transformer layers | Resident raw bytes | Resident fraction | Logical streamed B/model pass |
|---|---:|---:|---:|---:|
| F0 FULL | 0..35 | 3,583,928,320 | 100.00% | 0 |
| F1 H32 | 0..31 | 2,701,672,448 | 75.38% | 882,255,872 |
| F2 H24 | 0..23 | 2,026,254,336 | 56.54% | 1,557,673,984 |
| F3 H16 | 0..15 | 1,350,836,224 | 37.69% | 2,233,092,096 |
| F4 H8 | 0..7 | 675,418,112 | 18.85% | 2,908,510,208 |

For F1-F4, shared embed/final-norm/LM-head handling follows the validated streaming path and is included in the streamed-byte accounting.

## Pooled real-M1 results

| Config | Gen tok/s | E2E tok/s | Median TTFT | Peak MLX bytes | Min free | Peak swap MB | Logical streamed B/token | Band |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| F0 | 13.433 | 11.226 | 0.997 s | 3,621,677,296 | 23% | 1509.12 | 0 | interactive candidate |
| F1 | 2.527 | 2.378 | 1.753 s | 2,756,903,152 | 24% | 1210.31 | 896,041,120 | slow reference |
| F2 | 1.168 | 1.125 | 3.007 s | 2,081,485,040 | 34% | 1250.31 | 1,582,012,640 | slow reference |
| F3 | 0.526 | 0.513 | 5.051 s | 1,406,066,928 | 47% | 1266.31 | 2,267,984,160 | impractical reference |
| F4 | 0.435 | 0.425 | 6.029 s | 730,648,816 | 57% | 1450.31 | 2,953,955,680 | impractical reference |

Historical REALGEN 001 = 13.184615357 real tok/s; fresh F0 = 13.433 tok/s, consistent as a sanity check.

## Relative to F0

F1 is the strongest measured compromise in the current implementation:
- logical persistent raw-weight saving: 882,255,872 B;
- peak MLX saving: 864,774,144 B;
- minimum-free change: +1 pp;
- real generation retained: 18.81%;
- E2E retained: 21.18%;
- added logical streaming: 896,041,120 B/generated token.

F2 saves ~1.54 GB peak MLX and improves minimum free by +11 pp, but retains only 8.69% generation throughput.

F3/F4 produce large memory headroom but are below 1 real tok/s.

## Pareto result

All five measured points are non-dominated because every reduction in residency buys memory/headroom at a throughput cost. None is dominated by another point under the measured dimensions.

This means there is no hidden free lunch in the current synchronous streaming implementation.

## Critical interpretation

The current streaming path is suitable as a correctness/reference mechanism but is far too expensive for practical partial-residency generation.

F1 demonstrates the key architecture problem clearly: moving only ~24.6% of raw weights out of persistent residency reduces real generation from 13.433 to 2.527 tok/s, an ~81.2% throughput loss.

Do not label the loss as physical SSD bandwidth cost yet. The primary counter is logical bytes loaded/materialized from the streaming source. Darwin process-read bytes are diagnostic only and differ substantially from logical traffic:
- F1 process-read diagnostic: ~26.5 MB/token;
- F1 logical streamed traffic: ~896.0 MB/token.

Therefore the next scientific question is where the streaming wall time actually goes: source/range access, OS page cache, tensor reconstruction/materialization, quantized-weight setup, MLX evaluation/synchronization, or compute.

## Decision

Do not reduce residency further and do not begin a broad optimization bundle.

Use F1 H32 as the first attribution target because it is the least aggressive partial-residency point and the strongest current RAM/speed trade-off. Perform timing attribution before selecting async prefetch, buffering, range-I/O or another treatment.
