# Pi Agentic Cold Replay 001 — Preregistered Plan

Date: 2026-08-18
Status: **PREREGISTERED / READY**

## Question

How much of Pi Agentic Coding Benchmark 001's Ollama SIZE trajectory `4.4 -> 7.2 GB` is caused by the high-water requirement of individual benchmark workloads, versus cumulative warm retention across consecutive heterogeneous tasks?

## Motivation

Controlled probes established:

- identical repeated Pi calls: warm SIZE only `4.1 -> 4.5 GB`;
- direct Ollama prompt pressure: `4.1 -> 4.5 GB`, retained at 4.6 GB after returning to a small prompt;
- controlled Pi tool depth 1 -> 4 turns: `4.1 -> 4.3 GB`;
- depth-8 synthetic probes were not reliably followed by Qwen 4B and are not suitable for further causal inference.

The next probe should therefore reproduce the real benchmark workload shape rather than invent a new synthetic protocol.

## Frozen source workload

Use the exact frozen Coding Benchmark 01 v1.0.1:

- same T01-T06 prompt files;
- same supplied source/fixture files;
- same `task_prompt(...)` wrapper used by `scripts/pi_agentic_benchmark.py`;
- same Pi tool surface: `read,write,edit`;
- no bash/test feedback;
- hidden tests are not copied into the agent workspace;
- same model `qwen3.5:4b-mlx`;
- context 4096;
- max output 2048;
- isolated run-local `PI_CODING_AGENT_DIR`;
- extensions/skills/templates/themes/context files disabled;
- one attempt per task.

This is a memory/workload replay, **not a benchmark rescore**. Frozen canonical scores remain unchanged.

## Cold-start design

Before every task T01-T06:

1. execute `ollama stop qwen3.5:4b-mlx`;
2. capture post-stop machine state;
3. create a fresh temporary task workspace from the frozen inputs;
4. run the exact Pi agent prompt/tool configuration used in Agentic 001;
5. do not expose hidden tests and do not provide feedback;
6. capture tool calls, final text, provider usage, wall time and post-task memory/Ollama state;
7. stop the model before starting the next task.

No task inherits model high-water from a previous task.

## Historical warm reference

Canonical Agentic 001 post-task Ollama SIZE:

| Task | Historical warm SIZE |
|---|---:|
| T01 | 4.4 GB |
| T02 | 5.2 GB |
| T03 | 5.6 GB |
| T04 | 6.4 GB |
| T05 | 6.8 GB |
| T06 | 7.2 GB |

Historical provider usage/tool counts are comparison context only. The replay may not reproduce identical model behavior even at temperature 0, so each replay's observed tool count/usage must be recorded.

## Metrics per task

- exit code / timeout;
- JSONL/event errors;
- tool names and count;
- final assistant text;
- last non-zero provider usage;
- wall time;
- PhysMem;
- system memory free percentage;
- swap used;
- Ollama reported SIZE;
- Ollama context and processor;
- historical warm SIZE for direct comparison.

## Interpretation rules

### Evidence for cumulative warm retention as major driver

Supported if individual cold replays remain near the ~4.1-4.6 GB range while the historical warm sequence reached 7.2 GB.

### Evidence for workload-specific high-water as major driver

Supported if one or more cold task replays independently approach their large historical warm allocations (for example >=6 GB), especially when the replay tool/usage shape is similar to the original task.

### Mixed result

Expected if cold task size rises with task complexity but remains materially below historical later-task warm SIZE. That would support both workload-specific high-water and cumulative retention.

## Validity caveat

This probe measures the replay actually produced. If a replay task's tool sequence or usage differs substantially from Agentic 001, that task cannot be treated as a perfectly matched workload replica. Preserve it and report the mismatch; do not rescue or rerun under the same run id.

## Non-claims

Do not infer the internal meaning of Ollama `SIZE`, a memory leak, KV-cache implementation, allocator fragmentation, or physical RAM equivalence.

## Safety

Each task starts cold. If after an explicit model stop the machine remains below 8% free memory or above 5600 MB swap used, abort remaining tasks and preserve the partial run.

## Failure policy

- one attempt per task;
- no prompt rescue;
- no hidden-test feedback;
- no output repair;
- no rerun under the same run id;
- script defects require a new documented run id.
