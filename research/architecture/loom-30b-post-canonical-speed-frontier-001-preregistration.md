# LOOM 30B Post-Canonical Speed Frontier 001 — Preregistration

Date: 2026-08-27
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Maximize practical sustained decode throughput of the already canonicalized Qwen3-30B-A3B Q4 expert-major runtime on Apple M1/8GB while preserving exact model semantics first.

The aspirational engineering target is `>=5.0 tok/s`. This target is not a reason to relax exactness, memory, or validity gates.

Canonical backend commit:
`36414d7` — `scripts/loom_30b_moe_expert_major_backend_001.py`.

Settled runtime acceptance remains:
- expert-major full-bank runtime GO;
- accepted three-pair PACKED/SOURCE median ratio `0.794284` = `20.5716%` lower decode wall;
- canonicalization GO with FORMULAIC_RESOLVER.

Do not reopen those questions.

Final outcomes:
- `SPEED_5TPS_REACHED`
- `SPEED_FRONTIER_ADVANCED`
- `SPEED_FRONTIER_NO_EXACT_GAIN`
- `SPEED_FRONTIER_INCONCLUSIVE`

## Stage 0 — sustained canonical baseline + bounded attribution

No treatment changes.

Use the canonical expert-major backend and accepted full-bank/runtime contract.

Run one deterministic sustained decode workload:
- same canonical model/tokenizer/runtime family;
- greedy/frozen input;
- prefill;
- 1 unmeasured warmup decode token;
- exactly 32 measured decode tokens;
- fresh process.

Record:
- aggregate decode wall and sustained tok/s;
- per-token wall p50/p95;
- peak RSS, memory pressure, swap delta;
- exact routed-expert counts;
- aggregate wall attributable to expert file access, expert materialization/synchronization, expert compute, routing, and non-expert/backbone work where existing instrumentation permits;
- number and aggregate wall of expert-path `open`, `pread`, `close` operations;
- materialization/eval synchronization count.

Instrumentation must be bounded and must not change model semantics, caching policy, expert order, or workload.

Also run the frozen three-position exactness oracle against the accepted canonical output SHA.

If baseline cannot be measured validly: `SPEED_FRONTIER_INCONCLUSIVE`.

## Stage 1 — persistent packed file descriptor

Precondition: canonical PACKED still performs file open/close in the per-expert hot path.

Treatment only:
- open the full-bank file once per PACKED backend/process lifetime;
- use the same `pread` ranges/order;
- explicit deterministic `close()` / context-managed teardown;
- no payload caching, mmap, read-ahead manipulation, or expert retention.

Require:
- 3-position exactness PASS;
- zero fallback/cache;
- no fd leak;
- one fresh 16-token performance run after 1 warmup;
- peak RSS <= Stage-0 baseline +32 MiB;
- swap delta <= baseline +32 MiB;
- tok/s improvement >=2.0% versus the immediately previous accepted implementation.

If PASS, retain this change cumulatively. If valid but gain <2.0%, revert it and continue.

## Stage 2 — expert materialization / synchronization collapse

Precondition: Stage-0 attribution shows expert materialization/synchronization is >=10% of decode wall OR retained instrumentation confirms a standalone synchronization/eval occurs once per routed expert.

Treatment only:
- remove/restructure the redundant per-expert materialization synchronization while preserving safe raw-buffer lifetime;
- synchronization may move only to the actual expert-compute boundary required for correctness;
- expert compute order, routing order, quantization, dtype, math, outputs, and one-expert-live invariant remain unchanged;
- no persistent expert payload cache.

Require:
- 3-position exactness PASS with identical raw float32 final-logit SHA;
- zero fallback/cache;
- one fresh 16-token performance run;
- peak RSS <= previous accepted implementation +64 MiB;
- swap delta <= previous +32 MiB;
- tok/s improvement >=5.0% versus immediately previous accepted implementation.

If PASS, retain cumulatively. If valid but gain <5.0%, revert and continue.

## Stage 3 — bounded allocation/copy reduction

Precondition: after Stage 2, expert read/materialization allocation/copy overhead remains >=10% of decode wall.

Frozen treatment options, in this order:
1. reusable single-expert host buffer with `preadv`/equivalent bounded read-into, if safe with the accepted synchronization lifetime;
2. otherwise no Stage-3 treatment.

Restrictions:
- at most one expert payload buffer retained;
- no multi-expert cache;
- same expert access/order/math;
- no mmap/global cache/eviction manipulation.

Require:
- 3-position exactness PASS;
- zero fallback/cache;
- one fresh 16-token performance run;
- peak RSS <= previous accepted +32 MiB;
- swap delta <= previous +32 MiB;
- tok/s improvement >=3.0% versus immediately previous accepted implementation.

If PASS retain; otherwise revert.

## Stage 4 — bounded one-ahead overlap

Precondition: after accepted prior stages, external expert I/O remains >=20% of measured decode wall and no earlier stage has made runtime unsafe.

Treatment:
- at most one future routed expert may be prefetched asynchronously while the current expert is materialized/computed;
- maximum additional payload residency: one expert payload (`2,506,752 B`) plus bounded metadata;
- mathematical expert compute/accumulation order must remain unchanged;
- no multi-expert cache or speculative route prediction.

Require:
- 3-position exactness PASS;
- zero fallback/cache;
- one fresh 16-token performance run;
- peak RSS <= previous accepted +32 MiB;
- swap delta <= previous +32 MiB;
- tok/s improvement >=3.0%.

If PASS retain; otherwise revert.

## Stage 5 — final sustained speed decision

Using the final cumulative exactness-preserving implementation, run exactly 3 fresh-process repetitions of:
- same frozen workload;
- prefill;
- 1 warmup token;
- exactly 32 measured decode tokens.

Record per repetition:
- aggregate wall;
- tok/s;
- p50/p95 token wall;
- peak RSS;
- swap delta;
- fallback/cache/safety state.

Final exactness: repeat the frozen three-position SHA oracle once on final code.

Decision statistic: median sustained tok/s across the 3 repetitions.

Classification:
- `SPEED_5TPS_REACHED` iff median sustained throughput >=5.0 tok/s and all validity/exactness/safety gates PASS;
- `SPEED_FRONTIER_ADVANCED` iff final median is > Stage-0 baseline by >=5.0% but <5.0 tok/s;
- `SPEED_FRONTIER_NO_EXACT_GAIN` iff valid final improvement is <5.0%;
- `SPEED_FRONTIER_INCONCLUSIVE` only for genuine instrumentation/environment ambiguity.

## Hard bounds / efficiency

- no network/model download;
- no DFlash;
- no quantization change in this checkpoint;
- no model-quality tradeoff;
- no full-bank rebuild;
- no physical cold-I/O campaign;
- no cache/eviction experiments;
- no threshold rescue;
- read only directly relevant canonical code/evidence;
- all stages are one compound engineering funnel; do not stop for Git/human sync between internal stages;
- Pi may edit the canonical backend and directly required runtime code locally but must not commit/push/edit project decision docs;
- rejected treatment must be reverted before next stage;
- retain only treatments that pass exactness, safety and their preregistered minimum speed-gain gate.

Evidence:
`results-local/research/30b-post-canonical-speed-frontier-001/<UTC>/`

## After this checkpoint

If sustained throughput remains materially below 5 tok/s, the next speed frontier may examine non-exact levers separately (lower-bit expert quantization and/or independent speculative decoding) with explicit quality gates. Those mechanisms are NOT authorized by this preregistration.
