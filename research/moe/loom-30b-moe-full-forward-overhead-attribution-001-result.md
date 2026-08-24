# LOOM 30B MoE Full-Forward Overhead Attribution 001 — Result

Date: 2026-08-24
Run: `20260824T080141Z`
Classification: `LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS`

## Result

The ~18 s gap in the first complete 30B external-expert forward was overwhelmingly research instrumentation rather than model execution.

Reference F1 wall from the prior checkpoint was 20.333756 s. The fully instrumented attribution run reconciled 100% of its own 21.662793 s wall.

Dominant categories:
- forced `gc.collect`: 13.350101 s / 61.63%;
- per-expert RSS sampling: 5.879225 s / 27.14%;
- expert source `pread`: 1.217114 s / 5.62%;
- expert-output `mx.eval`: 0.301939 s / 1.39%;
- MLX array construction: 0.157429 s / 0.73%;
- attention `mx.eval`: 0.147799 s / 0.68%;
- file opens: 0.132775 s / 0.61%;
- byte-view work: 0.108174 s / 0.50%;
- all remaining categories individually below 0.39%.

The reference path issued 864 explicit GC calls totaling 13.350101 s. Per-expert GC was therefore the dominant artificial cost. Per-expert/process RSS measurement was the second major observer effect.

## Controlled runtime simplification

Instrumentation variants:
- audited reference: 21.662793 s;
- minimal measurement: 14.289831 s;
- timing skeleton: 14.188257 s.

GC cadence A/B:
- GC every expert: 14.188257 s;
- GC every layer: 2.359604 s;
- GC at end only: 1.641729 s.

`GC_END_ONLY` remained bitwise exact:
- logits parity PASS;
- router parity PASS;
- final routed-expert residency 0 / 0 B;
- maximum logical expert live 2,506,752 B;
- MLX peak 821,640,984 B;
- RSS peak 1,247,002,624 B;
- isolated swap delta 0.0 MiB;
- memory-pressure gate PASS.

Fastest safe per-layer wall P50/P90/P95/max:
- 0.032469 / 0.033652 / 0.034337 / 0.063860 s.

Forward-equivalent rate: 0.6091/s, explicitly not autoregressive generation TPS.

For the fastest safe exact path, approximate shares were:
- file/pread: 65.36%;
- compute: 21.93%;
- other software/runtime overhead: 12.71%.

## Decisions

- ~18 s gap primarily instrumentation: YES.
- per-expert GC dominant: YES.
- reduced GC cadence safe in this checkpoint: YES.
- full expert-major pack justified by measured bottleneck: NO.
- first autoregressive generation: CONDITIONALLY justified.
- routing-cache study: CONDITIONALLY justified, preferably from real sequential generation traces.
- DFlash branch: CONDITIONALLY justified after a clean autoregressive baseline.

## Strongest conclusion

The earlier ~20 s full-forward wall was not representative of the 30B runtime. Forced cyclic GC and RSS sampling in the hot loop accounted for most of it. With those research-only costs removed and explicit GC deferred to the end, the complete exact external-expert forward falls to 1.641729 s with no swap growth and no expert leakage.

Raw evidence: `results-local/moe/full-forward-overhead-attribution-001/20260824T080141Z/`.
