# STREAMED-LAYER-GRADIENT 001 — result

Date: 2026-08-22
Classification: `STREAMED_LAYER_GRADIENT_001_COMPLETE`
Interpretation: `STREAM_LAYER_COST_FIXED_OR_NONLINEAR`

## Result

All four arms completed 2/2 valid runs with exact real-M1 token parity and no resource aborts. Shared stages were persistent in every arm; only the number of streamed transformer layers changed.

| Arm | Streamed layers | Persistent raw B | Logical streamed B/token | Gen tok/s | Wall/token | Peak MLX B |
|---|---:|---:|---:|---:|---:|---:|
| S0 | 0 | 3,583,928,320 | 0 | 14.022271 | 71.315 ms | 3,621,677,296 |
| S1 | 1 | 3,499,501,056 | 84,427,264 | 5.819925 | 171.824 ms | 3,537,250,032 |
| S2 | 2 | 3,415,073,792 | 168,854,528 | 4.755397 | 210.287 ms | 3,452,822,768 |
| S4 | 4 | 3,246,219,264 | 337,709,056 | 3.463355 | 288.737 ms | 3,283,968,240 |

Marginal observed penalties:
- S1 vs S0: +100.508 ms/token for the first streamed layer;
- S2 vs S1: +38.464 ms/token for the second;
- S4 vs S2: +39.225 ms/token per additional layer.

The first streamed layer therefore carries a disproportionate penalty; subsequent layers are very stable at about 38–39 ms/layer.

## Descriptive two-component model

A post-run descriptive fit to the four pooled points using

`wall/token = resident_base + fixed_stream_activation * I(N>0) + marginal_layer_cost * N`

gives approximately:

- resident base: **71.315 ms/token**;
- fixed streaming activation term: **61.284 ms/token** whenever at least one transformer layer is streamed;
- marginal streamed-layer term: **39.007 ms/token/layer**;
- descriptive fit `R² ≈ 0.999993`.

This is not yet an internal causal decomposition. It is a compact system-level model of the measured gradient and motivates source-level inspection of work executed once per token whenever streaming is active.

## Correctness and resources

- S1 parity: PASS
- S2 parity: PASS
- S4 parity: PASS
- all scientific prompt outputs exact versus S0
- resource aborts: none
- physical SSD traffic proven: NO

## Interpretation

The current stream penalty has at least two system-level components:

1. a large activation/fixed component associated with crossing from zero streamed layers to any streamed layer;
2. a repeatable marginal component of about 39 ms/token for each additional 84,427,264-byte transformer layer.

This rules out a simple uniform additive-cost model from zero layers. It also means that eliminating only the fixed component would not solve deep out-of-core execution: at four streamed layers the repeated per-layer component is already the larger share of excess wall time.

The next step is a low-cost source/control-flow audit to identify operations executed once per generated token only when the streamed-layer set is non-empty, before selecting a causal treatment.

Raw local evidence:
`results-local/memory/streamed-layer-gradient-001/20260822-165032/`
