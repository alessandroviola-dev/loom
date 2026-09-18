# LOOM

**Archived research project · 2026**

LOOM explored how far a capable local AI model could be pushed on severely constrained consumer hardware, using an Apple Silicon M1 Mac with 8 GB unified memory as the reference platform.

The project focused on practical runtime engineering: model serving, expert residency, storage layout, sidecar design, quantization trade-offs, context handling and speculative-decoding experiments.

LOOM is concluded. The final stop decision was a product decision, not an unresolved runtime failure: the retained 30B model became materially faster and more usable, but its practical capability still remained below the level required for the intended real workloads. Further speed work would not have solved that limitation.

## Final retained profile

The final stable local profile is:

**UNLOCKED UOPT-003 S40**

Reference results:

| Metric | Final retained result |
| --- | ---: |
| Decode | **7.557 tok/s** |
| 1,155-token cold prefill | **11.306 tok/s** |
| 1,155-token cold TTFT | **102.242 s** |
| Expert hit rate | **89.831%** |
| Frozen refusal gate | **0/6** |
| Held-out degeneration gate | **0/6** |
| Benign capability gate | **8/8** |

Matched UOPT-003 improvement versus the S32 baseline:

- decode: **6.660 → 7.557 tok/s** (**+13.46%**)
- cold TTFT: **161.676 → 102.242 s** (**−36.76%**)
- expert hit rate: **81.745% → 89.831%**
- expert misses: **90,229 → 50,260**

## Research question

LOOM asked a practical question:

> How usable can a 30B-class local model become on an 8 GB M1 Mac if the surrounding runtime, storage and expert-access path are engineered aggressively?

The work deliberately treated runtime performance and model capability as separate problems.

The runtime side improved substantially.

The capability ceiling did not move enough.

That distinction is the main conclusion of the project.

## What was tested

The completed research lineage includes:

| Work package | Result |
| --- | --- |
| WP1 Runtime / Product Serving | GO |
| WP2 Context Intelligence | GO |
| WP3 low-rank behavioral transform | NO_GO |
| WP3-R2 Behavioral Unlock | GO |
| WP4 Final Integration / Acceptance | GO |
| UOPT-001 | PARTIAL_GO |
| UOPT-002 | GO |
| UOPT-003 | **GO — final retained S40** |
| UOPT-004 | NO_GO |
| UOPT-005 | NO_GO |
| UOPT-006 | NO_GO |

### Key findings

1. **Lossless expert-major layout was high leverage.**  
   UOPT-002 reduced routed-expert miss I/O while preserving model math.

2. **Residency tuning mattered.**  
   UOPT-003 S40 improved decode and cold TTFT without changing model weights.

3. **More aggressive routed-expert quantization crossed the quality boundary.**  
   UOPT-004 and UOPT-005 reduced footprint but failed the frozen arithmetic reference.

4. **Storage placement materially affected performance.**  
   One experiment isolated an external-storage bottleneck: moving only the sidecar internal changed decode from **0.69 to 9.63 tok/s** and TTFT from **148.277 to 5.605 s** in that diagnostic comparison.

5. **Draftless speculative decoding did not engage usefully.**  
   UOPT-006 produced **0 drafted / 0 accepted tokens** and no meaningful decode speedup.

6. **The final bottleneck was model capability, not runtime throughput.**  
   Additional optimization ideas remained possible, but were intentionally not pursued because they would not address the practical intelligence ceiling.

## Project status

LOOM is:

- **closed**
- **archived**
- **read-only by default**
- retained as a research record and reproducible local setup

There is no active roadmap.

A future restart should begin by reassessing the model and hardware premise rather than automatically continuing optimization of the same 30B profile.

## Research archive

Start here:

- [Research overview](docs/RESEARCH_OVERVIEW.md)
- [Final handoff](HANDOFF.md)
- [Closed roadmap](ROADMAP.md)
- [Project closure record](research/integration/loom-project-closure-20260906.md)
- [UOPT-006 final experiment](research/integration/loom-unlocked-speed-optimization-006-result.md)
- [Local operator documentation](docs/LOOM_OPERATIONS.md)

The repository intentionally preserves detailed experiment records, including historical implementation notes and local-runtime provenance.

## Historical operator interface

The retained profile was operated with:

```bash
scripts/loom-deep use unlocked
scripts/loom-deep start
scripts/loom-deep stop
scripts/loom-deep status
scripts/loom-deep health
scripts/loom-deep current
```

Serving remained loopback-only:

```text
http://127.0.0.1:18080/
```

See [docs/LOOM_OPERATIONS.md](docs/LOOM_OPERATIONS.md) for the historical/recovery workflow.

## Repository policy

Git contains durable source, configuration, patches and research documentation.

Large or machine-local artifacts remain intentionally outside Git, including:

- model GGUF files
- expert sidecars
- local runtime builds
- caches
- temporary candidates
- local benchmark evidence
- external archive/staging data

This keeps the repository focused on reproducible engineering and research records rather than model distribution.

## License

LOOM is released under the **MIT License** for the original work in this repository.

See [LICENSE](LICENSE).

Third-party projects, dependencies, models, patches or incorporated components remain subject to their own respective licenses. The MIT license for LOOM does not replace or override upstream licensing terms.

## A note on the archive

Some documents are intentionally preserved as historical technical records rather than rewritten as polished documentation. That includes experiment naming, local paths, measurements, rollback notes and implementation-specific provenance.

For a concise reading path, start with this README and [docs/RESEARCH_OVERVIEW.md](docs/RESEARCH_OVERVIEW.md).
