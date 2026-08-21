# LOOM — ChatGPT / Pi operating protocol

Date: 2026-08-21
Status: ACTIVE

## Purpose

LOOM is entering a more exploratory research phase. Token budget and agent attention must be spent on implementation and experiments, not repetitive repository administration.

## Role split

### Pi / local execution agent

Pi is used only for high-value local work:

- write or modify serious experiment/runtime code;
- inspect local runtime/source state when required by the experiment;
- execute benchmarks and tests;
- collect raw evidence and concise result summaries;
- stop on experiment gates or unexpected failures.

Pi should NOT spend turns on routine project administration unless explicitly required for a local code/test dependency:

- no routine Git synchronization;
- no routine commits/pushes;
- no HANDOFF updates;
- no ROADMAP updates;
- no verbose historical recap;
- no repeated repository-status ceremony beyond the minimum needed to protect a local experiment.

For local safety before code/test work, Pi may report only the minimum branch/dirty-tree facts needed to avoid overwriting work.

### ChatGPT / research coordinator

ChatGPT owns:

- scientific direction and experiment design;
- review of Pi results;
- comparison with previous evidence;
- deciding GO / NO-GO / next factor;
- GitHub synchronization and repository administration;
- commits/pushes when supported by the connected GitHub tooling;
- HANDOFF maintenance;
- ROADMAP maintenance;
- preserving canonical checkpoints and experimental provenance.

The default workflow is therefore:

1. ChatGPT defines the research question and sends Pi a code/test-only prompt.
2. Pi implements and runs the experiment locally.
3. Pi returns concise raw results plus changed-file paths.
4. ChatGPT reviews the evidence.
5. ChatGPT performs repository/documentation synchronization.
6. ChatGPT defines the next experiment.

## Research promotion rule

From this point forward, an optimization is not considered useful because it only reduces RAM or only increases throughput.

Every major direction must be evaluated on three axes:

1. **Memory** — resident/peak memory, swap, model bytes and headroom.
2. **Speed** — real autoregressive tok/s, TTFT and relevant latency.
3. **Capability** — whether the resulting system can still perform useful real tasks.

LOOM's objective is not merely to make a model fit into 8 GB. The objective is to run the strongest practical LLM possible on 8 GB while retaining usable performance and capability.

## Current architectural principle

Pure full-model layer streaming is already known to reduce RAM substantially while destroying throughput. Do not repeat it as a final solution.

Future memory-hierarchy work should search for the best **residency / streaming / prefetch overlap frontier**: keep as much of the model resident as possible, stream only the unavoidable cold portion, and measure RAM saved against real tok/s lost.
