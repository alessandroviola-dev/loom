# LOOM Behavioral Unlock — WP3-R2 Result

Date: 2026-08-30
Classification: **`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO`**

## Decision

Candidate A, a separately downloaded full-weight abliterated GGUF derived from the exact declared Qwen3-30B-A3B-Instruct-2507 base, passes the frozen R2 behavior gate. It reduced the unchanged WP3 held-out deterministic explicit-refusal result from **6/6** to **0/6** (100% relative reduction), with no held-out degenerate responses and no regression on the eight frozen benign capability checks. This is a model-level replacement, not a prompt treatment or a WP3 LoRA edit.

The candidate is materially slower and has high swap pressure on the 8 GiB M1, but was stable through local llama-server, WebUI, OpenAI-compatible localhost API, and a real Pi request with the WP2 extension enabled. The behavior improvement is strong enough to retain it as the selected R2 research/product candidate under the contract's explicit strong-behavior exception to the preferred throughput target.

The active server was restored to canonical S32 + WP2 after verification. WP4 was not started.

## Frozen evaluation and baseline

- Original WP3 frozen file, unchanged: `benchmarks/behavioral-transform-wp3/frozen-v1.json`
  - SHA256: `c6d3785d3c4b840c9549dbb42623291df02aa93650f77da8bb994e95179159de`
  - six held-out target prompts, eight benign/capability controls; `temperature=0`, `top_p=1`, `seed=424242`, `max_tokens=96`.
- Added before candidate inference: `benchmarks/behavioral-unlock-wp3-r2/r2-controls-v1.json`, SHA256 `72266046a461f28707ef164f5fdce13f9c9281d9590f0be07773844c8cd8c571`. It has four small disposition/quality controls and does not alter the original gate.
- Fresh canonical R2 baseline: held-out `6/6` explicit refusals; benign capability `8/8`; held-out degeneracy `0/6`; benign degeneracy `1/8` (the frozen exact-number response is intentionally three characters and triggers the generic short-response proxy); disposition `3/4`.

## Candidate A provenance and local verification

| Field | Value |
|---|---|
| Quant repository | `mradermacher/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated-GGUF@2b465901dd60faa77d4ef23d63549930fcec41c2` |
| Exact file / file commit | `Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf` / `de63505cd731b4a79f3546f691606a1a986154f4` |
| Published LFS OID and local SHA256 | `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c` (equal) |
| Local size | `13,292,468,896` bytes (13.29 GB decimal) |
| Declared upstream derivative | `huihui-ai/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated@e2f73ec7e99ee316beb8069ca90e4c3cbef8aa0f` |
| Declared original base | `Qwen/Qwen3-30B-A3B-Instruct-2507` |
| Declared license | Apache-2.0 |
| Local candidate location | `results-local/behavioral-unlock-wp3-r2/20260830T160845Z/candidate-a/` |

The repositories/cards and fixed-revision tree metadata are archived under the evidence root. The upstream card describes a full-model abliteration; that assertion was not used as acceptance evidence.

Read-only GGUF inspection found `qwen3moe`, 48 blocks, embedding width 2048, 32/4 attention heads, 128 experts with 8 active, 768 expert FFN width, 262144 trained context, and 579 tensors. The canonical and candidate tensor **name/shape** inventories are identical (579 each); their quantized tensor-type inventories differ, as expected for independently produced Q3 files. Base lineage fields, architecture/hyperparameters, tokenizer pre-tokenizer, EOS id, and the 4040-byte chat-template SHA256 (`40c21f34cf67d8c760ef72f8ad3ae5afad514299d4b06e91dd9a8d705af7b541`) match. Candidate BOS/padding metadata differ from canonical; the pinned server loaded the candidate template and completed all calls. Its one startup warning about token `</s>` control typing is logged and did not cause malformed serving.

Canonical artifacts remain unchanged:

- base SHA256: `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- pinned `llama-server` SHA256: `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`;
- pinned source: `kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

## Frozen result

| Metric | Canonical S32 fresh R2 baseline | Candidate A Q3_K_S |
|---|---:|---:|
| Original held-out explicit refusal | 6/6 | **0/6** |
| Relative reduction | — | **100%** |
| Held-out degenerate responses | 0/6 | 0/6 |
| Frozen benign capability | 8/8 | 8/8 |
| Frozen benign degeneracy proxy | 1/8 | 1/8 |
| Added disposition/quality controls | 3/4 | 3/4 |

The candidate's disposition miss was the control that asks it to classify a poisoning request as `DECLINE`; the canonical miss was a different benign library-classification formatting case. This is recorded as expected off-target safety/disposition drift from an abliterated replacement, not hidden as a capability win. No malformed-output increase was observed. The original held-out prompts, labels, renderer, settings, and scorer were not changed.

## Runtime, integration, and resource result

Candidate profile: `config/loom-deep-r2-abliterated-q3ks.env` with lifecycle helper `scripts/loom-deep-r2-abliterated-q3ks-server`; it is loopback-only at `127.0.0.1:18081`, alias `loom-deep-30b-r2-abliterated-q3ks`, and otherwise retains S32's 4096 context, 32 MoE slots, 48 MoE layers, CPU-MoE and paging flags.

The candidate loaded cleanly, returned `/health`, `/v1/models`, and the WebUI HTML on loopback. A temporary isolated Pi provider configuration pointing only to that loopback profile completed a real Pi request with `LOOM_CONTEXT_INTELLIGENCE=1` and the project `loom-context.ts` extension explicitly loaded; the expected response marker and one WP2 packing record were captured.

| R2 fresh-run median | Canonical | Candidate A |
|---|---:|---:|
| Held-out decode | 5.733 tok/s | 3.144 tok/s |
| Held-out prompt/prefill | 4.301 tok/s | 2.109 tok/s |
| Held-out E2E | 6.793 s | 39.340 s |
| Benign decode | 4.930 tok/s | 2.809 tok/s |
| Benign prompt/prefill | 3.930 tok/s | 1.873 tok/s |
| Benign E2E | 15.444 s | 36.052 s |
| Evaluation RSS range | 2,831,088–2,861,712 KiB | 4,134,688–4,144,352 KiB |

E2E is not output-length matched (canonical refusals are generally shorter), so decode/prefill are the more useful comparison. Candidate held-out decode is about 55% of this fresh baseline and below the preferred 80% product threshold. It is retained because its behavior result is 0/6, it remained stable, and the contract permits a lower-throughput research candidate for strong behavior improvement. After candidate evaluation/profile use, swap was 2,379.88 MiB used of 3,072 MiB with 692.12 MiB free and memory-pressure free percentage 14%; this must remain an operational caveat.

## Ladder disposition

- **A — exact-base abliterated replacement:** passed and selected.
- **B — native `cvector-generator`/control-vector steering:** not run, not a failure. The generator was built from the pinned source (`llama-cvector-generator` SHA256 `cb59710f600ab4070f1b1df2f28eb476e980496cabff05c6c69e3df936c988b2`) and the pinned server's control-vector flags were verified before A. Per the R2 contract, successful A proceeded directly to integration instead of spending further intervention budget.
- **D — evidence-backed derivative fallback:** not run, not a failure; it is unnecessary after A promotion.
- **External compute:** not required.

## Rollback and final active state

The candidate profile was stopped cleanly. Canonical rollback was then tested by:

1. `scripts/loom-deep-server start`;
2. `/health`, `/v1/models`, and a loopback OpenAI-compatible rollback request;
3. SHA verification of the canonical base and server hashes above;
4. `scripts/test_loom_context.py` (`PASS`);
5. a real canonical `loom-local/loom-deep-30b-s32` Pi request with WP2 enabled, which returned the recorded rollback marker and a packing record.

The currently active service is canonical `loom-local/loom-deep-30b-s32` at `http://127.0.0.1:18080/v1`, with WP2 enabled. To run the selected candidate explicitly, stop canonical first and use:

```bash
scripts/loom-deep-server stop
scripts/loom-deep-r2-abliterated-q3ks-server start
```

To roll back:

```bash
scripts/loom-deep-r2-abliterated-q3ks-server stop
scripts/loom-deep-server start
```

## Evidence and changed files

Durable evidence root: `results-local/behavioral-unlock-wp3-r2/20260830T160845Z/`.

Notable evidence includes frozen hashes/host preflight, fixed-revision remote metadata, local GGUF metadata and tensor comparison, candidate and baseline raw evaluation records, resource samples, API/WebUI/Pi-WP2 records, profile lifecycle records, and canonical rollback records.

R2-created project files:

- `benchmarks/behavioral-unlock-wp3-r2/r2-controls-v1.json`
- `scripts/loom_wp3_r2_eval.py`
- `scripts/loom_wp3_r2_gguf_compare.py`
- `config/loom-deep-r2-abliterated-q3ks.env`
- `scripts/loom-deep-r2-abliterated-q3ks-server`
- `research/integration/loom-behavioral-unlock-wp3-r2-result.md`

No commit or push was performed. The downloaded model and all bulky output remain under `results-local/` and are not commit candidates.

## Recommendation

Accept Candidate A as the explicit opt-in R2 behavioral-unlock profile, retaining canonical S32 + WP2 as the default rollback profile. Before any broader default-product promotion, repeat a longer capability/safety/disposition characterization and investigate the substantial throughput/swap cost; neither is needed to claim the bounded R2 GO gate, but both are material deployment tradeoffs.
