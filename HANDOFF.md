# LOOM — Active Handoff

Last updated: 2026-08-23
Status: ACTIVE — 30B MoE external-expert storage/runtime research
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_EXPERT_PACK_001_PASS`
Next: `LOOM_30B_MOE_PHYSICAL_IO_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Every final promoted LOOM-produced model must eventually pass validated decensoring/behavioral-freedom preservation using Heretic or a LOOM-native independent equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.
ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical dense baseline

Qwen3-8B full parameter count; affine 3-bit/group64; BF16 KV; MLX/mlx-metal 0.31.2; mlx-lm 0.31.3; thinking disabled.

REALGEN001 historical real M1 generation: 13.184615357 tok/s; E2E 12.046861457 tok/s.

CAPABILITY001: practical-agent 1/11 = 9.09%; Coding Benchmark 45/100; critical failures 0.

Exact partial residency works, but naïve synchronous dense layer streaming is too slow. Retained promoted cleanup improvements:
- shared intermediate cleanup consolidation: +25.206% generation / -35.678 ms/token;
- streamed-layer post-forward cleanup defer: +17.522% generation / -21.308 ms/token.

Select-time GC removal is NO-GO and shared-stage cleanup/eval micro-axes are considered exhausted absent new evidence.

## STREAMED-BLOCK-REUSE-AUDIT001 — COMPLETE

Report: `research/memory/streamed-block-reuse-audit-001-result.md`.

A weightless quantized Qwen3 topology shell is mechanically possible, but current strict MLX loading requires existing parameter leaves. Construction-only reuse cannot be isolated without changing binding semantics. This dense micro-route is closed on the present runtime.

## 30B target

Local model:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Exact local static audit:
- architecture: Qwen3MoeForCausalLM;
- 48 MoE layers;
- hidden size 2048;
- 128 routed experts/layer;
- top-k 8;
- MoE intermediate 768;
- MLX 4-bit/group128;
- total stored tensor payload: 16,220,499,968 B;
- mandatory/non-routed stored bytes: 819,015,680 B (0.763 GiB);
- routed expert bank: 15,401,484,288 B (14.344 GiB);
- one routed expert: 2,506,752 B (2.390625 MiB);
- top-k expert bytes/layer: 20,054,016 B;
- zero-cache useful expert traffic/token: 962,592,768 B (918 MiB).

Static result: `LOOM_30B_MOE_FEASIBILITY_001_STATIC_CONDITIONAL`.
Report: `research/moe/loom-30b-moe-feasibility-001-result.md`.

Core structural finding: the full model is genuinely compatible with sparse external-expert research because the mandatory non-expert set is only ~0.763 GiB while ~14.344 GiB lives in routed experts.

## EXPERT-PACK-001 — PASS

Report: `research/moe/loom-30b-moe-expert-pack-001-result.md`.
Raw evidence: `results-local/moe/expert-pack-001/20260823T204053Z/`.

Prototype packed all 128 experts from layers 0 and 15, covering both an ordinary layer and a shard-boundary layer.

Validated:
- 256 experts;
- 641,728,512 B useful payload;
- 2,304 components;
- zero hash/byte/metadata mismatches.

Storage geometry improvement:
- source: 9 exact data ranges/expert;
- packed: 1 contiguous 2,506,752 B range/expert;
- top-k=8: 72 -> 8 data reads;
- byte amplification remains 1.0x;
- packed useful/span efficiency: 100%.

This proves lossless expert-major storage and independently addressable routed experts.

## Critical I/O caveat

The same run reported ~14–15 GB/s range-read throughput and ~66 ms zero-cache 48-layer I/O-only extrapolation. These numbers are NOT canonical physical-SSD evidence.

The benchmark used `os.pread` and Darwin `F_NOCACHE`, but tested files had already been created/read in the workflow. Throughput far exceeds plausible physical storage throughput and therefore indicates filesystem/page-cache or memory-resident service. `F_NOCACHE` alone does not prove that pre-existing resident pages were absent.

Therefore:
- pack correctness: PASS;
- 9->1 read geometry: PASS;
- physical SSD throughput: UNVALIDATED;
- ~66 ms/token storage extrapolation: NON-CANONICAL.

Do not build the complete 14.3 GiB expert pack solely on those throughput numbers.

## Exact next step

`LOOM_30B_MOE_PHYSICAL_IO_001`

Goal: establish defensible physical/cold-ish storage throughput and random-range latency on the reference M1 internal SSD without sudo and without confusing RAM/page-cache bandwidth with storage bandwidth.

Requirements:
1. benchmark a data set/access working set larger than available RAM or otherwise prove cache bypass/absence;
2. use deterministic expert-sized 2,506,752 B reads and top-k-sized workloads;
3. disable read-ahead where possible and document exact Darwin APIs;
4. distinguish sequential throughput, random expert-sized access and token-like 384-expert access;
5. record memory pressure/free RAM and storage state;
6. treat any result above plausible hardware limits as invalid/cache-contaminated;
7. no generation and no full model load.

The result decides whether the next action is full expert-bank repack, one-layer external-expert execution, or stronger cache/amortization/storage redesign.

## Storage state

Historical Qwen3-4B-GGUF, Qwen3-8B-GGUF and Qwen3-8B-4bit MLX were moved to external archive. Canonical Qwen3-8B-3bit remains local. Qwen3-30B-A3B-MLX-4bit is local on the internal SSD. Expert-pack prototype uses ~612 MiB plus metadata. Free space observed in the pack run: 63.251 GiB.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
