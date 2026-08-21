# LOOM Roadmap

Last reset: 2026-08-21
Current active checkpoint: `CAPABILITY_000A_MEMORY_ATTRIBUTION_COMPLETE`
Detailed historical roadmap through REALGEN 002 is preserved in Git history at commit `844325f63b1880107040b219524ad5391276769c`.

## Mission

LOOM exists to make **excellent, large, full-parameter-count LLMs practical on very small Apple Silicon systems**, with Apple M1 / 8 GB as the reference machine.

The long-term direction is roughly **27B / 32B-class models on 8 GB**, without using smaller parameter-count models as the primary escape hatch.

Every major direction is judged on:

1. **Memory**;
2. **Speed**;
3. **Capability**.

A model that merely fits is not enough. A model that is fast but materially less capable is not enough.

## Operating method

Canonical protocol: `research/governance/chatgpt-pi-operating-protocol.md`.

Pi is reserved for code, local runtime/source inspection, benchmarks/tests and concise raw evidence.

ChatGPT owns experiment design/review, GitHub synchronization, ROADMAP/HANDOFF and research continuity.

Default loop:
`ChatGPT designs -> Pi codes/tests -> Pi returns evidence -> ChatGPT reviews/syncs -> next experiment`.

## Canonical Qwen3-8B baseline

REALGEN 001:

- Qwen3-8B full parameter count;
- 3-bit affine/group64;
- BF16 KV;
- Apple M1 / 8 GB;
- MLX 0.31.2 / mlx-lm 0.31.3;
- built-in M1 `qmv_fast`;
- real autoregressive generation **13.184615357 tok/s**;
- pooled end-to-end **12.046861457 tok/s**;
- raw persistent weights **3,583,928,320 B**;
- MLX peak **3,826,575,836 B**.

REALGEN 002 tested M1_S1_R8 transfer: exact but **-9.178832%** representative throughput. Closed; retain built-in qmv_fast.

The separate M5 verifier remains ~13.990655 tok/s oracle-verification evidence only.

## Known memory frontier

Pure layer streaming has already been demonstrated: RAM falls, throughput collapses.

Do not rediscover pure streaming as the endpoint. The architectural problem is to find the best point between full residency and full streaming, then hide unavoidable I/O through overlap and amortization.

## Direction A — CAPABILITY / useful-agent baseline — ACTIVE

CAPABILITY 001 will measure whether the current 8B 3-bit system can complete useful real tasks through Pi: coding, safe Git operations and result/experiment reasoning.

### CAPABILITY 000 — local model -> Pi bridge

The localhost MLX bridge successfully connected Pi to the canonical Qwen3-8B 3-bit model. A real Qwen-generated `read(numbers.txt)` tool call was observed.

The smoke then hit the hard <5% free-memory floor.

### CAPABILITY 000A — memory attribution — COMPLETE

Report: `research/capability/capability-000a-memory-attribution-result.md`.

Findings:

- model instance count: **1**;
- duplicate model: **no**;
- model-load transition free memory **67% -> 30%**;
- direct 18-token request completes at 20% free;
- direct 366-token tool-schema request completes at 17% free;
- Pi process is only ~45.55 MB RSS and leaves 18% free before inference;
- the first real Pi prefill crosses the hard memory floor before completion.

BF16 KV theoretical size is 147,456 bytes/token: 288 MiB @2048, 432 MiB @3072, 576 MiB @4096.

The dynamic prefill high-water is therefore the immediate unresolved bottleneck; KV alone is not yet proven as the cause.

### CAPABILITY 000B — Pi prefill envelope — NEXT

Frozen plan: `research/capability/capability-000b-pi-prefill-envelope-plan.md`.

Keep Qwen3-8B 3-bit, BF16 KV, context 4096, max output 2048 and full Pi tool surface unchanged.

Required outputs:

1. exact first Pi request capture with no model execution;
2. exact token decomposition;
3. direct replay of the same payload without Pi;
4. prefill high-water memory telemetry;
5. source-based attribution of KV/temporary allocation behavior;
6. identification of the first justified memory factor.

Do not choose a remedy until 000B is complete.

### CAPABILITY 001 — blocked pending sustainable bridge

Once 000B identifies/resolves the agentic prefill problem, run the frozen 12-task CAPABILITY 001 suite unchanged and establish the capability baseline.

Future representation changes must be reported as:
`memory delta + speed delta + capability delta`.

## Direction B — RAM / speed frontier — HIGH PRIORITY AFTER CAPABILITY BASELINE

### MEMORY-FRONTIER 001

Use the known 8B as a laboratory and measure real M1 generation across controlled resident fractions/windows rather than all-or-nothing streaming.

For every point record together:

- resident/persistent bytes;
- MLX peak;
- system free/swap;
- SSD bytes read per token;
- real generation tok/s;
- TTFT;
- correctness/exactness where representation is unchanged.

Primary artifact: a **RAM <-> tok/s Pareto curve**.

## Direction C — hide unavoidable SSD cost

After the frontier is measured, isolate one factor at a time:

1. asynchronous prefetch;
2. double/triple buffering;
3. transfer/super-layer chunk sizing;
4. direct safetensors range I/O / mmap / pread;
5. macOS page-cache measurement/control;
6. resident-hotset selection.

## Direction D — amortize weight I/O across multiple tokens

For an out-of-core dense model, reloading streamed weights per M1 token may dominate compute.

Future `OUTCORE-BLOCK 001` should compare M1 versus larger exact-valid token blocks under partial residency to measure:

- SSD bytes per candidate/accepted token;
- block wall time;
- prefetch overlap;
- resident-memory requirement;
- whether M>1 materially moves the RAM/speed frontier.

This is why the current resident-8B M5 speculative ceiling does not close multi-token execution as an out-of-core technique.

## Direction E — representation without shrinking parameter count

Allowed research factors include:

- mixed precision by tensor/layer;
- compressed cold weights;
- selective bit widths;
- quantized KV;
- storage formats designed for out-of-core execution.

But a representation is promoted only if its combined memory/speed/capability result is useful.

## Direction F — scale beyond 8B

Progression:

1. solve the architectural memory/speed tradeoff on the well-characterized 8B;
2. apply the engine to a model that does not comfortably fit physical RAM;
3. reach a **27B/32B-class full-parameter-count model producing correct tokens without OOM on M1 8 GB**;
4. then optimize that larger model from merely-running toward interactive speed.

## Closed / paused work

Do not routinely reopen without genuinely new evidence:

- Stretch 037–041;
- REALGEN 002 M1 S1_R8;
- gate/up fusion;
- row-chunk qmatmul;
- outer MLP compile;
- fused residual/RMSNorm;
- persistent BF16 dequantized projection caches;
- MLX 0.32 M5 comparison;
- GQA shared-KV clone;
- GC-only cleanup removal.

## Immediate order

1. **CAPABILITY 000B — exact Pi prefill envelope and peak-memory attribution.**
2. Select and test the first justified prefill-memory remedy without changing model capability unnecessarily.
3. Run **CAPABILITY 001** on the canonical 8B 3-bit system.
4. Run **MEMORY-FRONTIER 001**.
5. Add prefetch/buffering based on measured frontier evidence.
6. Run **OUTCORE-BLOCK 001**.
7. Scale the resulting engine toward 27B/32B.

## Final objective

LOOM should become an execution system that treats **RAM + SSD + Apple unified memory + scheduling** as one managed memory hierarchy and can run an LLM whose total weights exceed physical RAM while retaining useful speed and capability.
