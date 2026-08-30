# LOOM Roadmap

Last updated: 2026-08-30
Current: WP1 Runtime + Product Serving GO and fully persisted. WP2 Context Intelligence GO and persisted. WP3 Behavioral Transform is now authorized and active.
Canonical context: `/AGENTS.md` v3.85.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
WP3 contract: `research/integration/loom-behavioral-transform-wp3.md`.

## 1. Canonical product state

- `loom-deep`: Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging **S32** through persistent localhost `llama-server`.
- canonical Pi model label: `loom-local/loom-deep-30b-s32`.
- S24 remains validated runtime rollback.
- Caveman + Cavemem Context Intelligence is enabled by default for the local Pi provider and can be disabled independently.
- `loom-balanced`: Qwen3-8B 3-bit ~13 tok/s remains lighter provisional tier.

## 2. WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Validated S24/S32 matched A/B:
- S24 median decode `4.382 tok/s`, E2E `29.185 s`;
- S32 median decode **5.596 tok/s**, E2E **23.849 s**;
- decode improvement `1.2768x`;
- byte-identical outputs.

Operational stack:
- embedded existing WebUI `http://127.0.0.1:18080/`;
- OpenAI-compatible API base `http://127.0.0.1:18080/v1`;
- localhost-only/offline;
- Pi verified against local server;
- serving-path stable-prefix reuse validated under `--cache-ram 512`;
- lifecycle helper `scripts/loom-deep-server` persisted in commit `75e210f4d46cb8b7955e46763e329f28f37b699e`.

Validated lifecycle script SHA256:
`616752d8bf3da44b5ab5244f429c03b6be7e30c917f6aa6e8651a03f6ed1d939`.

## 3. WP2 — Context Intelligence — COMPLETE / GO / PERSISTED

Classification:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`

Implementation commit:
`0e249f8f5cfaf89398d01e2ee50281fb75b86cd7`

Result:
`research/integration/loom-context-intelligence-wp2-result.md`

Evidence:
`results-local/context-intelligence-wp2/20260830T133259Z/`

Canonical Context Intelligence:
- Caveman deterministic context selection/compression/recovery;
- Cavemem SQLite/FTS5 progressive project memory;
- Pi `before_provider_request` bridge for `loom-local`;
- no extra LLM, embedding model, daemon or model-visible tool schema;
- reversible/fail-open integration.

Validated final comparison:
- A/B/C task success `6/7` each;
- combined heavy-context provider-input reduction **23.24%** median;
- no-op input overhead **0%**;
- exact recovery **6/6, 100% SHA-verified**;
- no accepted stale-memory error;
- real combined Pi task passed;
- server remained healthy.

## 4. WP3 — Behavioral Transform — ACTIVE

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Contract:
`research/integration/loom-behavioral-transform-wp3.md`

Goal:
produce and validate an actual model/adapter-level behavioral transform for the canonical 30B, with a reversible runtime-loadable artifact and no unacceptable capability/resource regression.

Prompt-only behavior does not count.

### Engineering strategy

Use external projects as method references rather than mandatory installed stacks.

Priority:
1. LOOM-native Heretic-style/projected single-direction low-rank adapter as the cheapest strong baseline;
2. Abliterix-derived MoE-aware refinement if measurements justify expert/router/layer-specific treatment;
3. Senbonzakura-derived multi-direction/subspace if single-direction editing is stably insufficient;
4. clean low-rank alternative only if required by representation/toolchain constraints.

The preferred final artifact is a small **GGUF LoRA adapter** loaded separately by `llama-server`, not a second full 30B copy.

Preferred path:

`frozen contrast/eval sets -> streamed residual statistics -> stable direction/subspace -> low-rank delta -> GGUF adapter -> canonical llama-server -> frozen base/transformed A/B`

### Resource strategy

- do not require a full BF16/FP16 30B resident representation if selected-tensor streaming can avoid it;
- use FP32/FP64 for sensitive geometric accumulation;
- dequantize only selected tensors/blocks needed to form the delta;
- start rank-1 / attention-output / small bounded layer-strength search;
- broad TPE is not the first action;
- only escalate to MoE-specific or multi-direction mechanisms when measured evidence supports it.

### Promotion targets

`LOOM_BEHAVIORAL_TRANSFORM_WP3_GO` requires:
- actual model/adapter transform;
- exact provenance and adapter hash;
- transformed profile loadable through canonical local serving;
- material frozen target-behavior improvement; target >=50% relative reduction when baseline rate supports it;
- no material degeneration/broken-output increase;
- representative capability non-inferior within frozen tolerance;
- target >=90% of canonical S32 decode unless a smaller loss is justified by a substantially stronger Pareto result;
- safe memory/swap;
- real Pi transformed-profile request;
- successful adapter disable/rollback;
- durable evidence.

`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO` = valid bounded transform routes fail to give a useful Pareto improvement.

`LOOM_BEHAVIORAL_TRANSFORM_WP3_PHYSICAL_BLOCKED` = proven physical/toolchain/representation barrier prevents all actual transforms after the bounded method ladder.

Do not stop for routine internal method failures.

## 5. WP4 — Final Integration + Acceptance — PLANNED / NOT AUTHORIZED

After WP3, assemble the best validated runtime + Context Intelligence + behavioral profile and run final end-to-end acceptance with exact hashes, capability/resource tests and documented operation.

## 6. Research inputs

- mini-SGLang concepts already informed WP1 runtime/cache work;
- Caveman + Cavemem are canonical WP2 mechanisms;
- internal Heretic technical paper + current Abliterix/Heretic/Senbonzakura research are WP3 references;
- llama.cpp separate GGUF LoRA loading is the preferred runtime representation for the WP3 transform.
