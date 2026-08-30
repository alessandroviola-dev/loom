# LOOM Roadmap

Last updated: 2026-08-30
Current: Stage1R2 Apple Metal MoE paging GO at 4.40 tok/s. Comparability audit completed: historical MLX and new GGUF are architecture-matched but checkpoint-different. Stage2 product-candidate validation is preregistered. Validator/guided-repair remains PAUSED.
Canonical context: `/AGENTS.md` v3.71.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional primary.
- `loom-deep`: historical custom MLX ~1.4 tok/s; Apple Metal MoE paging candidate S24 reaches 4.40 tok/s.
- `loom-fast`: future clean-runtime tier; legacy 4B parked.
- `loom-auto`: validator-first architecture planned but paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

Do not replace canonical DEEP before Stage2 product validation.

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

Candidate model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`.

## 3. Comparability audit — COMPLETE

Canonical result:
`research/architecture/loom-30b-stage2-comparability-audit-001-result.md`

Classification:
`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`.

Historical MLX lineage:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`, upstream `Qwen/Qwen3-30B-A3B`, MLX affine Q4/group128.

New candidate:
`Qwen/Qwen3-30B-A3B-Instruct-2507`, ByteShape Q3_K_S-3.25bpw.

Core MoE structure matches, but checkpoint/version, RoPE/context, quantization and chat-template text differ. Strict same-checkpoint runtime/quality parity claims are forbidden.

## 4. Current — Stage2 product-candidate validation 001

Preregistration:
`research/architecture/loom-30b-stage2-product-candidate-validation-001-preregistration.md`

Block A:
- S24 reproducibility over 3 fresh Apple processes;
- median >=4.0 tok/s, no run <3.5;
- no critical pressure/OOM/corruption/runaway;
- swap <=3.5 GiB.

Block B:
- 7 fresh matched practical tasks on historical MLX and Apple S24;
- temp 0, same semantic prompts;
- product-native tokenizer/chat template allowed;
- objective validation T1–T5 and frozen rubrics T6–T7;
- measure decode/prompt throughput, load/TTFT when observable, E2E, memory/wired/compressed/swap.

GO requires all preregistered gates, including:
- Apple objective >=4/5 and at most one PASS below historical;
- rubric total at most one point below historical;
- Apple matched generation throughput >=2.0x historical;
- Apple median matched E2E <=0.80x historical;
- complete safe evidence.

GO classification:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.

A GO may promote Apple Metal MoE paging to canonical DEEP on product-utility grounds only.

## 5. After Stage2 — 30B acceleration funnel

Primary architecture reference from the repository research bundle: mini-SGLang concepts, independently adapted for Apple Silicon:
- persistent process / stable prefix caching;
- KV/prompt reuse;
- chunked prefill;
- overlap scheduling;
- expert/I/O prefetch.

Secondary end-to-end optimization: Caveman-style deterministic context packing.

Goal: move from current 4.40 tok/s toward 5+ first, then investigate whether 6–9 tok/s is achievable without unacceptable quality or memory cost.

## 6. Later work

After the 30B runtime priority:
- resume sanitized validator-guided repair/selective-DEEP graph;
- semantic verifier/open-ended validation;
- automatic validator/contract derivation;
- provider/UI;
- mandatory Heretic;
- FAST clean-runtime reintroduction.
