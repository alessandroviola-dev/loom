# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system; tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_014_EIGHT_TOKEN_ORACLE_BLOCK_VERIFICATION_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Promotion target

Interactive usability target: approximately **20 token/s**.

This is a profile-promotion target, not a scientific PASS threshold for intermediate experiments. A technically correct/memory-safe experiment can PASS below 20 token/s, but it is not promoted as a usable interactive LOOM profile until speed is in the target range or a later evidence-based revision is explicitly frozen.

Canonical decision:
`research/usability-speed-target-v1.md`.

## Safety / research constraints

- Never reset or replace production Pi configuration.
- Never silently delete verified models or canonical results.
- Record disk around model/runtime work.
- Runtime guardrail where applicable: free memory <5% OR swap >5600 MB abort.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness/parser/capture defects are not model failures.
- Do not weaken guardrails post-hoc.
- Change one scientific factor at a time where causal attribution matters.
- No automatic rescue ladders or hidden retries.
- No new large-model acquisition while existing artifacts suffice.
- Do not attribute whole-run host telemetry to a sub-phase without phase-scoped evidence.
- Long child runs use file-backed state/final/stdout/stderr or drained pipes.
- Do not equate logical safetensors materialization time or Darwin process disk-I/O accounting with forensic model-file SSD throughput.
- Do not purge macOS caches casually to manufacture a cold-cache state.

Verified GGUF and Direct MLX 3-bit/4-bit artifacts remain retained. Stretch disk remains ~36.27 GiB free; no download is planned.

## Frozen capability references

Canonical Ollama/MLX 4B `qwen3.5:4b-mlx`, context 4096:
- Coding Baseline 001: artifact 40.71, delivery-adjusted 30.00, delivery 3/6, generation 16.01 tok/s
- Pi Agentic Coding 001: delivery-adjusted 77.15, strict 60.00, delivery 6/6, ~612 s.

llama.cpp 4B Q4 efficiency reference:
- pp512 230.85 tok/s
- tg128 22.33 tok/s.

Direct MLX Qwen3-8B 3-bit coding reference:
- technically stable full session
- min free 14%
- artifact 38.57
- delivery-adjusted 27.86
- delivery 2/6
- not promoted on quality.

## Track A — Amplify

Amplifier 001–003 characterized a resource boundary in the canonical 4B repair workflow. Do not claim leak/KV/allocator root cause.

Amplifier 004 remains preregistered/queued:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- single change: repair-feedback variable detail capped at 768 UTF-8 bytes.

Stretch remains primary while the architectural speed/memory frontier is improving.

# Track B — Stretch / Memory Hierarchy

Frozen subject:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Environment/config:
- Qwen3, hidden 4096, 36 layers, vocab 151936
- 32 attention heads, 8 KV heads, head dim 128
- RMSNorm eps 1e-6
- `tie_word_embeddings=false`
- 3-bit/group64
- mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.

Weight layout:
- complete tensor payload 3,583,928,320 B
- embedding 272,269,312 B
- transformer body 3,039,381,504 B
- each transformer layer 84,427,264 B / 25 tensors
- final RMSNorm 8,192 B
- LM head 272,269,312 B.

## Frozen Stretch results

### 001 — COMPLETE PASS
`LAYER_ADDRESSABLE_IO_PASS`: all 36 layers exactly addressable and selectively readable.

### 002 — COMPLETE PASS
`SINGLE_LAYER_MLX_EVICTION_PASS`: one layer materializes 0 -> 84,427,264 -> 0 B active.

### 003 — COMPLETE PASS
`TWO_LAYER_BOUNDED_RESIDENCY_PASS`: repeated one-layer cycles remain bounded.

### 004 — COMPLETE PASS
`TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`: real Qwen3 block compute with exact resident/streamed activation parity.

### 005 — COMPLETE PASS
`EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`: exact parity; resident/streamed layer-weight ratio ~8x.

### 006 — COMPLETE PASS
`FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`, valid run `20260819-164605`:
- body 3,039,315,964 B resident vs max streamed layer 84,427,264 B
- ratio 35.99922371048291x
- exact full-body parity.

### 007A — COMPLETE PASS
`SHARED_COMPONENT_ANATOMY_PASS`:
- embedding 272,269,312 B
- norm 8,192 B
- LM head 272,269,312 B
- untied embedding/head.

### 007B — COMPLETE PASS
`PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`, run `20260819-170334`:
- resident full model 3,583,928,320 B
- max streamed raw-weight stage 272,269,312 B
- ratio 13.16317396798652x
- full logits max/mean diff 0.0 / 0.0.

### 008 — COMPLETE PASS
`ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`, run `20260819-173553`:
- first actual persistent-KV autoregressive streamed proof
- prompt and post-token logits exact parity
- KV offsets 4 -> 5
- KV total 37,748,736 B.

Earlier stdout-pipe stall is harness-only/no scientific result.

### 009 — COMPLETE PASS
`FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`, run `20260819-183143`:
- exact resident/streamed sequence `[1,374,264,4647]`
- exact logits all four feedback steps
- KV offsets 4 -> 8
- mean 36-layer materialization 0.188658 s/token
- mean 36-layer forward 0.192317 s/token.

### 010 — COMPLETE PASS
`SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`, run `20260819-183844`:
- exact prompt + 16 feedback logits
- identical sequence `[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`
- final KV offset 20, 37,748,736 B
- mean full pass 2.888971 s/token
- logical throughput 0.346144 token/s
- discovered materialization transition ~0.19 s early -> ~1.4 s late while forward stays ~0.19 s.

Result:
`research/stretch/sixteen-token-autoregressive-stability-010-result.md`.

### 011 — COMPLETE PASS
`MATERIALIZATION_IO_ATTRIBUTION_PASS`, run `20260819-185036`:
- all correctness/KV gates remain exact
- late transformer materialization process reads ~3,039,395,840 B/token, near 3,039,381,504 B transformer payload
- late full-pass process reads ~3.584 GB/token, near complete payload
- build/select reads negligible
- page-ins zero
- materialization-time vs disk-read Pearson 0.9995866107996246
- mean forward 0.191414 s/token
- logical throughput 0.312407 token/s.

Canonical interpretation: pure one-layer dense autoregressive streaming reaches a regime approximately equivalent to one target-weight traversal per generated token under Darwin process-I/O accounting. This is strong diagnostic evidence, not forensic per-file tracing.

Result:
`research/stretch/materialization-io-attribution-011-result.md`.

### 012 — COMPLETE PASS

Plan:
`research/stretch/eight-layer-persistent-hotset-012-plan.md`

Runner/blob:
- `scripts/stretch_eight_layer_persistent_hotset_012.py`
- `8e10660af778655a279f30e7d59785163bc204e3`.

Valid run `20260819-192349`:
`EIGHT_LAYER_PERSISTENT_HOTSET_PASS`.

Single change vs 011:
- layers 0..7 retained persistently across prompt + 16 tokens.

Correctness/state:
- prompt + all 16 sequential feedback logits max/mean diff 0.0 / 0.0
- same frozen 16-token sequence
- final resident/hybrid KV offsets 20
- KV 37,748,736 B.

Weight residency:
- persistent hotset exactly 675,418,112 B
- largest new streamed/shared stage 272,269,312 B
- hybrid simultaneous raw-weight budget 947,687,424 B (~903.79 MiB)
- resident/hybrid ratio 3.7817620338074676x.

Timing:
- mean layer materialization 0.407471 s/token
- mean layer forward 0.190394 s/token
- mean full pass 2.092360 s/token
- median full pass 2.020580 s/token
- logical throughput **0.477929 token/s**
- improvement vs Stretch 011: approximately **+52.98%**.

I/O:
- late tokens 8–16 mean materialization process reads ~651,784,647 B/token
- late full-pass process reads ~899,052,885 B/token
- materialization-time/disk-read Pearson 0.9972018123495737
- page-ins zero.

The I/O reduction is much larger than simple eight-layer payload subtraction, showing a strong host/cache interaction. Treat this as observed runtime behavior, not deterministic hotset-byte arithmetic.

Resource:
- whole-run min free 23%
- stream prompt min free 60%
- stream tokens min free 59%
- peak swap 1634.62 MB
- peak child RSS 1054.344 MB.

Result:
`research/stretch/eight-layer-persistent-hotset-012-result.md`.

Decision: residency helps but 0.478 token/s remains ~42x below the ~20 token/s usability target. Do not build a long hotset-only frontier yet; test traversal amortization next.

### 013 — COMPLETE PASS

Plan:
`research/stretch/four-token-oracle-block-verification-013-plan.md`

Runner/blob:
- `scripts/stretch_four_token_oracle_block_verification_013.py`
- `deeb0339294162f38cd4522d2890b6a0c728f96e`.

Valid run `20260819-193702`:
`FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`.

Single scientific change vs 012:
- 16 one-token target traversals -> 4 causal target traversals of 4 known-correct oracle tokens each.

Correctness:
- prompt max/mean logit diff 0.0 / 0.0
- all 16 block-position max/mean diffs 0.0 / 0.0
- top-1 equality all 16 positions
- all 16 oracle tokens accepted
- resident/oracle sequence identical
- streamed KV offsets 4 -> 8 -> 12 -> 16 -> 20
- final KV 37,748,736 B.

Hotset/residency unchanged:
- persistent hotset 675,418,112 B
- hybrid max raw-weight budget 947,687,424 B
- resident/hybrid ratio 3.7817620338074676x.

Target-side performance:
- block size 4
- target traversals 4
- accepted tokens 16
- accepted tokens/traversal 4.0
- target block walls `[2.153909,1.990925,2.123198,2.216662]` s
- total target-block wall 8.484694 s
- wall/accepted token 0.530293375 s
- oracle target-verification throughput **1.8857486198 token/s**
- ratio vs Stretch 012 **3.9456668664x**.

I/O:
- mean full-pass process-read accounting per accepted oracle token ~49,986,816 B
- strong host/cache-state effects remain; process accounting is not per-file tracing.

Resource:
- min free 24%
- stream blocks min free 59%
- peak swap 1684.88 MB
- peak child RSS 1105.328 MB.

Canonical interpretation:
> Four known-correct tokens can be consumed and verified in one causal streamed/hotset target traversal while reproducing sequential resident logits exactly. The oracle target-side rate scales almost ideally with block size (3.9457x for a 4-token block), proving target traversal amortization is a viable speed axis.

Boundary:
- no real drafter
- zero draft cost
- no rejection/rollback cost
- `1.88575 token/s` is an oracle target-verification upper-bound metric, not deployable speculative throughput.

Result:
`research/stretch/four-token-oracle-block-verification-013-result.md`.

Decision: test one larger oracle block before selecting a real drafter.

## Stretch 014 — Eight-Token Oracle Block Verification — READY

Plan:
`research/stretch/eight-token-oracle-block-verification-014-plan.md`

Runner:
`scripts/stretch_eight_token_oracle_block_verification_014.py`

Frozen runner blob:
`6d7afd43969e752a7cce39ae474d7054ccc7edd8`.

Frozen source:
- exact Stretch 013 blob `deeb0339294162f38cd4522d2890b6a0c728f96e`.

Single scientific change:
- oracle block size **4 -> 8**
- target traversals for the same 16-token oracle sequence **4 -> 2**.

Preserved:
- same 16-token oracle sequence
- resident sequential control
- eight-layer hotset 0..7
- layers 8..35 streamed
- shared stages streamed
- ordinary BF16 KVCache
- exact per-position numerical parity/top-1 gates
- Darwin I/O attribution
- host/runtime guardrails
- file-backed child transport
- no tokenizer/sampling/real drafter/KV quantization/prefetch/download.

Expected streamed KV offsets:
`4 -> 12 -> 20`.

Primary metric:
`oracle_target_verification_tokens_per_second` for 16 accepted tokens across two target traversals.

Primary PASS:
`EIGHT_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`.

Harness note:
- an earlier pre-freeze 014 wrapper revision routed the inherited child through the Stretch 013 path;
- corrected before any Stretch 014 scientific run;
- final frozen wrapper routes both parent and child through 014 so the same 8-token transform is applied in both processes;
- no scientific result exists for the pre-freeze revision.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_eight_token_oracle_block_verification_014.py
python3 scripts/stretch_eight_token_oracle_block_verification_014.py
```

No download is expected.

If 014 materially improves target-side throughput, preregister one final 16-token oracle block upper-bound point before introducing a real drafter. If scaling saturates, stop increasing block size and move to residual-cost/real-drafter work.

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before advancing.