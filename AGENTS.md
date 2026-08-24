# LOOM — Pi Agent Protocol

Version: 1.2
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is the persistent context for Pi. Do not require long prompts that restate it.

## Role split — local override

Pi owns only local technical execution:
- inspect relevant local code/runtime;
- write the minimum code required by the active work package;
- run tests/benchmarks;
- create local evidence under `results-local/`;
- diagnose and mechanically self-correct inside scope.

ChatGPT owns:
- scientific direction and experiment selection;
- Git/GitHub synchronization;
- `HANDOFF.md`, `ROADMAP.md`, research result documents and project-state administration.

Therefore Pi must NOT run Git operations, edit `HANDOFF.md`/`ROADMAP.md`, open PRs, merge, push, or create project documentation unless the work package explicitly overrides this rule.

## Token-efficiency rules

Use tokens for execution, not narration.

1. Read this file, then only files/evidence explicitly relevant to the work package.
2. Use targeted search (`rg`, exact paths); do not scan the whole repo without need.
3. Do not restate project history or the prompt.
4. Do not create notes, research dumps, changelogs or extra documentation.
5. Do not print full logs; preserve them locally and return only decisive evidence.
6. Do not refactor or change architecture outside the requested variable.
7. Distinguish measured fact, inference, hypothesis and unverified limit.
8. Mechanical failures may be diagnosed/fixed autonomously inside scope; do not broaden the scientific experiment as a rescue.
9. A failed preregistered treatment remains failed; no silent parameter changes.
10. Stop on scientific ambiguity, safety/destructive action, missing required artifact, or a gate that explicitly says STOP.

## Scientific loop

`OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`

Preserve one-factor experiments, deterministic inputs, exactness/parity gates, provenance and explicit failure classifications.

## Stable LOOM target context

Reference machine: Apple M1 / 8 GB unified memory.

Target model:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Canonical anatomy:
- 48 MoE layers; 128 routed experts/layer; top-k 8;
- full stored tensor payload: 16,220,499,968 B;
- resident non-routed backbone: 819,015,680 B;
- external routed bank: 15,401,484,288 B;
- one expert: 2,506,752 B;
- zero-cache expert payload: 962,592,768 B/token;
- BF16 KV: 98,304 B/token.

Proven invariants:
- external serial-expert math is bitwise exact;
- full 48-layer forward/logits are exact;
- only one routed expert needs to be live at a time;
- production-like lifecycle uses `GC_END_ONLY`; never add per-expert `gc.collect()` or per-expert RSS subprocesses to timed paths;
- on-disk expert-major `9 ranges -> 1 contiguous read` is lossless and materially faster when available;
- source-range access remains the general fallback for arbitrary un-packed experts;
- 4-GiB raw `GLOBAL_LRU` cache is `MEMORY_FAIL`: ~80.9% hits were real but swap grew +2.41 GiB and decode slowed. Do not reuse this design unless a future work package explicitly revisits it;
- persistent live-MLX expert cache is not currently promoted;
- full 14.344-GiB expert pack is not automatically authorized.

DFlash exact-target static invariant:
- candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`;
- BF16 safetensors 1,362,042,120 B (~1.2685 GiB), 680,813,824 learned weight elements;
- 5 draft layers, H=2048, block=8 / proposals=7;
- exact target taps `[1,12,23,34,45]`, concatenated to 10,240 then fused to 2048;
- static M1/8-GB fit is plausible, but current LOOM/MLX has **no native DFlash integration path**;
- do not integrate the drafter until target-tap capture/parity and multi-position target verification are separately proven.

DFlash target-interface invariant:
- `LOOM_DFLASH_TARGET_INTERFACE_001_PASS`;
- tap IDs `[1,12,23,34,45]` are 1-based post-block outputs (`layers[i-1]`);
- prefill tap shape `[1,28,2048]`, decode `[1,1,2048]`, dtype `float32`;
- logical tap payload: 1,146,880 B prefill / 40,960 B decode;
- taps-enabled target remains router/logit/token bitwise exact;
- MLX peak delta measured +18,612,224 B, RSS high-water unchanged, swap delta 0;
- captured tap references are released before the next forward and routed-expert ownership remains zero;
- next prerequisite is multi-position/block target verification; do not integrate DFlash weights before it passes.

For volatile project state, read `HANDOFF.md` only when the active work package explicitly needs it. Do not edit it.

## Work-package contract

A normal prompt may now be only:

```text
LOOM WP <id>
Goal: ...
Inputs: exact files/evidence to inspect
Change: single allowed variable / code scope
Gates: correctness + performance/memory criteria
Evidence: output directory/files
Return: requested key metrics only
STOP
```

Everything not changed by the work package inherits this file.

## Default evidence rules

- Original model files are immutable.
- Experimental scripts may be local under `scripts/`.
- Raw benchmark evidence stays local under `results-local/<area>/<checkpoint>/<UTC-RUN-ID>/`.
- Record real UTC run ID and enough provenance to reproduce the test.
- Do not manufacture measurements or infer unmeasured physical I/O.

## Default concise return

Unless the work package requests different fields, return only:

```text
Checkpoint: <id>
Classification: <PASS/CONDITIONAL/FAIL-specific>
Key metrics: <only decisive values>
Parity/tests: <PASS/FAIL>
Memory/safety: <decisive values>
Evidence: <directory>
Files: <created/modified>
Blocker: <only if present>
STOP
```

This protocol implements the project-local form of the Ophelia Vault token-efficient / bounded-agent workflow. Local LOOM restrictions above prevail where they are stricter.