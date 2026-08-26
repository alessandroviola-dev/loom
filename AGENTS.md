# LOOM — Pi Agent Protocol

Version: 3.29
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
- workload/provenance;
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
7. do not advance from stale AGENTS/HANDOFF/ROADMAP except inside a fully preregistered compound funnel as defined above;
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

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` = `SERVING_IO_BOTTLENECK_IDENTIFIED`.
External expert data-access is dominant:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- 384 expert reads, `962,592,768 B` payload;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority candidate remains lossless expert-major contiguous storage. No speedup claim until physical-I/O causality is valid.

## Expert-major physical-I/O history

A/B 001 is INVALID because repeated packed trials were cache-contaminated, although exact payload equality and structural read reduction `3456 -> 384` are valid.

Frozen physical-I/O validity authority: every accepted timed arm/repetition independently `>=80%` conservative physical coverage.

Fresh-inode byte-copy cold protocol is rejected (~21% coverage across three valid ~160-MiB trials).
Instrumentation persistence is repaired and PASS.
`F_GLOBAL_NOCACHE` semantics are resolved locally with fixed-ABI helper: SET 1 => raw 0/errno 0; RESET 0 => raw 1/errno 0.

### Global-nocache validation 002 — FAIL

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_002` = `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`.
Evidence: `results-local/research/30b-expert-major-global-nocache-cold-io-validation-002/20260826T141527Z/`.

Same packed region, three valid trials:
- T1 `96.0406%`, `0.251112 s`;
- T2 `25.8365%`, `0.226934 s`;
- T3 `23.9728%`, `0.228232 s`.

Payload/hash PASS 3/3; set/reset/restoration PASS 3/3; swap delta 0 B; minimum free memory 56%.
Conclusion: first touch can be strongly physical, but same-page repeated cold enforcement is rejected. Do not spend more runs on eviction/control variants for the same pages.

## Current checkpoint — COMPOUND DECISION FUNNEL

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_001`

Preregistration: `research/architecture/loom-30b-expert-major-decision-funnel-001-preregistration.md`.

Decision question: **Does expert-major contiguous storage provide enough causally valid physical-I/O improvement to justify runtime integration?**

Final outcomes:
- `EXPERT_MAJOR_GO`
- `EXPERT_MAJOR_NO_GO`
- `EXPERT_MAJOR_INCONCLUSIVE`

### Stage 0 — offline construction

Construct at least 3 mutually disjoint matched source/packed groups, preferably 64 expert payloads each (`160,432,128 B` per arm/group).
Every group must contain exactly the same ordered logical expert payload in both arms and must not reuse source or packed payload pages used by another repetition.
If 3 valid non-reuse groups cannot be constructed: `EXPERT_MAJOR_INCONCLUSIVE` and STOP.

### Stage 1 — decisive paired first-touch A/B

Exactly 3 matched pairs; frozen arm order: `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`.
Each group is touched once only.
Use established fixed-ABI global-nocache controls and complete repaired instrumentation.

Every arm/repetition must PASS:
- conservative physical coverage `>=80%`;
- exact payload/hash equality;
- complete arithmetic-consistent evidence;
- control set/reset/restoration;
- swap delta `<=16,000,000 B`;
- free memory `>=10%`;
- no unsafe memory pressure;
- matched logical bytes and expected read-count structure.

Any invalid arm => `EXPERT_MAJOR_INCONCLUSIVE`.

Primary statistic: paired ratio `packed_wall/source_wall`; decision statistic = median of 3 paired ratios.

`EXPERT_MAJOR_GO` only if valid and:
- median paired ratio `<=0.70`;
- packed conservative physical bytes `<=1.05x` source in every pair;
- no exactness/read-structure regression.

`EXPERT_MAJOR_NO_GO` if comparison is valid but median paired ratio `>0.70`, or valid evidence shows unacceptable physical-byte/read-structure regression.

Bounds:
- no model forward/network/DFlash/runtime edits;
- no purge/reboot/cache-thrash/RAM-fill/swap eviction/fresh-copy workaround;
- max 3 matched pairs;
- timed logical payload <= `962,592,768 B` total across both arms;
- no intermediate human/Git synchronization inside the frozen funnel.

If final outcome is GO, the next phase should likewise bundle runtime integration + exactness + bounded end-to-end benchmark into one preregistered compound WP rather than returning to micro-test iteration.
