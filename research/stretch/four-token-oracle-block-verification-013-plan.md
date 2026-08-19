# Stretch 013 — Four-Token Oracle Block Verification — Preregistered Plan

Date: 2026-08-19
Status: READY AFTER RUNNER FREEZE

## Purpose

Stretch 012 improved the eight-layer-hotset runtime from 0.312407 token/s (Stretch 011 pure streaming) to 0.477929 token/s while preserving exact resident parity. This is a real RAM-for-I/O improvement, but it remains far below the LOOM interactive usability target of approximately 20 token/s.

The dominant architectural cost remains repeated target-weight traversal. Stretch 013 therefore tests whether multiple known-correct autoregressive tokens can be verified in one target traversal.

This is an **oracle upper-bound experiment**, not deployable speculative decoding.

## Single scientific change vs Stretch 012

Keep the exact eight-layer persistent-hotset architecture and replace sixteen one-token streamed target feedback passes with **four target block passes of four oracle tokens each**.

The oracle draft sequence is the frozen resident-greedy sequence already reproduced exactly in Stretch 010–012:

`[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`.

Block size: **4**.
Target block traversals after prompt: **4**.
Oracle draft tokens verified: **16**.

No real draft model runs in this experiment and draft-model cost is zero by construction. Reported throughput is therefore an upper bound on the target-verification side only.

## Frozen upstream

Stretch 009 source:
`scripts/stretch_four_token_kv_autoregressive_parity_009.py`
blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`.

Stretch 010 transform:
`scripts/stretch_sixteen_token_autoregressive_stability_010.py`
blob `ff3dc83abc6388113fca15594eef6b3ec00ebe50`.

Stretch 011 instrumentation:
`scripts/stretch_materialization_io_attribution_011.py`
blob `16125f7eb0b2fb662591e194de0498513a563a6d`.

Stretch 012 hotset transform:
`scripts/stretch_eight_layer_persistent_hotset_012.py`
blob `8e10660af778655a279f30e7d59785163bc204e3`.

Stretch 012 canonical result:
`research/stretch/eight-layer-persistent-hotset-012-result.md`.

## Preserved architecture

Unchanged:
- Qwen3-8B 3-bit/group64
- mlx 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- frozen prompt token IDs `[[1,42,2048,151935]]`
- ordinary BF16 36-layer KVCache
- official fully resident sequential control
- transformer layers 0..7 retained persistently
- layers 8..35 streamed and evicted per target traversal
- embedding/final RMSNorm/LM head streamed per target traversal
- Darwin `proc_pid_rusage(RUSAGE_INFO_V2)` attribution
- exact weight/materialization gates
- host launch gate and runtime safety guardrails
- file-backed child state/final/stdout/stderr
- no tokenizer
- no sampling
- no KV quantization
- no prefetch/double buffering
- no OS-cache purge
- no new model/download.

## Oracle block-verification semantics

The resident control still performs the frozen ordinary 16-token greedy autoregressive sequence one token at a time and retains resident logits after each consumed token.

The streamed/hotset target path performs:
1. ordinary streamed prompt prefill, producing the prompt logits and KV offset 4;
2. block 1 consumes oracle tokens 1–4 together;
3. block 2 consumes oracle tokens 5–8 together;
4. block 3 consumes oracle tokens 9–12 together;
5. block 4 consumes oracle tokens 13–16 together.

Each target block contains four causally masked positions and uses the same persistent per-layer KVCache state.

Expected streamed cache offsets:
- after prompt: 4
- after block 1: 8
- after block 2: 12
- after block 3: 16
- after block 4: 20.

KV allocation should remain approximately 37,748,736 B because offset 20 remains below the first 256-position allocation boundary.

## Verification rule

For each block `[d1,d2,d3,d4]`:
- `d1` must equal the target top-1 prediction immediately preceding the block;
- target logits after consuming `d1` must predict `d2`;
- target logits after consuming `d2` must predict `d3`;
- target logits after consuming `d3` must predict `d4`.

The final position logits predict the first token of the next oracle block, or a diagnostic token after block 4.

Because the oracle sequence is already known to be the resident greedy sequence, all 16 oracle tokens should be accepted. Any mismatch is a correctness failure and must not be rescued.

## Numerical parity gates

Prompt:
- preserve full resident-vs-streamed prompt-logit parity gate.

For every one of the 16 consumed oracle token positions:
- compare the corresponding block-position logits against the frozen resident sequential logits after consuming the same token;
- use the inherited numerical threshold formula;
- require top-1 equality.

Thus block execution must reproduce the same per-position target state/output as ordinary resident sequential execution, not merely accept the oracle IDs.

Primary correctness requires all 16 position-level comparisons PASS and all 16 oracle tokens accepted.

## Hotset/weight gates

Preserve Stretch 012:
- persistent layer IDs 0..7 exactly
- hotset initial materialized delta ~675,418,112 B within preregistered tolerance
- no layer-sized rematerialization for hotset layers during block passes
- layers 8..35 materialize ~84,427,264 B per traversal
- embedding/head stage ~272,269,312 B
- hybrid simultaneous raw-weight accounting includes persistent hotset + max new stage.

## Target traversal accounting

After prompt:
- baseline Stretch 012: 16 one-token target traversals for 16 tokens
- Stretch 013: 4 four-token target traversals for 16 oracle tokens.

Frozen target-traversal amortization:
**4 accepted oracle tokens per target traversal** if all gates pass.

Report:
- number of target block traversals
- accepted oracle tokens
- accepted tokens / traversal
- total target block wall time
- wall seconds / accepted token
- **oracle target-verification token/s = accepted tokens / total block wall time**.

This is not deployable end-to-end speculative throughput because draft-model proposal cost, rejection behavior and rollback/recovery cost are intentionally absent.

## I/O metrics

For each of the four target blocks report:
- transformer materialization process disk-read bytes
- full-pass process disk-read bytes
- page-ins
- full block wall
- values amortized per accepted oracle token.

Primary architectural question:
> Does one four-position causal target block cost materially closer to one target weight traversal than to four sequential target traversals?

No fixed speedup/I/O threshold is required for scientific PASS.

## Performance target context

LOOM interactive usability target:
~**20 token/s**.

Stretch 012 baseline:
**0.477929 logical token/s** under its valid host state.

Stretch 013 does not need to reach 20 token/s to PASS. Its purpose is to measure the maximum target-side benefit obtainable from four-token verification before adding a real drafter.

If the oracle target-verification rate remains far below the usability target, larger block sizes and/or additional residency/shared-stage optimization may be needed before a real speculative decoder can plausibly reach the target.

## Resource safety

Host launch gate unchanged:
- 3 samples each >=60% free memory
- swap <=5600 MB.

Runtime abort unchanged:
- free memory <5%
- swap >5600 MB.

No automatic hotset/block-size rescue is allowed.

## Failure classifications

Primary PASS:
`FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`.

Other relevant classifications:
- inherited source/version/config/host/resource failures
- `ORACLE_SEQUENCE_PROVENANCE_FAIL`
- `ORACLE_TOKEN_REJECTED`
- `ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`
- `ORACLE_BLOCK_TOP1_MISMATCH`
- `ORACLE_BLOCK_CACHE_STATE_FAIL`
- inherited hotset/weight-stage failures
- telemetry/runtime/harness failures.

Harness/API failures are not model failures.

## Decision after result

If four-token oracle verification materially amortizes target traversal and increases accepted-token-equivalent throughput, test a separately preregistered larger oracle block (for example 8 tokens) before selecting a real draft model.

If block verification gives little gain despite four accepted tokens/traversal, identify the residual stage cost (shared embedding/head, block compute, I/O or framework overhead) before adding a drafter.

Only after the oracle upper bound is promising should LOOM add a real draft model and measure acceptance rate plus actual end-to-end throughput.