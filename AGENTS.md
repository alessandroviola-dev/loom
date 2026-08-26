# LOOM — Pi Agent Protocol

Version: 3.27
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
Report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.
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

Frozen cold timing gate: every accepted repetition must independently show `>=80%` conservative physical coverage.

Fresh-inode byte-copy cold protocol is rejected: three valid 160,432,128-B trials achieved only `21.7537%`, `21.6914%`, `20.8250%` coverage; payload/hash PASS; zero swap.

Instrumentation persistence repair is PASS.

Measurement redesign selected direct reads of the existing packed payload with `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0`.

## Global-nocache validation 001 — protocol FAIL, coldness positive

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001` = `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`.
Report: `research/architecture/loom-30b-expert-major-global-nocache-cold-io-validation-001-result.md`.
Evidence: `results-local/research/30b-expert-major-global-nocache-cold-io-validation-001/20260826T134143Z/`.

T1:
- conservative physical coverage `95.3113%`;
- wall `0.246744 s`;
- raw/conservative physical `153,010,000 / 152,910,000 B`;
- payload/hash PASS;
- swap delta `0 B`;
- minimum free memory `59%`.

Coldness passed strongly. Validation stopped after the runner treated reset raw return `1` as failure; T2/T3 were not run.

## Global-nocache reset semantics audit 001 — RESOLVED

`LOOM_30B_GLOBAL_NOCACHE_RESET_SEMANTICS_AUDIT_001` = `GLOBAL_NOCACHE_RESET_SEMANTICS_RESOLVED`.
Report: `research/architecture/loom-30b-global-nocache-reset-semantics-audit-001-result.md`.
Evidence: `results-local/research/30b-global-nocache-reset-semantics-audit-001/20260826T135941Z/`.

Established locally:
- `F_GLOBAL_NOCACHE = 55` from `sys/fcntl.h`;
- SET argument `1`: raw return `0`, `errno=0`, transition `0 -> 1`;
- RESET argument `0` after SET: raw return `1`, `errno=0`, transition `1 -> 0`;
- old runner predicate `returned == 0` was wrong for RESET;
- no passive GET exists locally;
- reversible transactional verification on empty files produced `[0,1,0,1,0,1]` under native C, Python fcntl, and fixed-ABI C/ctypes; `0 B` payload read.

Frozen future control protocol:
1. use fixed-ABI native helper with explicit errno capture;
2. SET 1 must return `0`, errno `0`, no exception;
3. RESET 0 must return `1`, errno `0`, no exception;
4. restoration verification: SET 1 -> `0`, then RESET 0 -> `1`, errno `0` throughout;
5. any deviation fails closed and rejects the repetition.

Validation 001 remains overall FAIL because the preregistered 3/3 sequence was not completed; it is not retroactively reclassified.

## Current checkpoint

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_002`

Goal: repeat the packed-only 3-trial coldness validation with the same workload/method and only the now-established control-return predicate repaired.

Frozen workload/protocol:
- first 64 packed experts;
- `160,432,128 B` logical payload/trial;
- exactly 3 trials maximum;
- fresh read-only FD each trial;
- before payload: fixed-ABI SET `F_GLOBAL_NOCACHE=1` requiring raw `0`, errno `0`; set `F_NOCACHE=1`, `F_RDAHEAD=0`;
- three idle `iostat -Id` intervals;
- timed 4-MiB-chunk read/hash;
- persist complete repaired instrumentation;
- after payload: RESET `F_GLOBAL_NOCACHE=0` requiring raw `1`, errno `0`;
- transactional restoration verification SET `1` -> `0`, RESET `0` -> `1`, errno `0` throughout;
- no retry or strategy modification after results.

Frozen PASS requires all 3/3 trials:
- conservative physical coverage `>=80%`;
- payload/hash PASS;
- complete arithmetic-consistent instrumentation;
- all control set/reset/restoration checks PASS;
- swap delta `<=16,000,000 B`;
- free memory `>=10%`;
- no unsafe memory-pressure event.

FAIL if any completed trial is below 80% or any safety/control/hash/persistence gate fails. UNRESOLVED only for a genuinely new environment/instrumentation ambiguity.

No source arm, model forward, network, DFlash, runtime integration, threshold changes or post-hoc strategy changes.

Classifications:
- `PACKED_GLOBAL_NOCACHE_COLD_IO_PASS`
- `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`
- `PACKED_GLOBAL_NOCACHE_COLD_IO_UNRESOLVED`

Only after PASS may `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_002` be preregistered.
