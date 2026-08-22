# LOOM — Decensoring / Behavioral-Freedom Requirement v1

Status: FROZEN PROJECT REQUIREMENT
Date: 2026-08-22

## Requirement

Every LLM promoted as a LOOM-produced model/runtime must include a validated **decensored / behavioral-freedom profile** in addition to meeting LOOM's memory, speed and capability requirements.

This does **not** change the current memory-runtime research sequence. The active experiment remains `NORM_EVAL_BOUNDARY_001`; behavioral editing is a later promotion/release stage unless a future experiment explicitly studies it.

## Accepted implementation routes

A promoted LOOM model may satisfy this requirement through either:

1. the pinned Heretic approach/repository where its license and runtime are acceptable; or
2. a LOOM-native, independently implemented equivalent/clone based on the documented algorithms and primary literature.

Because the audited Heretic snapshot is AGPL-3.0-or-later, LOOM should prefer a clean independent implementation if repository/code licensing would conflict with LOOM's intended distribution model.

## Source research

Primary engineering note:
`LOOM_HERETIC_TECHNICAL_PAPER.md` / project source material

Audited upstream snapshot:
`p-e-w/heretic@bedb94ef117a271532ac2058447fbc165d5051bd`

The source analysis characterizes Heretic more generally as a contrastive residual-direction model-editing framework rather than merely a prompt jailbreak. Its reusable core is:

- estimate a behavioral direction from contrastive prompt populations;
- optionally project/orthogonalize that direction;
- edit selected output projections using reversible low-rank directional transforms;
- search intervention location/strength under multiple objectives;
- measure both target-behavior change and preservation of the original model.

## LOOM interpretation

For project purposes, "decensored" means that a promoted LOOM artifact has undergone an explicit model-behavior editing stage intended to reduce unwanted refusal/alignment behavior, rather than relying only on system prompts or inference-time jailbreak text.

The editing mechanism must remain separable from the inference/memory architecture so that LOOM can evaluate the same underlying runtime before and after the behavioral transform.

## Promotion gate

A LOOM model/runtime is not considered fully promoted/release-ready until all four axes are recorded:

1. **Memory** — fits the target constrained hardware/resource envelope.
2. **Speed** — meets the relevant usability target or is explicitly classified as experimental.
3. **Capability** — compared against the frozen practical capability baseline or the appropriate successor benchmark.
4. **Behavioral freedom / decensoring** — a validated behavioral-edit profile exists and its collateral capability drift is measured.

Decensoring alone is never a sufficient promotion criterion. A behavioral edit that materially damages capability, correctness, stability or the resource envelope must remain experimental.

## Required behavioral-edit evidence

When this phase begins, freeze at minimum:

- source model/revision and tokenizer revision;
- quantization/runtime/backend;
- behavior contrast datasets and exact revisions;
- residual extraction position and estimator;
- direction method and stability checks;
- target components/layers and low-rank transform details;
- behavior-change metric(s);
- preservation metric(s), including more than a keyword proxy where practical;
- memory and throughput delta versus the pre-edit model;
- exact seed/code/environment provenance.

The Heretic paper specifically warns that keyword refusal rate and first-token KL are useful inexpensive proxies but insufficient as sole final validation. LOOM should therefore retain its own capability benchmark and add stronger sequence/task preservation checks before promotion.

## Resource-oriented reuse

Heretic-derived concepts that are directly relevant to LOOM and may be researched later include:

- streaming residual means rather than retaining all activations;
- FP32/FP64 geometric analysis on top of lower-precision model storage;
- CPU offload of analysis outputs;
- reversible low-rank adapter state;
- compact layer-strength parameterization;
- architecture-aware editable-component mapping;
- multi-objective Pareto search;
- reproducibility bundles with model/dataset commits, seeds, environment and hashes.

These are research inputs, not changes to the current runtime benchmark path.

## Initial future sequence

When the memory/speed architecture reaches an appropriate checkpoint, the first Heretic-derived LOOM work should begin with analysis primitives rather than immediately editing model behavior:

1. `STREAMING_RESIDUAL_MEAN_PARITY`
2. direction reproducibility/stability
3. reversible low-rank transform parity
4. behavior-change vs capability-preservation A/B
5. resource-cost measurement of the behavioral transform
6. only then freeze a LOOM decensored profile for a promoted model

## Project rule

From this document onward, a final LOOM-produced LLM is defined not only by how large a model can run on small hardware, but by the combination:

**full parameter count / practical capability + constrained-memory execution + usable speed + validated decensored behavioral profile.**
