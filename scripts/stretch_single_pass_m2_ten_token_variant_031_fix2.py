#!/usr/bin/env python3
"""LOOM Stretch 031 M2 ten-token treatment, harness Fix2.

The executable shim path is explicitly propagated to the generated parent and
its canonical child.  --dispatch-preflight-child is a no-model sentinel only.
"""
from __future__ import annotations

import sys
from pathlib import Path

from stretch_single_pass_geometry_harness_031_fix2 import dispatch_preflight_child, run_variant


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dispatch-preflight-child":
        raise SystemExit(dispatch_preflight_child("M2", sys.argv[2:]))
    raise SystemExit(run_variant("M2", launcher_path=Path(__file__).resolve()))
