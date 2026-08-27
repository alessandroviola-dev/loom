# LOOM 30B Expert-Major Canonicalization Runtime Contract 002 — Result

Date: 2026-08-27
Checkpoint: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002`
Classification: `EXPERT_MAJOR_CANONICALIZATION_GO`

## Decision

The canonical expert-major backend productionization passes the frozen static, exactness, memory, swap and bounded performance-regression gates when validation-only full-manifest parsing is moved out of the hot PACKED runtime process.

Selected runtime representation: `FORMULAIC_RESOLVER`.

This closes the canonicalization regression discovered in Canonicalization 001 / RSS Repair 001. The implementation is accepted for repository review/commit. The settled full-runtime performance estimate remains the three-pair Full-Bank Runtime Funnel 002 result; the single-pair smoke below is a production-regression check, not a replacement effect estimate.

## Evidence

Local evidence:
`results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/`

Runtime contract:
`results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/runtime-contract.json`

Runtime-contract SHA-256:
`ee43eaa935e957d40856898c73fe238ff626c880514a8deb9b73491567657aba`

Working-tree implementation:
`scripts/loom_30b_moe_expert_major_backend_001.py`

## Stage 0 — offline contract derivation PASS

Fixed-layout invariant PASS:
- `6144` expert records;
- lexicographic `48 × 128` `(layer_id, expert_id)` order;
- constant expert payload `2,506,752 B`;
- contiguous affine offsets with no gaps/overlap;
- total routed bank `15,401,484,288 B`.

Therefore the frozen preferred branch selected `FORMULAIC_RESOLVER` rather than `COMPACT_INDEX_RESOLVER`.

Full validation remained offline/preflight.

## Stage 1/2 — canonical runtime/static gate PASS

- code compile/syntax: PASS;
- offline full validation: `6144` payloads + `55,296` source components PASS;
- resolver coverage: `6144/6144` PASS;
- retained access replay: `18,048` PASS;
- unresolved: `0`;
- ambiguous: `0`;
- invalid-range: `0`;
- SOURCE fallback: `0`;
- persistent expert cache: `0`.

Hot PACKED runtime proof PASS:
- contract-only probe and PACKED runtime children recorded `0` full-manifest opens/parses;
- no 9-component provenance trees were loaded into the hot runtime process.

## Stage 3 — exactness PASS

Three accepted consecutive decode positions:
- routed expert identities/order identical SOURCE vs PACKED;
- integrity/mapping contract PASS;
- raw final-logit float32 SHA identical at all three positions.

Reported SHA-256 prefixes/suffixes:
- `c128586d…1083d`;
- `d37f9c18…5c382`;
- `4c09bc0f…caf6c`.

No fallback, persistent expert cache, or unsafe memory pressure.

## Stage 4 — bounded regression smoke PASS

Frozen order: `SOURCE -> PACKED`.

Measured decode wall:
- SOURCE `4.379309374 s`;
- PACKED `1.924031958 s`;
- ratio `0.439345978 <= 0.95` PASS.

This single smoke is used only as a canonicalization-regression gate. The accepted practical performance estimate remains Full-Bank Runtime Funnel 002 median ratio `0.794284` (`20.5716%` lower measured decode wall across three matched pairs).

RSS milestones SOURCE / PACKED (bytes):
- startup `94,732,288 / 94,715,904`;
- backend `94,732,288 / 94,715,904`;
- runtime-ready `96,256,000 / 96,223,232`;
- backbone `432,537,600 / 305,020,928`;
- prefill `100,794,368 / 122,863,616`;
- warmup `78,872,576 / 90,750,976`;
- measured token 1 `70,647,808 / 90,521,600`;
- measured token 2 `68,960,256 / 90,603,520`;
- measured token 3 `69,025,792 / 90,636,288`;
- peak `432,537,600 / 305,020,928`.

PACKED peak RSS delta vs SOURCE: `-127,516,672 B`, comfortably inside the frozen `+128 MiB` limit.

Swap delta:
- SOURCE `+987.37 MiB`;
- PACKED `-8.00 MiB`.

Frozen matched swap gate PASS. No unsafe pressure, fallback, or persistent cache.

## Interpretation

The prior RSS blocker was a productionization artifact: validation-manifest parsing polluted the hot PACKED process allocator history. The accepted production design separates complete validation/provenance into offline preflight and supplies the hot runtime only a tiny prevalidated formulaic contract.

Because the full bank has a proven fixed-size affine layout, runtime resolution requires no 6144-entry manifest/index in memory: `(layer_id, expert_id)` deterministically maps to the expert payload offset.

`EXPERT_MAJOR_CANONICALIZATION_GO` is therefore accepted. Next action is review the final local working-tree implementation, then commit/push it with the canonical project state before moving to the next serving bottleneck.
