# LOOM — Pi Agent Protocol

Version: 3.69
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not commit/push/PR/edit project decision docs unless explicitly authorized.
GitHub is canonical. Active clone: `<repository-root>`.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue/post-hoc gate relaxation;
3. fail closed before expensive execution;
4. invalid/inconclusive runs support no performance claim;
5. production code requires exact review + Git persistence;
6. do not tune on exposed evaluation examples;
7. hidden ground truth/spec metadata must never enter model repair/judge inputs unless explicitly preregistered as public input;
8. expensive model downloads require an explicit preregistered checkpoint.

## Product direction

**Big models. Small machines.**
- BALANCED: Qwen3-8B 3-bit/group64 Direct MLX, ~13 tok/s, provisional primary.
- DEEP: Qwen3-30B-A3B; historical custom MLX path ~1.4 tok/s. Apple Metal MoE paging Stage1R2 has now reached 4.40 tok/s on the frozen Stage1 workload, but canonical DEEP is not replaced until Stage2 reproducibility/quality work passes.
- FAST: concept retained; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but PAUSED during this runtime investigation.
- LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Validator track — PAUSED cleanly

VERIFY_RULE Validator Hardening 001 completed **GO**: 24/24, FP/FN 0/0, contradiction reject 2/2, forbidden-heuristic reject 2/2, p95 0.006542 ms. Planned sanitized guided-repair work is paused, not cancelled.

## Apple MoE paging feasibility — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Feasibility established native Metal build, bounded LRU expert slots, `pread`, Apple Metal path and plausible S8/S16/S24 projections on base M1 8 GiB. S32 rejected.

## Stage1 / Stage1R — CLOSED MECHANICALLY

Stage1:
`LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO`.

Stage1R:
`LOOM_30B_APPLE_MOE_PAGING_STAGE1R_MECHANICAL_NO_GO`.

No performance claim follows from those attempts. Root causes were stdio/evidence instrumentation and use of interactive `llama-cli` rather than the noninteractive frontend.

## Noninteractive frontend recovery — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-noninteractive-frontend-recovery-001-result.md`

Correct one-shot frontend:
`llama-completion -no-cnv`

`llama-completion` SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Recovered bounded-output harness:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`
SHA256:
`4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`

Harness streams output directly to durable disk, keeps bounded parent-memory accounting, has 64 MiB/profile runaway protection, incremental telemetry and `finally` finalization.

## Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Evidence:
`results-local/research/30b-apple-moe-paging-stage1r2-001/20260829T211631Z/final-report.json`

Classification:
**`LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_GO`**.

Verified model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
Size `12,424,439,872` bytes.
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Measured frozen Stage1 workload:
- S8: 2.99 tok/s, load 19.294 s, E2E 52.606 s;
- S16: 3.58 tok/s, load 16.625 s, E2E 45.110 s;
- S24: **4.40 tok/s**, load **14.426 s**, E2E **37.704 s**.

S24 memory/safety:
- RSS 2935.766 MiB;
- wired 5032.297 MiB;
- compressed 1567.734 MiB;
- swap 1125.94 MiB;
- minimum headroom 13%;
- no critical pressure/OOM/corruption/runaway.

Historical contextual speedup at S24:
- 3.1384× vs 1.402 tok/s compact practical DEEP reference;
- 3.5795× vs 1.229233 tok/s exact-Q4 historical reference.

These are historical practical references, not same-artifact one-factor comparisons.

## Current checkpoint — Stage2 comparability audit

Before matched quality/performance Stage2, identify the exact historical custom MLX 30B checkpoint/artifact and determine whether it is checkpoint-identical to ByteShape `Qwen3-30B-A3B-Instruct-2507`, architecture-only comparable, or nonmatched for quality.

This audit is metadata/provenance only: no model inference, no download, no package/source mutation.

After the audit, preregister Stage2 for:
- S24 reproducibility across fresh processes;
- fresh matched practical tasks;
- TTFT/load/E2E and memory/swap stability;
- quality/correctness preservation;
- explicit interpretation rules if checkpoint identity differs.

Do not replace canonical DEEP solely from Stage1R2.