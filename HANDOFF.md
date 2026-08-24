# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — full 30B generation proven; 4-GiB raw cache rejected; DFlash target interface proven; block verifier next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_TARGET_INTERFACE_001_PASS`
Next core checkpoint: `LOOM_30B_DFLASH_BLOCK_VERIFIER_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring/behavioral-freedom preservation using Heretic or a LOOM-native independent equivalent: `research/behavior/decensoring-requirement-v1.md`.

## Operating split / token-efficient Pi protocol

Pi: local code/runtime inspection, implementation, tests/benchmarks and concise local evidence.
ChatGPT: scientific direction, experiment design/review, GitHub synchronization, `HANDOFF.md`, `ROADMAP.md` and project continuity.

Local override: Pi does not perform Git/GitHub administration or edit HANDOFF/ROADMAP unless explicitly overridden.

Root `/AGENTS.md` is the persistent Pi context. Future prompts are compact work packages; do not restate stable history. `.qwen/settings.json` uses a 4096-token local-agent context.

## Canonical target

Local model: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`.

- 48 MoE layers; 128 routed experts/layer; top-k 8;
- full tensor payload 16,220,499,968 B;
- resident non-routed target 819,015,680 B;
- external routed bank 15,401,484,288 B;
- one expert 2,506,752 B;
- zero-cache expert traffic 962,592,768 B/token;
- BF16 KV 98,304 B/token.

## Proven runtime chain

- `EXPERT_PACK_001_PASS`: lossless expert-major `9 -> 1` storage geometry.
- `PHYSICAL_IO_002_CONDITIONAL`: device-verified random expert ~1.89 GB/s; zero-cache storage-only floor ~0.4816 s/token.
- `ONE_LAYER_EXTERNAL_EXPERT_001_PASS`: bitwise-exact external expert layer, one expert live at a time.
- `SHARED_BACKBONE_RESIDENCY_001_PASS`: complete 819-MB shared target resident.
- `FULL_FORWARD_EXTERNAL_001_CONDITIONAL`: all 48 layers + final logits exact.
- `FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS`: `GC_END_ONLY` production-like full forward 1.641729 s.
- `FIRST_GREEDY_GENERATION_001_PASS`: first real generation, source zero-cache decode ~0.647 tok/s.
- `TRACE_PACK_DECODE_AB_001_PASS`: packed decode-equivalent ~1.080 tok/s; expert-read wall -59.27%; exact output.
- `ROUTING_CACHE_TRACE_001_PASS`: temporal expert reuse is real; perfect single-token cache ceiling ~2.066 tok/s.
- `REAL_RAW_CACHE_001_MEMORY_FAIL`: real 4-GiB raw LRU hit 80.9056% but +2410.56 MiB swap and decode ~0.205 tok/s. Do not reuse this design.

## DFlash static audit

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001_CONDITIONAL_STATIC_MEMORY_FIT__INTEGRATION_BLOCKED`.

Report: `research/architecture/loom-30b-dflash-speculator-static-001-result.md`.

Exact-target candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

- BF16 safetensors: 1,362,042,120 B = 1.268501 GiB;
- 680,813,824 learned weight elements;
- 5 draft layers, H=2048;
- block=8 / proposals=7;
- target taps `[1,12,23,34,45]`;
- static M1/8-GB fit plausible;
- no native LOOM/MLX integration path.

Drafter integration remains blocked until target-side prerequisites are proven.

## DFLASH-TARGET-INTERFACE-001 — PASS

Report: `research/architecture/loom-30b-dflash-target-interface-001-result.md`.
Raw evidence: `results-local/research/dflash-target-interface-001/20260824T101801Z/`.

The current external-expert target can expose the exact DFlash taps without changing target behavior.

Tap contract:
- IDs `[1,12,23,34,45]` are 1-based post-block outputs (`layers[i-1]`);
- prefill: `[1,28,2048]`;
- decode: `[1,1,2048]`;
- dtype: float32;
- references released before next forward.

Correctness:
- router bitwise exact;
- final logits bitwise exact;
- token sequence `[19,151645]` exact;
- routed expert ownership remains zero.

Memory:
- logical tap bytes: 1,146,880 B prefill / 40,960 B decode;
- MLX peak baseline/taps: 881,332,232 / 899,944,456 B;
- delta +18,612,224 B;
- RSS high-water unchanged at 965,066,752 B;
- swap delta 0.

Gate: PASS.

## Exact next step — `LOOM_30B_DFLASH_BLOCK_VERIFIER_001`

Do not load/integrate DFlash weights yet.

Prove the second target-side prerequisite independently of the learned drafter:
1. recover a real deterministic continuation of at least 7 tokens from existing trace evidence;
2. compare sequential teacher-forced target verification against one multi-position target block for B=2,4,7;
3. establish exact candidate/logit alignment, causal mask and KV semantics rather than assuming them;
4. require token/logit parity at each verified position within justified numerical tolerance;
5. preserve external-expert ownership and memory safety;
6. record layer-local routed expert unions and useful external bytes per verified position;
7. where safe, load each unique `(layer, expert)` once per block to quantify real union amortization separately from the sequential control;
8. measure wall time, MLX/RSS/swap and distinguish semantics PASS from performance gain.

If block verification fails, DFlash integration remains blocked. If it passes, the target-side prerequisites are complete and a minimal DFlash port becomes scientifically justified.

## Strategic interpretation

DFlash is not a memory-fit mechanism. Its potential value is escaping the ~2.066 tok/s single-token fixed-cost ceiling through multiple accepted tokens per target verification and expert-union amortization.

Real routing traces already show mean union bytes/position decline with block length, but those values remain structural until the block verifier measures them on the real runtime.

## Later order

1. `LOOM_30B_DFLASH_BLOCK_VERIFIER_001`.
2. Minimal DFlash drafter port only if verifier PASS.
3. Measure real acceptance length, unique expert bytes/accepted token, workspace and sustained generation speed.
4. Revisit smaller complementary cache/storage only if block economics justify it.
5. Capability/coding benchmark after practical speed improves.
6. Behavioral decensoring validation before final promotion.

## Local-only warning

Experimental scripts/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
