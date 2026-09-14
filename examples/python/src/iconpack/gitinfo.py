"""Git commit of the catalog for sidecar logs."""

from __future__ import annotations

import subprocess
from pathlib import Path


def catalog_commit(root: Path) -> str:
    """Return HEAD sha, or unknown when git is unavailable."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return out.strip() or "unknown"
