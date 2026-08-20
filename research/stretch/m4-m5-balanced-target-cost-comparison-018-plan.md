# LOOM Stretch 018 — Balanced M4 vs M5 Target-Cost Comparison

Date: 2026-08-20
Status: READY

## Objective

Determine whether the lower raw target-verification rate observed in Stretch 017 at `M=5` is reproducible when `M=4` and `M=5` are exercised under a balanced run order, while separately tracking target block wall time, materialization time, forward time, and Darwin process-read accounting.

This experiment does **not** reopen the correctness frontier:

- Stretch 013 proved end-to-end exactness at `M=4`.
- Stretch 017 proved end-to-end exactness at `M=5`.
- Stretch 016 mapped the first layer-0 MLP numerical divergence at `M=6`.

Therefore the question is now operational/performance attribution:

> Under the frozen MLX 0.31.2 target path, which exact block size, M4 or M5, has the better observed target-side verification cost when host/cache ordering is balanced?

## Frozen sources

M4 source:
- `scripts/stretch_four_token_oracle_block_verification_013.py`
- blob `deeb0339294162f38cd4522d2890b6a0c728f96e`

M5 source:
- `scripts/stretch_five_token_oracle_block_confirmation_017.py`
- blob `6171440736badf5150297f9c8945209fe49d0826`

Stretch 018 runner:
- `scripts/stretch_m4_m5_balanced_target_cost_comparison_018.py`
- blob `0a745a2ea4fd6adf70d33b82156ec9c3889a1498`

## Frozen environment/policy

Each constituent run inherits its already-frozen gates and path:

- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- persistent hotset layers 0..7
- layers 8..35 streamed
- shared stages streamed
- ordinary BF16 KVCache
- resident sequential correctness control
- exact numerical parity and top-1 checks
- existing host-state/resource gates
- Darwin process-I/O attribution
- file-backed child transport
- no tokenizer
- no sampling
- no real drafter
- no KV quantization
- no prefetch
- no runtime upgrade
- no strict-mode patch
- no numerical-threshold relaxation
- no model download
- no deliberate macOS cache purge.

## Experimental design

Balanced order:

`M4 -> M5 -> M5 -> M4`

Each item is a complete invocation of its already-frozen scientific runner.

Rationale:
- the earlier Stretch 013 and 017 measurements were taken in different host/cache states;
- an ABBA order gives both variants one earlier and one later position;
- no attempt is made to manufacture a cold-cache state;
- each inherited runner independently applies its host launch gate and correctness gates.

If any constituent run does not reach its expected scientific PASS classification, Stretch 018 is classified `CONTROLLED_COMPARISON_INCOMPLETE` and no M4-vs-M5 winner is promoted.

Expected constituent PASS classifications:
- M4: `FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`
- M5: `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`

## Important geometry boundary

The inherited workloads are not identical in total continuation length:

- M4 source: 16 accepted oracle tokens, four blocks per run
- M5 source: 15 accepted oracle tokens, three blocks per run.

Therefore Stretch 018 compares normalized target-block metrics and pooled accepted-token target rate, not whole-script elapsed time.

The primary pooled target rate for each variant is:

`sum(accepted oracle tokens across both runs) / sum(target block wall across both runs)`.

This avoids averaging per-run rates with unequal accepted-token counts.

## Required measurements

For M4 and M5 separately, aggregate across both balanced constituent runs:

- pooled target-verification token/s
- mean and median target-block wall seconds
- mean and median layer-materialization seconds/block
- mean and median layer-forward seconds/block
- mean/median full-pass process-read bytes/block
- mean materialization process-read bytes/block
- mean full-pass process-read bytes/accepted token
- mean materialization process-read bytes/accepted token.

Record raw block arrays as well as aggregates.

Derived M5/M4 ratios:

- pooled target-rate ratio
- median target-block wall ratio
- median materialization-time ratio
- median forward-time ratio
- mean full-pass process-read bytes/block ratio
- mean full-pass process-read bytes/accepted-token ratio.

## Scientific completion classification

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`

requires all four constituent runs to reach their own expected scientific PASS classification and provide complete target-block/I-O metrics.

`CONTROLLED_COMPARISON_INCOMPLETE`

is non-comparative: it means at least one constituent run failed or was rejected by its inherited host/correctness/harness gates. Do not infer a winner from a partial ABBA sequence.

## Interpretation rules

1. If M4 retains a materially higher pooled target rate while process-read accounting per block/token is similar between variants, evidence favors a genuine small-M compute/dispatch cost increase at M5.
2. If target-rate differences track large differences in process-read accounting or materialization time, do not attribute the rate gap solely to M.
3. Forward-time differences may still reflect the expected extra row of quantized computation even when I/O is matched.
4. Do not infer forensic SSD reads from Darwin process-read counters.
5. Do not purge caches or weaken the host gate to force all four runs to complete.
6. Do not use Stretch 018 to change the frozen exactness boundary: M5 remains the maximum demonstrated exact block; M4 may separately become the operational speed sweet spot.

## Decision after run

If M4 is robustly faster under balanced conditions:
- freeze M4 as the current operational exact block-size baseline;
- retain M5 as the maximum exactness frontier, not the preferred speed point;
- move to a separate speed axis such as additional residency/hotset or prefetch.

If M5 is equal/faster once I/O is balanced:
- retain M5 as both maximum exact and current preferred oracle target block;
- then move to another speed axis.

If I/O/cache effects remain dominant or inconsistent:
- do not select a block-size winner;
- design a narrower materialization/cache attribution experiment before changing residency/runtime policy.

Any newer-MLX experiment remains a separate preregistered environment change and must not overwrite the frozen 0.31.2 baseline.
