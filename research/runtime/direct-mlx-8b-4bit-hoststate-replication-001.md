# LOOM — Direct MLX 8B 4-bit Host-State Controlled Replication 001

Date: 2026-08-19
Host-state preflight run: `20260819-134010`
Full benchmark run: `20260819-134012`
Status: **LAUNCH_ELIGIBLE → PARTIAL_RESOURCE_FAIL**

## Purpose

Replicate the previously failed Qwen3-8B-4bit full Coding Benchmark 001 under a prospectively controlled host-memory state, without changing model/runtime/benchmark settings.

The original full 4-bit run (`20260819-133144`) began at 56% system free memory, whereas the successful standalone 4-bit T01 began at 74% and the completed 3-bit full benchmark at 75%. This replication therefore tested whether the original failure was primarily explained by that uncontrolled host-state difference.

## Frozen host-state gate

Wrapper:
`scripts/direct_mlx_8b_4bit_hoststate_replication_001.py`

Required frozen full-runner blob:
`541e23ef5a824a29f3f67e162e48228b2ccabb14`

Launch requirement:
- 3 consecutive `memory_pressure` samples
- each sample >=70% system free memory
- one sample per second
- no automated purge/process killing/swap manipulation

If launch eligible, wrapper is replaced with the exact frozen 4-bit full benchmark runner.

## Host-state result

Observed samples:
- sample 1: 72% free / 1381.75 MB swap
- sample 2: 74% free / 1381.75 MB swap
- sample 3: 74% free / 1381.75 MB swap

Classification: `LAUNCH_ELIGIBLE`.

The frozen full benchmark then reported its own safety preflight at:
- 72% free
- 1381.75 MB swap

Thus the replication met the prospective host-state condition and began from a state comparable to the successful standalone 4-bit T01 / completed 3-bit full-run references.

## Frozen runtime condition

Unchanged from the failed original full run:
- model `mlx-community/Qwen3-8B-4bit`
- verified SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- Direct MLX environment `mlx-lm==0.31.3`, `mlx==0.31.2`, `transformers==5.12.1`
- exact Coding Benchmark 01 v1.0.1 T01–T06
- exact frozen adapter/scorer
- one loaded model session
- local/offline
- `enable_thinking=False`
- `max_kv_size=4096`
- **unquantized KV**
- max 2048 generated tokens/task
- seed 0
- no retries/repair/salvage/test feedback
- frozen abort: free memory <5% OR swap >5600 MB

## Observed execution

Progress reached:
- T01 running
- T02 running
- T03 running
- T04 running

Telemetry reported at abort:
- peak sampled process RSS: **332.046875 MB**
- peak observed swap: **2879.38 MB**
- minimum observed free memory: **4%**
- disk before: **35.333 GiB**
- disk after: **35.328 GiB**

Classification: **PARTIAL_RESOURCE_FAIL**.

The free-memory guardrail fired again despite the controlled high-free-memory launch state. Swap remained well below the 5600 MB guardrail.

## Canonical interpretation

> The controlled replication demonstrates that the original 4-bit full-session resource failure was not solely an artifact of starting at 56% host free memory. Starting from 72–74% free allowed the same frozen profile to progress materially farther, reaching T04 rather than failing during T01, but the session still crossed the 5% free-memory boundary. Therefore the exact Qwen3-8B-4bit + Direct MLX + `max_kv_size=4096` + unquantized-KV continuous coding profile is not established as workload-stable on the reference M1/8 GB machine.

Host state is supported as a meaningful modifier of how far the run progresses, but it does not rescue the exact profile.

Do not repeat the same frozen profile again.

## Quality boundary

No aggregate quality comparison is valid because the benchmark did not complete. The prospectively frozen Pi gate remains unevaluable.

Do not compare any partial task score/output against the completed 3-bit benchmark.

## Next diagnostic

Run the existing read-only resource inspector against:
`results-local/mlx/8b-4bit-coding-benchmark-001/20260819-134012`

Recover:
- exact persisted task count/results;
- child exit/wall state;
- free-memory/swap timeline across T01–T04;
- whether completed task boundaries correspond to stepwise retained pressure;
- raw child stdout/stderr tails.

No model rerun is authorized until this inspection is complete.

## Rescue boundary

After the diagnostic, at most one separately preregistered low-confound rescue may be considered.

The leading candidate is **8-bit KV-cache quantization** while preserving model, benchmark, `max_kv_size=4096`, prompts/scorer, generation budget and safety thresholds. MLX-LM exposes `kv_bits` as a generation parameter; this must be treated as a new profile, not as a correction to the failed unquantized-KV experiment.

Do not begin a rescue ladder. If a single justified rescue fails, close this branch and move on.
