#!/usr/bin/env python3
"""Offline diagnosis for the latest CE-002 lightweight coding retrieval run.

No model or ForgeLoom process is started. The script separates:
- CE-002 retrieval/safety,
- retained-model coding result,
- workspace scope discipline.
"""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".loom" / "runtime" / "loom-deep"
RUNS = STATE / "ce002-live-coding-retrieval-lite"
GATEWAY_ACCOUNTING = STATE / "context-webui-ci" / "accounting.jsonl"
ERROR = "ERROR_CE002_271828"
TARGET = "src/retry_policy.py"
EXPECTED = [5, 13, 29, 61]


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
    if not RUNS.exists():
        raise SystemExit("CE-002 LITE DIAG FAIL: no lightweight run directory found")
    runs = sorted(path for path in RUNS.iterdir() if path.is_dir())
    if not runs:
        raise SystemExit("CE-002 LITE DIAG FAIL: no lightweight run directory found")
    return runs[-1]


def verify_policy(workspace: Path) -> tuple[bool, list[int] | None, str | None]:
    target = workspace / TARGET
    if not target.exists():
        return False, None, "target file missing"
    try:
        spec = importlib.util.spec_from_file_location("ce002_lite_diag_policy", target)
        if spec is None or spec.loader is None:
            return False, None, "could not import target"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        retry_delay = getattr(module, "retry_delay", None)
        if not callable(retry_delay):
            return False, None, "retry_delay missing"
        actual = [retry_delay(i) for i in range(1, 5)]
        if actual != EXPECTED:
            return False, actual, f"expected {EXPECTED!r}, got {actual!r}"
        for bad in (0, 5):
            try:
                retry_delay(bad)
            except ValueError:
                pass
            else:
                return False, actual, f"retry_delay({bad}) did not raise ValueError"
        return True, actual, None
    except Exception as exc:
        return False, None, f"import/verification error: {exc}"


def run_start_epoch(run: Path) -> float | None:
    try:
        return datetime.strptime(run.name, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).timestamp()
    except Exception:
        return None


def row_epoch(row: dict) -> float | None:
    value = row.get("timestamp")
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except Exception:
            pass
    return None


def main() -> None:
    run = latest_run()
    workspace = run / "workspace"
    engine_runtime = run / "engine-runtime"

    files = sorted(
        path.relative_to(workspace).as_posix()
        for path in workspace.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and not path.name.endswith(".pyc")
        and not path.relative_to(workspace).as_posix().startswith(".ruff_cache/")
        and path.name != ".DS_Store"
    )
    allowed = {"README.md", TARGET}
    unexpected = sorted(path for path in files if path not in allowed)
    scope_ok = not unexpected

    coding_ok, actual, coding_error = verify_policy(workspace)

    accounting: list[dict] = []
    for path in engine_runtime.glob("*/accounting.jsonl"):
        accounting.extend(load_jsonl(path))

    retrievals = [row for row in accounting if row.get("event") == "evidence_retrieval"]
    retrieval_ids = []
    max_visible = 0
    for row in retrievals:
        retrieval_ids.extend(str(value) for value in (row.get("evidenceIds") or []))
        max_visible = max(max_visible, int(row.get("finalVisibleTokens", 0) or 0))
    retrieval_ids = sorted(set(retrieval_ids))

    evidence_match = False
    blobs = engine_runtime / "evidence" / "blobs"
    for evidence_id in retrieval_ids:
        if not evidence_id.startswith("ev1-"):
            continue
        blob = blobs / f"{evidence_id[4:]}.json"
        if not blob.exists():
            continue
        try:
            value = json.loads(blob.read_text())
        except Exception:
            continue
        text = json.dumps(value.get("message"), sort_keys=True)
        if (
            ERROR in text
            and TARGET in text
            and "attempt 1 -> 5 seconds" in text
            and "attempt 4 -> 61 seconds" in text
            and "ValueError" in text
        ):
            evidence_match = True
            break

    threshold = [
        row for row in accounting
        if row.get("event") == "pi_compaction_after" and row.get("reason") == "threshold"
    ]
    overflow = [
        row for row in accounting
        if row.get("event") in {"pi_compaction_before", "pi_compaction_after"}
        and row.get("reason") == "overflow"
    ]
    ce_errors = [
        row for row in accounting
        if row.get("event") in {"evidence_archive_error", "evidence_retrieval_error"}
    ]

    gateway_rows = load_jsonl(GATEWAY_ACCOUNTING)
    start = run_start_epoch(run)
    if start is not None:
        filtered = []
        for row in gateway_rows:
            epoch = row_epoch(row)
            if epoch is not None and epoch >= start - 2:
                filtered.append(row)
        gateway_rows = filtered
    guarded = [row for row in gateway_rows if row.get("guardChecked") is True]
    max_input = max((int(row.get("finalInputTokens", 0) or 0) for row in guarded), default=0)
    max_total = max((int(row.get("projectedTotalTokens", 0) or 0) for row in guarded), default=0)
    hard_blocks = sum(1 for row in guarded if row.get("guardBlocked") is True)

    retrieval_safety_ok = (
        bool(retrievals)
        and evidence_match
        and max_visible <= 1200
        and hard_blocks == 0
        and max_input <= 2800
        and max_total <= 3600
        and not threshold
        and not overflow
        and not ce_errors
    )

    print("CE-002 lightweight coding retrieval diagnostic")
    print(f"  run                       : {run}")
    print(f"  workspace files           : {files}")
    print(f"  unexpected files          : {unexpected}")
    print(f"  scope discipline          : {'PASS' if scope_ok else 'FAIL'}")
    print(f"  hidden expected delays    : {EXPECTED}")
    print(f"  actual delays             : {actual}")
    print(f"  coding contract           : {'PASS' if coding_ok else 'FAIL'}")
    if coding_error:
        print(f"  coding detail             : {coding_error}")
    print(f"  retrieval applications    : {len(retrievals)}")
    print(f"  retrieval evidence ids    : {retrieval_ids}")
    print(f"  evidence matches fixture  : {evidence_match}")
    print(f"  max retrieval visible     : {max_visible}")
    print(f"  guarded provider calls    : {len(guarded)}")
    print(f"  max exact final input     : {max_input}")
    print(f"  max projected total       : {max_total}")
    print(f"  hard-guard blocks         : {hard_blocks}")
    print(f"  Pi threshold compactions  : {len(threshold)}")
    print(f"  Pi overflow events        : {len(overflow)}")
    print(f"  CE archive/retrieval errs : {len(ce_errors)}")
    print(f"  retrieval/safety          : {'PASS' if retrieval_safety_ok else 'FAIL'}")

    if unexpected:
        for rel in unexpected:
            path = workspace / rel
            try:
                excerpt = path.read_text(errors="replace")[:1200]
            except Exception:
                continue
            print(f"\nextra file excerpt: {rel}\n{excerpt}")

    print("\nCE-002 LITE diagnostic complete (offline; no inference performed)")


if __name__ == "__main__":
    main()
