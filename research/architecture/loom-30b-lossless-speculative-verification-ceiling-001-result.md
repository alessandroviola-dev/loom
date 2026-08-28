# LOOM 30B Lossless Speculative Verification Ceiling 001 — Result

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Final classification: `SPEC_VERIFY_FRONTIER_NOT_PROMISING`

## Question

Can the canonical Qwen3-30B-A3B Q4 verifier, given perfect oracle future-token proposals, verify multiple tokens per target step fast enough to justify investment in a real drafter and plausibly approach the `5 tok/s` engineering target?

This experiment is an oracle-only verifier ceiling. Its throughput is NOT production generation speed.

## Frozen reference

Canonical exact-Q4 backend commit: `96958de`.
Accepted sustained baseline: `1.229233 tok/s` median from 3×32-token runs.

## Readiness / exactness

- `K=2`: PASS. Four-position oracle covered exact greedy IDs, routed expert order, raw float32 final-logit SHA, BF16-KV mechanics, finite logits, zero SOURCE fallback and zero persistent expert cache.
- `K=4`: PASS under the same exactness requirements.
- `K=8`: INVALID. Raw float32 final-logit SHA and routing order mismatched at all eight checked positions; no performance evidence was admitted.

## Oracle ceiling measurements

### K=2

- throughput: `1.548806 tok/s`;
- gain vs canonical baseline: `+26.00%`;
- expert access requests: `12,288`;
- unique expert payload loads: `9,540`;
- expert reuse rate: `22.36%`;
- expert payload traffic: `747,325,440 B/output-token`;
- chunks for 32 outputs: `16`;
- wall attribution over 32 outputs:
  - expert I/O `10.581 s`;
  - expert compute `5.236 s`;
  - materialization `1.074 s`;
  - backbone `3.447 s`;
  - routing `0.324 s`;
- peak RSS `273,006,592 B`;
- swap delta `0 MiB`;
- safety PASS.

### K=4

- throughput: `1.776372 tok/s` in the candidate run;
- gain vs canonical baseline: `+44.51%`;
- expert access requests: `12,288`;
- unique expert payload loads: `7,259`;
- expert reuse rate: `40.93%`;
- expert payload traffic: `568,641,024 B/output-token`;
- chunks for 32 outputs: `8`;
- wall attribution over 32 outputs:
  - expert I/O `9.168 s`;
  - expert compute `4.783 s`;
  - materialization `0.692 s`;
  - backbone `3.203 s`;
  - routing `0.168 s`;
- peak RSS `416,399,360 B`;
- swap delta `0 MiB`;
- safety PASS.

### K=8

INVALID exactness; no performance run.

## Final selected ceiling point

Selected `K=4`.

Final 3×32-output-token oracle-ceiling throughput:
- `1.792925 tok/s`;
- `1.807852 tok/s`;
- `1.785392 tok/s`;
- median `1.792925 tok/s`.

Median theoretical verifier speedup vs canonical baseline: `1.458572×` (`+45.86%`).

Final p50/p95 wall per output token:
- p50 `0.557813 s`;
- p95 `0.596685 s`.

Final K=4 reuse:
- access requests `12,288`;
- unique loads `7,259`;
- reuse `40.93%`;
- `568,641,024 B/output-token`.

Final RSS repetitions:
- `201,785,344 B`;
- `433,782,784 B`;
- `497,106,944 B`.

Swap delta `0 MiB` in all repetitions; safety PASS.

Final exactness PASS: greedy IDs, routing order, raw float32 final-logit SHA, finite logits, zero SOURCE fallback and zero persistent expert cache.

Evidence:
`results-local/research/30b-lossless-speculative-verification-ceiling-001/20260828T101836Z/`

No tracked runtime files changed.

## Interpretation

The verifier can amortize expert traffic across multiple exact token positions: K=4 reduces expert payload traffic from the canonical top-8 single-token level of `962,592,768 B/token` to `568,641,024 B/output-token`, a substantial mechanism-level improvement.

However, even with impossible perfect 100% oracle proposals and zero real-drafter cost, the valid K=4 median ceiling is only `1.792925 tok/s`, far below both the frozen `2.458466 tok/s` PROMISING threshold and the aspirational `5 tok/s` target.

Therefore a real drafter cannot plausibly rescue the current Qwen3-30B-A3B verifier to the desired speed: real speculative decoding would add drafter latency and imperfect acceptance below this oracle upper bound.

`K=8` is not accepted evidence and must not be repaired/rerun under this checkpoint. A future K=8 repair would require a materially new, separately preregistered hypothesis; it is not justified for current prioritization because the accepted K=4 oracle ceiling already fails the frozen promising gate.

## Decision

Freeze the current Qwen3-30B-A3B practical runtime at the exact-Q4 baseline `1.229233 tok/s` for production comparison.

Do not invest further in current-verifier DFlash, routing truncation, Q2/Q3 expert requantization, or a real speculative drafter absent a materially new mechanism.

Proceed to the next-model LOOM bake-off/readiness phase for Qwen3.8-27B and Qwen3.8-Flash-Next.