# LOOM — Usability Speed Target v1

Date: 2026-08-19
Status: ACTIVE PROJECT TARGET

## Decision

For an interactive LOOM profile, generation speed is now a first-class promotion criterion alongside correctness and memory safety.

Target usable generation speed:
**approximately 20 tokens/second**.

This target is a profile-promotion target, not a scientific PASS/FAIL threshold for individual intermediate experiments. Experiments may remain scientifically valid while operating below 20 tok/s if they establish a useful causal result or optimization point.

## Current reference

The current pure phase-streamed Qwen3-8B 3-bit path measured in Stretch 011 is approximately 0.312 logical token/s in the tested 16-token workload, with late steady-state process disk-read accounting near one complete model payload per generated token.

Therefore memory reduction alone is insufficient: LOOM must also reduce or amortize repeated weight traversal.

## Optimization priorities

1. Complete Stretch 012 as the first controlled RAM-for-I/O point: eight persistent transformer layers.
2. Immediately after the first hotset point, test multi-token/oracle block verification as a separate factor, initially with known-correct future tokens so the target-model traversal amortization upper bound can be measured without draft-model quality confounds.
3. If block verification materially reduces target traversals per accepted token, introduce a real draft mechanism and measure accepted tokens per target traversal.
4. Combine persistent residency and multi-token verification only after each factor has been characterized independently.

## Promotion rule

A final or recommended interactive LOOM profile should not be promoted as practically usable solely because it fits in memory. It must preserve correctness/resource safety and approach the ~20 tok/s usability target closely enough to support normal interactive use.

Do not weaken scientific correctness, memory guardrails, or parity gates to chase throughput.
