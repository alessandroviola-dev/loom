# LOOM Roadmap

Last updated: 2026-08-30
Current: WP1 Runtime + Product Serving GO and fully persisted. WP2 Context Intelligence GO and persisted. WP3 original GGUF-LoRA families completed valid NO_GO. **WP3-R2 Behavioral Unlock completed locally with GO** using the Huihui Q3_K_S replacement. R2 persistence is pending. WP4 remains not authorized.
Canonical context: `/AGENTS.md` v3.88.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
R2 contract: `research/integration/loom-behavioral-unlock-wp3-r2.md`.

## 1. Canonical product profiles

### Fast/default DEEP
- `loom-deep-30b-s32`;
- Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw;
- Apple Metal MoE paging S32;
- validated median decode `5.596 tok/s`;
- persistent localhost `llama-server`;
- Caveman + Cavemem enabled through WP2.

### Behavioral-unlocked DEEP
- intended product label: `loom-deep-30b-unlocked`;
- selected R2 candidate: `Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`;
- local SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- frozen explicit refusals `6/6 -> 0/6`;
- frozen benign capability `8/8 -> 8/8`;
- stable local API/WebUI and real Pi + WP2 request;
- slower, about `55%` of fresh S32 decode under R2 comparison;
- materially higher swap pressure;
- behavioral/disposition drift must remain documented.

Do not silently replace the fast/default profile with the unlocked profile. Both are useful and should remain selectable.

## 2. WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

## 3. WP2 — Context Intelligence — COMPLETE / GO / PERSISTED

Classification:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`

Implementation commit:
`0e249f8f5cfaf89398d01e2ee50281fb75b86cd7`

Result:
`research/integration/loom-context-intelligence-wp2-result.md`

Evidence:
`results-local/context-intelligence-wp2/20260830T133259Z/`

Validated Context Intelligence remains Caveman deterministic compression/recovery + Cavemem project memory, with `23.24%` median heavy-context input reduction, `0%` no-op overhead and `6/6` exact recovery.

## 4. WP3 — Behavioral Transform — COMPLETE / VALID NO_GO

Rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA candidates were all actually served but retained the original frozen refusal result `6/6`. Those three bounded adapter families are rejected.

## 5. WP3-R2 — Behavioral Unlock — COMPLETE LOCALLY / GO

Classification:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO`.

Local result:
`research/integration/loom-behavioral-unlock-wp3-r2-result.md`

Evidence:
`results-local/behavioral-unlock-wp3-r2/20260830T160845Z/`

Selected Candidate A is the exact-lineage Huihui abliterated Q3_K_S replacement. It achieved `100%` relative reduction on the frozen held-out explicit-refusal gate (`6/6 -> 0/6`) while benign capability remained `8/8` and degeneration did not increase under the frozen evaluation.

Candidate A passed loopback API/WebUI, a real Pi + WP2 request and rollback verification. Canonical S32 + WP2 is active again on port `18080` after the R2 run.

R2 GO does not erase its performance/resource tradeoff: fresh decode was about `55%` of fresh baseline and swap pressure was high.

## 6. Current persistence action

Persist only the bounded R2 reproducibility/product-profile package:
- R2 result document;
- frozen R2 controls/eval specs;
- small reusable R2 scripts/configuration/provenance needed to operate or reproduce the selected unlocked profile.

Exclude the ~13 GB GGUF, `results-local/`, caches, temp environments, secrets, home config and unrelated historical scripts.

## 7. WP4 — FINAL INTEGRATION + ACCEPTANCE — PLANNED / NOT AUTHORIZED

WP4 should validate the two-profile product:
- fast/default S32 + WP2;
- unlocked Candidate A + WP2.

Required final acceptance includes profile selection/switching, API/WebUI/Pi, clean rollback, capability, decode/prefill/E2E, RAM/swap and exact provenance/hashes for both.
