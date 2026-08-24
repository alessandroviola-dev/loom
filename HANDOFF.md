# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — exact B7 target verification proven; minimal learned DFlash port next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`
Next core checkpoint: `LOOM_DFLASH_DRAFTER_PORT_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while balancing memory, speed, capability and later behavioral-freedom validation.

Stable target anatomy and proven invariants live in `/AGENTS.md`. Pi uses compact work packages; ChatGPT owns Git/HANDOFF/ROADMAP.

## Established runtime

- Qwen3-30B-A3B external-expert execution is bitwise exact across all 48 layers.
- Shared resident backbone: 819,015,680 B; routed bank stays external.
- Real greedy generation works on M1 8 GB.
- Expert-major disk layout materially improves decode.
- 4-GiB raw RAM cache is rejected despite real ~80.9% reuse because it causes severe swap/memory pressure.

## DFlash candidate

`RedHatAI/Qwen3-30B-A3B-speculator.dflash`

Static audit:
- BF16 weights ~1.2685 GiB;
- 5 draft layers;
- proposals=7;
- target taps `[1,12,23,34,45]`;
- static M1/8-GB fit plausible;
- custom LOOM/MLX port required.

Target interface is proven exact and low-overhead.

## B7 verification chain

The original batched B7 verifier failed exactness because multi-position attention introduced a tiny numerical difference at layer 0. Diagnosis proved union-coalesced MoE was not responsible.

`LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS` solves this by preserving canonical `q_len=1` attention sequentially per position while moving the seven positions through the model layer-by-layer and reusing each unique expert within the layer.

Result:
- all layer hidden states bitwise exact;
- KV bitwise exact;
- router IDs/weights bitwise exact;
- final logits/token decisions bitwise exact;
- first divergence: none;
- 1,205 unique `(layer, expert)` instances;
- 431,519,451 B useful external expert bytes/verified position;
- sequential B7 wall 10.8152 s;
- wavefront wall 6.5430 s;
- speedup 1.653x;
- peak MLX 985,002,536 B;
- peak RSS 1,003,978,752 B;
- swap delta 0;
- ownership PASS, zero routed-expert leak.

Report: `research/architecture/loom-dflash-b7-wavefront-verifier-001-result.md`.
Raw evidence: `results-local/research/dflash-b7-wavefront-verifier-001/20260824T111511Z/`.

## Exact next step — `LOOM_DFLASH_DRAFTER_PORT_001`

Target-side prerequisites are complete. The next checkpoint should port only the learned DFlash drafter into MLX and establish reference parity/memory behavior using frozen target taps.

Do not yet build the speculative-generation loop. First prove:
1. exact architecture/tensor mapping from publisher weights;
2. correct fusion of the five target taps;
3. correct five-layer draft forward/block logits versus an independent/source reference where runnable;
4. real BF16 resident/workspace memory on M1 8 GB;
5. no target/expert lifecycle regression.

Only after drafter parity passes should LOOM combine it with the exact B7 wavefront verifier and measure acceptance length / sustained tok/s.

## Later order

1. minimal DFlash drafter port/parity;
2. integrate drafter + exact wavefront verifier;
3. measure actual acceptance length, external expert bytes/accepted token and sustained generation speed;
4. capability/coding benchmark after practical speed improves;
5. context/stability;
6. behavioral decensoring validation before final promotion.
