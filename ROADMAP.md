# LOOM Roadmap

Last updated: 2026-08-29
Current: Apple Metal MoE expert paging Stage1R2 completed **GO**. Best safe S24 reached 4.40 tok/s on the frozen Stage1 workload with no critical memory/OOM/corruption/runaway event. Immediate priority is a bounded Stage2 comparability audit before reproducibility + matched practical/quality evaluation. Validator/guided-repair remains PAUSED.
Canonical context: `/AGENTS.md` v3.69.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional primary.
- `loom-deep`: historical custom MLX Qwen3-30B-A3B path ~1.4 tok/s; Apple Metal MoE paging candidate now reaches 4.40 tok/s on Stage1R2.
- `loom-fast`: future clean-runtime tier; legacy 4B parked.
- `loom-auto`: validator-first architecture planned but paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

Do not replace canonical DEEP until Stage2 establishes reproducibility and quality/correctness preservation.

## 2. Validator track — paused cleanly

Output Validator v0: GO.
Selective Rescue 001: scientific NO_GO at 5/8 final CORRECT, zero false accepts.
8B Validator-Guided Repair 001: MECHANICAL_NO_GO from hidden-spec leakage.
VERIFY_RULE Validator Hardening 001: GO — 24/24, FP/FN 0/0, contradiction/forbidden-heuristic reject 2/2.

Resume only after the current 30B runtime priority.

## 3. Apple MoE paging feasibility — GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-result.md`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Mechanism/build feasibility established native Metal support, bounded expert slots/LRU, `pread`, Apple synchronization path and plausible S8/S16/S24 memory projections. S32 rejected.

## 4. Stage1 / Stage1R — closed mechanically

Stage1:
`LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO`.

Stage1R:
`LOOM_30B_APPLE_MOE_PAGING_STAGE1R_MECHANICAL_NO_GO`.

These attempts support no performance claim. Mechanical causes were stdio/evidence failures and interactive `llama-cli` use.

## 5. Noninteractive frontend recovery — GO

Canonical result:
`research/architecture/loom-30b-noninteractive-frontend-recovery-001-result.md`

Correct one-shot frontend:
`llama-completion -no-cnv`.

Frozen binary SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

Frozen recovered harness SHA256:
`4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`.

Harness uses direct durable output streaming, bounded parent-memory accounting, incremental telemetry/finalization and 64 MiB/profile runaway protection.

## 6. Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Evidence:
`results-local/research/30b-apple-moe-paging-stage1r2-001/20260829T211631Z/final-report.json`

Classification:
`LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_GO`.

Verified candidate:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
Size `12,424,439,872` bytes.
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Measured frozen workload:

| Profile | Generation tok/s | Prompt tok/s | Load | E2E | Min headroom | Peak swap |
|---|---:|---:|---:|---:|---:|---:|
| S8 | 2.99 | 2.95 | 19.294 s | 52.606 s | 33% | 1110.0 MiB |
| S16 | 3.58 | 3.43 | 16.625 s | 45.110 s | 22% | 1110.0 MiB |
| S24 | **4.40** | **3.95** | **14.426 s** | **37.704 s** | 13% | 1125.94 MiB |

S24 passed all safety/functional gates. No critical memory pressure, OOM, corruption, NaN, repeated-token collapse or output-runaway occurred.

Historical contextual S24 speedups:
- 3.1384× vs 1.402 tok/s compact practical DEEP reference;
- 3.5795× vs 1.229233 tok/s historical exact-Q4 reference.

These are practical historical references, not strict same-model one-factor comparisons. TTFT was not separately observable.

## 7. Current — Stage2 comparability audit

Before matched quality/performance Stage2, identify the exact historical custom MLX 30B checkpoint/artifact behind the ~1.4 tok/s references.

Classify historical-vs-new model identity as:
- exact checkpoint-identical;
- same architecture/family but different checkpoint;
- insufficient provenance for strict quality matching.

Audit only existing metadata/artifacts. No inference/download/package/source/model mutation.

## 8. Stage2 after comparability audit

Preregister a fresh bounded Stage2 covering:
- S24 reproducibility across fresh processes;
- fresh matched practical tasks;
- decode/prompt throughput;
- load/TTFT where observable and E2E wall;
- memory/wired/compressed/swap stability;
- output quality/correctness preservation;
- explicit interpretation rules if checkpoint identity differs.

A Stage2 GO may promote Apple Metal MoE paging toward canonical DEEP. Do not change product defaults before that result.

## 9. Later work

After the 30B runtime priority:
- resume sanitized validator-guided repair/selective-DEEP graph;
- semantic verifier/open-ended validation;
- automatic validator/contract derivation;
- provider/UI;
- mandatory Heretic;
- FAST clean-runtime reintroduction.