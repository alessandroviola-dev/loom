#!/usr/bin/env python3
"""Telemetry-only rerun wrapper for LOOM Direct MLX 8B 3-bit Smoke 001.

Imports the frozen Smoke 001 implementation and overrides only swap_used_mb()
so locale-formatted macOS decimal commas are parsed correctly.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path


def load_smoke_module():
    here = Path(__file__).resolve()
    target = here.with_name("direct_mlx_8b_3bit_smoke.py")
    spec = importlib.util.spec_from_file_location("loom_direct_mlx_8b_3bit_smoke_001", target)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load frozen Smoke 001 runner: {target}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def locale_safe_swap_used_mb(module) -> float | None:
    proc = subprocess.run(
        ["sysctl", "-n", "vm.swapusage"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if proc.returncode != 0:
        return None
    match = re.search(
        r"\bused\s*=\s*([0-9]+(?:[.,][0-9]+)?)\s*([KMGT])(?:B)?\b",
        proc.stdout,
        re.IGNORECASE,
    )
    if not match:
        return None
    value = match.group(1).replace(",", ".")
    return round(module.parse_scaled_mb(value, match.group(2)), 2)


def main() -> int:
    module = load_smoke_module()

    # Verify the parser against the current host format before launching MLX.
    probe = locale_safe_swap_used_mb(module)
    print("LOOM Direct MLX 8B 3-bit Smoke 001 — swap telemetry fix rerun")
    print(f"Locale-safe swap parser preflight: {probe!r} MB")
    if probe is None:
        print("Swap parser preflight: FAIL")
        return 2
    print("Swap parser preflight: PASS")

    # This is the only behavioral override. All frozen model/runtime/generation
    # settings remain defined by direct_mlx_8b_3bit_smoke.py.
    module.swap_used_mb = lambda: locale_safe_swap_used_mb(module)
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
