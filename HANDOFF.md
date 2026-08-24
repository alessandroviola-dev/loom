# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — DFlash target continuation corpus complete and hash-frozen; target/drafter compatibility audit ready to resume
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`
Next core checkpoint: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while balancing memory, speed, capability and later behavioral-freedom validation.

Stable target anatomy and long-lived invariants live in `/AGENTS.md`. Pi uses compact work packages; ChatGPT owns Git/HANDOFF/ROADMAP.

## Established target/runtime

- Qwen3-30B-A3B external-expert execution is bitwise exact across all 48 layers.
- Shared resident backbone 819,015,680 B; routed bank external.
- Real greedy generation works on M1 8 GB.
- Expert-major disk layout materially improves decode.
- 4-GiB raw RAM cache is rejected: ~80.9% hit but +2.41 GiB swap and severe slowdown.

## DFlash prerequisites already proven

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Target side:
- exact taps `[1,12,23,34,45]` exposed with router/logit/token bitwise parity;
- exact B7 wavefront verifier PASS;
- canonical q_len=1 attention per position;
- unique expert reuse per layer;
- B7 hidden/KV/router/logits/token decisions bitwise exact;
- 431,519,451 B useful expert bytes/verified position;
- 10.8152 s sequential -> 6.5430 s wavefront = 1.653x;
- zero swap/expert leak.

Drafter side:
- MLX maps all 680,813,824 learned BF16 params;
- standalone component memory-safe;
- publisher anchor/block mask repaired and independently revalidated;
- corrected MLX/reference masked parity 63/63 proposal decisions.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- 96 committed output tokens with ordinary-greedy parity PASS;
- target KV/router/logit parity bitwise PASS;
- deterministic rerun PASS;
- zero expert leak;
- acceptance 0/96 cycles;
- verifier calls/output token 1.96875;
- useful external expert bytes/output token 3,098,293,248 B;
- control 0.7735 tok/s;
- DFlash 0.1544 tok/s = 0.1996x;
- swap delta +737.43 MiB.

Acceptance remains the first blocker; memory remediation stays deferred.

## Mask repair and independent reference — PASS

`LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001_REPAIRED_PROBE_ZERO_ACCEPTANCE` found and repaired the missing publisher anchor/block attention mask in `Drafter.propose`.

`LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS` then established:
- explicit independent 8×13 mask assertion PASS;
- 9 frozen P1/P2/P3 states at positions 1/16/32;
- 63/63 mapped proposal decisions match;
- deterministic rerun PASS;
- no NaN/Inf;
- frozen-prefix acceptance observation `[0,0,0,0,0,0,0,0,0]` in both MLX and independent reference.

Therefore the corrected MLX drafter implementation is no longer the leading explanation for zero acceptance. Target compatibility remains unproven, and 4-bit causality is not established.

## First target-compatibility attempt — BLOCKED

`LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001` initially stopped as `ENGINE_OR_DATA_BLOCKED` before Gate A because only 45/63 immutable frozen target continuation decisions existed.

The missing 18 decisions were six tokens each for `P1_t32`, `P2_t32`, and `P3_t32`.

No target replay/control or compatibility statistics were run in that attempt.

Report:
`research/architecture/loom-dflash-target-compatibility-audit-001-result.md`

Evidence:
`results-local/research/dflash-target-compatibility-audit-001/20260824T144106Z/`

## TARGET-CONTINUATION-FREEZE-001 — PASS

Classification:
`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`

Report:
`research/architecture/loom-dflash-target-continuation-freeze-001-result.md`

Historical recovery:
`NOT_RECOVERED_INCOMPLETE_P1_P2_P3_T32`

A complete reference was therefore generated through an independent already-validated target oracle, not through the compatibility replay/scoring path.

Baseline type:
`REBASELINED_REFERENCE`

Hard overlap gate:
- 45 historical decisions available;
- independent oracle parity 45/45;
- first mismatch none.

Complete frozen corpus:
- same 9 exact frozen states;
- 63/63 continuation decisions;
- 45 historical decisions preserved;
- 18 new decisions explicitly labeled `REBASELINED_REFERENCE`, not historical observations;
- deterministic rerun PASS;
- no NaN/Inf.

Canonical artifact SHA-256:
`0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`

Evidence:
`results-local/research/dflash-target-continuation-freeze-001/20260824T145202Z/`

Provenance:
`results-local/research/dflash-target-continuation-freeze-001/20260824T145202Z/provenance.json`

The data/provenance blocker is now removed.

## Exact next step — resume `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`

Do not rerun full E2E and do not optimize memory/performance.

Gate A:
1. verify the canonical frozen-reference SHA-256;
2. replay the current target against all 63 frozen continuation decisions;
3. require exact 63/63 parity;
4. deterministic rerun PASS;
5. no NaN/Inf.

Validation control:
- pass the frozen target continuation through the same scoring/validation path used for proposal analysis;
- require target-top1 recovery 63/63.

If replay or validation control fails, STOP before drafter compatibility interpretation.

Only if both pass, score the validated masked DFlash proposals under exact target-prefix conditioning and report:
- proposal-vs-target top1 parity;
- target rank of each proposal;
- proposal log-probability;
- top5/top10/top50 inclusion;
- target top1/top2 margins;
- accepted-prefix distribution across all 9 states.

Do not change target, drafter, weights, mappings, acceptance rules or thresholds. Do not attribute any incompatibility specifically to 4-bit quantization without a later isolated control.

## Later order

1. complete target/drafter compatibility audit;
2. isolate compatibility cause only if needed;
3. only after nonzero useful acceptance, combined-runtime memory remediation;
4. rerun full E2E economics;
5. capability/coding benchmark once practical speed improves;
6. context/stability;
7. behavioral decensoring validation before final promotion.
