# LOOM Stretch 022 — M5 H32 vs H36 Balanced Hotset Comparison — Preregistered Plan

Status: **READY / PREREGISTERED**

## Question

Does moving from 32 persistent transformer layers to all 36 transformer layers improve the frozen exact `M=5` target-verification path enough to justify full transformer residency on the Apple M1 / 8 GB reference system?

This is the final planned transformer-hotset ceiling experiment for the frozen MLX 0.31.2 architecture.

## Frozen environment

- Model: Qwen3-8B 3-bit / group64
- 36 transformer layers
- Apple M1 / 8 GB
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- ordinary BF16 KV cache
- exact parity/top-1 policy
- oracle block size `M=5`
- 15 frozen oracle continuation tokens
- 3 target traversals x 5 tokens
- shared embedding/final norm/LM head remain streamed as inherited
- inherited host/resource/I-O gates
- no tokenizer, sampling, real drafter, KV quantization, prefetch, runtime upgrade, download, or deliberate cache purge.

## Frozen sources

H32 helper:
- `scripts/stretch_five_token_h32_hotset_variant_021.py`
- blob `b6b39dfb095b905ed659d52903309783efc02be7`

H36 helper:
- `scripts/stretch_five_token_h36_hotset_variant_022.py`
- blob `9111dde483206a774a9fe5426522dab6e77cecca`

Balanced runner:
- `scripts/stretch_m5_h32_h36_balanced_hotset_comparison_022.py`
- blob `c9ed18984896835c99a22c68aaedb330d030ec7e`

## Scientific factor

Only one intended factor changes:

- H32: persistent transformer layers `0..31`
- H36: persistent transformer layers `0..35`

Everything else is frozen.

H36 therefore eliminates transformer-layer streaming entirely. Shared stages remain handled exactly as in the inherited M5 path.

## Residency budgets

Each transformer layer payload:
`84,427,264 B`

Expected H32 hotset:
`2,701,672,448 B`

Expected H36 hotset:
`3,039,381,504 B`

If the largest newly materialized shared stage remains `272,269,312 B`, nominal hybrid raw-weight budgets are:

- H32: `2,973,941,760 B` (~2.77 GiB)
- H36: `3,311,650,816 B` (~3.08 GiB)

These are raw-weight accounting values, not total system RAM usage. System-wide memory/swap gates remain decisive.

## Balanced design

Frozen order:

`H32 -> H36 -> H36 -> H32`

No deliberate cache purge.

Each constituent run must independently:
- return code 0
- reach inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`
- expose exactly the expected hotset layer IDs
- preserve oracle block size `M=5`
- accept all 15 frozen oracle tokens
- expose hotset and hybrid residency accounting
- pass all inherited numerical, KV, I/O, host-state and runtime safety gates.

Any unusable constituent yields:
`HOTSET_COMPARISON_INCOMPLETE`

No winner is inferred from a partial run sequence. No automatic retry or gate relaxation is permitted.

## Primary PASS

`M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`

## Primary measurements

For H32 and H36 separately:
- pooled accepted-token target-verification token/s
- median full target-block wall
- median transformer materialization wall
- median forward wall
- mean process-read bytes per block
- materialization process-read bytes per block
- persistent hotset bytes
- hybrid raw-weight budget
- minimum observed free memory
- peak observed swap.

Primary ratios:
- H36/H32 pooled target-rate ratio
- H36/H32 block-wall ratio
- H36/H32 materialization ratio
- H36/H32 forward ratio
- H36/H32 process-read ratio.

## Interpretation policy

Use only the balanced within-experiment H36/H32 ratios for causal performance conclusions. Do not compare absolute rates from Stretch 019, 020, 021, and 022 as if they were controlled across experiments.

If H36 materially improves target rate while preserving all gates:
- freeze H36 as the transformer-residency ceiling profile;
- close the transformer-hotset scaling axis;
- attribute the remaining wall primarily using forward/shared-stage evidence before choosing the next factor.

If H36 is flat/slower or resource-limited:
- retain H32 as the preferred transformer-residency profile;
- close the transformer-hotset scaling axis;
- do not weaken resource gates or search intermediate H33-H35 points post-hoc.

Regardless of outcome, Stretch 022 ends the planned transformer-hotset sweep. The next experiment must change a different scientific factor, likely shared-stage residency/prefetch or another separately preregistered runtime/kernel axis.

## Non-claims

This remains an oracle target-verification upper bound. It does not include:
- real draft-model latency
- acceptance-rate losses
- rejection/rollback cost
- tokenizer/sampling overhead
- user-facing end-to-end generation speed.
