# LOOM Roadmap

Last updated: 2026-08-31
Current: LOOM final product GO/fully persisted; UOPT-001 PARTIAL_GO/persisted; **UOPT-002 architectural UNLOCKED speed work active**.
Canonical context: `/AGENTS.md` v3.93.
Active contract: `research/integration/loom-unlocked-speed-optimization-002.md`.

## 1. Finished product baseline

### FAST / default
- label `loom-deep-30b-s32`;
- stable model `models/loom-deep-30b-fast.gguf`;
- SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- historical matched decode `5.596 tok/s`;
- WP4 operational snapshot `6.209 tok/s`;
- FAST `-ub 1`;
- WP2 enabled by default.

### UNLOCKED
- label `loom-deep-30b-unlocked`;
- stable model `models/loom-deep-30b-unlocked.gguf`;
- SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- frozen refusal `0/6`, held-out degeneration `0/6`, benign `8/8`;
- behavioral/disposition drift remains documented.

FAST remains default. Only one 30B profile is resident at a time.

## 2. Completed work

WP1 Runtime + Product Serving: GO / persisted.

WP2 Context Intelligence: GO / persisted. Caveman deterministic context packing/recovery + Cavemem SQLite/FTS5 memory.

WP3 Behavioral Transform: valid NO_GO for rank-1 directional, MoE-router and rank-4 subspace routes.

WP3-R2 Behavioral Unlock: GO / persisted.

WP4 Final Integration + Acceptance: GO / persisted in `98949e77863c93a7d9dba266204a911ab85db09c`.

### UOPT-001 — PARTIAL_GO / PERSISTED

Persistence commit:
`93b5f44733d120a4e9c0f0b1fea6e58309f71ccd`.

Retained product change: UNLOCKED `-ub 2` while FAST remains `-ub 1`.

Matched metrics:
- decode `2.579 -> 3.161 tok/s`;
- short TTFT `19.525 -> 15.283 s`;
- ~413-token cold TTFT `199.104 -> 184.700 s`;
- ~1,150-token cold TTFT `433.558 -> 393.983 s`;
- warm long-prefix TTFT `0.195 -> 0.190 s`.

All frozen gates and product integration passed. Current-runtime parameter tuning did not reach the 5 tok/s / FAST-like cold-TTFT targets.

## 3. UOPT-002 — Architectural UNLOCKED Speed Optimization — ACTIVE

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_002`

Branch:
`research/unlocked-speed-001`

Full-GO targets:
- matched fresh decode median >= `5.0 tok/s`;
- existing ~1,150-token cold TTFT <= `184 s`;
- stretch cold TTFT < `120 s`.

Frozen promotion gates:
- refusal `0/6`;
- held-out degeneration `0/6`;
- benign `8/8`;
- Qwen3 routed top-k unchanged;
- exact provenance/hashes;
- loopback API/WebUI/Pi+WP2/cache;
- no crash/OOM/corruption;
- clean rollback to FAST and persisted UOPT-001 UNLOCKED.

Architectural ladder:
1. quantify expert-level I/O, cache hit/miss, page/read amplification and router-to-expert stalls;
2. reproduce a pinned bounded expert-residency implementation if compatible;
3. test router-driven sorted/merged explicit expert prefetch;
4. quantify/mitigate GGUF page amplification without destructive production-model modification;
5. test streamed expert caching / compute-I/O overlap with unchanged top-k;
6. exact-output speculative decoding only as a justified fallback.

External reports (oversized-moe-runtime, ExpertCache, explicit-read prefetch, expert-contiguous/streaming projects) are hypotheses only until locally reproduced.

Storage is constrained; UOPT-001 observed ~5 GiB free. Do not build a second full 13.29 GB GGUF or rewrite the hard-linked stable model unless a later explicit user storage action makes that safe.

Evidence:
`results-local/unlocked-speed-uopt-002/<timestamp>/`.

Pi does not commit/push during execution.
