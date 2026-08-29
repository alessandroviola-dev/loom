# LOOM — Pi Agent Protocol

Version: 3.66
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

Evidence:
`results-local/research/30b-apple-moe-paging-feasibility-001/20260829T130414Z/report.json`

Classification: **`LOOM_30B_APPLE_MOE_PAGING_FEASIBILITY_GO`**.

Observed on base M1 8 GiB:
- exact PoC source `kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892` fetched cleanly;
- native Metal `llama-cli` build succeeded;
- built binary SHA `c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844`;
- Metal device `Apple M1`, ~5461 MiB exposed;
- `--moe-n-slots`, `--moe-n-layers`, `--no-mmap`, `--no-warmup` present;
- source confirms bounded expert slots/LRU, `pread` disk loading and Apple Metal synchronization/interceptor path;
- read-only 512 MiB storage probe ~2579.51 MiB/s;
- frozen projected totals for Q3_K_S-3.25: 8 slots 6.304 GiB, 16 6.954, 24 7.604, 32 8.253; 32 rejected;
- Q3_K_S-3.25 and IQ3_S-3.29 both compatible for Stage 1;
- selected only Q3_K_S-3.25.

Feasibility GO makes no inference-speed or quality claim.

## Current checkpoint — 30B Apple MoE Paging Stage 1 001

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-preregistration.md`

Single authorized model:
`byteshape/Qwen3-30B-A3B-Instruct-2507-GGUF/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
Expected SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`
Published size ~12.4 GB; normalized quality 97.97%.

Create only:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`

Frozen real-generation sweep:
- S8: 8 expert slots;
- S16: 16 expert slots;
- S24: 24 expert slots only if frozen S16 host-safety gate passes;
- no 32-slot test;
- `--moe-n-layers 48`, `--no-mmap`, `--no-warmup`, required expert CPU override, `-ub 1` for every profile;
- exact prompt/cap/context from preregistration;
- one measured run per profile; no post-hoc flag tuning/retries.

GO requires exact artifact/runtime provenance, coherent output, best safe generation >=2.5 tok/s, no corruption/critical memory event and complete evidence.

No second model download, package install, source patch, validator work, Heretic/provider/UI or production integration.