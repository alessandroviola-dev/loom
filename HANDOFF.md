# LOOM — Active Handoff

Last updated: 2026-08-29
Status: ACTIVE — Apple MoE paging feasibility is GO. Original Stage 1 closed `MECHANICAL_NO_GO` from harness failures, then `LOOM_30B_STAGE1_HARNESS_RECOVERY_GO` completed. Current checkpoint is fresh preregistered Stage1R using the same scientific workload and recovered frozen harness.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_APPLE_MOE_PAGING_STAGE1R_001`
Pi context: `/AGENTS.md` v3.67.

## Product direction

- BALANCED 8B remains the fast provisional primary tier (~13 tok/s).
- DEEP 30B remains quality/escalation tier; current custom MLX runtime ~1.4 tok/s is too slow for frequent use.
- FAST retained conceptually; legacy 4B parked.
- LOOM AUTO validator-first track remains valid but paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## Validator track — paused at clean checkpoint

`LOOM_VERIFY_RULE_VALIDATOR_HARDENING_GO`: 24/24 fixtures, FP/FN 0/0, p95 0.006542 ms. Sanitized guided-repair work may resume later; do not run it now.

## Apple MoE paging feasibility — GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`

Frozen PoC:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Verified binary SHA:
`c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844`

S8/S16/S24 were feasible candidates from static projection; S32 rejected.

## Original Stage 1 — MECHANICAL_NO_GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-result.md`

No valid S8/S16/S24 measurement exists.

Mechanical history:
1. first S8 invalid from stdout/stderr pipe backpressure;
2. minimum drain correction still left evidence persistence RAM-only until post-child finalization, so interruption/error produced no reconstructable scientific profile evidence.

No performance conclusion about the model/runtime follows from Stage 1.

## Harness recovery — GO

Evidence:
`results-local/research/30b-stage1-harness-recovery-001/20260829T195240Z/`

Recovered harness:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`

Frozen SHA256:
`6857a7f7deeb6c8d88db81df4ce06e4ac2e571079971cebdd16718b625930ecf`

Size: 446 lines / 26,980 bytes.

Synthetic validation passed:
- 2,097,152 bytes continuous combined output retained;
- stdout/stderr marker bytes 1,048,576 each;
- incremental telemetry persisted;
- clean exit and nonzero exit evidence persisted;
- resume path reaches pre-inference point without running a model.

## Exact next action — Stage1R real generation

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-stage1r-001-preregistration.md`

Reuse only this existing local GGUF:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Expected size: `12,424,439,872` bytes.
Expected SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

No model download is authorized.

Before inference verify:
- harness SHA exactly `6857a7f7...930ecf`;
- GGUF SHA/size exactly;
- source commit exactly `41ec4c4...de892`;
- binary SHA exactly `c65a60d7...43844`;
- no conflicting inference process.

Run original frozen sweep S8 -> S16 -> conditional S24 with temp 0, n=96, ctx=1024, `--moe-n-layers 48`, `--no-mmap`, `--no-warmup`, `--cpu-moe`, `-ub 1`.

S24 only if S16 exits cleanly, no critical/red memory pressure, peak swap <=3.5 GiB, no OOM and >=5% headroom. Never S32.

GO requires coherent output and best safe generation >=2.5 tok/s with complete durable evidence and no critical host-pressure event.

If GO: Stage 2 establishes reproducibility and a fresh matched practical/quality comparison before changing canonical DEEP.
If scientific NO_GO: diagnose the observed bottleneck; no post-hoc second quant or flag tuning.
If mechanical NO_GO: preserve evidence and stop before any unregistered retry.