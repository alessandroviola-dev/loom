# LOOM — TRACE PACK DECODE A/B 001 — Result

Date: 2026-08-24
Classification: `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001_PASS`
Run: `20260824T084956Z`
Raw evidence: `results-local/moe/trace-pack-decode-ab-001/20260824T084956Z/`

## Purpose

Measure on the real autoregressive decode hot path whether lossless expert-major storage materially improves Qwen3-30B-A3B external-expert decode versus the original safetensor exact-range layout, without changing model math, routing, KV semantics, GC cadence, or expert residency.

## Pack correctness

The canonical measured decode trace referenced 384 routed `(layer, expert)` instances. A trace-scoped expert-major binary containing exactly those 384 experts was built:

- useful payload: 962,592,768 B;
- binary bytes: 962,592,768 B;
- no padding;
- validated components: 3,456;
- validated bytes: 962,592,768 B;
- mismatches: 0.

Each expert is represented as one contiguous 2,506,752-B range rather than nine source component ranges.

## Read geometry

CONTROL — source exact ranges:
- 3,456 pread calls/decode position;
- 962,592,768 B requested;
- byte amplification 1.0x.

TREATMENT — expert-major pack:
- 384 pread calls/decode position;
- 962,592,768 B requested;
- byte amplification 1.0x.

Read-call reduction: 88.888889%.

## Exactness

Treatment preserved target behavior:
- router parity PASS;
- final logits parity PASS;
- generated-token parity PASS;
- expected token remained canonical EOS (`151645`).

No model-math change is involved.

## Real decode A/B

Expert-read wall, median / P90 / P95:
- CONTROL: 1.085528 / 1.093269 / 1.094834 s;
- TREATMENT: 0.442087 / 0.444556 / 0.444872 s.

Expert-read reduction:
- 0.643441 s;
- 59.274514%.

Total decode wall, median / P90 / P95:
- CONTROL: 1.645328 / 1.683489 / 1.692522 s;
- TREATMENT: 0.926028 / 0.929970 / 0.930031 s.

Total decode reduction:
- 0.719300 s;
- 43.717720%.

Decode-equivalent rates:
- CONTROL: 0.607781 tok/s;
- TREATMENT: 1.079881 tok/s.

These are real one-step autoregressive-path rates, not yet a sustained long-generation benchmark.

## Treatment timing

Median treatment timing:
- attention: 0.181141 s;
- router: 0.019075 s;
- metadata: 0.000694 s;
- open: 0.012078 s;
- pread: 0.381424 s;
- slicing: 0.048317 s;
- MLX reconstruction: 0.043738 s;
- synchronization: 0.207464 s;
- expert compute: 0.004186 s;
- aggregation: 0.013104 s;
- LM head: 0.004683 s.

Approximate bottleneck shares:
- expert access: 47.74%;
- attention: 19.56%;
- reconstruction: 4.72%;
- expert compute: 0.45%;
- other: 27.52%.

The packed path substantially reduces storage/access overhead, but expert access remains the largest single category. Synchronization is also now material and should be treated separately from physical I/O.

## Device qualification

Timing is application-level `os.pread` timing. OS page cache may contribute. No `disk0` counter was collected in this A/B, so these results are not promoted as physical-SSD throughput. The A/B decode latency effect itself is valid because model semantics and requested useful bytes were held constant.

## Memory

Treatment:
- MLX peak: 881,152,008 B;
- RSS peak: 910,983,168 B;
- swap delta: 0 MiB for every treatment run;
- final routed-expert residency: 0 / 0 B.

## Decision

- expert-major storage materially reduces expert access wall: YES;
- materially reduces real decode wall: YES;
- exact output preserved: YES;
- future routing/cache baseline: PACKED;
- full 14.344-GiB expert-major pack: CONDITIONAL;
- longer real routing trace: CONDITIONAL, but scientifically justified as the next evidence step before cache implementation.

A complete pack is not built automatically from this result. The effect size is strong, but cache-policy evidence should first determine whether a full-bank duplicate is necessary or whether a smaller/on-demand packed working set can deliver most of the value.

## Strongest supported conclusion

Lossless expert-major storage is not merely a storage-format improvement: on the real autoregressive decode path it reduced expert-access time by 59.27% and total decode wall by 43.72%, with bitwise-identical routing and logits. PACKED is therefore the correct performance baseline for subsequent cache economics.