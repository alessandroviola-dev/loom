# LOOM — Active Handoff

Last updated: 2026-08-29
Status: ACTIVE — Apple MoE feasibility GO. Stage1 and Stage1R both closed MECHANICAL_NO_GO for harness/frontend reasons, with no valid performance measurement. Noninteractive frontend recovery completed GO. Current checkpoint is fresh preregistered Stage1R2 using `llama-completion -no-cnv` and bounded-output instrumentation.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_001`
Pi context: `/AGENTS.md` v3.68.

## Product direction

- BALANCED 8B remains provisional primary at ~13 tok/s.
- DEEP 30B remains quality/escalation tier; current custom MLX path ~1.4 tok/s is too slow for frequent use.
- FAST retained conceptually; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## Validator track — paused cleanly

`LOOM_VERIFY_RULE_VALIDATOR_HARDENING_GO`: 24/24, FP/FN 0/0, p95 0.006542 ms. Sanitized guided-repair remains paused, not cancelled.

## Apple MoE paging feasibility — GO

Result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Base M1 8 GiB feasibility confirmed Metal build, bounded LRU expert paging, `pread`, Apple Metal path and plausible S8/S16/S24 projections. S32 rejected.

## Stage1 / Stage1R mechanical history

Stage1:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-result.md`
`LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO`.

Stage1R:
`research/architecture/loom-30b-apple-moe-paging-stage1r-001-result.md`
`LOOM_30B_APPLE_MOE_PAGING_STAGE1R_MECHANICAL_NO_GO`.

No valid S8/S16/S24 scientific measurement exists.

Stage1R exact root cause: the frozen `llama-cli` frontend is interactive. It entered its unconditional `> ` / `readline` loop and produced ~4.55 GB repeated prompt output. The prior harness retained unbounded per-output bookkeeping/full decode, so the observed ~14 GiB swap is not accepted as model memory evidence.

## Noninteractive frontend recovery — GO

Result:
`research/architecture/loom-30b-noninteractive-frontend-recovery-001-result.md`

Evidence:
`results-local/research/30b-noninteractive-frontend-recovery-001/20260829T205441Z/report.json`

Frozen correct binary:
`llama-completion`
SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Frozen recovered harness:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`
SHA256:
`4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`

Recovery guarantees:
- direct durable output streaming;
- bounded parent-memory accounting;
- 64 MiB/profile output cap -> `MECHANICAL_OUTPUT_RUNAWAY`;
- incremental telemetry;
- `finally` finalization.

Synthetic runaway retained exactly 67,108,864 bytes, terminated child, parent RSS increase ~10.313 MiB, swap delta 0 MiB, evidence survived.

## Exact next action — Stage1R2

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-preregistration.md`

Reuse only:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Required model size: `12,424,439,872` bytes.
Required SHA256: `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Before inference verify exact harness SHA, model SHA/size, clean source commit, and `llama-completion` SHA. No download/rebuild/edit is authorized.

Run fresh Stage1R2 evidence root and frozen sweep:
- S8;
- S16;
- S24 only if S16 safety gate passes;
- never S32.

Common flags remain exact original scientific workload plus noninteractive frontend:
`-n 96 -c 1024 --temp 0 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -ub 1 -no-cnv`.

S24 safety gate: S16 clean, no critical/red pressure, peak swap <=3.5 GiB, no OOM, host responsive, >=5% headroom.

GO requires coherent output and best safe generation >=2.5 tok/s with exact provenance, complete evidence, no critical memory/OOM and no output-runaway cap event.

If GO: Stage2 reproducibility + fresh matched practical/quality comparison before changing canonical DEEP.
If scientific NO_GO: diagnose valid bottleneck without post-hoc quant/flag rescue.
If mechanical NO_GO: preserve evidence and stop before unregistered retry.