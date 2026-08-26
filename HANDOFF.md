# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. Same-page cold enforcement is rejected. The project is switching from serial micro-tests to one preregistered compound decision funnel for expert-major.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_001`
Pi context: `/AGENTS.md` v3.29.

## Synchronization

Normal rule: significant checkpoint -> ChatGPT updates GitHub -> user pulls -> next independent Pi WP.

Exception now frozen: a compound preregistered funnel may traverse multiple internal stages without intermediate Git/pull only when question, outcomes, branch logic, quantitative gates, workload and budget are all fixed before execution. Any scientific rule change terminates the funnel.

## Core 30B serving/I/O

External expert data-access is the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage.

## Physical-I/O evidence to date

A/B 001 remains INVALID due cache contamination, while exact payload equality and structural read reduction `3456 -> 384` remain valid.

Every accepted timed arm/repetition must independently show `>=80%` conservative physical coverage.

Fresh-inode copy protocol is rejected (~21% coverage). Instrumentation and `F_GLOBAL_NOCACHE` semantics are resolved.

Global-nocache validation 002 proved the key pattern on the same region:
- first touch T1 `96.0406%` physical coverage;
- repeat T2 `25.8365%`;
- repeat T3 `23.9728%`.

Payload/hash and controls PASS 3/3; swap 0 B. Conclusion: first touch is usable, repeated same-page cold enforcement is not. Do not spend more runs on eviction/control variants for the same pages.

## Exact next step — single decision funnel

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_001`
Preregistration: `research/architecture/loom-30b-expert-major-decision-funnel-001-preregistration.md`.

The funnel answers one strategic question: **should expert-major be integrated into the runtime?**

Stage 0, offline: construct >=3 mutually disjoint matched source/packed expert groups, preferably 64 experts / `160,432,128 B` per arm/group, with exact ordered payload identity and no page reuse across repetitions. If impossible -> `EXPERT_MAJOR_INCONCLUSIVE`.

Stage 1, executed automatically if Stage 0 passes: exactly 3 first-touch matched pairs with frozen order `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`. Every arm must independently pass >=80% conservative physical coverage, exact payload/hash, control restoration, instrumentation, memory and swap gates.

Primary statistic: median of three paired `packed_wall/source_wall` ratios.
- GO if valid median `<=0.70`, packed physical bytes <=1.05x source per pair, no structural/exactness regression.
- NO-GO if valid but median `>0.70` or valid evidence shows unacceptable physical-byte/read-structure regression.
- INCONCLUSIVE only if valid measurement cannot be established.

No model forward, network, DFlash or runtime edits inside this funnel. No human/Git round-trip between its internal stages.

If GO, the next phase should similarly bundle runtime integration + exactness + bounded end-to-end benchmark into one compound WP.
