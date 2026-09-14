"""Blender subprocess backend. bpy is never imported here."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from iconpack.jobs import RenderJob, job_to_dict, should_skip


def blender_bin() -> str | None:
    env = os.environ.get("BLENDER_BIN", "").strip()
    if env:
        return env
    return shutil.which("blender")


def run_blender(
    root: Path,
    jobs: list[RenderJob],
    *,
    resume: bool,
    quality: str,
) -> list[str]:
    """Invoke scripts/blender_batch.py once per job. One process owns the GPU."""
    binary = blender_bin()
    if not binary:
        raise FileNotFoundError("BLENDER_BIN")
    script = root / "scripts" / "blender_batch.py"
    if not script.is_file():
        raise FileNotFoundError(script)
    device = os.environ.get("CYCLES_DEVICE", "OPTIX").strip() or "OPTIX"
    written: list[str] = []
    log_dir = root / "renders" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    for job in jobs:
        if should_skip(root, job, resume=resume):
            written.append(f"skip:{job.png_path}")
            continue
        payload = job_to_dict(job)
        payload["root"] = str(root)
        payload["quality"] = quality
        payload["cycles_device"] = device
        job_file = log_dir / f"{job.icon_id}_{job.effect}.job.json"
        job_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        cmd = [binary, "--background", "--python", str(script), "--", str(job_file)]
        png_out = root / job.png_path
        if png_out.is_file():
            png_out.unlink()
        proc = subprocess.run(cmd, cwd=root, check=False)
        if proc.returncode != 0 or not png_out.is_file():
            raise RuntimeError(
                f"Blender failed for {job.icon_id}/{job.effect} (exit {proc.returncode})"
            )
        written.append(job.png_path)
    return written
