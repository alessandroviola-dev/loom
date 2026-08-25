# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — BF16 tap intervention completed with `NO_MATERIAL_RECOVERY`; precision changes drafter logits but not proposal/rank; P1_t01 target token is outside mapped drafter output support; next audit support coverage across all frozen states
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001_NO_MATERIAL_RECOVERY`
Next core checkpoint: `LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while preserving correctness, bounded memory and reproducible evidence.

Stable context lives in `/AGENTS.md`. Pi executes compact local WPs; ChatGPT owns Git/HANDOFF/ROADMAP and scientific checkpoint administration.

## DFlash validated chain

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Publisher target: `Qwen/Qwen3-30B-A3B`
Required target taps: `[1,12,23,34,45]`.

Proven:
- target tap interface;
- exact B7 wavefront target verifier;
- complete MLX drafter port;
- publisher anchor/block mask repaired;
- corrected publisher-reference proposal parity 63/63.

First E2E remains rejected:
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Frozen target continuation:
- historical overlap 45/45;
- complete 63/63 token reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit:
- target replay/control 63/63;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal target rank min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

Target identity:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## P1_t01 BF16 vs Q4 control — COMPLETE

Checkpoint:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`

Runtime:
`results-local/mlx/venv-mlx-lm-0.31.3` / MLX 0.31.2.

Pinned upstream BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Frozen P1_t01:
- 43 tokens;
- prefix SHA-256 `7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f`;
- anchor position 42/token 271;
- taps `[1,12,23,34,45]`.

Measured Q4 vs BF16:
- first router divergence layer 0, position 1;
- identical full-prefix router top-k layers `0/48`;
- tap relative-L2 `0.114863, 0.345792, 0.310635, 0.198639, 0.274675`;
- final hidden relative-L2 `0.270665`, cosine `0.964671`;
- final logits relative-L2 `0.336189`, cosine `0.957269`;
- Q4 top1 = BF16 top1 = `12050`;
- top-5 overlap `4/5`.

Conclusion remained `NOT_CAUSAL`: precision materially changes internal target distributions, but one state did not establish that quantization caused DFlash incompatibility.

## Persistent BF16 research cache

The first BF16 control did not retain raw taps, which was identified as a research-process defect. This has been corrected.

External storage root:
`<external-archive>/`

Persistent BF16 cache:
`<external-archive>/bf16-cache/`

Final cache:
- 3,470 routed expert entries;
- ~31 GiB routed experts;
- ~2.9 GiB dense;
- ~33 GiB total.

Initial persistent cache build:
- 3,470 misses/new expert entries;
- `32,747,028,480 B` expert network payload.

Final BF16 re-extraction:
- 3,470 HDD hits;
- 0 network bytes;
- 0 retries.

Retained exact artifacts include the five float32 BF16 taps `[5,43,2048]`, hashes/provenance and final-anchor BF16 target logits.

`AGENTS.md` v3.0 now requires a retention plan before expensive runs so costly/transient artifacts are identified and persisted before execution.

## BF16 tap drafter probe — COMPLETE

Checkpoint:
`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001`

Classification:
`NO_MATERIAL_RECOVERY`

Report:
`research/architecture/loom-dflash-bf16-tap-drafter-probe-001-result.md`

Evidence:
- local: `results-local/research/dflash-bf16-tap-drafter-probe-001/20260825T084409Z/`;
- external: `<external-archive>/artifacts/dflash-bf16-tap-drafter-probe-001/20260825T084409Z/`.

Re-extraction parity:
- exact retained taps finite/hash-valid;
- BF16 target top1 `12050`;
- deterministic/finite/no-leak PASS;
- tap/final-hidden/final-logit/margin/top5 metrics reproduce completed BF16 control.

Q4-tap baseline:
- proposal `1778`;
- proposal BF16-target rank `41641`;
- top5/top10/top50 false.

BF16-tap treatment:
- proposal `1778`;
- proposal BF16-target rank `41641`;
- top5/top10/top50 false.

Drafter-logit Q4 -> BF16 tap movement:
- max abs `2.72215`;
- mean abs `0.343385`;
- RMSE `0.432349`;
- relative-L2 `0.215100`;
- cosine `0.977013`.

Both conditions are deterministic and finite; mask is bitwise equal; only tap hashes differ.

Interpretation:
- target precision affects drafter logits materially;
- it is not sufficient to change the top proposal or improve BF16-target rank/top-k compatibility on P1_t01;
- simple target-tap precision drift is therefore not sufficient to repair this incompatibility.

Critical structural observation:
- target token `12050` is absent from the drafter mapped ~32k output support;
- exact target-token proposal is structurally unavailable on P1_t01 through the current mapping, independently of Q4/BF16 tap values;
- prevalence across the other 62 frozen states is unknown.

## Exact next step

Checkpoint:
`LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`

Goal:
Audit the validated DFlash output mapping against the complete frozen 63-state target-next-token reference before spending more compute/network on BF16 or E2E work.

Required static checks:
1. identify the exact validated drafter-output -> target-vocab mapping artifact/code and prove provenance;
2. prove mapping cardinality/uniqueness/valid target token IDs;
3. for every frozen state, determine whether its target next token belongs to drafter mapped support;
4. report representable count/63 and unsupported count/63;
5. list every unsupported state/token;
6. join with existing compatibility evidence and partition 0/63 failures by representable vs unsupported target token;
7. no model execution required except tiny static parsing if necessary.

Decision:
- large unsupported fraction -> output-support coverage is a major structural blocker and must be understood before DFlash salvage;
- most/all representable -> P1_t01 support absence is local/minority and the next hypothesis returns to drafter training/interface/distribution compatibility.

Restrictions:
- no BF16 forward;
- no network model downloads;
- no DFlash E2E;
- no retraining/remapping;
- no memory/performance remediation;
- no mapping changes in the audit.

## Later order

1. `LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`;
2. decide whether mapped support structurally explains a meaningful share of zero acceptance;
3. if support is not sufficient, reopen drafter training/interface/distribution hypotheses;
4. only salvage/modify DFlash after a mechanistically supported path exists;
5. otherwise return to the next high-leverage LOOM architecture/I/O branch toward practical 30B-on-8GB serving.
