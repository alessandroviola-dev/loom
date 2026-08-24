# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001_FAIL_GATE`
Strategic next: `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, full intended model capacity, reproducible correctness and later behavioral-freedom validation.

Canonical target values and stable invariants live in `/AGENTS.md`.

## Proven

- full Qwen3-30B-A3B external-expert execution across all 48 layers;
- exact final logits and real greedy generation;
- complete ~819-MB shared-backbone residency;
- expert-major disk geometry as a real decode win;
- real routing reuse;
- large 4-GiB resident raw cache rejected for memory pressure;
- DFlash exact-target static fit plausible;
- exact target taps `[1,12,23,34,45]` exposed with negligible runtime-memory cost.

## B7 block finding

`LOOM_DFLASH_BLOCK_VERIFIER_001_FAIL_GATE`:
- B2/B4 exact;
- B7 not exact, though token decisions/router IDs remain stable;
- B7 routing union reduces useful expert bytes to ~452.65 MB/verified position;
- B7 block wall 6.317 s vs 9.927 s sequential;
- memory and expert ownership safe.

`LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001_FAIL_GATE` localizes the issue:
- divergence starts at layer 0 / position 0 / post-attention hidden;
- initial max error `1.4901161e-08` while K/V are still bitwise exact;
- normal B7 block and union-coalesced B7 are bitwise identical to each other;
- therefore expert union/coalescing is not the cause;
- the cause is B7 batched-attention arithmetic, whose tiny difference cascades to final logits.

Do not relax the gate merely because token decisions match.

## Next — exact wavefront verifier

`LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001`.

Goal: retain B7 expert-I/O union amortization without using the numerically different multi-query attention kernel.

Execution candidate:
1. process each layer across the 7 candidate positions;
2. attention remains canonical `q_len=1` and position-sequential, so per-position attention/KV matches normal decode;
3. collect routes for all 7 positions at that layer;
4. load each unique expert once, reuse it across assigned positions, preserving per-position expert execution/aggregation semantics;
5. advance to next layer.

Required gate:
- 48-layer and final-logit bitwise parity against sequential teacher-forced B7;
- correct KV advancement;
- zero expert leak / swap growth;
- retain material expert-byte reduction and measure real wall.

If PASS, target-side B7 verification is complete and a minimal learned DFlash port becomes justified.

## After wavefront PASS

1. minimal DFlash drafter port;
2. measure real draft memory/workspace;
3. measure acceptance length and target verifications/output token;
4. measure unique expert bytes/accepted token and sustained generation tok/s;
5. reconsider small complementary storage/cache only from measured block economics;
6. capability/coding benchmark;
7. context/stability;
8. if speed remains insufficient, route prediction/prefetch or LOOM-native co-design;
9. behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only the active work-package delta. Pi performs local code/tests/evidence; ChatGPT owns Git/HANDOFF/ROADMAP.
