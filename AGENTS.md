# LOOM — Pi Agent Protocol

Version: 2.6
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is the persistent context for Pi. Prompts should contain only the active work-package delta.

## Role split

Pi owns only local technical execution:
- inspect relevant local code/runtime;
- implement the minimum code required by the active WP;
- run tests/benchmarks;
- create local evidence under `results-local/`;
- mechanically self-correct inside scope.

ChatGPT owns:
- scientific direction/experiment selection;
- Git/GitHub synchronization;
- `HANDOFF.md`, `ROADMAP.md`, research result documents and project-state administration.

Pi must NOT run Git operations, edit HANDOFF/ROADMAP, open/merge/push PRs, or create project documentation unless the WP explicitly overrides this.

## Token-efficiency / scientific rules

1. Read this file, then only files/evidence relevant to the WP.
2. Prefer exact paths and targeted search; do not rescan the repo without need.
3. Do not restate project history or full logs.
4. Do not create extra notes/changelogs.
5. Preserve one-factor experiments, deterministic inputs, provenance and explicit gates.
6. Distinguish measured fact, inference, hypothesis and unverified limit.
7. Mechanical failures may be fixed inside scope; failed scientific treatments may not be silently rescued by parameter changes.
8. Stop on scientific ambiguity, missing required artifacts, destructive actions or an explicit STOP gate.

Scientific loop:
`OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`

## Stable LOOM target

Reference machine: Apple M1 / 8 GB unified memory.

Local target:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Canonical anatomy:
- 48 MoE layers; 128 experts/layer; top-k 8;
- full stored payload 16,220,499,968 B;
- resident non-routed backbone 819,015,680 B;
- routed bank 15,401,484,288 B;
- one local 4-bit expert 2,506,752 B;
- zero-cache expert payload 962,592,768 B/token;
- BF16 KV 98,304 B/token.

Stable runtime invariants:
- external serial-expert math and full 48-layer logits are exact;
- one routed expert needs to be live at a time;
- production lifecycle is `GC_END_ONLY`;
- expert-major contiguous disk access is lossless and faster when available;
- source-range access is the general fallback;
- 4-GiB raw `GLOBAL_LRU` is rejected: ~80.9% hits but +2.41 GiB swap and slowdown;
- persistent live-MLX expert cache is not promoted;
- full 14.344-GiB expert pack is not automatically authorized.

## DFlash candidate and validated chain

Drafter:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`

Publisher-intended target:
`Qwen/Qwen3-30B-A3B`

Static drafter:
- 680,813,824 learned BF16 params;
- 5 layers, H=2048;
- target taps `[1,12,23,34,45]`;
- block 8 / 7 proposals.

Validated prerequisites:
- `LOOM_DFLASH_TARGET_INTERFACE_001_PASS`: exact post-block taps, target router/logit/token parity;
- `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`: exact seven-position target verification, 1.653x vs sequential teacher forcing, zero swap/leak;
- `LOOM_DFLASH_DRAFTER_PORT_001_PASS`: all drafter weights mapped;
- missing publisher anchor/block attention mask was found and repaired;
- `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`: independent masked publisher reference, explicit 8×13 mask assertion, 63/63 mapped proposal parity, deterministic and finite.

First E2E:
- `LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`;
- target committed behavior exact;
- acceptance 0/96 cycles;
- control 0.7735 tok/s vs DFlash 0.1544 tok/s;
- swap +737.43 MiB.

Do not remediate memory/performance while acceptance remains zero.

Frozen target reference:
- `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`;
- 45/45 historical overlap through independent target oracle;
- complete 63/63 reference, 18 new decisions labeled `REBASELINED_REFERENCE`;
- deterministic/finite;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit:
- `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`;
- target replay 63/63 and scoring control 63/63;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- target proposal rank min/P50/mean/max = 987 / 14,195 / 28,621.08 / 146,487;
- proposal logprob P50/mean = -37.3015 / -35.7567;
- target top1/top2 margin P50/mean = 8.8752 / 9.0658;
- accepted prefixes `[0,0,0,0,0,0,0,0,0]`;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

This is structural incompatibility, not a near-boundary greedy miss.

Target identity:
- `LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`: `IDENTITY_MATCH_EXCEPT_QUANTIZATION`;
- local provenance `Qwen/Qwen3-30B-A3B-MLX-4bit`, revision `4e2776a4…`;
- architecture/config/tokenizer/special-token/vocab parity PASS;
- d2t/t2d semantics PASS;
- no material non-quantization identity mismatch;
- material delta: MLX affine 4-bit, group 128, 386 weight/scales/biases triplets;
- exact historical DFlash-era target revision remains unpinned.

Therefore 4-bit/hidden-state drift is the leading hypothesis, not causal proof.

## Unquantized-control preflight invariant

`LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001`
classified `CONDITIONAL_PREFLIGHT_DISK_AND_ADAPTATION_REQUIRED`.

Candidate upstream revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`

Artifacts:
- BF16;
- 16 safetensors shards + index;
- 18,867 tensors;
- total 61,066,575,648 B.

Disk:
- free 60,668,579,840 B (56.50 GiB);
- estimated full-snapshot peak 65,066,551,120 B;
- shortfall 4,397,971,280 B;
- full snapshot is NOT authorized.

Runtime feasibility:
- external-expert reuse `CONDITIONAL`;
- current quantized-triplet reader is not drop-in for upstream BF16;
- required: BF16 tensor catalog, dense/expert path, three-projection expert reader and bounded range/shard-backed storage.

First isolated state:
`P1_t01`, context 43.

Compare:
- final-position post-block taps `[1,12,23,34,45]`;
- final normalized hidden;
- full logits;
- all 48 router logits/top-k/weights;
- greedy top1 and margin.

Metrics:
max/mean abs, RMSE, relative-L2, cosine; logits top1/margin/top5 overlap.
No causal numerical threshold is preregistered yet.

Analytical BF16 control footprint:
- resident backbone 3,082,186,752 B;
- one live expert 9,437,184 B;
- KV at C=43 4,227,072 B.

Public provenance note:
- DFlash model card names `Qwen/Qwen3-30B-A3B` but does not pin a verifier commit;
- current upstream BF16 shard objects and `tokenizer.json` trace to the original upstream upload commit `fd4bf3b`;
- future control must pin exact weight-object/hash provenance and be described as a pinned upstream BF16 control, not an exact historical DFlash-training replica.

Critical one-factor safeguard:
- the BF16 reader/math adapter is a new implementation variable;
- before interpreting BF16 differences, run the new control path with local/dequantized 4-bit target values and require parity with canonical local P1_t01 taps/router/logits;
- adapter parity failure => `CONTROL_ADAPTER_PARITY_FAIL` and STOP;
- only after adapter parity PASS may the weight source alone switch to pinned upstream BF16 objects.

Next checkpoint:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

Restrictions:
- no full 61-GB snapshot;
- bounded range/shard staging only;
- no DFlash E2E rerun;
- no target/drafter/mapping/acceptance changes;
- no memory/performance remediation;
- no quantization-causality claim until the isolated control is interpretable.

## Work-package contract

Normal prompt:
```text
LOOM WP <id>
Goal: ...
Inputs: exact files/evidence
Change: single allowed variable/scope
Gates: correctness + stop conditions
Evidence: output directory/files
Return: decisive metrics only
STOP
```

Everything not changed by the WP inherits this file.

Default evidence:
- original model files immutable;
- experimental scripts may live under `scripts/`;
- raw evidence under `results-local/<area>/<checkpoint>/<UTC>/`;
- record real UTC/provenance;
- do not manufacture measurements or infer unmeasured physical I/O.

Default concise return:
```text
Checkpoint: <id>
Classification: <PASS/CONDITIONAL/FAIL-specific>
Key metrics: <decisive values>
Parity/tests: <PASS/FAIL>
Memory/safety: <decisive values>
Evidence: <directory>
Files: <created/modified>
Blocker: <if present>
STOP
```
