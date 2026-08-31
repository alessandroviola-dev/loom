# LOOM_UNLOCKED_SPEED_UOPT_002_GO

Date: 2026-08-31
Branch: `research/unlocked-speed-001`
Classification: **GO**

UOPT-002 promotes the validated lossless expert-major I/O transform behind the
normal `unlocked` profile.  It clears both co-primary targets without changing
Qwen3 routing/top-k, model math, FAST, or the retained UOPT-001 source GGUF.

## Product operation

```text
scripts/loom-deep use unlocked
scripts/loom-deep start
```

selects the isolated UOPT-002 runtime, `-ub 4`, and the local sidecar
automatically.  `fast` remains the default and remains the unchanged WP4 / FAST
rollback path.  `scripts/loom-deep current` displays the selected runtime and,
for UNLOCKED, the sidecar binding.  `scripts/loom-uopt002-build-runtime`
rebuilds the isolated runtime from its pinned source and committed patch; it
never replaces `.loom/runtime/loom-llama-server`, the UOPT-001 rollback binary.

## Immutable local artifacts and provenance

The following artifacts are intentionally ignored by Git and reside on the
repository's internal-SSD volume, not `external archive`:

| Artifact | Local path | Size | SHA-256 |
|---|---|---:|---|
| UOPT-001 source GGUF / rollback source | `models/loom-deep-30b-unlocked.gguf` | 13,292,468,896 bytes | `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c` |
| UOPT-002 lossless expert-major sidecar | `models/unlocked-expert-major-v1.bin` | 12,457,082,880 bytes | `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e` |
| sidecar construction/verification manifest | `models/expert-major-manifest.json` | 55,215 bytes | `4e50683bf62592ef1e34fa20962457af698a030fb1f3db100600cd61286f08ed` |
| isolated patched runtime | `.loom/runtime/loom-uopt002/llama-server` | 49,984 bytes | `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b` |

The source GGUF hash was rechecked after promotion.  It is not mutated or
replaced.  The sidecar is a non-destructive, lossless concatenation of exactly
the 48 × 128 routed-expert payloads from that GGUF, ordered per expert as the
llama graph binds pools: `up`, `gate`, `down`.  Every one of the 18,432 source
components was re-read and compared with its sidecar bytes; the aggregate
payload SHA-256 on both sides was identical:
`4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`.
The local manifest records tensor offsets, strides, source hash/size, sidecar
hash/size, construction timing, and per-layer and whole-artifact verification.

`LOOM_EXPERT_MAJOR_SIDECAR` is set only for the `unlocked` launch.  The patched
runtime is built from `kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
with `patches/loom-uopt002-expert-major-sidecar.patch`
(SHA-256 `3aac3cf3043b11d5f78a7e25dc5b4edce7bdb9e1f8907cec1ce64a7d2132b775`).
The patch retains the existing router, active top-k, LRU/slot mapping and
Metal handoff.  On a miss it makes one `preadv` into the unchanged three pool
buffers rather than three source-GGUF reads.  It aborts on a malformed or
unreadable requested sidecar; it never silently falls back to source bytes.

`config/loom-deep-profiles.env` binds the product to relative paths under this
repository.  The launcher verifies the sidecar and its runtime-library
directory before starting; it supplies the isolated local library directory
via `DYLD_LIBRARY_PATH`.  Final listener/FD inspection confirms normal
inference opens only repository-local internal-SSD paths and has no
`external archive` dependency.

## Matched performance

The final validated candidate uses S32, CPU-MoE, no-mmap, cache RAM 512 and
`-ub 4`; the UOPT-001 source control remains S32/CPU-MoE/no-mmap/`-ub 2`.
The deterministic matched 1,155-prompt-token cold workload and fresh short
three-repeat decode results are:

| Metric | UOPT-001 source control | UOPT-002 sidecar | Gate |
|---|---:|---:|---:|
| Fresh short decode median | 3.192 tok/s | **6.903 tok/s** final promoted repeat (validated candidate median: 7.359) | >= 5.0 tok/s |
| Fresh/cold TTFT, prompt_n 1,155 | 401.493 s | **162.726 s** final promoted fresh-process repeat (validated candidate: 156.949) | <= 184 s |
| Warm prompt-cache TTFT | 0.110 s | 0.083 s | non-regressing |

The final exact cold run was a fresh process with `cache_n: 0`, not a
cache-only claim.  Runtime telemetry from the validated exact run recorded
76,344 misses, 76,344 sidecar reads and 154,788,986,880 logical bytes: one
2,027,520-byte request per miss.  The source path made exactly three reads per
miss for the same payload, so this is the measured three-to-one request
reduction rather than a reduced-expert shortcut.

## Final acceptance

Evidence is retained locally at
`results-local/unlocked-speed-uopt-002/20260831T170415Z/`; final promotion
acceptance is `results-local/unlocked-speed-uopt-002/20260831T180023Z/`.  The
pre-promotion candidate acceptance and the promoted-profile re-run establish:

- lifecycle `start/status/health/stop`, loopback-only API `/health` and
  `/v1/models`, and WebUI all pass;
- real Pi with WP2, deterministic WP2 unit/recovery, and prompt/KV reuse pass;
- frozen gates are explicit refusals **0/6**, held-out degeneration **0/6**,
  benign capability **8/8**;
- deterministic source-versus-sidecar equivalence re-read all 18,432
  components after promotion: each source range equals its sidecar range and
  the aggregate payload SHA-256 is
  `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`;
  the validated matched S32/ub4 greedy A/B also recorded exact text SHA-256
  `f81a55cc56ea3aa8fd6126ed5ec7e224d07109144cc98d81179591a55155759e`;
- matched fresh decode and the 1,155-token cold-TTFT confirmation pass;
- direct UOPT-001 source-runtime/ub2 rollback and FAST rollback pass; final
  state is FAST with WP2 restored.

The optimized path has no source-GGUF mutation, crash, OOM, corruption, public
listener, or external-volume inference dependency.  Its remaining cold-path
paging pressure is explicit in the local evidence and does not alter the GO
classification.
