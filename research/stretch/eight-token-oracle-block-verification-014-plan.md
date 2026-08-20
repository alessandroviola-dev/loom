# LOOM Stretch 014 — Eight-Token Oracle Block Verification

Date: 2026-08-20
Status: READY

## Objective

Test whether increasing the oracle verification block from 4 tokens to 8 tokens materially improves streamed target-verification throughput.

Stretch 013 established the current oracle upper-bound reference:

- block size: 4 tokens
- target traversals: 4
- accepted tokens: 16
- oracle verification throughput: 1.8857486 tok/s
- Stretch 012 reference: 0.477929 tok/s
- Stretch 013 speedup over Stretch 012: 3.9457x

The usability target remains approximately 20 tok/s.

## Frozen baseline

Stretch 013 is the frozen workload baseline. Its source blob is:

`deeb0339294162f38cd4522d2890b6a0c728f96e`

Canonical Stretch 013 result:
`research/stretch/four-token-oracle-block-verification-013-result.md`.

No model, quantization, KV-cache, prompt, safety gate, host-state gate, hotset, I/O instrumentation or numerical workload changes are permitted.

## Scientific change

Exactly one experimental factor changes:

- Stretch 013: 4-token oracle blocks × 4 traversals
- Stretch 014: 8-token oracle blocks × 2 traversals

The same frozen 16-token oracle sequence is used:

`[1, 374, 264, 4647, 1483, 304, 279, 1809, 315, 5994, 320, 1654, 23740, 285, 8, 311]`

The experiment remains an oracle upper bound. It does not claim real speculative-decoding speed because there is still no draft model and therefore no draft-model cost, proposal latency, rejection or rollback cost.

## Frozen runner

Runner:
`scripts/stretch_eight_token_oracle_block_verification_014.py`

Frozen runner blob:
`6d7afd43969e752a7cce39ae474d7054ccc7edd8`.

The runner verifies exact Stretch 013 source provenance before transformation.

Parent and child both route through the Stretch 014 wrapper so the same 8-token transform is applied in both processes. An earlier pre-freeze wrapper revision routed the child through Stretch 013; it was corrected before any Stretch 014 scientific run and has no scientific result.

## Required gates

- Stretch 013 source provenance: PASS
- Frozen transform: PASS
- Prompt parity: PASS
- All 16 position numerical parities: PASS
- All 16 position top-1 predictions equal: PASS
- Both 8-token oracle blocks fully accepted: PASS
- Generated sequence equal: PASS
- streamed KV-cache offsets: 4 → 12 → 20
- allocated KV bytes remain unchanged below the 256-position boundary
- persistent eight-layer hotset remains exact
- streamed-layer/shared-stage materialization gates remain exact
- resident and streamed safety/host-state gates remain PASS
- Darwin process-I/O attribution preserved
- no OS cache purge.

## Measurements

Record:

- full streamed block wall time
- block traversals/s
- accepted tokens/block
- accepted tokens/target traversal
- oracle verification tok/s
- ratio vs Stretch 013 1.8857486 tok/s
- ratio vs Stretch 012 0.477929 tok/s
- materialization wall time
- forward wall time
- materialization disk-read bytes
- full-pass disk-read bytes
- bytes per accepted token
- peak swap
- minimum free memory
- peak child RSS.

## Interpretation

The primary question is whether doubling block size continues to amortize the target traversal or whether block compute/shared-stage/framework overhead begins to dominate.

No fixed speedup threshold is required for scientific PASS. The approximately 20 tok/s target remains a profile-promotion target, not an intermediate gate.

Primary PASS classification:
`EIGHT_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`.

If 8-token blocks materially improve target-side throughput, continue to a single 16-token oracle block as one final upper-bound point before selecting a real draft model. If improvement saturates, stop increasing block size and move to the residual-cost/real-drafter phase.