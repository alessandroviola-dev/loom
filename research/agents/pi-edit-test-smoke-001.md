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

Terminal-reported checks:

- Pi process exit code: `0`
- solution changed: **true**
- tests unchanged: **true**
- independent external tests pass: **true**
- tracked LOOM working tree unchanged: **true**
- no reported Pi error in terminal

The model diagnosed the bug correctly: the clamping expression had its outer `max()` bound reversed. The produced edit fixed the implementation and the independent runner confirmed all tests passed.

Therefore the coding workflow itself is a **functional pass** at context 4096.

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

The original smoke runner contained a validation defect: it computed `answer_ok` but did not include it in the aggregate `success` condition. This caused the terminal to print `Success: True` despite the strict output-format failure.

The runner was subsequently patched so future runs expose both:

- `functional_success`
- `strict_success`

and `success` now follows strict success.

## Research interpretation

This run establishes that Pi + Qwen 3.5 4B MLX can perform a complete minimal agentic coding loop at context 4096 on the reference M1/8 GB machine:

```text
read -> diagnose -> edit -> test -> verified pass
```

At the same time, it reveals that instruction-following around final response formatting remains imperfect. This mirrors the broader Baseline 001 finding: semantic/code quality can be stronger than protocol/delivery reliability.

This distinction must remain explicit in the full agentic benchmark. Functional correctness and protocol/instruction adherence should be scored separately rather than collapsed into one binary result.

## Pending ingestion

The run's `smoke-summary.json` still needs to be ingested for:

- memory before/after;
- swap before/after;
- Ollama resident size/context;
- total elapsed time;
- event/JSONL metadata;
- exact unittest output.

Run directory:

`results-local/agent-smoke/pi-edit-20260818-213432`
