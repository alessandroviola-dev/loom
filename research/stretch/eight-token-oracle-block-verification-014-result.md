# LOOM Stretch 014 — Eight-Token Oracle Block Verification Result

Date: 2026-08-20
Run: `20260820-122922`
Classification: **ORACLE_BLOCK_NUMERICAL_PARITY_FAIL**
Scientific result: **VALID FAIL**

## Frozen baseline

Plan:
`research/stretch/eight-token-oracle-block-verification-014-plan.md`

Runner:
`scripts/stretch_eight_token_oracle_block_verification_014.py`

Frozen runner blob:
`6d7afd43969e752a7cce39ae474d7054ccc7edd8`

Frozen Stretch 013 source blob:
`deeb0339294162f38cd4522d2890b6a0c728f96e`

Run directory:
`results-local/stretch/eight-token-oracle-block-verification-014/20260820-122922`

## Launch / provenance

The run passed all launch and provenance gates:

- source provenance: PASS
- frozen transform: PASS
- MLX / mlx-lm / transformers version lock: PASS (`0.31.2` / `0.31.3` / `5.12.1`)
- Qwen3-8B 3-bit/group64 config and quantization: PASS
- transformer-layer provenance: 36/36 PASS
- host samples: 63%, 64%, 65% free memory
- launch swap: 727.19 MB
- host-state gate: PASS.

This run supersedes the earlier `HOST_STATE_NOT_READY` launch attempt as the first scientific Stretch 014 result. The earlier launch rejection remains a preflight-only event with no scientific result.

## Correctness result

Prompt parity remained exact:

- prompt max abs diff: `0.0`
- prompt mean abs diff: `0.0`
- prompt token equality: PASS.

The first 8-token target block immediately lost numerical parity versus the resident sequential control:

- step 1 max abs diff: `0.34375`
- step 1 mean abs diff: `0.05856526270508766`
- step 1 resident top-1: `374`
- step 1 streamed top-1: `374`
- numerical threshold: `0.0002375`
- step 1 numerical parity: FAIL.

All 16 target positions failed the preregistered numerical-parity gate. Max absolute differences by step were:

`[0.34375, 0.375, 0.365234375, 0.3125, 0.296875, 0.375, 0.28125, 0.375, 0.4375, 0.5390625, 0.84375, 0.84375, 0.78125, 0.5, 0.4375, 0.5]`

Top-1 equality remained true through steps 1–15 and became false at step 16.

The frozen oracle input sequence was:

`[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`.

The reported streamed generated sequence is also this sequence because Stretch 014 deliberately feeds the frozen oracle tokens. Therefore sequence equality is not evidence of numerical parity; the position-level logits/top-1 gates are decisive.

## KV / memory state

State remained structurally correct despite the numerical failure:

- resident final KV offset: 20
- streamed final KV offset: 20
- resident KV bytes: 37,748,736 B
- streamed KV bytes: 37,748,736 B
- persistent hotset: 675,418,112 B
- resident full-model materialized delta: 3,583,928,320 B
- max newly materialized streamed stage: 272,269,312 B
- resident/max-stage ratio: 13.16317396798652x.

Resource observations:

- whole-run minimum free memory: 17%
- stream-block minimum free memory: 56%
- peak swap: 1544.38 MB
- peak child RSS: 980.734 MB
- disk free after: 36.706 GiB.

No runtime resource gate caused the scientific failure.

## Interpretation boundary

Canonical result:

> Doubling the oracle target block from 4 to 8 tokens does not preserve the exact resident sequential numerical behavior under the frozen MLX 0.31.2 / mlx-lm 0.31.3 Qwen3-8B 3-bit setup. The divergence begins at the first position of the first 8-token block and eventually changes a top-1 prediction at position 16.

This result does **not** yet identify the root cause.

Current root-cause candidates include:

- shape-dependent quantized linear / `quantized_matmul` execution at `M=8`;
- attention / causal-block execution differences;
- another block-internal shape-dependent numerical path.

Do not:

- weaken the numerical threshold post hoc;
- relabel Stretch 014 as PASS because the oracle token sequence is identical;
- proceed directly to a 16-token oracle block before attribution;
- upgrade MLX inside the attribution experiment.

## Decision

Freeze Stretch 014 as `ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`.

Next experiment: **Stretch 015 — Eight-Token Divergence Attribution**. Preserve the frozen model/runtime and directly compare `M=1`, `M=4`, and `M=8` at quantized projection and layer-internal checkpoints to identify the earliest shape-dependent divergence before any further block-size scaling or real-drafter work.
