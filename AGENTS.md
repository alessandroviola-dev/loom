# LOOM — Pi Agent Protocol

Version: 3.31
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git/push/PR/edit project docs unless explicitly authorized.

After every **significant scientific checkpoint**, ChatGPT updates canonical project state on GitHub and the user pulls before the next independent Pi WP.

### Compound preregistered funnel exception

A single Pi WP may contain multiple internal stages/gates and advance through them automatically **without intermediate Git/pull cycles** only when all of the following are frozen before execution:
- scientific question and final outcomes;
- stage order and branch logic;
- quantitative PASS/FAIL/INCONCLUSIVE gates;
- workload/provenance and deterministic fallback order;
- cost/traffic/runtime bounds;
- fail-closed behavior.

No threshold, causal factor, workload, rescue, or branch may be changed after results begin arriving. Any such change ends the funnel and requires a new checkpoint.

Rules:
1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. treatment comparison invalid if more than intended factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. do not advance from stale AGENTS/HANDOFF/ROADMAP except inside a fully preregistered compound funnel;
8. instrumentation required by a gate must persist successfully before a timed result can be accepted;
9. failed frozen methods must not be silently modified and rerun under the same checkpoint;
10. control/API return values affecting scientific validity must be established locally, not inferred from convention.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Mission / stable 30B target

Mission: **Big models. Small machines.** Practical ~27B/32B local AI on Apple M1/8GB.
Q4 target: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Stable facts:
- 48 MoE layers, 128 experts/layer, top-k 8;
- payload `16,220,499,968 B`;
- resident non-routed `819,015,680 B`;
- routed bank `15,401,484,288 B`;
- Q4 expert `2,506,752 B`;
- BF16 KV `98,304 B/token`;
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- raw 4-GiB global LRU rejected.

## DFlash — CLOSED AS ACTIVE PATH

Final: `BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`. Do not reopen absent a new independent mechanism.

## Core serving/I/O — BOTTLENECK IDENTIFIED

External expert data-access is dominant:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- 384 expert reads, `962,592,768 B` payload;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

## Physical-I/O history

- A/B 001: INVALID due cache contamination; exact payload equality and structural read reduction `3456 -> 384` remain valid.
- Every accepted timed physical-I/O arm requires `>=80%` conservative physical coverage.
- Fresh-inode byte-copy cold protocol rejected (~21% coverage).
- Instrumentation persistence repaired and PASS.
- `F_GLOBAL_NOCACHE` semantics resolved locally: SET 1 => raw 0/errno 0; RESET 0 => raw 1/errno 0.
- Same-page global-nocache repetition rejected: first touch `96.0406%`, repeats `25.8365%` and `23.9728%`.

## Decision Funnel 001 — INCONCLUSIVE

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_001` = `EXPERT_MAJOR_INCONCLUSIVE`.
Result: `research/architecture/loom-30b-expert-major-decision-funnel-001-result.md`.
Reason: trace-order groups were not contiguous in packed physical order; no timing ran.

## Decision Funnel 002 — EXPERT_MAJOR_GO

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002` = `EXPERT_MAJOR_GO`.
Result: `research/architecture/loom-30b-expert-major-decision-funnel-002-result.md`.
Evidence: `results-local/research/30b-expert-major-decision-funnel-002/20260826T144530Z/`.

Stage 0 PASS:
- 3 x 64-expert groups;
- `160,432,128 B/arm/group`;
- exact matched logical payload;
- zero SOURCE/PACKED cross-group overlap.

Valid paired first-touch physical-I/O results:
- Pair 1 ratio `0.602456` (`0.425011 s` SOURCE vs `0.256050 s` PACKED);
- Pair 2 ratio `0.595950` (`0.423898 s` vs `0.252622 s`);
- Pair 3 ratio `0.581170` (`0.425366 s` vs `0.247210 s`).

Median paired wall ratio: `0.595950` = `40.405%` lower access wall.

All six arms PASS:
- physical coverage ~`95.37–100.87%`;
- whole-group payload/hash exactness;
- read structure `576 -> 64` per group;
- packed/source conservative physical-byte ratios `0.947801`, `0.952811`, `0.945495`;
- control validity;
- zero swap delta;
- minimum free memory `55%`.

Interpretation: expert-major contiguous storage is now causally validated for raw external-expert physical I/O and is accepted for isolated runtime integration testing.

## Current checkpoint — COMPOUND RUNTIME FUNNEL 001

`LOOM_30B_EXPERT_MAJOR_RUNTIME_FUNNEL_001`

Preregistration: `research/architecture/loom-30b-expert-major-runtime-funnel-001-preregistration.md`.

Decision question: **Does replacing only the external expert data-access backend with expert-major preserve exact runtime semantics and improve practical end-to-end decode enough to justify canonical adoption on M1/8GB?**

Final outcomes only:
- `EXPERT_MAJOR_RUNTIME_GO`
- `EXPERT_MAJOR_RUNTIME_NO_GO`
- `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`

### Stage 0 — isolated integration

- inspect current exact external serial-expert runtime and retained pack/manifest;
- deterministically select the most recent existing canonical exact-runtime workload supporting final-logit capture and decode timing;
- create only an isolated experimental adapter/workspace under `results-local/`;
- SOURCE baseline remains unchanged;
- PACKED changes only expert data-access layout/backend;
- routing, expert math, quantization, dtypes, KV, non-routed weights, input tokens, scheduling/synchronization and output computation remain unchanged;
- no persistent expert cache; one routed expert logically live at a time;
- validate mapping/manifest coverage before model forward.

If one-factor isolation cannot be established: `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`.

### Stage 1 — exactness

Same forced/frozen token sequence for SOURCE and PACKED at three consecutive full 48-layer decode positions.
Require:
- identical routed expert IDs/order;
- expert payload mapping/hash PASS;
- identical raw final-logit float32 SHA at all 3 positions;
- no PACKED fallback to SOURCE;
- no persistent expert cache;
- no unsafe memory pressure.

Valid exactness failure => `EXPERT_MAJOR_RUNTIME_NO_GO`.
Measurement ambiguity => `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`.

### Stage 2 — practical end-to-end performance/safety

No artificial cache-state manipulation. Exactly 3 process-level matched pairs, frozen order:
- Pair 1 `SOURCE->PACKED`
- Pair 2 `PACKED->SOURCE`
- Pair 3 `SOURCE->PACKED`

Per arm:
- fresh runtime process;
- same frozen model/input/token sequence/settings;
- one unmeasured decode warmup token after prefill;
- exactly three measured decode tokens;
- record measured decode wall, peak RSS, memory pressure, swap, routing/backend status;
- close process before next arm.

Safety gates:
- no persistent expert cache;
- median PACKED peak RSS <= median SOURCE peak RSS + `128 MiB`;
- PACKED swap delta <= matched SOURCE swap delta + `64 MiB` in every pair;
- no unsafe memory pressure.

Primary runtime ratio per pair: `packed_measured_decode_wall/source_measured_decode_wall`.
Decision statistic: median of three ratios.

`EXPERT_MAJOR_RUNTIME_GO` only if exactness and safety PASS and median runtime ratio `<=0.90` (>=10% practical decode-wall improvement).

`EXPERT_MAJOR_RUNTIME_NO_GO` if evidence is valid but exactness/safety fails or median runtime ratio `>0.90`.

`EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` only for genuine integration/environment/instrumentation ambiguity.

Bounds:
- no network/model download;
- no DFlash;
- no cache/eviction experiments;
- no project docs/Git edits by Pi;
- isolated experimental integration only;
- 3 exactness decode positions max;
- exactly 3 performance pairs;
- one warmup + 3 measured decode tokens/arm;
- no rescue repetitions;
- total runtime wall cap `360 s`;
- stop on unsafe memory pressure.

If GO, expert-major becomes the accepted runtime direction and can be productionized/canonicalized using this evidence.
