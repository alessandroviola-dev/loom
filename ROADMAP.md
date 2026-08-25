# LOOM Roadmap

Last updated: 2026-08-25
Current: `BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`
Strategic next: `LOOM_30B_MOE_SERVING_IO_REENTRY_001`
Canonical context: `/AGENTS.md` v3.19.

## DFlash — active salvage closed

Final report:
`research/architecture/loom-dflash-bf16-causal-decision-001-result.md`

Validated result:
- P3: BF16 verifier target 1620, DFlash remains rank 2; no exact recovery;
- P1: BF16 verifier target 326, DFlash improves rank 3 -> 2 but remains non-top1;
- preregistered recovery signal required >=2/3 exact recoveries;
- with P3 and P1 both failing, the signal is impossible;
- P2 and corrected E2E are not justified.

Conclusion: verifier precision/distribution mismatch affects DFlash but is not sufficient to restore exact speculation. Preserve DFlash/BF16 artifacts and cache, but do not spend further active LOOM budget on this mechanism without a new independent hypothesis.

## Core target

Return to practical 30B-on-8GB serving.

Stable foundation:
- exact external serial-expert target runtime;
- one expert logically live at a time;
- known model anatomy and resident/routed byte budgets;
- retained routing/cache traces;
- retained physical-I/O and cache experiments;
- expert-major contiguous disk layout preferred;
- large raw global LRU rejected.

## Next

`LOOM_30B_MOE_SERVING_IO_REENTRY_001`

Before new code or expensive execution:
1. review the latest retained 30B serving/I/O benchmarks and relevant scripts;
2. identify the dominant measured latency/resource bottleneck;
3. rank only evidence-supported candidate interventions;
4. choose one minimal experiment with a quantitative pass/fail gate;
5. then execute only that experiment.

Priority is practical token latency / throughput under the 8GB constraint, not further DFlash salvage.
