# Stretch 028 — SINGLE_PASS Compute Re-Attribution — RESULT

Date: 2026-08-20
Run: `20260820-164802`
Classification: `SINGLE_PASS_COMPUTE_REATTRIBUTION_PASS`

## Frozen architecture

- Qwen3-8B 3-bit/group64
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- M=5 exact oracle target block
- H36 transformer residency
- full raw-weight persistence
- one final cleanup per pass (Stretch 027 SINGLE_PASS baseline)
- ordinary BF16 KV

CONTROL blob: `6636456df5a773ac6062fdad66b7dc96abe8bd81`
PROFILED blob: `0858e39a46bf09fe7750691b6dcd95b6753e5c70`
Runner blob: `65d1c93967ed786623a3899e0f510ad9ef8de1e2`

Balanced order:
`CONTROL -> PROFILED -> PROFILED -> CONTROL`

PROFILED adds explicit `mx.eval` component boundaries only. Its throughput is instrumentation perturbation telemetry, not an optimization result.

## Balanced perturbation telemetry

- CONTROL pooled target-verification rate: `12.707685947332573 token/s`
- PROFILED pooled target-verification rate: `8.706180343302105 token/s`
- PROFILED/CONTROL: `0.6851113868713122x`
- CONTROL median block wall: `0.394962 s`
- PROFILED median block wall: `0.609049 s`

Instrumentation therefore perturbed throughput materially (~31.49% lower). Component ranking/share, not PROFILED absolute speed, is the scientific output.

## Compute attribution

Mean synchronized transformer compute per target block:
`0.44969600122810033 s`

Attention path:
`0.1231006117692838 s/block`

MLP path:
`0.3265953894588165 s/block`

MLP/attention ratio:
`2.653076899982628x`

Mean components per target block:

- up_proj: `0.09931493003387004 s` (~22.08% of profiled transformer compute)
- attention: `0.09857969474978745 s` (~21.92%)
- gate_proj: `0.0965807989705354 s` (~21.48%)
- down_proj: `0.09428692991302039 s` (~20.97%)
- SwiGLU: `0.013753473293036222 s`
- input RMSNorm: `0.01251025051654627 s`
- residual 2: `0.01232073619030416 s`
- residual 1: `0.012010666502950093 s`
- post-attention RMSNorm: `0.010338521058050295 s`

The three large MLP quantized projections (`gate_proj + up_proj + down_proj`) sum to approximately `0.290182659 s/block` in the synchronized PROFILED path.

Other target wall:
- final cleanup: `0.0617505 s/block`
- shared forward: `0.028035333333333332 s/block`
- residual unattributed: `0.034740665438566354 s/block`
- accounted share: `0.9395083002891038` (~93.95%)

## Slowest layer candidates

Highest mean profiled compute layers:
35, 33, 34, 32, 25, 31, 27, 28.

This is diagnostic only; no layer-specific optimization search is authorized from this ranking.

## Resources

- CONTROL min free memory: `17%`
- PROFILED min free memory: `23%`
- CONTROL peak swap: `2678.75 MB`
- PROFILED peak swap: `2691.75 MB`
- disk free after: `35.674 GiB`

All inherited correctness, KV, residency, and resource gates passed.

## Decision

Stretch 028 confirms that after cleanup consolidation the dominant remaining target-side category is true transformer compute.

Within compute, MLP remains ~`2.653x` attention because it contains three large quantized projections. Individually, `up_proj`, attention, `gate_proj`, and `down_proj` are all near the same ~0.095–0.099 s/block scale.

The next causal optimization axis is therefore the quantized MLP projection path. Stretch 029 will test one factor only: fusing `gate_proj` and `up_proj` into one 3-bit/group64 `mx.quantized_matmul`, while preserving the same raw quantized payload and all exactness/resource gates.

If the first FUSED constituent fails frozen numerical parity, Stretch 029 stops and records a valid scientific fusion-parity FAIL; no rescue variant is allowed.
