# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-31
Status: FINAL product persisted; UOPT-001 PARTIAL_GO/persisted; **UOPT-002 GO/persisted; no active macro**

## Purpose

Use substantial Pi macro work packages instead of user-facing micro-checkpoints. Pi records/fixes/reverts routine failures internally and returns only at macro completion or a genuine user-action blocker.

## Finished product

Base product persistence commit:
`98949e77863c93a7d9dba266204a911ab85db09c`.

Latest UNLOCKED optimization persistence commit:
`07223f99e75a44f559270af976ab2d8b52b5edb4`.

Profiles:
1. `loom-deep-30b-s32` — FAST/default;
2. `loom-deep-30b-unlocked` — validated behavioral-unlock profile with promoted UOPT-002 lossless expert-major I/O path.

Final UX:
```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Stable endpoint: `127.0.0.1:18080` loopback only.

WP1 Runtime + Product Serving: GO / persisted.

WP2 Context Intelligence: GO / persisted.

WP3 Behavioral Transform: valid NO_GO for bounded low-rank routes.

WP3-R2 Behavioral Unlock: GO / persisted; frozen result `0/6` refusal, `0/6` held-out degeneration, `8/8` benign.

WP4 Final Integration + Acceptance: GO / persisted.

## UOPT-001 — COMPLETE / PARTIAL_GO / PERSISTED

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_001`

Persistence commit:
`93b5f44733d120a4e9c0f0b1fea6e58309f71ccd`.

Retained source-UNLOCKED rollback `-ub 2`; FAST remains `-ub 1`.

Matched retained metrics:
- decode `2.579 -> 3.161 tok/s`;
- ~1,150-token cold TTFT `433.558 -> 393.983 s`;
- warm long-prefix TTFT `0.195 -> 0.190 s`.

All behavior/capability/integration gates passed. Broad current-runtime tuning was exhausted; expert paging/cold prefill remained the bottleneck.

## UOPT-002 — COMPLETE / GO / PERSISTED

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_002`

Persistence commit:
`07223f99e75a44f559270af976ab2d8b52b5edb4`.

Contract:
`research/integration/loom-unlocked-speed-optimization-002.md`

Result:
`research/integration/loom-unlocked-speed-optimization-002-result.md`

Promoted local artifacts:
- unchanged source/rollback GGUF `models/loom-deep-30b-unlocked.gguf`, SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- lossless expert-major sidecar `models/unlocked-expert-major-v1.bin`, size `12,457,082,880` bytes, SHA256 `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`;
- isolated runtime `.loom/runtime/loom-uopt002/llama-server`, SHA256 `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`.

These large/runtime artifacts remain local and outside Git. The committed patch and build scripts reproduce the isolated runtime/sidecar path.

Architecture:
- lossless expert-major reordering of routed-expert bytes;
- unchanged Qwen3 router, top-k and model math;
- one sidecar `preadv` path per miss instead of three source-GGUF reads;
- UNLOCKED product uses `-ub 4`;
- persisted UOPT-001 source path remains rollback at `-ub 2`.

Final acceptance:
- fresh decode full-GO target >= `5.0 tok/s`: PASS, `6.903 tok/s` final promoted confirmation; validated candidate median `7.359`;
- 1,155-token cold TTFT target <= `184 s`: PASS, `162.726 s` final promoted confirmation; validated candidate `156.949 s`;
- frozen refusal `0/6`: PASS;
- held-out degeneration `0/6`: PASS;
- benign `8/8`: PASS;
- deterministic source-vs-sidecar A/B exact: PASS;
- API/WebUI/Pi+WP2/cache/loopback: PASS;
- FAST + UOPT-001 rollback: PASS;
- source UNLOCKED and FAST hashes unchanged;
- no `external archive` runtime dependency;
- final state after acceptance: FAST + WP2 healthy.

## Current action

No macro is active. UOPT-002 is closed and promoted.

Any new optimization or product-policy change must begin with a new explicit macro contract. Do not silently extend UOPT-002.

## Global execution rules

1. Evidence over narrative.
2. Do not return after routine experiment NO_GO results inside an authorized macro.
3. Never relax frozen gates after seeing results.
4. Preserve exact provenance and hashes.
5. Keep known-good FAST and UNLOCKED rollback baselines unless a later explicit policy change retires them.
6. No public internet exposure by default.
7. No SIP/security disabling or destructive unrelated cleanup.
8. Large local models/sidecars remain outside Git.
9. External benchmark claims are hypotheses until locally reproduced.
10. Never destructively modify stable model artifacts.
11. Pi commits only under the explicit bounded macro-boundary exception.
