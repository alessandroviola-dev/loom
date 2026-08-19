# Capability Amplifier 003 — T02 Prompt Anatomy

Date: 2026-08-19
Run: `20260819-150342`
Status: **FROZEN READ-ONLY DIAGNOSTIC**

## Purpose

Measure the saved T02 initial and repair prompt footprints after Amplifier 003, without launching a model or changing any benchmark artifact.

Inspector:
`scripts/inspect_amplifier_prompt_anatomy.py`

Target:
`results-local/amplify/capability-amplifier-003-repair-context-3072/20260819-150342`

## Initial prompt

- UTF-8 bytes: **1638**
- characters: **1634**
- lines: **47**
- whitespace-delimited words: **237**

Sections:
- preamble: 453 B
- permitted editable files: 13 B
- task prompt: 681 B
- supplied source files: 432 B

## Repair prompt

- UTF-8 bytes: **4573**
- characters: **4569**
- lines: **90**
- whitespace-delimited words: **442**

Sections:
- preamble: 521 B
- permitted editable files: 13 B
- original task prompt: 681 B
- validation failure type: 21 B
- validation feedback: **2762 B**
- current editable candidate: 458 B

No non-editable source-context section was present for T02.

## Comparison

- repair / initial bytes: **2.792x**
- byte delta: **+2935 B**
- repair / initial characters: **2.796x**
- repair / initial lines: **1.915x**
- repair / initial words: **1.865x**

The validation-feedback section alone accounts for roughly **60.4%** of the full repair prompt by UTF-8 bytes (`2762 / 4573`).

## Raw API evidence

- `T02-initial-api.json`: present
- `T02-repair-api.json`: absent

This is consistent with the resource guardrail aborting before a completed repair response was recorded.

## Interpretation

The repair prompt is materially inflated relative to the initial prompt, and the dominant incremental section is deterministic validation feedback. This provides a prospective rationale for a Compact Repair experiment that changes only feedback serialization/budget while preserving the original task prompt and current candidate.

This diagnostic does **not** establish that prompt length is the sole cause of the memory failure. Amplifier 003 also showed that ordinary 4096-context initial calls reach only 6% free memory, so the current Ollama/MLX 4B execution profile remains intrinsically narrow on the 8 GB reference host.

## Decision

Proceed with one bounded Compact Repair experiment before abandoning prompt-level Amplify work on this profile.

Do not automatically reduce repair context below 3072.
