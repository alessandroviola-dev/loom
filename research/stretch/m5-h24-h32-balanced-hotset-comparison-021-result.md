# LOOM Stretch 021 — M5 H24 vs H32 Balanced Hotset Comparison — Result

Status: **COMPLETE PASS**

Classification:
`M5_H24_H32_BALANCED_HOTSET_COMPARISON_PASS`

Valid run:
`20260820-145035`

Run directory:
`results-local/stretch/m5-h24-h32-balanced-hotset-comparison-021/20260820-145035`

Summary:
`results-local/stretch/m5-h24-h32-balanced-hotset-comparison-021/20260820-145035/summary.json`

## Frozen provenance

H24 helper:
- `scripts/stretch_five_token_h24_hotset_variant_020.py`
- blob `09363f4ce669a7de7b2f16fe4dfb63519c72eb9f`

H32 helper:
- `scripts/stretch_five_token_h32_hotset_variant_021.py`
- blob `b6b39dfb095b905ed659d52903309783efc02be7`

Balanced runner:
- `scripts/stretch_m5_h24_h32_balanced_hotset_comparison_021.py`
- blob `fa52f21a7ae02a4fcae6c73416ad2ef63cc0ae45`

Frozen exact target geometry:
- oracle block size `M=5`
- balanced order `H24 -> H32 -> H32 -> H24`
- no deliberate cache purge
- Qwen3-8B 3-bit/group64
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- ordinary BF16 KV
- exact parity/top-1 policy
- inherited host/resource/I-O gates.

Scientific factor only:
- persistent transformer residency `24 -> 32` layers.

## Result

All four constituent runs passed their inherited scientific and provenance gates.

Target verification:
- H24 pooled rate: `2.7358720706219777 token/s`
- H32 pooled rate: `3.0490014164644244 token/s`
- H32/H24 rate ratio: `1.1144532119044803x`
- H32 controlled improvement: **~11.45%**.

Target block wall:
- H24 median: `1.807173 s`
- H32 median: `1.6119785 s`
- H32/H24 ratio: `~0.8920x`
- reduction: **~10.80%**.

Materialization / compute / process-I/O attribution:
- H32/H24 median materialization ratio: `0.3422754314008055x` (~65.77% lower)
- H32/H24 median forward ratio: `0.964972714944873x` (~3.50% lower)
- H32/H24 mean full-pass process-read bytes/block ratio: `0.006146087778740841x` (~99.39% lower).

Residency:
- H24 persistent hotset: `2,026,254,336 B`
- H32 persistent hotset: `2,701,672,448 B`
- H24 hybrid raw-weight budget: `2,298,523,648 B`
- H32 hybrid raw-weight budget: `2,973,941,760 B`.

Resource telemetry:
- H24 minimum observed free memory: `21%`
- H32 minimum observed free memory: `25%`
- H24 peak observed swap: `2076.62 MB`
- H32 peak observed swap: `2124.25 MB`.

Disk free after:
`~35.684 GiB`

## Canonical interpretation

Stretch 021 confirms that persistent transformer residency still improves the exact M5 target path at H32, but the marginal throughput gain has fallen to ~11.45%. The residency curve therefore shows clear diminishing returns relative to the earlier H8->H16 and H16->H24 steps.

The forward-time ratio is now close to unity while materialization and process-read accounting continue to fall sharply. This indicates that the remaining target-path cost is increasingly dominated by actual forward/shared-stage work rather than transformer-layer rematerialization.

Do **not** infer from H32's `25%` minimum free memory versus H24's `21%` that H32 intrinsically uses less memory; these are system-wide observations from different constituent runs and are host-state dependent.

Do **not** compare absolute target-rate values across separate Stretch experiments as causal measurements. Use the balanced within-experiment ratios for decisions.

## Decision

1. Freeze `M=5 + H32` as the best demonstrated target-side profile so far under the frozen MLX 0.31.2 runtime.
2. Run one final preregistered transformer-residency ceiling test at H36.
3. Preserve H32 as the hybrid control; H36 removes transformer streaming entirely while shared stages remain streamed.
4. Keep all numerical/resource/I-O gates unchanged and use balanced order H32 -> H36 -> H36 -> H32.
5. After H36, close the transformer-hotset scaling axis regardless of outcome and choose the next independent speed factor from the residual cost evidence.
