# LOOM — Pi Agent Protocol

Version: 3.41
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

A fully preregistered compound funnel may traverse internal stages without intermediate Git/pull only when question, outcomes, branches, quantitative gates, workload/fallback order, resource bounds and fail-closed behavior are frozen before execution.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. comparison invalid if more than intended treatment factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. do not advance from stale canonical docs except inside a fully preregistered compound funnel;
8. required gate instrumentation must persist before evidence is accepted;
9. failed frozen methods are not silently modified/rerun under the same checkpoint;
10. control/API semantics affecting validity must be established locally;
11. Integration Readiness Protocol v1 is mandatory before integration coding/model forward: `research/architecture/loom-integration-readiness-protocol-v1.md`;
12. producer/consumer compatibility must be proven mechanically before adapter coding;
13. static adapter dry-run with zero unresolved accesses and zero forbidden fallback must PASS before model forward;
14. benchmark/trace-scoped artifacts must not be promoted implicitly to general runtime artifacts;
15. metadata/coverage/provenance checks should use deterministic scripts/JSON rather than broad Pi reasoning;
16. settled mechanisms are not reopened absent regression or materially different target/runtime;
17. production regressions require a new bounded preregistered repair with original thresholds unchanged;
18. validation-only metadata/provenance stays out of the hot runtime when representable by a smaller runtime contract;
19. accepted production code is canonical only after review and Git persistence;
20. quality-trading speed work must freeze fidelity metrics/thresholds before candidate results are observed.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Mission / stable target

Mission: **Big models. Small machines.** Practical large open-weight AI on Apple M1/8GB.
Current target: `Qwen3-30B-A3B` MLX Q4.

Stable facts:
- 48 MoE layers, 128 experts/layer, top-k 8;
- routed identities `6144`;
- Q4 routed bank `15,401,484,288 B`;
- Q4 expert `2,506,752 B`;
- full top-8 expert traffic/token `962,592,768 B`;
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- DFlash closed;
- raw 4-GiB LRU rejected.

## Expert-major — ACCEPTED / CANONICAL / CLOSED

Physical-I/O: `EXPERT_MAJOR_GO`.
Accepted full-bank runtime: `EXPERT_MAJOR_RUNTIME_GO`.
Canonicalization: `EXPERT_MAJOR_CANONICALIZATION_GO` with `FORMULAIC_RESOLVER`.

Canonical backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Base canonicalization commit: `36414d7`.
Current exact-Q4 speed baseline commit: `96958de` (`perf: keep packed expert file descriptor open`).
Validated file SHA-256: `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

Do not reopen expert-major validation absent regression/new target.

## Exact-Q4 Speed Frontier 001 — ADVANCED / PERSISTED

`LOOM_30B_POST_CANONICAL_SPEED_FRONTIER_001 = SPEED_FRONTIER_ADVANCED`.

Result:
`research/architecture/loom-30b-post-canonical-speed-frontier-001-result.md`

Evidence:
`results-local/research/30b-post-canonical-speed-frontier-001/20260827T131329Z/`

Stage-0 sustained baseline: `1.063941 tok/s`.
Final exact 3×32-token throughput: `1.115874`, `1.229233`, `1.254611`; median `1.229233 tok/s`.

Ranked Stage-0 wall:
- expert file I/O `44.61%`;
- expert compute `26.50%`;
- non-expert/backbone `14.74%`;
- materialization/synchronization `11.51%`;
- routing `2.64%`.

Only process-lifetime PACKED fd was retained (`+8.65%`, exact/safe). Sync collapse, copy reduction, and one-ahead variants were reverted.

The exact-Q4 baseline is I/O-bound; `5 tok/s` at top-8 Q4 implies ~`4.81 GB/s` expert payload traffic before other work.

## Routing Sparsity Frontier 001 — CLOSED / NO ACCEPTABLE GAIN

`LOOM_30B_ROUTING_SPARSITY_SPEED_QUALITY_FRONTIER_001 = SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`.

Result:
`research/architecture/loom-30b-routing-sparsity-speed-quality-frontier-001-result.md`

Evidence:
`results-local/research/30b-routing-sparsity-speed-quality-frontier-001/20260827T135848Z/`

Frozen Q4 teacher oracle: 8 prompts ×16 positions = 128 positions.

Measured:
- `tau=.95`: STRICT, 7.8757 experts/layer, `947,630,592 B/token`, `1.216703 tok/s`, `-1.02%`;
- `tau=.90`: STRICT, 6.9440 experts/layer, `835,531,776 B/token`, `1.223280 tok/s`, `-0.48%`;
- `tau=.80`: fidelity FAIL, mean KL `0.113882`;
- `tau=.70`: fidelity FAIL, top1 `87.5%`, mean KL `0.331111`.

No tau selected; no tracked runtime code changed. Residual expert I/O at quality-valid tau=.90 remained `38.23%`.

Interpretation: routing mass is too distributed across top-8. Quality-valid truncation removes too little work; aggressive truncation loses fidelity first. Do not retry adjacent tau/fixed-top-k variants without a materially new hypothesis.

## Current checkpoint — LOWER-BIT EXPERT SPEED/QUALITY FRONTIER 001

`LOOM_30B_LOWER_BIT_EXPERT_SPEED_QUALITY_FRONTIER_001`

Preregistration:
`research/architecture/loom-30b-lower-bit-expert-speed-quality-frontier-001-preregistration.md`

Goal: lower bytes/compute per executed expert while keeping full top-8 routing.

Frozen baseline:
- commit `96958de`;
- exact-Q4 median `1.229233 tok/s`;
- same 128-position Q4 teacher oracle.

Candidate set is capability-gated locally:
- `Q3` only if installed MLX natively supports bits=3 with the current group-size/shape contract;
- `Q2` only if installed MLX natively supports bits=2 with the current group-size/shape contract.

No group-size search, mixed precision, custom kernel, BF16 substitution, routing sparsity, or speculative decoding in this checkpoint.

Source for target requantization is the deployed Q4 expert representation. Full accepted Q4 artifacts are immutable.

For supported candidates:
1. local capability/round-trip pilot;
2. resumable full `6144/6144` lower-bit expert-major bank;
3. static integrity + `18,048` replay, zero fallback/cache;
4. same 128-position fidelity oracle;
5. 32-token sustained speed only if fidelity >=USABLE;
6. fastest eligible candidate selected;
7. final `3×32` sustained decision.

USABLE fidelity unchanged:
- top1 >=90%;
- teacher top1 in candidate top3 >=97%;
- mean KL <=0.10;
- finite logits.

STRICT unchanged:
- top1 >=95%;
- top3 >=99%;
- KL <=0.05.

Eligible also requires >=10% speed gain over `1.229233 tok/s` and RSS/swap/safety PASS.

Final classes:
- `EXPERT_QUANT_5TPS_REACHED_QUALITY_GATED`;
- `EXPERT_QUANT_FRONTIER_ADVANCED`;
- `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`;
- `EXPERT_QUANT_FRONTIER_INCONCLUSIVE`.

## Strategic next

If lower-bit experts advance speed but remain materially below `5 tok/s`, freeze the best quality-valid lower-bit verifier and then test an independent speculative-decoding frontier. The path to 5 tok/s is expected to be cumulative: fewer bytes/compute per verifier token plus more accepted output tokens per verifier step.

After the current Qwen3-30B-A3B speed frontier is frozen, execute the planned same-hardware bake-off against Qwen3.8-27B and Qwen3.8-Flash-Next on speed, memory, intelligence/quality and steerability/refusal behavior.
