# LOOM — Pi Agent Protocol

Version: 3.72
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not commit/push/PR/edit project decision docs unless explicitly authorized.
GitHub is canonical. Active clone: `<repository-root>`.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue/post-hoc gate relaxation;
3. fail closed before expensive execution;
4. invalid/inconclusive runs support no performance claim;
5. production code requires exact review + Git persistence;
6. do not tune on exposed evaluation examples;
7. hidden ground truth/spec metadata must never enter model repair/judge inputs unless explicitly preregistered as public input;
8. expensive model downloads require an explicit preregistered checkpoint.

## Product direction

**Big models. Small machines.**
- BALANCED: Qwen3-8B 3-bit/group64 Direct MLX, ~13 tok/s, provisional primary.
- DEEP: **Apple Metal MoE paging is now canonical** after Stage2 product-candidate GO. Current model is Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw at S24. Historical custom MLX ~1.4 tok/s is retained as historical comparison/fallback only.
- FAST: concept retained; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but PAUSED during 30B acceleration work.
- LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Best safe S24 on frozen Stage1 workload:
- generation 4.40 tok/s;
- prompt 3.95 tok/s;
- load 14.426 s;
- E2E 37.704 s;
- RSS 2935.766 MiB;
- swap 1125.94 MiB;
- minimum headroom 13%;
- no critical pressure/OOM/corruption/runaway.

Candidate artifact:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Frontend:
`llama-completion -no-cnv`
SHA256 `38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

## Stage2 comparability audit — COMPLETE

Canonical result:
`research/architecture/loom-30b-stage2-comparability-audit-001-result.md`

Classification:
`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`.

Historical MLX:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`
(upstream `Qwen/Qwen3-30B-A3B`, MLX affine Q4/group128).

New DEEP upstream identity:
`Qwen/Qwen3-30B-A3B-Instruct-2507`, ByteShape Q3_K_S-3.25bpw.

Shared core topology: 48 layers / 128 experts / top-8 / hidden 2048. Checkpoint/version, RoPE/context, quantization and chat-template text differ. Do not claim same-checkpoint runtime-only superiority.

## Stage2 product-candidate validation — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-stage2-product-candidate-validation-001-result.md`

Classification:
**`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`**.

Block A S24 reproducibility:
- 4.38, 4.39, 4.39 tok/s;
- median **4.39 tok/s**;
- all clean; no critical pressure/runaway; peak swap ~1.5 GiB.

Fresh matched suite H historical MLX vs N Apple S24:
- objective T1–T5: H 2/5, N **4/5**;
- rubric T6–T7: H 6/6, N **5/6**;
- median generation: H 1.437, N **3.730 tok/s**;
- pooled generation: H 1.444, N **4.059 tok/s** = **2.81x**;
- median E2E: H 65.909 s, N **26.380 s** = **0.40x**;
- no critical memory/OOM/corruption/runaway.

All preregistered promotion gates passed. Apple S24 is now canonical DEEP on product-utility grounds. This is a different-checkpoint product decision, not a same-model one-factor runtime claim.

## Current checkpoint — 30B acceleration funnel design

Primary architectural reference from the repository research bundle: mini-SGLang concepts, independently adapted for Apple Silicon:
- persistent process / stable prefix caching;
- KV/prompt reuse;
- chunked prefill;
- overlap scheduling;
- expert/I/O prefetch.

Secondary end-to-end optimization: Caveman-style deterministic context packing after runtime work.

First step: bounded persistent/cache feasibility audit with no production/runtime mutation. Establish what persistent frontend/cache mechanisms are already available in the frozen fork/build and what can be measured without patching source. Then preregister the first acceleration experiment.

Acceleration goal: protect the 4.39–4.40 tok/s validated baseline, reach 5+ first, then investigate 6–9 tok/s without unacceptable quality/memory cost.
