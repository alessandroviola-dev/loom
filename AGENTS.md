# LOOM — Pi Agent Protocol

Version: 3.1
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is persistent context for Pi. Prompts contain only the active WP delta.

## Role split

Pi owns local technical execution only: inspect relevant local code/runtime, implement the minimum WP code, run tests/benchmarks, create `results-local/` evidence, and mechanically self-correct inside scope.

ChatGPT owns scientific direction, Git/GitHub synchronization, `HANDOFF.md`, `ROADMAP.md`, research result documents and project-state administration.

Pi must NOT run Git, edit HANDOFF/ROADMAP, open/merge/push PRs, or create project documentation unless explicitly authorized by the WP.

## Scientific rules

1. Read this file, then only exact files/evidence relevant to the WP.
2. Use targeted search; do not rescan the repo without need.
3. Preserve one-factor experiments, deterministic inputs, provenance and explicit gates.
4. Treat runtime/library version as an experimental variable whenever exact hidden-state parity matters.
5. Distinguish measured fact, inference, hypothesis and unverified limit.
6. Mechanical failures may be repaired inside scope; failed scientific treatments may not be silently rescued.
7. STOP on scientific ambiguity, missing required artifacts, destructive actions or explicit stop gates.
8. Do not optimize memory/performance while the active scientific blocker is unresolved unless required for feasibility.

Loop: `OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`.

## Expensive-run retention rule

Before any run expensive in network, compute time, or difficult-to-reproduce remote data, create a retention plan before execution.

The plan must identify:
- estimated cost/time/network volume;
- expensive intermediate artifacts future work may need;
- retained artifacts and exact storage location;
- hashes/provenance required for reuse;
- resumability/cache behavior where practical.

An expensive run is not complete if required retained artifacts were only transient. Reusable immutable remote/model-derived payloads should be cached when this prevents material repeated cost without changing scientific semantics.

External LOOM research root:
`<external-archive>/`

Persistent BF16 cache:
`<external-archive>/bf16-cache/`

Persistent research artifacts:
`<external-archive>/artifacts/`

The operational Q4 target stays on the Mac internal SSD unless a future WP explicitly authorizes otherwise.

## Stable target/runtime

Reference machine: Apple M1 / 8 GB unified memory.

Local target:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Canonical anatomy:
- 48 MoE layers; 128 experts/layer; top-k 8;
- stored payload 16,220,499,968 B;
- resident non-routed backbone 819,015,680 B;
- routed bank 15,401,484,288 B;
- one local 4-bit expert 2,506,752 B;
- zero-cache expert payload 962,592,768 B/token;
- BF16 KV 98,304 B/token.

Stable runtime invariants:
- external serial-expert math and full 48-layer final logits are exact;
- one routed expert needs to be live at a time;
- lifecycle `GC_END_ONLY`;
- expert-major contiguous disk access is lossless and faster when available;
- 4-GiB raw `GLOBAL_LRU` rejected due swap/slowdown;
- full expert pack is not automatically authorized.

## DFlash validated chain

Drafter: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Publisher target: `Qwen/Qwen3-30B-A3B`
Required target taps: `[1,12,23,34,45]` 1-based post-block.

Validated:
- target tap interface;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher anchor/block mask repaired;
- corrected publisher-reference proposal parity 63/63, deterministic/finite.

First E2E rejected:
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Frozen continuation:
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
Architecture/config/tokenizer/vocab/special-token/d2t-t2d checks previously PASS; local material model delta is MLX affine 4-bit group 128. Exact historical DFlash-era verifier revision remains unpinned.

## BF16 control / persistent evidence

Pinned upstream BF16 control revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.
Full snapshot 61,066,575,648 B remains unauthorized; bounded access only.

Freeze-time P1_t01 runtime:
`results-local/mlx/venv-mlx-lm-0.31.3` / MLX exactly `0.31.2`.

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`:
- Q4 Gate A bitwise taps/router/final-logit/greedy parity PASS;
- Q4/BF16 first router divergence layer 0 position 1;
- identical full-prefix router top-k layers 0/48;
- tap relative-L2 `[1,12,23,34,45]` = `0.114863, 0.345792, 0.310635, 0.198639, 0.274675`;
- final hidden rel-L2 `0.270665`, cosine `0.964671`;
- final logits rel-L2 `0.336189`, cosine `0.957269`;
- Q4 top1 = BF16 top1 = `12050`;
- result `NOT_CAUSAL`.

Persistent external BF16 state now retained:
- 3,470 routed expert entries ~31 GiB;
- dense cache ~2.9 GiB;
- ~33 GiB total;
- complete later re-extraction used 3,470 HDD hits / 0 network bytes;
- exact five float32 taps `[5,43,2048]` and final-anchor BF16 logits retained with hashes/provenance.

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

Drafter-logit movement Q4 -> BF16 taps:
- max abs `2.72215`;
- mean abs `0.343385`;
- RMSE `0.432349`;
- relative-L2 `0.215100`;
- cosine `0.977013`.

Conclusion: precision changes drafter logits materially but is insufficient to recover proposal/rank/top-k on P1_t01.

P1_t01 target token `12050` is absent from current mapped drafter support.

## Output support coverage audit — COMPLETE

`LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001` = `SUPPORT_COVERAGE_MAJOR_BLOCKER`.

Report:
`research/architecture/loom-dflash-output-support-coverage-audit-001-result.md`

Evidence:
`results-local/research/dflash-output-support-coverage-audit-001/20260825T090327Z/`

Validated mapping semantics:
- `d2t`: drafter output index -> target token ID;
- output rows: `32,000`;
- target vocab: `151,936`;
- unique mapped target support: `17,018`;
- invalid/out-of-vocab IDs: `0`;
- duplicate entries beyond unique support: `14,982`;
- duplicated target IDs: `6,098`.

Frozen 63-state support:
- representable: `30/63` (`47.62%`);
- structurally unsupported: `33/63` (`52.38%`);
- existing representable-but-wrong: `30/63`;
- target matches: `0/63`;
- P1_t01 target `12050`: unsupported.

Interpretation:
- mapped support is a major structural blocker and makes exact proposal impossible on 33/63 frozen states;
- it does NOT explain the full 0/63 failure because all 30 representable states are also wrong;
- large `32,000 -> 17,018` many-to-one mapping/collision structure is measured but is NOT yet declared a bug.

## Next checkpoint

`LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001`

Goal: determine whether the observed many-to-one `d2t` mapping and effective 17,018-target support are exactly publisher-intended semantics or a local conversion/interpretation defect.

Required static audit:
1. identify authoritative publisher mapping artifacts/logic from already available frozen/local provenance;
2. compare publisher and local `d2t`/`t2d` semantics and arrays bitwise where possible;
3. characterize duplicate multiplicities and treatment of tokenizer-equivalent/special/byte/fallback entries;
4. establish whether 32,000 output rows genuinely imply only 17,018 unique target-token IDs under publisher semantics;
5. do not modify mapping during audit;
6. no BF16 forwards, target generation, E2E, model download, or performance work.

Decision:
- publisher-intended mapping -> coverage blocker is intrinsic to this candidate/interface; combined with 30/63 representable-but-wrong, DFlash salvage requires substantive model/output-head changes and should be weighed against returning to LOOM's practical 30B-on-8GB serving path;
- local semantic/conversion mismatch -> repair mapping only, re-prove publisher parity, then rerun cheap support coverage before any E2E.

## Work-package contract

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

Original model files are immutable. Raw evidence stays under `results-local/<area>/<checkpoint>/<UTC>/`; expensive retained artifacts may additionally live under the declared external LOOM storage root.
