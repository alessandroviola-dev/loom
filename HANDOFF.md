# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — full 30B generation proven; DFlash taps proven; B7 batched attention identified as parity blocker
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001_FAIL_GATE`
Next core checkpoint: `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while balancing memory, speed, capability and later behavioral-freedom validation.

Stable target anatomy and proven invariants live in `/AGENTS.md`. Pi uses compact work packages; ChatGPT owns Git/HANDOFF/ROADMAP.

## Established runtime

- Qwen3-30B-A3B external-expert execution is bitwise exact across all 48 layers.
- Shared resident backbone: 819,015,680 B; routed bank stays external.
- Real greedy generation works on M1 8 GB.
- Expert-major disk layout materially improves decode (~1.08 decode-equivalent tok/s vs ~0.65 source baseline).
- 4-GiB raw RAM cache is rejected: ~80.9% hit but +2.41 GiB swap and severe slowdown.

## DFlash status

Exact-target candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Static:
- BF16 draft ~1.2685 GiB;
- 5 draft layers;
- proposals=7;
- target taps `[1,12,23,34,45]`;
- static M1/8GB fit plausible.

Target interface PASS:
- taps exposed as 1-based post-block outputs;
- router/logits/tokens remain bitwise exact;
- small memory overhead; swap delta 0.

## Block verifier result

`LOOM_DFLASH_BLOCK_VERIFIER_001_FAIL_GATE`:
- B2 exact PASS;
- B4 exact PASS;
- B7 token decisions/router IDs stable but numerical state not exact;
- B7 union economics: 1,264 unique layer-expert instances, 452,647,790 B/verified position;
- wall: 6.317 s block vs 9.927 s sequential;
- memory/ownership safe.

## B7 parity diagnosis

Report: `research/architecture/loom-dflash-block-b7-parity-diag-001-result.md`.
Raw evidence: `results-local/research/dflash-block-b7-parity-diag-001/20260824T110012Z/`.

Controlled paths:
- A sequential teacher-forced reference;
- B causal B7 block without union-coalesced MoE;
- C B7 union-coalesced MoE.

Result:
- first A/B and A/C divergence: layer 0, position 0, `post_attention_hidden`;
- max/mean initial error: `1.4901161e-08 / 2.6425653e-09`;
- KV K/V still bitwise exact there;
- A/B FAIL, A/C FAIL;
- B/C PASS across all 336 layer/position/stage comparisons;
- final A/B logits max/mean error: `0.021434784 / 0.001928339`;
- swap delta 0; no expert leak.

Conclusion: union-coalesced MoE is not the problem. The divergence comes from B7 batched attention numerics and then cascades through the target. Do not relax the gate or integrate DFlash yet.

## Exact next step — B7 wavefront verifier

`LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001`.

Test a correctness-preserving execution order:
1. keep canonical single-position (`q_len=1`) attention for each of the 7 positions so attention/KV arithmetic matches sequential decode;
2. operate layer-by-layer across the 7 positions;
3. after all 7 post-attention states/routes are known for a layer, load each unique `(layer,expert)` once;
4. reuse that expert across every assigned position, while preserving per-position expert math/aggregation order;
5. compare against the sequential teacher-forced B7 reference bitwise at every layer and final logits;
6. measure unique expert bytes, wall, memory and ownership.

If this passes, LOOM gets exact B7 verification plus expert-I/O amortization without relying on the numerically different batched-attention kernel. That would complete the target-side prerequisite for a minimal DFlash port.

## Later order

1. B7 wavefront verifier.
2. Minimal DFlash drafter port only if exact B7 target verification passes.
3. Measure real acceptance length, unique expert bytes/accepted token, sustained tok/s and memory pressure.
4. Capability/coding benchmark after practical speed improves.
5. Behavioral decensoring validation before final promotion.
