# LOOM — Active Handoff

Last updated: 2026-08-29
Status: ACTIVE — `LOOM_30B_APPLE_MOE_PAGING_FEASIBILITY_GO` completed successfully on the base M1 8 GiB host. Validator/guided-repair work remains PAUSED. Current checkpoint is the first real GGUF generation using Apple Metal expert paging.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_APPLE_MOE_PAGING_STAGE1_001`
Pi context: `/AGENTS.md` v3.66.

## Product direction

- BALANCED 8B remains the fast provisional primary tier (~13 tok/s).
- DEEP 30B remains quality/escalation tier but current custom MLX runtime is ~1.4 tok/s and too slow for frequent use.
- FAST retained conceptually; legacy 4B parked.
- LOOM AUTO validator-first track remains valid but paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## Validator track — paused at clean checkpoint

`LOOM_VERIFY_RULE_VALIDATOR_HARDENING_GO`: 24/24 fixtures, FP/FN 0/0, p95 0.006542 ms. Sanitized guided-repair work may resume later; do not run it now.

## Apple MoE paging feasibility — GO

Result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`
Evidence:
`results-local/research/30b-apple-moe-paging-feasibility-001/20260829T130414Z/report.json`

Exact frozen PoC:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Confirmed on M1 8GB:
- native Metal build succeeds;
- required MoE paging flags present;
- Apple Metal device detected;
- source confirms bounded LRU expert slots, `pread` expert loading and Metal synchronization/interceptor;
- storage diagnostic ~2579.51 MiB/s;
- projected Q3_K_S totals: S8 6.304 GiB, S16 6.954, S24 7.604, S32 8.253;
- S32 is out; S8/S16/S24 are Stage-1 candidates;
- selected only ByteShape Q3_K_S-3.25bpw.

## Exact next action — Stage 1 real generation

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-preregistration.md`

Download exactly one model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
Expected SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Create only:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`

Run frozen slot sweep S8 -> S16 -> conditional S24 with identical `-ub 1`, 48 MoE layers, no mmap/warmup and the PoC's expert CPU override. Exact prompt/cap/context are in the preregistration.

Safety: S24 only if S16 exits cleanly with no critical memory pressure, peak swap <=3.5 GiB, no OOM and >=5% host memory headroom. Never test 32 slots.

GO requires coherent output and best safe generation >=2.5 tok/s with valid provenance/evidence and no critical host-pressure event.

If GO: Stage 2 should establish reproducibility and compare the new DEEP path with canonical custom MLX under fresh matched practical tasks before changing product defaults.