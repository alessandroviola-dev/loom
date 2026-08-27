# LOOM 30B Expert-Major Canonicalization 001 — Result

Date: 2026-08-27
Checkpoint: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_001`
Classification: `EXPERT_MAJOR_CANONICALIZATION_NO_GO`

## Decision

The first productionized expert-major backend is **not accepted as canonical code in its current form** because the frozen RSS regression gate failed.

This result does **not** revoke the previously accepted expert-major mechanism/runtime direction. Static compatibility, full-runtime exactness and the bounded performance smoke all passed. The failure is isolated to memory behavior introduced during canonicalization.

## Evidence

Local evidence:
`results-local/research/30b-expert-major-canonicalization-001/20260827T084858Z/`

Changed working-tree file:
`scripts/loom_30b_moe_expert_major_backend_001.py`

### Stage 0 — accepted implementation recovery PASS

Accepted full-bank artifact reused from:
`results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/fullbank/experts.bin`

Manifest:
`results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/fullbank/manifest.json`

Artifact was reused, not rebuilt.

### Stage 1 — canonical code integration PASS

- one new file;
- 214 insertions;
- explicit SOURCE/PACKED no-cache backend;
- whitespace check PASS.

### Stage 2 — static production gate PASS

- manifest coverage: `6144/6144`;
- full payload hashes: `6144`;
- source-component provenance hashes: `55,296`;
- access replay: `18,048` accesses;
- unresolved: `0`;
- ambiguous: `0`;
- invalid-range: `0`;
- SOURCE fallback: `0`;
- persistent-cache accesses: `0`.

### Stage 3 — exactness regression PASS

Three accepted decode positions preserved identical routing and raw float32 final logits.

SHA prefixes/suffixes reported:
- `c128586d…e1083d`;
- `d37f9c18…55c382`;
- `4c09bc0f…3caf6c`.

### Stage 4 — performance/safety smoke

Performance PASS:
- SOURCE aggregate decode wall: `4.463661583 s`;
- PACKED aggregate decode wall: `4.187744208 s`;
- PACKED/SOURCE ratio: `0.938185866`;
- frozen performance gate: `<=0.95`.

Safety:
- SOURCE peak RSS: `191,348,736 B`;
- PACKED peak RSS: `402,259,968 B`;
- delta: `+201.14 MiB`;
- frozen RSS limit: `+128 MiB`;
- RSS: **FAIL**;
- swap: `0.0 / 0.0 MiB`, PASS;
- fallback: none;
- persistent cache: none;
- unsafe pressure: none.

## Interpretation

The accepted experimental full-bank backend already passed the runtime RSS gate, whereas the productionized implementation preserved exactness and speed but exceeded the canonicalization RSS allowance. Therefore this is a **canonicalization allocation/lifetime regression**, not evidence against expert-major storage itself.

A new checkpoint may repair only the productionization memory regression. It must not relax the RSS/performance thresholds, change the expert-major mechanism, introduce a multi-expert cache, or reopen settled physical-I/O/runtime acceptance testing.
