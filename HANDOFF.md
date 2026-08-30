# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — Stage1R2 Apple Metal MoE paging GO at 4.40 tok/s. Comparability audit proved historical MLX and new GGUF are architecture-matched but checkpoint-different. Stage2 product-candidate validation is now preregistered.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_STAGE2_PRODUCT_CANDIDATE_VALIDATION_001`
Pi context: `/AGENTS.md` v3.71.

## Product direction

- BALANCED 8B remains provisional primary at ~13 tok/s.
- Historical DEEP custom MLX remains ~1.4 tok/s.
- Apple Metal MoE paging is the leading DEEP candidate after S24 reached 4.40 tok/s safely.
- New candidate is `Qwen3-30B-A3B-Instruct-2507`; historical MLX derives from `Qwen3-30B-A3B`. Stage2 is therefore a product comparison, not strict same-checkpoint runtime parity.
- LOOM AUTO validator-first work remains paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Best safe S24:
- 4.40 generation tok/s;
- 3.95 prompt tok/s;
- load 14.426 s;
- E2E 37.704 s;
- RSS 2935.766 MiB;
- swap 1125.94 MiB;
- minimum headroom 13%;
- no critical pressure/OOM/corruption/runaway.

Verified GGUF SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Frozen runtime:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
with `llama-completion -no-cnv` SHA256 `38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

## Comparability audit — COMPLETE

Canonical result:
`research/architecture/loom-30b-stage2-comparability-audit-001-result.md`

Classification:
`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`.

Historical MLX:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`, upstream `Qwen/Qwen3-30B-A3B`, MLX Q4/group128.

New candidate:
`Qwen/Qwen3-30B-A3B-Instruct-2507`, ByteShape Q3_K_S-3.25bpw.

Shared core MoE topology: 48 layers, 128 experts, top-8, hidden 2048. Checkpoint/version, RoPE/context, quantization and chat template differ.

## Exact next action — Stage2 product-candidate validation

Preregistration:
`research/architecture/loom-30b-stage2-product-candidate-validation-001-preregistration.md`

Block A:
- Apple S24 only;
- exact Stage1R2 prompt;
- 3 fresh processes;
- reproducibility gate: 3/3 clean, median >=4.0 tok/s, no run <3.5, no critical pressure/OOM/corruption/runaway, swap <=3.5 GiB.

Block B:
- 7 fresh matched practical tasks on both historical MLX and Apple S24;
- temperature 0;
- same semantic prompt, each product using its canonical tokenizer/chat template;
- T1–T5 deterministic validation; T6–T7 frozen rubrics;
- measure decode/prompt throughput, load/TTFT where available, E2E and host memory/swap.

GO additionally requires:
- Apple objective score >=4/5 and at most one PASS below MLX;
- Apple rubric total at most one point below MLX;
- Apple matched generation throughput >=2.0x MLX;
- Apple median matched E2E <=0.80x MLX;
- no critical host failure and peak swap <=3.5 GiB;
- complete durable evidence.

GO:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.

A GO makes Apple MoE paging eligible to become canonical DEEP on product utility grounds only.

## After Stage2

If GO, canonicalize DEEP promotion, then open a separate 30B acceleration funnel. Primary reference: mini-SGLang concepts — persistent/prefix caching, chunked prefill, overlap scheduling and expert/I/O prefetch — independently adapted to Apple Silicon. Caveman-style deterministic context packing follows as end-to-end optimization.
