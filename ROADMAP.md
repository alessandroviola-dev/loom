# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_ENGINE_OR_DATA_BLOCKED`
Strategic next: `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001`

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

`LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`:
- repaired MLX drafter matches an independently implemented publisher-semantics masked reference;
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

Frozen-prefix accepted-prefix observation remained `[0,0,0,0,0,0,0,0,0]` in both paths.

The corrected MLX drafter is therefore validated against independent publisher semantics. This does not yet establish target incompatibility and does not identify 4-bit quantization as causal.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- 96 output tokens with committed target parity PASS;
- target KV/router/logit correctness PASS;
- acceptance 0/96;
- 3,098,293,248 useful external expert B/output token;
- control 0.7735 tok/s vs treatment 0.1544 tok/s;
- swap +737.43 MiB.

Do not optimize memory while acceptance remains zero.

## Target/drafter compatibility audit — BLOCKED on immutable continuation data

`LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001` was opened with target replay integrity as Gate A.

Result:
`ENGINE_OR_DATA_BLOCKED`.

Available immutable frozen target decisions:
- 45/63.

Missing:
- six continuation tokens for `P1_t32`;
- six continuation tokens for `P2_t32`;
- six continuation tokens for `P3_t32`.

Target replay/control and all compatibility statistics were therefore not run. This checkpoint supplies no compatibility conclusion.

Report:
`research/architecture/loom-dflash-target-compatibility-audit-001-result.md`

Evidence:
`results-local/research/dflash-target-compatibility-audit-001/20260824T144106Z/`

Do not backfill the missing historical decisions using the same current replay/scoring implementation. That would invalidate the intended replay-integrity proof by circular construction.

## Next — target continuation freeze

Checkpoint: `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001`.

Phase A — provenance recovery:
1. inspect only relevant existing local DFlash evidence/corpora;
2. search for a pre-existing independently captured seven-token target continuation for the three `*_t32` states;
3. accept recovered data only if state identity and provenance are unambiguous.

Phase B — rebaseline only if recovery fails:
1. use the same nine frozen prefixes/states;
2. use an independent already-validated target oracle path, not the later compatibility replay/scoring path;
3. generate seven greedy target continuation tokens per state;
4. require exact parity with all 45 already-available historical frozen decisions (`45/45`);
5. only after that overlap gate passes may the 18 missing decisions be accepted as new reference data;
6. require deterministic rerun and finite outputs;
7. freeze exact model/prefix/oracle provenance;
8. write and SHA-256 hash the complete 63-token reference artifact;
9. label newly generated decisions explicitly as `REBASELINED_REFERENCE`, not historical frozen data.

Gate:
- recovery with valid provenance OR independent-oracle rebaseline PASS;
- 63/63 complete continuation decisions;
- historical overlap parity 45/45 PASS;
- deterministic rerun PASS;
- content hash recorded.

Only after this checkpoint passes should `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001` be rerun.

Restrictions:
- no drafter/target weights or token-map changes;
- no acceptance-rule/threshold tuning;
- no memory/performance remediation;
- no full E2E rerun;
- no causal claim against 4-bit quantization.

## After compatibility is characterized

1. isolate compatibility cause only if needed;
2. only after nonzero useful acceptance, combined target+drafter memory remediation;
3. full E2E rerun;
4. measure accepted tokens/verifier, expert bytes/output token and sustained tok/s;
5. optimize only the dominant measured cost;
6. capability/coding benchmark;
7. context/stability;
8. if still insufficient: route prediction/prefetch, finer sparsity or LOOM-native co-design;
9. behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only active delta, exact inputs, gates, evidence and concise return fields. Pi performs local execution/tests/evidence; ChatGPT owns Git/HANDOFF/ROADMAP.
