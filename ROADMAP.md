# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001_CONVERSION_OR_DECODE_SEMANTICS_BUG`
Strategic next: `LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.2.

## DFlash status

Still-valid chain:
- target tap interface `[1,12,23,34,45]`;
- exact B7 wavefront verifier;
- complete 680,813,824-param BF16 drafter port;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward path;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

BF16 branch:
- Q4->BF16 target states drift materially;
- Q4/BF16 target top1 on P1_t01 both `12050`;
- Q4->BF16 taps materially move drafter 32k logits;
- ~33 GiB BF16 cache and exact P1_t01 taps/logits retained externally.

## Critical correction — d2t is an offset

The previous output-support audit interpreted publisher `d2t` values as absolute target-token IDs. That interpretation is wrong.

Authoritative upstream semantics:
- exact RedHatAI model card uses `--draft-vocab-size 32000`;
- `speculators` builds `d2t = selected_target_ids - arange(32000)`;
- correct decode is `target_id = draft_row + d2t[draft_row]`;
- `t2d` is a BOOL mask over the verifier vocab with the 32,000 selected target IDs set true;
- current vLLM Qwen3 DFlash reconstructs `targets = arange(32000) + draft_id_to_target_id` before expanding draft logits into verifier-vocab space.

Local MLX instead used `d2t[argmax]` directly. This is classified:
`CONVERSION_OR_DECODE_SEMANTICS_BUG`.

Report:
`research/architecture/loom-dflash-output-mapping-semantics-audit-001-result.md`

Local evidence:
`results-local/research/dflash-output-mapping-semantics-audit-001/20260825T091537Z/`

## Results requiring recomputation

Pending corrected decode, do NOT treat these as valid scientific conclusions:
- effective support `17,018`;
- `33/63` structurally unsupported / `30/63` representable;
- P1_t01 `12050` unsupported;
- proposal target IDs/ranks derived by direct `d2t` lookup;
- `0/63` compatibility insofar as based on wrong target IDs;
- first E2E `0/96` acceptance if it used the same decode.

Underlying drafter weights/logits/taps/mask math remain usable unless the repair finds another defect.

## Next — mechanical offset-decode repair

Checkpoint:
`LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`

Purpose:
repair only the mapping semantics and cheaply determine what DFlash actually predicts on the frozen corpus.

Required order:
1. locate every local direct-`d2t` absolute-ID interpretation;
2. replace with authoritative `row + d2t[row]` semantics only;
3. prove reconstructed 32,000 target IDs are unique, in-vocab and exactly equal `nonzero(t2d)`;
4. recompute true support over the frozen 63 target tokens;
5. recompute corrected proposal IDs and target ranks/top-k from retained draft logits where available;
6. if retained evidence is insufficient, allow only the minimum drafter-only replay; no target/BF16 rerun;
7. scientifically review corrected 63-state compatibility before any E2E.

Decision after repair:
- useful corrected compatibility/acceptance signal -> continue DFlash salvage and then authorize a bounded corrected E2E;
- still catastrophic compatibility -> investigate remaining drafter training/interface mismatch or abandon DFlash in favor of the next high-leverage LOOM serving architecture/I/O path.

Restrictions:
- no retraining;
- no BF16 forward;
- no target regeneration unless separately justified;
- no E2E yet;
- no performance/memory optimization until corrected compatibility is known.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only the active delta. Pi executes local work; ChatGPT owns scientific/Git state.
