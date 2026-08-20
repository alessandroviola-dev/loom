# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_017_FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This remains a promotion target, not a PASS threshold for intermediate research.

## Research rules

- Never reset/replace production Pi configuration.
- Never silently delete verified models or canonical results.
- Record disk around model/runtime work.
- Runtime abort where applicable: free memory <5% OR swap >5600 MB.
- Launch gate where preregistered: free memory >=60%, swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness defects are not model failures.
- Do not weaken resource or parity gates post-hoc.
- Change one scientific factor at a time where causal attribution matters.
- No hidden rescue ladders/retries.
- No new large-model download while existing artifacts suffice.
- Treat Darwin process-I/O accounting as diagnostic, not forensic per-file SSD tracing.
- Do not purge macOS caches to manufacture host state.
- After every meaningful result/decision update `HANDOFF.md` and `ROADMAP.md`.

## Frozen target/environment

Model:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Configuration:
- Qwen3
- hidden size 4096
- 36 transformer layers
- vocab 151936
- 32 attention heads / 8 KV heads
- head dim 128
- RMSNorm eps 1e-6
- untied embedding/head
- quantization 3-bit / group64

Frozen runtime:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1

Weights:
- total 3,583,928,320 B
- embedding 272,269,312 B
- transformer body 3,039,381,504 B
- each layer 84,427,264 B / 25 tensors
- final RMSNorm 8,192 B
- LM head 272,269,312 B

## Stretch history

### Stretch 001–009 — COMPLETE PASS

Established:
- layer-addressable safetensors I/O
- bounded MLX materialization/eviction
- exact resident/streamed block parity
- full 36-layer streamed body parity
- exact full-logit parity
- persistent ordinary KV cache
- exact sequential autoregressive parity through 4 feedback tokens.

Key checkpoint files remain under `research/stretch/` and `scripts/`.

### Stretch 010 — COMPLETE PASS

`SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`, run `20260819-183844`:
- exact prompt + 16 feedback logits
- identical sequence `[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`
- final KV offset 20
- logical throughput 0.346144 token/s
- late materialization cost rises strongly while layer forward stays ~0.19 s/token.

### Stretch 011 — COMPLETE PASS

`MATERIALIZATION_IO_ATTRIBUTION_PASS`, run `20260819-185036`:
- late transformer materialization reads ~3.039 GB/token under Darwin process accounting
- late full pass ~3.584 GB/token
- materialization-time/disk-read Pearson 0.9995866107996246
- logical throughput 0.312407 token/s.

Decision: repeated target-weight traversal is the dominant late cost under current accounting.

### Stretch 012 — COMPLETE PASS

`EIGHT_LAYER_PERSISTENT_HOTSET_PASS`, run `20260819-192349`:
- persistent layers 0..7
- hotset 675,418,112 B
- hybrid simultaneous raw-weight budget 947,687,424 B
- exact 16-token parity
- logical throughput **0.477929 token/s**
- ~52.98% improvement vs 011.

Decision: residency helps but is insufficient alone for ~20 token/s.

### Stretch 013 — COMPLETE PASS

`FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`, run `20260819-193702`:
- four causal target traversals x four known-correct oracle tokens
- all 16 position logits exact vs resident sequential control
- all oracle tokens accepted
- streamed KV `4 -> 8 -> 12 -> 16 -> 20`
- target-block total wall 8.484694 s
- oracle target-verification throughput **1.8857486198 token/s**
- rate ratio vs Stretch 012: **3.9456668664x**.

Boundary: oracle upper bound only; no real drafter/draft/rejection/rollback cost.

### Stretch 014 — COMPLETE VALID FAIL

`ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`, valid run `20260820-122922`:
- block size 8 / two traversals
- prompt exact
- first target position already diverges, max abs 0.34375
- all 16 numerical gates fail
- top-1 differs by step 16
- KV state/bytes remain correct
- failure is numerical, not host/resource.

Decision: do not relax parity and do not advance to M=16.

### Stretch 015 — COMPLETE ATTRIBUTION PASS

`QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`, run `20260820-124515`:
- M1 vs M4 exact through layer-0 trace
- M4 vs M8 exact through attention/post-attention norm
- first M4/M8 divergence: `gate_proj`
- `gate_proj`, `up_proj`, `down_proj` shape-dependent at M8
- q/k/v/o remain exact at M8.

Canonical attribution:
> Stretch 014 fails because the frozen MLX 0.31.2 quantized-linear path is shape-dependent; the first observed full-block divergence is in the MLP, not attention/RoPE/KV.

Result:
`research/stretch/eight-token-divergence-attribution-015-result.md`

### Stretch 016 — COMPLETE PASS

`QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`, run `20260820-125212`.

Runner/blob:
- `scripts/stretch_quantized_linear_m_boundary_mapping_016.py`
- `a5c3f4acd6a4150d2db7477f3f20d01a00b4f759`

Exact M boundary on actual layer-0 quantized projections:

Attention-side:
- q_proj exact through M=9; first divergent M=10
- k_proj exact through M=9; first divergent M=10
- v_proj exact through M=9; first divergent M=10
- o_proj exact through M=9; first divergent M=10

MLP-side:
- gate_proj exact through M=5; first divergent M=6
- up_proj exact through M=5; first divergent M=6
- down_proj exact through M=5; first divergent M=6

Largest relevant exact candidate under frozen runtime: **M=5**.

Result:
`research/stretch/quantized-linear-m-boundary-mapping-016-result.md`

Decision:
- MLP sets the first exactness boundary.
- do not treat M>=6 as exact under MLX 0.31.2.
- confirm M=5 across the full 36-layer streamed/hotset oracle path before promoting it as the exact block-size frontier.

## Stretch 017 — Five-Token Oracle Block Confirmation — READY

Plan:
`research/stretch/five-token-oracle-block-confirmation-017-plan.md`

Runner:
`scripts/stretch_five_token_oracle_block_confirmation_017.py`

Frozen runner blob:
`6171440736badf5150297f9c8945209fe49d0826`

Frozen source:
- Stretch 013 blob `deeb0339294162f38cd4522d2890b6a0c728f96e`.

Diagnostic workload:
- resident sequential continuation: first 15 frozen oracle tokens
- streamed target: 3 x 5-token oracle blocks
- oracle prefix: `[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8]`
- expected streamed KV offsets: `4 -> 9 -> 14 -> 19`.

Preserved:
- Qwen3-8B 3-bit artifact
- MLX 0.31.2 / mlx-lm 0.31.3
- eight-layer hotset
- layers 8..35 streamed
- shared stages streamed
- resident sequential control
- ordinary BF16 KV
- exact parity/top-1 gates
- I/O/resource/host gates
- file-backed child routing
- no real drafter
- no runtime upgrade/download.

Primary PASS:
`FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`.

Interpretation boundary:
- this is a correctness confirmation of M=5, not a pure throughput A/B against Stretch 013 because continuation length is 15 rather than 16.
- per-block/per-accepted-token timings are secondary characterization only.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_five_token_oracle_block_confirmation_017.py
python3 scripts/stretch_five_token_oracle_block_confirmation_017.py
```

No download is expected.

## Open questions after Stretch 017

1. Does M=5 remain exact end-to-end across all 36 layers and persisted KV state?
2. If yes, is the M=5 frontier worth retaining operationally, given block geometry and real speculative acceptance constraints?
3. Should the next speed axis be residual I/O/residency/prefetch or a separately preregistered newer-MLX runtime experiment?
4. A newer MLX runtime must not overwrite or redefine the frozen 0.31.2 baseline.
5. Real drafter selection remains deferred until the exact oracle target-side frontier is settled.
