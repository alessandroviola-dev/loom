# LOOM — Pi Agent Protocol

Version: 3.71
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
- DEEP: historical custom MLX path ~1.4 tok/s. Apple Metal MoE paging Stage1R2 reached 4.40 tok/s and is the leading DEEP candidate, but the candidate checkpoint differs from historical MLX.
- FAST: concept retained; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but PAUSED during 30B runtime investigation.
- LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Classification:
**`LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_GO`**.

Best safe S24:
- generation 4.40 tok/s;
- prompt 3.95 tok/s;
- load 14.426 s;
- E2E 37.704 s;
- RSS 2935.766 MiB;
- swap 1125.94 MiB;
- minimum headroom 13%;
- no critical pressure/OOM/corruption/runaway.

New candidate artifact:
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
**`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`**.

Historical MLX:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`
Declared upstream `Qwen/Qwen3-30B-A3B`; MLX affine Q4/group128.

New candidate upstream identity:
`Qwen/Qwen3-30B-A3B-Instruct-2507`; ByteShape Q3_K_S-3.25bpw.

Core architecture matches 48 layers / 128 experts / top-8 / hidden 2048, but checkpoint/version, RoPE/context, quantization and chat-template text differ. Historical 1.402 and 1.229233 tok/s remain contextual references only.

## Current checkpoint — Stage2 product-candidate validation 001

Preregistration:
`research/architecture/loom-30b-stage2-product-candidate-validation-001-preregistration.md`

Stage2 compares the historical MLX and Apple MoE candidates as different-checkpoint products, not as a strict runtime-only experiment.

Frozen plan:
- Block A: Apple S24 reproducibility, 3 fresh processes on the Stage1R2 prompt;
- Block B: 7 fresh matched practical tasks on historical MLX and Apple S24;
- temperature 0, same semantic prompts, own canonical tokenizer/chat template per candidate;
- exact provenance and durable telemetry/output evidence;
- objective tasks T1–T5 plus frozen rubrics T6–T7;
- no prompt tuning/retry after results begin.

Promotion gate requires, among other frozen conditions:
- S24 reproducibility median >=4.0 tok/s, no run <3.5;
- new candidate objective score >=4/5 and at most one PASS below historical;
- rubric total at most one point below historical;
- matched generation throughput >=2.0x historical;
- median matched E2E <=0.80x historical;
- no critical memory/OOM/corruption/runaway and peak swap <=3.5 GiB.

GO classification:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.

A GO may promote Apple MoE paging to canonical DEEP on product-utility grounds, but may not claim same-checkpoint runtime-only parity.

No model download, package install, runtime/source/model modification, slot tuning, mini-SGLang acceleration, Heretic integration, provider/UI work or Git action by Pi during Stage2.

## After Stage2

Open a separate 30B acceleration funnel if Stage2 validates the candidate. Primary architectural reference from repository research bundle: mini-SGLang concepts — persistent/prefix caching, chunked prefill, overlap scheduling and expert/I/O prefetch — independently adapted for Apple Silicon. Caveman-style context packing is secondary end-to-end optimization.
