# Pi Agentic Coding Benchmark 001 — Preliminary Result

Date: 2026-08-18
Run id: `20260818-214848`
Status: **COMPLETED — PRELIMINARY, METRIC/TASK INGESTION PENDING**

## Frozen configuration

- Benchmark: LOOM Coding Benchmark 01 v1.0.1
- Agent harness: Pi 0.84.2
- Provider/runtime: Ollama
- Model: `qwen3.5:4b-mlx`
- Context: 4096
- Max output: 2048
- One attempt per task
- Hidden tests excluded from agent workspaces
- Exposed tools: file tools only (`read,write,edit`), no bash/test feedback
- Run-local isolated `PI_CODING_AGENT_DIR`
- User production Pi configuration not loaded or modified
- Scoring protocol preregistered in `research/agents/pi-agentic-benchmark-001-plan.md`

## Terminal result

```text
[1/6] T01 delivery=PASS protocol=PASS
[2/6] T02 delivery=PASS protocol=FAIL
[3/6] T03 delivery=PASS protocol=FAIL
[4/6] T04 delivery=PASS protocol=PASS
[5/6] T05 delivery=PASS protocol=PASS
[6/6] T06 delivery=PASS protocol=PASS

Artifact score: 77.15/100
Delivery-adjusted score: 77.15/100
Strict protocol-adjusted score: 60.0/100
Delivery success: 6/6; protocol success: 4/6
```

Run directory:
`results-local/coding-agentic-pi/20260818-214848`

Summary:
`results-local/coding-agentic-pi/20260818-214848/run-summary.json`

## Immediate comparison with frozen single-shot baseline

Single-shot Baseline 001:
- artifact score: **40.71/100**
- strict delivery-adjusted score: **30.00/100**
- structured-output delivery success: **3/6**
- recovered semantic-content diagnostic: **82.86/100**

Pi agentic preliminary:
- artifact score: **77.15/100**
- delivery-adjusted score: **77.15/100**
- strict protocol-adjusted score: **60.00/100**
- delivery success: **6/6**
- protocol success: **4/6**

Deltas versus canonical single-shot views:
- artifact: **+36.44 points** (`40.71 -> 77.15`)
- strict: **+30.00 points** (`30.00 -> 60.00`), exactly 2x the single-shot strict score
- delivery reliability: **50% -> 100%** (`3/6 -> 6/6`)

The agentic artifact score remains **5.71 points below** the recovered single-shot semantic-content diagnostic (`82.86 -> 77.15`). That recovered score is diagnostic rather than a strict end-to-end delivery score, so it must remain a separate comparison axis.

## Preliminary interpretation

The central LOOM hypothesis is strongly supported at the preliminary level:

> Replacing full-file JSON transport with direct filesystem delivery through an agent harness removes the dominant delivery bottleneck and materially improves end-to-end coding performance of the same local 4B model at context 4096.

However, protocol reliability remains imperfect:
- all six tasks delivered their required artifacts;
- T02 and T03 violated the preregistered strict protocol condition;
- the strict score therefore remains materially below the artifact/delivery score.

No task-level semantic interpretation is frozen yet. The exact task scores, final texts, file/tool events, timings, memory/swap trajectory and any adapter anomalies must be ingested from `run-summary.json` before the result becomes canonical.

## Required next step

Inspect the complete run summary and verify:
1. T01–T06 points earned and tests passed;
2. exact protocol failure reason for T02 and T03;
3. per-task tool sequences and final texts;
4. whether all non-editable inputs remained unchanged;
5. any unexpected persistent files or adapter errors;
6. total and per-task runtime;
7. memory pressure, swap and `ollama ps` state;
8. whether any evidence invalidates the preregistered isolation/failure policy.

Only after this ingestion should the result be frozen as the canonical Pi Agentic Coding Benchmark 001 result.
