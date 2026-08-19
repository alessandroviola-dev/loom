# LOOM — Direct MLX Coding Benchmark 001 Quality Diagnostic

Date: 2026-08-19
Run: `20260819-125647`
Status: **CLOSED — RESOURCE/STABILITY PASS, QUALITY NOT PROMOTED**

## Scope

Read-only diagnosis of the persisted Direct MLX Coding Benchmark 001 result. No model rerun, prompt change, parser change, salvage, repair, or rescoring rule is introduced.

Frozen primary result:
- artifact score: **38.57/100**
- delivery-adjusted score: **27.86/100**
- structured delivery: **2/6**
- full-session minimum free memory: **14%**
- full-session peak swap: **1683.38 MB**
- classification: **COMPLETE**

## Per-task diagnosis

### T01 — clean protocol + semantic PASS
- adapter: `written`
- frozen scorer: **15.0/15**
- tests: **6/6**
- output had the exact `files -> solution.py` envelope.

This is unambiguous model-earned success.

### T02 — clean protocol, near-semantic PASS
- adapter: `written`
- frozen scorer: **12.86/15**
- tests: **6/7**
- output had the exact `files -> buggy.py` envelope.
- missed the invalid-size case that expected `ValueError`.

This is model-earned partial semantic success.

### T03 — protocol/delivery failure dominates
- adapter: `failed`
- exact error: `JSONDecodeError: Extra data: line 3 column 1 (char 206)`
- scorer: **0/15**, tests **0/7**, because `answer.json` was never written.
- the raw response first emitted a valid-looking `{"files":{"answer.json": ...}}` payload, then appended a second fenced JSON block.

The frozen no-salvage policy correctly rejects the whole response. The first payload appears semantically plausible, but its correctness is **not scored or promoted** because the model violated the delivery contract.

### T04 — protocol failure plus independent content defect
- adapter: `failed`
- exact error: `JSONDecodeError: Extra data: line 1 column 917 (char 916)`
- scorer: **8.57/15**, tests **4/7**.
- because delivery failed, those artifact points come from the untouched isolated fixture/base file and are **not model-earned delivery-adjusted points**.
- the generated candidate itself also contains an apparent malformed return structure (`}`/`]` mismatch) despite defining `_coerce_score`.

Therefore T04 is not a protocol-only miss.

### T05 — protocol failure; semantic result not validated
- adapter: `failed`
- exact error: `JSONDecodeError: Extra data: line 1 column 842 (char 841)`
- scorer: **0/25**, tests **0/7**, because generated `order.py` was not written.
- raw output contains a substantial candidate implementation, but testing it would require post-hoc salvage, which is forbidden for this run.

No semantic credit is assigned.

### T06 — protocol failure plus visible semantic defect
- adapter: `failed`
- exact error: `JSONDecodeError: Extra data: line 1 column 929 (char 928)`
- scorer: **2.14/15**, tests **1/7** from the untouched fixture/base file; not model-earned delivery-adjusted points.
- the generated candidate sorts equal-frequency items using value comparison, conflicting with the frozen requirement that ties preserve first appearance.

Therefore T06 also contains semantic/instruction-following weakness independent of the delivery failure.

## Delivery accounting

Frozen delivery-adjusted contributions:
- T01: 15.00
- T02: 12.86
- T03: 0
- T04: 0
- T05: 0
- T06: 0

Total: **27.86/100**.

The artifact score **38.57/100** must not be interpreted as model-earned quality for failed-delivery tasks because the isolated benchmark copy retains baseline fixture files when `extract_files()` rejects an output.

## Canonical interpretation

> Direct MLX Qwen3-8B 3-bit clearly solves the resource/stability problem on the reference M1/8 GB machine, but the frozen coding-quality run does not establish a practical quality upgrade. Four of six tasks violate the exact structured-delivery contract, and at least T04 and T06 also show independent content/instruction defects. T03 is primarily a protocol failure; T05 semantic quality remains unresolved because no post-hoc salvage is allowed.

This is stronger than saying the result is "just JSON formatting": protocol failure is the dominant delivery issue, but semantic weakness is also present.

## Comparison boundary

Historical references are descriptive only:
- Ollama/MLX 4B Coding Baseline 001: artifact 40.71, strict 30.00, delivery 3/6.
- llama.cpp 4B Q4 in Compare 001: delivery-adjusted 34.29, delivery 4/6.
- Direct MLX 8B 3-bit: delivery-adjusted 27.86, delivery 2/6.

Runtimes, model formats and quantization conditions differ, so these gaps do not prove a causal parameter-count or quantization effect. They do show that the 8B/3-bit profile has **not earned promotion to Pi on quality evidence**.

## Decision

Do not authorize Pi integration for the 8B/3-bit profile as the main candidate.

The next main-branch experiment is a same-family, less aggressive Direct MLX quantization: `mlx-community/Qwen3-8B-4bit`, starting with a separately preregistered technical/safety smoke. This tests whether additional weight precision can improve the useful-quality frontier while preserving the Direct MLX memory advantage.
