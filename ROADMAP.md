# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001_NO_MATERIAL_RECOVERY`
Strategic next: `LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`

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

Target identity audit:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Completed — P1_t01 BF16 vs Q4 control

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`

Under freeze-time MLX 0.31.2, changing only target weights Q4 -> pinned upstream BF16 produced:
- first router divergence layer 0, position 1;
- identical full-prefix router top-k layers `0/48`;
- tap relative-L2 `[1,12,23,34,45]` = `0.114863, 0.345792, 0.310635, 0.198639, 0.274675`;
- final hidden relative-L2 `0.270665`, cosine `0.964671`;
- final logits relative-L2 `0.336189`, cosine `0.957269`;
- Q4 top1 = BF16 top1 = `12050`;
- top-5 overlap `4/5`.

Conclusion: precision materially changes internal states but the single-state result remained `NOT_CAUSAL` for DFlash incompatibility.

## Persistent BF16 infrastructure

External research root:
`<external-archive>/`

Persistent cache now retains:
- 3,470 BF16 routed expert entries (~31 GiB);
- dense BF16 cache (~2.9 GiB);
- ~33 GiB total.

Initial cache build transferred `32,747,028,480 B` from network. A complete subsequent P1_t01 BF16 re-extraction used 3,470 HDD hits, 0 network bytes and 0 retries.

Exact BF16 P1_t01 taps `[5,43,2048]`, hashes/provenance and final-anchor logits are now retained externally.

`AGENTS.md` v3.0 establishes a mandatory retention plan for expensive runs so costly intermediate artifacts are not left transient.

## Completed — BF16 tap drafter probe

Checkpoint:
`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001`

Classification:
`NO_MATERIAL_RECOVERY`

Report:
`research/architecture/loom-dflash-bf16-tap-drafter-probe-001-result.md`

One-factor result on `P1_t01`:

Q4 taps:
- drafter proposal `1778`;
- BF16-target rank `41641`;
- top5/top10/top50 false.

BF16 taps:
- drafter proposal `1778`;
- BF16-target rank `41641`;
- top5/top10/top50 false.

Drafter distribution did move materially:
- max abs `2.72215`;
- mean abs `0.343385`;
- RMSE `0.432349`;
- relative-L2 `0.215100`;
- cosine `0.977013`.

Therefore BF16/Q4 tap precision affects DFlash internal logits but is not sufficient to recover proposal token, target rank, or top-k compatibility on P1_t01.

Critical new observation:
- target token `12050` is absent from the drafter mapped ~32k output support;
- exact target-token proposal is structurally unavailable on P1_t01 regardless of Q4 vs BF16 taps;
- coverage across all 63 frozen target tokens is still unknown.

## Next — output support coverage audit

Checkpoint:
`LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`

Purpose:
Determine whether the mapped drafter vocabulary/support structurally prevents correct proposals on a meaningful fraction of the frozen target continuation.

Static audit only:
1. recover the exact already-validated drafter-output -> target-token mapping and its provenance;
2. verify cardinality, uniqueness and valid target-vocab IDs;
3. test all 63 frozen target next tokens for membership in mapped support;
4. report representable/63 and unsupported/63;
5. enumerate unsupported state IDs/tokens;
6. partition existing proposal incompatibility by support membership;
7. do not alter mapping.

Decision:
- large unsupported fraction -> mapped output support becomes a major structural DFlash blocker and must be resolved/understood before further expensive work;
- most/all target tokens representable -> P1_t01 is local/minority and next investigation returns to drafter training/interface/distribution mismatch.

Restrictions:
- no BF16 target forward;
- no model download;
- no DFlash E2E;
- no retraining/remapping;
- no acceptance/memory/performance optimization;
- no broad scientific treatment beyond static support analysis.

## Later order

1. `LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`;
2. classify how much of zero acceptance is structurally explained by output support;
3. investigate remaining training/interface/distribution mismatch if needed;
4. salvage DFlash only if a supported mechanism exists;
5. otherwise return to the next high-leverage LOOM architecture/I/O branch toward practical 30B-on-8GB serving.

## Token-efficient Pi workflow

Root `/AGENTS.md` is persistent context. Pi prompts carry only the active delta. Pi executes local work; ChatGPT owns Git/HANDOFF/ROADMAP and scientific checkpoint administration.
