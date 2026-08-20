# LOOM Stretch 017 — Five-Token Oracle Block Confirmation — Result

Date: 2026-08-20
Status: COMPLETE PASS
Classification: `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`

## Run

Valid run:
`results-local/stretch/five-token-oracle-block-confirmation-017/20260820-130124`

Summary:
`results-local/stretch/five-token-oracle-block-confirmation-017/20260820-130124/summary.json`

Runner:
`scripts/stretch_five_token_oracle_block_confirmation_017.py`

Frozen runner blob:
`6171440736badf5150297f9c8945209fe49d0826`

Frozen source:
- Stretch 013 blob `deeb0339294162f38cd4522d2890b6a0c728f96e`

## Frozen environment

- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- eight-layer persistent hotset, layers 0..7
- streamed layers 8..35
- ordinary BF16 KVCache
- resident sequential control
- unchanged numerical parity/top-1/resource/I-O policy
- no real drafter
- no MLX upgrade
- no strict-mode patch
- no threshold relaxation
- no download

All source, reconstruction, model/config, quantization and 36-layer provenance gates passed.

Host launch gate passed:
- sample 1: 70% free, 1088.62 MB swap
- sample 2: 70% free, 1088.62 MB swap
- sample 3: 71% free, 1088.62 MB swap

## Correctness result

Diagnostic geometry:
- resident continuation: 15 frozen-prefix positions
- streamed target: 3 x 5-token oracle blocks
- oracle sequence: `[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8]`

Correctness:
- prompt max/mean logit diff `0.0 / 0.0`
- prompt token equality: true
- all 15 position-level max/mean logit diffs `0.0 / 0.0`
- top-1 equality at all 15 positions
- all 15 oracle tokens accepted
- resident/streamed frozen sequence equal
- final resident KV offset 19
- final streamed KV offset 19
- final resident/streamed KV bytes `37,748,736 / 37,748,736 B`

Canonical correctness conclusion:

> `M=5` is now demonstrated exact end-to-end across the complete frozen 36-layer streamed/hotset target path under MLX 0.31.2 on the Apple M1 / Qwen3-8B 3-bit reference system.

Combined with Stretch 016, `M=5` is the maximum currently demonstrated exact oracle block size under the frozen runtime; layer-0 MLP projections first diverge at `M=6`.

## Weight residency

- resident full-model materialized delta: `3,583,928,320 B`
- max newly streamed weight-stage delta: `272,269,312 B`
- resident/max newly-materialized-stage ratio: `13.16317396798652x`
- persistent hotset materialized delta: `675,418,112 B`
- hybrid max simultaneous raw-weight budget: `947,687,424 B`
- resident/hybrid raw-weight ratio: `3.7817620338074676x`

## Secondary performance characterization

These timings are valid observations from Stretch 017 but are **not** a pure A/B comparison against Stretch 013 because continuation geometry differs (15 positions / 3x5 vs 16 positions / 4x4) and host/cache state was not paired.

Observed M=5 target blocks:
- full-pass walls: `[3.718927, 3.659837, 3.626868] s`
- mean full target block pass: `3.668544 s`
- median full target block pass: `3.659837 s`
- materialization walls: `[1.137753, 1.118737, 1.074513] s`
- forward walls: `[0.513579, 0.685394, 0.661975] s`
- accepted tokens/target traversal: `5.0`
- total target-block wall: `11.005632 s`
- wall/accepted token: `0.7337088 s`
- oracle target-verification throughput: `1.3629385391043423 token/s`
- ratio vs Stretch 012: `2.8517594435666016x`

For reference only, Stretch 013 M=4 observed `1.8857486198 token/s`. The raw cross-run ratio is therefore about `0.7227x` (M=5 slower), but this must not be promoted as a causal M4-vs-M5 result without a controlled comparison.

## I/O characterization

Darwin process-read accounting:
- materialize bytes/block: `[2366193664, 2365849600, 2365849600]`
- full-pass bytes/block: `[2910916608, 2910502912, 2910621696]`
- mean full-pass bytes/accepted token: `582136081.0666667 B`

This is much larger than the favorable process-read accounting observed in Stretch 013. Therefore the M=5 timing cannot be attributed solely to quantized-compute shape cost from this run.

Interpretation boundary:
- process-read accounting is diagnostic, not forensic per-file SSD tracing
- no macOS cache purge was performed
- host/page-cache state may materially affect observed traversal timing
- Stretch 017 was designed first for correctness confirmation, not paired performance attribution.

## Resource

- minimum observed free memory: 16%
- peak observed swap: 1731.56 MB
- peak child RSS: 881.984 MB
- stream-block minimum free memory: 49%
- disk free before: 36.697 GiB
- disk free after: 35.696 GiB

No resource guardrail failed.

## Decision

1. Freeze `M=5` as the maximum demonstrated exact oracle block under the frozen MLX 0.31.2 baseline.
2. Do not treat `M>=6` as an exact-parity path under this runtime.
3. Do not conclude from the unpaired Stretch 013/017 rates alone that M=4 is intrinsically faster than M=5.
4. Run a balanced controlled M4-vs-M5 performance/I-O comparison before choosing the operational block-size sweet spot.
5. Keep any runtime upgrade, residency expansion, prefetch, KV quantization or real-drafter work as separate scientific factors.
