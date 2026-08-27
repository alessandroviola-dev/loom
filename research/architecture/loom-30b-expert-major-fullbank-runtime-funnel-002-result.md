# LOOM 30B Expert-Major Full-Bank Runtime Funnel 002 — Result

Date: 2026-08-27
Checkpoint: `LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002`
Classification: `EXPERT_MAJOR_RUNTIME_GO`

## Decision

The full-bank expert-major backend is accepted as the runtime direction for the current Qwen3-30B-A3B Q4 external-MoE path on Apple M1/8GB.

The funnel completed from compile-time readiness through full-bank construction, static access replay, full-runtime exactness and practical process-level A/B without fallback, persistent expert cache, swap regression or unsafe memory pressure.

## Evidence

Local evidence:
`results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`

### Stage 0 — readiness PASS

- source coverage: `6144/6144` expert identities;
- destination disk gate: PASS;
- producer/consumer readiness contract: PASS.

### Stage 1 — full routed-bank PASS

- entries: `6144`;
- bytes: `15,401,484,288 B`;
- complete hash/provenance verification: PASS.

### Stage 2 — static dry-run PASS

- replayed accesses: `18,048`;
- unresolved accesses: `0`;
- SOURCE fallback: `0`;
- persistent expert cache: `0`.

### Stage 3 — exactness PASS

Three consecutive decode positions exercised the full 48-layer external-MoE path.

- routed expert identity/order: identical;
- expert mapping/hash: PASS;
- raw final-logit float32 SHA: identical SOURCE vs PACKED at all three positions.

### Stage 4 — practical runtime A/B PASS

Frozen matched-pair order was `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`.

PACKED/SOURCE measured decode-wall ratios:
- Pair 1: `0.794284`;
- Pair 2: `0.846718`;
- Pair 3: `0.768208`;
- median: `0.794284`.

The median therefore corresponds to `20.5716%` lower measured decode wall for PACKED versus SOURCE and passes the preregistered `<=0.90` runtime gate.

Safety:
- RSS gate: PASS;
- swap delta: `0 MiB`;
- unsafe memory pressure: none;
- backend fallback: none;
- persistent expert cache: none.

## Interpretation

Raw expert-major physical-I/O causality was already established by Decision Funnel 002. This runtime funnel establishes that the same mechanism survives full-bank integration and produces a practical end-to-end decode improvement while preserving exact runtime semantics and the low-memory external-expert invariant.

The experimental full-bank backend may now be productionized/canonicalized. The settled physical-I/O and runtime acceptance questions must not be reopened absent an independent regression or a materially different target/runtime.
