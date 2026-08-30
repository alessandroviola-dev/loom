# LOOM Behavioral Transform — WP3

Date: 2026-08-30
Status: **AUTHORIZED / ACTIVE**
Checkpoint: `LOOM_BEHAVIORAL_TRANSFORM_WP3`

## Goal

Produce the strongest technically valid **actual model/adapter-level behavioral transform** for canonical LOOM DEEP that can be created and validated on the reference Apple M1 8 GiB host, while preserving useful model capability, runtime stability, and the already validated WP1/WP2 product stack.

Prompt-only instructions, jailbreak prompts, system-prompt changes, or post-generation filtering do **not** satisfy WP3.

Preferred final artifact:
- a small reversible LoRA/adapter or equivalent transform;
- loadable by the canonical `llama-server` path;
- no second full 30B model copy unless unavoidable and explicitly justified by evidence.

WP3 is a macro work package. Pi should work autonomously through internal technical routes and must not return after routine sub-experiment GO/NO_GO outcomes. Record evidence, revert dead ends, and continue until WP3 is complete or a genuine user-action/physical/toolchain blocker is reached.

WP3 must not begin WP4.

## Canonical inherited stack

WP1: `LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`.

WP2: `LOOM_CONTEXT_INTELLIGENCE_WP2_GO`.

Canonical model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Canonical source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Canonical server binary SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Canonical runtime profile:
**S32**.

Validated S32 median decode:
`5.596 tok/s` on the matched WP1 A/B.

Operational server:
`http://127.0.0.1:18080`

Canonical Pi model label:
`loom-local/loom-deep-30b-s32`.

Canonical Context Intelligence:
Caveman + Cavemem through `.pi/extensions/loom-context.ts`.

WP3 must preserve a clean base/no-adapter rollback path and must not break the WP1/WP2 operational stack.

## Research basis and current external-method reality

### LOOM Heretic paper

Primary internal research artifact:
`LOOM_HERETIC_TECHNICAL_PAPER.md`.

Transferable concepts:
- contrastive residual-direction discovery;
- streamed residual means instead of storing all activations;
- FP32/FP64 geometric calculations over lower-precision model representation;
- reversible low-rank directional edits;
- norm-preserving transforms where useful;
- multi-objective behavior/preservation evaluation;
- architecture-aware component mapping;
- bounded hierarchical search rather than broad TPE first.

The internal paper explicitly warns that Heretic's bitsandbytes/NF4 path is not a portable Apple-Silicon requirement.

### Abliterix

Treat Abliterix as the first **methodology reference**, especially for:
- MoE-aware editing;
- expert-granular concepts;
- router/expert profiling concepts;
- projected/refined directions;
- stronger preservation-aware evaluation.

Do not assume the full upstream package is runnable on this host. Its documented production environment is Linux/CUDA and its large MoE reference runs require much larger GPU memory than the M1 8 GiB host.

### Heretic

Use as the established single-direction/low-rank baseline and as a source of validated conceptual patterns from the pinned LOOM technical paper.

### Senbonzakura

Use as the multi-direction/subspace fallback family when a single stable direction leaves substantial residual target behavior and the added complexity is evidence-justified.

Do not install/copy any upstream implementation wholesale merely to satisfy naming.

## License rule

Heretic, Abliterix and Senbonzakura are AGPL-family implementations/references.

Default WP3 policy:
- use mathematical ideas, public method descriptions and primary-paper concepts;
- prefer a clean LOOM-native implementation;
- do not copy substantial AGPL source/code structure into LOOM unless license compatibility is explicitly reviewed and accepted;
- preserve attribution/provenance for inspected external methods.

## Core technical strategy

The preferred end-to-end route is:

```text
frozen contrastive datasets
        |
canonical 30B inference / isolated analysis runtime
        |
streamed residual statistics
        |
stable behavior direction or low-dimensional subspace
        |
small low-rank directional delta
        |
GGUF-compatible LoRA/adapter artifact
        |
canonical llama-server --lora / adapter path
        |
frozen behavior + preservation + resource evaluation
```

The canonical quantized GGUF should remain the inference base.

Do not require a full BF16/FP16 30B resident copy on this host merely because upstream tools normally operate that way.

## Phase A — Method/representation audit

Before expensive model work:

1. verify branch/runtime/model/server provenance;
2. inspect current local disk headroom and available Python/PyTorch/MLX/llama.cpp tooling;
3. inspect the exact canonical Qwen MoE tensor topology relevant to attention output, routed/shared MLP projections, router and any supported LoRA tensor mapping;
4. inspect the pinned runtime's adapter/LoRA support and conversion tools;
5. inspect current upstream Abliterix, Heretic and Senbonzakura method descriptions/source only as needed to understand algorithmic options and architecture mapping;
6. freeze exact upstream commits/revisions used as research references;
7. decide the shortest technically valid analysis/edit representation for this host.

Preferred representation order:

1. **LOOM-native analysis over canonical GGUF / pinned llama.cpp path**, with minimal isolated instrumentation if required;
2. a compatible lightweight local source representation only for the specific tensors/residual statistics needed;
3. a smaller Qwen sibling only as a mechanical/mathematical smoke test, never as evidence that the final 30B transform works;
4. full upstream Transformers representation only if measured storage/RAM feasibility proves it can run locally without destabilizing the host.

Do not download another huge model representation before proving it is necessary and feasible.

## Phase B — Frozen behavioral/evaluation contract

Before final direction search or intervention tuning, freeze:

- target contrast set;
- reference/non-target contrast set;
- held-out target evaluation set;
- benign/capability preservation set;
- tokenizer/chat formatting;
- system prompt state;
- generation settings;
- seeds where applicable;
- objective scoring rules;
- resource metrics;
- dataset hashes/revisions.

Use local/offline evaluation after datasets are present.

The behavioral benchmark should measure the target alignment/refusal behavior without relying on a prompt-only bypass as the treatment.

Do not tune intervention parameters against the final held-out answers.

No remote LLM judge is required for WP3 GO. Prefer deterministic/local scoring plus bounded manual/structural checks. If a local judge is used, freeze it and treat it as an evaluation instrument, not ground truth.

## Phase C — Residual extraction and streaming parity

The first real technical gate inside WP3 is not final editing; it is trustworthy direction discovery.

Implement the smallest path that can obtain layer-aligned residual statistics for the canonical model or a mathematically equivalent representation.

Requirements:
- batch/stream residual accumulation;
- sensitive geometric accumulation in FP32/FP64;
- bounded memory;
- exact layer/component mapping;
- no need to retain the full prompt x layer x hidden tensor when a streamed mean is sufficient.

Where full-vs-streamed collection is mechanically possible on a bounded smoke slice, validate parity:
- direction cosine effectively 1 within numerical tolerance;
- bounded maximum absolute mean difference;
- repeated deterministic run produces stable direction;
- peak memory recorded.

If full collection is physically infeasible on 30B, validate streaming math on a bounded mechanically equivalent slice/sibling and separately validate 30B extraction provenance/shape before using 30B directions. Do not falsely claim 30B full-parity if it was not run.

## Phase D — Direction/subspace discovery

Start with the cheapest strong baseline:

1. mean-difference direction;
2. projected mean direction when it improves target/preservation separation;
3. per-layer vs one/few global mid-late directions;
4. attention output projection first unless architecture evidence supports another component.

Measure:
- norm;
- cross-run cosine stability;
- good/target separation;
- layer profile;
- bootstrap/subsample stability when affordable.

Only move to multi-direction/subspace methods if a single direction is stable but materially insufficient.

MoE-aware expert/router intervention is optional, not mandatory. Attempt it only if direct measurements show a plausible benefit over the simpler attention/output route.

## Phase E — Low-rank transform construction

Preferred first intervention:
- reversible directional low-rank edit;
- rank 1 first;
- small bounded layer envelope / strength;
- attention output projection first;
- norm-preserving variant if it materially improves preservation.

Construct the delta without rewriting the full base model whenever possible.

Preferred artifact route:
- PEFT-like LoRA tensors or directly generated equivalent;
- convert/write to a **GGUF LoRA adapter** compatible with the canonical model architecture;
- load as a separate adapter in `llama-server`.

The base GGUF must remain unmodified unless a later route proves adapter construction technically impossible and a separate explicit edit artifact is justified.

For quantized base tensors, dequantize only the specific tensor/block data required to compute the low-rank delta. Do not expand the entire 30B model to BF16/FP32 in memory.

## Phase F — Bounded method ladder

Pi should continue autonomously through these families as needed, retaining only evidence-backed candidates.

### Route 1 — LOOM-native single-direction adapter

Heretic-style/projected directional edit, low rank, small search.

This is the preferred first production candidate because it has the lowest implementation/resource burden.

### Route 2 — Abliterix-derived MoE-aware refinement

Only if Route 1 is insufficient and MoE-specific evidence indicates headroom.

Possible concepts:
- expert-granular targeting;
- router-aware selection;
- discriminative layer/component selection;
- refined/projected direction.

Do not port Abliterix's CUDA/vLLM stack.

### Route 3 — Senbonzakura-derived multi-direction/subspace

Only if single-direction editing leaves a repeatable residual target behavior and the added directions remain stable.

Bound the subspace dimension and search; do not start with a 200-trial wide search on M1 8 GiB.

### Route 4 — clean alternative

If all three families are mechanically incompatible but the measured representation data supports another simple low-rank directional method, a clean LOOM-native equivalent is allowed.

## Search/stopping rule

Do not use broad TPE as the first action.

Preferred progression:
1. deterministic/searchless baseline;
2. small strength/layer sweep;
3. bounded hierarchical refinement;
4. only then a small optimizer if evidence shows it is worth the extra runs.

Stop method escalation when:
- an adapter meets WP3 promotion gates; or
- three materially different, evidence-backed transform families fail to produce a better valid candidate; or
- a genuine physical/toolchain blocker makes all actual model-level transforms infeasible locally.

Routine candidate failure is not a reason to return early.

## Phase G — Adapter/runtime integration

A candidate is not complete until it runs through the canonical product path.

Requirements:
- adapter/artifact exact hash;
- canonical model remains unchanged;
- server can start/load with the adapter;
- adapter can be disabled without replacing the base model;
- health/API/WebUI remain operational;
- Pi can call the transformed model/profile locally;
- Context Intelligence still works or a measured compatibility issue is documented and repaired;
- no public network exposure.

Prefer one server configuration that can initialize the adapter and expose a stable transformed model/profile.

If the pinned runtime lacks required adapter support for the exact Qwen MoE tensor layout, an isolated provenance-controlled runtime patch/build is allowed, but the S32 base server remains the rollback until the patched path passes full acceptance.

## Phase H — Final WP3 evaluation

Compare at minimum:
- Base S32 + WP2;
- Best transformed S32 + WP2.

Use the same frozen generation/evaluation settings.

### Behavioral-change metrics

Record:
- hard/explicit refusal or target-behavior rate under the frozen target set;
- softer hedge/non-compliance metric if deterministically measurable;
- response degeneration/broken-output rate;
- representative qualitative samples as bounded evidence, without relying only on keyword counts.

### Capability preservation

Use a frozen representative local capability suite covering at least:
- factual/structured following;
- coding/reasoning or an existing LOOM practical subset;
- exact-output tasks;
- benign instruction following.

Record objective pass counts and any material regressions.

### Distribution/preservation proxy

Where technically available without prohibitive cost, measure one or more:
- first-token KL on benign prompts;
- short-sequence KL/logit divergence;
- perplexity delta;
- output agreement on frozen deterministic prompts.

No single KL metric is sufficient by itself.

### Resource/runtime

Record:
- adapter bytes;
- startup delta;
- median decode tok/s;
- prompt/prefill/E2E where comparable;
- peak RSS;
- swap;
- free-memory floor;
- crashes/OOM/corruption.

## WP3 promotion gates

### `LOOM_BEHAVIORAL_TRANSFORM_WP3_GO`

Use only if all are true:

1. an **actual model/adapter-level transform** exists;
2. exact base/model/runtime/adapter provenance is retained;
3. the artifact is reversible/disableable and the canonical base GGUF remains available;
4. final transformed profile loads through the local llama.cpp serving path;
5. frozen target-behavior evaluation shows a **material improvement** over base; target at least 50% relative reduction in the primary refusal/target-behavior rate when the baseline rate is large enough for that statistic to be meaningful;
6. no material increase in broken/degenerate output;
7. representative capability success is non-inferior within the frozen tolerance; no critical capability regression is accepted;
8. throughput remains practically usable; target >=90% of canonical S32 median decode unless a smaller loss is explicitly justified by a much stronger behavioral/capability Pareto result;
9. memory/swap remain safe on the 8 GiB host;
10. Pi can complete a real local request through the transformed profile;
11. adapter disable/rollback to canonical S32 succeeds;
12. complete durable evidence exists.

### `LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`

Use if valid bounded experiments show that available transform families do not produce a useful behavior/preservation/resource Pareto improvement.

### `LOOM_BEHAVIORAL_TRANSFORM_WP3_PHYSICAL_BLOCKED`

Use only if an actual model-level transform cannot be produced/evaluated because of a proven host/toolchain/representation constraint after the bounded method ladder is exhausted.

Do not relabel a prompt-only workaround as GO.

## Safety / host boundaries

Not authorized:
- disabling SIP or other host security mechanisms;
- destructive disk/system operations;
- deleting unrelated user data;
- exposing the service publicly;
- paid cloud/GPU services or new credentials;
- uploading private local datasets/conversations/models;
- replacing the canonical base model without keeping a rollback;
- uncontrolled multi-hundred-trial search;
- silently weakening frozen preservation gates after seeing results.

Project-local temporary environments/dependencies are allowed when necessary and recorded.

## Persistence policy

During WP3, Pi may modify local project code/artifacts and create `results-local/behavioral-transform-wp3/<timestamp>/` evidence.

Default: no commit/push during execution.

At WP3 completion, return the full bounded report. ChatGPT will review the result and may then explicitly authorize one macro-boundary persistence commit containing only reviewed WP3 source/config/result/benchmark files. Never commit model files, adapters if too large/unsuitable for repository policy, `.loom/`, `results-local/`, secrets, caches, home config or unrelated working-tree files.

## Final return required

Return one bounded report only when WP3 completes or reaches a genuine blocker. Include:

- classification;
- selected method family and why;
- external source revisions used as research references;
- exact direction/subspace construction;
- edited component/layer strategy;
- adapter/artifact format, size and SHA256;
- exact base model/runtime hashes;
- server load/start configuration;
- transformed profile/model id;
- behavior benchmark base vs transformed;
- capability preservation base vs transformed;
- KL/perplexity/logit/output-preservation metrics actually available;
- decode/prefill/E2E/RSS/swap delta;
- real Pi transformed-profile test;
- rollback test;
- changed project files;
- evidence roots;
- important failed/reverted routes;
- genuine remaining blocker if classification is not GO.

Do not begin WP4.
