# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001_PASS`
Strategic next: `LOOM_DFLASH_GREEDY_E2E_001`

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
- exact DFlash target taps `[1,12,23,34,45]`;
- exact B7 target verification with wavefront expert reuse.

## Exact B7 target verification — PASS

`LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`:
- canonical q_len=1 attention per position;
- seven positions progress layer-by-layer;
- each unique expert loaded once/layer and reused across assigned positions;
- hidden/KV/router/logits/token decisions bitwise exact;
- 431,519,451 B useful expert bytes/verified position;
- B7 target wall 10.8152 -> 6.5430 s = 1.653x;
- swap delta 0; no expert leak.

## Learned DFlash drafter — PORT + STABILITY PASS

`LOOM_DFLASH_DRAFTER_PORT_001_PASS` maps all 680,813,824 learned BF16 params and runs memory-safe in MLX.

`LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001_PASS` closes the remaining proposal-source stability concern:
- 9 frozen real target states across P1/P2/P3;
- 63 proposal decisions across full seven-step rollouts;
- 100% mapped proposal-token parity vs independent NumPy publisher-source translation;
- mismatches 0;
- deterministic rerun PASS;
- no NaN/Inf;
- top1-top2 margin P50/P10/min 0.4271 / 0.04625 / 0.00510;
- final-logit max-abs P50/max 0.00904 / 0.01310;
- seven-proposal drafter wall P50 0.08437 s;
- MLX resident 1,362,053,640 B; peak 2,305,009,460 B;
- RSS 1,449,148,416 B; swap delta 0; memory pressure PASS.

The drafter is now accepted for a controlled first end-to-end speculative experiment. No acceptance-length or speculative-speed claim exists yet.

## Next — first greedy DFlash end-to-end

Checkpoint: `LOOM_DFLASH_GREEDY_E2E_001`.

Combine only proven components:
1. target prefill and exact tap capture;
2. MLX learned drafter generates up to seven mapped target proposals;
3. exact B7 wavefront verifier evaluates them;
4. canonical greedy acceptance/rejection determines committed tokens;
5. exact ordinary-greedy target generation remains the reference.

Required correctness:
- identical committed output tokens to ordinary greedy target generation;
- exact accepted-prefix/rejection semantics;
- correct target KV after every commit/reject boundary;
- target verifier remains bitwise exact where applicable;
- no routed-expert leak;
- memory pressure PASS / no swap growth.

Required economics:
- proposal acceptance length distribution;
- accepted proposals per verifier call;
- verifier calls/output token;
- useful external expert bytes/output token;
- drafter wall, target-verifier wall and other wall separately;
- end-to-end tok/s versus ordinary greedy control;
- MLX/RSS/swap peak.

Do not add caching, prefetch, quantization, new packing or unrelated optimization in this checkpoint.

## After E2E

If correctness PASS:
1. run longer/multi-prompt sustained speculative generation;
2. profile the real bottleneck from drafter + verifier + storage;
3. optimize only the dominant measured cost;
4. capability/coding benchmark once practical speed improves;
5. context/stability;
6. if insufficient, evaluate route prediction/prefetch, finer-grained sparsity or LOOM-native co-design;
7. behavioral decensoring validation before final promotion.

If correctness FAIL:
- localize first acceptance/KV/output divergence before any speed optimization.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only the active work-package delta. Pi performs local code/tests/evidence; ChatGPT owns Git/HANDOFF/ROADMAP.
