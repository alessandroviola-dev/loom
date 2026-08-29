# LOOM — Pi Agent Protocol

Version: 3.67
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
- DEEP: Qwen3-30B-A3B; canonical custom MLX path ~1.4 tok/s. 30B runtime acceleration is the active priority.
- FAST: concept retained; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but PAUSED during this runtime investigation.
- LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Validator track — PAUSED cleanly

VERIFY_RULE Validator Hardening 001 completed **GO**: 24/24, FP/FN 0/0, contradiction reject 2/2, forbidden-heuristic reject 2/2, p95 0.006542 ms. Planned sanitized guided-repair work is paused, not cancelled.

## 30B Apple MoE Paging Feasibility 001 — COMPLETE / GO

Result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`

Exact PoC:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Verified binary SHA:
`c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844`

Base M1 8 GiB feasibility confirmed bounded LRU expert slots, `pread`, Apple Metal path, required flags and plausible S8/S16/S24 memory projections. Feasibility GO makes no inference-speed claim.

## Stage 1 001 — CLOSED / MECHANICAL_NO_GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-result.md`

Classification:
**`LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO`**.

No valid S8/S16/S24 scientific measurement exists. Do not interpret elapsed wall, TTFT or throughput from invalid attempts.

Mechanical failures:
1. original S8 blocked by stdout/stderr pipe backpressure;
2. after minimal drain correction, evidence durability remained insufficient and no valid profile result could be reconstructed.

## Harness recovery — COMPLETE / GO

Classification:
**`LOOM_30B_STAGE1_HARNESS_RECOVERY_GO`**.

Evidence:
`results-local/research/30b-stage1-harness-recovery-001/20260829T195240Z/`

Recovered harness:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`

Frozen local harness SHA256:
`6857a7f7deeb6c8d88db81df4ce06e4ac2e571079971cebdd16718b625930ecf`

Frozen size: 446 lines / 26,980 bytes.

Recovery synthetic tests passed >2 MiB continuous stdout/stderr drain, incremental telemetry persistence, nonzero-exit persistence and resume-to-pre-inference path. Runner remains a local untracked research artifact; exact content was frozen via hash + `git diff --no-index` capture.

## Current checkpoint — 30B Apple MoE Paging Stage 1R 001

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-stage1r-001-preregistration.md`

Reuse only the already verified local GGUF:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Expected size: `12,424,439,872` bytes.
Expected SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

**No model download is authorized in Stage1R.**

Frozen scientific workload remains the original Stage 1 workload:
- S8 -> S16 -> conditional S24;
- never S32;
- `--moe-n-layers 48`, `--no-mmap`, `--no-warmup`, `--cpu-moe`, `-ub 1`;
- exact original prompt, 96 max generated tokens, context 1024, temp 0;
- fresh process per profile;
- no post-hoc tuning/retry of a scientifically valid measured profile.

Before inference verify exact harness/model/source/binary SHA. Evidence must be durable before launch, continuously streamed during execution and finalized on every exit path.

Stage1R GO requires coherent output, best safe generation >=2.5 tok/s, exact provenance, complete durable evidence and no critical memory/OOM event in the promoted profile.

No package install, source/runtime patch, validator work, Heretic/provider/UI or production integration.