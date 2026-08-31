# LOOM UNLOCKED Architectural Speed Optimization — UOPT-002

Date: 2026-08-31
Branch: `research/unlocked-speed-001`
Checkpoint: `LOOM_UNLOCKED_SPEED_UOPT_002`
Status: COMPLETE / GO (promoted; see `loom-unlocked-speed-optimization-002-result.md`)

## Objective

Attack the remaining UNLOCKED bottleneck at the expert-paging / cold-prefill architecture level rather than continuing broad flag tuning.

UOPT-001 is complete and persisted as `LOOM_UNLOCKED_SPEED_UOPT_001_PARTIAL_GO` in commit `93b5f44733d120a4e9c0f0b1fea6e58309f71ccd`.

Retained UOPT-001 product baseline:
- exact UNLOCKED GGUF SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- pinned server SHA256 `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`;
- S32, CPU-MoE, no-mmap, UNLOCKED `-ub 2`;
- matched fresh short decode `3.161 tok/s` retained product repeat;
- short TTFT `15.283 s`;
- ~413-token cold TTFT `184.700 s`;
- ~1,150-token cold TTFT `393.983 s`;
- ~1,150-token warm TTFT `0.190 s`;
- frozen behavior/capability `0/6` refusals, `0/6` held-out degeneration, `8/8` benign.

## Promotion targets

Co-primary full-GO targets:
1. matched fresh decode median **>= 5.0 tok/s**;
2. materially reduce cold first-token latency, with the existing ~1,150-token cold path **<= 184 s** as the minimum full-GO target and **<120 s** as stretch target.

A decode-only win that leaves multi-minute avoidable cold TTFT is not full GO. A TTFT-only win that leaves decode below 5 tok/s is not full GO.

## Frozen invariants

No candidate may be promoted unless all remain true:
- explicit refusal `0/6`;
- held-out degeneration `0/6`;
- benign capability `8/8`;
- model semantics are not intentionally weakened (keep Qwen3-MoE routed top-k unchanged; no turbo-top-k / fewer active experts merely for speed);
- exact model/runtime/patch provenance is recorded;
- loopback-only serving on `127.0.0.1`;
- API, WebUI, Pi+WP2 and prompt/KV cache pass;
- no crash/OOM/corruption;
- clean rollback to persisted UOPT-001 UNLOCKED and FAST.

Do not modify the hard-linked production GGUF in place. Never use a relayout/conversion method that can mutate either stable model inode.

## Measurement protocol

Before architectural changes, reproduce the persisted UOPT-001 baseline on the current host and record current free disk/RAM/swap state.

For serious candidates use identical deterministic prompts/settings and at least 3 fresh runs after warmup where practical. Record:
- service start -> `/health`;
- request -> first streamed token (true TTFT);
- prompt/prefill tok/s;
- fresh decode tok/s;
- E2E;
- warm/cache-reuse TTFT;
- RSS, swap, memory-pressure/free-memory signal;
- disk bytes/read rate/page-fault or pager counters when available;
- expert cache/residency hit/miss statistics when available;
- exact source revisions, patch hashes, binary hashes and flags.

Evidence root:
`results-local/unlocked-speed-uopt-002/<timestamp>/`.

## Architectural ladder

Pi should work autonomously through the ladder, retaining winners and reverting losers. Routine failures are not blockers.

### A — bottleneck attribution at expert granularity

Instrument the persisted UOPT-001 path sufficiently to distinguish:
- expert weight bytes requested per layer/token;
- cache/residency hit vs miss behavior;
- physical reads / page-fault amplification;
- router-to-expert wait time;
- cold prefill vs steady decode I/O behavior.

Use low-overhead tracing and short bounded probes first. Do not permanently slow the product path merely to collect telemetry.

### B — bounded expert residency runtime

Audit and, if compatible, locally reproduce a pinned bounded-residency implementation rather than assuming current fork master contains one.

Priority hypotheses to audit:
- `dimitripavlov/oversized-moe-runtime` / llama.cpp discussion #27712: Qwen3-30B-A3B reported `5.79 -> 8.81 tok/s` with residency quota 48 on the author's system;
- page-aware routed-expert residency approaches such as ExpertCache / llama.cpp discussion #26938;
- other current exact-Qwen3-MoE implementations only if they expose an auditable engine boundary and preserve exact inference.

External numbers are hypotheses only. Pin exact upstream commit/release and verify license/patch boundary. Prefer an isolated project-local build/runtime; do not replace the known-good production binary until final acceptance.

Sweep only a small evidence-driven residency frontier that is physically plausible on 8 GiB. More resident experts is not automatically faster if it increases swap/pressure.

### C — explicit routed-expert prefetch / merged I/O

Audit whether the current pager issues layout-blind small reads after routing. If so, test a minimal explicit prefetch path that, after router top-k is known, sorts/merges required expert ranges and issues bounded asynchronous or parallel `pread`/equivalent reads before expert matmul.

Relevant hypothesis: llama.cpp discussion #25779 reports +31–52% on RAM-constrained GGUFs from explicit routed-expert prefetch.

Measure both cold prefill and decode. A prefetcher that improves decode but worsens cold TTFT or memory pressure materially is not automatically a winner.

### D — page-amplification / expert-layout mitigation

Audit the exact Q3_K_S tensor layout and quantify page amplification for one routed expert. Relevant hypothesis: llama.cpp discussion #27149 reports that expert-contiguous relayout can reduce page amplification dramatically and a Qwen3-30B-A3B prototype reached ~4.7 tok/s on an M1-class system.

Storage constraint is important: UOPT-001 observed only ~5 GiB free at that time. Re-measure current free space. Do not create a second full 13.29 GB model if insufficient space and do not destructively rewrite the hard-linked production GGUF.

Allowed without user return:
- metadata/index-only approaches;
- small representative relayout/probe artifacts;
- streaming sidecar/cache designs that fit available disk;
- project-local temporary artifacts that are safely removable and recorded.

If a full non-destructive expert-contiguous copy is the only viable route and disk space is insufficient, record that route as storage-blocked and continue the other ladder steps. Return to the user only if the entire macro cannot progress without freeing/adding storage.

### E — streamed expert cache / overlap

Audit compatible streamed-expert cache designs, including current BigMoeOnEdge-style approaches, but preserve the model's routed top-k. Do not use reduced active-expert count as a speed shortcut.

Test only cache sizes that leave safe host headroom. Measure whether asynchronous overlap hides SSD reads behind compute rather than merely increasing swap.

### F — exact-output speculative decode, only if justified

If expert-residency/prefetch work materially reduces cold TTFT but decode still remains below 5 tok/s, evaluate a small deterministic speculative-decoding pilot only if:
- target-model greedy output remains exact under verification;
- additional draft-model/runtime memory fits safely;
- it does not worsen cold TTFT enough to erase the interactive gain;
- any downloaded draft artifact has exact provenance and remains outside Git.

This is a fallback, not a substitute for fixing the identified paging bottleneck.

## Acceptance classes

### `LOOM_UNLOCKED_SPEED_UOPT_002_GO`

Requires both:
- matched fresh decode median >= `5.0 tok/s`;
- ~1,150-token cold TTFT <= `184 s`;

plus every frozen invariant and complete FAST/UOPT-001 rollback.

### `LOOM_UNLOCKED_SPEED_UOPT_002_PARTIAL_GO`

Allowed only for a reproducible architectural improvement that materially advances at least one co-primary metric without regressing the other or frozen gates after the justified ladder is exhausted. Preserve the fastest/best interactive validated candidate and identify the remaining physical bottleneck with evidence.

### Genuine blocker

Return before macro completion only when progress requires a user action that cannot safely be performed autonomously, such as freeing substantial disk space after all non-destructive routes are exhausted, obtaining unavailable credentials/paid resources, or making a destructive/security-changing host modification.

## Product integration / rollback

FAST remains default. UOPT-001 (`UNLOCKED -ub 2`) is the known-good UNLOCKED rollback baseline throughout UOPT-002.

Do not alter normal UX during research:

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Only a final accepted candidate may replace the implementation behind `unlocked`.

## Persistence

Pi must not commit/push during UOPT-002. Return one bounded final result for review. Any later authorized persistence must exclude GGUFs/models, `.loom/`, `results-local/`, home config, caches, external checkouts, build artifacts and unrelated historical files.
