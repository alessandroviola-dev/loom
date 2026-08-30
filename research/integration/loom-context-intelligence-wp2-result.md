# LOOM Context Intelligence — WP2 Result

Date: 2026-08-30  
Classification: **LOOM_CONTEXT_INTELLIGENCE_WP2_GO**

## Result

WP2 is complete. The default local Pi path now has a small, reversible host-side context layer, with no LLM, embedding model, background service, or new model-facing tool schema. WP1's canonical S32 server remains the rollback baseline.

Evidence root: `results-local/context-intelligence-wp2/20260830T133259Z/`.

## Architecture and integration

- **Caveman:** `scripts/loom-context` is a deterministic Python utility. It scores historical provider messages by lexical relevance, explicit/error priority, recency, and pin state; selects by value; emits selected items in original chronology; and records accounting. The active historical-evidence budget is **120 local estimated tokens**; current user input and system instructions are never rewritten. Small/in-budget contexts bypass unchanged.
- **Typed compressors retained:** log/shell (error/warning and head/tail preservation), repository search (leading/query-near paths), JSON (top-level shape and primitive values), code (declarations/returns plus query-near lines), and diff (headers/changed lines). No typed family was disabled. All are structural and deterministic.
- **Cavemem:** `.loom/memory.sqlite` (SQLite FTS5/BM25) with redacted artifacts in `.loom/artifacts/`. Records have stable IDs, project scope, timestamps, kind, summary, tags, priority, source, artifact reference, content hash, and privacy class. `record`, `search`, `get`, `timeline`, `observe`, and `recover` are available through `scripts/loom-context`.
- **Progressive retrieval:** memory is consulted only for explicit durable-project recall (decision/benchmark/constraint/rollback/runtime/WP1 style queries) and requires at least two lexical overlaps. Generic requests receive no injected memory. Exact source is only read with `scripts/loom-context recover loom://artifact/<sha256>[#Lx-Ly]`.
- **Pi integration point:** `.pi/extensions/loom-context.ts` uses Pi's `before_provider_request` hook for `loom-local` only, immediately before the HTTP request. It invokes the local utility, replaces only the outgoing payload, and fails open. Its `tool_execution_end` hook automatically considers only durable observations; ordinary turns are not persisted. No permanent Pi tool is registered.
- **Default/disable:** the trusted project extension is enabled by default for `loom-local`. Disable only this layer with `LOOM_CONTEXT_INTELLIGENCE=0`; use `--no-extensions` as a broader control. Both leave `scripts/loom-deep-server`/S32 untouched.

## Provider naming cleanup and retained runtime

Canonical Pi model is now `loom-local/loom-deep-30b-s32`; its model-server alias is `loom-deep-30b-s32`. A pre-mutation `models.json` backup is in the evidence root. Repository search found no live dependency on the S24 label. This is only a label correction; flags remain S32:

`--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`

Model SHA256: `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`  
`llama-server` SHA256: `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

## Frozen benchmark

Frozen specification: `benchmarks/context-intelligence-wp2/frozen-cases.json` (logs, search, JSON, code, diff, earlier decision, and small/no-op). Objective expected-string criteria were frozen before final-arm measurement. The final artifacts are `benchmark-promoted/summary.json` and per-arm request/response payloads.

| Arm | Task success | Median provider input | Heavy-case median input reduction | No-op input | Median host pack/retrieval wall |
|---|---:|---:|---:|---:|---:|
| A — WP1 baseline | 6/7 | 195 | — | 19 | 0 ms |
| B — Caveman | 6/7 | 168 | **23.24%** | 19 | 184.95 ms |
| C — combined | 6/7 | 177 | **23.24%** | 19 | 255.27 ms |

The one shared baseline/B/C miss was the deliberately long 40-hex-character JSON answer truncated by the frozen 16-token response cap; it is not an accepted wrong answer and does not alter relative task quality. All other six objective tasks succeeded in every final arm. No stale/incorrect memory caused an accepted wrong result.

Direct provider accounting is the promotion token metric: C achieves the required >=20% heavy-case median reduction and no-op overhead is exactly 0%. Local deterministic accounting is more conservative and retains all recovery handles. All six final benchmark recovery references were recovered and SHA-verified: **100% exact-source verification**.

Server timing was materially cache-order-sensitive because the preserved WP1 `--cache-ram 512` path was intentionally retained. Thus raw median prefill/E2E arm figures are evidence, not a causal speedup claim: A 278.05 ms/2088.15 ms, B 18,905.06 ms/21,581.55 ms, C 278.96 ms/2252.30 ms. In uncached packed requests, 0.185–0.255 s host work was small versus 12–72 s prompt prefill. Decode behavior remained within normal S32 variation (A 6.789, B 5.297, C 6.879 tok/s); no runtime semantic configuration changed.

## Safety, privacy, and resources

The redactor runs before every durable artifact/SQLite write. It replaces bearer/API/token/secret/password values and email addresses with deterministic redaction markers; original secret values are never written to `.loom`. Project scope is a path-derived hash. SQLite/artifact permissions are owner-only. There is no network access, embedding model, or daemon.

Final benchmark server RSS changed from 4075.9 MiB to 4099.7 MiB (+23.8 MiB sampled); sampled swap changed from 2007.4 MiB to 2074.2 MiB (+66.8 MiB) while 997.8 MiB remained free. The one-shot Python process exits after each request and the memory DB is disk-backed. No OOM/corruption occurred. The server remained healthy and localhost-only.

A real local Pi task completed through the default enabled combined path: `Reply only with 4.` produced `4` using `loom-local/loom-deep-30b-s32` (`pi-combined-default-enabled.jsonl`); its packing record confirms the small/no-op bypass. The disabled control and `LOOM_CONTEXT_INTELLIGENCE=0` mechanism were also exercised.

## Negative/reverted cases

1. Initial oversized corpus exceeded the inherited 4096-token server context (HTTP 400); corpus volume was bounded without changing task targets.
2. A 731-token log required 153.9 s prefill; the final frozen workload was bounded to avoid an unbounded 21-request run. Cancelled requests temporarily left the managed server non-responsive; it exited after TERM and was restarted with the unchanged WP1 command.
3. Broad automatic memory injection was net-negative on generic queries and was removed. Retrieval is now explicit-recall/lexical-gated.
4. Search compression initially had metadata overhead greater than its saving; prompt-visible redundant SHA/original-token annotations were removed while artifact hashes remain durable and recoverable.

Items 1–2 are the two bounded corpus/latency corrective iterations; items 3–4 are the two bounded quality/token net-negative subfeature reversals. No broader parameter search was performed.

## Provenance, changed files, and rollback

Hashes/config evidence: `final-hashes.txt`, `promoted-hashes.txt`, `pi-final-config-hashes.txt`, `s32-label-models.json`, `final-memory-timeline.json`, and `recovery-verification.json` under the evidence root.

Permanent changed/added files:

- `.pi/extensions/loom-context.ts`
- `.gitignore` (`.loom/` local-state exclusion)
- `config/loom-deep-server.env` (S32 alias label only)
- `scripts/loom-context`
- `scripts/test_loom_context.py`
- `scripts/benchmark_context_intelligence_wp2.py`
- `benchmarks/context-intelligence-wp2/frozen-cases.json`
- `research/integration/loom-context-intelligence-wp2-result.md`

Rollback:

```bash
LOOM_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-s32
# or broader Pi-extension control:
pi --no-extensions --model loom-local/loom-deep-30b-s32
# WP1 serving control remains unchanged:
scripts/loom-deep-server {start,status,health,stop}
```

To restore the old label only, use the preserved `pi-backup/models.json` and `source/loom-deep-server.env.before` evidence copies, then restart the managed server. This is not needed for runtime rollback: S24 remains documented WP1 rollback and no S32 runtime flag was changed.
