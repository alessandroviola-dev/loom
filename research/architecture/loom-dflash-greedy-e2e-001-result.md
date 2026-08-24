# LOOM DFlash Greedy E2E 001 — Result

Date: 2026-08-24
Checkpoint: `LOOM_DFLASH_GREEDY_E2E_001`
Classification: `LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`

## Summary

The first end-to-end greedy DFlash loop completed all three preregistered prompts with exact committed target-token parity, exact target router/logit/KV correctness, deterministic rerun parity and no routed-expert leak. However, the treatment is rejected.

The critical finding is not only memory pressure. The learned drafter achieved **zero accepted proposals across 96 speculative cycles**, making the speculative path structurally ineffective in its current integration. The treatment also caused swap growth and severe slowdown.

## Corpus / correctness

- prompts completed: P1/P2/P3;
- committed output tokens: 96;
- committed token parity vs ordinary greedy control: PASS;
- target KV/router/logit parity: bitwise PASS;
- deterministic rerun: PASS;
- routed-expert ownership: PASS / zero leak.

## Acceptance

- speculative cycles: 96;
- mean accepted proposals/cycle: **0.0**;
- P50 accepted proposals/cycle: **0.0**;
- proposal acceptance rate: **0%**.

This is a primary scientific blocker independent of the memory gate. A speculative system with zero accepted proposals cannot benefit from multi-token target verification even if memory pressure is later repaired.

## Economics

- verifier calls/output token: **1.96875**;
- useful external expert bytes/output token: **3,098,293,248 B**;
- control throughput: **0.7735 tok/s**;
- DFlash treatment throughput: **0.1544 tok/s**;
- relative speed: **0.1996x** control.

Wall breakdown:
- drafter: 43.906 s;
- verifier: 574.698 s;
- other: 3.110 s;
- total: 621.713 s.

## Memory

- MLX peak: **3,148,206,740 B**;
- RSS peak: **1,259,044,864 B**;
- swap delta: **+737.43 MiB**;
- memory gate: FAIL.

## Interpretation

Pi returned the classification as a memory-only failure, but LOOM treats the zero-acceptance result as an independent blocker. The previous drafter decision-stability checkpoint established MLX parity against an independent NumPy translation of the publisher implementation; it did **not** establish that the rollout was aligned correctly to the target's speculative-generation contract.

A shared semantic/alignment mistake could therefore have passed the MLX-vs-NumPy comparison while yielding systematically shifted or otherwise invalid proposals end-to-end.

Do not optimize memory, caching, packing or verifier performance yet. First diagnose the zero-acceptance path against the publisher/source contract, including:
- proposal seed/input token;
- target-tap position/timing;
- draft-logit index used for proposal k;
- d2t/t2d mapping location;
- target candidate/logit alignment;
- draft KV initialization/carry/reset semantics;
- proposal offset relative to the target greedy continuation.

## Evidence

Local raw evidence:
`results-local/research/dflash-greedy-e2e-001/20260824T124009Z/`

Local runner:
`scripts/loom_dflash_greedy_e2e_001.py`

## Gate

`FAIL_GATE`

Reasons:
1. `ZERO_ACCEPTANCE_BLOCKER` — 0 accepted proposals in 96 cycles;
2. `MEMORY_PRESSURE_FAIL` — swap delta +737.43 MiB;
3. performance regression — 0.1544 tok/s vs 0.7735 tok/s control.

Next checkpoint must diagnose proposal alignment/semantics before any memory remediation or optimization.