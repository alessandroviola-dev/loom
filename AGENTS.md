# LOOM — Pi Agent Protocol

Version: 3.70
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
- DEEP: historical custom MLX path ~1.4 tok/s. Apple Metal MoE paging Stage1R2 reached 4.40 tok/s and is now the leading DEEP candidate, but checkpoint identity differs from historical MLX so Stage2 must be a product-candidate comparison rather than strict runtime parity.
- FAST: concept retained; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but PAUSED during this runtime investigation.
- LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Validator track — PAUSED cleanly

VERIFY_RULE Validator Hardening 001 completed **GO**: 24/24, FP/FN 0/0, contradiction reject 2/2, forbidden-heuristic reject 2/2, p95 0.006542 ms. Planned sanitized guided-repair work is paused, not cancelled.

## Apple MoE paging Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Classification:
**`LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_GO`**.

Best safe profile S24:
- 4.40 generation tok/s
- 3.95 prompt tok/s
- load 14.426 s
- E2E 37.704 s
- RSS 2935.766 MiB
- wired 5032.297 MiB
- compressed 1567.734 MiB
- swap 1125.94 MiB
- minimum headroom 13%
- no critical pressure/OOM/corruption/runaway

Verified candidate:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Correct frontend:
`llama-completion -no-cnv`
SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

## Stage2 comparability audit — COMPLETE

Canonical result:
`research/architecture/loom-30b-stage2-comparability-audit-001-result.md`

Classification:
**`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`**.

Historical custom MLX artifact:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`
Declared upstream base:
`Qwen/Qwen3-30B-A3B`
Representation: MLX affine Q4/group128.

New GGUF identity:
`Qwen/Qwen3-30B-A3B-Instruct-2507`
ByteShape Q3_K_S-3.25bpw.

Shared architecture:
48 layers, 128 experts, top-8 routing, hidden size 2048.

Checkpoint/version, RoPE/context configuration, quantization and chat-template text differ. Tokenizer family aligns but byte-identical tokenizer identity is unproven.

Historical 1.402 tok/s and 1.229233 tok/s references both belong to the historical MLX lineage but different workloads. They remain contextual product references only.

## Current checkpoint — Stage2 product-candidate validation design

Next preregister a fresh Stage2 that treats historical MLX and Apple MoE paging as different checkpoint product candidates.

Stage2 must establish:
- S24 reproducibility across fresh processes;
- fresh matched practical-task comparison;
- decode/prompt throughput and E2E latency;
- load/TTFT where observable;
- memory/wired/compressed/swap stability;
- quality/correctness on fresh tasks;
- explicit product-selection gate.

Stage2 may support promotion of Apple MoE paging to canonical DEEP on product utility grounds, but must not claim same-checkpoint runtime-only parity.

After Stage2 validation, begin a separate 30B acceleration funnel. Primary architectural reference from the repository research bundle is mini-SGLang concepts: persistent/prefix caching, chunked prefill, overlap scheduling, and expert/I/O prefetch. Do not port CUDA-specific code blindly to Apple Silicon.

No product-default replacement before Stage2 result.