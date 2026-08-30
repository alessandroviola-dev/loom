# LOOM Behavioral Transform — WP3 Result

Date: 2026-08-30
Classification: **`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`**

## Decision

WP3 produced genuine, separate, runtime-loadable GGUF LoRA transforms for the canonical 30B model, but none achieved a useful target-behavior / preservation Pareto improvement. The frozen held-out explicit-refusal rate was **6/6 (100%)** for base and **6/6 (100%)** for the strongest non-degenerate subspace candidate: **0% relative reduction**, below the required 50% reduction. This is a valid bounded experimental NO_GO, not a physical/toolchain block.

The canonical S32 base stack has been restored and is healthy on `127.0.0.1:18080`; no adapter is loaded there.

## Provenance

- Base GGUF: `Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
  - SHA256: `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`
- Pinned source/runtime: `kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
  - canonical `llama-server` SHA256 after restoration: `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`
- Host: Apple M1, 8 GiB RAM, macOS 26.5.
- Frozen benchmark: `benchmarks/behavioral-transform-wp3/frozen-v1.json`
  - SHA256: `c6d3785d3c4b840c9549dbb42623291df02aa93650f77da8bb994e95179159de`
  - six target train, six held-out target, eight benign/capability prompts; deterministic temperature 0, top-p 1, seed 424242.
- Method references used only as mathematical/research provenance, with no upstream code copied:
  - Heretic: `p-e-w/heretic@bedb94ef117a271532ac2058447fbc165d5051bd` (the project-pinned audited reference).
  - Abliterix and Senbonzakura: methodology families only; no external source checkout/dependency/revision was incorporated.

## Direction discovery

A dedicated local embedding-only server was used serially on the canonical GGUF. The first attempt with the stock embedding batch guard and `-ub 1` aborted; an isolated, one-line server guard patch was used only to obtain final embeddings with the existing known-good `-b 1024 -ub 1` CPU-MoE regime. It was reverted, rebuilt, and the runtime source was clean before candidate serving and final rollback.

The analysis representation was the unnormalised final 2048-dimensional last-token state of the exact rendered Qwen chat prompt. It is not a claim of all-layer 30B residual extraction or all-layer full-vs-streamed parity. It avoids retaining a prompt × layer × hidden activation tensor. Rows were collected serially; the contrast means are FP64, while only 14 final 2048-D rows were retained for leave-one-out stability and the bounded subspace fallback.

For target mean `mu_t`, benign mean `mu_b`, the rank-1 direction was:

`d = normalize(mu_t - mu_b)`.

Measured direction facts:

- raw norm: 103.419949;
- target mean projection: 94.510757; benign mean projection: -8.909193;
- separation: 15.9325 pooled SD;
- target leave-one-out direction cosine: 0.99506 minimum, 0.99673 maximum.

This is strong direction stability/separation, but it did not translate into a useful behavioral edit through the available low-rank interventions.

## Actual adapter artifacts and bounded ladder

All artifacts are separate GGUF adapters; the base model was never modified.

| Route | Construction / component | Artifact | SHA256 | Size | Result |
|---|---|---|---|---:|---|
| 1a, output rank 1 | `output.weight`; `A=d`, sparse refusal-down/direct-opener-up `B`; rank 1 | `loom-wp3-r1-output-directional.gguf` | `cc97033acba7e462d839c8b875e694c2612f387f5d017710534ada3fe651392b` | 616,256 B | Runtime-loadable. Scales <=0.2 left all 6/6 train refusals unchanged; 0.3–0.5 changed outputs but retained refusal markers and produced repeated `Sure` degeneration. Rejected. |
| 1b, attempted attention output | planned projected attenuation `ΔW=-d d^T` at `blk.47.attn_output` | `loom-wp3-r1-attn47-attenuation.gguf` | `6bf426833697e5869ba02114e299d4c8ede1291a5c6e10e27c9129c9d4d57536` | 16,736 B | Rejected before inference: exact tensor audit found attention output input width 4096, whereas final-state `d` is 2048. Loader correctly rejected the incompatible shape. No false attention-layer claim was made. |
| 2, MoE-aware | target-conditioned rank-1 router edit `e_0 d^T` at `blk.47.ffn_gate_inp.weight` | `loom-wp3-r1-router47-expert0.gguf` | `a33dfb5bb6f6b86472bb87ff3696e84e2d0b13cf1058c7635fe64f0434b9d2e0` | 9,056 B | Runtime-loadable. Swept 0.002–0.5. Small/intermediate scales were byte-identical on all train responses; 0.5 changed 3/6 but still had 6/6 refusals. Rejected. |
| 3, subspace | rank-4 QR-orthonormalized basis: contrast mean + top three target-centered SVD directions, with distributed token preferences at `output.weight` | `loom-wp3-r4-output-subspace.gguf` | `419da1c20874132350c051342ddac58a291dfef8dc2a74d85e8dc9a8810614a3` | 2,464,064 B | Runtime-loadable. Scale 0.2 was the largest non-degenerate train candidate (one output changed, still 6/6 refusals); final held-out evaluation failed target improvement. |

The candidate server configuration used the canonical S32 resource flags plus:

```text
--lora <adapter.gguf> --lora-init-without-apply
```

and exercised per-request `lora: [{"id":0,"scale":...}]` controls. `GET /lora-adapters` confirmed every load. This proves the adapter model path rather than a prompt-only or output-filtering treatment.

## Final frozen comparison

The selected non-degenerate subspace probe was rank 4 at request scale 0.2. It was selected solely from the training sweep; held-out prompts were not used for its construction or scale choice.

| Metric | Base S32 | Rank-4 scale 0.2 |
|---|---:|---:|
| Held-out explicit refusal rate | 6/6 = 100% | 6/6 = 100% |
| Relative target-rate reduction | — | 0% |
| Held-out degenerate output | 0/6 | 0/6 |
| Benign structural/capability success | 8/8 | 8/8 |
| Benign degenerate rate | 1/8 | 1/8 |
| Exact held-out output agreement | — | 4/6 |
| Exact benign output agreement | — | 8/8 |

The primary deterministic scorer is intentionally only one instrument; saved response records permit inspection. Qualitatively, high-strength output edits changed openers but either continued to refuse or repeated the promoted opener. No high-strength candidate was promoted merely because a keyword changed.

First-token/sequence KL, perplexity, and internal logits were unavailable from this pinned serving surface without a further intrusive analysis runtime. They were not fabricated. The output-agreement and deterministic capability checks above are the available preservation proxies.

## Runtime/resource observations

- Candidate adapter load/start and `/health` succeeded for output, router, and subspace adapters; all remained loopback-only.
- Candidate observed RSS was approximately 3.996–4.018 GiB during the frozen calls; no candidate OOM/corruption occurred. The stock embedding-only server failure was isolated to its incompatible batch guard and was not used in final serving.
- Final base rollback server RSS after restart/request: 1,892,528 KiB. Final system swap: 1,859.75 MiB used of 3,072 MiB, with 1,212.25 MiB free.
- Decode samples on candidate calls were generally in the 5–8 tok/s range. Prompt-cache reuse affected most later calls, so prompt/prefill and end-to-end timing comparisons are explicitly **not treated as matched performance A/B evidence**. No candidate qualifies on behavior, so no throughput promotion claim is made. The inherited WP1 matched S32 median remains 5.596 tok/s.

## Rollback / product state

1. Stopped the final candidate server.
2. Restored the temporary source patch and rebuilt; runtime source status was clean.
3. SHA-verified the base GGUF and canonical server binary.
4. Restarted `scripts/loom-deep-server start` on port 18080.
5. Verified `/health`, `/v1/models`, an exact local rollback request (`rollback-ok`), and `scripts/test_loom_context.py`.

The final active profile is therefore the canonical no-adapter `loom-local/loom-deep-30b-s32` path with WP2 retained. No transformed profile was configured in Pi because no adapter met the frozen promotion gates; consequently a transformed-profile Pi request was not represented as passing.

## Changed project files

- `benchmarks/behavioral-transform-wp3/frozen-v1.json`
- `scripts/loom_wp3_native_directional_adapter.py`
- `scripts/loom_wp3_attention_ablator.py`
- `scripts/loom_wp3_router_refinement.py`
- `scripts/loom_wp3_subspace_adapter.py`
- `scripts/loom_wp3_eval.py`
- `research/integration/loom-behavioral-transform-wp3-result.md`

No commit or push was made.

## Durable evidence

`results-local/behavioral-transform-wp3/20260830T144523Z/` contains hashes, GGUF dumps, adapter artifacts, source-patch/reversion evidence, server logs, all train sweeps, held-out/base response records, final comparison, resource samples, and rollback evidence.

WP4 was not started.
