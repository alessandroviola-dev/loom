# LOOM Behavioral Unlock — WP3-R2

Date: 2026-08-30
Status: **AUTHORIZED / ACTIVE**
Checkpoint: `LOOM_BEHAVIORAL_UNLOCK_WP3_R2`

## Why R2 exists

WP3 completed valid `LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`: real GGUF LoRA candidates were produced and loaded, but rank-1 directional, MoE-router and rank-4 subspace routes left the frozen held-out refusal result unchanged at `6/6`.

That result remains valid and must not be relabeled or erased. It only falsifies those bounded adapter families under the frozen WP3 experiment. It does **not** establish that Qwen3-30B-A3B-Instruct-2507 cannot be behaviorally unlocked.

WP3-R2 therefore tests materially different routes discovered after WP3:

1. an independently produced abliterated derivative of the **same upstream base model** already exists in GGUF, including Q3_K_S;
2. llama.cpp natively supports control vectors applied to per-layer activations and ships a GGUF control-vector generator, which is a different intervention class from the failed LoRA adapters;
3. related Qwen3-30B-A3B derivatives have published evidence that refusal suppression on this architecture can be substantial.

WP4 remains blocked until WP3-R2 completes.

## Canonical baseline preserved

Base model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Runtime:
S32 through the pinned Apple Metal MoE paging llama.cpp source.

Canonical server binary SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Canonical Pi model label:
`loom-local/loom-deep-30b-s32`

WP2 Caveman+Cavemem remains enabled by default and independently disableable.

Never overwrite/delete the canonical base GGUF or remove the S32/WP2 rollback path while R2 is in progress.

## External research inputs frozen at authorization

### Exact-base abliterated derivative

Upstream behavioral derivative:
`huihui-ai/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated`

The published card identifies base model:
`Qwen/Qwen3-30B-A3B-Instruct-2507`.

GGUF quantization source discovered:
`mradermacher/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated-GGUF`

Candidate file:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

Published size is approximately 13.3 GB and architecture is `qwen3moe`.

Treat all third-party artifacts as untrusted candidates until provenance, metadata, architecture, chat template, file integrity and behavior/capability are locally verified.

### Native llama.cpp control vectors

Current llama.cpp server/completion interfaces support:
- `--control-vector FNAME`;
- `--control-vector-scaled FNAME:SCALE,...`;
- `--control-vector-layer-range START END`.

Current llama.cpp also ships a `cvector-generator` that can generate control vectors directly from GGUF models using mean or PCA-style contrast reduction.

This acts on activations during inference and is not equivalent to the WP3 LoRA weight-edit candidates.

## Operating rule

This is a macro research package. Pi works autonomously through internal candidates and must not return after routine candidate failures.

Pi may:
- inspect current upstream cards/repositories and freeze exact revisions/URLs;
- download candidate model files after verifying free disk space and expected lineage;
- build the `cvector-generator` target from the already-pinned/provenance-controlled llama.cpp source or an isolated exact-revision source when required;
- run bounded base/candidate A/B evaluations;
- create temporary local configs and candidate launch scripts;
- generate small control-vector artifacts;
- test multiple bounded layer ranges/scales/methods when preregistered before final evaluation;
- stop/restart the local server cleanly;
- integrate a successful candidate with Pi/WP2 only after candidate promotion gates pass.

Pi must not:
- commit/push during R2 execution;
- expose the server publicly;
- delete/overwrite the canonical base model;
- silently replace the frozen behavior evaluation after seeing results;
- claim success from prompt-only/system-prompt manipulation;
- accept an external model solely because its card says `abliterated` or `uncensored`;
- start WP4.

## Phase A — freeze R2 evaluation and provenance

Before candidate inference:

1. preserve the original WP3 frozen held-out behavior evaluation unchanged;
2. preserve a representative capability/control set;
3. add a small benign decision-disposition/quality control set to detect obvious off-target behavioral drift;
4. freeze all criteria before reading candidate outputs;
5. create `results-local/behavioral-unlock-wp3-r2/<timestamp>/`;
6. record current canonical model/server/config hashes and health;
7. record available disk space.

The original WP3 held-out behavior gate must remain directly comparable. R2 may add new controls, but may not rewrite the old prompts/labels to manufacture success.

## Phase B — candidate A: exact-base external abliterated Q3_K_S

This is the highest-priority route because it is a full model-level edit of the exact upstream base rather than a small adapter approximation.

### Acquisition

Prefer the published Q3_K_S GGUF candidate above.

Before download/use:
- freeze repository/revision metadata;
- verify license and declared base lineage;
- record exact file name and remote metadata;
- verify sufficient disk space;
- download to a candidate/evidence-controlled local model location without altering the canonical base;
- compute local SHA256 and size;
- inspect GGUF metadata, architecture, tokenizer/chat-template metadata and tensor inventory;
- compare architecture/hyperparameters against canonical Qwen3-30B-A3B-Instruct-2507.

If the downloaded artifact has a mismatched architecture/base identity or broken template/metadata that cannot be cleanly corrected without changing semantics, reject it and continue.

### Runtime compatibility

Attempt to run the candidate through the same pinned Apple MoE paging runtime and as much of S32 as the artifact supports.

Do not assume that an external quant has identical performance characteristics to the canonical 3.25bpw file.

Measure:
- clean load/health;
- behavior gate;
- representative capability;
- decode throughput;
- prompt/prefill/E2E where practical;
- RSS/swap/free memory;
- WebUI/API compatibility;
- WP2/Pi compatibility after candidate behavior is proven.

### Candidate A promotion

Candidate A is behaviorally promising only if the original frozen held-out refusal result is materially lower than base. Target:
- >=50% relative reduction from the base `6/6` rate; and
- preferably <=1/6 refusal for a strong promotion candidate.

No accepted malformed/degenerate-response increase.

Capability must remain practically non-inferior on the frozen controls. Record any disposition/style drift; do not hide it.

Throughput/resource degradation is a product Pareto metric, not an automatic behavioral failure. Prefer >=80% of canonical S32 decode; lower may still remain a research candidate only if behavior improvement is strong and operation remains stable.

If Candidate A passes behavior and practical capability/resource gates, proceed directly to integration verification before spending time on control-vector search.

## Phase C — candidate B: native activation/control-vector steering

Execute only if Candidate A fails or has unacceptable Pareto cost, or as a bounded comparison after A if cheap.

Use llama.cpp native control-vector generation/application on the canonical GGUF.

### Key hypothesis

WP3 LoRA adapters may have failed because refusal behavior is re-derived during token generation rather than removed by a small static low-rank weight edit. A runtime control vector applied to activations across a layer range is a materially different causal intervention.

### Generation

Use frozen contrast examples disjoint from final held-out evaluation.

Test bounded, preregistered variants such as:
- mean reduction first;
- PCA only if mean is insufficient;
- early/middle/deeper layer ranges supported by the generator/runtime;
- a small set of signed scales around a neutral baseline.

Do not conduct an open-ended scale search against final held-out outputs.

All control-vector files must be hashed and reversible by simply omitting the server flag.

### Promotion

Apply the same frozen behavior/capability/resource criteria as Candidate A.

If a control vector materially improves behavior while preserving capability and stability, create a candidate profile with an explicit disable path and test Pi/WP2 through it.

## Phase D — evidence-backed external derivative fallback

If A and B fail, search current exact-/near-lineage Qwen3-30B-A3B-Instruct-2507 derivatives with published refusal/capability evidence.

Priority:
1. exact same upstream base;
2. same Qwen3-30B-A3B architecture with transparent weight-edit provenance;
3. only then compressed/pruned variants such as REAM-derived models.

Do not promote a model purely from its name/card. Every fallback must pass the local frozen R2 evaluation.

A related published example currently reports a Heretic-derived Qwen3-30B-A3B-Instruct-2507 REAM model at `2/100` refusals vs `100/100` for its own baseline. Treat that only as evidence that the architecture is alterable, not as proof that the model should be adopted.

## Phase E — external compute escalation boundary

If all local replacement/control-vector routes fail but evidence indicates that full-weight editing or behavioral fine-tuning is the remaining credible route, stop R2 as a genuine user-action blocker and report exactly:
- why local routes failed;
- what remote/full-precision procedure is justified;
- estimated hardware/storage/runtime class;
- whether a one-time external GPU run could produce a GGUF/adapter artifact reusable permanently on the Mac.

Do not purchase cloud compute, create paid accounts or require new credentials without returning to the user.

## R2 final classification

### `LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO`

Requires a local runtime profile that:
- is an actual model-level or activation-level intervention, not prompt-only;
- produces >=50% relative reduction on the original frozen `6/6` behavior baseline;
- passes frozen practical capability controls without material degeneration;
- has exact hashes/provenance;
- runs stably on the host;
- records throughput/RAM/swap impact;
- works through localhost API and one real Pi request with WP2 where applicable;
- has a clean rollback to canonical S32 + WP2.

### `LOOM_BEHAVIORAL_UNLOCK_WP3_R2_NO_GO`

All bounded local replacement/control-vector/external-derivative candidates fail to produce a useful behavior/capability/product Pareto result.

### `LOOM_BEHAVIORAL_UNLOCK_WP3_R2_EXTERNAL_COMPUTE_REQUIRED`

Local routes are exhausted, but evidence supports a specific full-weight/fine-tuning route that requires compute unavailable on this host.

## Required final report

Return only at R2 completion or genuine external-compute/user-action blocker with:
- classification;
- exact candidates tested;
- external repo/revision/file provenance;
- local SHA256/size for downloaded model/control-vector artifacts;
- base vs candidate original frozen behavior results;
- capability-control results;
- any off-target drift observed;
- decode/prefill/E2E/RSS/swap;
- server/API/Pi/WP2 integration result where candidate passes;
- selected candidate/profile if GO;
- exact rollback;
- failed/rejected candidate reasons;
- evidence root;
- changed local files/configs;
- recommendation for next action.

Do not commit or push. Do not start WP4.
