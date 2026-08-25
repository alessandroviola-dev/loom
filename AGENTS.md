# LOOM — Pi Agent Protocol

Version: 3.2
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

Validated before current mapping discovery:
- target tap interface;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher anchor/block mask repaired;
- drafter numerical/reference forward path deterministic/finite.

Frozen target continuation:
- 45/45 historical overlap;
- 63/63 target-token reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Target identity audit:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.
Local material target delta: MLX affine Q4 group 128.

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

Persistent BF16 cache now retains ~33 GiB (3,470 routed experts + dense); later complete P1_t01 replay used 3,470 HDD hits and 0 network bytes. Exact BF16 taps `[5,43,2048]` and final-anchor logits are retained.

`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001` found that Q4->BF16 taps materially move the 32k drafter-logit distribution (rel-L2 `0.215100`, cosine `0.977013`). This distribution-level fact remains valid. Any proposal token/rank result derived through the old direct-`d2t` decode is contaminated and must be recomputed.

## CRITICAL mapping-semantics correction

`LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001` is scientifically classified `CONVERSION_OR_DECODE_SEMANTICS_BUG` after authoritative upstream review.

Local audit found:
- raw publisher `d2t` length 32,000;
- raw `d2t` values have 17,018 unique numeric values;
- `t2d` is BOOL over target vocab 151,936 with exactly 32,000 true IDs;
- MLX decoded proposals as `d2t[argmax(draft_logits)]`.

Authoritative upstream semantics:
- model card trains this exact DFlash with `--draft-vocab-size 32000`;
- `speculators` builds `d2t` as an OFFSET:
  `d2t = selected_target_ids - arange(draft_vocab_size)`;
- therefore true target ID for draft row `j` is:
  `target_id = j + d2t[j]`;
- `t2d` is the BOOL mask of the 32,000 selected target IDs;
- current vLLM DFlash inference likewise computes `targets = arange(32000) + draft_id_to_target_id` and scatters 32k logits into target-vocab space.

Upstream evidence:
- `vllm-project/speculators` commit `2aec948e43b0313e61aa639c7c8e150a8f1a2929`, `src/speculators/train/vocab_mapping.py`;
- `vllm-project/vllm` commit `d9fbe526c0787eb5e6dd1e3e4d9b88848d21bc6b`, `vllm/model_executor/models/qwen3_dflash.py`;
- published RedHatAI model card.

Consequences: the prior interpretation of `d2t` as absolute target IDs was wrong. Pending corrected replay, invalidate all downstream conclusions that depend on that decode, including:
- claimed effective support 17,018;
- 30/63 representable vs 33/63 unsupported;
- P1_t01 `12050` unsupported classification;
- decoded proposal target IDs/ranks from direct `d2t[argmax]`;
- `0/63` compatibility conclusion insofar as based on wrong decoded IDs;
- first E2E `0/96` acceptance is suspect if the same decode was used.

Do NOT invalidate underlying drafter logits/weights/taps/mask math solely because of this decode bug.

Report:
`research/architecture/loom-dflash-output-mapping-semantics-audit-001-result.md`

Local evidence:
`results-local/research/dflash-output-mapping-semantics-audit-001/20260825T091537Z/`

## Next checkpoint

`LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`

Goal: mechanically repair only draft-row -> target-token decode semantics to `target_id = row + d2t[row]`, prove parity against authoritative upstream behavior, and recompute frozen 63-state support/proposal compatibility from retained evidence where possible.

Restrictions:
- no retraining/remapping of learned weights;
- no BF16 forward;
- no target-model regeneration unless proven necessary;
- no E2E until corrected 63-state compatibility is known;
- preserve drafter weights, taps, mask, anchor and logits math unchanged.

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
