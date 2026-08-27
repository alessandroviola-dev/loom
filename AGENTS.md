# LOOM — Pi Agent Protocol

Version: 3.42
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

A fully preregistered compound funnel may traverse internal stages without intermediate Git/pull only when question, outcomes, branches, gates, workload/fallback order, resource bounds and fail-closed behavior are frozen before execution.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue or post-hoc gate relaxation;
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
13. static adapter dry-run with zero unresolved accesses and forbidden fallback must PASS before model forward;
14. benchmark/trace-scoped artifacts are not promoted implicitly to runtime artifacts;
15. metadata/coverage/provenance checks use deterministic scripts/JSON where possible;
16. settled mechanisms are not reopened absent regression/materially different target;
17. production regressions require a new bounded preregistered repair;
18. validation-only metadata stays out of hot runtime when representable by a smaller contract;
19. accepted production code is canonical only after review and Git persistence;
20. quality-trading speed work freezes fidelity metrics/thresholds before candidate results;
21. verifier-ceiling experiments using oracle proposals are upper bounds only and must never be reported as production generation speed.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Stable target / accepted runtime

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

Canonical backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Current exact-Q4 speed baseline commit:
`96958de` — `perf: keep packed expert file descriptor open`.
Validated file SHA-256:
`6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

Accepted exact sustained throughput:
`1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

## Settled speed work

### Expert-major — ACCEPTED / CANONICAL / CLOSED

Physical-I/O `EXPERT_MAJOR_GO`; full-bank runtime `EXPERT_MAJOR_RUNTIME_GO`; canonicalization `EXPERT_MAJOR_CANONICALIZATION_GO` with `FORMULAIC_RESOLVER`.

### Exact-Q4 Speed Frontier 001 — ADVANCED / PERSISTED

Only process-lifetime PACKED fd retained. Stage-0 attribution before this delta:
- expert file I/O `44.61%`;
- expert compute `26.50%`;
- backbone `14.74%`;
- materialization/sync `11.51%`;
- routing `2.64%`.

### Routing Sparsity Frontier 001 — CLOSED / NO ACCEPTABLE GAIN

`SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`.
Quality-valid tau `.95/.90` were not faster; `.80/.70` failed fidelity. Do not retry adjacent tau/fixed-top-k without a new hypothesis.

### Lower-Bit Expert Frontier 001 — CLOSED / NO ACCEPTABLE GAIN

`LOOM_30B_LOWER_BIT_EXPERT_SPEED_QUALITY_FRONTIER_001 = EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`.

Result:
`research/architecture/loom-30b-lower-bit-expert-speed-quality-frontier-001-result.md`

Evidence:
`results-local/research/30b-lower-bit-expert-speed-quality-frontier-001/20260827T144620Z/`

Local stack: MLX `0.32.0`, mlx-lm `0.31.3`; Q2 and Q3 native at group size 128.
Both complete lower-bit banks built and passed `6144/6144` + `18,048/18,048` replay with zero fallback/cache.

Q2:
- expert `1,327,104 B`;
- bank `8,153,726,976 B`;
- traffic `509,607,936 B/token`;
- fidelity: top1 `84.375%`, top3 `96.094%`, KL `0.426378` => FAIL.

Q3:
- expert `1,916,928 B`;
- bank `11,777,605,632 B`;
- traffic `736,100,352 B/token`;
- fidelity: top1 `87.500%`, top3 `100%`, KL `0.150060` => FAIL.

No sustained speed benchmark was allowed because both failed USABLE fidelity. No tracked runtime code changed. Q4 remains production baseline.

Do not adopt Q2/Q3 or relax fidelity gates post hoc.

## Current checkpoint — LOSSLESS SPECULATIVE VERIFICATION CEILING 001

`LOOM_30B_LOSSLESS_SPECULATIVE_VERIFICATION_CEILING_001`

Preregistration:
`research/architecture/loom-30b-lossless-speculative-verification-ceiling-001-preregistration.md`

Purpose: before downloading/building any real drafter, measure the exact verifier-only throughput ceiling under perfect oracle proposals.

Frozen candidate chunk sizes only:
- `K=2`;
- `K=4`;
- `K=8`.

Requirements:
- canonical Q4/top-8 semantics unchanged;
- oracle proposals are exact greedy teacher tokens and imply 100% acceptance only for ceiling measurement;
- causal/KV behavior equivalent to sequential decode;
- routed identities and per-token accumulation exact;
- raw float32 final-logit SHA must match sequential reference;
- no lower-bit bank, routing sparsity, real drafter, DFlash, network/model download;
- within-chunk reuse of one loaded expert is allowed only for the same expert identity required at multiple positions, without persistent cache.

For each valid K measure 32 verified output tokens, expert unique loads/bytes per output token, reuse rate, wall attribution, RSS/swap/safety.

Best K gets final `3×32` confirmation.

Classification:
- `SPEC_VERIFY_5TPS_CEILING_REACHED` if median >=5 tok/s;
- `SPEC_VERIFY_FRONTIER_PROMISING` if median >=2.458466 tok/s but <5;
- `SPEC_VERIFY_FRONTIER_NOT_PROMISING` if valid ceiling <2.458466 tok/s;
- `SPEC_VERIFY_FRONTIER_INCONCLUSIVE` only for genuine runtime/API/instrumentation ambiguity.

Oracle-ceiling tok/s is NOT production speed.

## Strategic next

If ceiling is promising/reaches 5: preregister a real lossless drafter frontier, starting with zero-download n-gram/prompt lookup where applicable, then a small tokenizer-compatible Qwen-family drafter only if justified by the measured ceiling.

If ceiling is not promising: stop optimizing this verifier with speculative decoding and move to the planned Qwen3.8-27B / Qwen3.8-Flash-Next bake-off or a materially different verifier architecture.
