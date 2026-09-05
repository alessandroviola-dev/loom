# LOOM_UNLOCKED_SPEED_UOPT_005_NO_GO

Date: 2026-09-04

Branch: `research/unlocked-speed-001`

Classification: **COMPLETE / NO_GO**

## Final decision

UOPT-005 is formally closed **NO_GO**. Candidate A failed functional quality
(`3/4`) and arithmetic (`400` vs required `410`) despite passing refusal
`0/6`, degeneration `0/6`, and benign capability `8/8`. Candidate B.1
(Q3 layers `40–47`) returned `400`; B.2 (`36–47`) and B.3 (`32–47`) returned
`414`. The losslessly validated layer and tensor frontiers did not produce
`410`; production UOPT-003 S40 remains the stable, unchanged baseline.

## Completed preparation

- BF16 source verification: **13/13** verified.
- HF→BF16 GGUF conversion: validated.
- Imatrix: completed.
- Candidate A: expert `IQ3_XXS` constructed.

## Storage isolation finding

Candidate A's initial performance pathology was caused by its sidecar being on
external archive. Storage isolation removed that bottleneck:

| Metric | external archive sidecar | Isolated storage |
| --- | ---: | ---: |
| Decode | 0.69 tok/s | **9.63 tok/s** |
| Prefill | 0.24 tok/s | **6.31 tok/s** |
| TTFT | 148.277 s | **5.605 s** |

external archive is therefore identified as the bottleneck, not a candidate-model
performance result.

## Candidate A quality and decision

| Gate | Result |
| --- | --- |
| Explicit refusal | **0/6 — PASS** |
| Held-out degeneration | **0/6 — PASS** |
| Benign capability | **8/8 — PASS** |
| Functional | **3/4 — FAIL** |
| Arithmetic | **400 vs expected 410 — FAIL** |
| Decision | **NO_GO** |

Candidate A is rejected for quality. The promoted UOPT-003 S40 production
profile remains unchanged.

## Candidate B session checkpoint — 2026-09-04

The existing validated quality-disjoint imatrix was used for a coarse-to-fine
layer ranking. B.1 restored only the highest-energy cohort (expert layers
`40–47`) from `IQ3_XXS` to `Q3_K`; layers `0–39` remained `IQ3_XXS`.

| Gate | B.1 result |
| --- | --- |
| Explicit refusal | **0/6 — PASS** |
| Held-out degeneration | **0/6 — PASS** |
| Benign capability | **8/8 — PASS** |
| Functional | **3/4 — FAIL** |
| Arithmetic | **400 vs expected 410 — FAIL** |

B.1 therefore remains a functional-quality failure. Its mixed sidecar required
a candidate-only isolated runtime extension for variable per-layer sidecar
strides; routing/top-k, LRU, resolver and production runtime were not changed.

The next minimal cohort, layers `36–39`, was added to construct B.2 (Q3 layers
`36–47`, IQ3 layers `0–35`). B.2 GGUF and its losslessly verified mixed sidecar
were completed before the cutoff; B.2 evaluation was resumed subsequently with
only that sidecar copied temporarily to internal SSD. The copy SHA-256 exactly
matched `0af9cb85323a43a8ac0261b1893e12093248b4fe019c8bb618eb1dcd4cd45d1e`.

## Candidate B.2 evaluation — NO_GO / STOP

B.2 ran on the isolated UOPT-002 mixed-sidecar extension required for its
validated variable layer strides, with the S40-equivalent configuration: 40
slots, 48 MoE layers, cache RAM 512 MiB, `--no-mmap`, CPU-MoE and `-ub 4`.
Routing/top-k were unchanged. The candidate server was loopback-only and the
production S40 profile was not running or mutated.

| Gate | B.2 result |
| --- | --- |
| Explicit refusal | **0/6 — PASS** |
| Held-out degeneration | **0/6 — PASS** |
| Benign capability | **8/8 — PASS** |
| Functional | **3/4 — FAIL** |
| Specific failure | Arithmetic returned `414`; expected exactly `410` |

B.2 is therefore **NO_GO** under the stop rule. At that decision no B.3
had been built and no canonical benchmark had run. The temporary internal B.2
sidecar was removed after its verified evaluation; production S40 model,
sidecar and UOPT-002 runtime hashes were re-verified unchanged. Detailed B.2
evidence is local at
`results-local/unlocked-speed-uopt-005/20260904T142234Z-candidate-b2-quality/`.

## Candidate B.3 arithmetic-first evaluation — NO_GO / STOP

B.3 added only the next coarse-to-fine cohort, layers `32–35`: Q3_K_S expert
layers `32–47`, IQ3_XXS expert layers `0–31`. Its GGUF and lossless mixed
sidecar verification passed (model SHA-256
`c98fb0af28f1a164ffab63fcae0565d30297a8ad569482cd3154cb4fcb13c25b`,
sidecar SHA-256
`2a150286feb2f8a8f5fae469f950707654b61e395ca9bc524857a74a3f5fe596`).
It ran with the same S40-equivalent isolated UOPT-002 mixed-sidecar runtime
configuration: 40 slots, 48 MoE layers, 512 MiB cache RAM, `--no-mmap`,
CPU-MoE and `-ub 4`; routing/top-k were unchanged.

The required arithmetic-only first gate returned **`414`**, not exact target
**`410`**. B.3 is therefore **NO_GO**: frozen refusal/degeneration, benign and
full-functional suites were not started, and no canonical benchmark ran. The
candidate server stopped cleanly and its SHA-verified temporary internal
sidecar was removed. Production S40 hashes were re-verified unchanged.

At this intermediate checkpoint, B.4 (adding layers `28–31` to the Q3
cohort) was only a proposal; it was not constructed.
Detailed B.3 evidence is local at
`results-local/unlocked-speed-uopt-005/20260904T145041Z-candidate-b3/` and
mirrored construction evidence is at
`<external-archive>/uopt-005/20260331T000000Z/evidence/candidate-b3-20260904T145041Z/`.

Exact B.1/B.2 construction policies, hashes, manifests and cutoff evidence
remain at
`<external-archive>/uopt-005/20260331T000000Z/evidence/`.

## B.3 follow-up — isolated 36–39 frontier / NO_GO

Per the post-B.3 instruction, **B.4 / layers 28–31 was not constructed** and
no new BF16→candidate quantization was performed. Instead, valid B.1/B.2 GGUFs
and sidecars were reused to losslessly splice the four-layer frontier. The
reassembler retained B.1 metadata/tensor order and rewrote GGUF tensor types
and offsets for only selected routed-expert tensors. Every assembled GGUF was
post-write SHA-256 verified tensor-by-tensor (all `579` physical tensor spans)
against its selected B.1/B.2 quantized source. Each temporary reassembled
sidecar then passed the canonical mixed-sidecar verifier (`18,432` routed
expert components) against its assembled GGUF.

All evaluations used the isolated mixed-sidecar runtime with the exact
S40-equivalent CPU-MoE/no-mmap configuration (40 slots, 48 layers, cache RAM
512 MiB, `-ub 4`), loopback only. Routing/top-k and speculative decoding were
unchanged/disabled. The sidecar was copied to internal storage only for the
individual evaluation and removed afterwards.

| Q3_K_S expert layers (with 40–47 retained Q3) | Arithmetic-only output |
| --- | ---: |
| 36–37 | `414` |
| 38–39 | `414` |
| 36 | `400` |
| 37 | `414` |
| 38 | `400` |
| 39 | `414` |

Thus the decisive singleton changes are layers **37** and **39**; layers 36
and 38 leave the B.1 result at 400. No coarse-half or singleton configuration
returned the required exact `410`. All candidates are **NO_GO** at the
arithmetic-first gate: no frozen/refusal/degeneration/benign/full-functional
suite and no benchmark ran. No quality verdict or promotion is claimed.

Production S40 remained untouched and re-verified after the evaluations:
GGUF SHA-256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
sidecar SHA-256 `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`.
Detailed durable local evidence is
`results-local/unlocked-speed-uopt-005/20260904T164011Z-splice-frontier/`.

## Tensor/projection frontier 37/39 — exhausted NO_GO

The layer frontier localized the arithmetic transition to expert layers 37 and
39. No new BF16 quantization was run. This follow-up reused B.1/B.2 Q3/IQ3
artifacts only: every candidate GGUF was losslessly reassembled with metadata,
tensor type and offset updates, then post-write verified against its selected
quantized source across all `579` physical tensor spans. Its mixed sidecar was
component-verified against the candidate GGUF across all `18,432`
`(layer, expert, projection)` components.

Projection-level splice has nonuniform up/gate/down pool strides inside a
layer. The isolated candidate runtime already sums the three pool strides per
expert and scatters its packed `preadv` correctly; no production or candidate
runtime change was made. The original layer-only verifier rejected this valid
layout, and its first sidecar assembly defect was detected before inference;
the corrected tensor-aware verifier passed every evaluated candidate.

All runs were arithmetic-only, loopback-only, isolated S40-equivalent CPU-MoE
(no-mmap, 40 slots, 48 layers, cache RAM 512 MiB, `-ub 4`), with routing/top-k
unchanged and speculative decoding disabled. Temporary internal sidecars were
removed after each evaluation.

| Q3 expert projection splice | Arithmetic output |
| --- | ---: |
| gate37 + gate39 | `400` |
| up37 + up39 | `414` |
| down37 + down39 | `414` |
| up37 | `414` |
| down37 | `414` |
| up39 | `400` |
| down39 | `414` |
| up37 + down37 | `414` |
| up37 + down39 | `414` |
| down37 + down39 | `414` |
| up37 + down37 + down39 | `414` |

Gate and up39 are noncausal for this arithmetic probe. All **11** losslessly validated candidate tensor splices were evaluated. The
complete nonempty subset frontier of the causal tensors `{up37, down37, down39}`
was exhausted: every subset returned `414`, while the empty causal set returns
B.1's `400`. No tensor/projection-level safe splice reached required exact
`410`.

This frontier is **NO_GO / exhausted**. Quality suites and benchmarks did not
run, and no quality verdict, promotion or performance claim is made. Do not
automatically descend to expert-by-expert: standard GGUF has one quantization
type/stride per projection tensor, so a Q3/IQ3 per-expert mix would require an
isolated runtime/sidecar-format change with per-expert type, allocation stride
and offset tables plus a new verifier. The raw blocks could be reused, but the
minimum engineering cost is estimated at 1–3 focused days plus a new bounded
expert search (up to 384 expert/projection binary switches before screening),
with benefit unproven after this all-414 causal tensor frontier.

Production S40 hashes again remained unchanged: model
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`; sidecar
`4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`.
Detailed durable local evidence is
`results-local/unlocked-speed-uopt-005/20260904T233313Z-tensor-frontier/`.
