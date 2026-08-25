# LOOM — Pi Agent Protocol

Version: 3.3
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is persistent context for Pi. WP prompts must contain only the active delta.

## Role split

Pi owns local execution only: inspect targeted local code/evidence, implement the minimum authorized WP change, run tests/benchmarks, create `results-local/` evidence, and mechanically self-correct inside scope.

ChatGPT owns scientific direction, Git/GitHub synchronization, research result documents, `HANDOFF.md`, `ROADMAP.md`, and checkpoint administration.

Pi must NOT run Git, edit AGENTS/HANDOFF/ROADMAP, push/open/merge PRs, or create project documentation unless explicitly authorized.

## Scientific rules

1. Read this file first, then only files/evidence relevant to the active WP.
2. Preserve one-factor experiments, deterministic inputs, provenance and explicit gates.
3. Runtime/library version is experimental provenance when exact hidden-state parity matters.
4. Distinguish fact, inference, hypothesis and unverified limit.
5. Mechanical failures may be repaired inside scope; failed scientific treatments may not be silently rescued.
6. STOP on scientific ambiguity, destructive actions, missing required artifacts, or explicit stop gates.
7. Do not optimize memory/performance while the active scientific blocker is unresolved unless required for feasibility.

Loop: `OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`.

## Expensive-run retention rule

Before any materially expensive network/compute run, create a retention plan identifying cost, expensive intermediates, exact storage, hashes/provenance and resumability/cache behavior. A run is not complete if required expensive artifacts were only transient.

External LOOM research root:
`<external-archive>/`

Persistent BF16 cache:
`<external-archive>/bf16-cache/`

Persistent research artifacts:
`<external-archive>/artifacts/`

Operational Q4 target remains on the internal SSD unless explicitly changed by a future WP.

## Mission / stable target

Mission: **Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB with exactness, bounded memory and reproducible evidence.

Local target:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Target anatomy:
- 48 MoE layers; 128 experts/layer; top-k 8;
- stored payload 16,220,499,968 B;
- resident non-routed backbone 819,015,680 B;
- routed bank 15,401,484,288 B;
- one local Q4 expert 2,506,752 B;
- BF16 KV 98,304 B/token.

Stable runtime invariants:
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- expert-major contiguous disk access preferred;
- 4-GiB raw global LRU rejected due swap/slowdown.

## DFlash validated mechanical chain

Drafter: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Target: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]` 1-based post-block.

Still-valid mechanical/numerical work:
- target tap interface;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher anchor/block mask repaired;
- deterministic/finite 32k drafter forward path;
- frozen target continuation 45/45 historical overlap and 63/63 target-token reference;
- frozen target reference SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## BF16 precision branch

Pinned upstream BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.
Freeze-time runtime for P1_t01: MLX 0.31.2 via `results-local/mlx/venv-mlx-lm-0.31.3`.

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`:
- Q4 replay exact;
- Q4->BF16 materially changes routing/taps/final logits;
- tap rel-L2 `[1,12,23,34,45]` = `0.114863, 0.345792, 0.310635, 0.198639, 0.274675`;
- final logits rel-L2 `0.336189`, cosine `0.957269`;
- Q4 and BF16 target top1 both `12050`;
- result remained `NOT_CAUSAL`.

Persistent BF16 cache retains ~33 GiB (3,470 routed experts + dense); a later complete P1_t01 replay used 3,470 HDD hits and 0 network bytes. Exact BF16 taps `[5,43,2048]` and final-anchor logits are retained.

`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001` showed Q4->BF16 taps materially move the 32k drafter-logit distribution (rel-L2 `0.215100`, cosine `0.977013`). That distribution-level fact remains valid. Old decoded proposal IDs/ranks from direct `d2t` interpretation are superseded.

## DFlash mapping semantics — RESOLVED

Authoritative upstream semantics:
- model card uses `--draft-vocab-size 32000`;
- `speculators` stores `d2t` as offset:
  `d2t = selected_target_ids - arange(draft_vocab_size)`;
- true target ID for draft row `j` is:
  `target_id = j + d2t[j]`;
- `t2d` is BOOL mask of the 32,000 selected target IDs;
- current vLLM DFlash inference reconstructs `targets = arange(32000) + draft_id_to_target_id`.

Upstream references:
- `vllm-project/speculators` commit `2aec948e43b0313e61aa639c7c8e150a8f1a2929`, `src/speculators/train/vocab_mapping.py`;
- `vllm-project/vllm` commit `d9fbe526c0787eb5e6dd1e3e4d9b88848d21bc6b`, `vllm/model_executor/models/qwen3_dflash.py`.

The earlier local interpretation `target_id = d2t[row]` was a mechanical decode-semantics bug.

## Corrected d2t offset decode — COMPLETE

`LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001` = `MECHANICAL_DECODE_REPAIR_PASS_COMPATIBILITY_STILL_ZERO`.

Report:
`research/architecture/loom-dflash-d2t-offset-decode-repair-001-result.md`

Evidence:
`results-local/research/dflash-d2t-offset-decode-repair-001/20260825T093731Z/`

Mechanical repair:
- 8 decode/analysis scripts changed;
- all now use `draft_row + d2t[draft_row]`;
- no weight/tap/mask/anchor/drafter-math change.

Correct mapping invariants:
- 32,000 draft rows;
- 32,000 reconstructed target IDs;
- all valid/in-vocab;
- all unique;
- reconstructed support exactly equals TRUE positions of `t2d`;
- effective support cardinality `32,000`.

Frozen 63-state corrected support:
- representable `50/63` (`79.37%`);
- unsupported `13/63` (`20.63%`);
- P1_t01 target `12050` remains unsupported.

Corrected proposals:
- raw draft-row argmax unchanged `63/63`;
- old decoded vs corrected target-token ID differs `63/63`;
- corrected target top1 matches `0/63`;
- P1_t01 corrected proposal `8747`, target `12050`, no match.

Therefore:
- old effective support `17,018` is invalid and superseded by `32,000`;
- old `30/63 vs 33/63` support partition is invalid and superseded by `50/63 vs 13/63`;
- old numeric proposal IDs are invalid;
- aggregate frozen top1 compatibility `0/63` **survives correct decoding**.

Corrected target-distribution top5/top10/top50 and proposal ranks were not recovered because complete frozen target logits were not retained. No target forward was run.

The historical first E2E `0/96` remains contaminated until its decode path is corrected/replayed; do not call it reconfirmed solely from the frozen audit.

## Current interpretation

The mapping bug was real and materially distorted support/proposal interpretation, but it does not explain the catastrophic frozen top1 incompatibility.

Reduced draft vocabulary is a secondary structural limit: 13/63 frozen target tokens cannot be proposed. More importantly, all 50 representable frozen target tokens are also predicted incorrectly at top1.

A remaining drafter/target compatibility mechanism must therefore be diagnosed before E2E or performance work.

## Next checkpoint

`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`

Goal: cheaply quantify where the exact target token ranks **inside the DFlash 32k drafter distribution** for the 50 representable frozen states under corrected mapping semantics.

Required direction:
1. map each of the 50 representable frozen target tokens to its unique draft row;
2. use retained full 32k drafter logits if available; otherwise perform only the minimum unchanged drafter-only replay on the frozen tap corpus;
3. measure target-row rank, probability/logit, top-k placement and rank distribution for those 50 states;
4. keep the 13 unsupported states separate;
5. preserve raw drafter math and corrected decode unchanged;
6. do not confuse drafter-side target rank with rank under target-model logits.

Restrictions:
- no target-model forward;
- no BF16 forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no memory/performance optimization.

## WP contract

```text
LOOM WP <id>
Goal: ...
Change: minimum active delta
Gates: correctness + stops
Evidence: results-local/.../<UTC>/
Return: decisive metrics only
STOP
```

Original model files are immutable. Raw evidence stays under `results-local/`; expensive retained artifacts may additionally live under the declared external storage root.
