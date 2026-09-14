"""Discover the Hover Icons repository root."""

from __future__ import annotations

from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    """Return the directory that contains AGENT.md and catalog/icons.yaml."""
    cur = (start or Path.cwd()).resolve()
    for path in [cur, *cur.parents]:
        if (path / "AGENT.md").is_file() and (path / "catalog" / "icons.yaml").is_file():
            return path
    raise FileNotFoundError("Hover Icons repo root not found (AGENT.md + catalog/icons.yaml)")
