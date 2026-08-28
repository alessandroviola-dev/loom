# LOOM Qwen3.8 Next-Model Readiness 001 — Preregistration

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Determine, without blindly downloading hundreds of gigabytes or attempting unsafe full loads, whether LOOM can be ported from the frozen Qwen3-30B-A3B runtime to the two current Qwen3.8 candidates requested for the final same-hardware bake-off:

1. `Qwen3.8-27B` — dense/hybrid model;
2. `Qwen3.8-Flash-Next` — ultra-sparse MoE with N-gram embedding and native MTP.

This checkpoint is architecture/readiness and artifact-selection only. It does not make intelligence, final speed, or steerability claims.

Frozen comparison reference:
- Qwen3-30B-A3B exact-Q4 production baseline commit `96958de`;
- sustained median `1.229233 tok/s`;
- oracle K=4 verifier ceiling `1.792925 tok/s` is an upper-bound diagnostic only and NOT production speed.

Final outcomes:
- `QWEN38_BOTH_READY_FOR_LOOM_ADAPTATION`
- `QWEN38_27B_READY_ONLY`
- `QWEN38_FLASH_READY_ONLY`
- `QWEN38_NEITHER_READY`
- `QWEN38_READINESS_INCONCLUSIVE`

## External candidate identities to verify and pin

The run must mechanically verify current immutable revisions, license, architecture config, file inventory and provenance before any large transfer.

### Dense candidate

Preferred practical source candidate:
`mlx-community/Qwen3.8-27B-4bit`

Expected order-of-magnitude artifact size from current public metadata: ~16.1 GB.
Base model must resolve to `Qwen/Qwen3.8-27B`.

Also inspect metadata only for the matching native-MTP artifact if present, including `mlx-community/Qwen3.8-27B-MTP-4bit` or the MTP tensors embedded in the chosen checkpoint. Do not assume MTP compatibility from filename alone.

### Flash candidate

Upstream identity:
`Qwen/Qwen3.8-Flash-Next`.

Do NOT download the ~360 GB upstream BF16 checkpoint in this readiness checkpoint.

Preferred practical Q4-class candidate for provenance/readiness inspection:
`Vontra/Qwen3.8-Flash-Next-MLX-oQ4-MTP`

It is eligible for later adaptation only if metadata proves:
- base model is the official Flash-Next checkpoint;
- quantization provenance is explicit;
- native MTP is preserved;
- qwen4_exp tensor/config inventory is self-consistent;
- no hidden architecture substitution;
- license terms are retained.

The smaller mixed-Q2 community checkpoint may be inspected as metadata-only fallback evidence but MUST NOT become the intelligence bake-off artifact in this checkpoint because its lower precision would confound architecture/model-quality comparison.

## Stage 0 — local readiness and transfer guard

No model download initially.

Record:
- macOS / Apple M1 / physical RAM;
- installed MLX, mlx-lm, mlx-vlm versions;
- free disk on the project volume;
- current accepted LOOM artifact roots;
- whether local runtime code has native model definitions for `qwen3_5` / Qwen3.8-27B and `qwen4_exp` / Flash-Next;
- whether MTP interfaces exist for either architecture;
- whether safetensor metadata/index can be inspected without full model loading.

Hard transfer rule:
- no transfer >2 GiB until Stage 1/2 metadata contracts PASS;
- no full model forward in this checkpoint;
- no process may intentionally load a >8GB candidate fully into unified memory.

## Stage 1 — Qwen3.8-27B architecture/artifact contract

Using remote metadata/config/index and at most <=2 GiB bounded metadata/header transfer before authorization, freeze:
- immutable source revision;
- tokenizer identity/vocabulary;
- layer count;
- hidden/intermediate dimensions;
- attention/Gated-DeltaNet block pattern;
- dense FFN tensor inventory;
- quantization scheme/group size of the practical 4-bit artifact;
- total text-model bytes;
- vision-only bytes separable from text path;
- native MTP existence, dimensions, artifact location and tokenizer compatibility;
- non-weight runtime state/KV requirements relevant to 8GB.

Then derive a LOOM streaming contract without running the model:
- exact tensors required for one layer/token;
- which weights could remain resident under a conservative runtime budget;
- which weights must stream;
- lower bound and projected bytes read per verifier token for sequential decode;
- projected bytes/output-token for MTP chunk widths K=2 and K=4 assuming perfect acceptance and one weight load reused across chunk positions;
- feasibility of one-layer-at-a-time execution without persistent dense-model residency.

Readiness PASS requires all:
- text-only tensor graph can be enumerated deterministically;
- every required tensor maps to a source offset/file;
- no architectural component requires the entire 27B checkpoint resident simultaneously;
- the resident core/KV/scratch budget has a plausible <=8GB implementation envelope;
- streaming contract is explicit and fail-closed;
- MTP, if proposed as a later speed mechanism, is provenance-compatible with the selected model.

Only after PASS may Pi download the selected `mlx-community/Qwen3.8-27B-4bit` artifact, and only if free disk >= artifact size +25% +10 GiB scratch. Download must be resumable. No model forward yet.

After download, verify file hashes/index/tensor inventory against the frozen contract. Do not convert or execute.

## Stage 2 — Qwen3.8-Flash-Next architecture/artifact contract

Before any large Flash transfer, use upstream/practical-artifact metadata to freeze:
- immutable official base revision;
- qwen4_exp architecture identity;
- layer count;
- 512-expert or actual routed-expert geometry from config, not assumptions;
- active experts/token and shared-expert semantics;
- expert tensor shapes/quantization;
- routed expert-bank bytes;
- resident non-routed bytes;
- N-gram embedding table geometry, lookup semantics, precision and bytes;
- whether N-gram addresses are deterministic before the corresponding main-model compute and therefore prefetch/offload-compatible;
- MTP block inventory/dimensions and runtime support;
- GDN/QSA state requirements;
- text-only versus vision-only separability.

Derive a LOOM-specific physical contract:
1. expert bank remains external and addressable by `(layer, expert)` or the architecture's exact equivalent;
2. N-gram table remains external unless a smaller resident representation is proven;
3. only required expert/N-gram slices are loaded per step;
4. non-routed backbone + GDN/QSA state + KV/scratch must fit a plausible 8GB runtime envelope;
5. MTP verification can in principle reuse one loaded expert across multiple chunk positions only when routing identities coincide, preserving mathematical order.

Compute projected bytes/output-token for:
- sequential decode;
- ideal K=2 MTP verification;
- ideal K=4 MTP verification;
using exact config/tensor byte counts from the selected practical artifact.

Flash readiness PASS requires deterministic coverage of all runtime tensor categories, explicit offload contracts for the expert bank and N-gram table, no requirement for full-checkpoint residency, and a plausible resident-core budget.

Do NOT download the preferred ~100+ GiB Flash practical artifact during this readiness checkpoint unless ALL Flash readiness checks PASS and free disk >= artifact size +25% +20 GiB scratch. Even after PASS, the default action for this checkpoint is metadata-only; report the exact transfer size and wait for the next adaptation checkpoint to authorize the full transfer.

## Stage 3 — prioritize adaptation order

No vendor benchmark may decide the winner.

Rank which model should be adapted first based only on measured/static local feasibility:
1. lowest projected resident memory risk;
2. lowest projected verifier bytes/output-token under its native architecture/MTP;
3. smallest transfer/build cost;
4. strongest deterministic compatibility with existing LOOM expert-major/runtime abstractions.

This ranking selects execution order only, not final model quality.

Output an exact next checkpoint recommendation:
- `QWEN38_27B_LOOM_ADAPTATION_001`, or
- `QWEN38_FLASH_NEXT_LOOM_ADAPTATION_001`.

Both candidates that pass readiness remain scheduled for later adaptation and final bake-off.

## Final bake-off contract — frozen now, executed later

Once both feasible candidates have working local runtimes, compare all three practical local models under matched text-only conditions:

1. Qwen3-30B-A3B LOOM baseline;
2. Qwen3.8-27B LOOM runtime;
3. Qwen3.8-Flash-Next LOOM runtime.

Required dimensions:
- sustained generation tok/s and TTFT;
- RAM, swap and disk footprint;
- fixed local quality/intelligence suite spanning reasoning, math, coding, debugging, knowledge, Italian instruction following and structured output;
- refusal/steerability profile under identical benign and policy-boundary prompts.

Do not mix base-model intelligence comparison with separately modified/abliterated/uncensored derivatives. If the user later wants the least refusal-prone derivative, test that as a separate post-bake-off controllability track so model quality and alignment modifications are not conflated.

## Hard bounds / efficiency

- no full upstream BF16 Flash download;
- no blind >2 GiB transfer before candidate metadata/readiness PASS;
- no full candidate forward in this checkpoint;
- no model conversion/requantization yet;
- no benchmark-quality conclusion from vendor/community claims;
- no broad unrelated repo reread;
- use deterministic config/index/header scripts and JSON;
- pin immutable revisions and hashes;
- downloads, if authorized by a PASS gate, must be resumable;
- Pi must not commit/push/edit AGENTS/HANDOFF/ROADMAP/project decision docs.

Evidence:
`results-local/research/qwen38-next-model-readiness-001/<UTC>/`
