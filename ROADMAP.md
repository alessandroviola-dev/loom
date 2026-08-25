# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001_SUPPORT_COVERAGE_MAJOR_BLOCKER`
Strategic next: `LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical long-lived context is in `/AGENTS.md`.

## Proven DFlash chain

- target tap interface `[1,12,23,34,45]` established;
- exact B7 wavefront verifier;
- complete MLX drafter port;
- publisher anchor/block mask repaired;
- corrected publisher-reference proposal parity 63/63.

First E2E:
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Memory/performance optimization remains deferred while DFlash compatibility is unresolved.

## Frozen compatibility baseline

Frozen target continuation:
- historical overlap 45/45;
- complete 63/63 target token reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit:
- target replay/control 63/63 PASS;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal ranks min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

Target identity: `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Completed — BF16 precision branch

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`:
- substantial Q4/BF16 hidden/router/logit drift;
- Q4 top1 = BF16 top1 = `12050`;
- result remained `NOT_CAUSAL`.

`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001_NO_MATERIAL_RECOVERY`:
- Q4-tap proposal `1778`, BF16-target rank `41641`;
- BF16-tap proposal still `1778`, rank still `41641`;
- drafter logits moved (relative-L2 `0.215100`, cosine `0.977013`) without proposal/top-k recovery.

Conclusion: target precision materially affects DFlash internals but is not sufficient to explain/repair P1_t01 incompatibility.

Persistent BF16 infrastructure:
- external root `<external-archive>/`;
- ~33 GiB retained BF16 cache;
- exact P1_t01 BF16 taps/logits retained;
- subsequent full BF16 re-extraction used HDD cache with 0 network bytes.

## Completed — output support coverage audit

Checkpoint:
`LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`

Classification:
`SUPPORT_COVERAGE_MAJOR_BLOCKER`

Report:
`research/architecture/loom-dflash-output-support-coverage-audit-001-result.md`

Evidence:
`results-local/research/dflash-output-support-coverage-audit-001/20260825T090327Z/`

Static mapping facts:
- mapping `d2t`: drafter output index -> target token ID;
- output rows: `32,000`;
- target vocabulary: `151,936`;
- unique mapped target-token support: `17,018`;
- duplicate entries beyond unique support: `14,982`;
- duplicated target IDs: `6,098`;
- invalid/out-of-vocab IDs: `0`.

Frozen 63-state coverage:
- representable `30/63` = `47.62%`;
- structurally unsupported `33/63` = `52.38%`;
- representable but wrong `30/63`;
- target matches `0/63`;
- P1_t01 target `12050` unsupported.

Implications:
- exact proposal is structurally impossible on 33 states through current mapped support;
- support coverage is therefore a major blocker;
- it is not the only incompatibility because every one of the 30 representable states is also wrong;
- 32,000 rows collapsing to 17,018 unique target IDs is a high-leverage structural observation, but not yet established as erroneous.

## Next — output mapping semantics audit

Checkpoint:
`LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001`

Purpose:
Determine whether the observed many-to-one `d2t` mapping is exactly intended by the publisher's DFlash/tokenizer interface or is a local conversion/interpretation defect.

Static audit:
1. recover authoritative publisher `d2t` / `t2d` artifacts or generation logic from already available local/frozen provenance;
2. verify publisher/local mapping semantics and exact equality where possible;
3. quantify collision multiplicities and inspect tokenizer-equivalent, special, byte/fallback cases;
4. establish authoritative unique target support cardinality;
5. no mapping modification during the audit.

Decision:
- publisher-intended 17,018 unique support -> coverage blocker intrinsic to candidate/interface; together with 30 representable-but-wrong states, DFlash salvage would require substantive model/output-head changes, so compare that cost against returning to LOOM's practical 30B-on-8GB path;
- local semantic/conversion mismatch -> repair mapping mechanically, re-prove publisher parity, rerun cheap support coverage before any E2E.

Restrictions:
- static/local evidence first;
- no BF16 forward;
- no target generation;
- no DFlash E2E;
- no model download unless a precise missing authoritative artifact is separately justified;
- no performance/memory optimization;
- no speculative mapping repair inside the audit.

## Later order

1. `LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001`;
2. if local mapping defect, repair and re-audit support cheaply;
3. if publisher-intended blocker, make an explicit DFlash salvage-vs-abandon decision;
4. investigate representable-but-wrong mechanism only if DFlash remains worth salvaging;
5. otherwise return to the next high-leverage LOOM architecture/I/O branch toward practical 30B-on-8GB serving.

## Token-efficient Pi workflow

Root `/AGENTS.md` is persistent context. Pi prompts carry only the active delta. Pi executes local work; ChatGPT owns Git/HANDOFF/ROADMAP and scientific checkpoint administration.
