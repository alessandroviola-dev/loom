# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — full 30B generation proven; DFlash target taps proven; B7 block verifier parity unresolved
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_BLOCK_VERIFIER_001_FAIL_GATE`
Next core checkpoint: `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a LOOM-native independent equivalent: `research/behavior/decensoring-requirement-v1.md`.

## Operating split / token-efficient protocol

Pi performs local code/runtime inspection, implementation, tests and concise local evidence. ChatGPT owns scientific direction, Git/GitHub, HANDOFF/ROADMAP and project continuity.

Root `/AGENTS.md` is Pi's persistent context. Pi prompts should normally contain only the active work-package delta.

## Canonical target/runtime state

Stable target anatomy and proven invariants live in `/AGENTS.md`.

Key established chain:
- external serial-expert Qwen3-30B-A3B execution is bitwise exact;
- complete 819-MB shared backbone resides on M1 8 GB;
- full 48-layer target forward/logits are exact;
- first real greedy generation works;
- packed expert-major access improves decode materially (~1.08 decode-equivalent tok/s vs ~0.65 source baseline);
- large 4-GiB raw RAM cache is rejected: ~80.9% hit was real but caused +2.41 GiB swap and severe slowdown;
- current single-token fixed-cost ceiling remains ~2.066 tok/s even with perfect expert-cache hits.

## DFlash exact-target status

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Static audit:
- BF16 safetensors 1,362,042,120 B (~1.2685 GiB);
- 5 draft layers, H=2048, proposals=7;
- target taps `[1,12,23,34,45]`;
- static M1/8-GB memory fit plausible;
- custom LOOM/MLX integration required.

`LOOM_DFLASH_TARGET_INTERFACE_001_PASS`:
- exact target taps exposed as 1-based post-block outputs;
- prefill `[1,28,2048]`, decode `[1,1,2048]`, float32;
- router/logits/tokens bitwise exact;
- +18,612,224 B MLX peak only;
- swap delta 0; no expert leak.

## DFLASH-BLOCK-VERIFIER-001 — FAIL GATE

Report: `research/architecture/loom-30b-dflash-block-verifier-001-result.md`.
Raw evidence: `results-local/research/dflash-block-verifier-001/20260824T103943Z/`.

Sequential teacher-forced vs multi-position target verification:
- B2: PASS exact;
- B4: PASS exact;
- B7: FAIL exactness gate.

B7 still preserves:
- token decisions;
- selected router IDs;
- correct BF16 KV length advance to 50;
- memory pressure PASS;
- zero routed-expert leak.

But B7 numerical state differs:
- max final-logit diff: 0.0214348;
- max router-logit diff: 0.00273609;
- KV state not bitwise exact.

Routing union / external useful bytes per verified position:
- B2: 661 unique experts / 828,481,536 B;
- B4: 978 / 612,900,864 B;
- B7: 1,264 / 452,647,790 B.

Sequential vs block wall:
- B2: 3.187 / 2.825 s;
- B4: 5.898 / 4.414 s;
- B7: 9.927 / 6.317 s.

Memory:
- peak MLX 960,393,224 B;
- sampled RSS 758,333,440 B;
- swap delta 0 MiB;
- ownership PASS.

Interpretation: the block approach remains structurally promising and exact through B4, but B7 is the DFlash-critical proposal length. Do not relax the gate or integrate the drafter while the B7 divergence is unexplained.

## Exact next step — `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001`

Isolate the first B7 divergence with controlled variants:
1. sequential teacher-forced reference;
2. B7 causal block using normal per-position/per-expert MoE semantics without union coalescing;
3. B7 union-coalesced MoE path.

Compare layer-by-layer and position-by-position after attention/KV, router, MoE and full block. Determine whether the first divergence is caused by:
- causal attention/KV batched execution;
- router arithmetic;
- expert batching/union coalescing;
- aggregation order;
- another identified runtime boundary.

Do not redefine exactness until the source of numerical divergence is known. If a mathematically equivalent batched kernel is inherently non-bitwise, quantify deterministic tolerance only after localization and repeated stability evidence.

## Later order

1. `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001`.
2. Repair/revalidate B7 verifier if mechanical cause is found.
3. Minimal DFlash drafter port only after B7 verification is scientifically acceptable.
4. Measure acceptance length, expert bytes/accepted token, sustained tok/s and memory pressure.
5. Capability/coding benchmark after practical speed improves.
6. Behavioral decensoring validation before final promotion.

## Local-only warning

Experimental scripts/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
