# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — Apple Metal MoE expert paging Stage1R2 completed GO at 4.40 tok/s on S24. Stage2 comparability audit completed and proved the historical MLX and new GGUF are architecture-matched but checkpoint-different. Current task is to preregister a Stage2 product-candidate comparison before any DEEP default change.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_STAGE2_PRODUCT_CANDIDATE_VALIDATION_DESIGN`
Pi context: `/AGENTS.md` v3.70.

## Product direction

- BALANCED 8B remains provisional primary at ~13 tok/s.
- Historical DEEP custom MLX path remains ~1.4 tok/s.
- Apple Metal MoE paging is the leading DEEP candidate after S24 reached 4.40 tok/s safely.
- Because the new candidate is `Qwen3-30B-A3B-Instruct-2507` while the historical MLX lineage derives from `Qwen3-30B-A3B`, Stage2 must compare product utility, not strict same-checkpoint runtime parity.
- LOOM AUTO validator-first work remains paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Best safe S24:
- generation 4.40 tok/s
- prompt 3.95 tok/s
- load 14.426 s
- E2E 37.704 s
- RSS 2935.766 MiB
- swap 1125.94 MiB
- minimum headroom 13%
- no critical pressure/OOM/corruption/runaway

Verified GGUF:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Frozen runtime:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
with `llama-completion -no-cnv`.

## Stage2 comparability audit — COMPLETE

Canonical result:
`research/architecture/loom-30b-stage2-comparability-audit-001-result.md`

Classification:
`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`.

Historical MLX:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`
Declared upstream: `Qwen/Qwen3-30B-A3B`.
MLX affine Q4/group128.

New GGUF:
ByteShape `Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw`.
Embedded upstream: `Qwen/Qwen3-30B-A3B-Instruct-2507`.

Architecture matches on 48 layers / 128 experts / top-8 / hidden 2048. Checkpoint/version, RoPE/context configuration, quantization and chat template differ. Tokenizer family aligns but byte-identical tokenizer identity is unproven.

Historical 1.402 tok/s and 1.229233 tok/s references are both from the historical MLX lineage but under different workloads; both are contextual only.

## Exact next action

Preregister a fresh bounded Stage2 product-candidate validation:
1. verify S24 reproducibility across fresh processes;
2. run fresh matched practical tasks on historical MLX and new Apple MoE candidate;
3. measure decode/prompt throughput, load/TTFT where observable, E2E, memory/wired/compressed/swap;
4. score quality/correctness under frozen criteria;
5. decide whether Apple MoE paging is good enough to promote as canonical DEEP on product utility grounds.

No strict same-checkpoint quality/runtime claim is allowed.

After Stage2, open a separate 30B acceleration funnel. Primary reference from the repository research bundle: mini-SGLang concepts (persistent/prefix cache, chunked prefill, overlap scheduling, expert/I/O prefetch), adapted independently for Apple Silicon rather than porting CUDA-specific code.
