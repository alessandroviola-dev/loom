# LOOM — Active Handoff

Last updated: 2026-08-23
Status: ACTIVE — 30B MoE external-expert prototype
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_MOE_FEASIBILITY_001_STATIC_CONDITIONAL`
Next: `LOOM_30B_MOE_EXPERT_PACK_001`

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

Dense partial-residency research established exact streaming and lifecycle rules but naïve dense streaming remains too slow for the final ~30B architecture.

## 30B MoE target

Local model: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`
Public identity: `Qwen/Qwen3-30B-A3B-MLX-4bit`

Local static audit recovered:
- `Qwen3MoeForCausalLM`
- 48 layers
- hidden 2048
- 32 Q heads / 4 KV heads / head_dim 128
- vocab 151936
- 128 routed experts/layer
- top-k 8
- MoE intermediate 768
- no shared-expert tensors
- MLX 4-bit, group size 128

Model payload: 16,220,499,968 B (15.106518 GiB).

## LOOM_30B_MOE_FEASIBILITY_001_STATIC — CONDITIONAL

Canonical report: `research/moe/loom-30b-moe-feasibility-001-static-result.md`.

Mandatory/non-routed stored set: 819,015,680 B = 0.762768 GiB.
Routed expert bank: 15,401,484,288 B = 14.343750 GiB.
One routed expert: 2,506,752 B = 2.390625 MiB.
Top-k 8 experts in one layer: 20,054,016 B = 19.125 MiB.
Zero-cache selected-expert traffic across all 48 layers: 962,592,768 B = 918 MiB/token.

Static model-budget examples after reserving the mandatory set:
- 4.0 GiB: 1,386 experts / 22.559% of expert bank
- 5.0 GiB: 1,814 experts / 29.525%
- 6.0 GiB: 2,243 experts / 36.507%

Zero-cache bandwidth lower bound:
- 1 tok/s: 962.593 MB/s
- 2 tok/s: 1,925.186 MB/s
- 5 tok/s: 4,812.964 MB/s
- 10 tok/s: 9,625.928 MB/s

At 2 GB/s, 5 tok/s still requires 58.446% external-traffic reduction/cache-hit-equivalent. This is an arithmetic requirement only; routing locality/popularity has not yet been measured.

## Critical storage-layout finding

Current safetensors are expert-bank-major, not complete-expert-major. Each routed expert consists of 9 discontiguous tensor slices. 93.75% of experts are contained in one shard; layers 15, 31 and 47 cross two shards.

Median useful expert bytes: 2,506,752 B.
Median summed contiguous span required by the current arrangement: 3,132,327,424 B.
Median useful/span efficiency: 0.080028%.

Verdict: `REPACK_RECOMMENDED`.

This means the immediate blocker is the physical artifact layout, not the basic MoE parameter split. Exact expert byte slices are recoverable, but direct disk streaming from the current layout would cause excessive fragmented/range I/O.

## Strongest current conclusion

Qwen3-30B-A3B remains scientifically viable as LOOM's first ~30B target. Only 0.763 GiB of stored tensors are mandatory/non-routed; 14.344 GiB are routed experts. A layout-aware expert-major representation should be tested before any full external-expert runtime.

The remaining decisive unknown is not static anatomy but empirical reuse/locality: can routing/cache behavior reduce the 918 MiB/token zero-cache demand enough for practical speed on M1 8 GB?

## Exact next checkpoint — LOOM_30B_MOE_EXPERT_PACK_001

Do not attempt full-model generation yet.

1. build a deterministic LOOM expert-major packed representation from the local safetensors without modifying originals;
2. first validate one layer / a small controlled subset before optionally packing the full bank;
3. prove byte-exact reconstruction of selected expert tensors against source slices;
4. measure packed expert range count and read amplification;
5. benchmark sequential/random packed expert read throughput separately from model compute;
6. keep shared tensors untouched;
7. if packing/access passes, proceed to a one-layer external-expert execution prototype and only then to a minimal end-to-end routed path.

Do not assume expert cache hit rate or popularity until real routing traces exist.

## Provenance warning

Pi's static evidence directory was reported as `results-local/moe/feasibility-001-static/20260330T000001Z/`, which does not match the actual date 2026-08-23. Treat it as a timestamp/provenance anomaly; future evidence runs must use actual runtime UTC timestamps.

## Storage state

Historical Qwen3-4B-GGUF, Qwen3-8B-GGUF and Qwen3-8B-4bit MLX are archived externally. Canonical Qwen3-8B-3bit remains local. Qwen3-30B-A3B-MLX-4bit is local. Internal free space after 30B download: ~64 GiB.

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
