# LOOM 30B Lower-Bit Expert Speed/Quality Frontier 001 — Preregistration

Date: 2026-08-27
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Reduce the dominant expert bytes/token cost of the canonical Qwen3-30B-A3B runtime by lowering routed-expert storage/compute precision from the deployed Q4 representation to locally supported Q3 and/or Q2 representations, while preserving full top-8 routing and enforcing a frozen quality gate.

This checkpoint intentionally allows bounded quantization loss. It does NOT change routing sparsity, tokenizer, KV implementation, non-routed backbone weights, model architecture, or expert-major access order.

Aspirational target remains `>=5.0 tok/s`, but quality/safety gates must not be relaxed to reach it.

Frozen reference:
- canonical exact-Q4 code commit `96958de`;
- canonical expert-major `FORMULAIC_RESOLVER` runtime;
- exact-Q4 sustained median `1.229233 tok/s`;
- full top-8 routing;
- existing 128-position Q4 teacher oracle from Routing Sparsity Frontier 001.

Final outcomes only:
- `EXPERT_QUANT_5TPS_REACHED_QUALITY_GATED`
- `EXPERT_QUANT_FRONTIER_ADVANCED`
- `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`
- `EXPERT_QUANT_FRONTIER_INCONCLUSIVE`

## Stage 0 — local capability/readiness contract

No model forward and no full-bank build initially.

Inspect only the installed local MLX/runtime APIs and directly relevant canonical code/artifacts.

Mechanically establish:
- installed MLX version/API surface;
- current Q4 expert tensor/component ABI and quantization group size;
- whether the existing local MLX runtime natively supports target `bits=3` and/or `bits=2` for the same expert matrix shapes and the same group size;
- whether target quantized tensors can be consumed without dense persistent expert materialization or a multi-expert cache;
- deterministic serialization metadata required for a lower-bit expert-major bank;
- projected per-expert bytes and full-bank bytes for each supported target;
- free-disk requirement before candidate construction.

Frozen candidate set:
- `Q3` iff native local support for `bits=3` with the frozen group size/shape contract PASSes;
- `Q2` iff native local support for `bits=2` with the frozen group size/shape contract PASSes.

No other bit width, group-size change, mixed precision, custom kernel, or post-hoc rescue is authorized in this checkpoint.

Source for requantization is the currently deployed Q4 expert representation: deterministically reconstruct/dequantize each Q4 expert tensor and requantize it to the target bit width. Do not download or substitute BF16/FP16 source weights in this checkpoint.

Run a bounded deterministic round-trip pilot on fixed identities spanning the model (at minimum layers `0, 15, 31, 47`, expert `0` in each):
- Q4 source decode PASS;
- target quantize/serialize/reload PASS;
- target expert compute produces finite values and correct shapes;
- no hidden SOURCE fallback/cache;
- scratch RSS remains bounded.

If neither Q3 nor Q2 has a compatible local path: `EXPERT_QUANT_FRONTIER_INCONCLUSIVE` and STOP.

## Stage 1 — reuse/freeze quality oracle

Reuse the already-frozen Q4 teacher oracle from:
`results-local/research/30b-routing-sparsity-speed-quality-frontier-001/20260827T135848Z/`

Before candidate evaluation, mechanically verify its retained contexts/reference logits/top-rank files and persist their digests into this checkpoint evidence.

Oracle remains:
- 8 fixed prompts;
- 16 teacher-forced continuation positions each;
- 128 positions total;
- exact-Q4 float32 reference logits/top ranks.

Frozen fidelity tiers remain unchanged.

### STRICT
All required:
- reference top-1 agreement `>=95%`;
- reference top-1 in candidate top-3 `>=99%`;
- mean `KL(reference || candidate) <=0.05` nats;
- no NaN/Inf.

### USABLE
All required:
- reference top-1 agreement `>=90%`;
- reference top-1 in candidate top-3 `>=97%`;
- mean `KL(reference || candidate) <=0.10` nats;
- no NaN/Inf.

Only candidates meeting at least USABLE fidelity may be selected.

## Stage 2 — candidate full-bank construction and static gate

For each locally supported candidate in deterministic order `Q2`, then `Q3`:

Build a separate resumable lower-bit expert-major artifact from the canonical Q4 expert source.

Requirements:
- all `6144/6144` routed experts;
- deterministic lexicographic `(layer_id, expert_id)` order;
- unchanged routing identity ABI;
- target bit width and frozen group size recorded explicitly;
- complete offsets/sizes/ranges manifest;
- source-Q4 provenance root/digest;
- candidate artifact digest/provenance;
- no modification/rebuild of the accepted Q4 full bank;
- build must be resumable/checkpointed.

Before a candidate build, require free disk >= projected candidate bank size + 25% + 2 GiB scratch margin. If this cannot be satisfied without deleting accepted source/Q4 artifacts, that candidate is INCONCLUSIVE/unavailable; never delete accepted Q4 artifacts.

After build, static gate requires:
- coverage `6144/6144`;
- uniqueness/bounds PASS;
- complete candidate artifact integrity PASS;
- frozen retained `18,048` access replay resolves with zero unresolved/ambiguous/invalid accesses;
- zero SOURCE fallback;
- zero persistent multi-expert cache;
- one expert logically live at a time, except bounded transient quantization/kernel scratch.

Any deterministic candidate artifact/adapter defect => candidate FAIL and do not performance-test it.

## Stage 3 — candidate fidelity gate

For each candidate passing Stage 2, run the SAME 128-position teacher-forced oracle before sustained performance testing.

Record:
- top-1 agreement;
- reference top-1 in candidate top-3;
- mean KL(reference || candidate);
- finite-logit validity;
- candidate fidelity tier.

If candidate fails USABLE fidelity:
- mark candidate quality FAIL;
- do not run sustained speed benchmark;
- continue to the next preregistered candidate if available.

## Stage 4 — candidate sustained performance gate

For each candidate meeting at least USABLE fidelity, run exactly one fresh-process sustained test:
- same frozen runtime/workload family;
- full top-8 routing;
- prefill;
- one unmeasured warmup token;
- exactly 32 measured decode tokens.

Record:
- aggregate wall and tok/s;
- p50/p95 token wall;
- actual expert bytes/token;
- expert I/O / expert compute / materialization / backbone attribution where measurable;
- peak RSS;
- swap delta;
- fallback/cache/safety state.

Candidate is eligible only if all hold:
- fidelity >= USABLE;
- sustained throughput `>=1.10 × 1.229233 tok/s`;
- peak RSS <= exact-Q4 baseline +64 MiB;
- swap delta <= exact-Q4 baseline +64 MiB;
- no unsafe pressure;
- zero SOURCE fallback;
- zero persistent multi-expert cache.

## Stage 5 — select candidate

Among all eligible candidates:
- select highest sustained tok/s;
- if throughput is within 2%, prefer better fidelity tier/metrics, then higher bit width (`Q3` over `Q2`).

If no candidate is eligible: `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN` and STOP.

Do not combine with the rejected routing-sparsity variants from the prior checkpoint.

## Stage 6 — final sustained decision

For the selected candidate, run exactly 3 fresh-process repetitions:
- prefill;
- one warmup token;
- exactly 32 measured decode tokens.

Record per repetition:
- tok/s;
- p50/p95;
- peak RSS;
- swap delta;
- safety/fallback/cache.

Decision statistic: median sustained tok/s across the 3 repetitions.

Repeat the 128-position fidelity oracle once on the final selected implementation/artifact.

Classification:
- `EXPERT_QUANT_5TPS_REACHED_QUALITY_GATED` iff median `>=5.0 tok/s`, final fidelity >=USABLE, and all safety gates PASS;
- `EXPERT_QUANT_FRONTIER_ADVANCED` iff median is >=10% above `1.229233 tok/s`, final fidelity >=USABLE, safety PASS, but median <5.0 tok/s;
- `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN` iff no valid selected implementation improves baseline by >=10%;
- `EXPERT_QUANT_FRONTIER_INCONCLUSIVE` only for genuine local API/environment/artifact-resource ambiguity.

## Artifact retention / disk economy

Accepted Q4 artifacts are immutable and must never be deleted.

Rejected lower-bit candidate binaries may be removed only if needed to satisfy the preregistered disk gate for the next candidate, and only after preserving:
- candidate manifest;
- candidate full-artifact digest;
- build parameters/provenance;
- quality/performance decision evidence.

A selected candidate artifact must be retained.

## Hard bounds / efficiency

- no network/model download;
- no BF16/FP16 source substitution;
- no routing sparsity;
- no DFlash;
- no speculative decoding in this checkpoint;
- no group-size search;
- no mixed precision/custom kernel rescue;
- no full-bank Q4 rebuild;
- no threshold rescue;
- no broad repo/history reread;
- deterministic scripts/JSON for capability/build/integrity checks;
- one compound funnel; no intermediate Git/human sync after execution begins;
- candidate runtime work should live under `results-local/` unless a final accepted implementation later requires canonicalization;
- Pi must not commit/push/edit AGENTS/HANDOFF/ROADMAP/project decision docs.

Evidence:
`results-local/research/30b-lower-bit-expert-speed-quality-frontier-001/<UTC>/`

## After this checkpoint

If lower-bit experts improve throughput but sustained speed remains materially below `5 tok/s`, freeze the best quality-valid bit-width as the compressed-expert baseline and move to an independent speculative-decoding frontier. The intended path to 5 tok/s is cumulative: reduce bytes/compute per verifier token first, then increase accepted output tokens per verifier step.

Only after the current Qwen3-30B-A3B speed frontier is frozen should LOOM execute the planned Qwen3.8-27B / Qwen3.8-Flash-Next bake-off.
