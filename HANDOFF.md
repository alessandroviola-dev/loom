# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — LOOM is optimizing useful capability rather than resident model size on the Apple M1 / 8 GB reference system. Amplifiers 001–003 established that the current Ollama/MLX 4B profile has extremely narrow memory headroom for multi-call repair workflows. Call isolation works, and reducing repair context from 4096 to 3072 changes pressure but still fails the 5% free-memory guardrail. Before designing another amplifier, measure the actual repair-prompt footprint.
Checkpoint: `CAPABILITY_AMPLIFIER_REPAIR_PROMPT_ANATOMY`

## Mission

Study practical local LLM/agent execution on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / research constraints

- Never reset, replace or destroy production Pi configuration.
- Controlled Pi experiments use run-local `PI_CODING_AGENT_DIR`.
- Never silently delete verified models or canonical results.
- Record disk around model acquisitions / large runtime work.
- Runtime safety boundary: free memory <5% OR swap >5600 MB abort.
- System-wide free memory and swap are decisive; process RSS is diagnostic only.
- Do not relabel harness/parser/capture defects as model failures.
- Do not assign aggregate quality scores to partial resource/runtime runs.
- Change one experimental factor at a time when testing causal operational hypotheses.
- Do not weaken guardrails post-hoc.
- No automatic context-reduction rescue ladder.

Verified 3-bit, 4-bit and GGUF artifacts remain retained.

# Frozen references

## Canonical Ollama/MLX 4B

Model: `qwen3.5:4b-mlx`, context 4096.

Coding Baseline 001 (`20260818-203156`):
- artifact 40.71/100
- strict/delivery-adjusted 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt throughput 186.46 tok/s
- generation 16.01 tok/s.

Pi Agentic Coding Benchmark 001 (`20260818-214848`):
- artifact/delivery-adjusted 77.15/100
- strict protocol-adjusted 60.00/100
- delivery 6/6
- protocol 4/6
- no hidden-test feedback
- whole run ~612 s.

## llama.cpp 4B efficiency reference

Qwen3-4B Q4 control:
- pp512 230.85 tok/s
- tg128 22.33 tok/s
- minimum free memory 22%.

This remains an important alternate Amplify subject. It is not the same model/runtime condition as `qwen3.5:4b-mlx`, so future comparisons must be framed as capability/efficiency comparisons, not one-factor causal comparisons.

# Research pivot

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Long-term tracks:
1. **Amplify — small model, big capability**: validation/repair, planner/verifier/tool loops, retrieval, later specialization/distillation.
2. **Stretch — big model, small machine**: SSD/layer/expert streaming, MoE offload, hierarchical caching, small resident controller + selectively invoked larger component.

Joint frontier metrics: quality/delivery, free memory/swap, wall time, model calls, prompt/generated tokens, disk footprint where relevant.

# Phase 6 — Capability Amplification

## Amplifier 001 — warm-resident

Runner blob: `9f472c60b523762276291232f6e8c6ffc1c5fcae`
Diagnostic: `research/amplify/capability-amplifier-001-resource-diagnostic.md`

Run `20260819-142640`:
- host gate 74/74/74% free
- T01 initial 6/6, 15/15
- T02 initial 3/7, 6.43/15
- T02 repair triggered
- `PARTIAL_RESOURCE_FAIL`: free 4% <5%
- peak swap 2500.88 MB
- no aggregate quality score.

Interpretation: warm continuous Ollama residency lacks sufficient headroom. Do not call this a leak.

## Amplifier 002 — call-isolated

Runner blob: `df332568820e28c90baa5247df27e92cba43c0d6`
Diagnostic: `research/amplify/capability-amplifier-002-resource-diagnostic.md`

One changed factor vs 001: unload and confirm target absent from `ollama ps` before/after every model call.

Valid run `20260819-144256`:
- host gate 71/72/72% free
- T01 initial 6/6
- T02 initial 3/7
- model unload confirmed
- T02 repair starts 68% free / 2346.94 MB swap
- repair trajectory 68 -> 63 -> 23 -> 16 -> 4% free
- `PARTIAL_RESOURCE_FAIL`
- peak swap 2611.50 MB.

Interpretation: call isolation works operationally but is insufficient. A recovery gate alone is not the leading fix.

## Amplifier 003 — repair context 3072 — FROZEN RESOURCE FAIL

Plan: `research/amplify/capability-amplifier-003-repair-context-3072-plan.md`
Runner: `scripts/capability_amplifier_003_repair_context_3072.py`
Runner blob: `c2bcc8f126eb5b599645ba12d1fd08a348e2b443`
Diagnostic: `research/amplify/capability-amplifier-003-resource-diagnostic.md`

Single changed factor vs 002:
- initial calls remain `num_ctx=4096`
- repair calls use `num_ctx=3072`.

Attempt `20260819-150107`:
- 69% free
- `HOST_STATE_NOT_READY`
- 0 model calls
- not a scientific model result.

Valid run `20260819-150342`:
- host gate 71/74/74% free; swap 1247.88 MB
- disk 36.344 -> 35.342 GiB free
- classification `PARTIAL_RESOURCE_FAIL`
- exact reason `memory free 4% < 5%`
- whole wall 48.841 s
- overall peak swap 2318.12 MB
- no aggregate quality score.

T01 initial:
- context 4096
- 6/6, 15/15
- prompt 301, gen 98
- 15.042 tok/s
- wall 11.791 s
- min free 6%.

T02 initial:
- context 4096
- 3/7, 6.43/15
- prompt 406, gen 118
- 16.199 tok/s
- wall 12.918 s
- min free 6%.

T02 repair decisive evidence:
- isolation confirmed
- `call_context=3072`
- starts **70% free / 2069.12 MB swap**
- trajectory **70 -> 65 -> 31 -> 7 -> 6 -> 4% free**
- no completed repair API response
- post-abort unload returns 70% free.

Canonical interpretation:
> A 25% repair-context reduction from 4096 to 3072 changes the observed pressure trajectory and lowers peak swap relative to Amplifier 002, but does not prevent the same free-memory safety breach. The 3072 repair began from a recovered 70%-free state and still failed.

Do not infer a specific KV-cache, allocator, prompt-only, MLX, or Ollama root cause.
Do not automatically try repair context 2048.

Additional observation:
- successful T01/T02 initial calls themselves reach only 6% free, leaving very little operating margin in the current Ollama/MLX 4B profile.

# Current checkpoint — repair prompt anatomy

Checkpoint: `CAPABILITY_AMPLIFIER_REPAIR_PROMPT_ANATOMY`

Inspector:
`scripts/inspect_amplifier_prompt_anatomy.py`

Target run:
`results-local/amplify/capability-amplifier-003-repair-context-3072/20260819-150342`

Purpose:
- compare saved T02 initial vs repair prompt footprint;
- count UTF-8 bytes, characters, lines and whitespace-delimited words;
- break repair prompt into preamble, original task, validation feedback, candidate and non-editable context;
- confirm repair raw API response is absent;
- no model launch and no mutation.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/inspect_amplifier_prompt_anatomy.py
python3 scripts/inspect_amplifier_prompt_anatomy.py \
  results-local/amplify/capability-amplifier-003-repair-context-3072/20260819-150342 \
  --task T02
```

## Decision after prompt anatomy

1. If repair prompt is materially inflated relative to initial, preregister **Compact Repair** as the next one-factor architecture: keep model, 3072 repair context, call isolation, validation, max-one-repair, scorer and guardrails; change only repair information serialization/prompt budget.
2. If repair prompt is already relatively compact, stop treating prompt reduction as the leading fix. Re-evaluate the primary Amplify execution profile, with the previously validated llama.cpp 4B as the strongest alternate due to substantially larger observed memory headroom and higher throughput.
3. Do not automatically descend to context 2048.

## Continuation rule

After every meaningful result/decision, update this file and `ROADMAP.md` before moving to the next checkpoint.
