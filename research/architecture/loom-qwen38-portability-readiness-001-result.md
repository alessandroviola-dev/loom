# LOOM Qwen3.8 Portability Readiness 001 — Result

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Final classification: `QWEN38_BOTH_PORTABLE`

## Scope

Metadata-only static feasibility for adapting LOOM to two newer Qwen3.8 candidates. No safetensor payloads were downloaded and no model forward was executed.

## Frozen sources

Candidate A — dense:
- upstream `Qwen/Qwen3.8-27B@1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`;
- Q4 reference `mlx-community/Qwen3.8-27B-4bit@3e6447f082e89cc7f0bc6e5441afd38dfce760ff`.

Candidate B — Flash-Next:
- upstream `Qwen/Qwen3.8-Flash-Next@de4b8e4d43b917e7706784d8bb445c9af86a3540`;
- Q4+MTP reference `Vontra/Qwen3.8-Flash-Next-MLX-4bit-MTP@327c8a604de613b42f84ba5e6b796c0931e8aa3b`.

## Local environment observation

Host: Apple M1 / 8 GiB.
Readiness probe reported MLX/mlx-lm/mlx-vlm/oMLX absent in the probed interpreter and about 31 GiB local disk free.

This conflicts with the previously validated LOOM execution environment that used MLX 0.32.0 / mlx-lm 0.31.3. Therefore the next execution checkpoint must mechanically locate and freeze the exact Python environment used by accepted LOOM runs before any large download. Do not install/upgrade blindly.

## Candidate A — Qwen3.8-27B

Classification: `PORTABLE_DENSE_STREAMING`.

Static facts:
- 64 language layers: 48 linear-attention + 16 full-attention;
- largest layer `215,665,088 B`;
- projected mandatory resident bytes `1,587,312,640 B`;
- projected external weight traffic `13,702,468,608 B/output-token` for naive one-token layer streaming;
- required storage bandwidth at 1/2/5 tok/s: `13.702 / 27.405 / 68.512 GB/s`.

PORTABLE gate passed because the tensor/index ABI is resolved, largest layer plus resident state fits the frozen working-set envelope, deterministic layer-to-source mapping exists, and full model residency is not required.

Remaining work:
- freeze the validated MLX execution environment;
- implement isolated Qwen3.5-family streamed-layer adapter;
- prove Q4 quantized layer execution locally;
- static 64-layer dry-run;
- acquire the fixed Q4 checkpoint on storage with sufficient scratch margin.

Interpretation: A is simpler and cheaper to acquire, but the projected one-token dense streaming bandwidth is much worse than the current Qwen3-30B-A3B expert-major path. Portability does not imply competitive speed.

## Candidate B — Qwen3.8-Flash-Next

Classification: `PORTABLE_FLASH_STREAMING`.

Static facts:
- 48 layers;
- 512 routed experts/layer; top-10 routed + one shared expert;
- routed expert size `3,072,000 B`;
- routed expert traffic `1,474,560,000 B/output-token`;
- shared-expert traffic `147,532,800 B/output-token`;
- bounded N-gram lookup traffic `1,600 B/output-token` for the frozen lookup interpretation;
- projected resident bytes `991,928,320 B`;
- projected transient bytes `154,032,152 B`;
- projected total external bytes `3,858,155,864 B/output-token`;
- required storage bandwidth at 1/2/5 tok/s: `3.858 / 7.716 / 19.291 GB/s`;
- MTP metadata ABI: 76 tensors covered; local runtime integration not yet ready, so baseline readiness is MTP-disabled.

PORTABLE gate passed because qwen4_exp is mechanically mappable with bounded adapter work, 512-expert addressing is deterministic, the N-gram table can be represented as bounded deterministic offload rather than mandatory full RAM residency, and projected resident/transient state fits the working-set envelope.

Remaining work:
- Qwen4Exp bounded-state adapter;
- exact local N-gram hash/partition implementation;
- static dry-run;
- compatible runtime path;
- native MTP integration after baseline correctness;
- weight acquisition on external storage: current local disk is insufficient for the measured `105.434 GiB` payload.

Interpretation: B is harder to integrate and far larger on disk, but its sparse structure, deterministic N-gram offload and native MTP make it architecturally more aligned with LOOM than the dense 27B.

## Priority

Execution/download priority from the preregistered readiness ranking: A first, B second.

Reason: A has the highest probability of reaching a first correct local token with the smallest acquisition and adapter effort. This priority is for experimental efficiency, not a prediction that A will win on throughput.

## Contracts

Evidence contracts:
- `results-local/research/qwen38-portability-readiness-001/20260828T112000Z/contract_candidate_A.json`;
- `.../contract_candidate_B_expert_major.json`;
- `.../contract_candidate_B_ngram_offload.json`;
- `.../contract_candidate_B_resident_state.json`;
- `.../contract_candidate_B_native_mtp.json`.

Total network bytes consumed: `2,024,970 B` (A `736,072`; B `1,288,898`); safetensor payload bytes `0`.

Evidence:
`results-local/research/qwen38-portability-readiness-001/20260828T112000Z/`.

## Decision

Both candidates are statically portable to LOOM under an 8-GiB working-set discipline.

Next: execute a bounded actual-acquisition / first-token / speed feasibility funnel for Candidate A. Stop early if measured dense streaming is clearly noncompetitive. Candidate B remains queued for a separate external-storage Qwen4Exp/N-gram/MTP adaptation checkpoint.
