#!/usr/bin/env python3
"""Recover the latest CE-002 live coding retrieval run without new inference."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".loom" / "runtime" / "loom-deep"
RUN_ROOT = STATE / "ce002-live-coding-retrieval"
GATEWAY_ACCOUNTING = STATE / "context-webui-ci" / "accounting.jsonl"

ERROR = "ERROR_CE002_271828"
TARGET = "src/retry_policy.py"
EXPECTED = [5, 13, 29, 61]
TRANSIENT_PARTS = {"__pycache__", ".ruff_cache"}


def fail(message: str) -> None:
    raise SystemExit(f"CE-002 CODING RECOVERY FAIL: {message}")


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(errors="replace").splitlines():
        try:
            value = json.loads(line)
        except Exception:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def latest_run() -> Path:
    if not RUN_ROOT.exists():
        fail(f"run root not found: {RUN_ROOT}")
    candidates = [p for p in RUN_ROOT.iterdir() if p.is_dir() and (p / "workspace").is_dir()]
    if not candidates:
        fail("no recoverable coding-retrieval run found")
    return sorted(candidates, key=lambda p: p.name)[-1]


def workspace_files(workspace: Path) -> list[str]:
    result: list[str] = []
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(workspace)
        if any(part in TRANSIENT_PARTS for part in rel.parts):
            continue
        if rel.as_posix().endswith(".pyc") or rel.as_posix() == ".DS_Store":
            continue
        result.append(rel.as_posix())
    return sorted(result)


def verify_workspace(run: Path) -> list[int]:
    workspace = run / "workspace"
    files = workspace_files(workspace)
    allowed = {"README.md", TARGET}
    unexpected = sorted(set(files) - allowed)
    if unexpected:
        fail(f"unexpected persisted workspace files: {unexpected!r}")
    target = workspace / TARGET
    if not target.exists():
        fail(f"target file missing: {target}")

    spec = importlib.util.spec_from_file_location("ce002_recovered_retry_policy", target)
    if spec is None or spec.loader is None:
        fail("could not import recovered retry policy")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    retry_delay = getattr(module, "retry_delay", None)
    if not callable(retry_delay):
        fail("retry_delay is missing or not callable")

    actual = [retry_delay(i) for i in range(1, 5)]
    if actual != EXPECTED:
        fail(f"hidden contract mismatch: expected {EXPECTED!r}, got {actual!r}")
    for bad in (0, 5):
        try:
            retry_delay(bad)
        except ValueError:
            pass
        else:
            fail(f"retry_delay({bad}) did not raise ValueError")
    return actual


def engine_rows(run: Path) -> list[dict]:
    rows: list[dict] = []
    engine_root = run / "engine-runtime"
    for path in engine_root.glob("*/accounting.jsonl"):
        rows.extend(load_jsonl(path))
    return rows


def verify_retrieval(run: Path, rows: list[dict]) -> tuple[list[str], int]:
    retrievals = [row for row in rows if row.get("event") == "evidence_retrieval"]
    if not retrievals:
        fail("no evidence_retrieval accounting row found")
    final_retrieval = retrievals[-1]
    ids = [value for value in (final_retrieval.get("evidenceIds") or []) if isinstance(value, str)]
    if not ids:
        fail("retrieval row contains no evidence ids")
    visible = int(final_retrieval.get("finalVisibleTokens", 0) or 0)
    if visible <= 0 or visible > 1200:
        fail(f"retrieval visible estimate invalid: {visible}")

    blobs = run / "engine-runtime" / "evidence" / "blobs"
    matched = False
    for evidence_id in ids:
        if not evidence_id.startswith("ev1-"):
            continue
        path = blobs / f"{evidence_id[4:]}.json"
        if not path.exists():
            continue
        try:
            blob = json.loads(path.read_text())
        except Exception:
            continue
        text = json.dumps(blob.get("message"), sort_keys=True)
        if ERROR in text and "attempt 1 -> 5 seconds" in text and "attempt 4 -> 61 seconds" in text:
            matched = True
            break
    if not matched:
        fail(f"retrieved ids do not point to the archived diagnostic: {ids!r}")

    archive_errors = [row for row in rows if row.get("event") == "evidence_archive_error"]
    retrieval_errors = [row for row in rows if row.get("event") == "evidence_retrieval_error"]
    if archive_errors or retrieval_errors:
        fail(f"archive/retrieval errors recorded: archive={archive_errors!r} retrieval={retrieval_errors!r}")

    threshold = [row for row in rows if row.get("event") == "pi_compaction_after" and row.get("reason") == "threshold"]
    overflow = [
        row for row in rows
        if row.get("event") in {"pi_compaction_before", "pi_compaction_after"} and row.get("reason") == "overflow"
    ]
    if threshold or overflow:
        fail("Pi threshold compaction or overflow occurred")
    return ids, visible


def verify_gateway(rows: list[dict]) -> tuple[int, int, int, int]:
    governors = [row for row in rows if row.get("event") == "context_governor"]
    attempts = len(governors)
    if attempts < 4:
        fail(f"expected at least 4 provider attempts from governor accounting, found {attempts}")

    all_gateway = load_jsonl(GATEWAY_ACCOUNTING)
    chat_rows = [
        row for row in all_gateway
        if row.get("guardChecked") is True
        or row.get("guardBlocked") is True
        or row.get("event") in {"hard_guard_block", "hard_guard_unavailable"}
    ]
    if len(chat_rows) < attempts:
        fail(f"gateway accounting has only {len(chat_rows)} candidate rows for {attempts} provider attempts")
    run_gateway = chat_rows[-attempts:]
    if len(run_gateway) != attempts:
        fail("gateway reconstruction cardinality mismatch")

    blocked = [
        row for row in run_gateway
        if row.get("guardBlocked") is True or row.get("event") in {"hard_guard_block", "hard_guard_unavailable"}
    ]
    if blocked:
        fail(f"recovered run contains {len(blocked)} hard-guard block/unavailable attempt(s): {blocked!r}")

    checked = [row for row in run_gateway if row.get("guardChecked") is True]
    if len(checked) != attempts:
        fail(f"expected {attempts} checked gateway rows, found {len(checked)}")
    max_input = max(int(row.get("finalInputTokens", 0) or 0) for row in checked)
    max_total = max(int(row.get("projectedTotalTokens", 0) or 0) for row in checked)
    if max_input > 2800 or max_total > 3600:
        fail(f"CE-001 envelope exceeded: input={max_input} total={max_total}")
    return attempts, len(checked), max_input, max_total


def main() -> None:
    run = latest_run()
    actual = verify_workspace(run)
    rows = engine_rows(run)
    ids, visible = verify_retrieval(run, rows)
    attempts, guarded, max_input, max_total = verify_gateway(rows)

    rpc_rows = load_jsonl(run / "rpc.jsonl")
    agent_ends = sum(1 for row in rpc_rows if row.get("type") == "agent_end")

    summary = {
        "recovered": True,
        "run": str(run),
        "error": ERROR,
        "target": TARGET,
        "expected": EXPECTED,
        "actual": actual,
        "providerAttempts": attempts,
        "guardedProviderCalls": guarded,
        "retrievalEvidenceIds": ids,
        "retrievalVisibleTokens": visible,
        "maxExactFinalInput": max_input,
        "maxProjectedTotal": max_total,
        "hardGuardBlocks": 0,
        "piThresholdCompactions": 0,
        "piOverflowEvents": 0,
        "rpcLoggedAgentEnds": agent_ends,
    }
    output = run / "recovered-summary.json"
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print("CE-002 LIVE CODING RETRIEVAL RECOVERED: PASS")
    print(f"  run                      : {run}")
    print(f"  hidden expected delays   : {EXPECTED}")
    print(f"  actual delays            : {actual}")
    print(f"  provider attempts        : {attempts}")
    print(f"  RPC logged agent_end     : {agent_ends}")
    print(f"  final evidence ids       : {ids}")
    print(f"  retrieval visible tokens : {visible}")
    print(f"  max exact final input    : {max_input}")
    print(f"  max projected total      : {max_total}")
    print("  hard-guard blocks        : 0")
    print("  Pi threshold compactions : 0")
    print("  Pi overflow events       : 0")
    print(f"  recovered summary        : {output}")


if __name__ == "__main__":
    main()
