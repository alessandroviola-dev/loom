# LOOM 30B Expert-Major Decision Funnel 001 — Result

Date: 2026-08-26
Classification: `EXPERT_MAJOR_INCONCLUSIVE`
Evidence: `results-local/research/30b-expert-major-decision-funnel-001/20260826T143324Z/`

## Result

Stage 0 stopped the funnel before any timed I/O.

- Three groups of 64 experts were identified.
- Logical payload: `160,432,128 B` per arm/group.
- Source cross-group overlap: none.
- Packed cross-group overlap: none.
- Retained metadata/hash validity: PASS.
- Expected reads/group: SOURCE `576`, PACKED `64`.
- No timed payload reads, controls, memory/swap measurements or performance ratios were executed.

## Why Stage 0 failed

The preregistration selected groups in canonical trace order and additionally required those selected experts to be contiguous in the packed expert-major layout. Those two orderings are not equivalent. The selected trace-order groups therefore did not satisfy the packed-contiguity requirement.

This is a measurement-design failure, not evidence for or against expert-major performance.

## Scientific interpretation

Do not classify expert-major as ineffective from this funnel. The causal question remains unanswered.

A new funnel may change Stage 0 only through a new preregistration. The preferred correction is to select groups from physical packed order first, then map exactly the same expert identities into the source nine-range representation. Timing and decision thresholds remain unchanged.
