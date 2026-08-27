# LOOM 30B Lower-Bit Expert Speed/Quality Frontier 001 — Result

Date: 2026-08-27
Branch: `research/stretch-015-divergence-attribution`
Final classification: `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`

## Frozen reference

- canonical exact-Q4 backend commit: `96958de`;
- full top-8 routing;
- exact-Q4 sustained median: `1.229233 tok/s`;
- reused 128-position Q4 teacher oracle from Routing Sparsity Frontier 001.

## Local capability

Installed runtime:
- MLX `0.32.0`;
- mlx-lm `0.31.3`.

Native local quantization APIs support both `bits=2` and `bits=3` at the frozen group size `128` for the current expert matrix shapes.

Representative round-trip pilots PASS for both Q2 and Q3 at:
- layer 0 / expert 0;
- layer 15 / expert 0;
- layer 31 / expert 0;
- layer 47 / expert 0.

Each pilot verified Q4 decode -> requantize -> serialize/reload -> full expert compute with finite output shape `[1,1,2048]`, zero SOURCE fallback and zero persistent expert cache.

## Disk gates

PASS for both candidates.

- Q2: free `1,228,682,448,896 B`; required `12,339,642,368 B`.
- Q3: free `1,220,500,398,080 B`; required `16,869,490,688 B`.

Accepted Q4 artifacts were not modified or deleted.

## Q2 candidate

Artifact:
`<external-archive>/artifacts/30b-lower-bit-expert-speed-quality-frontier-001/20260827T144620Z/Q2/experts.bin`

SHA-256:
`945fb36ce6912e2be3caaa69264e44a8aa71907c189dd753b539106252bf468a`

Geometry:
- expert bytes: `1,327,104 B` projected / actual;
- full bank: `8,153,726,976 B` projected / actual;
- full top-8 expert traffic: `509,607,936 B/token`.

Static gate:
- `6144/6144` PASS;
- retained replay `18,048/18,048` PASS;
- zero unresolved/fallback/cache.

Fidelity against frozen Q4 teacher:
- top-1 agreement: `84.375%`;
- teacher top-1 in candidate top-3: `96.094%`;
- mean KL: `0.426378` nats;
- tier: FAIL.

Because USABLE fidelity failed, sustained speed testing was prohibited by preregistration.

## Q3 candidate

Artifact:
`<external-archive>/artifacts/30b-lower-bit-expert-speed-quality-frontier-001/20260827T144620Z/Q3/experts.bin`

SHA-256:
`bd321bb35cde48d85033c859a22a277091e8b5ad236e05f6fade2da1fcf11c87`

Geometry:
- expert bytes: `1,916,928 B` projected / actual;
- full bank: `11,777,605,632 B` projected / actual;
- full top-8 expert traffic: `736,100,352 B/token`.

Static gate:
- `6144/6144` PASS;
- retained replay `18,048/18,048` PASS;
- zero unresolved/fallback/cache.

Fidelity against frozen Q4 teacher:
- top-1 agreement: `87.500%`;
- teacher top-1 in candidate top-3: `100.000%`;
- mean KL: `0.150060` nats;
- tier: FAIL.

Q3 was closer to the USABLE boundary but still failed both the frozen top-1 threshold (`>=90%`) and KL threshold (`<=0.10`). Sustained speed testing was therefore prohibited.

## Decision

No candidate was selected. No final `3×32` campaign was run and no tracked canonical runtime code changed.

Interpretation:
- lower-bit expert-major storage is technically viable on the installed MLX stack;
- Q2 cuts expert traffic from Q4 `962,592,768 B/token` to `509,607,936 B/token`, but fidelity loss is too large;
- Q3 cuts traffic to `736,100,352 B/token`, but fidelity still misses the preregistered USABLE gate;
- do not adopt Q2/Q3 or relax the frozen quality gate post hoc.

The accepted production baseline remains full-top-8 Q4 at median `1.229233 tok/s`.

## Evidence

`results-local/research/30b-lower-bit-expert-speed-quality-frontier-001/20260827T144620Z/`

## Next scientific question

Since exact-Q4 micro-optimization, routing sparsity, Q3 and Q2 have all failed to provide the required quality-valid step toward `5 tok/s`, the next high-leverage question is verifier-side multi-token speculative verification.

Before selecting or downloading a real drafter, measure the lossless verifier throughput ceiling using oracle-correct speculative chunks. If even perfect proposals cannot materially accelerate the canonical verifier, a real drafter cannot solve the speed target.
