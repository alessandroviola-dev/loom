# LOOM Roadmap

Last updated: 2026-08-30
Current: user-directed acceleration mode. Prompt Cache R2 is validated GO. The prior paging/I/O tracing preflight completed NO_GO because current external native tracing could not validate a high-value per-process read observable. Rather than continue user-facing micro-checkpoints, LOOM is now executing one autonomous full-capability integration sprint with internal evidence gates.
Canonical context: `/AGENTS.md` v3.78.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional lighter tier.
- `loom-deep`: Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging S24.
- historical custom MLX ~1.4 tok/s: historical fallback/comparison only.
- `loom-fast`: later clean-runtime tier.
- LOOM AUTO validator/guided repair remains secondary until the integrated local model path is usable.
- behavioral freedom/decensoring remains mandatory for full promotion.

## 2. Canonical DEEP baseline

Stage2 product GO already promoted Apple S24 to canonical DEEP.

Validated fresh-process decode baseline:
~4.39–4.40 tok/s.

Canonical model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Canonical source baseline:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

## 3. Validated prompt cache

`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`.

Stable-prefix result:
- median prompt-eval C/B `0.04025`;
- median E2E C/B `0.10751`;
- decode preservation `99.43%`.

Prompt cache is accepted for reusable stable-prefix prefill/E2E acceleration.

## 4. Paging/I/O observation result

`LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_NO_GO`.

Current external observation tools did not provide a validated high-value per-process read measurement in the active session.

This does not reject paging optimization. It authorizes the full sprint to use isolated source-level measurement instrumentation, overhead calibration and A/B testing internally.

## 5. Current — Full Capability Integration Sprint 001

Contract:
`research/integration/loom-full-capability-integration-sprint-001.md`

The sprint is one autonomous Pi task with internal phases/gates.

Primary final deliverables:
1. persistent local DEEP serving;
2. localhost API, preferably OpenAI-compatible;
3. usable browser chat UI;
4. Pi connected to and validated against LOOM;
5. prompt cache and best validated runtime acceleration enabled;
6. decode optimization pushed toward >=5 tok/s where evidence supports it;
7. lightweight local tracing/measurement;
8. deterministic context packing + progressive project memory when net-positive;
9. actual behavior/adapter-level decensoring profile using Heretic or a technically valid LOOM-native equivalent;
10. capability/resource preservation validation;
11. simple start/stop/health workflow and durable operational docs.

## 6. Repository-paper mechanisms available to the sprint

- mini-SGLang: KV/prefix caching, chunked prefill, scheduling and prefetch/overlap concepts.
- Caveman: deterministic typed compression, token-budget packing, recovery handles.
- Cavemem: progressive local memory.
- LoopX: durable external state and compact re-entry packets.
- pi-dynamic-workflows: bounded optional orchestration/journaling.
- Observal: local tracing/accounting/replay philosophy.
- Heretic: contrastive residual-direction behavioral editing.

Use mechanisms selectively; do not install large upstream stacks merely to satisfy a checklist.

## 7. Internal runtime optimization stopping rule

Prompt cache is already retained.

For decode, Pi may instrument/patch/build isolated candidates and perform repeated A/B tests.

- target >=5 tok/s first;
- continue higher only while evidence shows credible low-risk headroom;
- after three materially different evidence-backed interventions fail to beat the best validated runtime, stop micro-optimization and finish integration;
- revert regressions/broken candidates automatically.

## 8. Full-promotion requirement

A final `LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_GO` requires:
- operational runtime/API/web/Pi integration;
- acceptable performance/stability;
- actual model/adapter-level behavioral-freedom transform;
- preservation/resource evidence.

If product integration is complete but an evidenced physical/toolchain limitation prevents the actual behavioral transform on the M1 8 GiB host, classify:
`LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_PRODUCT_GO_BEHAVIOR_BLOCKED`.

Do not call a prompt-only jailbreak a completed Heretic/decensoring stage.

## 9. After the sprint

Only after the end-to-end local product exists should LOOM return to lower-priority research such as:
- deeper capability amplifier/validator work;
- more aggressive context packing;
- broader memory systems;
- FAST tier;
- additional quantization/model candidates;
- polished provider/UI distribution.
