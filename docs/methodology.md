# Methodology

Every model/runtime configuration should be tested with the same benchmark version and under documented machine conditions.

## Minimum measurements

- Model/runtime/backend
- Quantization
- Model size on disk
- Resident size if reported
- Context length
- GPU/CPU split
- Time to first token when available
- Prompt-processing throughput
- Generation throughput
- Total latency
- Physical memory used
- Compressed memory
- Memory pressure
- Swap usage
- Task correctness
- Subjective usability notes separated from objective measurements

## Rules

- Do not compare different benchmark prompts as if they were equivalent.
- Record failed runs.
- Distinguish model-file size from runtime resident memory.
- Distinguish total system swap from model-attributable deltas.
- Prefer repeated runs over single observations.
- Update `HANDOFF.md` after each meaningful step.
