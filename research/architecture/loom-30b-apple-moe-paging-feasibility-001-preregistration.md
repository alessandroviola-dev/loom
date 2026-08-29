# LOOM 30B Apple MoE Paging Feasibility 001 — Preregistration

Date: 2026-08-29
Status: **PREREGISTERED / NOT YET RUN**

## Priority pivot

Pause the validator/guided-repair research track after `LOOM_VERIFY_RULE_VALIDATOR_HARDENING_GO`.

New active priority: determine whether the Qwen3-30B-A3B DEEP tier can move from the current ~1.4 tok/s custom MLX path toward an Apple-Silicon GGUF/Metal expert-paging path inspired by recent public work.

This checkpoint is feasibility only. **No model download and no model inference.**

## External mechanism under test

Primary source target:
- repo: `kisasexypantera94/llama.cpp`
- branch: `moe-expert-residency`
- frozen commit: `41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

The source adds Metal MoE expert-residency controls including `--moe-n-slots` and `--moe-n-layers`, with LRU expert slots and disk-backed expert loading.

Reference evidence only, not a performance claim for this Mac:
- public PoC reports Qwen3-30B-A3B Q6_K on M1 Pro 16GB at 13 tok/s after warmup;
- Potato OS reports Qwen3-30B-A3B on Pi 5 8GB + SSD around 8–9 tok/s using low-bpw GGUF and an optimized llama-family runtime;
- `ik_llama.cpp` is a useful quant/kernel reference but is **not** assumed as the Mac execution backend because its maintainers do not treat Metal as a fully performant supported backend.

## Candidate model family for later Stage 1

Do NOT download in this checkpoint.

Inspect compatibility for these two ByteShape candidates only:

1. KQ candidate:
`byteshape/Qwen3-30B-A3B-Instruct-2507-GGUF`
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
remote size ~12.4 GB; published normalized quality 97.97%; SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

2. IQ candidate:
`Qwen3-30B-A3B-Instruct-2507-IQ3_S-3.29bpw.gguf`
remote size ~12.5 GB; published normalized GPU score 97.35%; SHA256 `b8770ce5b81cb47fbdfc75a00fae220297955ef58697411888c1f3dc30a2e230`.

No candidate is selected yet. Stage 1 may authorize exactly one after this feasibility result.

## Allowed network

Network is authorized only to fetch/clone source code and immutable Git metadata for the frozen PoC source.

Forbidden:
- Hugging Face/model downloads;
- package-manager installs/upgrades;
- Python package mutation;
- OS/system mutation;
- changing the existing LOOM 8B/30B runtimes;
- inference.

Use already-installed Apple developer tools/CMake/compilers only. If a required build dependency is absent, report it; do not install it.

## Source scope

Create exactly one new tracked experimental harness:
`scripts/loom_30b_apple_moe_paging_feasibility_001.py`

External source/build artifacts must live under the results-local evidence tree, never inside tracked production/runtime directories.

Evidence root:
`results-local/research/30b-apple-moe-paging-feasibility-001/<timestamp>/`

## Required checks

### A. Host/provenance
Persist:
- Apple chip identity;
- physical RAM;
- macOS version;
- architecture;
- free disk;
- current swap/memory state;
- Xcode/clang/cmake versions if present.

Expected host: Apple M1, 8GB-class unified memory.

### B. Frozen source
Fetch the PoC repo and checkout exactly:
`41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Persist remote URL, HEAD, clean status and source diff status.
No source patching.

### C. Native Metal build
Configure/build only the minimum CLI target needed for feasibility.
Metal must be enabled/detected.
No source modifications or dependency installs.

Persist full configure/build commands, stdout/stderr, elapsed wall and binary SHA.

### D. Feature verification
From the built binary prove:
- `--moe-n-slots` exists;
- `--moe-n-layers` exists;
- `--no-mmap` exists;
- `--no-warmup` exists;
- Metal/Apple device is visible through the binary/device listing or equivalent startup diagnostics.

Also source-inspect and persist evidence for the expected expert-paging mechanism: expert slot cache/LRU, disk read path (`pread` or equivalent), and Metal synchronization/interceptor path.

### E. Local storage/I/O readiness
Do not write a synthetic multi-GB benchmark file.
Use an already-existing large local LOOM model/expert artifact, if available, for a bounded read-only storage throughput probe. If no suitable local file exists, record `NOT_MEASURED` rather than creating/downloading one.

Record filesystem, source path/size, read method, bytes sampled and observed throughput. Treat this as diagnostic only, not a cross-platform performance claim.

### F. Memory projection
Using frozen known Qwen3-30B-A3B geometry and candidate sizes, estimate conservative working-memory envelopes for slot counts `8, 16, 24, 32`.

Separate at least:
- non-expert/resident model data;
- expert slot pool estimate;
- KV/context allowance;
- runtime/Metal overhead allowance;
- OS safety headroom.

State assumptions explicitly. Do not claim measured residency.

### G. Candidate compatibility decision
Without downloading a GGUF, inspect source quant/backend support and classify each candidate:
- `COMPATIBLE_FOR_STAGE1`
- `UNCERTAIN`
- `INCOMPATIBLE`

Prefer no candidate purely from marketing throughput. Selection must be based on source/backend compatibility, quality target and 8GB memory projection.

## Frozen GO gate

`LOOM_30B_APPLE_MOE_PAGING_FEASIBILITY_GO` only if all are true:
1. exact frozen PoC commit verified;
2. native build succeeds without source patch/package mutation;
3. built runtime exposes both MoE slot/layer controls;
4. Metal/Apple device path is detected;
5. source evidence confirms disk-backed expert paging + bounded slot cache + Metal synchronization path;
6. at least one of the two frozen ByteShape candidates is not source-incompatible;
7. free storage is sufficient for one ~12.5GB candidate plus >=8GB safety margin;
8. at least one conservative slot-count projection is plausible on the 8GB host while retaining OS safety headroom;
9. zero model download/inference and zero forbidden mutation.

Otherwise:
- deterministic incompatibility -> `LOOM_30B_APPLE_MOE_PAGING_FEASIBILITY_NO_GO`;
- instrumentation/build evidence invalid -> `LOOM_30B_APPLE_MOE_PAGING_FEASIBILITY_MECHANICAL_NO_GO`.

## Required return

Return:
- classification;
- host facts;
- frozen source provenance;
- build commands/result/binary SHA;
- exact feature/device evidence;
- source evidence for LRU/pread/Metal synchronization;
- local read-only I/O probe result or NOT_MEASURED;
- slot-count memory projection table;
- compatibility classification for KQ-3.25 and IQ-3.29;
- recommended single Stage-1 candidate, if GO, with reasoning;
- proof no model download/inference/package/system mutation;
- evidence path.

No Git commit/push.

STOP.
