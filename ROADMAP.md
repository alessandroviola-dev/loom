# LOOM Roadmap

Last updated: 2026-08-31
Current: LOOM final product **GO / fully persisted** at `98949e77863c93a7d9dba266204a911ab85db09c`. New active research branch: **UOPT-001 UNLOCKED speed optimization**.
Canonical context: `/AGENTS.md` v3.91.
Active contract: `research/integration/loom-unlocked-speed-optimization-001.md`.

## 1. Finished product baseline

### FAST / default
- label `loom-deep-30b-s32`;
- stable model `models/loom-deep-30b-fast.gguf`;
- SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- historical S32 matched decode `5.596 tok/s`;
- WP4 operational snapshot `6.209 tok/s`;
- WP2 enabled by default.

### UNLOCKED
- label `loom-deep-30b-unlocked`;
- stable model `models/loom-deep-30b-unlocked.gguf`;
- SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- frozen refusal `0/6`;
- benign capability `8/8`;
- held-out degeneration `0/6`;
- WP4 operational decode `2.963 tok/s`;
- slower and more swap-constrained; disposition drift remains documented.

FAST remains default. Only one 30B profile is resident at a time.

## 2. Final operator interface

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Stable normal endpoints:
- WebUI `http://127.0.0.1:18080/`;
- API `http://127.0.0.1:18080/v1`.

## 3. Completed work

WP1 Runtime + Product Serving: GO / persisted.

WP2 Context Intelligence: GO / persisted. Caveman deterministic context packing/recovery + Cavemem SQLite/FTS5 memory; `23.24%` median heavy-context input reduction, `0%` no-op overhead, exact recovery `6/6`.

WP3 Behavioral Transform: valid NO_GO for rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA routes.

WP3-R2 Behavioral Unlock: GO / persisted. Exact-lineage Huihui replacement achieved refusal `0/6`, benign `8/8`.

WP4 Final Integration + Acceptance: GO / persisted in `98949e77863c93a7d9dba266204a911ab85db09c`. FAST -> UNLOCKED -> FAST, API/WebUI/Pi+WP2/cache, frozen UNLOCKED reproduction and rollback all passed.

## 4. UOPT-001 — UNLOCKED Speed Optimization — ACTIVE

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_001`

Branch:
`research/unlocked-speed-001`

Primary target:
**>= 5.0 tok/s matched fresh decode median** on Apple M1 8 GiB.

Stretch target:
beat FAST historical `5.596 tok/s` if scientifically achievable without regression.

Frozen promotion gates:
- refusal `0/6`;
- benign capability `8/8`;
- held-out degeneration `0/6`;
- exact provenance/hashes;
- loopback API/WebUI/Pi+WP2/cache;
- no crash/OOM/corruption;
- clean rollback to current FAST and current validated UNLOCKED.

Research ladder:
1. current exact-model runtime frontier: MoE slots/residency, mmap/no-mmap, CPU/Metal placement, batch/ubatch and relevant thread/Metal knobs;
2. newer evidence-backed MoE paging/residency runtimes, prioritizing bounded expert-residency approaches;
3. only if runtime work is insufficient, a small exact-lineage quantization frontier of the validated Huihui derivative;
4. combine only independently validated winners.

External benchmark numbers are hypotheses only; all promotion claims require local matched reproduction.

Evidence:
`results-local/unlocked-speed-uopt-001/<timestamp>/`.

Pi does not commit/push during execution. UOPT returns one final bounded report for review.
