#!/usr/bin/env python3
"""Read-only prompt anatomy inspector for LOOM Capability Amplifier runs.

Reads already-saved prompt files from a results-local run directory.
Does not start Ollama, load a model, modify benchmark artifacts, or score quality.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def stats(text: str) -> dict:
    return {
        "bytes_utf8": len(text.encode("utf-8")),
        "chars": len(text),
        "lines": len(text.splitlines()),
        "whitespace_words": len(text.split()),
    }


def split_sections(text: str, markers: list[str]) -> list[tuple[str, str]]:
    positions: list[tuple[int, str]] = []
    for marker in markers:
        pos = text.find(marker)
        if pos >= 0:
            positions.append((pos, marker))
    positions.sort()

    sections: list[tuple[str, str]] = []
    if not positions:
        return [("FULL_TEXT", text)]

    if positions[0][0] > 0:
        sections.append(("PREAMBLE", text[: positions[0][0]]))

    for index, (pos, marker) in enumerate(positions):
        content_start = pos + len(marker)
        content_end = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        sections.append((marker.rstrip(":"), text[content_start:content_end]))
    return sections


def print_file(label: str, path: Path, markers: list[str]) -> dict | None:
    print("-" * 80)
    print(label)
    print("-" * 80)
    print(f"path: {path}")
    if not path.exists():
        print("status: MISSING")
        return None

    text = path.read_text(encoding="utf-8")
    overall = stats(text)
    print("overall:", json.dumps(overall, sort_keys=True))
    print("sections:")
    for name, body in split_sections(text, markers):
        print(f"  {name}: {json.dumps(stats(body), sort_keys=True)}")
    return overall


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--task", default="T02")
    args = parser.parse_args()

    run_dir = args.run_dir.expanduser().resolve()
    prompt_dir = run_dir / "prompts"
    initial = prompt_dir / f"{args.task}-initial.txt"
    repair = prompt_dir / f"{args.task}-repair.txt"

    print("=" * 80)
    print("LOOM AMPLIFIER — READ-ONLY PROMPT ANATOMY")
    print("=" * 80)
    print(f"run_dir: {run_dir}")
    print(f"task: {args.task}")
    print("model launch: NONE")

    initial_stats = print_file(
        "INITIAL PROMPT",
        initial,
        ["PERMITTED EDITABLE FILES:", "TASK PROMPT:", "SUPPLIED SOURCE FILES:"],
    )
    repair_stats = print_file(
        "REPAIR PROMPT",
        repair,
        [
            "PERMITTED EDITABLE FILES:",
            "ORIGINAL TASK PROMPT:",
            "VALIDATION FAILURE TYPE:",
            "VALIDATION FEEDBACK:",
            "CURRENT EDITABLE CANDIDATE:",
            "ORIGINAL NON-EDITABLE SOURCE CONTEXT:",
        ],
    )

    print("-" * 80)
    print("COMPARISON")
    print("-" * 80)
    if initial_stats and repair_stats:
        for key in ("bytes_utf8", "chars", "lines", "whitespace_words"):
            initial_value = initial_stats[key]
            repair_value = repair_stats[key]
            ratio = (repair_value / initial_value) if initial_value else None
            delta = repair_value - initial_value
            print(f"{key}: initial={initial_value} repair={repair_value} delta={delta} ratio={ratio:.3f}x")
    else:
        print("comparison unavailable because one or more prompt files are missing")

    print("-" * 80)
    print("RAW API FILE PRESENCE")
    print("-" * 80)
    raw_dir = run_dir / "raw"
    for phase in ("initial", "repair"):
        path = raw_dir / f"{args.task}-{phase}-api.json"
        print(f"{path.name}: {'PRESENT' if path.exists() else 'MISSING'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
