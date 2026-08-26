# LOOM — Pi Agent Protocol

Version: 3.21
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git/push/PR/edit project docs unless explicitly authorized.

After every **significant scientific checkpoint**, ChatGPT updates canonical project state on GitHub and the user pulls before the next Pi WP. Significant checkpoints include: classification change, accepted/invalid experiment, frozen baseline change, branch-direction change, or selection of a new next checkpoint. Tiny diagnostics may be grouped only while the canonical next checkpoint remains unchanged.

Rules:
1. one-factor experiments; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. treatment comparison invalid if more than intended factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from an INVALID benchmark;
7. do not advance from stale AGENTS/HANDOFF/ROADMAP.

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
P3 and P1 both failed exact BF16 recovery, making preregistered >=2/3 impossible. Do not reopen absent a new independent mechanism.

## Core serving/I/O — BOTTLENECK IDENTIFIED

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` = `SERVING_IO_BOTTLENECK_IDENTIFIED`.
Report: `research/architecture/loom-30b-moe-serving-io-reentry-001-result.md`.
Evidence: `results-local/research/30b-moe-serving-io-reentry-001/20260826T122316Z/analysis.json`.

Dominant measured bottleneck: **external expert data-access**.
- data access `0.442087 s / 0.926028 s = 47.74%` median wall;
- 384 reads, `962,592,768 B` payload;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority candidate: lossless expert-major contiguous storage.

## Expert-major physical-I/O A/B 001 — INVALID

`LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_001` = `EXPERT_MAJOR_PHYSICAL_IO_INVALID`.
Report: `research/architecture/loom-30b-expert-major-physical-io-ab-001-result.md`.

Observed but not accepted as cold-I/O performance:
- source p50 `1.097739 s`;
- packed p50 `0.382613 s`;
- apparent ratio `0.348547`;
- reads/pass `3456 -> 384`;
- exact byte/hash equality PASS.

## Coverage audit — CACHE CONTAMINATION IDENTIFIED

`LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001` = `PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`.
Report: `research/architecture/loom-30b-expert-major-io-coverage-audit-001-result.md`.
Evidence: `results-local/research/30b-expert-major-physical-io-ab-001/20260826T122942Z/`.

Exact accounting:
- logical bytes/pass both arms: `962,592,768 B`;
- source conservative physical coverage: `99.8761%`;
- packed conservative physical coverage: `50.0644%`;
- packed first valid-like pass: `94.26%` physical coverage;
- subsequent packed repetitions: only `38.61–40.20%`.

Root cause: packed-file macOS OS/page-cache residency surviving accepted `F_NOCACHE/F_RDAHEAD` hints. Not duplicates, overlap, sparse file, clone construction, counter units or payload mismatch.

Previous packed wall timing is not reusable as a cold physical-I/O speedup claim. Structural facts remain valid: exact payload equality and logical read-count reduction `3456 -> 384`.

Frozen validity gate for any future cold A/B:
- every timed repetition in each arm must show **>=80% conservative physical coverage**;
- repetitions below 80% are invalid and cannot enter latency aggregates.

## Current checkpoint

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_001`

Goal: validate a reproducible packed cold-read protocol before repeating the full A/B.

Requirements:
1. no model forward/network/DFlash/runtime optimization;
2. use bounded diagnostic I/O only;
3. test a minimal cache-state method that does not rely on `F_NOCACHE/F_RDAHEAD` alone;
4. every accepted packed trial must independently demonstrate >=80% conservative physical coverage;
5. retain exact logical/physical byte accounting and payload validation;
6. PASS only if the method yields reproducible >=80% physical coverage without unsafe memory/swap pressure;
7. only after PASS preregister `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_002`.

Classifications:
- `PACKED_COLD_IO_PROTOCOL_PASS`
- `PACKED_COLD_IO_PROTOCOL_FAIL`
- `PACKED_COLD_IO_PROTOCOL_UNRESOLVED`
