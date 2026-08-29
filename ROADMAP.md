# LOOM Roadmap

Last updated: 2026-08-29
Current: `LOOM_30B_APPLE_MOE_PAGING_FEASIBILITY_GO` completed on base M1 8GB. Immediate priority is Stage 1 real generation with one ByteShape Q3_K_S-3.25bpw GGUF. Validator/guided-repair work remains PAUSED.
Canonical context: `/AGENTS.md` v3.66.

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

Result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`

Frozen PoC:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Base M1 8GB evidence:
- native Metal build successful;
- Apple Metal device exposed;
- bounded MoE slots/LRU + `pread` + Metal sync source path confirmed;
- local storage diagnostic ~2579.51 MiB/s;
- Q3_K_S-3.25 projected totals S8 6.304 GiB, S16 6.954, S24 7.604, S32 8.253;
- 32 slots rejected;
- selected Q3_K_S-3.25bpw for Stage 1.

This GO is mechanism/build feasibility only, not an inference-speed claim.

## 4. Current — Apple MoE Paging Stage 1 001

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-stage1-001-preregistration.md`

Exactly one authorized download:
`byteshape/Qwen3-30B-A3B-Instruct-2507-GGUF/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.
Published size ~12.4 GB; normalized quality 97.97%.

Frozen real-generation sweep:
- 8 expert slots;
- 16 expert slots;
- conditional 24 expert slots if S16 safety gate passes;
- identical `-ub 1` to preserve slot-count as the sweep factor;
- no 32 slot run;
- 48 MoE layers, no mmap, no warmup, exact expert CPU override.

GO requires at least one coherent clean run and best safe generation >=2.5 tok/s without critical host pressure or corruption.

## 5. If Stage 1 GO

Stage 2 must test reproducibility and a fresh matched practical comparison against canonical DEEP custom MLX. Measure:
- TTFT/load behavior;
- decode tok/s;
- E2E wall;
- memory/wired/compressed/swap;
- storage traffic/cache behavior;
- output quality/correctness.

Do not replace canonical DEEP solely from one Stage-1 speed result.

## 6. If Stage 1 NO_GO

Do not download a second quant post hoc. Diagnose whether the failure is throughput, memory pressure, model/runtime compatibility or output corruption. Any alternative quant/runtime requires a fresh preregistration.

## 7. Later work

After this runtime priority:
- resume sanitized validator-guided repair/selective-DEEP graph;
- semantic verifier/open-ended validation;
- automatic validator/contract derivation;
- provider/UI;
- mandatory Heretic;
- FAST clean-runtime reintroduction.
