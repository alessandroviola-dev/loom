# LOOM — Direct MLX 8B 4-bit KV8 Rescue 001 Closure

Date: 2026-08-19
Status: **BRANCH CLOSED — EXACT RUN CLASSIFICATION NOT CANONICALIZED**

## Operator report

The KV8 Rescue 001 command was executed by the operator and was reported as failed.

The detailed terminal output / run summary for that attempt was not ingested into the canonical LOOM record before the project research pivot described in `research/notes/capability-amplification-pivot-2026-08-19.md`.

Therefore this file deliberately does **not** classify the attempt as `PARTIAL_RESOURCE_FAIL`, `RUNTIME_FAIL`, `INVALID_HARNESS`, or another scientific outcome without evidence.

## Decision

Regardless of the unresolved exact KV8 run classification, the 8B 4-bit rescue ladder is closed by project decision.

Reasons:
- the unquantized 4-bit full-session profile already resource-failed twice, including one host-state-controlled replication;
- the controlled run demonstrated a genuine continuous-workload memory boundary;
- further KV/context rescue iterations would move LOOM toward an open-ended fit-the-model optimization ladder;
- the project has adopted a more valuable next research question: capability amplification of a smaller validated model, followed later by explicit memory-hierarchy research.

Do not infer a KV8-specific causal finding from this closure note.

No further KV6/KV4/context-reduction rescue is authorized in this branch unless the project later opens a new, separately motivated experiment.
