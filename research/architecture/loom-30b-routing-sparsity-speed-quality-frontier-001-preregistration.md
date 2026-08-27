# LOOM 30B Routing Sparsity Speed/Quality Frontier 001 — Preregistration

Date: 2026-08-27
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — execute only after the accepted persistent-FD delta from Speed Frontier 001 is reviewed and committed.

## Purpose

Push practical Qwen3-30B-A3B throughput beyond the exact-Q4 frontier by reducing the number of routed experts actually executed per layer under explicit frozen fidelity gates.

This checkpoint intentionally permits a bounded semantic/model-fidelity tradeoff. It does NOT change expert quantization, model weights, tokenizer, KV implementation, or full-bank layout.

Aspirational engineering target remains `>=5.0 tok/s`, but quality/safety gates must not be relaxed to reach it.

Reference runtime:
- canonical expert-major backend;
- accepted persistent PACKED file descriptor from `LOOM_30B_POST_CANONICAL_SPEED_FRONTIER_001`;
- accepted exact sustained median `1.229233 tok/s` from 3 × 32-token runs.

Final outcomes:
- `SPARSITY_5TPS_REACHED_QUALITY_GATED`
- `SPARSITY_FRONTIER_ADVANCED`
- `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`
- `SPARSITY_FRONTIER_INCONCLUSIVE`

## Stage 0 — freeze fidelity oracle before variants

No sparsity treatment yet.

Use the accepted top-8 Q4 runtime as the teacher/reference.

Freeze a deterministic local fidelity set before any variant result is observed:
- 8 fixed prompts covering arithmetic/reasoning, logic, Python coding, debugging, Italian explanation, technical explanation, structured output, and concise instruction following;
- generate/freeze 16 teacher continuation positions per prompt using the accepted greedy Q4 runtime;
- total `128` teacher-forced positions;
- save the exact tokenized contexts and reference float32 logits/top ranks under this checkpoint evidence directory.

For each candidate variant, evaluate the SAME 128 positions and record:
- reference top-1 token agreement rate;
- fraction of positions where reference top-1 is within candidate top-3;
- mean KL divergence `KL(reference || candidate)` at temperature 1.0;
- candidate/reference raw-logit finite-value validity;
- any NaN/Inf.

Frozen quality tiers:

### STRICT fidelity
All required:
- top-1 agreement `>=95%`;
- reference top-1 in candidate top-3 `>=99%`;
- mean KL `<=0.05` nats;
- no NaN/Inf.

### USABLE fidelity
All required:
- top-1 agreement `>=90%`;
- reference top-1 in candidate top-3 `>=97%`;
- mean KL `<=0.10` nats;
- no NaN/Inf.

Only a variant meeting at least USABLE fidelity may be retained or classified as an advancement.

Also record the accepted exact 32-token throughput baseline from Speed Frontier 001 (`1.229233 tok/s`) as the comparison reference. A single fresh baseline smoke may be run only if required to establish environment validity; it must not redefine the accepted baseline statistic.

If the fidelity oracle cannot be constructed deterministically: `SPARSITY_FRONTIER_INCONCLUSIVE` and STOP.

## Treatment definition — dynamic routing-mass truncation

The original router still computes/selects the normal top-8 expert candidates and their original gate weights.

For a treatment threshold `tau`:
1. use the existing top-8 expert IDs and gate weights only;
2. determine the smallest subset whose cumulative normalized routing mass is `>= tau`;
3. minimum retained experts = 1, maximum = 8;
4. selection is by descending original gate weight, but mathematical expert execution/accumulation must preserve the original baseline order among retained experts;
5. renormalize only the retained gate weights to sum to the original selected routing mass/normalization convention used by the current runtime;
6. skipped expert payloads are not read/materialized/computed;
7. no route prediction, replacement experts, caching, or hidden SOURCE fallback.

No other routing modification is allowed.

## Stage 1 — tau = 0.95

Run fidelity oracle first.

If USABLE fidelity FAILs:
- record result;
- do not retain;
- continue to Stage 2 only as a measured frontier point.

If USABLE fidelity PASSes:
- run one fresh sustained performance test: prefill, 1 warmup, 32 measured tokens;
- record tok/s, p50/p95, average/min/max retained expert count per MoE layer, expert payload bytes/token, peak RSS, swap, fallback/cache/safety.

Candidate is eligible for final selection if:
- USABLE fidelity PASS;
- throughput `>=1.10 × 1.229233 tok/s`;
- peak RSS <= accepted exact runtime +64 MiB;
- swap delta <= accepted exact runtime +64 MiB;
- no unsafe pressure/fallback/persistent expert cache.

Do not yet stop if eligible; later thresholds may be faster.

## Stage 2 — tau = 0.90

Same procedure/gates as Stage 1.

## Stage 3 — tau = 0.80

Same procedure/gates as Stage 1.

## Stage 4 — tau = 0.70

Same procedure/gates as Stage 1.

This is the most aggressive authorized routing-mass variant. Do not test thresholds below `0.70`, fixed top-k reductions, or any post-hoc threshold.

## Stage 5 — choose fastest quality-valid sparsity point

Among all variants meeting at least USABLE fidelity and all safety gates:
- select the variant with highest measured sustained tok/s;
- break a throughput tie within 2% in favor of higher fidelity, then higher `tau`;
- if no variant meets USABLE fidelity + safety + minimum 10% speed gain, final class = `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`.

Record whether the selected variant is STRICT or USABLE fidelity.

## Stage 6 — bounded raw-I/O one-ahead overlap repair on selected variant

Precondition:
- a Stage-5 sparsity variant was selected;
- measured residual expert file I/O remains `>=20%` of decode wall.

Purpose: recover the positive `+8.45%` overlap signal seen in Speed Frontier 001 without reproducing its RSS failure.

Treatment is strictly bounded:
- at most one future expert raw payload may be in-flight/resident;
- no prefetched MLX arrays/tensors;
- no queue retaining multiple payloads;
- maximum additional intended raw payload storage = one `2,506,752 B` expert buffer plus bounded thread/future metadata;
- current expert compute/accumulation order unchanged;
- no speculative route prediction;
- no persistent multi-expert cache.

Require:
- selected sparsity fidelity tier remains unchanged within measurement tolerance and no new invalid logits;
- one fresh 32-token run;
- throughput gain `>=3%` versus selected sparsity implementation;
- peak RSS <= selected sparsity implementation +32 MiB;
- swap delta <= selected +32 MiB;
- no fallback/cache/unsafe pressure.

If PASS, retain cumulatively. Otherwise revert overlap only.

## Stage 7 — final sustained decision

Run exactly 3 fresh-process repetitions on the final selected implementation:
- prefill;
- 1 warmup token;
- exactly 32 measured decode tokens.

Record:
- tok/s each repetition and median;
- p50/p95 token wall;
- average retained experts/layer;
- expert payload bytes/token;
- peak RSS/swap/safety;
- final 128-position fidelity oracle metrics and tier.

Classification:
- `SPARSITY_5TPS_REACHED_QUALITY_GATED` iff median `>=5.0 tok/s`, final fidelity >= USABLE, and all safety gates PASS;
- `SPARSITY_FRONTIER_ADVANCED` iff median is `>=10%` above exact baseline `1.229233 tok/s`, final fidelity >= USABLE, safety PASS, but median <5.0 tok/s;
- `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN` iff no quality-valid/safe final implementation improves exact baseline by >=10%;
- `SPARSITY_FRONTIER_INCONCLUSIVE` only for genuine environment/instrumentation ambiguity.

## Hard bounds / efficiency

- no network/model download;
- no expert quantization change;
- no full-bank rebuild;
- no DFlash;
- no threshold rescue or variants outside `0.95/0.90/0.80/0.70`;
- no broad repository/history reread;
- reuse existing canonical/full-bank artifacts;
- deterministic JSON evidence;
- one compound funnel; no intermediate Git/human synchronization after execution begins;
- Pi may edit the committed canonical backend and directly required runtime code locally but must not commit/push/edit project decision docs;
- retain only the final selected quality-valid implementation and any Stage-6 overlap that independently passes its gate.

Evidence:
`results-local/research/30b-routing-sparsity-speed-quality-frontier-001/<UTC>/`

## After this checkpoint

If sustained throughput remains materially below `5 tok/s`, the next authorized high-leverage frontier should reduce bytes/expert using lower-bit expert quantization (Q3/Q2 or mixed precision) under a separate frozen quality gate, optionally combined only with the already selected routing-sparsity point.

Only after the current Qwen3-30B-A3B speed frontier is frozen should LOOM move to the Qwen3.8-27B / Qwen3.8-Flash-Next bake-off.
