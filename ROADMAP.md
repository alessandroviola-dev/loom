# LOOM Roadmap

Last updated: 2026-08-23
Current checkpoint: `STREAMED_BLOCK_REUSE_AUDIT_001_COMPLETE`
Strategic next: `QWEN3_30B_A3B_EXTERNAL_EXPERT_FEASIBILITY_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Dense Qwen3-8B laboratory — RETAINED

Dense experiments established exact partial residency and several lifecycle rules:
- shared stages should stay resident;
- shared intermediate cleanup consolidation materially helps;
- streamed post-forward cleanup defer materially helps and is safe through four streamed layers;
- select-time GC removal is NO-GO;
- shared eval removal is not a useful axis.

Gradient002 under the promoted lifecycle:
- S0 11.101 tok/s / 90.078 ms
- S1 8.037 / 124.425 ms
- S2 6.546 / 152.775 ms
- S4 5.015 / 199.383 ms

Descriptive fit: `90.078 + 11.043*I(streaming) + 24.746*N` ms/token.

Dense research remains the controlled MLX implementation lab; it is no longer assumed to be the final 32B architecture.

## B — STREAMED-BLOCK-REUSE-AUDIT001 — COMPLETE

A weightless reusable Qwen3/quantized topology shell is mechanically possible with zero retained native parameter bytes, but the current strict MLX binding path requires existing parameter leaves. A construction-only one-factor A/B is therefore invalid without changing binding semantics.

Decision: close this micro-route on the present runtime.

## C — High-leverage architecture branch — ACTIVE

Research note: `research/architecture/high-leverage-architecture-exploration-001.md`.

### C1 — Sparse MoE / external experts — HIGHEST PRIORITY

Qwen3-30B-A3B directly matches the scale target: 30.5B total / ~3.3B active per token, 128 routed experts / 8 active.

Relevant systems: PowerInfer/PowerInfer-2, EdgeMoE, MoE-Infinity, Fiddler, KTransformers.

Core hypothesis: keep dense/shared backbone and hot experts resident; place cold experts lower in the hierarchy; predict/cache/prefetch only activated experts; consider moving activations to compute near resident expert data when cheaper than moving weights.

### C2 — Neuron/cluster-level conditional loading

Relevant: DejaVu, PowerInfer-2, `LLM in a Flash`.

Potential LOOM implication: whole transformer layers are too coarse as an I/O unit. Future storage may need expert/neuron-cluster layout, contiguous flash reads and activation-aware caching.

### C3 — Multi-token/block amortization

Relevant: Multi-token Prediction, Medusa, EAGLE, Lookahead Decoding.

Out-of-core implication: reduce full model/expert sweeps per accepted output token. Existing `OUTCORE-BLOCK` concept moves upward in strategic importance.

### C4 — Recursive/shared-weight architectures

Mixture-of-Recursions combines shared weights with adaptive recursive depth. This is a candidate if LOOM eventually trains/builds a new architecture rather than adapting conventional pretrained dense models.

### C5 — External learned memory

Memory Layers at Scale, RETRO and Memorizing Transformers suggest replacing some dense parametric memory with sparsely accessed external learned/retrieval memory.

### C6 — Recurrent/SSM resident core

Mamba/Mamba-2, Griffin/RecurrentGemma and RWKV can reduce state/KV costs and may be suitable cores for a sparse/external-memory LOOM architecture.

## D — QWEN3_30B_A3B_EXTERNAL_EXPERT_FEASIBILITY001 — NEXT

Do anatomy/traffic modeling before attempting inference:
1. exact dense/shared bytes;
2. expert bytes per layer;
3. active expert bytes/token;
4. expected quantized storage footprint;
5. naive NVMe bandwidth lower bound;
6. expert-routing temporal locality and cacheability;
7. feasible hot-expert cache sizes inside 8 GB;
8. route-prediction/prefetch opportunity;
9. whole-expert vs neuron-cluster I/O granularity.

The result should decide whether Qwen3-30B-A3B can become the first real ~30B LOOM target.

## E — If external-expert feasibility passes

1. capture real expert activation traces;
2. model hot/cold distribution and temporal locality;
3. design segmented expert cache;
4. predict/prefetch future expert sets;
5. evaluate contiguous flash representation;
6. combine with multi-token/block verification to amortize I/O;
7. measure real 30B capability/speed/memory.

## F — If existing MoE is insufficient

Begin model-system co-design research:
- sparse neuron clusters by construction;
- recursive/shared layer stacks;
- learned external memory;
- recurrent/SSM resident core;
- multi-token output heads;
- storage layout designed together with routing.

## G — Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Immediate order

1. `QWEN3_30B_A3B_EXTERNAL_EXPERT_FEASIBILITY_001`
2. expert activation trace/cache study if feasible
3. flash-aware external-expert execution
4. multi-token/block amortization
5. custom LOOM architecture research if necessary
6. capability validation
7. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
