# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001_CONDITIONAL`
Strategic next: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical long-lived context is in `/AGENTS.md`.

## Proven DFlash chain

- exact target taps `[1,12,23,34,45]`;
- exact B7 wavefront target verifier;
- complete MLX drafter port;
- publisher anchor/block mask repaired;
- independent masked publisher reference PASS;
- corrected MLX/reference proposal parity 63/63.

First E2E:
`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`
- target behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Memory/performance remediation remains deferred while acceptance is zero.

## Structural target incompatibility

Frozen target continuation:
- 45/45 historical overlap;
- complete 63/63 reference;
- deterministic/finite;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit:
- target replay 63/63 PASS;
- scoring control 63/63 PASS;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- target proposal rank min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- accepted prefixes all zero.

Verdict:
`INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

## Target identity

`IDENTITY_MATCH_EXCEPT_QUANTIZATION`:
- DFlash-relevant config/architecture PASS;
- tokenizer/vocab/special-token PASS;
- d2t/t2d semantics PASS;
- no material non-quantization mismatch.

Local delta:
MLX affine 4-bit, group 128, 386 quantized triplets.

Hidden-state/precision drift is therefore the leading hypothesis, not causal proof.

## Unquantized control preflight

`LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001`
classified `CONDITIONAL_PREFLIGHT_DISK_AND_ADAPTATION_REQUIRED`.

Candidate upstream BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Artifacts:
- 16 BF16 safetensors shards + index;
- 18,867 tensors;
- 61,066,575,648 B total.

Disk:
- free 60,668,579,840 B;
- full-snapshot peak 65,066,551,120 B;
- shortfall 4,397,971,280 B.

Therefore the full snapshot route is rejected.

External-expert reuse is conditional because a BF16 reader/math path does not yet exist.

Public provenance check supports using pinned current upstream BF16 object hashes: the weight shard objects and tokenizer.json trace to the original upstream upload commit `fd4bf3b`. The DFlash publisher does not pin an exact verifier revision, so this control must not be described as an exact historical-training replica.

## Next — P1_t01 bounded BF16 control

Checkpoint:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

Frozen state:
`P1_t01`, context 43.

Critical one-factor design:
1. build only the bounded BF16-capable control reader/math adapter;
2. validate that adapter using local/dequantized 4-bit target values against canonical P1_t01 target evidence;
3. require target/tap/router/logit parity before any BF16 interpretation;
4. if adapter parity fails, STOP as `CONTROL_ADAPTER_PARITY_FAIL`;
5. only after parity passes, change only the weight source to pinned upstream BF16 tensors;
6. do not materialize the full BF16 model locally.

Compare:
- post-block taps `[1,12,23,34,45]` at final prefix position;
- final normalized hidden;
- all 48 router logits/top-k/weights;
- full final logits;
- greedy top1, top1/top2 margin and top5 overlap.

Metrics:
- max/mean abs;
- RMSE;
- relative-L2;
- cosine;
- determinism/no NaN/no leak.

Restrictions:
- bounded range/shard staging only;
- no full 61-GB snapshot;
- no DFlash E2E;
- no target/drafter/mapping/acceptance changes;
- no memory/performance remediation;
- no quantization-causality claim unless adapter parity makes the comparison one-factor.

## Decision after control

- adapter FAIL -> debug only adapter semantics;
- adapter PASS + BF16/4-bit hidden states/logits materially diverge -> precision/weight drift gains direct evidence; broader-state confirmation may be required before causal promotion;
- adapter PASS + BF16/4-bit states remain close -> reject simple 4-bit hidden-state drift as sufficient explanation and reopen the next unresolved DFlash interface/training-distribution hypothesis;
- only after a scientifically supported route to nonzero acceptance should memory optimization resume.

## Later order

1. P1_t01 bounded BF16 control;
2. broader confirmation if required;
3. decide DFlash salvageability;
4. memory remediation only after useful acceptance;
5. full E2E economics;
6. capability/coding/context validation;
7. otherwise return to the next high-leverage LOOM architecture/I/O branch.

## Token-efficient Pi workflow

Root `/AGENTS.md` is persistent context. Pi prompts carry only the active delta. Pi executes local work; ChatGPT owns Git/HANDOFF/ROADMAP.
