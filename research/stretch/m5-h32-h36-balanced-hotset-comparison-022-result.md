# LOOM Stretch 022 — M5 H32 vs H36 Balanced Hotset Comparison — Result

Status: **COMPLETE PASS**

Classification:
`M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`

Valid run:
`20260820-145851`

Run directory:
`results-local/stretch/m5-h32-h36-balanced-hotset-comparison-022/20260820-145851`

Summary:
`results-local/stretch/m5-h32-h36-balanced-hotset-comparison-022/20260820-145851/summary.json`

## Frozen provenance

H32 helper:
- `scripts/stretch_five_token_h32_hotset_variant_021.py`
- blob `b6b39dfb095b905ed659d52903309783efc02be7`

H36 helper:
- `scripts/stretch_five_token_h36_hotset_variant_022.py`
- blob `9111dde483206a774a9fe5426522dab6e77cecca`

Balanced runner:
- `scripts/stretch_m5_h32_h36_balanced_hotset_comparison_022.py`
- blob `c9ed18984896835c99a22c68aaedb330d030ec7e`

Frozen target geometry/policy:
- exact oracle block `M=5`
- balanced order `H32 -> H36 -> H36 -> H32`
- Qwen3-8B 3-bit/group64
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- ordinary BF16 KV
- exact numerical/top-1 gates
- inherited host/resource/I-O policy
- no deliberate cache purge.

Scientific factor only:
- persistent transformer residency `32 -> 36` layers.

## Controlled result

All four constituent runs passed their inherited scientific and provenance gates.

Target verification:
- H32 pooled rate: `2.763691141669756 token/s`
- H36 pooled rate: `3.0539262293580034 token/s`
- H36/H32 rate ratio: `1.105017193604671x`
- controlled improvement: **~10.50%**.

Target block wall:
- H32 median: `1.722024 s`
- H36 median: `1.5799655 s`
- reduction: **~8.25%**.

Attribution:
- H36/H32 median transformer-materialization ratio: `0.037393043671519056x` (~96.26% lower)
- H36/H32 median transformer-forward ratio: `0.9246821007589214x` (~7.53% lower)
- H36/H32 mean full-pass process-read bytes/block ratio: `0.08764572674662417x` (~91.24% lower).

Residency:
- H32 persistent transformer hotset: `2,701,672,448 B`
- H36 persistent transformer hotset: `3,039,381,504 B`
- H32 hybrid raw-weight budget: `2,973,941,760 B`
- H36 hybrid raw-weight budget: `3,311,650,816 B`.

Resource telemetry:
- H32 minimum observed free memory: `15%`
- H36 minimum observed free memory: `25%`
- H32 peak observed swap: `1992.44 MB`
- H36 peak observed swap: `2040.5 MB`.

Disk free after:
`~35.673 GiB`

## Canonical interpretation

H36 is the transformer-residency ceiling: all 36 transformer layers are persistent and only shared stages remain streamed. H36 improves the controlled M5 target-verification rate by ~10.50% versus H32 while preserving every inherited correctness/resource gate.

The residency curve now shows diminishing controlled gains:
- H8 -> H16: ~+56.87%
- H16 -> H24: ~+34.86%
- H24 -> H32: ~+11.45%
- H32 -> H36: ~+10.50%.

The transformer-materialization reduction is ~96.26%, while transformer-forward time changes far less. After H36, transformer weight traversal is no longer an available optimization axis; remaining steady-state cost is dominated by compute plus the still-streamed shared stages.

Do **not** infer from H36's higher observed minimum-free percentage that H36 intrinsically uses less RAM than H32. System-wide memory observations are host-state dependent; causal performance decisions use the balanced within-experiment comparison.

Do **not** compare absolute token/s values across separate Stretch experiments as causal measurements.

## Decision

1. Freeze `M=5 + H36` as the best demonstrated transformer-resident target profile under the frozen runtime.
2. Close transformer-residency scaling permanently: H36 is the physical ceiling and no H33–H35 rescue search is allowed.
3. The next independent factor may test persistence of the remaining shared weight stages: embedding, final RMSNorm, and LM head.
4. Shared-stage persistence must be preregistered separately and preserve M=5, H36, model/runtime/KV/parity/safety/I-O policy.
5. If full-weight persistence yields only a small gain, move away from residency toward compute/kernel/runtime or real speculative-drafting work.
