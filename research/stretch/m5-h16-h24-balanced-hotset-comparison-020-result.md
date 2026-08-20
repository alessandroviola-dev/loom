# LOOM Stretch 020 — M5 H16 vs H24 Balanced Hotset Comparison — Result

Status: **COMPLETE PASS**

Classification:
`M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS`

Valid run:
`20260820-144043`

Run directory:
`results-local/stretch/m5-h16-h24-balanced-hotset-comparison-020/20260820-144043`

Summary:
`results-local/stretch/m5-h16-h24-balanced-hotset-comparison-020/20260820-144043/summary.json`

## Frozen provenance

H16 helper:
- `scripts/stretch_five_token_h16_hotset_variant_019.py`
- blob `6a0bd001ad7a5a5bf5646b54a302f7fc372e4367`

H24 helper:
- `scripts/stretch_five_token_h24_hotset_variant_020.py`
- blob `09363f4ce669a7de7b2f16fe4dfb63519c72eb9f`

Balanced runner:
- `scripts/stretch_m5_h16_h24_balanced_hotset_comparison_020.py`
- blob `d2f891462a786f334ceb11bb2e2528e9c2f0203d`

Frozen exact target geometry:
- oracle block size `M=5`
- balanced order `H16 -> H24 -> H24 -> H16`
- no deliberate cache purge
- Qwen3-8B 3-bit/group64
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- ordinary BF16 KV
- exact parity/top-1 policy
- inherited host/resource/I-O gates.

Scientific factor only:
- persistent transformer residency `16 -> 24` layers.

## Result

All four constituent runs passed their inherited scientific and provenance gates.

Target verification:
- H16 pooled rate: `1.8043852696963538 token/s`
- H24 pooled rate: `2.433357437090613 token/s`
- H24/H16 rate ratio: `1.3485797506538635x`
- H24 controlled improvement: **~34.86%**.

Target block wall:
- H16 median: `2.7883325 s`
- H24 median: `2.0068175 s`
- H24/H16 ratio: `~0.71972x`
- reduction: **~28.03%**.

Materialization / compute / process-I/O attribution:
- H24/H16 median materialization ratio: `0.16043963086388105x` (~83.96% lower)
- H24/H16 median forward ratio: `0.7771261247356858x` (~22.29% lower)
- H24/H16 mean full-pass process-read bytes/block ratio: `0.024249004705030764x` (~97.58% lower).

Residency:
- H16 persistent hotset: `1,350,836,224 B`
- H24 persistent hotset: `2,026,254,336 B`
- H16 hybrid raw-weight budget: `1,623,105,536 B`
- H24 hybrid raw-weight budget: `2,298,523,648 B`.

Resource telemetry:
- H16 minimum observed free memory: `16%`
- H24 minimum observed free memory: `21%`
- H16 peak observed swap: `2199.81 MB`
- H24 peak observed swap: `2288.56 MB`.

Disk free after:
`~35.687 GiB`

## Canonical interpretation

Stretch 020 confirms that increasing persistent transformer residency remains a high-leverage speed axis at H24. H24 improves the controlled M5 target-verification rate by ~34.86% versus H16 while preserving all inherited exactness/resource gates.

The gain is primarily associated with a sharp reduction in materialization and process-read cost. The forward-time reduction is smaller, so the result reinforces repeated weight traversal/materialization as the dominant target-side cost under the frozen MLX 0.31.2 architecture.

Do **not** infer from H24's `21%` minimum free memory versus H16's `16%` that H24 intrinsically uses less memory; these are system-wide observations from different constituent runs and are host-state dependent.

Do **not** compare absolute target-rate values across separate Stretch experiments as causal measurements. Use the balanced within-experiment ratios for decisions.

## Decision

1. Freeze `M=5 + H24` as the best demonstrated target-side profile so far under the frozen runtime.
2. Continue the same residency axis by one preregistered step to H32 while preserving all gates.
3. Do not jump directly to H36; H32 keeps a meaningful hybrid configuration with four transformer layers still streamed.
4. If H32 materially improves rate and remains within gates, H36 may be considered as a separate ceiling experiment.
5. If H32 is flat, slower, or resource-limited, stop residency scaling and move to another independent factor such as prefetch/double-buffering.
