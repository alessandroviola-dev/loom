# LOOM — Pi Agent Protocol

Version: 3.28
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git/push/PR/edit project docs unless explicitly authorized.

After every **significant scientific checkpoint**, ChatGPT updates canonical project state on GitHub and the user pulls before the next Pi WP. Significant checkpoints include classification change, accepted/invalid/unresolved experiment, frozen baseline change, branch-direction change, or selection of a new next checkpoint.

Rules:
1. one-factor experiments; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. treatment comparison invalid if more than intended factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID or UNRESOLVED evidence;
7. do not advance from stale AGENTS/HANDOFF/ROADMAP;
8. instrumentation required by a gate must persist successfully before a timed result can be accepted;
9. a failed frozen method must not be silently modified and rerun under the same checkpoint;
10. control/API return values that affect scientific validity must be established locally, not inferred from convention.

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

Final: `BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`.
Do not reopen absent a new independent mechanism.

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

Frozen cold timing gate: every accepted timed repetition must independently show `>=80%` conservative physical coverage.

Fresh-inode byte-copy cold protocol is rejected: three valid ~160-MiB trials achieved only ~21% coverage.

Instrumentation persistence repair is PASS.

`F_GLOBAL_NOCACHE` set/reset semantics are resolved locally using a fixed-ABI helper:
- SET 1: raw 0, errno 0;
- RESET 0: raw 1, errno 0;
- transactional restoration verification PASS.

## Global-nocache cold-I/O validation 002 — FAIL

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_002` = `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`.
Report: `research/architecture/loom-30b-expert-major-global-nocache-cold-io-validation-002-result.md`.
Evidence: `results-local/research/30b-expert-major-global-nocache-cold-io-validation-002/20260826T141527Z/`.

Same packed region, three valid trials:
- T1: `96.0406%`, `0.251112 s`, `154,260,000 / 154,080,000 B` raw/conservative physical;
- T2: `25.8365%`, `0.226934 s`, `41,810,000 / 41,450,000 B`;
- T3: `23.9728%`, `0.228232 s`, `39,020,000 / 38,460,000 B`.

Other gates:
- payload/hash PASS 3/3;
- initial set/reset/restoration PASS 3/3;
- swap delta 0 B 3/3;
- minimum free memory 56%.

Interpretation:
- control semantics and instrumentation are no longer blockers;
- first touch can be strongly physical;
- repeated touches of the same region remain cache-served;
- direct global-nocache repeated-same-payload cold enforcement is rejected;
- do not keep adding eviction/control variants to the same-pages protocol.

## Current checkpoint

`LOOM_30B_FIRST_TOUCH_NONREUSE_IO_DESIGN_001`

Goal: design a valid physical-I/O comparison that avoids reusing already-touched pages instead of trying to evict them.

Analysis-first requirements:
1. no model forward/network/DFlash/runtime integration/full performance A/B;
2. inspect packed layout, source ranges, retained traces and expert identities to determine how many mutually disjoint matched source/packed payload groups can be constructed;
3. each candidate repetition must compare exactly the same logical expert payload between source and packed arms while not reusing payload pages from earlier repetitions;
4. preserve one-factor causality: only storage layout/read fragmentation may differ within a matched pair;
5. quantify total unique logical bytes, offsets/ranges, overlap between repetitions and expected RAM/cache interaction;
6. retain per-arm/per-repetition `>=80%` conservative physical-coverage validity authority;
7. rank at most 2 non-reuse designs and select exactly one;
8. preregister a minimal packed-only or paired validation before full A/B;
9. avoid RAM-fill/cache-thrash, swap pressure, purge/reboot dependence, copied fresh files, or unverifiable cache-state assumptions;
10. do not execute a large validation in this design checkpoint; at most one <=32-MiB metadata/semantics probe if mechanically necessary.

Preferred direction to evaluate first:
- disjoint first-touch expert subsets/regions across repetitions, with source and packed matched on exact payload bytes for each repetition.

Classification:
- `FIRST_TOUCH_NONREUSE_IO_DESIGN_SELECTED`
- `FIRST_TOUCH_NONREUSE_IO_DESIGN_INSUFFICIENT`

Only after a selected design passes a separately preregistered physical-coverage validation may `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_002` be considered.
