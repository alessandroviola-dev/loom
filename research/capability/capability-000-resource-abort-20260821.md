# CAPABILITY 000 — resource abort checkpoint

Date: 2026-08-21
Status: `CAPABILITY_000_RESOURCE_ABORT`

## Result

The local Pi bridge reached a genuine model-generated tool call before the resource gate stopped execution.

Observed path:

`Pi -> loom-mlx-local localhost bridge -> mlx_lm -> results-local/mlx/models/Qwen3-8B-3bit/`

Observed tool event:

- Qwen3-8B requested `read(numbers.txt)`.

The run then reached system-wide free memory **4%**, below the frozen hard-abort threshold of 5%, and stopped before task completion.

CAPABILITY 001 was therefore not started.

Local implementation files produced by Pi and not yet synchronized to GitHub:

- `scripts/loom_pi_mlx_bridge.py`
- `scripts/capability_000_pi_bridge_smoke.py`

Local raw evidence:

`results-local/capability/capability-000/20260821-135208/`

## Interpretation

This is not evidence that the Qwen3-8B lacks agentic reasoning capability. The model successfully entered the Pi tool loop and selected the correct first tool family. The blocking issue is the memory cost of the integrated agent stack.

Do not lower the frozen 4096 context or alter model representation yet. First attribute memory across the bridge/model/Pi/tool-loop stages.

## Next step

Run a diagnostic-only CAPABILITY 000A memory attribution with the existing local bridge implementation. Measure host free memory, swap, MLX memory where available, and per-process RSS across staged states: host baseline; bridge/server startup; model load; direct non-tool request; direct request with tool schema; Pi startup; Pi first model response; first tool call/feedback. Stop at the inherited hard resource abort.

After attribution, choose whether the correct intervention is bridge-memory reduction, server lifecycle/KV handling, context adaptation, or a different integration architecture.
