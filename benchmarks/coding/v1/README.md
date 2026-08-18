# LOOM Coding Benchmark 01 — v1

Status: FROZEN AFTER INITIAL VALIDATION

Purpose: provide a small, reproducible coding benchmark that can be run unchanged across local models, runtimes and agent layers on constrained hardware.

## Design principles

- Deterministic inputs and tests.
- Python standard library only.
- Small fixtures so context cost remains reasonable on 8 GB hardware.
- Tasks cover different failure modes rather than only code generation.
- Objective scoring wherever possible.
- Same task files and prompts for every compared configuration.
- Failed runs are recorded, not discarded.

## Tasks and scoring

| ID | Skill | Points |
|---|---|---:|
| T01 | Code generation from specification | 15 |
| T02 | Debugging existing faulty code | 15 |
| T03 | Code comprehension | 15 |
| T04 | Constrained refactoring | 15 |
| T05 | Multi-file reasoning | 25 |
| T06 | Instruction following under implementation constraints | 15 |
| **Total** |  | **100** |

Each task contains an exact `prompt.md`. The model or agent must receive that prompt unchanged.

## Benchmark modes

Results must declare one mode:

- `single_shot`: the model receives the prompt and supplied files once, with no test feedback before its final answer.
- `agentic`: the agent may inspect files, edit them and run tests. Tool/test iterations must be recorded.

Scores from different modes must never be compared as if they were the same benchmark condition.

## Running tests

From this directory:

```bash
python3 runner.py
```

The runner executes each task's unittest suite, calculates the objective score and prints a JSON result. It also writes a local result file under `results-local/`, which is ignored by git.

## Reproducibility rules

1. Start each model/configuration from a clean checkout of this benchmark version.
2. Do not edit tests or prompts.
3. Only files explicitly named as editable by a task may be changed.
4. Record runtime, model, quantization/backend, context, benchmark mode and hardware state.
5. Record failures and timeouts.
6. Do not change this v1 suite after it is frozen; fixes require a new benchmark version.
