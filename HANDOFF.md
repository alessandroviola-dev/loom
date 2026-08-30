# LOOM — Active Handoff

Last updated: 2026-08-30
Status: WP1 GO/persisted; WP2 GO/persisted; WP3 original adapter families valid NO_GO; WP3-R2 Behavioral Unlock GO/persisted; **WP4 Final Integration + Acceptance completed locally with GO and awaits one bounded final persistence commit**.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.90.
WP4 contract: `research/integration/loom-final-acceptance-wp4.md`.

## Final product

LOOM is now a two-profile local product with one active 30B at a time and one stable serving endpoint.

### FAST / default

Pi label:
`loom-local/loom-deep-30b-s32`

Stable local model:
`models/loom-deep-30b-fast.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Final WP4 snapshot:
- decode `6.209 tok/s`;
- prefill `3.438 tok/s`;
- E2E `7.131 s`;
- RSS `4.00->4.01 GiB`;
- swap `1269->1308 MiB`.

### UNLOCKED

Pi label:
`loom-local/loom-deep-30b-unlocked`

Stable local model:
`models/loom-deep-30b-unlocked.gguf`

SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

Final frozen reproduction:
- explicit refusals `0/6`;
- held-out degeneration `0/6`;
- benign capability `8/8`.

Final WP4 snapshot:
- decode `2.963 tok/s`;
- prefill `1.673 tok/s`;
- E2E `9.129 s`;
- RSS `4.13->4.16 GiB`;
- swap `1667->1708 MiB`.

UNLOCKED remains slower and more swap-constrained; disposition drift remains explicit.

## Operator UX

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Normal endpoints for whichever profile is active:
- WebUI `http://127.0.0.1:18080/`;
- API `http://127.0.0.1:18080/v1`.

FAST remains default.

## Final acceptance — COMPLETE LOCALLY / GO

Classification:
`LOOM_FINAL_ACCEPTANCE_WP4_GO`.

Local result:
`research/integration/loom-final-acceptance-wp4-result.md`

Evidence:
`results-local/final-acceptance-wp4/20260830T182958Z/`

Passed:
- FAST -> UNLOCKED -> FAST switching twice;
- no intentional concurrent 30B residency;
- previous profile PID verified stopped before replacement;
- loopback-only serving;
- API/WebUI/health/models for both;
- real Pi + WP2 requests for both labels;
- Context Intelligence disable rollback;
- KV/prompt reuse for both, repeated 1,149-token prefix reduced to one evaluated token;
- hashes before/after stable hard-link placement;
- final rollback to FAST + WP2.

Stable local models and runtime remain ignored/private:
- `models/loom-deep-30b-fast.gguf`;
- `models/loom-deep-30b-unlocked.gguf`;
- `.loom/runtime/loom-llama-server`.

## Current exact action

Create one bounded final persistence commit containing only reviewed WP4 product files:
- `config/loom-deep-profiles.env`;
- `config/loom-deep-server.env`;
- `config/loom-deep-r2-abliterated-q3ks.env`;
- `scripts/loom-deep`;
- `scripts/loom_wp4_probe.py`;
- `docs/LOOM_OPERATIONS.md`;
- `research/integration/loom-final-acceptance-wp4-result.md`.

May additionally include `research/integration/loom-behavioral-transform-wp3-result.md` for archival completeness if it contains only the reviewed WP3 NO_GO result.

Exclude `models/`, `.loom/`, `results-local/`, home Pi config, caches/secrets and all unrelated historical untracked scripts.

After that commit is pushed and reviewed, LOOM can be marked FINAL / GO / FULLY PERSISTED.
