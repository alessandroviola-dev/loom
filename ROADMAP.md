# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`
Strategic next: `LOOM_DFLASH_DRAFTER_PORT_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, full intended model capacity, reproducible correctness and later behavioral-freedom validation.

Canonical target values and stable invariants live in `/AGENTS.md`.

## Proven target/runtime

- full Qwen3-30B-A3B external-expert execution across all 48 layers;
- exact final logits and real greedy generation;
- complete ~819-MB shared-backbone residency;
- expert-major disk geometry as a real decode win;
- real routing reuse;
- large 4-GiB resident raw cache rejected for memory pressure;
- exact DFlash target taps `[1,12,23,34,45]` exposed with small overhead.

## DFlash target verification — PASS

Exact-target candidate:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Static draft:
- BF16 ~1.2685 GiB;
- 5 layers;
- proposals=7;
- static M1/8-GB fit plausible;
- custom LOOM/MLX port required.

The first B7 block implementation was not exact because batched attention changed floating execution. Diagnosis proved expert union/coalescing was not the cause.

`LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS` establishes the correct target-side schedule:
1. canonical `q_len=1` attention sequentially per position;
2. seven positions progress layer-by-layer;
3. routes are collected for all positions at a layer;
4. each unique expert is loaded once and reused across assigned positions.

Result:
- hidden/KV/router/final logits/token decisions bitwise exact;
- 1,205 unique layer-expert instances;
- 431,519,451 B external expert bytes/verified position;
- B7 wall 10.8152 s sequential -> 6.5430 s wavefront;
- 1.653x measured speedup;
- peak MLX ~985 MB;
- peak RSS ~1.004 GB;
- swap delta 0;
- no expert leak.

This completes both target-side prerequisites for a learned DFlash port: target taps and exact B7 verification.

## Next — minimal learned drafter port

Checkpoint: `LOOM_DFLASH_DRAFTER_PORT_001`.

Scope:
- port/instantiate only the exact learned DFlash drafter in MLX;
- map publisher BF16 weights exactly;
- feed frozen target taps using the proven contract;
- reproduce fusion + five draft layers + draft/block logits;
- compare with an independent/source reference where runnable;
- measure actual M1 resident/workspace memory;
- no speculative-generation integration yet.

Required gate:
- tensor mapping complete;
- deterministic reference parity at justified exact/tolerance level;
- no NaN/Inf;
- memory pressure PASS / no unexpected swap;
- target/external-expert runtime remains untouched.

If the drafter port passes, integrate it with the exact B7 wavefront verifier and measure real acceptance length and accepted-token economics.

## After drafter PASS

1. DFlash speculative loop + B7 wavefront verifier;
2. measure acceptance length and target verification steps/output token;
3. measure unique external expert bytes/accepted token and sustained generation tok/s;
4. reconsider only small complementary cache/storage from measured block economics;
5. capability/coding benchmark;
6. context/stability;
7. if speed remains insufficient: route prediction/prefetch, finer-grained sparsity or LOOM-native co-design;
8. behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only the active work-package delta. Pi performs local code/tests/evidence; ChatGPT owns Git/HANDOFF/ROADMAP.
