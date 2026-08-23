# LOOM 30B MoE Feasibility 001 — Static Result

Date: 2026-08-23
Classification: `LOOM_30B_MOE_FEASIBILITY_001_STATIC_CONDITIONAL`
Target: `Qwen/Qwen3-30B-A3B-MLX-4bit`

## Exact local architecture

Local config/header audit recovered `Qwen3MoeForCausalLM` with 48 layers, hidden size 2048, 32 Q heads, 4 KV heads, head_dim 128, vocab 151936, untied embeddings, SiLU, RMSNorm eps 1e-6, MoE intermediate size 768, 128 routed experts per layer, top-k 8, `norm_topk_prob=true`, no shared-expert tensors, no dense-MLP tensors, no sliding window, max positions 40960, MLX 4-bit quantization with group size 128.

## Exact stored-byte accounting

Total tensor payload: 16,220,499,968 B (15.106518 GiB) across 1,351 tensors / 4 shards.

Mandatory/non-routed set: 819,015,680 B (0.762768 GiB):
- embedding: 165,306,368 B
- LM head: 165,306,368 B
- final norm: 4,096 B
- attention, all layers: 481,296,384 B
- layer norms: 417,792 B
- routers: 6,684,672 B
- shared experts / other shared tensors: 0

Per layer: 10,035,712 B shared/non-routed + 139,264 B router + 320,864,256 B routed expert bank = 331,039,232 B total.

Routed expert bank: 15,401,484,288 B (14.343750 GiB).

One routed expert: 2,506,752 B (2.390625 MiB), identical for all 6,144 expert instances. Each gate/up/down projection is 835,584 B including weight/scales/biases tensors.

Top-k=8 selected experts in one layer: 20,054,016 B (19.125 MiB).

Zero-cache selected-expert traffic across 48 layers for one token: 962,592,768 B = 918 MiB/token.

## Static resident/cache budgets

With mandatory shared set fixed at 819,015,680 B:

| Model budget | Expert cache | Complete experts | Full expert bank | Complete 128-expert layer banks |
| --- | ---: | ---: | ---: | ---: |
| 4.0 GiB | 3,475,951,616 B | 1,386 | 22.559% | 10 |
| 4.5 GiB | 4,012,822,528 B | 1,600 | 26.042% | 12 |
| 5.0 GiB | 4,549,693,440 B | 1,814 | 29.525% | 14 |
| 5.5 GiB | 5,086,564,352 B | 2,029 | 33.024% | 15 |
| 6.0 GiB | 5,623,435,264 B | 2,243 | 36.507% | 17 |

This is stored-byte accounting only; it does not prove runtime workspace/KV-cache sufficiency.

## Zero-cache external bandwidth lower bound

| Generation rate | Required expert bandwidth |
| --- | ---: |
| 1 tok/s | 962.593 MB/s / 918 MiB/s |
| 2 tok/s | 1,925.186 MB/s / 1,836 MiB/s |
| 5 tok/s | 4,812.964 MB/s / 4,590 MiB/s |
| 10 tok/s | 9,625.928 MB/s / 9,180 MiB/s |

At 2 GB/s external bandwidth, 5 tok/s would still require 58.446% expert-traffic reduction/cache-hit-equivalent; at 1 GB/s it would require 79.223%. These are arithmetic requirements, not predicted cache hit rates.

## Physical layout

Each expert is represented by 9 tensor slices. Median/max ranges per expert are 9/9. 93.75% of experts are contained in one shard; 6.25% cross two shards (layers 15, 31, 47).

The current safetensors layout is expert-bank-major: each switch-MLP tensor packs all 128 experts on axis 0 rather than storing complete experts contiguously.

Median same-shard gap between required expert slices: 120,746,752 B. Median summed contiguous span per expert: 3,132,327,424 B for only 2,506,752 useful bytes. Median useful/span efficiency is 0.080028% (P10 0.059797%, P90 0.143477%; worst 0.040349%).

Verdict: `REPACK_RECOMMENDED`.

## Decision

- Mandatory shared set fits a realistic M1 static stored-byte budget: `YES`.
- Routed experts independently addressable from headers: `CONDITIONAL`; exact byte slices are recoverable, but each expert requires 9 discontiguous reads and some layers cross shards.
- Direct streaming from the current safetensors layout is not the intended prototype path because read amplification / range count is extreme.
- Zero-cache expert traffic is high at 918 MiB/token, so useful generation will require measured cache/locality benefit, faster storage, traffic amortization, or some combination.
- First external-expert prototype: `CONDITIONAL`, but scientifically justified if it is layout-aware and does not assume routing popularity or temporal locality.

## Strongest supported conclusion

Qwen3-30B-A3B is structurally suitable for LOOM's sparse-external-expert research because only 0.763 GiB of stored tensors are mandatory/non-routed while 14.344 GiB reside in the routed expert bank. The present artifact layout, not the MoE architecture itself, is the immediate mechanical blocker. A LOOM expert-major representation can remove the current multi-gigabyte contiguous-span amplification, after which measured routing/cache behavior determines whether the 918 MiB/token zero-cache demand can be reduced enough for practical generation.

## Provenance note

Pi reported raw local evidence under `results-local/moe/feasibility-001-static/20260330T000001Z/`. That run-id date is inconsistent with the actual checkpoint date (2026-08-23) and must be treated as a provenance/timestamp anomaly. The numeric result is retained, but future evidence runs must use an actual runtime UTC timestamp.

Local script reported: `scripts/loom_30b_moe_feasibility_001_static.py`.
