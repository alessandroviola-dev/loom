# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_DRAFTER_PORT_001_PASS`
Strategic next: `LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, full intended model capacity, reproducible correctness and later behavioral-freedom validation.

Canonical target values and stable invariants live in `/AGENTS.md`.

## Proven target/runtime

- full Qwen3-30B-A3B external-expert execution across all 48 layers;
- exact final logits and real greedy generation;
- complete ~819-MB shared-backbone residency;
- expert-major disk geometry as a real decode win;
- real routing reuse;
- large 4-GiB resident raw cache rejected for memory pressure;
- exact DFlash target taps `[1,12,23,34,45]` exposed with small overhead;
- exact B7 target verification with wavefront expert reuse.

## DFlash target verification — PASS

`LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS` establishes the target schedule needed for proposals=7:
- q_len=1 attention remains canonical per position;
- seven candidate positions move layer-by-layer;
- each unique expert is loaded once/layer and reused across assigned positions;
- hidden/KV/router/logits/token decisions are bitwise exact;
- useful external expert bytes fall to 431,519,451 B/verified position;
- B7 target verification wall: 10.8152 s sequential -> 6.5430 s wavefront = 1.653x;
- swap delta 0; no expert leak.

## DFlash learned drafter port — PASS AS COMPONENT

`LOOM_DFLASH_DRAFTER_PORT_001_PASS`.

Report: `research/architecture/loom-dflash-drafter-port-001-result.md`.

MLX mapping:
- 680,813,824 learned BF16 params;
- 1,361,627,648 learned weight bytes;
- 60 learned + 2 mapping tensors;
- no missing/extra learned weights.

Independent reference is a NumPy translation of publisher source because the official Torch/Speculators runtime is unavailable locally.

Observed cross-implementation errors:
- fusion max abs 1.38e-05;
- draft layers max abs 0.0515–0.1442;
- final draft logits max/mean 0.01956 / 0.003045.

The tested deterministic mapped draft-token decisions were identical and no NaN/Inf occurred.

Measured M1 memory:
- MLX resident 1,362,053,632 B;
- MLX peak 2,289,441,196 B;
- workspace 927,387,564 B;
- RSS peak 1,423,212,544 B;
- swap delta 0;
- memory gate PASS.

This proves the component can run and fit, but does not yet certify it as a reliable speculative proposal source across real states.

## Next — drafter decision stability

Checkpoint: `LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001`.

Before end-to-end speculative integration:
1. collect a preregistered corpus of real frozen target taps from multiple prompts and positions;
2. compare MLX vs independent NumPy source translation on identical states;
3. run full autoregressive draft rollouts up to seven proposals;
4. require mapped proposal-token parity at every rollout position;
5. record proposal top-1/top-2 margins and logit-error distributions;
6. repeat deterministically;
7. measure standalone drafter wall, resident/peak MLX, RSS and swap.

If PASS, integrate the learned drafter with the exact B7 wavefront target verifier for a first greedy end-to-end DFlash experiment.

If FAIL, localize the first real state/rollout decision mismatch before any integration.

## After decision-stability PASS

1. first greedy DFlash speculative loop + exact B7 wavefront verifier;
2. measure real acceptance length and target verification steps/output token;
3. measure unique external expert bytes/accepted token and sustained generation tok/s;
4. compare against current source and packed non-speculative baselines;
5. only then reconsider complementary small cache/storage ideas;
6. capability/coding benchmark;
7. context/stability;
8. if speed remains insufficient: route prediction/prefetch, finer-grained sparsity or LOOM-native co-design;
9. behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only the active work-package delta. Pi performs local code/tests/evidence; ChatGPT owns Git/HANDOFF/ROADMAP.
