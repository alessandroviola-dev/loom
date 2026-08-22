# SHARED-STAGE-RESIDENCY 001 — result

Date: 2026-08-22
Classification: `SHARED_STAGE_RESIDENCY_001_COMPLETE`

## Purpose

Test one factor on the MEMORY-FRONTIER 001 F1/H32 point: keep the same transformer residency while making the large shared stages persistent instead of streaming them every generated token.

## Arms

CONTROL:
- transformer layers 0..31 persistent
- transformer layers 32..35 streamed
- embedding, final norm and LM head streamed
- persistent raw weights: 2,701,672,448 B
- logical streamed token-path bytes: 882,255,872 B/token

TREATMENT:
- transformer layers 0..31 persistent
- transformer layers 32..35 streamed through the same path
- embedding, final norm and LM head persistent, materialized once pre-execution
- persistent raw weights: 3,246,219,264 B
- logical streamed token-path bytes: 337,709,056 B/token

Exact token parity passed for CONTROL and TREATMENT, including separate 16-token preflight and every scientific prompt.

## Scientific design

Four fresh ABBA constituents, each using the first three canonical REALGEN 001 prompts and 64 greedy unknown tokens/prompt or EOS. No resource aborts.

## Pooled results

| Arm | Valid | Persistent B | Streamed B/token | Real gen tok/s | E2E tok/s | Median TTFT | Peak MLX | Min free | Peak swap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTROL | 2/2 | 2,701,672,448 | 882,255,872 | 2.532 | 2.384 | 1.735 s | 2,739,421,424 B | 25% | 1326.94 MB |
| TREATMENT | 2/2 | 3,246,219,264 | 337,709,056 | 3.459 | 3.214 | 1.503 s | 3,283,968,240 B | 23% | 1311.62 MB |

## Causal treatment effect

TREATMENT vs contemporaneous CONTROL:
- generation ratio: **1.3666x**
- generation throughput: **+36.66%**
- E2E throughput: **+34.80%**
- TTFT: **-13.34%**
- peak MLX: **+544,546,816 B** (+519.32 MiB)
- minimum-free delta: **-2 pp**
- persistent raw bytes: **+544,546,816 B**
- logical streamed bytes/token: **-544,546,816 B/token**
- process-read diagnostic: **-14,500,245 B/token**

## Context versus F0

Historical MEMORY-FRONTIER F0 is contextual only, not the causal control.

TREATMENT:
- retains **25.75%** of F0 generation throughput
- still saves **337,709,056 B** peak MLX versus F0
- still saves **337,709,056 B** persistent raw weights versus F0
- speed band remains `SLOW_REFERENCE`

## Interpretation

Repeated shared-stage streaming is a **material addressable system cost**. Making embedding, final norm and LM head persistent improves real generation by 36.66% without changing model math or transformer residency.

However, this factor is not sufficient to explain the F1 slowdown. Even after removing 544,546,816 B/token of repeated shared-stage streaming, the system reaches only 3.459 tok/s versus 13.433 tok/s for F0. The remaining exact system-level difference is that transformer layers 32..35 are still streamed each generated token.

No internal mechanism is claimed from this experiment. In particular, physical SSD traffic is **not proven**; the causal factor is shared-stage persistence as a whole.

## Raw local evidence

`results-local/memory/shared-stage-residency-001/20260822-162744/`

Local runner:
`scripts/loom_shared_stage_residency_001.py`
