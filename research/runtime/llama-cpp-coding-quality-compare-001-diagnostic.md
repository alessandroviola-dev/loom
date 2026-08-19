# LOOM — llama.cpp Coding Quality Compare 001 — Failure-Mode Diagnostic

Date: 2026-08-19
Source run: `20260819-110234`
Status: **CLOSED — Q2 PROFILE STRUCTURED INSTRUCTION/DELIVERY DEGRADATION**

## Purpose

Interpret the six Qwen3-8B Q2_K adapter failures from Coding Quality Compare 001 without rerunning inference or changing the frozen benchmark.

## Resource / transport state

The 8B profile itself completed normally:
- profile classification `COMPLETE`;
- server ready `True`;
- no guardrail abort;
- no execution failure;
- peak process RSS `1953.015625 MB`;
- peak swap `2026.44 MB`;
- minimum free memory `7%`.

Every 8B task returned:
- HTTP 200;
- `stop_type=eos`;
- non-empty model content;
- syntactically valid JSON.

Therefore the 0/100 delivery score is not explained by server failure, timeout, memory guardrail, HTTP failure or malformed JSON syntax.

## 8B Q2 failure pattern

### T01
Expected editable file: `solution.py`.
Observed:
`{"files": {"filename": "solution.py"}}`

Failure: the placeholder word `filename` was used literally as the key; no file contents were supplied.

### T02
Expected editable file: `buggy.py`.
Observed:
`{"files": {"filename": "buggy.py"} }`

Same literal-placeholder failure.

### T03
Expected editable file: `answer.json`.
Observed:
`{"files": {"filename": "answer.json"} }`

Same literal-placeholder failure.

### T04
Expected editable file: `solution.py`.
Observed:
`{"files": {"filename": "solution.py"}}`

Same literal-placeholder failure.

### T05
Expected editable file: `order.py`.
Observed shape:
`{"files": {"filename": "order.py", "value": "<generated code>"}}`

The model generated a substantial code body but encoded it as a generic `filename` / `value` record rather than mapping the exact permitted filename to the complete replacement contents.

### T06
Expected editable file: `solution.py`.
Observed:
`{"files": {"filename": "solution.py"}}`

Same literal-placeholder failure.

## 4B control behavior under identical transport

Qwen3-4B Q4_K_M used the same:
- pinned llama.cpp server;
- raw `/completion` transport;
- context 4096;
- request settings;
- `json_schema={}`;
- benchmark prompt construction;
- adapter parser.

It successfully delivered T01, T02, T05 and T06 in the required exact `{"files": {"actual_filename": "contents"}}` envelope.

T03 and T04 failed because the 4B returned task-answer JSON directly instead of wrapping it in the required `files` envelope. Those failures remain valid benchmark failures.

## Canonical interpretation

The diagnostic does **not** identify a transport/harness defect specific to the 8B condition.

Instead, the tested Qwen3-8B Q2_K profile shows a strong and repeated structured instruction-following failure: it recognizes that a `files` object is required but treats the prompt's illustrative `filename` placeholder as a literal schema field, often terminating after only ~11–13 generated tokens.

T05 shows that semantic code generation ability is not necessarily zero, but the profile still fails the frozen delivery protocol. No post-hoc salvage is permitted for the primary score.

The 8B artifact score of 15/100 is not treated as model-earned quality because failed adapter outputs were not written to the working tree; fixture baseline state can contribute to that raw score.

## Causal boundary

This experiment does **not** prove that Q2 weight quantization alone caused the failure pattern. The compared profiles differ in both parameter count and quantization level. The supported conclusion is narrower: the tested **8B Q2_K profile** is inferior to the tested **4B Q4_K_M profile** on the frozen structured-delivery workload.

Testing the same 8B family at Q3/Q4 quality under a viable memory strategy is required before attributing the degradation specifically to Q2 quantization.

## Conclusion

> Qwen3-8B Q2_K is technically runnable and API-servable on the reference M1/8GB system, but under the frozen Coding Benchmark 01 single-shot protocol this tested profile does not preserve reliable structured instruction following. It is **not a practical upgrade** over Qwen3-4B Q4_K_M for this workload.

Primary result remains unchanged:
- 8B Q2 delivery-adjusted: `0/100`
- 4B Q4 delivery-adjusted: `34.29/100`
- relation: `4B_HIGHER`

## Next research branch

Do not relax the benchmark envelope and do not proceed to Pi or ~9B from this Q2 profile.

Next test a higher-quality 8B representation using a separately preregistered memory strategy, starting with Qwen3-8B Q3_K_M under llama.cpp automatic device-fit / partial-offload policy at the same context 4096 and unchanged LOOM safety guardrails.
