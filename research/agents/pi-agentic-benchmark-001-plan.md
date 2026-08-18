# Pi Agentic Coding Benchmark 001 — preregistered plan

Date: 2026-08-18
Status: **PREREGISTERED / RUN PENDING**

## Purpose

Measure whether Pi `0.84.2` + local `qwen3.5:4b-mlx` can convert the strong semantic/code quality seen in Coding Baseline 001 into reliable filesystem delivery when the model can read and edit real files instead of serializing complete files inside one JSON envelope.

## Frozen benchmark

Use **LOOM Coding Benchmark 01 v1.0.1** unchanged:

- T01 generation — 15 points
- T02 debugging — 15 points
- T03 comprehension — 15 points
- T04 refactoring — 15 points
- T05 multi-file reasoning — 25 points
- T06 instruction-following constraints — 15 points
- total — 100 points

Prompts, fixtures, hidden tests, task weights and frozen runner semantics are not changed.

## Reference configuration

- machine: Apple M1, 8 GB unified memory
- Pi: `0.84.2`
- provider: Ollama
- model: `qwen3.5:4b-mlx`
- backend: MLX through Ollama
- context: **4096**
- max output: **2048**
- session: ephemeral

## Agent harness

Script:

`script/pi_agentic_benchmark.py` (repository path is actually `scripts/pi_agentic_benchmark.py`)

Per task Pi receives only:
- the frozen task prompt text;
- the task's supplied source/context files;
- any existing permitted editable starter file.

Pi tools exposed:
- `read`
- `write`
- `edit`

No `bash` tool is exposed in this benchmark run. This intentionally prevents test execution and keeps the first agentic comparison focused on filesystem delivery rather than test-feedback/retry loops.

## Hidden-test separation

The agent workspace does **not** contain frozen test files.

Each task runs in a temporary workspace outside the repository tree. Hidden tests remain only inside a separate scoring copy. Pi is explicitly instructed:
- work only in the current directory;
- do not access parent directories, absolute paths, network resources or unrelated files;
- do not create persistent scratch files.

After Pi exits, only permitted editable output files are copied into the scoring copy. The frozen runner is then executed externally.

Important limitation: Pi has no built-in OS sandbox. This run relies on workspace separation, a minimal tool allowlist and explicit instruction rather than kernel-enforced filesystem isolation. Any evidence of out-of-workspace access would invalidate the affected task and require a stronger sandboxed rerun.

## Pi configuration isolation

The run must not load or modify the user's production Pi environment.

For the benchmark, the adapter creates a run-local `PI_CODING_AGENT_DIR` containing only a minimal `models.json` for the local Ollama model.

Per-run resource discovery is disabled:
- `--no-extensions`
- `--no-skills`
- `--no-prompt-templates`
- `--no-themes`
- `--no-context-files`
- `--no-approve`
- `--no-session`

Environment additionally disables update/telemetry startup work:
- `PI_OFFLINE=1`
- `PI_SKIP_VERSION_CHECK=1`
- `PI_TELEMETRY=0`

The user's normal OpenAI/Codex auth, settings, sessions, skills, extensions and packages are outside the run-local agent directory and must remain unchanged.

## Task delivery protocol

For every task:
1. Pi gets one agent session/attempt.
2. No hidden test feedback is provided.
3. Pi may iteratively read/edit/write the visible files.
4. Only task-declared editable files may be created or changed.
5. Supplied non-editable files must remain byte-identical.
6. No unexpected persistent files may remain in the workspace.
7. Final assistant text must be exactly `DONE` for strict protocol compliance.

## Score views — frozen before run

### 1. Artifact score

Raw score from the frozen v1.0.1 runner after copying whatever editable artifacts exist into the isolated scoring tree.

This view may include starter-file partial passes and therefore is not sufficient alone to measure agent delivery.

### 2. Delivery-adjusted score

A task's frozen-runner points count only if:
- Pi process exits successfully;
- no Pi event error is recorded;
- JSONL parses cleanly;
- every permitted editable file is actually **created or changed** by the agent.

If delivery fails, that task contributes zero to this view even if untouched starter artifacts pass some hidden tests.

### 3. Strict protocol-adjusted score

A task's frozen-runner points count only if all delivery requirements pass **and**:
- supplied non-editable inputs remain unchanged;
- no unexpected persistent files remain;
- final assistant text is exactly `DONE`.

This separates functional code quality from harness/protocol reliability.

## Telemetry

Capture:
- Pi version/model/context/tools;
- raw Pi JSONL and stderr per task;
- tool names observed;
- final assistant text;
- task wall time;
- event/JSONL errors;
- output-created/changed status;
- non-editable input integrity;
- unexpected file list;
- memory/swap and `ollama ps` before run, after every task and after run;
- frozen benchmark per-task score and total score.

## Pre-run reference points

Single-shot Baseline 001:
- strict delivery-adjusted: **30.00/100**
- artifact: **40.71/100**
- recovered semantic-content diagnostic: **82.86/100**

Pi smoke evidence at context 4096:
- minimal read-only tool smoke: PASS
- isolated read/edit/bash/test smoke: functional PASS, strict final-output FAIL

## Primary questions

1. Does filesystem delivery materially close the 30.00 → 82.86 single-shot gap?
2. Which tasks still fail because of coding/comprehension quality rather than transport?
3. How often does the 4B model violate strict delivery/protocol requirements?
4. Does context 4096 remain sufficient across all six tasks with a minimal file-tool harness?
5. What time, swap and Ollama resident-size cost does the full agentic run impose?

## Failure policy

- No retries based on hidden test results.
- No prompt edits after seeing a task result.
- No manual code repair.
- No envelope salvage because delivery is filesystem-based.
- If the adapter itself has a material implementation defect, preserve the failed run, fix the adapter, document the defect, and rerun under a new run ID; never overwrite the original result.
