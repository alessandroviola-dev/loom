# LOOM — Agent Protocol (Archived)

Version: 4.00
Status: **PROJECT CLOSED / READ-ONLY BY DEFAULT**

LOOM is no longer an active research project.

## Archive rule

No agent, automation, or coding assistant should:

- start a new LOOM work package;
- continue UOPT research;
- mutate the retained production profile;
- download/build replacement models;
- change runtime patches;
- commit or push new LOOM work;

unless the owner explicitly reopens the project.

## Canonical final state

Repository: `Ilcoach/loom`

Final retained local product: **UNLOCKED UOPT-003 S40**.

Operator commands:

```text
scripts/loom-deep use unlocked
scripts/loom-deep start|stop|status|health|current
```

Retained artifacts:

- `models/loom-deep-30b-unlocked.gguf`
  - SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- `models/unlocked-expert-major-v1.bin`
  - SHA256 `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- `.loom/runtime/loom-uopt002/llama-server`
  - SHA256 `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`

Default profile remains S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`.

## Final research verdicts

- UOPT-001 — PARTIAL_GO
- UOPT-002 — GO
- UOPT-003 — GO / final retained production profile
- UOPT-004 — NO_GO
- UOPT-005 — NO_GO
- UOPT-006 — NO_GO

UOPT-006 draftless speculative decoding produced no useful speculation:

- `ngram-simple`: drafted `0`, accepted `0`, decode `+0.52%`
- `ngram-mod`: drafted `0`, accepted `0`, decode `-0.45%`

No phase 2 and no UOPT-007 are authorized.

## Final decision rationale

The project is closed because the 30B model's practical capability does not meet the intended workload requirements. Additional speed optimization would not address that limitation.

## Git hygiene retained for any future reopen

Never commit:

- `.loom/`
- `results-local/`
- model GGUFs or sidecars
- caches/temp files
- external-drive artifacts
- home-directory configuration
- secrets
- unrelated untracked scripts

If the project is ever explicitly reopened, read `HANDOFF.md`, `ROADMAP.md`, and `research/integration/loom-project-closure-20260906.md` first.
