# LOOM Qwen3.8 Portability Readiness 001 — Preregistration

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Before downloading very large Qwen3.8 weight payloads, determine whether LOOM can mechanically partition and execute the two target architectures on Apple M1/8GB with bounded resident memory and without an architectural blocker.

This checkpoint is **readiness only**. It does not claim model quality, production tok/s, or final winner.

Frozen candidates:

### Candidate A — Qwen3.8-27B
- upstream: `Qwen/Qwen3.8-27B`;
- reference MLX Q4 artifact: `mlx-community/Qwen3.8-27B-4bit`;
- published artifact size approximately `16.1 GB`;
- dense 27B target: all transformer-layer weights participate in each token.

### Candidate B — Qwen3.8-Flash-Next
- upstream: `Qwen/Qwen3.8-Flash-Next`;
- reference MLX Q4+MTP artifact: `Vontra/Qwen3.8-Flash-Next-MLX-4bit-MTP`;
- published artifact size approximately `113.209 GB / 105.434 GiB`;
- `qwen4_exp` architecture;
- 48 layers;
- 125B main-model parameters with 6B activated/token;
- 51B n-gram embedding;
- native 4B MTP block;
- 512 routed experts with 10 active + 1 shared expert per MoE layer.

External metadata is evidence to be mechanically revalidated during execution; no vendor speed claim is a LOOM result.

Final outcomes:
- `QWEN38_BOTH_PORTABLE`
- `QWEN38_FLASH_ONLY_PORTABLE`
- `QWEN38_27B_ONLY_PORTABLE`
- `QWEN38_NEITHER_PORTABLE`
- `QWEN38_READINESS_INCONCLUSIVE`

`PORTABLE` means a concrete LOOM partition/runtime contract exists whose bounded active working set fits the frozen M1/8GB safety envelope and whose tensor/architecture ABI has no unresolved hard blocker. It does NOT mean fast.

## Hard network/resource bound

Stage 0–4 may download only metadata/small configuration/index files.

- maximum network payload: `100 MiB` per candidate;
- no safetensors weight shard download;
- no model conversion/full artifact build;
- no deletion of existing LOOM artifacts;
- no package upgrade during this checkpoint.

If a required metadata file alone exceeds the cap, use Hub/API metadata or range-safe index access; do not download weight shards.

## Stage 0 — freeze source identity and local runtime capability

Record:
- current Git HEAD;
- macOS/Apple Silicon identity;
- installed Python, MLX, mlx-lm, mlx-vlm/oMLX versions if present;
- current free RAM/swap state and free disk;
- immutable upstream/reference artifact revisions where available;
- licenses for both candidates.

Fetch and retain only directly required small files/metadata such as:
- `config.json`;
- `model.safetensors.index.json` or equivalent tensor index metadata;
- tokenizer/config metadata only when needed for ABI determination;
- repository file-size inventory.

Persist hashes/ETags/revisions in evidence.

If source identity cannot be frozen, candidate = INCONCLUSIVE.

## Stage 1 — Candidate A dense-27B tensor/streaming contract

Mechanically derive from config/index:
- layer count and tensor inventory;
- quantized weight byte totals by layer and by non-layer/shared component;
- largest single layer/tensor working set;
- minimum resident state required for one-token decode excluding streamed layer weights;
- attention/KV/state geometry relevant to bounded decode;
- whether weights can be consumed layer-by-layer without requiring the full 16.1-GB payload resident;
- exact adapter responsibilities required to bind MLX tensors to a streamed-layer loader;
- predicted bytes read per output token under a no-cache layer-streaming implementation;
- storage bandwidth required for `1`, `2`, and `5 tok/s` from weight traffic alone.

Static portable gate for Candidate A requires all:
- tensor/index ABI fully resolved;
- one-layer + mandatory resident decode working set projected <= `5.5 GiB`;
- no framework requirement to materialize the complete dense model simultaneously;
- no required persistent weight cache above the resident bound;
- deterministic plan for layer identity → source range(s);
- no hidden remote/API dependency at runtime.

If PASS, classify Candidate A `PORTABLE_DENSE_STREAMING` and produce its consumer/producer contract. Do not download weights yet.

## Stage 2 — Candidate B Flash-Next architecture decomposition

Mechanically derive from config/index/repository metadata:
- exact layer types and MoE layout;
- routed expert tensor identities and quantized byte geometry;
- 512-expert coverage and top-10 + shared routing semantics;
- non-routed/shared-expert/backbone weight totals;
- n-gram table tensors, table size, lookup geometry, and whether lookup addresses are determinable before/while computing adjacent blocks;
- Gated DeltaNet recurrent/state tensors;
- Qwen Sparse Attention/indexer state;
- gated-residual working state;
- native MTP tensor/state footprint;
- largest single expert/shared-expert/backbone working set;
- minimum resident state for one-token text decode.

Produce separate proposed LOOM contracts for:
1. routed expert-major storage/resolver;
2. n-gram deterministic lookup/offload;
3. resident/shared/backbone/state partition;
4. optional native-MTP attachment (readiness only; MTP may be disabled in the later baseline).

Compute projected per-output-token external bytes for:
- routed top-10 experts;
- shared expert;
- n-gram lookup;
- any nonresident backbone component;
and bandwidth required for `1`, `2`, and `5 tok/s`.

Static portable gate for Candidate B requires all:
- `qwen4_exp` tensor/index ABI fully mapped or a bounded adapter gap explicitly identified with no missing mathematical semantics;
- one active expert/shared/backbone/state working set projected <= `5.5 GiB`;
- 512-expert identities can be addressed deterministically without loading the whole bank;
- n-gram lookup can be represented as bounded random/deterministic access rather than full-table residency;
- no requirement for the full ~113-GB artifact to reside in RAM;
- no hidden remote/API runtime dependency.

If PASS, classify Candidate B `PORTABLE_FLASH_STREAMING` and produce its contracts. Do not download weights yet.

## Stage 3 — integration-readiness mechanical checks

For each candidate that passed its architecture gate, create machine-readable JSON contracts containing at minimum:
- model/revision/artifact identity;
- tensor coverage required;
- layout/quantization metadata;
- layer/expert/n-gram identity ABI;
- projected resident and transient memory;
- projected external bytes/token;
- fallback policy = fail closed;
- runtime package/API requirements;
- exact unresolved implementation work, if any;
- artifact download size required for the later execution checkpoint.

Apply Integration Readiness Protocol v1 mechanically. No model forward.

## Stage 4 — prioritization for actual acquisition

If both candidates are portable, rank **download/execution order**, not final model quality, using:
1. probability of successful first text token on M1/8GB;
2. projected bytes/token and working-set margin;
3. acquisition size/time burden;
4. architectural fit with already proven LOOM mechanisms.

Do not use vendor tok/s benchmarks to declare a local winner.

Expected considerations that must be verified rather than assumed:
- dense 27B has small acquisition size but high full-layer bytes/token;
- Flash-Next has very large storage but sparse expert activation, deterministic n-gram offload opportunity, and native MTP.

## Decision

- both static gates PASS => `QWEN38_BOTH_PORTABLE`;
- only Flash PASS => `QWEN38_FLASH_ONLY_PORTABLE`;
- only dense 27B PASS => `QWEN38_27B_ONLY_PORTABLE`;
- both validly fail due hard architecture/memory requirements => `QWEN38_NEITHER_PORTABLE`;
- missing/ambiguous metadata or local API semantics prevents a valid decision => `QWEN38_READINESS_INCONCLUSIVE`.

## After this checkpoint

For each portable candidate, run a separate bounded acquisition + first-token/runtime checkpoint in the Stage-4 priority order.

Only after a candidate actually runs locally should it enter the final matched bake-off:
- sustained tok/s / TTFT;
- RAM/swap/disk;
- intelligence/quality on a frozen common LOOM set;
- instruction following/refusal/steerability profile;
- combined practical winner.

The canonical Qwen3-30B-A3B comparison baseline remains `1.229233 tok/s` production exact-Q4. The oracle K=4 `1.792925 tok/s` result is not a production baseline.

Evidence:
`results-local/research/qwen38-portability-readiness-001/<UTC>/`

Pi must not commit/push/edit project decision docs.