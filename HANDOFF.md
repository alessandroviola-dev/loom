# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — exact target verification and MLX DFlash drafter port proven; drafter decision stability next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_DRAFTER_PORT_001_PASS`
Next core checkpoint: `LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while balancing memory, speed, capability and later behavioral-freedom validation.

Stable target anatomy and proven invariants live in `/AGENTS.md`. Pi uses compact work packages; ChatGPT owns Git/HANDOFF/ROADMAP.

## Established runtime

- Qwen3-30B-A3B external-expert execution is bitwise exact across all 48 layers.
- Shared resident backbone: 819,015,680 B; routed bank stays external.
- Real greedy generation works on M1 8 GB.
- Expert-major disk layout materially improves decode.
- 4-GiB raw RAM cache is rejected despite real ~80.9% reuse because it causes severe swap/memory pressure.

## DFlash target side — COMPLETE

Exact-target candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Static:
- BF16 checkpoint ~1.2685 GiB;
- 5 draft layers;
- proposals=7;
- target taps `[1,12,23,34,45]`.

Target interface:
- exact taps exposed with target router/logits/tokens bitwise exact;
- small memory overhead and zero swap.

Exact B7 target verification:
- `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`;
- canonical q_len=1 attention per position, seven positions advanced layer-by-layer;
- each unique expert loaded once/layer and reused across assigned positions;
- hidden/KV/router/final logits/token decisions bitwise exact;
- 431,519,451 B useful expert bytes/verified position;
- 10.8152 s sequential -> 6.5430 s wavefront = 1.653x;
- swap delta 0; no expert leak.

## DFLASH-DRAFTER-PORT-001 — PASS

Report: `research/architecture/loom-dflash-drafter-port-001-result.md`.
Raw evidence: `results-local/research/dflash-drafter-port-001/20260824T113139Z/`.

MLX drafter component:
- 680,813,824 learned BF16 params;
- 1,361,627,648 learned weight bytes;
- 60 learned + 2 mapping tensors;
- no missing/extra learned weights.

Reference:
- separate NumPy translation of publisher source;
- publisher Torch/Speculators runtime unavailable locally.

Cross-implementation numerics:
- fusion max abs: 1.38e-05;
- draft-layer max abs: 0.0515–0.1442;
- draft-layer mean abs: 0.00768–0.02422;
- final-logit max/mean: 0.01956 / 0.003045;
- mapped draft-token decisions identical on the tested deterministic case;
- no NaN/Inf.

Memory:
- MLX resident 1,362,053,632 B;
- MLX peak 2,289,441,196 B;
- workspace 927,387,564 B;
- RSS peak 1,423,212,544 B;
- swap delta 0;
- memory PASS.

Interpretation: the MLX component port is accepted, but speculative integration remains blocked. Because the official publisher runtime is unavailable and intermediate cross-implementation errors are nontrivial, one deterministic case is insufficient to certify the MLX drafter as a stable proposal source.

## Exact next step — `LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001`

Do not connect drafter and target verifier yet.

Validate decision stability over real target states:
1. collect frozen real target tap sets from multiple prompts/positions using the proven target interface;
2. run the MLX drafter and independent NumPy publisher translation on exactly the same states;
3. exercise full autoregressive draft rollouts up to 7 proposals, including d2t/t2d mapping semantics;
4. require proposal-token parity at every draft position;
5. record top-1/top-2 margins and final-logit error distribution so apparent parity is not supported only by large accidental margins;
6. require deterministic rerun stability and no NaN/Inf;
7. measure standalone drafter wall and memory without target verification.

If proposal parity remains stable across the preregistered corpus, a first greedy end-to-end DFlash integration with the exact B7 wavefront verifier becomes justified. If decisions diverge, localize the earliest rollout/state mismatch before integration.

## Later order

1. drafter decision-stability corpus;
2. first greedy DFlash loop only if PASS;
3. measure real acceptance length, target verifications/output token, external expert bytes/accepted token and sustained tok/s;
4. capability/coding benchmark after practical speed improves;
5. context/stability;
6. behavioral decensoring validation before final promotion.
