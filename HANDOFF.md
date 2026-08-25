# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — output-support coverage audit COMPLETE; 33/63 frozen target tokens structurally unsupported, 30/63 representable but still wrong; next verify whether the 32k->17,018 many-to-one output mapping is publisher-intended or a local mapping-semantic defect
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001_SUPPORT_COVERAGE_MAJOR_BLOCKER`
Next core checkpoint: `LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while preserving correctness, bounded memory and reproducible evidence.

Stable context lives in `/AGENTS.md`. Pi executes compact local WPs; ChatGPT owns Git/HANDOFF/ROADMAP and scientific checkpoint administration.

## Stable DFlash chain

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Publisher target: `Qwen/Qwen3-30B-A3B`
Target taps: `[1,12,23,34,45]`.

Validated:
- target tap interface;
- exact B7 wavefront verifier;
- complete MLX drafter port;
- publisher anchor/block mask repaired;
- corrected publisher-reference proposal parity 63/63.

First E2E remains rejected:
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Frozen continuation:
- historical overlap 45/45;
- complete 63/63 target reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility baseline:
- target replay/control 63/63;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal target rank min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- accepted prefixes zero;
- `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

Target identity audit: `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## BF16 branch completed

Pinned upstream BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Freeze-time runtime:
`results-local/mlx/venv-mlx-lm-0.31.3` / MLX 0.31.2.

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS` measured substantial Q4/BF16 internal drift but identical top1 `12050`:
- first router divergence layer 0 position 1;
- router full-prefix identical layers 0/48;
- tap rel-L2 `0.114863, 0.345792, 0.310635, 0.198639, 0.274675`;
- final hidden rel-L2 `0.270665`, cosine `0.964671`;
- final logits rel-L2 `0.336189`, cosine `0.957269`.

Persistent external BF16 cache now retains ~33 GiB:
- 3,470 routed expert entries ~31 GiB;
- dense ~2.9 GiB;
- exact P1_t01 BF16 taps `[5,43,2048]` and final-anchor logits retained;
- verified full re-extraction used 3,470 HDD hits and 0 network bytes.

External root:
`<external-archive>/`

`AGENTS.md` v3.1 retains the mandatory expensive-run retention rule.

## BF16 tap drafter probe — COMPLETE

`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001` = `NO_MATERIAL_RECOVERY`.

Q4 taps:
- proposal `1778`;
- BF16-target rank `41641`;
- top5/top10/top50 false.

BF16 taps:
- proposal `1778`;
- BF16-target rank `41641`;
- top5/top10/top50 false.

Drafter logits moved materially (relative-L2 `0.215100`, cosine `0.977013`) but proposal/rank did not recover. Simple tap-precision drift is not sufficient to repair P1_t01 incompatibility.

Critical observation from that probe: target `12050` is absent from mapped drafter support.

## Output support coverage audit — COMPLETE

Checkpoint:
`LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`

Classification:
`SUPPORT_COVERAGE_MAJOR_BLOCKER`

Report:
`research/architecture/loom-dflash-output-support-coverage-audit-001-result.md`

Evidence:
`results-local/research/dflash-output-support-coverage-audit-001/20260825T090327Z/`

Mapping integrity/provenance: PASS.

Validated mapping:
- direction: `d2t`, drafter output index -> target token ID;
- drafter rows: `32,000`;
- target vocab: `151,936`;
- unique target support: `17,018`;
- invalid/out-of-vocab IDs: `0`;
- duplicate entries beyond unique support: `14,982`;
- duplicated target IDs: `6,098`.

Frozen 63 states:
- representable: `30/63` (`47.62%`);
- unsupported / structurally unrepresentable: `33/63` (`52.38%`);
- representable but wrong: `30/63`;
- target matches: `0/63`;
- P1_t01 target `12050`: unsupported.

Scientific interpretation:
- support coverage is a major structural blocker and makes exact target proposal impossible on more than half the corpus;
- support coverage cannot explain the full 0/63 failure because all 30 representable states are still wrong;
- at least one additional incompatibility mechanism therefore exists;
- the large 32,000 -> 17,018 many-to-one structure is measured but is not yet declared a bug.

## Exact next step

Checkpoint:
`LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001`

Goal:
Determine whether the many-to-one mapping/collision structure is exactly publisher-intended or a local conversion/interpretation defect before spending more work on DFlash.

Static audit only:
1. locate authoritative publisher `d2t`/`t2d` mapping artifacts or generation logic already present in local/frozen provenance;
2. compare publisher vs local semantics and arrays bit-for-bit where possible;
3. characterize collision multiplicities and tokenizer-equivalent/special/byte/fallback cases;
4. establish whether effective support really is 17,018 unique target IDs under publisher semantics;
5. do not alter mapping in the audit.

Decision:
- publisher-intended -> structural coverage blocker is intrinsic; combined with 30 representable-but-wrong states, DFlash likely requires substantive model/output-head work and should be reconsidered against LOOM's main 30B-on-8GB objective;
- local mismatch -> repair mapping only, re-prove publisher parity, rerun cheap support coverage, still no E2E until supported.

Restrictions:
- no BF16 forward;
- no target generation;
- no model download unless an exact missing authoritative artifact is explicitly identified and separately authorized;
- no DFlash E2E;
- no mapping modification in this audit;
- no performance/memory optimization.
