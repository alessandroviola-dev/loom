#!/usr/bin/env python3
"""LOOM Stretch 031 M2 ten-token treatment, harness Fix1.

Fixes only the original helper's nonexistent final-source summary-title anchor.
The frozen scientific workload remains M2, five blocks, and the common ten-token
oracle prefix.  Use --preflight to render and inspect source without MLX work.
"""
from __future__ import annotations

from stretch_single_pass_geometry_harness_031_fix1 import run_variant


if __name__ == "__main__":
    raise SystemExit(run_variant("M2"))
