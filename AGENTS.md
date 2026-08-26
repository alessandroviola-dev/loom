# LOOM — Pi Agent Protocol

Version: 3.25
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
9. a failed frozen method must not be silently modified and rerun under the same checkpoint.

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
P3 and P1 failed exact BF16 recovery, making preregistered >=2/3 impossible. Do not reopen absent a new independent mechanism.

## Core serving/I/O — BOTTLENECK IDENTIFIED

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` = `SERVING_IO_BOTTLENECK_IDENTIFIED`.
External expert data-access is dominant:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- 384 expert reads, `962,592,768 B` payload;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority candidate remains lossless expert-major contiguous storage, but no speedup claim is accepted until physical-I/O causality is valid.

## Expert-major A/B 001 — INVALID

`LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_001` = `EXPERT_MAJOR_PHYSICAL_IO_INVALID`.
Observed but not accepted: source p50 `1.097739 s`, packed p50 `0.382613 s`, apparent ratio `0.348547`, reads/pass `3456 -> 384`, exact payload equality PASS.
Reason: packed conservative physical coverage only `50.0644%`.

## Coverage audit — CACHE CONTAMINATION IDENTIFIED

`LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001` = `PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`.
- logical bytes/pass both arms `962,592,768 B`;
- source conservative physical coverage `99.8761%`;
- packed aggregate `50.0644%`;
- first packed repetition `94.26%`, later `38.61–40.20%`.
Cause: macOS page-cache residency surviving `F_NOCACHE/F_RDAHEAD` hints.
Future cold timing validity requires **>=80% conservative physical coverage on every accepted repetition**.

## Cold-I/O protocol validation 002 — FAIL

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002` = `PACKED_COLD_IO_PROTOCOL_FAIL`.
Report: `research/architecture/loom-30b-expert-major-cold-io-protocol-validation-002-result.md`.

Fresh non-cloned inode + byte-copy + fsync + descriptor hints produced only `21.7537%`, `21.6914%`, `20.8250%` conservative physical coverage on three valid 160,432,128-B trials. Payload/hash PASS 3/3; swap delta 0 B. Method rejected.

Working hypothesis only: preparation by ordinary byte-copy may populate macOS page cache for the new inode. Not proven as sole cause.

## Cold-I/O measurement strategy redesign 001 — SELECTED

`LOOM_30B_COLD_IO_MEASUREMENT_STRATEGY_REDESIGN_001` = `COLD_IO_MEASUREMENT_STRATEGY_SELECTED`.
Report: `research/architecture/loom-30b-cold-io-measurement-strategy-redesign-001-result.md`.
Evidence: `results-local/research/30b-cold-io-measurement-strategy-redesign-001/20260826T133031Z/`.

Bounded 32-MiB mechanism probe:
- `F_GLOBAL_NOCACHE` accepted locally;
- global+descriptor conservative physical coverage `49.35%`;
- descriptor-only `57.58%`;
- hashes PASS; swap increase 0 B.

Interpretation: mechanism availability is demonstrated, but the tiny probe does NOT establish coldness and is not a performance result.

Selected strategy:
- direct read of the existing packed payload;
- no preparation copy/write;
- fresh read-only FD per trial;
- set `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0` before any payload read;
- reset global control after each trial;
- per-trial conservative physical coverage remains the validity authority.

Rejected alternatives for now:
- fresh copy written under global nocache: additional write/copy causal confounding;
- `purge(8)`: system-wide and operationally disruptive.

## Current checkpoint

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001`

Goal: validate the selected direct-existing-packed `F_GLOBAL_NOCACHE` strategy before any source-vs-packed A/B.

Frozen workload/protocol:
1. packed-only validation; first 64 packed experts; `160,432,128 B` logical payload/trial;
2. exactly 3 trials maximum;
3. fresh read-only FD each trial;
4. before first payload read set `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0`;
5. collect three idle `iostat -Id` intervals for conservative background subtraction;
6. timed 4-MiB-chunk read/hash;
7. persist repaired instrumentation, payload/hash, raw and conservative physical counters, memory/swap and control status;
8. reset global control after each trial; fail closed if set/reset fails.

Frozen PASS requires all 3/3 trials:
- conservative physical coverage `>=80%`;
- payload/hash PASS;
- complete arithmetic-consistent persisted instrumentation;
- successful global/per-FD control set and reset;
- swap delta `<=16,000,000 B`;
- free memory `>=10%`;
- no unsafe memory-pressure event.

FAIL if any trial is below 80% or any safety/control/hash/persistence gate fails.

No source arm, model forward, network, DFlash, runtime integration, threshold changes or post-hoc strategy modification in this checkpoint.

Only after `PACKED_GLOBAL_NOCACHE_COLD_IO_PASS` may physical-I/O A/B 002 be preregistered.

Classifications:
- `PACKED_GLOBAL_NOCACHE_COLD_IO_PASS`
- `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`
- `PACKED_GLOBAL_NOCACHE_COLD_IO_UNRESOLVED`
