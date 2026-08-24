# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`
Strategic next: `LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001`

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
- MLX DFlash drafter port and cross-implementation decision stability.

## DFlash target side — PASS

`LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`:
- canonical q_len=1 attention per candidate position;
- seven positions move layer-by-layer;
- each unique expert loaded once/layer and reused;
- hidden/KV/router/logits/token decisions bitwise exact;
- 431,519,451 B useful expert bytes/verified position;
- 10.8152 -> 6.5430 s = 1.653x;
- swap delta 0; no expert leak.

## DFlash drafter — COMPONENT/STABILITY PASS

- all 680,813,824 learned BF16 params mapped in MLX;
- 9 real target-tap states;
- 63/63 mapped proposal decisions match the independent NumPy publisher translation;
- deterministic rerun PASS;
- seven-proposal drafter P50 ~0.08437 s;
- standalone memory pressure PASS.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`.

Report: `research/architecture/loom-dflash-greedy-e2e-001-result.md`.

Correct committed target behavior:
- P1/P2/P3 completed;
- 96 output tokens;
- committed token parity PASS;
- target KV/router/logit parity PASS;
- deterministic rerun PASS;
- zero expert leak.

But speculative usefulness is zero:
- 96 cycles;
- mean/P50 accepted proposals = 0.0;
- acceptance rate = 0%;
- verifier calls/output token = 1.96875;
- useful external expert bytes/output token = 3,098,293,248 B;
- control 0.7735 tok/s;
- DFlash 0.1544 tok/s = 0.1996x.

Memory also fails:
- MLX peak 3,148,206,740 B;
- RSS peak 1,259,044,864 B;
- swap +737.43 MiB.

This is not a memory-only failure. Zero acceptance is an independent blocker and is now the first priority.

## Next — acceptance alignment diagnosis

Checkpoint: `LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001`.

Before any memory/performance optimization, determine why the decision-stable drafter receives zero target acceptance.

Audit a small deterministic set of E2E cycles against publisher/source semantics:
1. target greedy continuation tokens;
2. actual mapped proposals 1..7;
3. verifier target logits/token positions;
4. drafter seed/input token;
5. target-tap timing/position;
6. draft-logit index per proposal;
7. d2t/t2d mapping location;
8. draft KV init/carry/reset;
9. proposal offset relative to target continuation;
10. acceptance/correction/bonus semantics.

The key distinction is:
- **integration/alignment bug**: off-by-one, wrong seed, tap timing, mapping or KV semantics. Repair only the proven variable and run a short acceptance probe;
- **alignment correct but acceptance truly ~0**: investigate drafter/target compatibility, especially the drafter trained for the intended Qwen3 target versus the local MLX 4-bit target, in a separate checkpoint.

Do not optimize memory, caching, packing, quantization or verifier kernels while zero acceptance is unresolved.

## After nonzero acceptance

1. memory remediation for combined target + BF16 drafter runtime;
2. full E2E rerun;
3. measure accepted tokens/verifier, expert bytes/output token and sustained tok/s;
4. optimize only the measured dominant cost;
5. capability/coding benchmark;
6. context/stability;
7. if still insufficient: route prediction/prefetch, finer sparsity or LOOM-native co-design;
8. behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only active delta, exact inputs, gates, evidence and concise return fields. Pi performs local execution/tests/evidence; ChatGPT owns Git/HANDOFF/ROADMAP.
