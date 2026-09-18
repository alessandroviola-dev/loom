# scripts

LOOM execution and measurement utilities.

## Ollama single-shot coding benchmark

`scripts/ollama_single_shot.py` runs the frozen `Coding Benchmark 01 v1.0.0` against a local Ollama model without exposing benchmark tests to the model.

It:

- creates an isolated benchmark copy under `results-local/`;
- sends each task exactly once;
- provides only the frozen prompt and allowed source files;
- requests machine-parseable JSON file replacements;
- writes only permitted target files;
- records Ollama token/timing metrics and macOS memory snapshots;
- runs the frozen benchmark scorer after all six tasks;
- preserves raw API responses and a combined `run-summary.json` locally;
- never modifies the frozen benchmark tree.

Reference command from the repository root:

```bash
python3 scripts/ollama_single_shot.py \
  --model qwen3.5:4b-mlx \
  --context 4096
```

By default the adapter issues `ollama stop MODEL` before the run so the first task begins from an unloaded model. Use `--keep-loaded` only when intentionally measuring a warm-start condition.

Local run artifacts are written under `results-local/` and are excluded by `.gitignore`.

## External research archive

The BF16 DFlash scripts never assume a machine-specific mount point. Set
`LOOM_EXTERNAL_ARCHIVE` to a writable external archive root when running them;
models, caches, and artifacts remain outside the repository and are ignored by
Git.
