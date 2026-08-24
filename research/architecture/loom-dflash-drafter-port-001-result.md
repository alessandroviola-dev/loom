# LOOM DFlash Drafter Port 001 — Result

Date: 2026-08-24
Classification: `LOOM_DFLASH_DRAFTER_PORT_001_PASS`
Evidence: `results-local/research/dflash-drafter-port-001/20260824T113139Z/`

## Result

The exact-target DFlash drafter was ported to MLX and validated against an independent NumPy translation of the publisher source. The original publisher Torch/Speculators runtime was unavailable locally, so this checkpoint does not authorize speculative integration by itself.

## Mapping

- learned BF16 parameters: 680,813,824
- learned weight bytes: 1,361,627,648 B
- tensors: 60 learned + 2 mapping tensors
- missing learned tensors: 0
- extra learned tensors: 0

## Numerical comparison

- fusion max abs error: 1.38e-05
- draft-layer max abs error range: 0.0515–0.1442
- draft-layer mean abs error range: 0.00768–0.02422
- final draft-logit max abs error: 0.01956
- final draft-logit mean abs error: 0.003045
- mapped draft-token decisions: identical on the tested deterministic case
- NaN/Inf: none

These are cross-implementation numerical comparisons, not bitwise parity. The nontrivial intermediate deltas require broader decision-stability evidence before the MLX drafter is used to drive speculative generation.

## Memory

- MLX resident: 1,362,053,632 B
- MLX peak: 2,289,441,196 B
- measured workspace: 927,387,564 B
- RSS peak: 1,423,212,544 B
- swap delta: 0 MiB
- memory gate: PASS

## Gate

Component port: PASS.

Speculative integration: NO from this checkpoint alone.

Next requirement: exercise real target-tap states across multiple prompts/positions and full 7-proposal draft rollouts, comparing MLX vs the independent NumPy reference at the decision level. Only after stable proposal parity should the drafter be connected to the exact B7 wavefront target verifier.
