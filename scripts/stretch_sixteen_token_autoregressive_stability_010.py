#!/usr/bin/env python3
"""LOOM Stretch 010 — frozen transform of Stretch 009.

Scientific change: deterministic autoregressive continuation depth 4 -> 16.
Instrumentation-only addition: expose full streamed pass wall per token and
logical runtime tok/s. All model/cache/weight/safety policies remain inherited
from the exact frozen Stretch 009 source.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SOURCE_009_BLOB = "3e0780850bb65f9dccf07946f89597fa2e4d17e1"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def replace_exact(text: str, old: str, new: str, expected_count: int, label: str) -> str:
    observed = text.count(old)
    if observed != expected_count:
        raise RuntimeError(
            f"transform invariant failed for {label}: expected {expected_count} occurrence(s), found {observed}"
        )
    return text.replace(old, new)


def transformed_source(source: str) -> str:
    source = replace_exact(
        source,
        "GENERATED_TOKENS = 4\n",
        "GENERATED_TOKENS = 16\n",
        1,
        "continuation depth",
    )
    source = replace_exact(
        source,
        'print("LOOM Stretch 009 — Four-Token KV Autoregressive Parity")',
        'print("LOOM Stretch 010 — Sixteen-Token Autoregressive Stability")',
        1,
        "terminal experiment title",
    )
    source = replace_exact(
        source,
        '"four-token-kv-autoregressive-parity-009"',
        '"sixteen-token-autoregressive-stability-010"',
        1,
        "run directory",
    )
    source = replace_exact(
        source,
        '"experiment": "Stretch 009 — Four-Token KV Autoregressive Parity",',
        '"experiment": "Stretch 010 — Sixteen-Token Autoregressive Stability",',
        1,
        "summary experiment label",
    )
    source = replace_exact(
        source,
        'print(f"Expected cache offsets: 4 -> 5 -> 6 -> 7 -> {FINAL_OFFSET}")',
        'print(f"Expected cache offsets: prompt=4; token1=5; ...; token{GENERATED_TOKENS}={FINAL_OFFSET}")',
        1,
        "cache-offset display",
    )
    source = replace_exact(
        source,
        'summary["classification"] = "FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS"',
        'summary["classification"] = "SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS"',
        1,
        "PASS classification",
    )

    # Instrumentation only: the source already records total_pass_wall_seconds
    # in each streamed pass. Promote those values into the per-token summary.
    source = replace_exact(
        source,
        '''    forward_times = [\n        float(r["pass"]["total_layer_forward_wall_seconds"])\n        for r in child["stream"]["tokens"]\n    ]\n    summary["per_token_timing"] = {\n        "layer_materialize_seconds": materialize_times,\n        "layer_forward_seconds": forward_times,\n        "mean_layer_materialize_seconds": round(statistics.mean(materialize_times), 6),\n        "median_layer_materialize_seconds": round(statistics.median(materialize_times), 6),\n        "mean_layer_forward_seconds": round(statistics.mean(forward_times), 6),\n        "median_layer_forward_seconds": round(statistics.median(forward_times), 6),\n    }\n''',
        '''    forward_times = [\n        float(r["pass"]["total_layer_forward_wall_seconds"])\n        for r in child["stream"]["tokens"]\n    ]\n    full_pass_times = [\n        float(r["pass"]["total_pass_wall_seconds"])\n        for r in child["stream"]["tokens"]\n    ]\n    mean_full_pass = statistics.mean(full_pass_times)\n    summary["per_token_timing"] = {\n        "layer_materialize_seconds": materialize_times,\n        "layer_forward_seconds": forward_times,\n        "full_pass_seconds": full_pass_times,\n        "mean_layer_materialize_seconds": round(statistics.mean(materialize_times), 6),\n        "median_layer_materialize_seconds": round(statistics.median(materialize_times), 6),\n        "mean_layer_forward_seconds": round(statistics.mean(forward_times), 6),\n        "median_layer_forward_seconds": round(statistics.median(forward_times), 6),\n        "mean_full_pass_seconds": round(mean_full_pass, 6),\n        "median_full_pass_seconds": round(statistics.median(full_pass_times), 6),\n        "logical_streamed_tokens_per_second": round(1.0 / mean_full_pass, 6),\n    }\n''',
        1,
        "full-pass timing summary",
    )
    source = replace_exact(
        source,
        '''            print(f"Mean layer-materialize/token: {t.get('mean_layer_materialize_seconds')} s")\n            print(f"Mean layer-forward/token: {t.get('mean_layer_forward_seconds')} s")\n''',
        '''            print(f"Mean layer-materialize/token: {t.get('mean_layer_materialize_seconds')} s")\n            print(f"Mean layer-forward/token: {t.get('mean_layer_forward_seconds')} s")\n            print(f"Stream token full-pass walls: {t.get('full_pass_seconds')}")\n            print(f"Mean full streamed pass/token: {t.get('mean_full_pass_seconds')} s")\n            print(f"Median full streamed pass/token: {t.get('median_full_pass_seconds')} s")\n            print(f"Logical streamed tok/s: {t.get('logical_streamed_tokens_per_second')}")\n''',
        1,
        "full-pass timing display",
    )
    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source009 = repo / "scripts" / "stretch_four_token_kv_autoregressive_parity_009.py"
    observed = git_blob(source009, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 010 — Sixteen-Token Autoregressive Stability frozen transform")
        print(f"Stretch 009 source blob: {observed}")
    if observed != SOURCE_009_BLOB:
        print(f"Source provenance: FAIL expected {SOURCE_009_BLOB}, got {observed}", file=sys.stderr)
        return 2
    if not is_child:
        print("Source provenance: PASS")

    source = transformed_source(source009.read_text(encoding="utf-8"))

    # Critical inherited properties must remain visible after transformation.
    required_fragments = [
        'stdout=out_handle',
        'stderr=err_handle',
        '"KV_CACHE_GROWTH_UNEXPECTED"',
        '"MULTI_TOKEN_KV_NUMERICAL_PARITY_FAIL"',
        '"MULTI_TOKEN_TOP1_MISMATCH"',
        '"GENERATED_SEQUENCE_MISMATCH"',
        'MIN_FREE_PERCENT = 5',
        'MAX_SWAP_MB = 5600.0',
        'EXPECTED_KV_TOTAL_BYTES = 37_748_736',
        'GENERATED_TOKENS = 16',
    ]
    missing = [fragment for fragment in required_fragments if fragment not in source]
    if missing:
        raise RuntimeError(f"transformed-source invariant failed; missing {missing}")

    if not is_child:
        print("Frozen transform: PASS")
        print("Scientific change: generated tokens 4 -> 16 ONLY")
        print("Instrumentation: full-pass wall/tok-s summary added")
        print("Model/KV/weight/safety policy: UNCHANGED")

    transformed_globals = {
        "__name__": "__main__",
        # Parent must spawn this wrapper again for --child so the exact same
        # transformed source is used in both parent and child modes.
        "__file__": str(Path(__file__).resolve()),
    }
    exec(compile(source, str(source009), "exec"), transformed_globals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
