# LOOM — Pi Agent Protocol

Version: 3.24
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

## Cold-I/O protocol validation 001 — UNRESOLVED

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_001` = `PACKED_COLD_IO_PROTOCOL_UNRESOLVED`.
The selected fresh-inode method could not be classified because instrumentation failed after the timed read.

## Cold-I/O instrumentation repair 001 — PASS

`LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001` = `COLD_IO_INSTRUMENTATION_PASS`.
Report: `research/architecture/loom-30b-cold-io-instrumentation-repair-001-result.md`.
Evidence: `results-local/research/30b-cold-io-instrumentation-repair-001/20260826T130155Z/`.

Root cause fixed: `row.update()` referenced `row['payload_validation']` before insertion.
Success persistence PASS; intentional fail persistence PASS; fail-closed gate PASS; probe `16,777,216 B`; swap delta `0 B`.

## Cold-I/O protocol validation 002 — FAIL

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002` = `PACKED_COLD_IO_PROTOCOL_FAIL`.
Report: `research/architecture/loom-30b-expert-major-cold-io-protocol-validation-002-result.md`.
Evidence: `results-local/research/30b-expert-major-cold-io-protocol-validation-002/20260826T131142Z/`.

Frozen method tested unchanged:
- fresh non-cloned APFS inode via `O_CREAT|O_EXCL`;
- byte-copy selected packed payload;
- `fsync` before timed read;
- `F_NOCACHE/F_RDAHEAD` supplementary.

Three valid `160,432,128 B` trials:
- T1 coverage `21.7537%`, wall `0.221453 s`, raw physical `37,090,000 B`;
- T2 `21.6914%`, `0.253920 s`, `37,030,000 B`;
- T3 `20.8250%`, `0.224689 s`, `37,140,000 B`.
Payload/hash PASS 3/3; swap delta 0 B 3/3; 0/3 met frozen >=80% gate.

Therefore the fresh-inode byte-copy method is rejected. A plausible but unproven mechanism is that preparation itself leaves written pages resident in cache. Treat this only as a working hypothesis until measured.

Do not modify this failed method post hoc and call it the same experiment. Do not preregister A/B 002 yet.

## Current checkpoint

`LOOM_30B_COLD_IO_MEASUREMENT_STRATEGY_REDESIGN_001`

Goal: redesign the cold physical-I/O measurement strategy before another performance A/B.

Analysis-first requirements:
1. inspect retained I/O evidence, failed fresh-inode protocol, and locally available macOS file/cache mechanisms;
2. distinguish established facts from hypotheses about write-side cache population;
3. rank at most 3 safe candidate measurement/preparation strategies;
4. reject RAM-filling/cache-thrashing, swap-induced eviction, uncontrolled reboot dependence, or methods that cannot validate per-trial physical coverage;
5. choose exactly one minimal bounded validation experiment with the same frozen >=80% conservative physical-coverage criterion;
6. prefer <=256 MiB/trial, <=3 trials, no model forward/network/DFlash/full source-vs-packed A/B;
7. define quantitative PASS/FAIL and instrumentation before execution;
8. do not execute the selected validation experiment in this checkpoint unless only a tiny <=32 MiB probe is necessary to resolve mechanism availability/semantics.

Classifications:
- `COLD_IO_MEASUREMENT_STRATEGY_SELECTED`
- `COLD_IO_MEASUREMENT_STRATEGY_INSUFFICIENT`

Only after strategy selection and a separately preregistered validation PASS may `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_002` be considered.
