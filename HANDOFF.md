# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — BF16 precision/distribution mismatch is not sufficient to recover exact DFlash speculation on the preregistered causal set. DFlash is closed as the active recovery path; priority returns to core 30B-on-8GB serving/I/O.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_BF16_CAUSAL_DECISION_001_BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`
Next: `LOOM_30B_MOE_SERVING_IO_REENTRY_001`
Pi context: `/AGENTS.md` v3.19.

## Final DFlash causal result

Report:
`research/architecture/loom-dflash-bf16-causal-decision-001-result.md`

P3 corrected valid causal state:
- Q4 target/verifier top1 1620;
- Q4 DFlash rank 2 / proposal 5416;
- BF16 verifier top1 1620;
- BF16 DFlash rank 2 / proposal 350;
- no exact recovery.

P1 decisive test:
- exact Q4 gate PASS: target 326 rank 3 / proposal 3100;
- BF16 verifier top1 326;
- BF16 DFlash rank 2 / proposal 3100;
- no exact recovery;
- network only `87,265,184 B`, 57 requests, 2 retries due persistent cache reuse.

P3 and P1 both fail exact top1 recovery. The frozen preregistered signal required >=2/3 recoveries, so it is mathematically impossible. P2 and corrected E2E were correctly not executed.

Interpretation: BF16 changes the DFlash distribution and can improve rank, but it does not restore exact speculation. Do not continue DFlash salvage as the active path absent a new independent mechanism.

## Stable 30B runtime facts

- target `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`;
- 48 MoE layers, 128 experts/layer, top-k 8;
- payload `16,220,499,968 B`;
- resident non-routed `819,015,680 B`;
- routed bank `15,401,484,288 B`;
- one Q4 expert `2,506,752 B`;
- external serial-expert full-logit math exact;
- one routed expert logically live at a time;
- expert-major contiguous disk preferred;
- raw 4-GiB global LRU rejected.

## Exact next step

`LOOM_30B_MOE_SERVING_IO_REENTRY_001`

Strictly analysis-first: inspect existing serving/I/O evidence and scripts, identify the dominant measured bottleneck, and propose one minimal experiment with a quantitative success gate. No DFlash reopening and no expensive run until that contract is established.
