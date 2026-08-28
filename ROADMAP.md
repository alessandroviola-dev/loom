# LOOM Roadmap

Last updated: 2026-08-28
Current: canonical LOOM 30B v1 code persisted at `d3691b7`; historical runtime class `FUNCTIONAL_SLOW`
Immediate next: real manual terminal conversation
Canonical context: `/AGENTS.md` v3.49.

## 1. Frozen 30B research baseline

Qwen3-30B-A3B exact-Q4/top-8:
- backend commit `96958de`;
- sustained 3×32 `1.115874`, `1.229233`, `1.254611 tok/s`;
- research median `1.229233 tok/s`;
- exactness/safety PASS.

Closed current-verifier speed paths:
- routing sparsity: no acceptable gain;
- Q2/Q3 from deployed Q4: fidelity fail;
- DFlash: closed;
- real speculative drafter: not justified because perfect-oracle K=4 verifier ceiling is only `1.792925 tok/s` median.

## 2. Qwen3.8 — parked

Metadata-only readiness: `QWEN38_BOTH_PORTABLE`.
Qwen3.8-27B dense projected external traffic: `13.702 GB/token`.
Qwen3.8-Flash-Next projected external baseline: `3.858 GB/token`.
Do not spend large downloads now; revisit after practical model-size/architecture bake-off or a materially new mechanism.

## 3. LOOM 30B Interactive Runtime v1 — canonical code

Historical functional result:
`LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`.

Long-form:
- TTFT `47.832 s`;
- decode `1.116 tok/s`;
- end-to-end `0.921 tok/s`.

Functional validation PASS:
- semantic parity;
- exact incremental multi-turn state reuse;
- streaming;
- 3-turn/5-turn memory and stability;
- zero SOURCE fallback/cache.

Canonicalization repair: GO.
EOS-finalize repair: GO.

Production commit:
`d3691b765004849abb01a7675e5a6e7c5d0edd4c`.

Canonical runtime files:
- `scripts/loom_30b_runtime_core_v1_001.py` SHA `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` SHA `44b89ba34d597a3c9798c7ad1c081aa0eeff865cc5320e27213b3c6ebe4a5322`.

Remote compare proves the commit adds only those two files.

## 4. Current — manual LOOM 30B v1 session

Launch committed runtime from project root using validated environment:

`.venvs/stretch030-mlx0320-fix1/bin/python scripts/loom_30b_interactive_v1_001.py`

Manual checklist:
- ask normal free-form questions;
- ask a follow-up requiring prior-turn context;
- observe practical TTFT and streaming quality;
- `/reset` and verify conversational state clears;
- `/exit` and verify clean termination.

No model/runtime modifications during this session. Manual impressions supplement but do not replace objective benchmark numbers.

If acceptable, freeze **LOOM 30B v1 FUNCTIONAL_SLOW** as the large practical comparator.

## 5. Next scientific decision — 30B vs 8B vs 4B

Run one matched Qwen-family 8B and one 4B baseline on the same M1/8GB.

Primary question:
**How much correct/useful work is produced per unit of waiting time and memory?**

Measure:
- TTFT;
- sustained decode tok/s;
- RAM/swap;
- disk footprint;
- end-to-end task time;
- fixed practical intelligence across reasoning/math, coding, debugging, Italian technical explanation, structured instruction following, supplied-context reasoning and planning/tool-use decisions.

Possible decisions:
- 30B primary/deep;
- 8B fast primary + 30B escalation;
- 4B/8B skill/tool/protocol-centric primary, 30B only where measured benefit justifies latency.

## 6. Small-model intelligence amplification

After size bake-off:
- dynamically retrieved skills/protocols;
- planner -> executor -> verifier workflows;
- Python/calculator/filesystem/Git/web/RAG tools;
- persistent/retrieved memory;
- test-time retries/candidate verification;
- task-specific LoRA/distillation with frozen eval gates;
- optional routing from fast small model to 30B deep mode.

## 7. Behavioral/refusal editing

Use `LOOM_HERETIC_TECHNICAL_PAPER.md` only after runtime roles are selected. Freeze refusal/steerability and capability-preservation gates; do not make unmeasured absolute guardrail-free claims.

## 8. Separate 30B speed R&D

Do not block product work. Materially new hypotheses include direct higher-precision -> mixed-bit expert quantization, fused Metal packed-Q4 expert kernel, vectored/grouped expert reads, trace-driven bounded cache simulation, and TTFT/prefill optimization if manual use justifies it.

Final project architecture is chosen from measured practical utility.