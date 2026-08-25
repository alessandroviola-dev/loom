# LOOM — Pi Agent Protocol

Version: 3.19
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Rules

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git/push/PR/edit project docs unless explicitly authorized.

1. one-factor experiments; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. continuation provenance includes IDs, segmentation, KV boundary, selector, DFlash anchor and scoring row;
4. treatment comparison is invalid if more than the intended factor changes;
5. expensive/network work requires retained/resumable artifacts and pre-dispatch hard caps;
6. fail closed offline before expensive execution.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Mission / stable target

Mission: **Big models. Small machines.** Practical ~27B/32B local AI on Apple M1/8GB.
Q4 target: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Stable 30B target facts:
- 48 MoE layers, 128 experts/layer, top-k 8;
- payload `16,220,499,968 B`;
- resident non-routed `819,015,680 B`;
- routed bank `15,401,484,288 B`;
- Q4 expert `2,506,752 B`;
- BF16 KV `98,304 B/token`;
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- expert-major contiguous disk preferred;
- raw 4-GiB global LRU rejected.

## DFlash branch — CLOSED AS ACTIVE RECOVERY PATH

Drafter: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps `[1,12,23,34,45]`.
Correct mapping: `target_id = draft_row + d2t[draft_row]`.
Support `50/63` representable, `13/63` unsupported; corrected exact top1 `0/63`.

Closed explanations: temporal shift, MLX drafter implementation, static verifier/tap interface, tap transport dtype.

Pinned BF16 revision: `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.
Network guard: PASS, remote source parity PASS.

Exact Q4 frozen baselines:
- P3 target 1620, rank 2, proposal 5416;
- P1 target 326, rank 3, proposal 3100;
- P2 target 994, rank 3, proposal 4057.

Final BF16 causal decision:
`BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`.
Report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.

Validated causal coordinates:
- P3 anchor 271, position/raw-row 2;
- P1 anchor 13, position/raw-row 6;
- P2 anchor 11, position/raw-row 3.

P3 valid corrected evidence:
- BF16 verifier top1 1620;
- Q4 DFlash rank 2 / proposal 5416;
- BF16 DFlash rank 2 / proposal 350;
- no exact recovery.

P1 decisive test:
- Q4 gate rank 3 / proposal 3100 PASS;
- BF16 verifier top1 326;
- BF16 DFlash rank 2 / proposal 3100;
- no exact recovery;
- network `87,265,184 B`, 57 requests, 2 retries.

P3 + P1 both fail exact recovery, so the preregistered >=2/3 signal is impossible. P2 and corrected E2E are not justified for this mechanism.

Interpretation: BF16 materially changes DFlash distributions and can improve rank, but precision/distribution mismatch alone is not sufficient to restore exact speculation.

Do not continue DFlash salvage as the active LOOM path absent a new independent mechanism. Preserve artifacts/cache for diagnostics.

## Next checkpoint

`LOOM_30B_MOE_SERVING_IO_REENTRY_001`

Goal: return to the core 30B-on-8GB path and choose the highest-leverage serving/I/O experiment from the already established exact external-MoE runtime, routing/cache traces and physical-I/O evidence.

Before changing code:
1. inspect current retained 30B serving/I/O evidence and latest relevant scripts/results;
2. identify the dominant measured latency/resource bottleneck, not a speculative one;
3. propose one minimal experiment with a quantitative success gate;
4. do not reopen DFlash or start unrelated optimization.

No expensive run until the re-entry analysis identifies the next measured bottleneck and an offline-valid experiment contract.
