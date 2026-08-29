# LOOM Roadmap

Last updated: 2026-08-29
Current: Apple MoE feasibility GO; Stage1 and Stage1R closed MECHANICAL_NO_GO with no valid performance measurement; noninteractive frontend recovery GO completed. Immediate priority is preregistered Stage1R2 using `llama-completion -no-cnv` with bounded-output instrumentation. Validator/guided-repair remains PAUSED.
Canonical context: `/AGENTS.md` v3.68.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional primary.
- `loom-deep`: Qwen3-30B-A3B; canonical custom MLX ~1.4 tok/s, under alternative-runtime investigation.
- `loom-fast`: future clean-runtime tier; legacy 4B parked.
- `loom-auto`: validator-first architecture planned but paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## 2. Validator track — paused cleanly

Output Validator v0: GO.
Selective Rescue 001: scientific NO_GO at 5/8 final CORRECT, zero false accepts.
8B Validator-Guided Repair 001: MECHANICAL_NO_GO from hidden-spec leakage.
VERIFY_RULE Validator Hardening 001: GO — 24/24, FP/FN 0/0, contradiction/forbidden-heuristic reject 2/2.

Resume only after the current 30B runtime priority.

## 3. Apple MoE paging feasibility — GO

Result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Base M1 8GB feasibility established native Metal build, bounded MoE slots/LRU + `pread` + Metal synchronization and plausible S8/S16/S24 memory projections. S32 rejected.

## 4. Stage1 / Stage1R — closed mechanically

Stage1 result:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-result.md`
Classification: `LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO`.

Stage1R result:
`research/architecture/loom-30b-apple-moe-paging-stage1r-001-result.md`
Classification: `LOOM_30B_APPLE_MOE_PAGING_STAGE1R_MECHANICAL_NO_GO`.

No valid S8/S16/S24 scientific measurement exists.

Stage1R showed the frozen `llama-cli` frontend is interactive and entered a repeated `> ` / `readline` loop, generating ~4.55 GB output. The associated ~14 GiB swap is excluded from model-memory conclusions because the prior harness also retained unbounded output bookkeeping/full decode.

## 5. Noninteractive frontend recovery — GO

Result:
`research/architecture/loom-30b-noninteractive-frontend-recovery-001-result.md`

Evidence:
`results-local/research/30b-noninteractive-frontend-recovery-001/20260829T205441Z/report.json`

Correct one-shot frontend:
`llama-completion -no-cnv`.

Frozen `llama-completion` SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

Frozen recovered harness SHA256:
`4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`.

Harness now uses direct durable streaming, bounded parent-memory accounting, incremental telemetry/finalization, and a 64 MiB/profile output cap. Synthetic runaway terminated at the cap with ~10.313 MiB parent RSS increase and zero swap delta.

## 6. Current — Stage1R2 001

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-preregistration.md`

Reuse only existing verified model:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Size `12,424,439,872` bytes.
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.
No model download/copy/requantization authorized.

Before inference verify exact recovered harness SHA, clean frozen source commit, exact model SHA/size and exact `llama-completion` SHA. No runner edit or binary rebuild authorized.

Frozen real-generation sweep:
- S8;
- S16;
- conditional S24 if S16 safety gate passes;
- never S32;
- temp 0, max 96 generated tokens, ctx 1024;
- `--moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -ub 1 -no-cnv`;
- fresh `llama-completion` process per profile;
- no post-hoc tuning or retry of a scientifically valid profile.

GO requires at least one coherent clean run and best safe generation >=2.5 tok/s without critical memory/OOM, output-runaway or provenance/evidence failure.

## 7. If Stage1R2 GO

Stage2 must establish reproducibility and fresh matched practical/quality comparison against canonical DEEP custom MLX. Measure TTFT/load, decode tok/s, E2E wall, memory/wired/compressed/swap, storage/cache behavior and output quality/correctness.

Do not replace canonical DEEP solely from one Stage1R2 speed result.

## 8. If Stage1R2 scientific NO_GO

Do not download a second quant or tune flags post hoc. Diagnose the valid bottleneck. Any alternative quant/runtime requires fresh preregistration.

## 9. Later work

After this runtime priority:
- resume sanitized validator-guided repair/selective-DEEP graph;
- semantic verifier/open-ended validation;
- automatic validator/contract derivation;
- provider/UI;
- mandatory Heretic;
- FAST clean-runtime reintroduction.