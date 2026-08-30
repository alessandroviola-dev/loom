# LOOM — Pi Agent Protocol

Version: 3.73
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
- DEEP: **Apple Metal MoE paging is canonical** after Stage2 product-candidate GO. Current model is Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw at S24.
- Historical custom MLX ~1.4 tok/s is retained as historical comparison/fallback only.
- FAST: concept retained; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but PAUSED during 30B acceleration work.
- LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Canonical DEEP baseline

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Frontend:
`llama-completion -no-cnv`
SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Profile:
S24 (`--moe-n-slots 24`).

Validated Stage1R2 baseline:
- ~4.39–4.40 generation tok/s;
- Stage1R2 load 14.426 s;
- no critical pressure/OOM/corruption/runaway.

Stage2 product validation:
- Apple S24 reproducibility 4.38 / 4.39 / 4.39 tok/s;
- matched pooled generation 4.059 tok/s vs historical MLX 1.444 = 2.81x;
- median E2E 26.380 s vs 65.909 s = 0.40x;
- objective score 4/5 vs 2/5 historical.

Canonical result:
`research/architecture/loom-30b-stage2-product-candidate-validation-001-result.md`

## Persistent/cache feasibility — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-accel-persistent-cache-feasibility-001-result.md`

Classification:
**`LOOM_30B_ACCEL_PERSISTENT_CACHE_FEASIBILITY_GO`**.

Evidence:
`results-local/research/30b-accel-persistent-cache-feasibility-001/20260830T101246Z/`

Audit result:
- no built `llama-server` exists in the frozen build;
- canonical `llama-completion` exposes explicit `--prompt-cache` support;
- first recommended no-patch factor is stable-prefix warm prompt cache versus cache-disabled baseline;
- no inference/GGUF open/source patch/build/download/package/Git action occurred during the audit.

Prompt cache is an end-to-end/prefill optimization candidate, not a direct decode-speed claim.

## Current checkpoint — prompt cache 001

Preregistration:
`research/architecture/loom-30b-accel-prompt-cache-001-preregistration.md`

Frozen experiment:
- same canonical S24 model/runtime;
- stable prefix frozen byte-for-byte;
- three independent rounds;
- each round B cache-disabled target -> W fresh-cache warm prompt -> C same-cache target;
- fresh process every invocation;
- `-n 8 -c 1024 --temp 0 --moe-n-slots 24 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -ub 1 -no-cnv`;
- only scientific factor is `--prompt-cache` reuse.

Primary GO requirement:
median warm-cache target prompt-eval wall <=0.70x cache-disabled target baseline, with lower E2E, decode preservation >=90%, correct deterministic outputs, safe memory and complete evidence.

No source/runtime/model/package mutation, rebuild, slot/ubatch tuning, prompt tuning, expert-prefetch work, Caveman, production work or Pi Git action.

## After prompt-cache

Next decode-focused checkpoint: paging/I/O attribution. Measure where S24 decode time is spent before preregistering expert prefetch/overlap work inspired by mini-SGLang concepts.

Acceleration goal: protect the 4.39–4.40 tok/s validated baseline, reach 5+ first, then investigate 6–9 tok/s without unacceptable quality or memory cost.
