# LOOM 30B Lossless Speculative Verification Ceiling 001 — Preregistration

Date: 2026-08-27
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Measure the maximum verifier-side throughput that the canonical Qwen3-30B-A3B Q4 LOOM runtime could achieve under perfect speculative proposals, before spending time or network/disk budget on a real drafter.

This is a **ceiling experiment**, not a production speculative decoder. Oracle proposals are used only to isolate verifier capability.

The experiment must preserve exact greedy Q4 semantics and must not modify model weights, quantization, routing, tokenizer, KV semantics, or the accepted expert-major bank.

Frozen reference:
- canonical backend commit `96958de`;
- full top-8 Q4 routing;
- accepted exact sustained median `1.229233 tok/s`;
- accepted Q4 expert-major bank/runtime contract;
- existing frozen Q4 teacher contexts/continuations where reusable.

Final outcomes only:
- `SPEC_VERIFY_5TPS_CEILING_REACHED`
- `SPEC_VERIFY_FRONTIER_PROMISING`
- `SPEC_VERIFY_FRONTIER_NOT_PROMISING`
- `SPEC_VERIFY_FRONTIER_INCONCLUSIVE`

## Scientific question

If the verifier is given perfect future token proposals, can LOOM verify multiple consecutive tokens per target step fast enough to justify building/downloading a real drafter?

A real drafter cannot exceed this verifier-only perfect-proposal ceiling once drafter overhead and imperfect acceptance are added.

## Stage 0 — readiness / exact chunk-verification contract

No network/model download.

Inspect only directly relevant canonical runtime code and local MLX APIs.

Establish a deterministic lossless chunk-verification path for candidate chunk sizes:
- `K=2`;
- `K=4`;
- `K=8`.

No other K is authorized.

For each chunk, proposals are the already-known exact greedy Q4 continuation tokens for the frozen workload. This deliberately simulates 100% proposal acceptance and therefore measures only the target verifier ceiling.

Required semantics:
1. target receives current committed prefix plus K oracle proposal tokens;
2. causal attention/KV behavior must be mathematically equivalent to sequential target evaluation;
3. final target logits for every verified position must match the sequential canonical Q4 reference;
4. routed expert identities and per-token expert accumulation order must remain exact;
5. no skipped expert, routing sparsity, lower-bit bank, SOURCE fallback, persistent expert payload cache, or approximate acceptance;
6. any reuse of one loaded expert across multiple positions in the same layer/chunk is allowed only when the exact same expert identity is required by multiple token positions and the expert is applied independently to each corresponding hidden-state row;
7. such within-chunk reuse must not change mathematical output or retain expert payloads beyond that chunk/layer requirement.

Before sustained measurement, validate on at least 3 consecutive canonical positions for every K:
- identical greedy token IDs;
- identical routed expert order per position;
- identical raw float32 final-logit SHA per position versus sequential reference;
- finite logits;
- zero fallback/cache.

If no K can be implemented with exact semantics on the installed runtime: `SPEC_VERIFY_FRONTIER_INCONCLUSIVE` and STOP.

## Stage 1 — K=2 ceiling

Use a fresh process and the frozen deterministic canonical workload.

Procedure:
- prefill;
- one unmeasured warmup chunk where possible;
- exactly 32 verified output tokens total;
- oracle proposals guarantee perfect acceptance.

Record:
- aggregate wall;
- verified output tok/s;
- p50/p95 wall per output token;
- target forward/chunk count;
- total expert access requests;
- unique expert payload loads;
- expert-load reuse count/rate inside chunks;
- expert payload bytes/output token;
- expert I/O, expert compute, materialization/sync, routing, backbone wall where measurable;
- peak RSS, swap delta, memory pressure;
- fallback/cache/safety state.

Require exactness/safety PASS. Otherwise K=2 is invalid.

## Stage 2 — K=4 ceiling

Same procedure and measurements as Stage 1.

## Stage 3 — K=8 ceiling

Same procedure and measurements as Stage 1.

## Stage 4 — select verifier ceiling

Among exact/safe K variants, choose the highest sustained verified output tok/s.

Tie within 2% favors lower K because a real drafter is more likely to sustain acceptance at shorter proposal depth.

Do not combine with Q2/Q3, routing sparsity, DFlash, or any real drafter in this checkpoint.

## Stage 5 — confirmation of best K

For the selected K, run exactly 3 fresh-process repetitions:
- same frozen workload;
- prefill;
- one warmup chunk where possible;
- exactly 32 verified output tokens total.

Decision statistic: median verified output tok/s.

Repeat the exactness oracle on the final implementation/path.

Record:
- 3 tok/s values + median;
- p50/p95;
- chunk count;
- expert unique-loads/output-token;
- expert bytes/output-token;
- reuse rate;
- peak RSS/swap/safety;
- exact final logits/tokens/routing.

## Classification

- `SPEC_VERIFY_5TPS_CEILING_REACHED` iff median verifier-only ceiling is `>=5.0 tok/s`, exactness PASS and all safety gates PASS.
- `SPEC_VERIFY_FRONTIER_PROMISING` iff median is `<5.0 tok/s` but at least `2.0 × 1.229233 = 2.458466 tok/s`, exactness/safety PASS.
- `SPEC_VERIFY_FRONTIER_NOT_PROMISING` iff a valid exact/safe ceiling is `<2.458466 tok/s`.
- `SPEC_VERIFY_FRONTIER_INCONCLUSIVE` only for genuine runtime/API/instrumentation ambiguity that prevents a valid ceiling measurement.

The `2×` promising threshold is intentionally strict because a real drafter adds latency/RAM and will have <100% acceptance.

## Memory/safety gates

For every measured K:
- peak RSS <= canonical exact-Q4 baseline +128 MiB;
- swap delta <= baseline +64 MiB;
- no unsafe memory pressure;
- zero SOURCE fallback;
- zero persistent multi-expert cache;
- transient within-chunk expert reuse only as explicitly authorized.

## Hard bounds / efficiency

- no network/model download;
- no real drafter model;
- no DFlash;
- no n-gram/prompt lookup yet;
- no Q2/Q3;
- no routing sparsity;
- no model-weight/quantization change;
- no full-bank rebuild;
- no threshold/K rescue outside `2/4/8`;
- no broad repo/history reread;
- deterministic scripts/JSON evidence;
- Pi may edit only local evidence runner/directly required experimental runtime helper code;
- Pi must not commit/push/edit AGENTS/HANDOFF/ROADMAP/project decision docs;
- do not present oracle-ceiling tok/s as production user-visible generation speed.

Evidence:
`results-local/research/30b-lossless-speculative-verification-ceiling-001/<UTC>/`

## After this checkpoint

If `SPEC_VERIFY_5TPS_CEILING_REACHED` or `SPEC_VERIFY_FRONTIER_PROMISING`, preregister a real lossless drafter frontier. Candidate order should begin with zero-download/local mechanisms (n-gram/prompt lookup if applicable), then a small tokenizer-compatible Qwen-family draft model only if the measured ceiling justifies its cost.

If `SPEC_VERIFY_FRONTIER_NOT_PROMISING`, do not spend time on a drafter for this verifier architecture; freeze the current 30B speed frontier and move to the planned Qwen3.8 model bake-off or a materially different verifier architecture.
