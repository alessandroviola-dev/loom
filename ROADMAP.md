# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`
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

## DFlash drafter — publisher-semantics parity PASS

`LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`:
- repaired MLX drafter matches an independently implemented publisher-semantics masked reference;
- explicit independent 8×13 mask assertion PASS;
- 9 frozen real target-tap states from P1/P2/P3 at positions 1/16/32;
- 63/63 mapped proposal-token decisions match across seven autoregressive proposal positions;
- deterministic rerun PASS;
- no NaN/Inf.

Frozen-prefix acceptance remained `[0,0,0,0,0,0,0,0,0]` in both MLX and independent reference.

The corrected MLX drafter is therefore validated against independent publisher semantics. This does not establish target incompatibility and does not identify 4-bit quantization as causal.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- 96 output tokens with committed target parity PASS;
- target KV/router/logit correctness PASS;
- acceptance 0/96;
- 3,098,293,248 useful external expert B/output token;
- control 0.7735 tok/s vs treatment 0.1544 tok/s;
- swap +737.43 MiB.

Do not optimize memory while acceptance remains zero.

## Target/drafter compatibility audit — initial attempt BLOCKED

The first `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001` attempt stopped as `ENGINE_OR_DATA_BLOCKED` before target replay because only 45/63 immutable target continuation decisions existed.

No compatibility conclusion was produced.

## Target continuation freeze — PASS

`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS` removed the data/provenance blocker.

Historical recovery:
`NOT_RECOVERED_INCOMPLETE_P1_P2_P3_T32`

A new complete `REBASELINED_REFERENCE` was generated with an independent already-validated target oracle, not the later compatibility replay/scoring path.

Hard overlap validation:
- historical decisions available: 45;
- independent oracle parity: 45/45;
- first mismatch: none.

Complete reference:
- 9 exact frozen states;
- 63/63 target continuation decisions;
- 45 historical decisions retained;
- 18 previously missing decisions explicitly labeled `REBASELINED_REFERENCE`;
- deterministic rerun PASS;
- no NaN/Inf.

Canonical reference SHA-256:
`0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`

Report:
`research/architecture/loom-dflash-target-continuation-freeze-001-result.md`

Evidence:
`results-local/research/dflash-target-continuation-freeze-001/20260824T145202Z/`

The frozen-reference precondition for the compatibility audit is now satisfied.

## Next — resume target/drafter compatibility audit

Checkpoint:
`LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`

Gate A — target replay integrity:
1. verify the frozen artifact SHA-256;
2. replay the current target against all 63 frozen continuation decisions;
3. require exact 63/63 parity;
4. deterministic rerun PASS;
5. no NaN/Inf.

Validation control:
1. pass the frozen target continuation through the same scoring path used for proposal analysis;
2. require exact target-top1 recovery 63/63.

If either gate fails, stop before interpreting drafter compatibility.

Only if both pass:
1. score validated masked DFlash proposals under exact target-prefix conditioning;
2. report proposal-vs-target top1 parity;
3. record target rank and log-probability of each proposed token;
4. report top5/top10/top50 hit rates;
5. report target top1/top2 margins;
6. report exact accepted-prefix distribution across all 9 states.

Restrictions:
- no target/drafter/weight/mapping changes;
- no acceptance-rule or threshold tuning;
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
