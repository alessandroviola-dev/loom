# CAPABILITY 000C — Prefill chunk-size frontier

Date: 2026-08-21
Status: COMPLETE
Classification: `CAPABILITY_000C_PREFILL_FRONTIER_COMPLETE`

## Purpose

Map the exact 1504-token Pi request across different `prefill_step_size` values while keeping model, tokenizer, chat template, BF16 KV, tool schema and request bytes unchanged.

## Canonical request

- Qwen3-8B 3-bit affine/group64
- MLX 0.31.2 / mlx-lm 0.31.3
- BF16 KV
- context capacity 4096
- exact Pi input 1504 tokens
- decomposition: system 608 / user 65 / tools 814 / other 17

## Results

| step | M segments | wall s | tok/s | peak MLX MB | transient MB | min free % | swap MB | top1 same | bit exact |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 512 | 512,512,406,70,3 | 23.74 | 63.36 | 4089.8 | 455.6 | 15 | 2445.9 | yes | yes |
| 2048 | 1430,70,3 | 27.91 | 53.88 | 4180.1 | 545.9 | 17 | 2569.9 | yes | yes |
| 256 | 256,256,256,256,256,150,70,3 | 28.24 | 53.26 | 3980.7 | 346.5 | 15 | 2359.3 | yes | no |
| 1024 | 1024,406,70,3 | 36.72 | 40.96 | 4160.9 | 526.7 | 17 | 2826.1 | yes | yes |
| 384 | 384,384,384,278,70,3 | 39.95 | 37.64 | 4066.8 | 414.6 | 17 | 2581.9 | yes | yes |
| 768 | 768,662,70,3 | 29.77 | 50.53 | 4082.1 | 447.9 | 18 | 2478.6 | yes | yes |

## Interpretation

`512` is the strongest operational candidate. Relative to the canonical 2048 point it:

- reduces prefill wall from 27.91 s to 23.74 s (~14.94% less wall);
- raises effective prefill throughput from 53.88 to 63.36 tok/s (~17.59%);
- lowers peak MLX by 90.3 MB (~2.16%);
- lowers measured prefill transient by 90.3 MB (~16.54%);
- preserves top-1 and is bit-exact.

The 256 point is the lowest-memory point (3980.7 MB peak, 199.4 MB / 4.77% below 2048) with nearly unchanged wall, but it is not bit-exact. The Pareto frontier is 512 and 256.

System-level `min free %` and swap vary with host state and are diagnostic rather than causal across separate runs. The MLX peak/wall comparison and exact output checks are the stronger within-study evidence.

## Decision

Do not yet run the full 12-task CAPABILITY 001 suite. First validate the complete Pi multi-turn tool loop with `prefill_step_size=512` while preserving context 4096, BF16 KV, the full tool surface and the canonical Qwen3-8B 3-bit model.

Evidence: `results-local/capability/capability-000c/20260821-145837/`.

Local implementation: `scripts/capability_000c_prefill_frontier.py` (not yet synchronized to GitHub at this checkpoint because it exists only in the local worktree).
