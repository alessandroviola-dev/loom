# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — exact target verifier + decision-stable MLX DFlash drafter proven; first end-to-end speculative loop next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001_PASS`
Next core checkpoint: `LOOM_DFLASH_GREEDY_E2E_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while balancing memory, speed, capability and later behavioral-freedom validation.

Stable target anatomy and proven invariants live in `/AGENTS.md`. Pi uses compact work packages; ChatGPT owns Git/HANDOFF/ROADMAP.

## Established target/runtime

- Qwen3-30B-A3B external-expert execution is bitwise exact across all 48 layers.
- Shared resident backbone 819,015,680 B; routed bank external.
- Real greedy generation works on M1 8 GB.
- Expert-major disk access materially improves decode.
- 4-GiB raw RAM cache is rejected despite real ~80.9% reuse because it causes +2.41 GiB swap and slowdown.

## DFlash target side — COMPLETE

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Static:
- BF16 checkpoint ~1.2685 GiB;
- 5 draft layers;
- proposals=7;
- taps `[1,12,23,34,45]`.

Target interface:
- exact taps exposed with target router/logits/tokens bitwise exact;
- small memory overhead; swap delta 0.

Exact B7 verification:
- `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`;
- canonical q_len=1 attention per position;
- seven candidate positions advance layer-by-layer;
- each unique expert loaded once/layer and reused across assigned positions;
- hidden/KV/router/final logits/token decisions bitwise exact;
- 431,519,451 B useful expert bytes/verified position;
- 10.8152 s sequential -> 6.5430 s wavefront = 1.653x;
- swap delta 0; no expert leak.

## DFlash learned drafter — COMPONENT + DECISION STABILITY PASS

`LOOM_DFLASH_DRAFTER_PORT_001_PASS` proved complete MLX weight mapping and memory safety.

`LOOM_DFLASH_DRAFTER_DECISION_STABILITY_001_PASS` now validates the port across real target states.

Report: `research/architecture/loom-dflash-drafter-decision-stability-001-result.md`.
Raw evidence: `results-local/research/dflash-drafter-decision-stability-001/20260824T114723Z/`.

Corpus:
- 9 frozen real target-tap states;
- P1/P2/P3 at trace positions 1,16,32;
- seven-step autoregressive draft rollout per state.

Decision stability:
- 63 proposal decisions compared;
- 63/63 mapped token parity = 100%;
- mismatches 0;
- deterministic rerun PASS;
- no NaN/Inf.

Margins/errors:
- top1-top2 margin P50/P10/min 0.4271 / 0.04625 / 0.00510;
- final-logit max-abs P50/max 0.00904 / 0.01310;
- mean-abs P50/max 0.0009983 / 0.001386.

Standalone drafter cost:
- seven-proposal wall P50 0.08437 s, mean 0.09067 s.

Memory:
- MLX resident 1,362,053,640 B;
- MLX peak 2,305,009,460 B;
- workspace 942,955,820 B;
- RSS 1,449,148,416 B;
- swap delta 0;
- memory pressure PASS.

Interpretation: the MLX drafter is now sufficiently stable to serve as the proposal source for a first controlled greedy end-to-end DFlash checkpoint. This still does not establish acceptance length or end-to-end speedup.

## Exact next step — `LOOM_DFLASH_GREEDY_E2E_001`

Combine only already-proven components:
1. normal target prefill with exact taps;
2. MLX DFlash drafter proposes up to 7 mapped target tokens;
3. exact B7 wavefront target verifier evaluates the proposal block;
4. implement canonical greedy speculative acceptance/rejection semantics from the publisher/speculation contract;
5. compare generated target token sequence against ordinary greedy target generation on the same prompts;
6. measure accepted proposal lengths, verifier calls/output token, expert bytes/output token, combined wall/tok-s, MLX/RSS/swap and ownership.

No cache rescue, no quantization, no prefetch, no new storage optimization and no capability claims in this checkpoint.

Promotion requires exact target output parity and memory safety. Performance may PASS/CONDITIONAL independently depending on measured throughput.

## Later order

1. first greedy DFlash end-to-end loop;
2. if correct, longer sustained generation across multiple prompts;
3. optimize drafter/verifier/storage only from measured bottlenecks;
4. capability/coding benchmark;
5. context/stability;
6. behavioral decensoring validation before final promotion.
