# Pi Edit+Test Smoke 001

Date: 2026-08-18
Run id: `pi-edit-20260818-213432`
Status: **FUNCTIONAL PASS / STRICT OUTPUT FAIL**

## Configuration

- Reference machine: Apple M1, 8 GB unified memory
- Agent harness: Pi `0.84.2`
- Provider: `ollama`
- Model: `qwen3.5:4b-mlx`
- Context: 4096
- Session mode: ephemeral (`--no-session`)
- Exposed tools: `read,edit,bash`
- Workspace: disposable ignored directory under `results-local/agent-smoke/.../workspace`

## Task

Pi received a deliberately broken Python `clamp()` implementation plus deterministic `unittest` tests. It was instructed to:

1. inspect both files with `read`;
2. modify only the solution with `edit`;
3. run `python3 -m unittest -v` with `bash`;
4. leave the test file unchanged;
5. reply exactly `PASS` after tests succeeded.

## Observed tool sequence

```text
['read', 'read', 'bash', 'read', 'read', 'bash', 'edit', 'bash']
```

All required tool families were used: `read`, `edit`, `bash`.

## Functional outcome

- Pi process exit code: `0`
- solution changed: **true**
- tests unchanged: **true**
- independent external tests pass: **true**
- tracked LOOM working tree unchanged: **true**
- Pi event errors: **none**
- JSONL parse errors: **none**

Independent unittest result:

```text
test_above ... ok
test_below ... ok
test_inside ... ok
test_invalid_bounds ... ok

Ran 4 tests in 0.000s
OK
```

The model diagnosed the bug correctly: `max(high, min(low, value))` needed to become `max(low, min(high, value))`. The coding workflow itself is therefore a **functional pass** at context 4096.

## Strict instruction-following outcome

Prompt required the final response to be exactly:

```text
PASS
```

Observed final text:

```text
Now I understand the bug. The return statement is wrong: `max(high, min(low, value))` should be `max(low, min(high, value))`. Let me fix it:PASS
```

Therefore exact final-output compliance is **false**.

The original smoke runner contained a validation defect: it computed `answer_ok` but did not include it in aggregate `success`. This caused the historical run summary to contain `"success": true`. The run is canonically reclassified as:

- functional success: **PASS**
- strict output/protocol success: **FAIL**

The runner was subsequently patched so future runs expose `functional_success`, `strict_success`, and `answer_exact_pass`, and aggregate `success` follows strict success.

## Resource metrics

### Before

- PhysMem: `5622M used`, `2008M unused`
- wired: `1737M`
- compressor: `295M`
- system-wide memory free: **73%**
- swap: **1503.88 MB used**
- `ollama ps`: model not loaded

### After

- PhysMem: `7495M used`, `137M unused`
- wired: `1680M`
- compressor: `1238M`
- system-wide memory free: **61%**
- swap: **2159.19 MB used**
- `ollama ps`: `qwen3.5:4b-mlx`, **4.8 GB**, **100% GPU**, context **4096**

### Deltas / elapsed

- PhysMem used: **+1873 MB**
- swap used: **+655.31 MB**
- compressor: **+943 MB**
- memory-free percentage: **73% -> 61%**
- elapsed from first snapshot to final timestamp: approximately **114.0 s**

## Comparison with Pi Read-only Smoke 001

Read-only run `pi-20260818-212407`:
- elapsed ~34.0 s
- swap delta **+651.87 MB**
- final Ollama resident report **4.2 GB**
- context 4096, 100% GPU

Edit+test run:
- elapsed ~114.0 s
- swap delta **+655.31 MB**
- final Ollama resident report **4.8 GB**
- context 4096, 100% GPU

Interpretation:
- the edit/test loop took about **3.35x** as long as the minimal read-only smoke;
- observed swap growth was nearly identical (difference about **3.44 MB**), so the extra tool-loop complexity did not produce a proportionally larger swap delta in these two runs;
- Ollama's final resident-size report was larger in the edit/test run (4.8 vs 4.2 GB), but the cause is unresolved and must not yet be attributed to KV cache, tool count, or any single mechanism;
- memory snapshots started from materially different host states, so absolute PhysMem/free-percentage values are not a controlled apples-to-apples comparison.

## Research interpretation

This run establishes that Pi + Qwen 3.5 4B MLX can perform a complete minimal agentic coding loop at context 4096 on the reference M1/8 GB machine:

```text
read -> diagnose -> edit -> test -> verified pass
```

At the same time, instruction-following around exact response formatting remains imperfect. This mirrors the broader Baseline 001 finding: semantic/code quality can be stronger than protocol/delivery reliability.

Functional correctness and protocol/instruction adherence must therefore remain separately scored in the full agentic benchmark.

Run directory:

`results-local/agent-smoke/pi-edit-20260818-213432`
