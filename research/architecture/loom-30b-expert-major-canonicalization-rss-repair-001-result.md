# LOOM 30B Expert-Major Canonicalization RSS Repair 001 — Result

Date: 2026-08-27
Checkpoint: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RSS_REPAIR_001`
Classification: `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE`

## Decision

The bounded RSS repair did not produce an admissible one-factor canonicalization smoke because PACKED alone parsed the full `6144 × 9`-component validation manifest in the runtime process. That parsing raised allocator high-water RSS, and compacting/freeing live Python metadata afterward did not establish comparable allocator history between SOURCE and PACKED.

This does **not** reject expert-major. The accepted full-bank runtime direction remains `EXPERT_MAJOR_RUNTIME_GO` from `LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002`.

## Evidence

Local evidence:
`results-local/research/30b-expert-major-canonicalization-rss-repair-001/20260827T104738Z/`

Working-tree code:
`scripts/loom_30b_moe_expert_major_backend_001.py`

### Attribution

Concrete canonicalization-only issue:
- PACKED runtime parsed/retained the full 6144-entry manifest including 9 source components per expert;
- live metadata was reduced by `41,066,169 B` after compacting to resolver-only fields;
- process RSS did not normalize after the parse because allocator high-water remained;
- SOURCE did not execute the same validation-manifest parse, therefore the single smoke pair was not one-factor-valid for the frozen RSS gate.

### Static / semantic gates

PASS:
- full-bank integrity/provenance;
- manifest `6144/6144`;
- `18,048` access replay;
- unresolved/ambiguous/invalid-range/fallback accesses: `0`;
- persistent expert cache: `0`;
- three-position exactness: identical routing and identical raw float32 final-logit SHA.

### Smoke evidence — informative but inadmissible for final RSS decision

RSS milestones SOURCE / PACKED (bytes):
- init: `94,863,360 / 194,674,688`;
- ready: `1,238,220,800 / 195,035,136`;
- after prefill: `134,463,488 / 116,604,928`;
- after warmup: `95,371,264 / 90,406,912`;
- measured 1: `96,305,152 / 90,062,848`;
- measured 2: `96,944,128 / 89,292,800`;
- measured 3: `96,927,744 / 89,735,168`;
- observed peaks: `1,238,220,800 / 195,035,136`.

Measured decode wall:
- SOURCE `4.742729167 s`;
- PACKED `4.121929209 s`;
- ratio `0.869104911`.

Swap delta `0 MiB` both arms; no fallback, persistent cache, or unsafe memory pressure.

Because startup/allocator histories differed, the runtime ratio and RSS peak comparison are not accepted as the canonicalization decision evidence.

## Interpretation / required next repair

Validation/provenance metadata belongs to an **offline/preflight contract**, not the hot runtime object. The next bounded canonicalization checkpoint must separate full-manifest verification from runtime execution:
1. validate full manifest/artifact in a separate preflight process;
2. derive a tiny runtime contract/resolver artifact from that validated state;
3. make PACKED runtime load only the minimal resolver state required for `(layer_id, expert_id) -> payload`;
4. never parse the full 6144×9 validation manifest in the timed/runtime child;
5. then repeat only static gates, exactness, and one fresh-process smoke under the unchanged thresholds.

If the retained full-bank manifest proves fixed-size contiguous lexicographic `(layer, expert)` placement, the preferred runtime resolver is formulaic offset computation plus a small provenance contract rather than a 6144-entry Python dictionary.
