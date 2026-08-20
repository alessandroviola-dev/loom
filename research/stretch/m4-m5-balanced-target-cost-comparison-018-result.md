# LOOM Stretch 018 — Balanced M4 vs M5 Target-Cost Comparison — Result

Date: 2026-08-20
Status: COMPLETE PASS
Classification: `M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`

## Run

Valid run:
`results-local/stretch/m4-m5-balanced-target-cost-comparison-018/20260820-131448`

Runner:
`scripts/stretch_m4_m5_balanced_target_cost_comparison_018.py`

Frozen runner blob:
`0a745a2ea4fd6adf70d33b82156ec9c3889a1498`

Frozen constituents:
- Stretch 013 / M4 blob `deeb0339294162f38cd4522d2890b6a0c728f96e`
- Stretch 017 / M5 blob `6171440736badf5150297f9c8945209fe49d0826`

Balanced order:
`M4 -> M5 -> M5 -> M4`

Deliberate cache purge: NONE.

Each constituent run independently passed its inherited source, host-state, model/runtime, correctness, KV, parity, I/O and resource gates.

## Primary comparison

Pooled target-verification rate:
- M4: `1.6983236855279842 token/s`
- M5: `1.8646802766365072 token/s`
- M5 / M4 ratio: `1.0979534069542256x`
- M5 advantage: approximately `+9.80%`.

Median target-block wall:
- M4: `2.261242 s`
- M5: `2.7130515 s`
- M5 block wall is approximately `1.1998x` M4.

M5 carries 5 accepted oracle tokens per traversal versus 4 for M4, a 25% increase in useful tokens/traversal. The block-wall increase is smaller than the useful-token increase, so pooled target-verification throughput improves.

Observed higher pooled target rate: **M5**.

## Cost attribution

M5 / M4 ratios:
- median materialization time: `2.192652329749104x`
- median forward time: `1.163651646689249x`
- mean full-pass Darwin process-read bytes per block: `1.7289426930941516x`.

These data show that M5 is not free: materialization and process-read accounting become substantially more expensive per block. Nevertheless, the additional token amortization is sufficient to produce a net target-rate gain in the balanced experiment.

## Canonical interpretation

Stretch 017 by itself reported `1.3629385391 token/s` for M5, below the historical Stretch 013 M4 result of `1.8857486198 token/s`. Stretch 017 was explicitly a correctness-boundary confirmation, not a controlled performance A/B, and its process-I/O state differed substantially.

Stretch 018 resolves that ambiguity:

> Under a balanced ABBA comparison with no deliberate cache purge and identical frozen runtime/model/KV/hotset/parity policy, M5 has the higher pooled target-verification rate, by approximately 9.8%.

Therefore the low standalone Stretch 017 rate must not be promoted as evidence that M5 is intrinsically slower than M4.

Combined with Stretch 016/017:
- M5 is the maximum demonstrated exact end-to-end oracle block under frozen MLX 0.31.2 on the Apple M1 / Qwen3-8B 3-bit reference system;
- M5 is also the best measured exact block size among the controlled M4/M5 comparison;
- M>=6 remains outside the exact numerical path under this runtime because the MLP quantized-linear boundary begins at M=6.

## Strategic consequence

Block-size scaling under frozen MLX 0.31.2 is now sufficiently characterized:
- M4 is exact and fast;
- M5 is exact and modestly faster in the controlled comparison;
- M6+ cannot be treated as exact under the current numerical policy.

The next optimization axis should therefore reduce target traversal cost rather than increase block size.

The most direct next factor is transformer residency while retaining M5 unchanged. A balanced H8 vs H16 hotset experiment can test whether doubling persistent transformer layers reduces materialization/I/O enough to improve target rate without violating the 8 GB resource envelope.

## Boundaries / non-claims

- This remains oracle target-side verification: no real drafter, draft latency, acceptance-rate loss, rejection or rollback cost is included.
- Darwin process-read accounting is diagnostic, not forensic per-file SSD tracing.
- The ABBA order reduces simple first/last ordering bias but does not make host cache state perfectly identical.
- Do not extrapolate M5 performance to M>=6 under MLX 0.31.2.
- Do not promote `1.86468 token/s` as deployable speculative-decoding throughput.
- The ~20 token/s interactive promotion target remains unchanged.

Disk free after Stretch 018:
`35.691 GiB`.
