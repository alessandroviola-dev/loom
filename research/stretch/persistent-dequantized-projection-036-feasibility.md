# Stretch 036 — persistent dequantized BF16 projection feasibility

Date: 2026-08-20
Status: **NO-GO — diagnostic only; no Stretch-036 scientific plan or full-model ABBA was created.**

## Scope and frozen conditions

This isolated layer-0 study tested whether a canonical real affine 3-bit/group64 projection can be replaced by a persistent BF16 dense weight without changing the intended mathematical weight source.

- Qwen3-8B 3-bit affine/group64 checkpoint SHA-256: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`.
- Literal canonical child launcher; child `sys.prefix` matched the canonical venv. mlx/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`.
- Apple M1 / 8 GB; M5; BF16 inputs; H36/full raw-weight persistence/one final cleanup/BF16 KV remain frozen canonical conditions.
- Only the 21 real layer-0 projection tensors were materialized (`84,410,368 B` active setup memory). No model module, original FP16/BF16 weights, requantization, changed scales/biases, global MLX change, full-model cache, or full-model ABBA was used.
- For every treatment weight, and only for that path:

```python
W = mx.dequantize(packed_weight, scales, biases, group_size=64, bits=3)
# materialize; retain W as BF16
```

The actual packed tensors are U32 and the actual affine scales/biases are BF16. `W` was confirmed BF16 and shape `[N, K]`. No deliberate cache purge occurred. A real intermediate model activation was not recovered because its production requires an additional transformer traversal outside this projection-only feasibility scope; three deterministic BF16 inputs were instead used per K.

## A. Exact layer-0 memory accounting

All byte counts are measured from the actual loaded tensors. `BOTH incremental` is the conservative primary case: quantized payload and new BF16 cache both remain resident. `Discard-source net` is explicitly hypothetical and is **not** assumed available in the runtime.

| projection | K → N | packed B | scales B | biases B | canonical quant B | persistent BF16 B | BOTH incremental B | hypothetical discard-source net B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| q_proj | 4096 → 4096 | 6,291,456 | 524,288 | 524,288 | 7,340,032 | 33,554,432 | 33,554,432 | 26,214,400 |
| k_proj | 4096 → 1024 | 1,572,864 | 131,072 | 131,072 | 1,835,008 | 8,388,608 | 8,388,608 | 6,553,600 |
| v_proj | 4096 → 1024 | 1,572,864 | 131,072 | 131,072 | 1,835,008 | 8,388,608 | 8,388,608 | 6,553,600 |
| o_proj | 4096 → 4096 | 6,291,456 | 524,288 | 524,288 | 7,340,032 | 33,554,432 | 33,554,432 | 26,214,400 |
| gate_proj | 4096 → 12288 | 18,874,368 | 1,572,864 | 1,572,864 | 22,020,096 | 100,663,296 | 100,663,296 | 78,643,200 |
| up_proj | 4096 → 12288 | 18,874,368 | 1,572,864 | 1,572,864 | 22,020,096 | 100,663,296 | 100,663,296 | 78,643,200 |
| down_proj | 12288 → 4096 | 18,874,368 | 1,572,864 | 1,572,864 | 22,020,096 | 100,663,296 | 100,663,296 | 78,643,200 |

### x36 layer projection table

| cache candidate | canonical quantized source MiB x36 | persistent BF16 MiB x36 | BOTH incremental MiB x36 | hypothetical discard-source net MiB x36 |
|---|---:|---:|---:|---:|
| Q only | 252 | 1,152 | 1,152 | 900 |
| K only | 63 | 288 | 288 | 225 |
| V only | 63 | 288 | 288 | 225 |
| O only | 252 | 1,152 | 1,152 | 900 |
| K+V | 126 | 576 | 576 | 450 |
| Q+O | 504 | 2,304 | 2,304 | 1,800 |
| gate only | 756 | 3,456 | 3,456 | 2,700 |
| up only | 756 | 3,456 | 3,456 | 2,700 |
| down only | 756 | 3,456 | 3,456 | 2,700 |

The MLP classes were measured rather than discarded a priori. Their single-class 3,456 MiB conservative cache is already incompatible with the M1/8 GB operating envelope.

## B. One-time dequantization and materialization

`dequantize call` is graph construction wall time; `mx.eval` is the separate materialization wall time. The active-memory delta and peak are diagnostic MLX active allocations while all seven real layer-0 source payloads remained resident.

| projection | dequantize call ms | eval/materialize ms | total ms | active delta B | peak B | resulting dtype / shape |
|---|---:|---:|---:|---:|---:|---|
| q_proj | 0.4564 | 3.6975 | 4.1540 | 33,062,820 | 118,751,248 | BF16 `[4096,4096]` |
| k_proj | 0.0305 | 3.0457 | 3.0763 | 8,388,608 | 93,634,576 | BF16 `[1024,4096]` |
| v_proj | 0.0316 | 1.5840 | 1.6157 | 8,388,608 | 93,595,664 | BF16 `[1024,4096]` |
| o_proj | 0.0266 | 3.0926 | 3.1192 | 33,554,432 | 118,761,488 | BF16 `[4096,4096]` |
| gate_proj | 0.0257 | 34.4060 | 34.4317 | 100,663,296 | 185,909,264 | BF16 `[12288,4096]` |
| up_proj | 0.0304 | 5.4714 | 5.5018 | 100,663,296 | 185,991,184 | BF16 `[12288,4096]` |
| down_proj | 0.0339 | 4.8933 | 4.9273 | 100,663,296 | 185,991,184 | BF16 `[4096,12288]` |

No timing region dequantized a weight. No 36-layer BF16 cache was persisted during this feasibility run.

## C. Numerical validation

For each deterministic BF16 input, CONTROL was the canonical:

```python
y_q = mx.quantized_matmul(x, packed, scales, biases,
                          transpose=True, group_size=64, bits=3)
```

and TREATMENT was `y_d = x @ W.T`. All output shapes matched and both outputs were BF16, but **none of the 21 comparisons was bit-exact**. Therefore this report does not claim equivalence or numerical compatibility. The table gives the three inputs as `pattern / normal-1 / normal-2`, reporting `max_abs` and `mean_abs`; the final column is the largest `max_abs / max(|y_q|)` across them.

| projection | exact equality (3) | max_abs (3) | mean_abs (3) | max relative-to-output-magnitude |
|---|---|---|---|---:|
| q_proj | false / false / false | 0.671875 / 0.109375 / 0.093750 | 0.095849 / 0.012199 / 0.013503 | 7.363% |
| k_proj | false / false / false | 0.585938 / 0.074219 / 0.093750 | 0.110048 / 0.013644 / 0.015251 | 6.292% |
| v_proj | false / false / false | 0.414062 / 0.083984 / 0.068359 | 0.097172 / 0.012374 / 0.013426 | 5.300% |
| o_proj | false / false / false | 0.914062 / 0.250488 / 0.187500 | 0.094177 / 0.012100 / 0.013425 | 6.998% |
| gate_proj | false / false / false | 0.640625 / 0.093750 / 0.109375 | 0.096678 / 0.012515 / 0.013741 | 6.212% |
| up_proj | false / false / false | 0.593750 / 0.080078 / 0.085938 | 0.091558 / 0.011635 / 0.012855 | 7.143% |
| down_proj | false / false / false | 1.750000 / 0.293701 / 0.250000 | 0.174056 / 0.023067 / 0.024556 | 6.087% |

These are empirical output differences between the actual MLX quantized operation and dense BF16 multiplication of MLX's dequantized payload. They are not repaired, tolerated post hoc, or propagated into a model run.

## D. Steady-state M5 microbench

Each projection used 40 excluded warmups/side, then 60 `Q → BF16 → BF16 → Q` cycles: 120 `mx.eval`-synchronized samples/side. The same persistent BF16 `W` and fixed deterministic BF16 input remained in use. Values are median milliseconds `[p25, p75]`; `ratio = BF16/Q`; output rate is G output elements/s. Active/peak are MLX bytes after the warmed benchmark.

| projection | quantized M5 ms | persistent BF16 M5 ms | ratio | saved µs | Q / BF16 Gout/s | active / peak B |
|---|---:|---:|---:|---:|---:|---:|
| q_proj | 1.2600 [1.1789,1.4633] | 1.2340 [1.1412,1.3859] | 0.979333 | +26.04 | 0.01625 / 0.01660 | 118,800,400 / 119,177,232 |
| k_proj | 0.6634 [0.6507,0.6759] | 0.6863 [0.6645,0.7101] | 1.034484 | -22.88 | 0.00772 / 0.00746 | 93,595,664 / 93,759,504 |
| v_proj | 0.6638 [0.6546,0.6797] | 0.6875 [0.6692,0.7142] | 1.035620 | -23.65 | 0.00771 / 0.00745 | 93,595,664 / 93,759,504 |
| o_proj | 1.5571 [1.5272,1.6109] | 1.4537 [1.4218,1.4904] | 0.933584 | +103.42 | 0.01315 / 0.01409 | 118,800,400 / 119,128,080 |
| gate_proj | 2.2131 [2.1873,2.2588] | 4.1371 [4.1051,4.1899] | 1.869357 | -1,923.98 | 0.02776 / 0.01485 | 185,991,184 / 186,122,256 |
| up_proj | 2.2181 [2.2037,2.2506] | 4.1426 [4.1098,4.1794] | 1.867642 | -1,924.52 | 0.02770 / 0.01483 | 185,991,184 / 185,991,184 |
| down_proj | 2.1639 [2.1459,2.1935] | 2.7558 [2.7313,2.8058] | 1.273514 | -591.85 | 0.00946 / 0.00743 | 185,909,264 / 186,613,776 |

The two small positive isolated medians (Q/O) are neither a >=5% block projection nor memory-safe under the conservative BOTH-resident model. All MLP dense BF16 paths are materially slower.

## E. Arithmetic full-model projection and break-even

This is intentionally only arithmetic: one isolated per-projection median saving × 36 layers. It is not additive scheduling evidence and is not a full-model result. Reference wall is Stretch 031 M5 median block `0.3487060 s`; positive values only are speedups.

| class | per-layer saved µs | x36 block ms | block gain | x36 one-time dequant s | target traversals to break even |
|---|---:|---:|---:|---:|---:|
| Q | +26.04 | +0.9375 | +0.2688% | 0.1495 | 159.51 |
| K | -22.88 | -0.8235 | -0.2362% | 0.1107 | n/a (slower) |
| V | -23.65 | -0.8512 | -0.2441% | 0.0582 | n/a (slower) |
| O | +103.42 | +3.7230 | +1.0677% | 0.1123 | 30.16 |
| gate | -1,923.98 | -69.2632 | -19.8629% | 1.2395 | n/a (slower) |
| up | -1,924.52 | -69.2828 | -19.8685% | 0.1981 | n/a (slower) |
| down | -591.85 | -21.3068 | -6.1102% | 0.1774 | n/a (slower) |
| K+V | — | -1.6748 | -0.4803% | 0.1689 | n/a (slower) |
| Q+O | — | +4.6605 | +1.3365% | 0.2618 | 56.18 |

Even if numerical behavior had passed, the largest arithmetic positive, Q+O, is only `1.3365%`, below the admission target and requires an unsafe cache.

## F. Speed-per-memory Pareto view

Minimum free memory starts from the conservative observed Stretch 031 M5 `18%`. The column below subtracts added cache MiB from 8 GiB linearly **only as a feasibility diagnostic**; memory pressure is not assumed linear. `<5%` is classified memory-risky because it crosses the historical abort boundary.

| candidate | projected gain | added resident MiB (BOTH) | ms saved / 100 MiB | estimated min free % | memory-risky |
|---|---:|---:|---:|---:|---|
| Q | +0.2688% | 1,152 | +0.0814 | 3.94% | yes |
| K | -0.2362% | 288 | -0.2859 | 14.48% | no |
| V | -0.2441% | 288 | -0.2956 | 14.48% | no |
| O | +1.0677% | 1,152 | +0.3232 | 3.94% | yes |
| gate | -19.8629% | 3,456 | -2.0041 | -24.19% | yes |
| up | -19.8685% | 3,456 | -2.0047 | -24.19% | yes |
| down | -6.1102% | 3,456 | -0.6165 | -24.19% | yes |
| K+V | -0.4803% | 576 | -0.2908 | 10.97% | no |
| Q+O | +1.3365% | 2,304 | +0.2023 | -10.12% | yes |

## Decision

**`STRETCH_036_PERSISTENT_DEQUANTIZED_PROJECTION_FEASIBILITY_NO_GO`.**

No candidate satisfies the gate:

1. no projection was bit-exact over the three real-payload BF16 probes, and no alternative compatibility threshold was predefined;
2. only Q/O isolated timings are positive; Q+O reaches only `1.3365%` arithmetic block upside, not `>=5%`;
3. Q/O conservative x36 caches independently project below the historical `5%` free-memory abort threshold; and
4. K/V are memory-safer but slower; all MLP classes are both slower and memory-prohibitive.

Therefore no scientific Stretch-036 preregistration, source transform, 36-layer persistent cache, numerical rescue, or full-model ABBA is authorized. Canonical monolithic M5 3-bit/group64 affine `mx.quantized_matmul` remains unchanged.

## Evidence

- Runner: `scripts/stretch_persistent_dequantized_projection_036_feasibility.py`
- Parent summary: `results-local/stretch/persistent-dequantized-projection-036-feasibility/20260820-205800/summary.json`
- Child evidence: `results-local/stretch/persistent-dequantized-projection-036-feasibility/20260820-205800/child-summary.json`
- Captured stdout/stderr are colocated in that evidence directory.
