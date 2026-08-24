# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_BLOCK_VERIFIER_001_FAIL_GATE`
Strategic next: `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Architecture/runtime feasibility — PROVEN

The external-expert Qwen3-30B-A3B target already:
- fits structurally on M1 8 GB with an ~819-MB resident backbone;
- executes all 48 layers with exact final logits;
- performs real autoregressive generation;
- benefits materially from expert-major disk access;
- remains blocked from higher practical rates by external expert traffic and fixed single-token cost.

Large 4-GiB raw expert caching is rejected because it caused +2.41 GiB swap and severe slowdown despite ~80.9% real hit rate.

Canonical values and stable invariants live in `/AGENTS.md`.

## B — DFlash static + target interface

Exact-target DFlash candidate:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Static audit:
- BF16 draft ~1.2685 GiB;
- 5 layers, proposals=7;
- target taps `[1,12,23,34,45]`;
- static M1 8-GB fit plausible;
- custom LOOM/MLX integration required.

`LOOM_DFLASH_TARGET_INTERFACE_001_PASS` proves the five taps can be exposed with target router/logits/tokens bitwise exact, small memory overhead and zero swap/expert leak.

## C — Multi-position block verifier — FAIL AT B7

`LOOM_DFLASH_BLOCK_VERIFIER_001_FAIL_GATE`.

Report: `research/architecture/loom-30b-dflash-block-verifier-001-result.md`.

Results:
- B2 exact PASS;
- B4 exact PASS;
- B7 token decisions + selected router IDs PASS, but logits/router logits/KV not bitwise exact.

B7:
- max final-logit diff 0.0214348;
- max router-logit diff 0.00273609;
- KV reaches correct length 50 but state differs;
- peak MLX ~960 MB;
- swap delta 0;
- no expert leak.

Block routing economics are promising:
- B2 external union bytes/position: 828,481,536 B;
- B4: 612,900,864 B;
- B7: 452,647,790 B.

Wall comparison:
- B2 sequential/block 3.187 / 2.825 s;
- B4 5.898 / 4.414 s;
- B7 9.927 / 6.317 s.

These performance gains are not promoted until B7 correctness is resolved.

## D — B7 parity diagnosis — NEXT

Checkpoint: `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001`.

Goal: locate the first numerical divergence rather than relaxing the gate.

Required controlled comparison:
1. sequential teacher-forced B7 reference;
2. B7 causal block with no union-coalesced expert optimization;
3. B7 union-coalesced expert path.

Compare each position/layer at boundaries:
- post-attention + KV;
- router logits/IDs/weights;
- MoE output;
- final block hidden state/logits.

Classify first divergence as attention/KV, router, expert batching, aggregation ordering or another verified cause.

If normal B7 block already differs, diagnose batched causal attention/KV execution. If only coalesced B7 differs, repair the coalesced MoE path. Do not integrate DFlash before this is resolved.

If localization shows unavoidable deterministic floating-order differences from an otherwise mathematically equivalent batched kernel, a numerical-tolerance gate may be considered only after repeated stability evidence and token/router-decision invariance; do not assume that outcome in advance.

## E — DFlash integration gate

DFlash drafter implementation remains blocked until B7 verification becomes scientifically acceptable.

After that:
- port minimal exact-target drafter;
- measure actual resident/workspace memory;
- measure acceptance length;
- measure unique external expert bytes per accepted token;
- measure sustained generation tok/s;
- require memory pressure and deterministic target correctness.

## F — Later promotion path

1. `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001`.
2. B7 verifier repair/revalidation if justified.
3. Minimal DFlash port.
4. Sustained real generation benchmark.
5. Capability/coding benchmark.
6. Context scaling and stability.
7. If speed remains insufficient: route prediction/prefetch, finer-grained sparsity or LOOM-native model/system co-design.
8. Behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only the active delta, exact inputs, gates, evidence and concise return fields. Pi remains local execution only; ChatGPT owns Git/HANDOFF/ROADMAP.
