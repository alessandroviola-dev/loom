# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001_NO_MATERIAL_TAP_DTYPE_EFFECT`
Strategic next: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.9.

## Stable DFlash chain

Still valid:
- target taps `[1,12,23,34,45]`;
- exact B7 wavefront verifier;
- complete 680,813,824-param BF16 drafter port;
- publisher mask repair;
- deterministic/finite 32k drafter forward;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Mapping / support — resolved

Correct mapping:
`target_id = draft_row + d2t[draft_row]`.

True support:
- 32,000 valid unique target IDs;
- frozen `50/63` representable, `13/63` unsupported;
- corrected exact top1 remains `0/63`.

Historical E2E `0/96` is contaminated by the old decode and is not current acceptance evidence.

## Directional compatibility

For 50 representable targets:
- rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`, top10 `11/50`, top50 `19/50`, top100 `26/50`;
- top1 `0/50`.

The candidate remains mismatched at top1 but carries meaningful target-directional signal.

## Closed / exonerated hypotheses

Temporal alignment:
- full preregistered `-7..+7` = `NO_SYSTEMATIC_TEMPORAL_SHIFT`.

MLX drafter port:
- full-32k authoritative parity PASS on 6 stratified states;
- decision-level outputs exact and vector differences immaterial.

Verifier provenance / tap interface:
- static `16/16` contract PASS;
- no demonstrated material revision/config/tokenizer/tap mismatch;
- historical revision/runtime provenance remains partly unpinned but is not causal evidence.

## Completed — tap transport BF16 sensitivity

`LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001` = `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Report:
`research/architecture/loom-dflash-tap-transport-bf16-sensitivity-001-result.md`

Evidence:
`results-local/research/dflash-tap-transport-bf16-sensitivity-001/20260825T105437Z/`

One-factor tap round-trip `float32 -> bfloat16 -> float32`:
- proposal changes `0/63`;
- logit rel-L2 `0.000671`, cosine `0.999999776`;
- correct-target mean rank `438.96 -> 438.72`;
- rank improved/unchanged/worsened `11/32/7`;
- no top-k boundary crossings;
- top5/top10/top50/top100 unchanged `8/11/19/26`;
- exact target matches remain `0/50`;
- all P1/P2/P3 proposal/top-k decisions unchanged.

Decision: tap transport dtype is closed as a useful rescue mechanism.

## BF16 target context

Pinned available BF16 target revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Prior P1_t01 Q4->BF16 intervention changed target hidden states materially, and those BF16 taps materially moved DFlash logits. But P1_t01 target `12050` is outside DFlash support, so it cannot determine whether BF16 target states recover correct proposals on representable targets.

Persistent BF16 cache ~33 GiB remains available.

## Next — representable BF16 target control preflight

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001`

Purpose:
Before any new expensive verifier execution, define and cost-bound the smallest causal test of verifier-state precision/distribution on representable targets.

Static plan:
1. deterministically select one lowest-baseline-rank representable state per P1/P2/P3;
2. derive minimal verifier prefix/state reproduction and shared work;
3. audit persistent BF16 cache integrity/coverage, dense and routed assets, current disk availability and resumability;
4. estimate cache hits/misses from retained Q4 routing traces only as a lower-quality planning estimate because BF16 routing may diverge;
5. ensure the future on-demand BF16 runner can enforce hard network/request limits and terminate safely;
6. preregister retention, hard abort gates and comparison metrics for the later causal pilot.

Later causal metrics must compare Q4 vs BF16 target states on the selected representable states:
- target tap drift;
- DFlash full-32k distribution movement;
- correct target-row rank;
- top5/top10/top50/top100 membership;
- exact target top1 proposal.

Decision after preflight:
- ready within cache -> authorize bounded pilot;
- bounded missing cache -> authorize only with explicit hard network cap;
- infeasible/ambiguous -> do not spend further DFlash compute without a new decision.

Restrictions for preflight:
- no target/BF16-target forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no performance optimization.

## Later order

1. `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001`;
2. if feasible, one bounded representable-state Q4-target vs BF16-target causal pilot;
3. if no useful recovery signal, explicitly reassess/terminate DFlash salvage;
4. corrected bounded E2E only after a real compatibility/acceptance signal exists;
5. return to LOOM's high-leverage 30B-on-8GB serving/I/O path when DFlash scientific salvage is exhausted.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only the active delta. Pi executes local work; ChatGPT owns scientific/Git state.