# LOOM — Active Handoff

Last updated: 2026-08-30
Status: WP1 GO/persisted; WP2 GO/persisted; WP3 original adapter families valid NO_GO; WP3-R2 Behavioral Unlock GO/persisted; **WP4 Final Integration + Acceptance is authorized and active**.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.89.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
WP4 contract: `research/integration/loom-final-acceptance-wp4.md`.

## Final product candidates

### FAST / default

Label:
`loom-deep-30b-s32`

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Validated S32 median decode: `5.596 tok/s`.

### UNLOCKED

Label:
`loom-deep-30b-unlocked`

Model:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

WP3-R2 persistence commit:
`1252fcfad73878981a1aa1844a484949a12d5ff4`

Validated R2 behavior/capability:
- explicit refusal `6/6 -> 0/6`;
- benign capability `8/8 -> 8/8`;
- no increased frozen degeneration;
- API/WebUI and real Pi + WP2 passed;
- clean rollback to FAST passed.

Tradeoff: about `55%` of fresh FAST decode in the R2 comparison, with materially higher swap pressure and explicit disposition drift.

## Context Intelligence

WP2 Caveman + Cavemem remains canonical for both profiles. Normal final operation should use the existing `loom-local` provider integration and preserve independent `LOOM_CONTEXT_INTELLIGENCE=0` rollback.

## WP4 target

Turn the research state into a stable two-profile product.

Required final UX should provide simple profile selection, preferably:

```text
scripts/loom-deep use fast
scripts/loom-deep use unlocked
scripts/loom-deep start
scripts/loom-deep stop
scripts/loom-deep status
scripts/loom-deep health
scripts/loom-deep current
```

Only one 30B should be resident at a time.

Normal switching should use a stable loopback endpoint where practical, preferably `127.0.0.1:18080`, so Pi/WP2/WebUI do not require manual endpoint rewiring.

Final model artifacts should use stable local ignored `models/` paths, without unnecessary multi-GB duplication. Verify hashes before/after any hard-link/move.

WP4 must validate FAST -> UNLOCKED -> FAST, API/WebUI/Pi+WP2, frozen UNLOCKED behavior/capability reproduction, FAST health/performance, UNLOCKED resources/performance, cache compatibility and rollback.

Durable outputs:
- `docs/LOOM_OPERATIONS.md`;
- `research/integration/loom-final-acceptance-wp4-result.md`;
- local evidence under `results-local/final-acceptance-wp4/<timestamp>/`.

The still-local original WP3 NO_GO result may be archived with the eventual bounded WP4 persistence package. Do not sweep unrelated historical untracked scripts.

Pi must not commit/push during WP4 execution; return one final report for review.
