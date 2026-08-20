# LOOM Stretch 023 — M5/H36 Shared-Stage Persistence — Preregistered Plan

Status: **READY / NOT YET RUN**

## Question

With the exact M=5 oracle target and all 36 transformer layers already persistent, does also retaining the three remaining shared weight stages improve steady-state target-verification cost enough to justify full-model raw-weight persistence?

## Scientific factor

One factor only:

- control `STREAMED`: H36 transformer hotset remains persistent, while embedding, final RMSNorm and LM head are reconstructed/materialized on every streamed prompt/target pass;
- treatment `PERSISTENT`: the same three shared weight stages are materialized once after the H36 transformer hotset and retained for all subsequent streamed passes.

Everything else is frozen.

## Frozen sources

Control H36 helper:
- `scripts/stretch_five_token_h36_hotset_variant_022.py`
- blob `9111dde483206a774a9fe5426522dab6e77cecca`.

Treatment helper:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py`
- blob `8c263e7be15441581e481e6f41cbd16f87d4df4b`.

Balanced comparison runner:
- `scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023.py`
- blob `b8d69c218ee251662fc54a809ca6bf13a4a4e4da`.

## Frozen environment / workload

- Apple M1 / 8 GB reference machine
- Qwen3-8B 3-bit/group64
- `mlx 0.31.2`
- `mlx-lm 0.31.3`
- `transformers 5.12.1`
- exact oracle block size `M=5`
- three 5-token target blocks / 15 accepted oracle tokens per constituent run
- transformer hotset H36 = layers `0..35`
- ordinary BF16 KV cache
- resident sequential control and exact position-logit/top-1 gates
- inherited host launch/runtime abort gates
- inherited Darwin process-I/O instrumentation
- no tokenizer/sampling/drafter/KV quantization/prefetch/runtime upgrade
- no deliberate macOS cache purge
- no network/model download.

## Shared raw-weight geometry

- embedding: `272,269,312 B`
- final RMSNorm: `8,192 B`
- LM head: `272,269,312 B`
- total shared persistent payload: `544,546,816 B`.

Transformer H36 hotset:
`3,039,381,504 B`.

Full raw model payload if all shared stages are persistent:
`3,583,928,320 B` (~3.34 GiB).

The existing H36 streamed-shared hybrid maximum was `3,311,650,816 B`, so the nominal raw-weight increase to full persistence is about `272,277,504 B`; actual system memory remains governed by observed telemetry and inherited gates rather than raw-weight arithmetic alone.

## Balanced order

`STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`

No automatic retry. No cache purge between runs.

Every constituent run independently executes the inherited H36/M5 correctness and host/resource gates.

## Required treatment provenance

The PERSISTENT variant must demonstrate:

- exact H36 transformer IDs `0..35`;
- one-time persistent shared stage names exactly `[embedding, norm, head]`;
- expected shared payload `544,546,816 B`;
- full persistent raw-weight payload within the frozen active-memory tolerance around `3,583,928,320 B`;
- each target pass marks all three shared stages persistent and shows no stage-sized rematerialization;
- inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`;
- all 15 oracle tokens accepted at M=5.

The STREAMED control must remain the unchanged frozen Stretch 022 H36 helper and must not expose shared/full-weight persistence records.

## Primary comparison

Steady-state target verification rate:

`total accepted oracle tokens / total target-block wall seconds`

pooled separately over the two STREAMED and two PERSISTENT constituent runs.

The treatment's one-time shared setup occurs before measured prompt/target passes and is **not** included in this steady-state target rate. It is measured separately rather than hidden.

## Secondary attribution

For target blocks compare:

- median/mean full-pass wall;
- transformer materialization wall;
- transformer forward wall;
- summed shared-stage materialization wall for embedding + norm + head;
- summed shared-stage forward wall;
- full-pass Darwin process-read bytes/block;
- shared-stage materialization process-read bytes/block;
- persistent raw-weight bytes;
- minimum observed free memory;
- peak observed swap.

For PERSISTENT additionally record:

- one-time shared setup wall;
- one-time setup I/O record;
- estimated setup break-even in target blocks when steady-state block wall improves.

Process-read accounting remains diagnostic and is not treated as forensic physical SSD attribution.

## Success classification

If all four constituent runs pass all inherited and new provenance gates:

`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`

If any constituent run fails/rejects/is host-state-ineligible or shared-persistence provenance is invalid:

`SHARED_STAGE_COMPARISON_INCOMPLETE`

Stop immediately; no winner is inferred from partial data and no gate is weakened post-hoc.

## Interpretation policy

1. If PERSISTENT gives a meaningful higher pooled steady-state target rate and the gain tracks lower shared-stage materialization/process reads, full-weight persistence becomes the preferred frozen target architecture.
2. The one-time setup cost must be reported separately; a steady-state gain is not automatically an end-to-end win for very short sessions.
3. If the steady-state gain is small/flat while shared rematerialization disappears, the remaining bottleneck is compute/kernel/runtime rather than weight residency.
4. If PERSISTENT is resource-limited, do not search post-hoc partial shared subsets under this preregistration; design a new factor separately if justified.
5. Stretch 023 does not change the M=5 exactness frontier and does not introduce a real drafter.

## Next decision

Stretch 023 is intended to close the raw-weight residency axis. After this result, move to a different independent speed factor (compute/kernel/runtime/prefetch where still applicable) or begin real speculative-drafter integration; do not continue ad-hoc residency variants.
