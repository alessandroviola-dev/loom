# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — Stage2 product-candidate validation completed GO. Apple Metal MoE paging S24 is now canonical `loom-deep`. Current task is the 30B acceleration funnel, beginning with a bounded persistent/cache feasibility audit inspired by mini-SGLang concepts.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_ACCELERATION_PERSISTENT_CACHE_FEASIBILITY_001`
Pi context: `/AGENTS.md` v3.72.

## Product direction

- BALANCED 8B remains provisional primary at ~13 tok/s.
- DEEP is now Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging S24.
- Historical custom MLX ~1.4 tok/s is retained as historical comparison/fallback only.
- FAST retained conceptually; legacy 4B parked.
- LOOM AUTO validator-first work remains paused during 30B acceleration R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Validated S24 baseline:
- 4.40 generation tok/s;
- 3.95 prompt tok/s;
- load 14.426 s;
- E2E 37.704 s;
- RSS 2935.766 MiB;
- swap 1125.94 MiB;
- minimum headroom 13%;
- no critical pressure/OOM/corruption/runaway.

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Frozen runtime source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Frontend:
`llama-completion -no-cnv`, SHA256 `38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

## Stage2 comparability — COMPLETE

Historical MLX and Apple candidate are architecture-matched but checkpoint-different. Product utility comparisons are valid; same-checkpoint runtime-only superiority claims are not.

Historical MLX:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`.

New DEEP upstream:
`Qwen/Qwen3-30B-A3B-Instruct-2507`.

## Stage2 product-candidate validation — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-stage2-product-candidate-validation-001-result.md`

Classification:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.

Block A Apple S24 reproducibility:
- 4.38 / 4.39 / 4.39 tok/s;
- median 4.39 tok/s;
- no critical pressure/runaway; peak swap about 1.5 GiB.

Matched practical suite:
- objective T1–T5: historical 2/5, Apple 4/5;
- rubric T6–T7: historical 6/6, Apple 5/6;
- pooled generation: 1.444 vs 4.059 tok/s = 2.81x;
- median E2E: 65.909 vs 26.380 s = 0.40x;
- no critical memory/OOM/corruption/runaway.

All frozen promotion gates passed. Apple S24 is canonical DEEP on product-utility grounds.

## Exact next action — acceleration feasibility audit

Primary architecture reference: mini-SGLang concepts adapted independently for Apple Silicon.

First audit before runtime mutation:
1. inspect frozen fork/build for persistent frontend/server support;
2. identify stable-prefix / KV or prompt-cache mechanisms already available;
3. verify whether S24 MoE paging flags are accepted by the persistent frontend;
4. identify observable cache/prompt/decode metrics without source patching;
5. determine whether existing build can test persistent/warm behavior without model download or source mutation;
6. map expert/I/O prefetch hooks in the frozen source for the later direct decode-throughput experiment.

No production promotion work remains: DEEP promotion is complete.

After audit, preregister first acceleration experiment. Priority sequence:
- persistent process/cache behavior;
- paging/I/O attribution;
- overlap/expert prefetch;
- controlled lighter quant only under a separate download/quality preregistration if still justified;
- Caveman-style context packing later for end-to-end agent speed.

Target: 5+ tok/s first; investigate 6–9 tok/s without unacceptable quality or memory cost.
