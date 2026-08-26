# LOOM — Expert-major global-nocache cold-I/O validation 002

Date: 2026-08-26
Classification: `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`
Evidence: `results-local/research/30b-expert-major-global-nocache-cold-io-validation-002/20260826T141527Z/`

## Goal

Test whether the corrected fixed-ABI `F_GLOBAL_NOCACHE` protocol can reproducibly produce genuinely physical repeated reads of the same existing packed subset.

## Frozen protocol

- packed-only;
- first 64 packed experts;
- `160,432,128 B` logical payload per trial;
- exactly three trials maximum;
- fresh read-only FD per trial;
- fixed-ABI `F_GLOBAL_NOCACHE=1` SET requiring raw return `0`, errno `0`;
- `F_NOCACHE=1`, `F_RDAHEAD=0`;
- timed 4-MiB-chunk read/hash;
- RESET `F_GLOBAL_NOCACHE=0` requiring raw return `1`, errno `0`;
- transactional restoration verification;
- frozen physical-coverage gate `>=80%` independently per trial.

## Results

| Trial | Conservative coverage | Wall | Raw physical bytes | Conservative physical bytes |
|---|---:|---:|---:|---:|
| T1 | 96.0406% | 0.251112 s | 154,260,000 B | 154,080,000 B |
| T2 | 25.8365% | 0.226934 s | 41,810,000 B | 41,450,000 B |
| T3 | 23.9728% | 0.228232 s | 39,020,000 B | 38,460,000 B |

Other gates:
- payload/hash: PASS 3/3;
- initial set/reset/restoration: PASS 3/3;
- swap deltas: 0 B / 0 B / 0 B;
- minimum free memory: 56%.

## Interpretation

The corrected control semantics remove the prior runner ambiguity. The method still fails scientifically because only T1 satisfies the frozen `>=80%` coldness gate; T2 and T3 are heavily cache-served despite all control operations succeeding.

Therefore repeated reads of the same packed pages cannot be treated as reproducibly cold under this protocol. This is a method failure, not an instrumentation/control failure.

The evidence supports a stronger operational pattern: the first touch of the tested region can be predominantly physical, while subsequent touches of the same region are not. This motivates a non-reuse/first-touch measurement design rather than further attempts to evict the same pages.

No performance claim from prior A/B 001 is rehabilitated.
