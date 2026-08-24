# LOOM 30B MoE Shared Backbone Residency 001 — Result

Date: 2026-08-24
Classification: `LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS`
Run: `20260824T071921Z`

The complete non-routed Qwen3-30B-A3B target structure was constructed through targeted safetensor reads on the reference Apple M1 / 8 GB machine while keeping every routed-expert tensor absent.

## Exact resident structure

- resident tensor count: 919
- exact logical resident stored bytes: 819,015,680 B
- reconciliation to static audit: PASS
- routed-expert tensors resident: 0
- routed-expert logical bytes resident: 0
- expert exclusion gate: PASS

Final MLX active memory was 819,032,072 B with 0 B MLX cache. Final RSS was 817,463,296 B. Peak MLX construction memory was 819,032,072 B; peak RSS by `ru_maxrss` was 1,122,189,312 B. Swap remained unchanged at 921.94 MiB before and after the run. Memory-pressure gate passed with no swap growth and no throttled pages.

## Staged MLX active memory

S0-S9 (bytes):
`780, 165315340, 246715020, 328114700, 409514380, 490914060, 572313740, 653713420, 653717512, 819032072`

## Functional checks

- embedding: PASS
- layer-0 attention: PASS
- routers L0/L23/L47: PASS / PASS / PASS
- final norm: PASS
- LM head: PASS

## KV accounting

BF16 KV: 98,304 B/token (96 KiB/token).

- 128 tokens: 12 MiB
- 256: 24 MiB
- 512: 48 MiB
- 1,024: 96 MiB
- 2,048: 192 MiB
- 4,096: 384 MiB
- 8,192: 768 MiB

## Expert-cache capacity reference

At 2,506,752 B/expert:

- 512 MiB: 214 experts
- 1 GiB: 428
- 2 GiB: 856
- 3 GiB: 1,285
- 4 GiB: 1,713

The run also found plausible headroom for an additional quantized DFlash drafter under the modeled 6.0-7.5 GiB working budgets, without assuming its exact final footprint.

## Decision

- complete shared target viable on M1 8 GB: YES
- serial external-expert headroom: YES
- meaningful expert-cache headroom: YES
- plausible DFlash headroom: YES
- complete 48-layer external forward justified: YES

Strongest supported conclusion: the complete target backbone can remain resident through exact targeted reads with zero routed-expert tensors resident, leaving practical headroom for serial external experts, KV/runtime workspace, expert cache research and a possible quantized drafter.

Raw local evidence: `results-local/moe/shared-backbone-residency-001/20260824T071921Z/`.
