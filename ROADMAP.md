# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`
Strategic next: `LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical long-lived context is in `/AGENTS.md`.

## Proven DFlash chain

- target tap interface `[1,12,23,34,45]` established;
- exact B7 wavefront verifier;
- complete MLX drafter port;
- publisher anchor/block mask repaired;
- independent masked publisher reference PASS;
- corrected MLX/reference proposal parity 63/63.

First E2E:
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Memory/performance remediation remains deferred while acceptance is zero.

## Frozen-state compatibility

Frozen target continuation:
- independent-oracle historical overlap 45/45;
- complete 63/63 target token reference;
- deterministic/finite;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit on frozen target-tap states:
- target replay/control 63/63 PASS;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal ranks min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

## Identity and runtime provenance

Target identity audit:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

No material non-quantization architecture/tokenizer/vocab/mapping mismatch was found. Local material delta is MLX affine 4-bit, group 128.

Pinned upstream BF16 control:
- revision `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`;
- full 16-shard snapshot `61,066,575,648 B` and not authorized;
- bounded range/shard staging only;
- not proven to be the exact historical DFlash-training verifier revision.

Q4 frozen-tap replay mismatch was traced to runtime provenance:
- frozen evidence used MLX 0.31.2;
- failed replay used MLX 0.32.0;
- `LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001` = `MECHANICAL_REPLAY_MISMATCH_REPAIRED`;
- replay under freeze-time MLX 0.31.2 restored 5/5 tap bitwise parity, 48/48 router parity, final-logit parity and greedy token 12050.

Runtime/library version is part of frozen-state provenance.

## Completed — bounded P1_t01 BF16 vs Q4 control

Checkpoint:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

Classification:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`

Report:
`research/architecture/loom-dflash-unquantized-target-p1t01-range-control-001-result.md`

Evidence:
`results-local/research/dflash-unquantized-target-p1t01-range-control-001/20260824T212818Z/`

Gate A under MLX 0.31.2:
- frozen taps 5/5 bitwise;
- routers 48/48 bitwise;
- final logits bitwise;
- greedy token 12050;
- deterministic/finite/no-leak PASS.

Gate B changed only target weight source Q4 -> pinned upstream BF16.

Execution:
- 3,470 BF16 layer-expert pairs;
- expert payload `32,747,028,480 B`;
- 435 dense tensors / `3,082,186,752 B` reused;
- no dense redownload;
- 13 retries, 0 exhausted failures;
- peak dedicated disk `3,091,655,835 B` (<12 GiB);
- wall time `5,888.0 s`;
- deterministic/finite/no-leak PASS.

Measured Q4 vs BF16:
- first router divergence layer 0, position 1;
- full-prefix identical router top-k layers `0/48`;
- tap relative-L2 `[1,12,23,34,45]` = `0.114863, 0.345792, 0.310635, 0.198639, 0.274675`;
- final hidden relative-L2 `0.270665`, cosine `0.964671`;
- final logits relative-L2 `0.336189`, cosine `0.957269`;
- Q4 top1 = BF16 top1 = `12050`;
- top1/top2 margins Q4 `12.90015`, BF16 `11.875`;
- top-5 overlap `4/5`.

Interpretation:
- Q4 vs BF16 materially changes internal hidden/router/logit distributions on this frozen state;
- greedy next-token identity remains stable;
- because DFlash consumes internal taps, precision-induced hidden-state distribution shift is now a serious mechanistic hypothesis;
- classification remains `NOT_CAUSAL`: one current-upstream BF16 state does not prove quantization caused the 0/63 compatibility failure.

Mechanical transport remediation used expert-major execution, pooled HTTPS and 64 MiB coalesced ranges only; it did not alter scientific target semantics.

## Next — BF16 tap drafter probe

Checkpoint:
`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001`

Question:
Does replacing only the five DFlash input taps from Q4 target values to the completed BF16 target values materially improve drafter proposal compatibility on the same frozen `P1_t01` state?

One-factor contract:
1. unchanged validated DFlash drafter;
2. unchanged drafter weights/mapping/publisher mask/anchor/proposal path;
3. baseline = validated Q4-target taps for `P1_t01`;
4. treatment = completed BF16 target taps for the same state;
5. score both against the pinned BF16 target next-token distribution.

Required comparisons:
- drafter proposal token;
- proposal-logit distribution metrics where available;
- target rank of proposal;
- top5/top10/top50 compatibility;
- movement of proposal probability/rank from Q4-tap baseline to BF16-tap treatment;
- deterministic/finite checks;
- exact proof that only tap tensors changed.

Decision gate:
- material recovery under BF16 taps -> precision-induced tap distribution shift becomes a strong mechanistic contributor; preregister broader frozen-state confirmation before any causal promotion;
- no material recovery -> simple target-tap precision drift is unlikely to be sufficient; reopen DFlash training/interface/distribution hypotheses;
- ambiguous/mechanical failure -> repair only the probe mechanism without broadening the scientific treatment.

Restrictions:
- one `P1_t01` state only;
- no DFlash E2E;
- no retraining/remapping;
- no target/drafter architecture changes;
- no acceptance/memory/performance optimization;
- no broader state sweep;
- no causal claim from this single intervention.

## Later order

1. `LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001`;
2. broader preregistered frozen-state confirmation only if BF16-tap intervention materially recovers compatibility;
3. decide DFlash salvageability / causal plausibility;
4. memory remediation only after useful acceptance is supported;
5. full E2E economics/capability/context if viable;
6. otherwise return to the next high-leverage LOOM architecture/I/O branch.

## Token-efficient Pi workflow

Root `/AGENTS.md` is persistent context. Pi prompts carry only the active delta. Pi executes local work; ChatGPT owns Git/HANDOFF/ROADMAP and scientific checkpoint administration.
