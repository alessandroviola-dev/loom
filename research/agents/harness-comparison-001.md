# Agent Harness Comparison 001 — Qwen Code vs Pi at context 4096

Date: 2026-08-18
Reference machine: Apple M1, 8 GB unified memory
Runtime/model: Ollama 0.32.14 / `qwen3.5:4b-mlx`
Context: 4096

## Purpose

Measure whether agent-harness overhead can determine practical feasibility on the constrained LOOM reference machine.

This is a minimal read-only comparison, not a full coding-quality benchmark.

## Qwen Code smoke

Run id: `20260818-211009`
Harness: Qwen Code 0.21.13
Mode: normal Qwen Code configuration, approval mode `plan`, sandbox enabled
Task: read `README.md` and return its first Markdown heading

Observed:
- process exit code: 0, but semantic result is an API error;
- model resolved: `qwen3.5:4b-mlx`;
- no tool call reached;
- estimated initial prompt: 4474 tokens;
- hard model context: 4096;
- over limit: ~378 tokens;
- always-on context warning: ~1429 tokens;
- Seatbelt active (`permissive-open`);
- Ollama model was not loaded (`ollama ps` empty before and after).

Memory:
- PhysMem used: 6675M -> 6741M (+66M)
- memory free percentage: 73% -> 73%
- swap used: 1380.69M -> 1380.69M (+0M)
- compressor: 283M -> 283M
- elapsed from first snapshot to finished timestamp: ~2.08 s

Git:
- before: clean
- after: ` M .qwen/settings.json`

The exact settings diff is still pending local inspection. Do not attribute the modification to the model itself until that diff is inspected; it may be Qwen Code config normalization/migration.

## Pi smoke

Run id: `pi-20260818-212407`
Harness: Pi 0.84.2
Mode: ephemeral `--no-session`, JSON event mode
Exposed tools: `read` only
Task: read `README.md` and return its first Markdown heading

Observed:
- exit code: 0;
- success: true;
- tool used: `read`;
- final text: `# LOOM`;
- no event or JSONL parse errors;
- working tree unchanged relative to its starting state;
- Ollama after run: 4.2 GB, 100% GPU, context 4096.

Memory:
- PhysMem used: 7207M -> 7462M (+255M)
- memory free percentage: 73% -> 31%
- swap used: 1356.69M -> 2008.56M (+651.87M)
- compressor: 289M -> 3483M (+3194M)
- elapsed: ~34.00 s

Git:
- before: ` M .qwen/settings.json`
- after: ` M .qwen/settings.json`
- therefore Pi caused no additional repository delta.

## Result

| Harness | Tool surface | Context | Tool reached | Final result |
|---|---|---:|---|---|
| Qwen Code 0.21.13 | normal harness | 4096 | No | FAIL before first tool call; prompt estimated 4474 tokens |
| Pi 0.84.2 | `read` only | 4096 | Yes | PASS; returned `# LOOM` |

## Interpretation

Measured result:

> On the LOOM M1/8 GB reference machine, a minimal Pi harness can complete a real tool call with `qwen3.5:4b-mlx` at context 4096, while Qwen Code's normal configuration exceeds the same context window before the first tool call.

This establishes agent-harness/context overhead as a practical feasibility constraint.

Important limitation:
- this is not yet an equal-tool-surface comparison;
- Pi exposed only `read` while Qwen Code normal configuration carried a larger default tool/context surface;
- therefore the experiment does not prove Pi is globally superior or that its base framework always has lower overhead;
- it proves that the tested minimal Pi operating profile is feasible at 4096 while the tested normal Qwen Code profile is not.

Memory comparison limitation:
- Qwen Code failed before loading Ollama, so its run cannot be compared directly with Pi for loaded-model memory cost;
- the Pi smoke demonstrates the practical memory cost of a successful 4096 agent turn: +651.87 MB swap and free-memory pressure falling from 73% to 31% in this snapshot pair.

## Next controlled steps

1. Inspect local `git diff -- .qwen/settings.json` to identify the Qwen Code-generated settings delta.
2. Harden the Qwen Code smoke runner to treat semantic `[API Error: ...]` as failure even when the process exits 0.
3. Run Qwen Code in a reduced/safe configuration at 4096 to separate always-on memory/context overhead from core tool-schema overhead.
4. Run a controlled Pi edit + test smoke at 4096.
5. Only after those steps, choose the primary harness for full Coding Benchmark 01 agentic mode.
