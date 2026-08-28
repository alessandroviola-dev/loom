# LOOM Qwen3.8-27B Dense Streaming First-Token 001 — Preregistration

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Determine whether the statically portable `Qwen3.8-27B` Q4 reference can actually produce correct deterministic local text on Apple M1/8GB through a bounded LOOM dense layer-streaming runtime, and measure enough decode performance to decide whether a full bake-off benchmark is justified.

This checkpoint prioritizes first-token correctness and early performance elimination. It must not spend a full 3×32-token campaign on a candidate that is already clearly slower than the accepted Qwen3-30B-A3B baseline.

Candidate:
`mlx-community/Qwen3.8-27B-4bit@3e6447f082e89cc7f0bc6e5441afd38dfce760ff`

Upstream architecture identity:
`Qwen/Qwen3.8-27B@1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`

Comparison baseline:
Qwen3-30B-A3B exact-Q4 LOOM runtime, commit `96958de`, sustained median `1.229233 tok/s`.

Final classifications:
- `QWEN38_27B_DENSE_COMPETITIVE`
- `QWEN38_27B_DENSE_WORKS_SLOW`
- `QWEN38_27B_DENSE_FIRST_TOKEN_ONLY`
- `QWEN38_27B_DENSE_INCONCLUSIVE`

## Stage 0 — execution-environment reconciliation

Before any large download, mechanically locate the exact Python/interpreter environment used by the accepted Qwen3-30B-A3B LOOM runs.

The prior metadata-readiness probe reported MLX-family packages absent, which conflicts with accepted evidence using MLX `0.32.0` and mlx-lm `0.31.3`.

Required:
- inspect retained evidence/scripts/shebangs/venv metadata and shell history only as needed;
- identify the interpreter used by accepted LOOM model-forward runs;
- record Python path/version and installed `mlx`, `mlx-lm`, `mlx-vlm`, `huggingface_hub`, `safetensors` versions;
- prove a minimal local MLX array/eval and existing canonical Q4 expert load operation with no network;
- do not install/upgrade packages if a previously validated environment is available.

If the validated environment cannot be recovered, a new isolated environment may be created only with versions pinned to the accepted stack where available. Record the exact environment delta before model acquisition. Do not upgrade the project globally.

If no working MLX execution environment can be established deterministically: `QWEN38_27B_DENSE_INCONCLUSIVE` and STOP before weight download.

## Stage 1 — storage + acquisition gate

Acquire only the fixed Candidate-A Q4 revision.

Preferred storage:
- use the LOOM external root when available and healthy;
- do not consume local system disk down to an unsafe margin;
- do not delete accepted LOOM artifacts.

Before download record:
- target payload size from fixed index;
- destination filesystem free bytes;
- required free space = payload + 25% + 2 GiB scratch;
- filesystem health/writability.

Acquisition requirements:
- resumable snapshot download;
- fixed revision only;
- include all required model Q4 safetensors/config/tokenizer files;
- no upstream BF16/FP16 weights;
- network cap: 20 GiB total for this checkpoint;
- verify all indexed shards present and their exact sizes/digests where repository metadata permits;
- preserve a machine-readable local artifact manifest.

If disk/network gate cannot be satisfied without deleting accepted artifacts: `QWEN38_27B_DENSE_INCONCLUSIVE` and STOP.

## Stage 2 — static adapter compile/dry-run

Implement only the minimum Qwen3.8/Qwen3.5-family dense streaming adapter needed for this candidate.

Frozen semantics:
- language model only for this checkpoint; vision tower must not be required for text-only generation;
- 64 language layers in exact model order;
- 48 Gated DeltaNet linear-attention layers and 16 full-attention layers according to config;
- Q4 tensors read from fixed safetensor ranges;
- one layer's large weight payload logically live at a time, plus bounded state;
- mandatory embeddings/output/state may remain resident within the preregistered memory envelope;
- no hidden full-model load;
- no weight cache spanning multiple full layers;
- no remote inference/fallback.

Mechanically prove before full forward:
- every required text-language tensor maps exactly once;
- deterministic layer -> shard/range mapping;
- no unresolved/ambiguous tensor identities;
- quantization metadata understood by local MLX API;
- projected resident + largest transient layer <=5.5 GiB;
- all 64 layers can be instantiated/executed in a synthetic/static dry-run without retaining prior layer weight payloads.

Any deterministic adapter/artifact defect must fail closed before full forward.

## Stage 3 — representative component parity

Before full 64-layer forward, test representative layers:
- one early Gated DeltaNet layer;
- one middle Gated DeltaNet layer;
- one full-attention layer;
- one late layer.

For each:
- load from the fixed Q4 artifact;
- execute the layer with deterministic synthetic or retained hidden-state input;
- compare streamed execution with the same layer loaded through the most direct available local reference API from the same weights;
- require output shape/dtype/finite values and numerical parity within the API's deterministic quantized tolerance;
- prove state/KV update shapes and bounded lifetime;
- zero hidden remote fallback.

If representative layer semantics cannot be established: `QWEN38_27B_DENSE_INCONCLUSIVE` and STOP.

## Stage 4 — first full text token

Run a deterministic short text prompt through the complete 64-layer text model using dense layer streaming.

Requirements:
- deterministic tokenizer/chat template from the fixed artifact;
- text-only path;
- prefill then one greedy decode token;
- finite logits;
- deterministic repeated token ID/logit digest on one immediate rerun;
- all 64 layers executed in order;
- state/KV mechanics valid;
- no full-model residency;
- zero remote/SOURCE fallback;
- no persistent multi-layer weight cache;
- peak RSS <=6.5 GiB;
- swap delta <=512 MiB and no unsafe pressure.

Record first-token/prefill wall, single decode-token wall, bytes read, peak RSS/swap and output token.

If a correct deterministic first token cannot be produced: `QWEN38_27B_DENSE_INCONCLUSIVE` and STOP.

## Stage 5 — bounded autoregressive speed probe

Normal autoregressive decode only. Native MTP is NOT enabled in this checkpoint.

Reason: establish the candidate's ordinary production verifier/decode cost separately before testing an additional multi-token mechanism.

Run one fresh process:
- same deterministic prompt;
- prefill;
- one unmeasured warmup decode token;
- exactly 4 measured greedy output tokens.

Record:
- tok/s;
- each token wall;
- bytes read/output-token;
- I/O, layer compute/materialization/state overhead where measurable;
- peak RSS/swap/safety;
- deterministic output-token IDs.

Frozen early-stop rule:
- if 4-token throughput `<0.50 × 1.229233 = 0.6146165 tok/s`, classify `QWEN38_27B_DENSE_WORKS_SLOW` and STOP. No longer benchmark is justified.
- if throughput is `>=0.6146165` but `<0.90 × 1.229233 = 1.1063097 tok/s`, proceed to Stage 6 with only 3×8-token confirmation;
- if throughput `>=1.1063097 tok/s`, proceed to Stage 6 with 3×16-token confirmation.

These gates are decision-efficiency thresholds, not model-quality claims.

## Stage 6 — confirmation only if justified

If Stage 5 >=0.6146165 tok/s, run exactly 3 fresh-process repetitions using the frozen length selected above:
- prefill;
- one warmup;
- 8 or 16 measured greedy output tokens according to Stage 5 gate.

Record per repetition:
- tok/s;
- p50/p95 token wall;
- bytes/token;
- peak RSS/swap/safety;
- deterministic output sequence.

Decision statistic: median tok/s.

Classification:
- `QWEN38_27B_DENSE_COMPETITIVE` iff median >= `1.1063097 tok/s` (within 10% of current LOOM 30B baseline) with all validity/safety gates PASS;
- `QWEN38_27B_DENSE_WORKS_SLOW` iff deterministic local generation works but median is below `1.1063097 tok/s` or Stage-5 early stop fires;
- `QWEN38_27B_DENSE_FIRST_TOKEN_ONLY` iff Stage 4 works but a valid sustained decode measurement cannot be completed for resource reasons;
- `QWEN38_27B_DENSE_INCONCLUSIVE` only for genuine unresolved runtime/API/artifact ambiguity.

## MTP handling

The official Qwen3.8-27B architecture is trained with multi-step MTP. This checkpoint does NOT enable MTP.

If normal streaming generation works, record only static presence/footprint/ABI of any MTP tensors found in the fixed Q4 artifact. A later independent checkpoint may test native MTP/chunk verification if and only if baseline results justify it.

## Hard bounds

- fixed candidate/revision only;
- <=20 GiB network;
- no BF16/FP16 alternative model download;
- no Flash-Next download;
- no model-quality/quantization search;
- no routing sparsity;
- no DFlash;
- no speculative drafter;
- no full-model persistent RAM load;
- no broad repository reread;
- deterministic compatibility checks before full forward;
- Pi may create local adapter/runner files and evidence but must not commit/push/edit AGENTS/HANDOFF/ROADMAP/project decision docs.

Evidence:
`results-local/research/qwen38-27b-dense-streaming-first-token-001/<UTC>/`

## After this checkpoint

Candidate A is not declared the bake-off winner or loser on intelligence here. This checkpoint establishes only local execution correctness, memory safety and practical baseline decode speed.

After A is classified, proceed to the separately designed Flash-Next acquisition/adaptation checkpoint. Only after both have real local generation should the final three-model speed/intelligence/steerability bake-off run.
