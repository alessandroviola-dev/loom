# LOOM Roadmap

Last updated: 2026-08-30
Current: accelerated macro-work-package mode. WP1 Runtime + Product Serving completed GO. Canonical DEEP runtime is S32 at 5.596 tok/s median decode on persistent localhost `llama-server`; S24 remains rollback. WP2 Context Intelligence is now authorized and active with Caveman + Cavemem only.
Canonical context: `/AGENTS.md` v3.82.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
WP2 contract: `research/integration/loom-context-intelligence-wp2.md`.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional lighter tier.
- `loom-deep`: Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging **S32** through persistent localhost `llama-server`.
- S24: validated rollback profile.
- historical custom MLX ~1.4 tok/s: historical comparison/fallback only.
- `loom-fast`: later clean-runtime tier.

Goal of current push: a practical local LOOM stack on the M1 8 GiB host using a small number of macro work packages.

## 2. WP1 — COMPLETE / GO

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Canonical model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Canonical `llama-server` SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`.

Matched deterministic S24/S32 3x96-token A/B, byte-identical output:
- S24 median decode **4.382 tok/s**, E2E **29.185 s**;
- S32 median decode **5.596 tok/s**, E2E **23.849 s**;
- S32/S24 decode **1.2768x**;
- S32/S24 E2E **0.8172**.

S32 resource result:
- peak RSS `3914.6 MiB`;
- peak sampled swap `1651.88 MiB`;
- minimum sampled free memory `10%`;
- no crash/OOM/corruption/critical pressure indication.

Operational stack:
- existing embedded `llama-server` WebUI at `http://127.0.0.1:18080/`;
- OpenAI-compatible API at `http://127.0.0.1:18080/v1/chat/completions`;
- Pi connected to `http://127.0.0.1:18080/v1` and verified with a real offline request;
- localhost-only/offline configuration;
- operational start/status/health/stop script.

Serving-path stable-prefix cache reuse directly validated:
- cold 136 prompt tokens / 27.809 s;
- reuse 134 cached + 2 evaluated / 280.389 ms;
- reuse E2E 0.332 s.

Provider/model label cleanup from `loom-deep-30b-s24` to S32 naming is authorized mechanically inside WP2 if compatibility is preserved.

## 3. WP2 — Context Intelligence — ACTIVE

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Contract:
`research/integration/loom-context-intelligence-wp2.md`

Goal:
reduce provider-facing context and improve long-running project continuity without adding a heavy agent framework or permanent model/tool overhead.

Permanent mechanisms selected:

### Caveman-derived context layer
- deterministic lexical/BM25-style relevance scoring;
- explicit priority + recency + error/warning + pin preservation;
- select under token budget, then restore chronology;
- deterministic typed compression for real LOOM/Pi logs/search/JSON/code/diffs;
- exact machine-critical values preserved;
- every omission exactly recoverable through local handles;
- small/no-op content bypasses compression when net-negative.

### Cavemem-derived memory layer
- project-scoped local SQLite/FTS5-first memory;
- compact observations rather than raw transcript replay;
- persist decisions/results/failures/constraints/checkpoints with source provenance;
- cheap compact retrieval first, exact detail only on demand;
- privacy/redaction before persistence;
- no mandatory embedding model in v0.

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

## 4. WP2 validation

Frozen final comparison arms:
- A: WP1 baseline;
- B: Caveman packer/compression only;
- C: Caveman + Cavemem progressive retrieval.

Representative benchmark must cover context-heavy real LOOM/Pi evidence and negative small/no-op cases.

Promotion targets/gates include:
- objective task quality non-inferior to baseline;
- target >=20% median provider-input reduction on context-heavy cases;
- target <=5% provider-input overhead on small/no-op cases with no correctness regression;
- exact recovery and source verification;
- no accepted wrong result from stale/incorrect memory;
- packing/retrieval CPU overhead smaller than the saved prefill/E2E benefit;
- safe RAM/swap alongside S32;
- real Pi request through final combined path;
- simple disable/rollback to WP1 baseline.

If an individual compressor/retrieval idea is net-negative, revert/disable it and continue inside WP2. Do not stop for routine sub-NO_GO outcomes.

## 5. WP3 — Behavioral Transform — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Goal:
actual model/adapter-level behavioral transform with provenance, behavior evidence, capability preservation and runtime-loadable artifact.

Search/implementation priority:
1. Abliterix-derived MoE-aware methodology adapted to LOOM;
2. Heretic;
3. Senbonzakura-style multi-direction methods;
4. clean LOOM-native equivalent when upstream implementations are incompatible with the actual host/runtime.

Select by technical fit to canonical GGUF/llama.cpp/Apple Silicon. Prefer a small reversible/runtime-loadable adapter over a second full model copy when technically valid.

Prompt-only behavior does not count as WP3 completion.

## 6. WP4 — Final Integration + Acceptance

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Assemble best validated outputs from WP1-WP3.

Required:
- reliable clean startup;
- API/web/Pi all operational;
- S32 or later better validated runtime active;
- serving-path prompt/prefix cache active where directly verified;
- Caveman + Cavemem enabled only in validated net-positive form;
- behavioral-transform profile loaded/validated or exact physical/toolchain blocker documented;
- representative capability smoke tests;
- final performance/memory evidence;
- exact hashes/provenance;
- concise operational documentation.

## 7. Current research inputs

Use mechanisms selectively from:
- mini-SGLang — runtime concepts already informing WP1;
- Caveman + Cavemem for active WP2;
- Abliterix/Heretic/Senbonzakura concepts for later WP3.

Other repository papers remain research references, not current permanent integration requirements.
