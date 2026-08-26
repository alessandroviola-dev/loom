# LOOM — Pi Agent Protocol

Version: 3.22
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
8. instrumentation required by a gate must persist successfully before a timed result can be accepted.

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

Priority candidate: lossless expert-major contiguous storage.

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
Report: `research/architecture/loom-30b-expert-major-cold-io-protocol-validation-001-result.md`.
Evidence: `results-local/research/30b-expert-major-cold-io-protocol-validation-001/20260826T125114Z/`.

Candidate method:
- fresh non-cloned APFS inode via `O_CREAT|O_EXCL` byte-copy + `fsync`;
- `F_NOCACHE/F_RDAHEAD` supplementary.

Trial 1 attempted `160,432,128 B`, but instrumentation aborted after the timed read before physical bytes and payload validation were persisted. Trial not accepted; trials 2–3 correctly not run. Free memory `59% -> 60%`; swap delta `0 B`.

Interpretation: instrumentation failure only. The fresh-inode method is neither accepted nor rejected.

## Current checkpoint

`LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001`

Goal: make cold-I/O evidence capture fail-safe before another protocol trial.

Requirements:
1. no model forward/network/DFlash/full A/B;
2. no full 160 MiB cold trial;
3. repair persistence of pre/post physical device counters, logical bytes, wall time, read count, payload/hash validation, memory and swap state;
4. use only a tiny <=16 MiB synthetic/representative read probe to validate instrumentation end-to-end;
5. test both success-path and intentional fail-path persistence;
6. PASS only if required fields survive process exit/exception and are internally consistent;
7. do not claim cache-state validity from this instrumentation checkpoint.

Classifications:
- `COLD_IO_INSTRUMENTATION_PASS`
- `COLD_IO_INSTRUMENTATION_FAIL`

Only after PASS may `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002` retest the fresh-inode cache-state method.
