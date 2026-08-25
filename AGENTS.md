# LOOM — Pi Agent Protocol

Version: 3.4
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is persistent context for Pi. WP prompts must contain only the active delta.

## Role split

Pi owns local execution only: inspect targeted local code/evidence, implement the minimum authorized WP change, run tests/benchmarks, create `results-local/` evidence, and mechanically self-correct inside scope.

ChatGPT owns scientific direction, Git/GitHub synchronization, research result documents, `HANDOFF.md`, `ROADMAP.md`, and checkpoint administration.

Pi must NOT run Git, edit AGENTS/HANDOFF/ROADMAP, push/open/merge PRs, or create project documentation unless explicitly authorized.

## Scientific rules

1. Read this file first, then only files/evidence relevant to the active WP.
2. Preserve one-factor experiments, deterministic inputs, provenance and explicit gates.
3. Distinguish fact, inference, hypothesis and unverified limit.
4. Mechanical failures may be repaired inside scope; failed scientific treatments may not be silently rescued.
5. STOP on scientific ambiguity, destructive actions, missing required artifacts, or explicit stop gates.
6. Do not optimize memory/performance while the active scientific blocker is unresolved unless required for feasibility.

Loop: `OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`.

## Expensive-run retention rule

Before any materially expensive network/compute run, create a retention plan identifying cost, expensive intermediates, exact storage, hashes/provenance and resumability/cache behavior. A run is not complete if required expensive artifacts were only transient.

External LOOM root:
`<external-archive>/`

Persistent BF16 cache:
`<external-archive>/bf16-cache/`

Persistent research artifacts:
`<external-archive>/artifacts/`

Operational Q4 target remains on internal SSD.

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

Still valid:
- target tap interface;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher anchor/block mask repaired;
- deterministic/finite 32k drafter forward path;
- frozen target continuation 45/45 historical overlap and 63/63 token reference;
- frozen target SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## BF16 precision branch

Pinned upstream BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Freeze-time P1_t01 runtime: MLX 0.31.2 via `results-local/mlx/venv-mlx-lm-0.31.3`.

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`:
- Q4 replay exact;
- Q4->BF16 materially changes routing/taps/final logits;
- final logits rel-L2 `0.336189`, cosine `0.957269`;
- Q4 and BF16 target top1 both `12050`;
- result `NOT_CAUSAL`.

Persistent BF16 cache retains ~33 GiB and exact P1_t01 BF16 taps/logits. Later full replay used 0 network bytes.

`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001` showed Q4->BF16 taps materially move the 32k drafter-logit distribution (rel-L2 `0.215100`, cosine `0.977013`) but did not establish recovery.

## DFlash mapping semantics — RESOLVED

Authoritative upstream semantics:
- draft vocab size `32,000`;
- `d2t` stores offset `selected_target_id - draft_row`;
- true target ID for draft row `j` is `j + d2t[j]`;
- `t2d` is BOOL mask of the 32,000 selected target IDs;
- vLLM reconstructs `arange(32000) + draft_id_to_target_id`.

Upstream references:
- `vllm-project/speculators` commit `2aec948e43b0313e61aa639c7c8e150a8f1a2929`;
- `vllm-project/vllm` commit `d9fbe526c0787eb5e6dd1e3e4d9b88848d21bc6b`.

The former local direct-`d2t[row]` decode was a mechanical bug.

## Corrected offset decode — COMPLETE

`LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001` = `MECHANICAL_DECODE_REPAIR_PASS_COMPATIBILITY_STILL_ZERO`.

Report:
`research/architecture/loom-dflash-d2t-offset-decode-repair-001-result.md`

Evidence:
`results-local/research/dflash-d2t-offset-decode-repair-001/20260825T093731Z/`

Facts:
- 8 decode/analysis scripts repaired;
- true 32k support contains 32,000 valid unique target IDs and equals `t2d` support exactly;
- frozen support: `50/63` representable, `13/63` unsupported;
- P1_t01 target `12050` remains unsupported;
- raw drafter argmax unchanged 63/63;
- corrected exact target matches remain `0/63`;
- P1_t01 corrected proposal `8747`.

Historical first E2E `0/96` remains contaminated until corrected replay; no E2E is authorized yet.

## Corrected drafter target-rank audit — COMPLETE

`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001` = `PASS_DIRECTIONAL_SIGNAL_PRESENT`.

Report:
`research/architecture/loom-dflash-corrected-drafter-target-rank-audit-001-result.md`

Evidence:
`results-local/research/dflash-corrected-drafter-target-rank-audit-001/20260825T094730Z/`

Retained full 32k drafter logits were reused; no replay required. Raw argmax rows and retained-logit hashes revalidated.

For the 50 representable target tokens:
- rank min / median / mean / max: `2 / 93.5 / 438.82 / 3510`;
- top-5: `8/50`;
- top-10: `11/50`;
- top-50: `19/50`;
- top-100: `26/50`;
- rank 1: `0/50`.

Histogram:
- 2–5: 8;
- 6–10: 3;
- 11–50: 8;
- 51–100: 7;
- 101–1000: 17;
- 1001–10000: 7.

Best: `P3_t01`, target `1620`, draft row `1423`, rank `2`, probability `0.05192055`.
Worst: `P2_t01`, target `2464`, draft row `2147`, rank `3510`, probability `4.636e-05`.

Interpretation:
- zero top1 mismatch is real;
- the drafter distribution nevertheless carries substantial directional target signal;
- do not jump to retraining/calibration before checking systematic positional/temporal alignment.

## Next checkpoint

`LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`

Goal: using only frozen target tokens and retained corrected drafter logits/proposals, test whether DFlash is systematically aligned to a neighboring target position rather than the intended exact-next-token position.

Required direction:
1. operate within each frozen prompt/sequence only;
2. preregister relative target offsets `-7..+7`, with `0` as the intended position and no cross-sequence comparisons;
3. compare corrected proposal top1 token against the frozen target token at every valid offset;
4. for representable neighbor tokens, measure their drafter-row ranks from retained 32k logits;
5. report match count and rank summaries by offset;
6. explicitly test whether any non-zero offset dominates offset 0;
7. no model replay unless retained evidence is unexpectedly insufficient.

Restrictions:
- no target forward;
- no BF16 forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no performance/memory work.

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
