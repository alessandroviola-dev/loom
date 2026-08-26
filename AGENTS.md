# LOOM — Pi Agent Protocol

Version: 3.32
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git/push/PR/edit project docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

### Compound preregistered funnel exception

A single Pi WP may traverse multiple internal stages without intermediate Git/pull only when question, final outcomes, branch logic, quantitative gates, workload/fallback order, resource bounds and fail-closed behavior are frozen before execution. No scientific rescue or threshold/workload change after results begin.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. comparison invalid if more than intended treatment factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. do not advance from stale canonical docs except inside a fully preregistered compound funnel;
8. required gate instrumentation must persist before timed evidence is accepted;
9. failed frozen methods are not silently modified/rerun under the same checkpoint;
10. control/API semantics affecting validity must be established locally;
11. **Integration Readiness Protocol v1 is mandatory before integration coding/model forward**: `research/architecture/loom-integration-readiness-protocol-v1.md`;
12. producer/consumer compatibility must be proven mechanically before adapter coding: `consumer_required_coverage ⊆ provider_available_coverage`;
13. static adapter dry-run with zero unresolved accesses and zero forbidden fallback must PASS before model forward;
14. benchmark/trace-scoped artifacts must not be implicitly promoted to general runtime artifacts;
15. metadata/coverage/provenance checks should be deterministic scripts/JSON, not broad Pi reasoning/repository exploration.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Mission / stable 30B target

Mission: **Big models. Small machines.** Practical ~27B/32B local AI on Apple M1/8GB.
Q4 target: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Stable facts:
- 48 MoE layers, 128 experts/layer, top-k 8;
- routed identities `48 × 128 = 6144`;
- payload `16,220,499,968 B`;
- resident non-routed `819,015,680 B`;
- routed bank `15,401,484,288 B`;
- Q4 expert `2,506,752 B`;
- BF16 KV `98,304 B/token`;
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- raw 4-GiB global LRU rejected.

## DFlash — CLOSED

Final: `BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`. Do not reopen absent a new independent mechanism.

## Core serving/I/O

External expert data-access is dominant:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- 384 expert reads, `962,592,768 B` payload;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

## Expert-major physical-I/O — ACCEPTED

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002` = `EXPERT_MAJOR_GO`.
Result: `research/architecture/loom-30b-expert-major-decision-funnel-002-result.md`.
Evidence: `results-local/research/30b-expert-major-decision-funnel-002/20260826T144530Z/`.

Three valid first-touch pairs:
- ratios `0.602456`, `0.595950`, `0.581170`;
- median `0.595950` = `40.405%` lower expert-access wall;
- physical coverage ~95.37–100.87%;
- payload/hash PASS;
- reads `576 -> 64` per 64-expert group;
- zero swap; minimum free memory 55%.

Raw expert-major physical-I/O causality is settled and positive.

## Runtime Funnel 001 — INCONCLUSIVE BEFORE MODEL FORWARD

`LOOM_30B_EXPERT_MAJOR_RUNTIME_FUNNEL_001` = `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`.
Result: `research/architecture/loom-30b-expert-major-runtime-funnel-001-result.md`.
Evidence: `results-local/research/30b-expert-major-runtime-funnel-001/20260826T150012Z/`.

Selected workload: `LOOM_30B_MOE_REAL_RAW_CACHE_001` SOURCE control, P1 canonical sequence (`20260824T092553Z`).

Stage 0 failed manifest coverage before any model forward:
- retained pack contains only 384 experts from a different single decode position;
- runtime consumer requires prefill + consecutive decode coverage;
- no exactness/performance/RSS/swap stages ran.

Interpretation: artifact-scope/readiness failure, not evidence against expert-major. The 384-expert pack is a benchmark/trace artifact and is not runtime-complete.

## Current checkpoint — FULL-BANK COMPOUND RUNTIME FUNNEL 002

`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002`

Preregistration:
`research/architecture/loom-30b-expert-major-fullbank-runtime-funnel-002-preregistration.md`

Protocol:
`research/architecture/loom-integration-readiness-protocol-v1.md`

Final outcomes only:
- `EXPERT_MAJOR_RUNTIME_GO`
- `EXPERT_MAJOR_RUNTIME_NO_GO`
- `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`

### Stage 0 — compile-time contract

No coding/model forward.
- freeze the selected canonical workload;
- emit machine-readable provider/consumer contracts;
- prove source availability for all `6144/6144` experts;
- prove model/revision/format/ABI/dtype/quantization compatibility;
- require >=20 GiB destination free space;
- reuse a full-bank artifact only if complete compatible manifest already PASSes.

### Stage 1 — build/reuse full routed-bank expert-major artifact

Target:
- all `6144` experts;
- deterministic `(layer_id, expert_id)` order;
- `2,506,752 B/expert`;
- total `15,401,484,288 B`;
- contiguous per-expert payload;
- manifest key -> offset/size/source hash/packed hash;
- resumable/checkpointed build;
- full `6144/6144` coverage and integrity verification.

### Stage 2 — static compatibility / adapter dry-run

Still no model forward.
- mechanically prove consumer coverage subset;
- replay complete retained access sequence against manifest;
- every access resolves exactly once;
- zero SOURCE fallback;
- only then create isolated treatment adapter;
- treatment changes only expert data-access backend/layout;
- no persistent expert cache.

### Stage 3 — exactness

Exactly 3 forced consecutive decode positions through all 48 layers.
Require identical routed expert order and identical raw final-logit float32 SHA SOURCE vs PACKED, with mapping/hash PASS and no fallback/cache/safety regression.

Valid exactness failure => `EXPERT_MAJOR_RUNTIME_NO_GO`.

### Stage 4 — practical runtime A/B

No artificial cache manipulation. Exactly three fresh-process pairs:
- `SOURCE -> PACKED`
- `PACKED -> SOURCE`
- `SOURCE -> PACKED`

Per arm: prefill, one unmeasured warmup decode, exactly three measured decode tokens; record aggregate wall, RSS, pressure, swap, routing/backend status.

Safety:
- no persistent expert cache;
- median PACKED peak RSS <= median SOURCE +128 MiB;
- PACKED swap delta <= matched SOURCE +64 MiB;
- no unsafe memory pressure.

GO iff all artifact/static/exactness/safety gates PASS and median `PACKED/SOURCE measured decode wall <=0.90`.

NO-GO for valid artifact/exactness/safety failure or valid runtime ratio >0.90.

INCONCLUSIVE only for genuine environment/instrumentation/resource ambiguity.

Pi token economy: use deterministic scripts for metadata/coverage/hash work, read only directly relevant files, do not re-derive settled evidence, and stop immediately on a known compatibility failure.
