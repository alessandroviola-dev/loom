# LOOM Roadmap

Last updated: 2026-08-30
Current: Stage2 product-candidate validation completed GO. Apple Metal MoE paging S24 is now canonical `loom-deep`. Immediate priority is the 30B acceleration funnel, beginning with a persistent/cache feasibility audit inspired by mini-SGLang concepts. Validator/guided-repair remains PAUSED.
Canonical context: `/AGENTS.md` v3.72.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional primary.
- `loom-deep`: **Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging S24**.
- historical custom MLX ~1.4 tok/s: retained as historical comparison/fallback only.
- `loom-fast`: future clean-runtime tier; legacy 4B parked.
- `loom-auto`: validator-first architecture planned but paused during 30B acceleration R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## 2. Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Best safe S24:
- generation 4.40 tok/s;
- prompt 3.95 tok/s;
- load 14.426 s;
- E2E 37.704 s;
- peak swap 1125.94 MiB;
- minimum headroom 13%;
- no critical pressure/OOM/corruption/runaway.

## 3. Stage2 comparability audit — COMPLETE

Classification:
`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`.

Historical MLX lineage:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`.

New DEEP upstream identity:
`Qwen/Qwen3-30B-A3B-Instruct-2507`.

Architecture matches but checkpoint/version, RoPE/context, quantization and chat template differ. Do not claim strict same-checkpoint runtime parity.

## 4. Stage2 product-candidate validation — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-stage2-product-candidate-validation-001-result.md`

Classification:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.

Reproducibility:
- Apple S24 fresh-process runs: 4.38 / 4.39 / 4.39 tok/s;
- median 4.39 tok/s.

Fresh matched practical suite:
- objective T1–T5: historical 2/5, Apple 4/5;
- rubric T6–T7: historical 6/6, Apple 5/6;
- pooled generation: historical 1.444, Apple 4.059 tok/s = 2.81x;
- median E2E: historical 65.909 s, Apple 26.380 s = 0.40x;
- no critical memory/OOM/corruption/runaway.

All preregistered product-selection gates passed. Apple S24 is promoted to canonical DEEP on product-utility grounds.

## 5. Current — 30B acceleration funnel

Primary architecture reference from the repository research bundle: mini-SGLang concepts, independently adapted for Apple Silicon.

Priority order:
1. persistent process / stable-prefix cache feasibility audit;
2. persistent/warm S24 experiment if mechanically supported;
3. paging/I/O attribution;
4. overlap scheduling and expert/I/O prefetch;
5. controlled lighter-quant experiment only under separate artifact/quality preregistration if justified;
6. Caveman-style deterministic context packing for end-to-end agent speed.

Do not port CUDA-specific mini-SGLang implementation blindly.

Acceleration objectives:
- preserve validated ~4.39–4.40 tok/s baseline;
- reach 5+ tok/s first;
- then investigate 6–9 tok/s;
- reject gains that introduce unacceptable quality loss, critical memory pressure, OOM or unstable swap behavior.

## 6. Immediate checkpoint

`LOOM_30B_ACCELERATION_PERSISTENT_CACHE_FEASIBILITY_001`

Metadata/source/build audit only before modifying the promoted runtime. Determine:
- persistent frontend/server support in frozen fork/build;
- S24 flag compatibility;
- existing prompt/KV/prefix caching controls;
- observable timing/cache metrics without source patching;
- whether a bounded persistent/warm experiment can be run without download/source mutation;
- source locations suitable for later expert/I/O prefetch experiments.

## 7. Later work

After the 30B runtime priority:
- resume sanitized validator-guided repair/selective-DEEP graph;
- semantic verifier/open-ended validation;
- automatic validator/contract derivation;
- provider/UI;
- mandatory Heretic;
- FAST clean-runtime reintroduction.
