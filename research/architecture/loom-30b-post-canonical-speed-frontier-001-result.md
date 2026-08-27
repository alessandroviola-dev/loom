# LOOM 30B Post-Canonical Speed Frontier 001 — Result

Date: 2026-08-27
Checkpoint: `LOOM_30B_POST_CANONICAL_SPEED_FRONTIER_001`
Classification: `SPEED_FRONTIER_ADVANCED`

## Decision

The exact Q4 canonical runtime speed frontier advanced, but the aspirational `5.0 tok/s` target was not reached.

The only retained treatment is a process-lifetime persistent PACKED file descriptor with deterministic close. All other attempted exactness-preserving treatments were reverted by their frozen gain/safety gates.

## Evidence

Local evidence:
`results-local/research/30b-post-canonical-speed-frontier-001/20260827T131329Z/`

Summary:
`results-local/research/30b-post-canonical-speed-frontier-001/20260827T131329Z/summary.json`

## Stage 0 — sustained baseline

Canonical sustained throughput: `1.063941 tok/s`.

Ranked wall attribution:
1. expert file I/O: `13.415820 s` (`44.61%`);
2. expert compute: `7.971682 s` (`26.50%`);
3. non-expert/backbone: `4.432324 s` (`14.74%`);
4. materialization/synchronization: `3.462511 s` (`11.51%`);
5. routing: `0.794527 s` (`2.64%`).

## Treatment decisions

### Stage 1 — persistent PACKED fd

PASS and retained.

- exactness: PASS;
- throughput: `1.063941 -> 1.155990 tok/s`;
- gain: `+8.65%`;
- deterministic process-lifetime close;
- no payload cache/fallback.

### Stage 2 — synchronization collapse

Exactness PASS but performance FAIL; reverted.

- `1.155990 -> 0.804759 tok/s`;
- `-30.38%`.

### Stage 3 — bounded allocation/copy reduction

Performance signal positive but RSS gate FAIL; reverted.

- `1.155990 -> 1.197604 tok/s`;
- `+3.60%`;
- RSS delta `+151,879,680 B`, exceeding frozen `+32 MiB` bound.

### Stage 4 — bounded one-ahead overlap

Performance signal positive but RSS gate FAIL; reverted.

- `1.155990 -> 1.253617 tok/s`;
- `+8.45%`;
- RSS delta `+162,676,736 B`, exceeding frozen `+32 MiB` bound.

## Final sustained decision

Three fresh 32-token repetitions:
- `1.115874 tok/s`;
- `1.229233 tok/s`;
- `1.254611 tok/s`.

Median: `1.229233 tok/s`.

Compared with the Stage-0 `1.063941 tok/s` baseline, the accepted final median is approximately `15.53%` higher.

Token wall:
- p50 `0.825660 s`;
- p95 `1.217692 s`.

Safety:
- peak RSS `404,340,736 B`;
- swap delta `0.0 MiB` in each final repetition;
- no unsafe pressure/fallback/persistent payload cache.

Final exactness: PASS on all three frozen raw float32-logit SHA positions.

Final backend SHA-256 after retained Stage-1 change:
`6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

## Interpretation

The remaining dominant bottleneck is expert file I/O. At the frozen top-8 Q4 geometry, one decode token requires `384` routed expert payloads, or `962,592,768 B` of expert payload. A `5 tok/s` target would therefore imply roughly `4.81 GB/s` of expert payload traffic before accounting for compute, backbone, routing, and materialization.

The exact-Q4 path should not be expected to reach `5 tok/s` through additional small hot-path engineering alone.

Next speed work may intentionally trade a bounded amount of model fidelity for speed, but only under an explicit preregistered quality gate. The first candidate is routing sparsification because it can reduce expert I/O, materialization, and expert compute simultaneously without rebuilding the full bank.

## Repository state

Accepted local code delta:
`scripts/loom_30b_moe_expert_major_backend_001.py` — persistent process-lifetime PACKED file descriptor.

This accepted delta must be reviewed and committed before the next independent speed checkpoint executes.
