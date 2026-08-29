# LOOM Roadmap

Last updated: 2026-08-29
Current: Apple MoE paging feasibility GO; original Stage 1 closed MECHANICAL_NO_GO from harness failures; harness recovery GO completed. Immediate priority is preregistered Stage1R real generation using the same verified GGUF/runtime and frozen recovered harness. Validator/guided-repair work remains PAUSED.
Canonical context: `/AGENTS.md` v3.67.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional primary.
- `loom-deep`: Qwen3-30B-A3B; canonical custom MLX ~1.4 tok/s, now under alternative-runtime investigation.
- `loom-fast`: future clean-runtime tier; legacy 4B parked.
- `loom-auto`: validator-first architecture remains planned but experiments are paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## 2. Validator track — paused cleanly

Output Validator v0: GO.
Selective Rescue 001: scientific NO_GO at 5/8 final CORRECT, zero false accepts.
8B Validator-Guided Repair 001: MECHANICAL_NO_GO due hidden-spec leakage.
VERIFY_RULE Validator Hardening 001: GO — 24/24, FP/FN 0/0, contradiction/forbidden-heuristic reject 2/2.

Resume only after the current 30B runtime priority.

## 3. Apple MoE paging feasibility — GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`

Frozen PoC:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Verified binary SHA:
`c65a60d78d47aca232beaac2161090914b4c0cca79975b46227a1d32b5643844`.

Base M1 8GB feasibility established native Metal build, bounded MoE slots/LRU + `pread` + Metal synchronization and plausible S8/S16/S24 memory projections. S32 rejected.

## 4. Stage 1 001 — closed mechanical

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-result.md`

Classification:
`LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO`.

No scientifically valid S8/S16/S24 measurement exists. First attempt was invalid from stdio pipe backpressure; post-correction execution exposed a second evidence-durability flaw. No model/runtime performance claim follows.

## 5. Harness recovery — GO

Classification:
`LOOM_30B_STAGE1_HARNESS_RECOVERY_GO`.

Evidence:
`results-local/research/30b-stage1-harness-recovery-001/20260829T195240Z/`

Frozen recovered local runner:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`
SHA256 `6857a7f7deeb6c8d88db81df4ce06e4ac2e571079971cebdd16718b625930ecf`.
Size 446 lines / 26,980 bytes.

Recovery proves continuous >2 MiB output drain, incremental telemetry, clean/nonzero-exit persistence, and resume-to-pre-inference behavior without launching a model.

## 6. Current — Apple MoE Paging Stage1R 001

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-stage1r-001-preregistration.md`

Reuse only existing verified artifact:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Size `12,424,439,872` bytes.
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.
No model download authorized.

Freeze checks before inference:
- harness SHA exact;
- model SHA/size exact;
- source commit exact;
- binary SHA exact;
- no conflicting process.

Frozen real-generation sweep remains:
- S8;
- S16;
- conditional S24 if S16 safety gate passes;
- never S32;
- temp 0, max 96 generated tokens, ctx 1024;
- `--moe-n-layers 48`, `--no-mmap`, `--no-warmup`, `--cpu-moe`, `-ub 1`;
- fresh process per measured profile;
- no post-hoc tuning or retry of a scientifically valid profile.

Evidence must be durable before launch, streamed incrementally during execution, and finalized on all exit paths.

GO requires at least one coherent clean run and best safe generation >=2.5 tok/s without critical host pressure/corruption and with exact provenance/evidence.

## 7. If Stage1R GO

Stage 2 must establish reproducibility and fresh matched practical/quality comparison against canonical DEEP custom MLX. Measure TTFT/load, decode tok/s, E2E wall, memory/wired/compressed/swap, storage/cache behavior and output quality/correctness.

Do not replace canonical DEEP solely from one Stage1R speed result.

## 8. If Stage1R scientific NO_GO

Do not download a second quant or tune flags post hoc. Diagnose whether the valid observed failure is throughput, memory pressure, compatibility or output corruption. Any alternative quant/runtime requires a fresh preregistration.

## 9. Later work

After this runtime priority:
- resume sanitized validator-guided repair/selective-DEEP graph;
- semantic verifier/open-ended validation;
- automatic validator/contract derivation;
- provider/UI;
- mandatory Heretic;
- FAST clean-runtime reintroduction.
