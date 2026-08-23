# LOOM — High-Leverage Architecture Exploration 001

Date: 2026-08-23
Status: exploratory research note; does not invalidate current dense-runtime evidence.

## Strategic observation

The dense-streaming program has produced real wins, but a 27B/32B dense model on 8 GB still faces a fundamental weight-movement wall. The highest-leverage literature changes the problem from "move all weights faster" to "avoid needing most weights for each token" or "amortize one weight sweep across multiple tokens".

## Priority directions

### 1. Sparse MoE + external expert hierarchy — highest priority

Qwen3-30B-A3B is directly aligned with the LOOM scale target: 30.5B total parameters but only 3.3B activated per token, 128 routed experts and 8 active experts. This makes total model capacity and per-token active capacity very different quantities.

Relevant systems/papers:
- Qwen3 / Qwen3-30B-A3B (2025)
- PowerInfer / PowerInfer-2 (arXiv:2312.12456, arXiv:2406.06282)
- EdgeMoE (arXiv:2308.14352)
- MoE-Infinity (arXiv:2401.14361)
- Fiddler (ICLR 2025, arXiv:2402.07033)
- KTransformers (SOSP 2025)

Core transferable ideas: keep dense/shared backbone hot; store cold experts lower in the hierarchy; predict expert activation; cache hot/temporally local experts; move activations to resident experts where cheaper than moving weights; overlap expert fetch and compute.

PowerInfer-2 is particularly important because it explicitly demonstrates model-system co-design for models larger than device memory and reports a 47B sparse model at 11.68 tok/s on a smartphone.

### 2. Neuron/cluster-level conditional weight access

Instead of treating a transformer layer or expert as the atomic I/O unit, PowerInfer-2 decomposes matrix operations into neuron clusters. PowerInfer and DejaVu exploit predictable contextual activation sparsity; Apple's `LLM in a Flash` similarly reduces flash traffic using activation sparsity, windowing and row-column bundling.

This suggests a LOOM-native storage format should eventually be organized around predicted active rows/neuron clusters, not only whole layers.

Key papers:
- LLM in a Flash (ACL 2024, arXiv:2312.11514)
- Deja Vu: Contextual Sparsity for Efficient LLMs (ICML 2023 / arXiv:2310.17157)
- PowerInfer / PowerInfer-2.

### 3. Multi-token / blockwise execution to amortize weight movement

Autoregressive decode is memory-bandwidth bound partly because a model-weight sweep is repeated for every emitted token. Multi-token prediction and Medusa-style multiple decoding heads reduce the number of full decoding steps. This is unusually relevant to out-of-core inference: if one external-weight sweep can validate or produce multiple positions, the effective bytes moved per accepted token can fall sharply.

Key papers:
- Better & Faster Large Language Models via Multi-token Prediction (ICML 2024, arXiv:2404.19737)
- Medusa (ICML 2024, arXiv:2401.10774)
- EAGLE (arXiv:2401.15077)
- Lookahead Decoding (arXiv:2402.02057)

This strengthens the existing LOOM `OUTCORE-BLOCK` idea and suggests it may deserve higher strategic priority once the sparse/expert path is characterized.

### 4. Recursive/shared-weight models

Mixture-of-Recursions (NeurIPS 2025, arXiv:2507.10524) reuses a shared stack across recursion steps and dynamically assigns depth to tokens. This attacks parameter memory and adaptive compute simultaneously. If LOOM is willing to build/train a new architecture rather than preserve conventional dense-transformer semantics, recursive parameter sharing is a serious candidate.

Caveat: published experiments are much smaller than 30B-class models, so this is architectural research rather than an immediate deployment route.

### 5. External trainable memory instead of storing all knowledge in dense weights

`Memory Layers at Scale` (arXiv:2412.09764) scales sparse trainable memory to 128B memory parameters without proportional FLOPs. RETRO (ICML 2022) and Memorizing Transformers show a related semi-parametric direction: use a smaller compute core plus large external memory/retrieval.

This is the most radical reinterpretation of the LOOM goal: not necessarily a 32B dense neural core, but a smaller resident reasoning core plus very large sparse external learned memory whose relevant entries are fetched on demand.

### 6. Recurrent / state-space backbone

Mamba, Mamba-2, Griffin/RecurrentGemma and RWKV reduce sequence-state/KV costs and can improve long-context inference efficiency. They do not by themselves solve the weight-bandwidth wall, but they are attractive as the resident core of a sparse-expert or external-memory architecture.

## Proposed LOOM synthesis

A high-leverage future LOOM architecture would combine:

1. small/medium always-resident dense or recurrent core;
2. large total sparse expert or memory capacity on SSD;
3. predictive routing before the expert is needed;
4. segmented hot-expert/neuron cache in unified memory;
5. contiguous neuron/expert storage optimized for NVMe reads;
6. overlap of fetch with preceding compute;
7. multi-token/block verification so one external-weight load serves several output positions;
8. capability and exactness gates identical in spirit to current LOOM contracts.

This is a model-system co-design problem, not merely an inference-engine optimization.

## Strategic recommendation

Do not abandon the dense Qwen3-8B research; it remains the controlled laboratory for lifecycle and MLX behavior. But create a parallel high-leverage track centered first on **Qwen3-30B-A3B external-expert feasibility**, because it already matches the desired ~30B total scale while activating only ~3.3B parameters per token.

The first step should be anatomy/traffic modeling, not attempting full inference: map shared vs routed bytes per layer, active expert bytes/token, theoretical NVMe bandwidth floor, possible expert temporal locality and the amount of unified memory required for a useful hot-expert cache.
