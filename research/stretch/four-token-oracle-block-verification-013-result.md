# Stretch 013 — Four-Token Oracle Block Verification — Result

Date: 2026-08-19
Valid run: `20260819-193702`
Classification: **FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS**

## Provenance

Plan:
`research/stretch/four-token-oracle-block-verification-013-plan.md`

Runner:
`scripts/stretch_four_token_oracle_block_verification_013.py`

Frozen runner blob:
`deeb0339294162f38cd4522d2890b6a0c728f96e`.

Frozen upstream:
- Stretch 009 source `3e0780850bb65f9dccf07946f89597fa2e4d17e1`
- Stretch 010 transform `ff3dc83abc6388113fca15594eef6b3ec00ebe50`
- Stretch 011 instrumentation `16125f7eb0b2fb662591e194de0498513a563a6d`
- Stretch 012 hotset `8e10660af778655a279f30e7d59785163bc204e3`.

Scientific change vs Stretch 012:
- sixteen one-token streamed target traversals were replaced by four causal target traversals of four frozen oracle tokens each.

No real draft model ran. Draft cost, rejection behavior and rollback/recovery cost were therefore absent by construction.

## Correctness — PASS

Prompt parity:
- max absolute logit difference 0.0
- mean absolute logit difference 0.0
- token equality true.

All 16 oracle block positions:
- numerical parity PASS
- max absolute logit difference 0.0
- mean absolute logit difference 0.0
- top-1 equality true.

Resident generated sequence:
`[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`.

Streamed/oracle sequence identical.

All 16 oracle tokens were accepted.

KV:
- resident final offsets all 20
- streamed final offsets all 20
- resident/streamed final KV bytes 37,748,736 / 37,748,736 B.

Thus the four-position causal target blocks reproduced the corresponding sequential resident target states exactly for this frozen micro-case.

## Weight residency

- official resident full-model materialized delta: 3,583,928,320 B
- persistent eight-layer hotset: 675,418,112 B
- largest newly materialized shared/streamed stage: 272,269,312 B
- hybrid max simultaneous raw-weight budget: 947,687,424 B
- resident/hybrid raw-weight ratio: 3.7817620338074676x.

Hotset architecture remained unchanged from Stretch 012.

## Target traversal amortization

Oracle block size: 4.

Target block traversals after prompt: 4.

Accepted oracle tokens: 16.

Accepted tokens / target traversal: **4.0**.

Target block full-pass walls:
`[2.153909,1.990925,2.123198,2.216662]` s.

Total target-block wall:
**8.484694 s**.

Wall / accepted oracle token:
**0.530293375 s/token**.

Oracle target-verification rate:
**1.8857486198087994 token/s**.

Stretch 012 sequential-hotset logical rate:
**0.477929 token/s**.

Observed oracle target-side rate ratio vs Stretch 012:
**3.945666866435808x**.

This is very close to the ideal 4x traversal-amortization factor for a block of four, under the frozen host state and with zero draft cost.

## Target block stage timing

Transformer materialization walls per block:
`[0.154359,0.145043,0.210515,0.266315]` s.

Transformer forward walls per block:
`[0.423719,0.406265,0.400966,0.412646]` s.

Means:
- transformer materialization: 0.194058 s/block
- transformer forward: 0.410899 s/block
- full target block pass: 2.121173 s/block
- median full target block pass: 2.138553 s/block
- target block traversals/s: 0.471437.

The forward cost rises relative to a one-token pass, as expected for four positions, but the weight traversal is amortized over four accepted tokens.

## Darwin process I/O attribution

Transformer materialization disk-read bytes/block:
`[2637824,262144,97681408,225214464]`.

Full-pass disk-read bytes/block:
`[273022976,266240,149995520,376504320]`.

Amortized materialization bytes/accepted token:
`[659456.0,65536.0,24420352.0,56303616.0]`.

Amortized full-pass bytes/accepted token:
`[68255744.0,66560.0,37498880.0,94126080.0]`.

Mean full-pass process-read accounting per accepted oracle token:
**49,986,816 B/token**.

As in prior Stretch experiments, Darwin `ri_diskio_bytesread` remains process accounting rather than forensic per-file SSD tracing. The very low values in some blocks also demonstrate strong host/cache-state effects.

## Resource telemetry

Launch:
- 73%, 73%, 74% free
- swap ~1290–1299 MB.

Whole run:
- minimum free memory 24%
- peak swap 1684.88 MB
- peak child RSS 1105.328 MB.

Phase-scoped:
- stream prompt min free 60%
- stream blocks min free 59%
- stream-block peak child RSS 994.891 MB.

Disk:
36.275 -> 36.273 GiB.

## Canonical interpretation

Stretch 013 validates the core target-side premise of block/speculative verification for LOOM: when four future tokens are known-correct, the Qwen3-8B target can consume and verify them in one causal streamed/hotset traversal while reproducing the sequential resident target logits exactly at every position.

For this frozen run, four accepted tokens per target traversal increased the oracle target-verification rate from the Stretch 012 sequential-hotset baseline of 0.477929 token/s to 1.885749 token/s, a 3.9457x target-side improvement.

This is **not deployable generation throughput**. The experiment deliberately excludes the cost of producing draft tokens and excludes rejection/rollback behavior. It establishes an upper bound and proves that target traversal amortization itself works.

## Decision

The ~4x block-size-4 result is strong enough to justify one larger oracle upper-bound point before selecting a real drafter.

Next experiment: increase only oracle block size from 4 to 8 while preserving the eight-layer hotset, the same 16-token oracle sequence, all resident/parity/KV/I/O/resource gates, and zero draft cost.

The purpose is to measure whether target-side throughput continues to scale with block size or begins to saturate from block compute/shared-stage/framework overhead.