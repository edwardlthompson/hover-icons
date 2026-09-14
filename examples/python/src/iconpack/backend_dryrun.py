"""Dry-run backend: JSON sidecars and index only. Never write fake PNGs."""

from __future__ import annotations

import json
from pathlib import Path

from iconpack.jobs import RenderJob, job_to_dict, should_skip


def write_index(root: Path, jobs: list[RenderJob]) -> Path:
    path = root / "renders" / "index.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "backend": "dry-run",
        "jobs": [job_to_dict(job) for job in jobs],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def run_dry_run(root: Path, jobs: list[RenderJob], *, resume: bool) -> list[str]:
    """Write per-job JSON. Returns relative json paths written or skipped."""
    written: list[str] = []
    for job in jobs:
        sidecar = root / job.json_path
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        if should_skip(root, job, resume=resume):
            written.append(f"skip:{job.json_path}")
            continue
        sidecar.write_text(json.dumps(job_to_dict(job), indent=2) + "\n", encoding="utf-8")
        written.append(job.json_path)
    write_index(root, jobs)
    return written
