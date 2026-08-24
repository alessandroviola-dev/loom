# LOOM DFlash Drafter Decision Stability 001 — Result

Date: 2026-08-24
Classification: `LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001_PASS`
Gate: `PASS`
Raw evidence: `results-local/research/dflash-drafter-decision-stability-001/20260824T114723Z/`

## Scope

Validate the MLX DFlash drafter as a stable proposal source across frozen real target-tap states before any speculative target integration.

## Corpus

- 9 frozen real-tap states.
- Prompts P1/P2/P3.
- Trace positions 1, 16 and 32 for each prompt.
- Full autoregressive draft rollout through 7 proposals.

## Proposal-decision stability

- Compared proposal decisions: 63.
- MLX vs independent NumPy publisher-source translation parity: **100%**.
- Mismatches: **0**.
- First mismatch: none.
- Deterministic rerun proposal parity: PASS.

Top1-top2 mapped proposal margin:
- P50: 0.4271.
- P10: 0.04625.
- Minimum: 0.00510.

The minimum margin is materially larger than zero, and no decision mismatch was observed even at the weakest sampled margin.

## Cross-implementation logits

Final-draft-logit error across the corpus:
- max-abs P50: 0.00904.
- max-abs maximum: 0.01310.
- mean-abs P50: 0.0009983.
- mean-abs maximum: 0.001386.

No NaN or Inf occurred.

## Drafter performance

Seven-proposal rollout wall:
- P50: 0.08437 s.
- Mean: 0.09067 s.

This is standalone drafter cost only. It is not yet end-to-end speculative-generation throughput.

## Memory

- MLX resident: 1,362,053,640 B.
- MLX peak: 2,305,009,460 B.
- MLX workspace above resident: 942,955,820 B.
- RSS: 1,449,148,416 B.
- Swap delta: 0 MiB.
- Memory pressure: PASS.

## Interpretation

The broader real-state corpus closes the practical decision-stability concern left by `LOOM_DFLASH_DRAFTER_PORT_001_PASS`. Despite small MLX-vs-NumPy numerical differences, all 63 mapped proposal decisions across 9 real target states and seven-step rollouts are identical, deterministic, finite and memory-safe.

The component is therefore accepted as sufficiently stable for the first controlled greedy DFlash end-to-end experiment.

This checkpoint still makes **no** speculative-generation, acceptance-length or sustained target-throughput claim because the drafter was not connected to the target verifier here.

## Next

Run the first end-to-end greedy DFlash loop combining:
- the validated MLX drafter;
- proposals up to 7;
- the exact B7 wavefront target verifier;
- canonical acceptance/rejection semantics;
- exact comparison against ordinary greedy target generation.

Measure acceptance length, target verifications/output token, external expert bytes/accepted token, sustained wall/tok-s, and combined drafter+target memory.