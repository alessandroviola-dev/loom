# LOOM Roadmap

Last updated: 2026-08-21
Current checkpoint: `CAPABILITY_000M_REAL_PI_REPRODUCIBLE_PASS`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## Canonical 8B baseline

Qwen3-8B, affine 3-bit/group64, BF16 KV, MLX 0.31.2. REALGEN 001 = 13.184615357 tok/s real generation and 12.046861457 tok/s E2E.

## A — Capability baseline — ACTIVE

### Bridge admission — COMPLETE

CAPABILITY 000H-000M established the multi-turn memory mechanism and admitted the real Pi bridge.

Promoted request-boundary policy:
- detach only the completed response's stale `prompt_cache` after ownership verification;
- call `mx.clear_cache()` exactly once.

CAPABILITY 000M:
- real Pi functional 3/3;
- strict 3/3;
- zero resource aborts;
- zero telemetry errors;
- minimum free 9-11%;
- minimum post-clear free 16-19%.

Stable bridge source is published at commit `4d204471aedb9262ccaa3b86f29b0e344d0c2884`.

### CAPABILITY 001 — RUN READY / NEXT

Frozen 12-task baseline:
- C01-C06 existing Coding Benchmark 01 v1.0.1;
- G01 safe fast-forward sync;
- G02 dirty-tree protection;
- G03 divergence diagnosis;
- E01 balanced-ratio interpretation;
- E02 upper-bound reasoning.

Frozen runtime:
- Qwen3-8B full parameter count, 3-bit/group64;
- BF16 KV;
- context 4096;
- max output 2048;
- step 512;
- localhost-only provider;
- tools read/write/edit/bash;
- admitted request-boundary reclamation policy.

Authority:
- `research/capability/capability-001-frozen-spec.md`
- `research/capability/capability-001-context-amendment.md`
- `research/capability/capability-001-runtime-admission.md`
- `research/capability/capability-001-run-manifest.md`

Primary metric: task passes / 12. Secondary: existing C01-C06 score /100, critical failures, constraint violations, tool/protocol errors, wall/resource diagnostics. No quality threshold is applied to this baseline; a complete scorable run becomes `CAPABILITY_001_BASELINE_COMPLETE`.

## B — RAM/speed frontier

After CAPABILITY 001, run MEMORY-FRONTIER 001 with controlled partial residency and measure resident bytes, MLX peak, system free/swap, SSD bytes/token, real tok/s, TTFT and correctness.

## C — Hide SSD cost

Then isolate async prefetch, double/triple buffering, transfer chunk sizing, direct safetensors range I/O, macOS page-cache behavior and resident-hotset selection.

## D — Amortize I/O across tokens

OUTCORE-BLOCK 001 revisits M>1 for out-of-core execution where one weight load can serve multiple positions.

## E — Representation without shrinking parameter count

Later candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core storage formats. Judge each by memory + speed + capability.

## F — Scale beyond 8B

1. solve architecture on well-characterized 8B;
2. transfer to models exceeding comfortable physical RAM;
3. reach 27B/32B-class full-parameter generation on M1 8 GB without OOM;
4. optimize toward interactive speed.

## Immediate order

1. CAPABILITY 001 frozen 12-task baseline
2. MEMORY-FRONTIER 001
3. prefetch/buffering/range-I/O
4. OUTCORE-BLOCK 001
5. scale toward 27B/32B

## Local-only implementation warning

CAPABILITY 000 experimental harnesses and raw evidence remain local unless explicitly synchronized. The stable bridge source is now published; CAPABILITY 001 may add only its own harness/evidence locally.
