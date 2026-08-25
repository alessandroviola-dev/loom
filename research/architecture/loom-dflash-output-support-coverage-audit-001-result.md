# LOOM DFlash Output Support Coverage Audit 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`
Classification: `SUPPORT_COVERAGE_MAJOR_BLOCKER`
Gate: `COMPLETE`

## Purpose

Statically audit the already validated DFlash drafter output mapping against the complete frozen 63-state target-next-token reference. The goal is to separate proposal failures that are structurally impossible because the exact target token is absent from mapped drafter support from failures that occur even though the exact target token is representable.

No BF16 forward, Q4 target forward, DFlash proposal rerun, network download, or E2E decoding was required.

## Mapping provenance / integrity

Mapping provenance and semantics: PASS.

Validated interpretation:
- mapping direction: drafter output index -> target token ID (`d2t`);
- drafter output rows: `32,000`;
- target vocabulary size: `151,936`;
- unique mapped target-token support cardinality: `17,018`;
- invalid / out-of-vocabulary mapped IDs: `0`.

Collision structure:
- duplicate mapping entries beyond first unique occurrences: `14,982`;
- duplicated target IDs: `6,098`.

Therefore the 32,000 drafter output rows cover only 17,018 unique target token IDs. This observation is measured but is not yet classified as a mapping bug: a dedicated publisher-semantics audit is required to determine whether the many-to-one structure is intended by the published DFlash mapping or introduced by conversion/interpretation.

## Frozen 63-state coverage

Frozen target continuation reference:
- exactly `63/63` target next tokens;
- reference SHA-256: `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Static support membership:
- representable: `30/63` = `47.62%`;
- unsupported: `33/63` = `52.38%`.

Every unsupported state is structurally incapable of exact next-token proposal through the current mapped drafter output support.

`P1_t01` verification:
- target token: `12050`;
- mapped support membership: unsupported.

## Join with existing compatibility evidence

Existing frozen compatibility result remains:
- drafter/target top1 matches: `0/63`.

Partition:
- `STRUCTURALLY_UNREPRESENTABLE`: `33/63`;
- `REPRESENTABLE_BUT_WRONG`: `30/63`;
- `TARGET_MATCH`: `0/63`.

Thus output support structurally explains why exact target-token proposal was impossible for 33 states, but it cannot explain the remaining 30 failures: every representable state was still proposed incorrectly.

This proves that at least one additional incompatibility mechanism exists beyond output-support coverage.

## Interpretation

Measured facts:
1. The validated drafter output mapping has 32,000 rows but only 17,018 unique target-token IDs.
2. `33/63` frozen target next tokens are absent from that support.
3. `30/63` target next tokens are present in support, but the validated DFlash proposals are still wrong.
4. No frozen state is a target match.
5. Mapping IDs are all within the target vocabulary; the structural concern is coverage/collision, not invalid IDs.

Classification:
`SUPPORT_COVERAGE_MAJOR_BLOCKER`.

Scientific conclusion:
- mapped output support is a major structural blocker for this DFlash candidate on the frozen target continuation;
- it accounts for structural impossibility on more than half the frozen states;
- it is not sufficient to explain the full `0/63` compatibility failure because all 30 representable states remain wrong;
- the large many-to-one mapping/collision structure must be verified against publisher semantics before deciding whether the blocker is intrinsic to the published drafter or a repairable mapping/conversion issue.

No causal claim is made about the representable-but-wrong subset from this audit alone.

## Evidence

Local:
`results-local/research/dflash-output-support-coverage-audit-001/20260825T090327Z/`

Expected evidence:
- `provenance.json`;
- `mapping-audit.json`;
- `state-support.csv` or equivalent JSON;
- `compatibility-partition.json`;
- `summary.json`.

## Next checkpoint

`LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001`

Goal: determine whether the observed `32,000 -> 17,018` unique-target support and the 14,982 duplicate mapping entries are exactly intended by the published DFlash drafter/tokenizer mapping or are introduced by the local conversion/interpretation path.

Required static questions:
- recover the authoritative publisher mapping artifacts / generation semantics already available locally or from frozen provenance;
- compare publisher `d2t` and `t2d` semantics against the local validated mapping bit-for-bit where possible;
- establish whether multiple drafter output rows mapping to the same target token is intended;
- audit collision multiplicities and treatment of special/byte/fallback/tokenizer-equivalent entries;
- determine whether the effective unique support is genuinely 17,018 target IDs under publisher semantics;
- do not modify the mapping during the audit.

Decision:
- publisher-intended many-to-one support -> coverage blocker is intrinsic to this DFlash candidate/target interface; with 33 structurally unsupported and 30 representable-but-wrong states, DFlash salvage requires substantive model/output-head changes and should be reconsidered against LOOM's main practical 30B-on-8GB objective;
- local conversion/interpretation mismatch -> repair only the mapping mechanism, prove publisher parity again, then rerun the cheap support audit before any E2E work.

This next audit should remain static/cheap and must not trigger BF16 forwards, target generation, or model downloads unless an exact missing publisher artifact is explicitly identified first.
