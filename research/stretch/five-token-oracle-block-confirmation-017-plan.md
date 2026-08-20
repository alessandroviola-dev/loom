# LOOM Stretch 017 — Five-Token Oracle Block Confirmation

Date: 2026-08-20
Status: READY

## Objective

Confirm end-to-end whether the maximum exact small-M candidate discovered by Stretch 016 (`M=5`) remains numerically exact across the complete frozen streamed/hotset Qwen3-8B target path.

Stretch 016 established on the actual frozen layer-0 quantized linears:

- q/k/v/o exact through M=9, first divergent M=10
- gate/up/down exact through M=5, first divergent M=6
- therefore MLP imposes the first known exactness boundary.

This experiment asks only:

> Can three causal 5-token oracle target blocks reproduce fifteen sequential resident target positions exactly under the unchanged Stretch 013 runtime/model/KV/hotset policy?

## Frozen baseline

Preserve:

- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64 artifact
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- Stretch 013 eight-layer hotset 0..7
- streamed layers 8..35
- streamed shared stages
- resident sequential control
- ordinary BF16 KVCache
- exact position-level numerical parity threshold
- top-1 equality checks
- Darwin I/O attribution
- host/runtime safety gates
- file-backed child transport
- no tokenizer
- no sampling
- no real drafter
- no KV quantization
- no prefetch
- no MLX upgrade
- no strict-mode patch
- no threshold relaxation
- no download.

Frozen Stretch 013 source blob:
`deeb0339294162f38cd4522d2890b6a0c728f96e`.

Stretch 016 result:
`research/stretch/quantized-linear-m-boundary-mapping-016-result.md`.

## Diagnostic workload

Use the first fifteen tokens of the already frozen resident/oracle sequence:

`[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8]`

Resident control:
- greedy sequential generation for 15 feedback positions.

Streamed oracle target:
- 3 target traversals
- 5 known-correct oracle tokens per traversal
- expected streamed KV offsets: `4 -> 9 -> 14 -> 19`.

## Scientific changes vs Stretch 013

This is a boundary-confirmation experiment, not a single-factor performance comparison.

Necessary diagnostic changes:

1. oracle block size `4 -> 5`
2. oracle block count `4 -> 3`
3. continuation length `16 -> 15` so every streamed verification traversal is exactly M=5
4. oracle sequence is the frozen first-15 prefix of the prior 16-token sequence.

All model/runtime/KV/hotset/parity/safety policies remain unchanged.

Because continuation length differs from Stretch 013, do not claim a pure causal throughput speedup from the total-run rate alone. Per-block/per-accepted-token timing is retained as secondary characterization.

## PASS gates

Primary PASS classification:

`FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`

Requires:

- prompt numerical parity exact under inherited gate
- frozen 15-token resident sequence provenance
- all 15 oracle tokens accepted
- exactly 15 position-level parity records
- every position passes unchanged numerical threshold
- top-1 equality at every position
- resident sequential KV offsets reach 19
- streamed KV offsets exactly `4 -> 9 -> 14 -> 19`
- KV allocation remains within inherited boundary
- all I/O/resource/safety gates pass.

Failure classifications remain inherited where applicable, including numerical parity, top-1, cache-state, telemetry, resource and host-state failures.

## Interpretation

If PASS:
- freeze M=5 as the maximum end-to-end exact oracle block demonstrated under MLX 0.31.2 on the reference M1/3-bit system.
- do not attempt M>=6 under the same runtime as an exact-parity path unless testing a deliberately different numerical policy.
- decide next between another speed axis and a separately preregistered newer-runtime experiment.

If FAIL:
- layer-0 M=5 exactness is insufficient to guarantee full-model M=5 exactness.
- localize the earliest full-model/layer divergence before any runtime change.

## Non-claims

- This is still an oracle upper bound; no draft-model latency, rejection, rollback or acceptance-rate cost is included.
- A PASS does not mean a deployable speculative decoder reaches the measured rate.
- A PASS does not revise the ~20 token/s usability promotion target.
