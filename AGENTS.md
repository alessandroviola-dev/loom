# LOOM — Pi Agent Protocol

Version: 3.20
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git/push/PR/edit project docs unless explicitly authorized.

After every **significant scientific checkpoint**, ChatGPT must update canonical project state on GitHub and the user must pull before the next Pi WP. Significant checkpoints include: a classification change, accepted/invalid experiment, frozen baseline change, branch-direction change, or selection of a new next checkpoint. Tiny diagnostic substeps may be grouped only while the canonical next checkpoint remains unchanged.

Rules:
1. one-factor experiments; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. treatment comparison is invalid if more than the intended factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch hard caps;
5. fail closed offline before expensive execution;
6. no performance claim from an INVALID benchmark;
7. do not advance to a new scientific WP from stale AGENTS/HANDOFF/ROADMAP.

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

## DFlash branch — CLOSED AS ACTIVE RECOVERY PATH

Final decision: `BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`.
Report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.

P3: Q4 DFlash rank 2 / 5416; BF16 rank 2 / 350; no exact recovery.
P1: Q4 rank 3 / 3100; BF16 rank 2 / 3100; no exact recovery.
P3 + P1 make preregistered >=2/3 exact recovery impossible; P2/E2E not executed.
Do not reopen DFlash without a new independent mechanism.

## Core serving/I/O re-entry — BOTTLENECK IDENTIFIED

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` = `SERVING_IO_BOTTLENECK_IDENTIFIED`.
Report: `research/architecture/loom-30b-moe-serving-io-reentry-001-result.md`.
Local evidence: `results-local/research/30b-moe-serving-io-reentry-001/20260826T122316Z/analysis.json`.

Dominant measured bottleneck: **external expert data-access**.
Exact packed 48-layer decode-equivalent evidence:
- data-access `0.442087 s / 0.926028 s = 47.74%` median wall;
- 384 reads, `962,592,768 B` expert payload;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority candidate: lossless expert-major contiguous storage. Cache/materialization work remains secondary until physical-I/O causality is established.

## Expert-major physical-I/O A/B 001 — INVALID

`LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_001` = `EXPERT_MAJOR_PHYSICAL_IO_INVALID`.
Report: `research/architecture/loom-30b-expert-major-physical-io-ab-001-result.md`.
Local evidence: `results-local/research/30b-expert-major-physical-io-ab-001/20260826T122942Z/`.

Observed but NOT scientifically accepted:
- source p50/p95 `1.097739 / 1.116585 s`;
- packed p50/p95 `0.382613 / 0.552228 s`;
- apparent wall ratio `0.348547`;
- reads/pass `3456 -> 384`;
- throughput `874.539 -> 2275.084 MB/s`;
- byte/hash equality PASS.

Invalidity: packed physical coverage only `50.06%`; physical/counter validity FAIL. Do not interpret the apparent ~65% wall reduction as a layout speedup yet.

## Current checkpoint

`LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001`

Diagnostic only. Goal: explain packed ~50% physical coverage before repeating any full A/B.

Required:
1. reconstruct logical bytes, unique ranges, files, physical counters and coverage formula per arm;
2. distinguish counter semantics from genuine cache/readahead contamination, APFS behavior, overlap/duplicates, or sampling error;
3. verify identical payload for all 384 experts;
4. only if retained evidence is insufficient, allow a tiny <=3-expert / <=100 MiB physical-I/O probe;
5. decide whether previous timing is reusable, invalid-coldness, or unresolved;
6. state the minimal correction for a valid A/B.

Classifications:
- `PACKED_COVERAGE_COUNTER_SEMANTICS_EXPLAINED`
- `PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`
- `PACKED_COVERAGE_UNRESOLVED`

No full benchmark, model forward, network, DFlash, or runtime optimization during this checkpoint.
