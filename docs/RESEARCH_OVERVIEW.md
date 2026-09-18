# LOOM — Research Overview

Status: **FINAL / CLOSED / ARCHIVED**

LOOM was a bounded engineering research project about running a 30B-class local AI model on an Apple Silicon M1 Mac with 8 GB unified memory.

This document is the concise public-facing overview. The detailed archive remains the source of record for individual experiments and measurements.

## 1. Objective

The project investigated whether runtime engineering could make a large local model practically useful on hardware far below the memory envelope normally associated with that class of model.

The work focused on:

- local serving;
- expert residency;
- routed-expert access;
- storage placement;
- lossless sidecar layout;
- quantization frontiers;
- context handling;
- speculative decoding;
- operational rollback and recovery.

The target was not simply to make the model run.

The target was to make it useful enough for real workloads.

## 2. Reference platform

The reference platform was:

```text
Apple Silicon M1
8 GB unified memory
local-only / loopback serving
```

The retained product used a 30B UNLOCKED model with a patched llama.cpp-based runtime and a lossless expert-major sidecar.

## 3. Final retained state

The final stable profile is:

```text
UNLOCKED UOPT-003 S40
```

Reference metrics:

```text
decode                         7.557 tok/s
1,155-token cold prefill      11.306 tok/s
1,155-token cold TTFT         102.242 s
expert hit rate               89.831%
refusal gate                  0/6
degeneration gate             0/6
benign capability             8/8
```

Matched UOPT-003 improvement against S32:

```text
decode          6.660 → 7.557 tok/s
cold TTFT       161.676 → 102.242 s
expert misses   90,229 → 50,260
```

## 4. Main findings

### 4.1 Lossless layout changes can outperform weight changes

UOPT-002 introduced a lossless expert-major sidecar and patched runtime.

This materially reduced routed-expert miss I/O without changing the mathematical content of the model.

### 4.2 Expert residency was one of the strongest runtime levers

UOPT-003 increased the retained residency target from S32 to S40.

The result improved both decode speed and cold-start behavior while preserving the frozen behavioral gates.

### 4.3 Lower-bit expert quantization reached a quality boundary

UOPT-004 and UOPT-005 explored lower-bit routed-expert strategies.

They reduced memory footprint, but the tested candidates failed the frozen functional arithmetic reference.

The project therefore retained the larger, lossless profile rather than promoting a smaller but behaviorally degraded one.

### 4.4 Storage location can dominate apparent model performance

A diagnostic experiment showed that placing a temporary sidecar on an external archive volume created an artificial bottleneck.

Moving only the sidecar to internal storage changed:

```text
decode   0.69 → 9.63 tok/s
TTFT     148.277 → 5.605 s
```

This isolated storage placement as the cause rather than model or runtime logic.

### 4.5 Draftless speculative decoding did not provide value

UOPT-006 tested runtime-supported n-gram speculative modes.

Both tested modes produced:

```text
drafted tokens   0
accepted tokens  0
```

Neither reached the immediate 5% decode-improvement gate.

No second experimental phase was justified.

## 5. Why the project stopped

LOOM did not stop because the runtime was broken.

The runtime work succeeded in making the 30B model materially more usable on the reference machine.

The project stopped because the model's practical capability still remained below the level needed for the intended workloads.

At that point, further speed work would have optimized the wrong constraint.

The final conclusion was therefore:

> Reassess the model target before investing in additional runtime optimization.

## 6. Research lineage

```text
WP1      Runtime / Product Serving       GO
WP2      Context Intelligence            GO
WP3      Low-rank behavioral transform   NO_GO
WP3-R2   Behavioral Unlock               GO
WP4      Final Integration / Acceptance  GO

UOPT-001                               PARTIAL_GO
UOPT-002                               GO
UOPT-003                               GO / retained
UOPT-004                               NO_GO
UOPT-005                               NO_GO
UOPT-006                               NO_GO
```

## 7. Where to read next

For the final engineering state:

- [HANDOFF.md](../HANDOFF.md)

For the formal closure decision:

- [loom-project-closure-20260906.md](../research/integration/loom-project-closure-20260906.md)

For the final speculative-decoding experiment:

- [loom-unlocked-speed-optimization-006-result.md](../research/integration/loom-unlocked-speed-optimization-006-result.md)

For historical operation/recovery:

- [LOOM_OPERATIONS.md](LOOM_OPERATIONS.md)

For the closed roadmap:

- [ROADMAP.md](../ROADMAP.md)

## 8. Archive policy

LOOM is intentionally archived.

No new optimization work should be started from the historical roadmap unless the project is explicitly reopened.

If it is reopened, the first question should be whether the current 30B model and hardware premise still make sense.

## 9. License

Original LOOM work in this repository is available under the MIT License.

Third-party code, dependencies, models and upstream components remain governed by their own licenses.
