# LOOM — Pi Agent Protocol

Version: 3.30
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

Priority candidate remains lossless expert-major contiguous storage. No speedup claim until physical-I/O causality is valid.

## Physical-I/O history

- A/B 001: INVALID due cache contamination; exact payload equality and structural read reduction `3456 -> 384` remain valid.
- Every accepted timed arm/repetition requires `>=80%` conservative physical coverage.
- Fresh-inode byte-copy cold protocol rejected (~21% coverage).
- Instrumentation persistence repaired and PASS.
- `F_GLOBAL_NOCACHE` semantics resolved locally: SET 1 => raw 0/errno 0; RESET 0 => raw 1/errno 0.
- Same-page global-nocache repetition rejected: first touch `96.0406%`, repeats `25.8365%` and `23.9728%`.

## Decision Funnel 001 — INCONCLUSIVE

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_001` = `EXPERT_MAJOR_INCONCLUSIVE`.
Result: `research/architecture/loom-30b-expert-major-decision-funnel-001-result.md`.
Evidence: `results-local/research/30b-expert-major-decision-funnel-001/20260826T143324Z/`.

Stage 0 found three 64-expert groups (`160,432,128 B/arm`) with zero source/packed cross-group overlap and retained metadata PASS, but the groups were selected in canonical trace order and were not contiguous in packed physical order. No timing ran.

Interpretation: measurement-design failure only. No evidence for or against expert-major performance.

## Current checkpoint — COMPOUND DECISION FUNNEL 002

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002`

Preregistration: `research/architecture/loom-30b-expert-major-decision-funnel-002-preregistration.md`.

Decision question: **Does expert-major contiguous storage provide enough causally valid physical-I/O improvement to justify runtime integration?**

Final outcomes only:
- `EXPERT_MAJOR_GO`
- `EXPERT_MAJOR_NO_GO`
- `EXPERT_MAJOR_INCONCLUSIVE`

### Stage 0 — deterministic packed-first construction

Use retained metadata only; no payload read before timing.

1. enumerate packed expert entries by ascending physical offset;
2. exclude regions recently re-touched by global-nocache validation;
3. choose first three disjoint contiguous packed blocks of 64 entries;
4. map those exact expert IDs/order to SOURCE nine-range representation;
5. validate exact retained payload/hash provenance and zero cross-group overlaps;
6. if 64 fails, frozen fallback sizes are 32 then 16 experts/group; use the largest size yielding exactly 3 valid groups;
7. if none of `{64,32,16}` works: `EXPERT_MAJOR_INCONCLUSIVE` and STOP.

Expected reads/group for N experts: SOURCE `9*N`, PACKED `N`.

### Stage 1 — decisive paired first-touch A/B

Exactly 3 matched groups, used once only. Frozen arm order:
- Pair 1 `SOURCE->PACKED`
- Pair 2 `PACKED->SOURCE`
- Pair 3 `SOURCE->PACKED`

Every arm independently requires:
- conservative physical coverage `>=80%`;
- payload/hash PASS;
- complete arithmetic-consistent evidence;
- established fixed-ABI control set/reset/restoration PASS;
- swap delta `<=16,000,000 B`;
- free memory `>=10%`;
- no unsafe memory pressure;
- matched logical bytes;
- observed read structure SOURCE `9*N`, PACKED `N`.

Any invalid arm => `EXPERT_MAJOR_INCONCLUSIVE` and STOP.

Primary statistic: paired `packed_wall/source_wall`; decision statistic = median of 3 paired ratios.

`EXPERT_MAJOR_GO` only if valid and:
- median paired ratio `<=0.70`;
- packed conservative physical bytes `<=1.05x` source in every pair;
- no exactness/read-structure regression.

`EXPERT_MAJOR_NO_GO` if valid but median ratio `>0.70`, or valid evidence shows unacceptable physical-byte/read-structure regression.

Bounds:
- no model forward/network/DFlash/runtime edits;
- no purge/reboot/cache-thrash/RAM-fill/swap eviction/fresh-copy workaround;
- max 3 pairs;
- max group size 64 experts;
- total timed logical payload <= `962,592,768 B` for 64-expert groups, proportionally lower for fallback sizes;
- no intermediate human/Git sync inside the frozen funnel.

If GO, next phase should be one compound runtime funnel bundling isolated integration + exactness + safety + bounded end-to-end benchmark.
