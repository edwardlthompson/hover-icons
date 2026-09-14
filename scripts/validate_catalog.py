#!/usr/bin/env python3
"""Thin shim: schema-validate catalog/icons.yaml and source files."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    project = ROOT / "examples" / "python"
    cmd = [
        "uv",
        "run",
        "--project",
        str(project),
        "python",
        "-m",
        "iconpack.validate",
        *sys.argv[1:],
    ]
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
