# LOOM — Pi Agent Protocol

Version: 3.23
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
Candidate method remains:
- fresh non-cloned APFS inode via `O_CREAT|O_EXCL` byte-copy + `fsync`;
- `F_NOCACHE/F_RDAHEAD` supplementary.
The first 160,432,128-B trial was not accepted because instrumentation failed post-read before physical counters and payload validation were persisted.

## Cold-I/O instrumentation repair 001 — PASS

`LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001` = `COLD_IO_INSTRUMENTATION_PASS`.
Report: `research/architecture/loom-30b-cold-io-instrumentation-repair-001-result.md`.
Evidence: `results-local/research/30b-cold-io-instrumentation-repair-001/20260826T130155Z/`.

Root cause fixed:
`row.update()` indexed `row['payload_validation']` before the update inserted that key, causing a post-read/pre-persistence `KeyError`.

Validation:
- success-path evidence persistence PASS;
- intentional fail-path persistence PASS;
- fail-closed missing-field gate PASS;
- probe bytes `16,777,216 B`;
- swap delta `0 B`.

This checkpoint validates instrumentation only. It does NOT validate coldness and does NOT rehabilitate the INVALID A/B 001.

## Current checkpoint

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002`

Goal: retest the unchanged fresh-inode cache-state method with repaired fail-safe instrumentation.

Frozen method under test:
- create a fresh non-cloned APFS inode with `O_CREAT|O_EXCL`;
- byte-copy the selected packed payload into it;
- `fsync` before timed read;
- use `F_NOCACHE/F_RDAHEAD` only as supplementary hints.

Frozen validity gate:
- every accepted timed trial must independently show `>=80%` conservative physical coverage;
- payload/hash validation PASS;
- required instrumentation complete and internally consistent;
- no material swap increase or unsafe memory pressure.

Bounded protocol:
1. no model forward/network/DFlash/runtime optimization/full source-vs-packed A/B;
2. use the same representative packed subset scale as protocol validation 001 (`160,432,128 B`, unless an exact mechanical reason requires a smaller bounded equivalent); do not silently expand workload;
3. at most 3 independent fresh-inode trials;
4. persist logical/physical byte accounting, wall time, read count, payload/hash, memory/swap and protocol metadata for every trial, including failures;
5. PASS only if 3/3 trials satisfy the frozen >=80% conservative physical-coverage gate and safety/validation gates;
6. FAIL if the method demonstrably cannot satisfy the frozen gate under the bounded protocol;
7. UNRESOLVED only for a new instrumentation/environment ambiguity that prevents scientific classification.

Classifications:
- `PACKED_COLD_IO_PROTOCOL_PASS`
- `PACKED_COLD_IO_PROTOCOL_FAIL`
- `PACKED_COLD_IO_PROTOCOL_UNRESOLVED`

Only after PASS may `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_002` be preregistered.
