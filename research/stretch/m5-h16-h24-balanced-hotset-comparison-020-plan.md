# LOOM Stretch 020 — M5 H16 vs H24 Balanced Hotset Comparison — Plan

Date: 2026-08-20
Status: READY

## Objective

Measure whether increasing the persistent transformer hotset from 16 layers to 24 layers improves the already-exact M=5 streamed target path under the frozen MLX 0.31.2 baseline.

Stretch 019 established that H16 materially outperforms H8 under balanced host/cache ordering, with the gain dominated by lower materialization and process-read cost.

Stretch 020 asks one question only:

> Does increasing persistent residency from layers 0..15 to layers 0..23 provide another controlled target-rate improvement while preserving every inherited correctness/resource gate?

## Frozen baseline

Preserve:
- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64 artifact
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- exact oracle block size `M=5`
- 15-token frozen oracle continuation
- resident sequential control
- ordinary BF16 KV cache
- streamed non-hotset transformer layers
- streamed shared stages
- exact numerical parity threshold
- top-1 equality checks
- Darwin process-I/O attribution
- file-backed child transport
- inherited launch/runtime safety gates
- no tokenizer
- no sampling
- no real drafter
- no KV quantization
- no prefetch
- no MLX upgrade
- no strict-mode patch
- no threshold relaxation
- no deliberate cache purge
- no new model download.

## Frozen sources

H16 source:
`scripts/stretch_five_token_h16_hotset_variant_019.py`

H16 blob:
`6a0bd001ad7a5a5bf5646b54a302f7fc372e4367`

H24 source:
`scripts/stretch_five_token_h24_hotset_variant_020.py`

H24 blob:
`09363f4ce669a7de7b2f16fe4dfb63519c72eb9f`

Balanced parent:
`scripts/stretch_m5_h16_h24_balanced_hotset_comparison_020.py`

Frozen parent runner blob:
`d2f891462a786f334ceb11bb2e2528e9c2f0203d`

## Scientific factor

Only intended factor:
- H16: persistent transformer layers `0..15`
- H24: persistent transformer layers `0..23`.

Everything else remains inherited and frozen.

Expected persistent raw-weight payloads:
- H16: `16 * 84,427,264 = 1,350,836,224 B`
- H24: `24 * 84,427,264 = 2,026,254,336 B`.

Using the existing largest streamed shared stage of `272,269,312 B`, the nominal H24 hybrid simultaneous raw-weight budget is:
`2,298,523,648 B` (~2.14 GiB).

This is a raw-weight budget, not a prediction of total system memory usage.

## Balanced order

Run:
`H16 -> H24 -> H24 -> H16`.

Rationale:
- reduce first/last host-cache ordering bias;
- do not purge macOS caches;
- require every constituent run to independently pass its inherited host/correctness/resource gates.

Any partial or failed sequence is classified `HOTSET_COMPARISON_INCOMPLETE`. No winner may be inferred from an incomplete ABBA sequence.

## Constituent validity gates

Each run must:
- exit successfully
- classify `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`
- preserve oracle block size `M=5`
- accept all 15 oracle tokens
- preserve exact numerical/top-1 correctness
- expose the exact expected hotset layer IDs
- expose persistent-hotset and hybrid raw-weight accounting
- pass inherited cache/resource/I-O/host gates.

Expected hotset provenance:
- H16: exactly `[0..15]`
- H24: exactly `[0..23]`.

## Primary PASS classification

`M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS`

Requires all four constituent runs to be scientifically usable.

## Primary comparison outputs

For each variant, pool both valid runs and report:
- accepted-token target-verification token/s
- median target-block wall
- median layer-materialization wall
- median layer-forward wall
- mean full-pass process-read bytes/block
- mean materialization process-read bytes/block
- persistent hotset bytes
- hybrid raw-weight budget
- minimum observed free-memory percentage
- peak observed swap.

Report H24/H16 ratios for:
- pooled target rate
- median block wall
- median materialization
- median forward
- mean full-pass process-read bytes/block
- mean materialization process-read bytes/block
- hotset bytes.

## Interpretation

If H24 PASSes and is materially faster:
- freeze H24 as the new preferred demonstrated residency point;
- assess whether one more residency point is safe/useful or whether diminishing returns suggest switching to prefetch/double buffering.

If H24 PASSes but provides little/no target-rate gain:
- freeze the residency curve as showing diminishing returns near H16/H24;
- move to another independent speed axis rather than increasing residency mechanically.

If H24 fails a host/resource/correctness gate:
- preserve the failure as the observed H24 boundary;
- do not weaken gates or retry with hidden rescue changes;
- retain H16 as the preferred demonstrated safe point.

## Non-claims

- This remains oracle target-verification, not deployable speculative decoding throughput.
- No real drafter latency, rejection, rollback, or acceptance-rate cost is represented.
- The ~20 token/s usability promotion target remains unchanged.
- Darwin process-I/O accounting remains diagnostic and host/cache sensitive.
- A PASS does not establish that 24 resident layers are universally safe under unrelated workloads.
