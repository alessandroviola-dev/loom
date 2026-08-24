# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`
Strategic next: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`

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

## DFlash drafter — publisher-semantics parity PASS

The MLX port maps all 680,813,824 learned BF16 params and is standalone memory-safe.

The publisher anchor/block attention-mask bug discovered during acceptance diagnosis has been repaired and independently revalidated.

`LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`:
- independent publisher-semantics masked reference;
- explicit independent 8×13 mask assertion PASS;
- 9 frozen real target-tap states from P1/P2/P3 at positions 1/16/32;
- 63/63 mapped proposal-token decisions match across seven autoregressive proposal positions;
- deterministic rerun PASS;
- no NaN/Inf;
- no first mismatch;
- final-logit max-abs distribution max/mean 0.0166407 / 0.0109135;
- final-logit mean-abs distribution max/mean 0.00175031 / 0.00120281;
- MLX/reference top1-top2 mean margins 0.55770 / 0.55726;
- max absolute margin error 0.00708771.

Report:
`research/architecture/loom-dflash-masked-reference-parity-001-result.md`

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- 96 output tokens with committed target parity PASS;
- target KV/router/logit correctness PASS;
- acceptance 0/96;
- 3,098,293,248 useful external expert B/output token;
- control 0.7735 tok/s vs treatment 0.1544 tok/s;
- swap +737.43 MiB.

Do not optimize memory while acceptance remains zero.

## Acceptance alignment diagnosis — mask repaired, independent validation complete

`LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001_REPAIRED_PROBE_ZERO_ACCEPTANCE` found the missing publisher anchor/block mask in `Drafter.propose` and repaired only that semantic mismatch.

The repaired short probe remained 0/21 acceptance.

The subsequent masked-reference checkpoint has now established that the repaired MLX path matches independent publisher semantics on all 63 required proposal decisions.

Frozen-target accepted-prefix observation remained:
`[0,0,0,0,0,0,0,0,0]`
for both implementations.

Therefore:
- do not keep searching the already-validated mask/port path without new contrary evidence;
- do not yet conclude the drafter is incompatible with the current target;
- do not attribute any incompatibility specifically to 4-bit quantization.

## Next — target/drafter compatibility audit

Checkpoint: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`.

Phase A — target replay integrity gate:
1. use the same frozen target states/continuations;
2. reproduce the target continuation through the current target path;
3. require deterministic exact replay across all required decisions;
4. if replay drifts, stop and classify target replay drift before any drafter compatibility conclusion.

Phase B — compatibility characterization, only if replay passes:
1. score the validated masked DFlash proposals under exact target-prefix conditioning;
2. compare proposal token vs target top1;
3. record target rank and log-probability of each proposed token;
4. report top5/top10/top50 inclusion and target margins;
5. report exact accepted-prefix distribution;
6. pass the frozen target continuation through the same validation path as a control and require exact top1 recovery.

Restrictions:
- no drafter/target/weight/mapping changes;
- no threshold tuning;
- no memory/performance remediation;
- no full E2E rerun;
- no causal claim against 4-bit quantization.

Decision:
- replay FAIL => localize target replay drift first;
- replay PASS + proposals far from target => strong drafter/target incompatibility evidence;
- replay PASS + proposals near target => characterize the narrow mismatch before changing architecture;
- quantization-specific causality requires a later isolated control.

## After acceptance becomes useful

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
