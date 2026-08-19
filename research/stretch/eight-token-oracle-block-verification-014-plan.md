# LOOM Stretch 014 — Eight-Token Oracle Block Verification

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

No model, quantization, KV-cache, prompt, safety gate, host-state gate, or numerical workload changes are permitted.

## Scientific change

Exactly one experimental factor changes:

- Stretch 013: 4-token oracle blocks × 4 traversals
- Stretch 014: 8-token oracle blocks × 2 traversals

The same frozen 16-token oracle sequence is used:

`[1, 374, 264, 4647, 1483, 304, 279, 1809, 315, 5994, 320, 1654, 23740, 285, 8, 311]`

The experiment remains an oracle upper bound. It does not claim real speculative-decoding speed because there is still no draft model and therefore no draft-model cost or proposal latency.

## Required gates

- Stretch 013 source provenance: PASS
- Frozen transform: PASS
- Prompt parity: PASS
- All 16 position numerical parities: PASS
- All 16 position top-1 predictions equal: PASS
- All 8-token oracle blocks fully accepted: PASS
- Generated sequence equal: PASS
- KV-cache offsets: 4 → 12 → 20 for streamed blocks
- Allocated KV bytes remain unchanged throughout
- Resident and streamed safety/host-state gates remain PASS
- No OS cache purge

## Measurements

Record:

- full streamed block wall time
- block traversals/s
- accepted tokens/block
- oracle verification tok/s
- materialization wall time
- materialization disk-read bytes
- full-pass disk-read bytes
- peak swap
- minimum free memory
- peak child RSS

The primary comparison is oracle verification tok/s against Stretch 013's 1.8857486 tok/s.

## Interpretation

If 8-token blocks materially improve throughput, continue to a 16-token oracle block test. If the improvement saturates, stop increasing block size and move to a real speculative-decoding architecture where a resident draft model proposes blocks and Qwen3 verifies them.
