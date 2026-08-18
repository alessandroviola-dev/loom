# Ollama Context Retention Probe 001 — Result

Date: 2026-08-18
Run id: `20260818-223909`
Status: **COMPLETED / VALID**

## Question

Does the Qwen 3.5 4B MLX allocation growth observed during Pi Agentic Coding Benchmark 001 appear in direct Ollama/MLX inference without Pi, and does it scale with prompt/context pressure?

## Frozen configuration

- Runtime: Ollama `0.32.14`
- Model/backend: `qwen3.5:4b-mlx` / MLX
- Context: 4096
- API: direct Ollama `/api/generate`
- no Pi
- no tools
- temperature 0
- thinking disabled
- output budget 8 tokens

Preregistered plan:
- `research/runtime/ollama-context-retention-probe-001-plan.md`

Run directory:
- `results-local/ollama-context-retention/20260818-223909`

Summary:
- `results-local/ollama-context-retention/20260818-223909/probe-summary.json`

## Observed result

| Condition | Prompt tokens | Wall | Ollama SIZE | Context | Swap used | Free memory |
|---|---:|---:|---:|---:|---:|---:|
| warm-low | 418 | 6.469 s | 4.1 GB | 4096 | 1925.50 MB | 15% |
| warm-medium | 1618 | 9.784 s | 4.3 GB | 4096 | 2374.12 MB | 17% |
| warm-high | 3018 | 16.379 s | 4.5 GB | 4096 | 2407.56 MB | 20% |
| warm-low-after-high | 418 | 0.380 s | 4.6 GB | 4096 | 2205.38 MB | 12% |
| cold-low | 418 | 5.526 s | 4.1 GB | 4096 | 2189.38 MB | 17% |
| cold-high | 3018 | 20.952 s | 4.2 GB | 4096 | 2386.62 MB | 23% |

All six API calls succeeded.

## Findings

### 1. Runtime-level prompt/context pressure is real

With Pi completely absent, the warm arm increased Ollama reported SIZE as prompt pressure rose:

```text
418 tokens  -> 4.1 GB
1618 tokens -> 4.3 GB
3018 tokens -> 4.5 GB
```

Therefore the allocation growth seen in LOOM is not exclusively caused by the Pi agent harness. Direct Ollama/MLX inference itself shows pressure-sensitive growth.

### 2. Warm high-water retention is supported

After the 3018-token warm-high call, the next call returned to only 418 prompt tokens but Ollama reported SIZE did not return to the original 4.1 GB. It remained higher at **4.6 GB**.

Cold controls reset near baseline:

- cold-low: **4.1 GB**
- cold-high: **4.2 GB**

This supports retained warm high-water behavior at the level visible through `ollama ps`.

### 3. Prompt pressure alone does not explain Agentic 001's 7.2 GB

The direct high-pressure one-shot call reached only:

- warm-high: **4.5 GB**
- cold-high: **4.2 GB**

This is far below the **7.2 GB** observed after T06 of Pi Agentic Coding Benchmark 001.

Therefore a simple model of `larger prompt => 7.2 GB` is not supported. Additional factors from sustained agentic work remain unresolved.

The next most relevant factor to isolate is **multi-turn/tool-loop depth inside one Pi session**, because tool execution causes repeated model turns and growing conversational state even when the configured context window remains 4096.

## Swap interpretation

Swap changed materially during the probe, but did not follow Ollama SIZE monotonically. In particular, warm-low-after-high retained a larger 4.6 GB SIZE while swap fell from 2407.56 MB to 2205.38 MB.

Therefore `ollama ps` SIZE and macOS swap usage must remain separate observed metrics. They should not be treated as equivalent measures of physical resident memory.

## What this probe does not establish

It does not identify the internal implementation behind Ollama SIZE growth. Do not label the effect as:

- a memory leak;
- KV-cache growth;
- MLX allocator fragmentation;
- a Pi-specific bug;
- physical resident memory growth equal to the displayed SIZE.

Those mechanisms remain unmeasured.

## Comparison with previous memory probe

Pi Memory Retention Probe 001 showed four identical tiny warm Pi sessions growing only **4.1 -> 4.5 GB**, with swap not accumulating.

This direct Ollama probe independently shows **4.1 -> 4.6 GB** under increasing prompt pressure plus a low-after-high call.

Together, the evidence supports:

> Warm runtime retention and prompt pressure can explain a modest allocation increase around several hundred MB, but not the full 4.4 -> 7.2 GB trajectory of the six-task agentic benchmark.

## Next experiment

Run a controlled **Pi Multi-turn Memory Probe 001** with cold-started sessions that deliberately require different numbers of file-tool round trips while keeping model, context and task content otherwise small and deterministic.

The goal is to determine whether within-session tool/turn depth is the missing driver that produces substantially larger Ollama SIZE high-water marks.
