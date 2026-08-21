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

### 000C — prefill frontier

`prefill_step_size=512` dominates canonical 2048 on the exact Pi prefill and remains the admitted agent-runtime setting.

### 000H — sequential accumulation

All captured R1-R6 requests pass fresh. A critical sequential run showed R2 failure because R1 left +468.30 MiB active request-boundary MLX state.

### 000I — targeted request-local reclamation PASS

The stale completed `GenerationBatch.Response.prompt_cache` retains finished-request KV. Ownership-checked detach recovers 252.00 MiB active MLX and preserves model/tool behavior.

### 000K — allocator-cache reclamation PASS

After the stale-response detach, one `mx.clear_cache()` reclaims 486.23 MiB allocator cache, raises R2 minimum free from 5% to 11%, costs 3.900 ms at the measured boundary and preserves semantics.

### 000L — full-sequence boundary reclamation PASS

Exact R1-R6 all complete with detach + one `mx.clear_cache()` after every completed response.

Treatment vs control:
- peak MLX 4132.64 vs 4230.45 MiB;
- minimum free 10% vs 5%;
- semantic/tool equivalence PASS;
- mean clear latency 2.651 ms;
- boundary allocator cache 0.00 MiB after every clear.

### 000M — REAL PI REPRODUCIBLE PASS

Report: `research/capability/capability-000m-real-pi-reproducibility-result.md`.

Three independent real-Pi attempts with the promoted boundary policy all pass:

- functional 3/3 = 100%;
- strict 3/3 = 100%;
- 6 model turns each;
- no resource aborts;
- no telemetry errors;
- minimum free 9–11%;
- minimum post-clear free 16–19%;
- post-clear allocator cache 0.00 MiB;
- mean boundary clear 2.003–2.596 ms;
- correct `answer.txt=31`, preserved `numbers.txt`, final `DONE` every time.

The bridge admission gate is therefore closed successfully.

### CAPABILITY 001 — READY

Frozen suite: 12 practical agent tasks covering coding, Git safety and experimental reasoning.

Frozen runtime:
- Qwen3-8B full parameter count, 3-bit/group64;
- BF16 KV;
- context 4096;
- max output 2048;
- step 512;
- localhost-only provider;
- tools read/write/edit/bash;
- promoted boundary policy: ownership-checked stale `prompt_cache` detach + one `mx.clear_cache()` after every completed response.

Documents:
- `research/capability/capability-001-frozen-spec.md`
- `research/capability/capability-001-context-amendment.md`
- `research/capability/capability-001-runtime-admission.md`

Primary result is task passes / 12; secondary coding score /100 and critical/constraint/tool-protocol errors. No quality threshold is applied to this baseline.

Before the run, mechanically publish the promoted local `scripts/loom_pi_mlx_bridge.py` because that stable implementation currently exists only in the user's local worktree.

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

1. mechanically publish promoted `scripts/loom_pi_mlx_bridge.py`
2. CAPABILITY 001 frozen 12-task baseline
3. MEMORY-FRONTIER 001
4. prefetch/buffering/range-I/O
5. OUTCORE-BLOCK 001
6. scale toward 27B/32B

## Local-only implementation warning

Recent CAPABILITY scripts/evidence remain local unless explicitly synchronized. The stable bridge source is the only immediate code file that must be published before CAPABILITY 001.
