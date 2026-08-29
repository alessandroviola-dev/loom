# LOOM — Pi Agent Protocol

Version: 3.68
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

## Apple MoE paging feasibility — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Feasibility established native Metal build, bounded LRU expert slots, `pread`, Apple Metal path and plausible S8/S16/S24 projections on base M1 8 GiB. S32 rejected. Feasibility GO makes no inference-speed claim.

## Stage1 / Stage1R — CLOSED MECHANICALLY

Stage1 result:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-result.md`
Classification: `LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO`.

Stage1R result:
`research/architecture/loom-30b-apple-moe-paging-stage1r-001-result.md`
Classification: `LOOM_30B_APPLE_MOE_PAGING_STAGE1R_MECHANICAL_NO_GO`.

No valid S8/S16/S24 performance measurement exists from either checkpoint.

Stage1R root cause: frozen `llama-cli` is interactive/conversational and entered a `> ` / `readline` loop, producing ~4.55 GB runaway output. The observed ~14 GiB swap is invalid as model-residency evidence because the prior harness also retained output bookkeeping/full decode in memory.

## Noninteractive frontend recovery — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-noninteractive-frontend-recovery-001-result.md`

Classification:
`LOOM_30B_NONINTERACTIVE_FRONTEND_RECOVERY_GO`.

Evidence:
`results-local/research/30b-noninteractive-frontend-recovery-001/20260829T205441Z/report.json`

Correct frozen one-shot frontend:
`llama-completion -no-cnv`

`llama-completion` SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Recovered local harness:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`
SHA256:
`4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`

Harness output accounting is now bounded, streams directly to disk, has a 64 MiB/profile hard cap, incremental telemetry and `finally` finalization. Synthetic runaway terminated at exactly 64 MiB retained output with ~10.313 MiB parent RSS increase and 0 MiB swap delta.

## Current checkpoint — Stage1R2 001

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-preregistration.md`

Reuse only existing verified GGUF:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Size: `12,424,439,872` bytes.
SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

No download/copy/requantization.

Frozen scientific sweep remains S8 -> S16 -> conditional S24, never S32, with exact original prompt and:
- `-n 96`
- `-c 1024`
- `--temp 0`
- `--moe-n-layers 48`
- `--no-mmap`
- `--no-warmup`
- `--cpu-moe`
- `-ub 1`
- `-no-cnv`

Use `llama-completion`, never `llama-cli`.

Stage1R2 GO requires exact provenance, coherent output, best safe generation >=2.5 tok/s, no critical memory/OOM, no output-runaway cap event and complete durable evidence.

No package installs, binary rebuild, source/runtime/harness edit, validator work, Heretic/provider/UI or production integration.