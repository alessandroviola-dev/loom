# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — DFlash drafter is structurally incompatible with the current target; static identity matches except 4-bit conversion; bounded BF16 control designed
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001_CONDITIONAL`
Next core checkpoint: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while preserving correctness, bounded memory and reproducible evidence.

Stable context lives in `/AGENTS.md`. Pi executes compact local WPs; ChatGPT owns Git/HANDOFF/ROADMAP and scientific checkpoint administration.

## DFlash state

Candidate:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`

Publisher target:
`Qwen/Qwen3-30B-A3B`

Already proven:
- target taps `[1,12,23,34,45]` exact;
- exact B7 wavefront verifier;
- all drafter BF16 weights mapped;
- publisher anchor/block mask repaired;
- independent masked publisher reference PASS;
- corrected MLX/reference proposal parity 63/63.

First E2E remains rejected:
- target behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Do not optimize memory/performance while acceptance remains zero.

## Frozen target / compatibility

`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`:
- historical overlap 45/45;
- complete 63/63 target reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

`LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`:
- target replay and scoring control 63/63;
- drafter/target top1 0/63;
- top5/top10/top50 0/63;
- target proposal rank min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- accepted prefixes all zero.

Verdict:
`INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

## Target identity

`LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

Architecture/config/tokenizer/vocab/special tokens and d2t/t2d semantics all pass. No material non-quantization mismatch found.

Material delta:
MLX affine 4-bit, group size 128, 386 quantized triplets.

Therefore hidden-state/precision drift is the leading hypothesis, not proof.

## UNQUANTIZED-CONTROL-PREFLIGHT-001

Classification:
`CONDITIONAL_PREFLIGHT_DISK_AND_ADAPTATION_REQUIRED`.

Report:
`research/architecture/loom-dflash-unquantized-control-preflight-001-result.md`

Evidence:
`results-local/research/dflash-unquantized-control-preflight-001/20260824T160413Z/`

Candidate BF16 upstream revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`

Layout:
- 16 BF16 safetensors shards + index;
- 18,867 tensors;
- 61,066,575,648 B total.

Disk:
- free 60,668,579,840 B;
- full-snapshot peak estimate 65,066,551,120 B;
- shortfall 4,397,971,280 B.

Full BF16 snapshot is therefore NOT authorized.

Runtime:
- existing quantized-triplet reader is not drop-in for BF16;
- bounded BF16 tensor/range or shard-staging adapter required;
- analytical resident backbone 3,082,186,752 B;
- one BF16 expert 9,437,184 B;
- KV at context 43 4,227,072 B.

Public provenance check:
- DFlash names `Qwen/Qwen3-30B-A3B` but does not pin target commit;
- current upstream BF16 weight objects and tokenizer.json trace to original upload commit `fd4bf3b`;
- control must pin exact object hashes and must not claim exact historical DFlash-training reproduction.

## Exact next step

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

Frozen state:
`P1_t01`, context 43.

One-factor design:
1. implement the bounded BF16-capable control reader/math path;
2. first feed it local/dequantized 4-bit target values and require parity against the canonical local P1_t01 taps/router/logits;
3. adapter parity failure => STOP;
4. only after adapter parity passes, replace only the weight source with pinned upstream BF16 tensors;
5. compare final-position taps `[1,12,23,34,45]`, final normalized hidden, all router decisions and full logits.

Report max/mean abs, RMSE, relative-L2, cosine, logits top1/margin/top5 overlap, determinism and finite values.

Restrictions:
- no full 61-GB snapshot;
- bounded range/shard staging only;
- no DFlash E2E;
- no target/drafter/mapping/acceptance changes;
- no memory/performance remediation;
- no causal quantization conclusion unless the one-factor control is valid.

## Later order

1. P1_t01 bounded BF16 control;
2. if interpretable, decide whether precision drift explains the DFlash incompatibility and whether broader-state confirmation is needed;
3. determine whether this drafter is salvageable;
4. only after nonzero useful acceptance: memory remediation and full E2E economics;
5. capability/coding/context validation;
6. if DFlash is nonviable, return to next highest-leverage LOOM architecture/I/O branch.
