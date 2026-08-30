# LOOM Roadmap

Last updated: 2026-08-30
Current: Apple Metal MoE paging S24 is canonical `loom-deep`. Persistent/cache feasibility completed GO. Immediate priority is the preregistered `--prompt-cache` experiment, followed by paging/I/O attribution for direct decode acceleration. Validator/guided-repair remains PAUSED.
Canonical context: `/AGENTS.md` v3.73.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional primary.
- `loom-deep`: **Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging S24**.
- historical custom MLX ~1.4 tok/s: retained as historical comparison/fallback only.
- `loom-fast`: future clean-runtime tier; legacy 4B parked.
- `loom-auto`: validator-first architecture planned but paused during 30B acceleration R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## 2. Canonical DEEP validation

Stage1R2:
`LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_GO`.
Best safe S24 ~4.40 tok/s.

Stage2 comparability:
`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`.

Stage2 product validation:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.
Apple S24 reproducibility 4.38 / 4.39 / 4.39 tok/s; matched pooled generation 2.81x historical MLX; median E2E 0.40x historical; all promotion gates passed.

## 3. 30B acceleration funnel

Primary architectural reference: mini-SGLang concepts adapted independently for Apple Silicon.

Priority sequence:
1. prompt/prefix cache no-patch experiment;
2. paging/I/O attribution;
3. overlap scheduling / expert I/O prefetch;
4. controlled lighter quant only under separate artifact + quality preregistration if still justified;
5. persistent server path only under explicit build preregistration if useful;
6. Caveman-style deterministic context packing for end-to-end agent speed.

Target sequence:
- preserve ~4.39–4.40 tok/s baseline;
- reach 5+ decode tok/s;
- then investigate 6–9 tok/s;
- reject gains with unacceptable quality loss or memory instability.

## 4. Persistent/cache feasibility — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-accel-persistent-cache-feasibility-001-result.md`

Classification:
`LOOM_30B_ACCEL_PERSISTENT_CACHE_FEASIBILITY_GO`.

Evidence:
`results-local/research/30b-accel-persistent-cache-feasibility-001/20260830T101246Z/`.

Findings:
- no built `llama-server` available;
- canonical `llama-completion` supports explicit `--prompt-cache`;
- recommended first no-patch factor: exact stable-prefix warm prompt cache vs cache-disabled baseline;
- no inference/runtime mutation occurred during audit.

## 5. Current — prompt cache 001

Preregistration:
`research/architecture/loom-30b-accel-prompt-cache-001-preregistration.md`

Design:
- same canonical model/runtime/S24;
- frozen stable prefix and deterministic warm/target suffixes;
- 3 independent rounds;
- B cache-disabled target -> W fresh-cache warm -> C same-cache target;
- fresh process each invocation;
- primary metric prompt/prefill wall C/B;
- secondary E2E/cache/decode/memory metrics.

GO requires at least 30% median prompt-eval wall reduction, lower median E2E, >=90% decode-throughput preservation, correct outputs and safe memory.

This experiment optimizes prefill/E2E, not direct decode.

## 6. Next decode-focused checkpoint

After prompt-cache result, run paging/I/O attribution on canonical S24.

Measure enough evidence to distinguish:
- expert cache hit/miss behavior;
- expert bytes read per output token;
- synchronous `pread` cost;
- storage wait vs compute time;
- whether an expert prefetch/overlap intervention has sufficient headroom to plausibly push decode beyond 5 tok/s.

Do not patch runtime before the attribution checkpoint is preregistered and completed.

## 7. Later work

After 30B runtime priority:
- Caveman-style context packing;
- resume sanitized validator-guided repair/selective-DEEP graph;
- semantic verifier/open-ended validation;
- automatic validator/contract derivation;
- provider/UI;
- mandatory Heretic;
- FAST clean-runtime reintroduction.
