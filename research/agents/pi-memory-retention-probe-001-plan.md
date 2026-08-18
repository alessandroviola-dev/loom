# Pi Memory Retention Probe 001 — Preregistered Plan

Date: 2026-08-18
Status: **PREREGISTERED / NOT YET RUN**

## Question

Pi Agentic Coding Benchmark 001 showed Ollama's reported allocation increasing monotonically from **4.4 GB to 7.2 GB** across six separate Pi invocations while model context remained fixed at 4096.

This probe asks:

> Does the reported allocation grow across repeated **identical small Pi calls** when Ollama remains warm, or was the benchmark trajectory primarily a task/context high-water effect?

No causal label such as memory leak, KV-cache growth, MLX retention or Ollama bug is allowed before this controlled probe.

## Reference configuration

- Apple M1 / 8 GB unified memory
- Pi 0.84.2
- Ollama 0.32.14
- model: `qwen3.5:4b-mlx`
- context: 4096
- max output: 2048
- isolated run-local `PI_CODING_AGENT_DIR`
- production Pi auth/settings/sessions/extensions/skills remain untouched
- `--no-session`
- `--no-extensions`
- `--no-skills`
- `--no-prompt-templates`
- `--no-themes`
- `--no-context-files`
- one exposed tool: `read`

## Fixed task

Every invocation receives the same tiny workspace and prompt:

- file: `probe.txt`
- content: `LOOM_MEMORY_PROBE`
- Pi must read `probe.txt` with the read tool and reply exactly `DONE`

The task content, tool surface and context setting remain identical across repetitions.

## Experimental arms

### Arm A — warm repeated calls

1. Stop the model once before the arm.
2. Run **4 separate Pi processes** with the identical task.
3. Do **not** call `ollama stop` between iterations.
4. Capture memory/swap/`ollama ps` before and after every iteration.

Interpretation target:
- if Ollama reported size rises monotonically across identical calls, repeated-call retention/accumulation becomes supported;
- if size stabilizes, the 4.4 -> 7.2 GB benchmark trajectory is more consistent with task-specific high-water effects or another workload-dependent mechanism.

### Arm B — cold control

1. For **2 iterations**, call `ollama stop qwen3.5:4b-mlx` before each Pi invocation.
2. Run the exact same task.
3. Capture memory/swap/`ollama ps` after stop and after each invocation.

Interpretation target:
- similar post-call reported sizes across cold runs provide a reset/control baseline;
- materially different cold sizes imply additional uncontrolled variability that limits inference.

## Metrics

For each iteration record:

- Pi exit code
- exact final text
- whether `read` was observed
- provider-reported last non-zero usage
- wall time
- PhysMem line
- memory-pressure free percentage
- swap usage
- `ollama ps`
- parsed Ollama reported size when available
- context and processor reported by Ollama

Also record arm-start and final snapshots.

## Safety / failure policy

- No tracked LOOM file is modified by the model.
- Workspaces live under ignored `results-local/` or temporary directories.
- If Pi/API errors occur, preserve the iteration and continue only when safe.
- If the script detects extremely low memory-free percentage or very high swap according to its guardrail, it must stop the model and abort remaining warm iterations.
- No result from this probe changes any frozen Coding Benchmark score.

## Predeclared interpretation

Possible outcomes:

1. **Warm monotonic growth + cold reset:** evidence supports accumulation/retention across separate invocations.
2. **Warm stable size + cold similar:** benchmark growth was likely workload/high-water dependent rather than simple call-count accumulation.
3. **Warm/cold both highly variable:** inconclusive; a lower-level Ollama/MLX allocation probe is required.
4. **Growth tracks cumulative provider usage or specific iteration complexity despite identical task:** investigate provider/runtime caching and allocation behavior separately.

This experiment measures behavior only. It does not assign root cause.
