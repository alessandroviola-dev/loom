# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001_REPAIRED_PROBE_ZERO_ACCEPTANCE`
Strategic next: `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, full intended model capacity, reproducible correctness and later behavioral-freedom validation.

Canonical target values and stable invariants live in `/AGENTS.md`.

## Proven target/runtime

- full Qwen3-30B-A3B external-expert execution across all 48 layers;
- exact final logits and real greedy generation;
- complete ~819-MB shared-backbone residency;
- expert-major disk access gives a real decode win;
- real routing reuse exists;
- 4-GiB resident raw cache rejected for memory pressure;
- exact DFlash target taps `[1,12,23,34,45]`;
- exact B7 wavefront target verification with expert reuse;
- MLX DFlash drafter component runs and fits.

## DFlash target side — PASS

`LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`:
- canonical q_len=1 attention per candidate position;
- seven positions move layer-by-layer;
- each unique expert loaded once/layer and reused;
- hidden/KV/router/logits/token decisions bitwise exact;
- 431,519,451 B useful expert bytes/verified position;
- 10.8152 -> 6.5430 s = 1.653x;
- swap delta 0; no expert leak.

## DFlash drafter — COMPONENT PASS, publisher-semantics parity reopened

The MLX port maps all 680,813,824 learned BF16 params and is standalone memory-safe.

A prior decision-stability corpus showed 63/63 MLX-vs-NumPy proposal parity, but the subsequent E2E alignment diagnostic found that both validations preceded correction of the publisher anchor/block attention mask. Therefore that old 63/63 result is not sufficient proof of the corrected publisher contract.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- 96 output tokens with committed target parity PASS;
- target KV/router/logit correctness PASS;
- acceptance 0/96;
- 3,098,293,248 useful external expert B/output token;
- control 0.7735 tok/s vs treatment 0.1544 tok/s;
- swap +737.43 MiB.

Do not optimize memory while acceptance remains zero.

## Acceptance alignment diagnosis — mask bug repaired, acceptance still zero

`LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001_REPAIRED_PROBE_ZERO_ACCEPTANCE`.

Report: `research/architecture/loom-dflash-acceptance-alignment-diag-001-result.md`.

Recovered publisher contract:
- base attention positions strictly before anchor;
- causal same-block synthetic attention;
- slots 1–7 map via `d2t`;
- `sample_from_anchor=False`;
- target taps remain post-block `[1,12,23,34,45]`;
- no draft-KV carry;
- target correction/bonus logic aligned.

The MLX port had omitted the anchor/block attention mask. Only `Drafter.propose` masking was repaired.

Short repaired probe:
- 3 cycles;
- 0/21 proposals accepted;
- prefixes `[0,0,0]`;
- no k-1/k/k+1 systematic shift.

This does not yet prove drafter/target incompatibility. The corrected MLX path must first be compared with an independent masked publisher-semantics reference.

## Next — masked publisher-reference parity

Checkpoint: `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001`.

Required experiment:
1. implement the publisher mask independently in the reference path, not by calling/reusing the MLX mask builder;
2. assert the visibility matrix for anchor/base/synthetic slots against publisher source semantics;
3. use real frozen target-tap states from multiple prompts/positions;
4. compare MLX vs independent reference through fusion, five draft layers and seven autoregressive proposal positions;
5. require mapped proposal-token parity and deterministic rerun;
6. quantify final-logit error/margin distributions;
7. record target acceptance only as an observation.

Decision:
- parity FAIL => localize/fix corrected drafter implementation before any target compatibility claim;
- parity PASS + acceptance ~0 => proceed to a separate target/drafter compatibility audit, with local MLX 4-bit target mismatch as a hypothesis to test;
- do not rerun full E2E or remediate memory yet.

## After acceptance becomes nonzero

1. combined target+drafter memory remediation;
2. full E2E rerun;
3. measure accepted tokens/verifier, expert bytes/output token and sustained tok/s;
4. optimize only the dominant measured cost;
5. capability/coding benchmark;
6. context/stability;
7. if still insufficient: route prediction/prefetch, finer sparsity or LOOM-native co-design;
8. behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only active delta, exact inputs, gates, evidence and concise return fields. Pi performs local execution/tests/evidence; ChatGPT owns Git/HANDOFF/ROADMAP.
