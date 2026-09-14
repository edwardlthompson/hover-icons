"""Build render jobs from the catalog. Tame PNGs live under renders/base/."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from iconpack.catalog import Catalog, Icon
from iconpack.gitinfo import catalog_commit
from iconpack.prompt import fill_template, negative_for_effect
from iconpack.seed import seed_for

PREFERRED_EFFECTS = ("tame", "neon")
SCENE_HASH = "hover-icons-scene-v1-15deg-45key-1024-pad"


@dataclass(frozen=True)
class RenderJob:
    icon_id: str
    effect: str
    seed: int
    prompt: str
    negative: str
    source: str
    png_path: str
    json_path: str
    golden_path: str
    mesh_path: str
    color: str
    material: str
    controlnet_type: str
    controlnet_weight: float
    resolution: int
    catalog_commit: str
    scene_hash: str


def effect_order(effects: dict[str, str]) -> list[str]:
    """tame, neon, then any extra presets alphabetically."""
    head = [name for name in PREFERRED_EFFECTS if name in effects]
    extra = sorted(name for name in effects if name not in PREFERRED_EFFECTS)
    return head + extra


def png_path(root: Path, icon_id: str, effect: str) -> Path:
    if effect == "tame":
        return root / "renders" / "base" / f"{icon_id}.png"
    return root / "renders" / "effects" / effect / f"{icon_id}.png"


def sidecar_path(png: Path) -> Path:
    return png.with_suffix(".json")


def _job(
    root: Path, catalog: Catalog, icon: Icon, effect: str, template: str, negative: str
) -> RenderJob:
    png = png_path(root, icon.id, effect)
    golden = root / "renders" / "golden" / f"{icon.id}_{effect}.png"
    return RenderJob(
        icon_id=icon.id,
        effect=effect,
        seed=seed_for(icon.id, effect),
        prompt=fill_template(template, icon.description, icon.color, icon.effects[effect]),
        negative=negative_for_effect(negative, effect),
        source=icon.source,
        png_path=str(png.relative_to(root)),
        json_path=str(sidecar_path(png).relative_to(root)),
        golden_path=str(golden.relative_to(root)),
        mesh_path=str((root / "meshes" / f"{icon.id}.glb").relative_to(root)),
        color=icon.color,
        material=icon.effects[effect],
        controlnet_type=catalog.pack.controlnet.type,
        controlnet_weight=catalog.pack.controlnet.weight,
        resolution=catalog.pack.resolution,
        catalog_commit=catalog_commit(root),
        scene_hash=SCENE_HASH,
    )


def build_jobs(
    root: Path,
    catalog: Catalog,
    template: str,
    negative: str,
    *,
    only: set[str] | None = None,
    effects: set[str] | None = None,
    limit: int | None = None,
) -> list[RenderJob]:
    """Catalog order, tame then neon. Optional filters for golden-sample runs."""
    jobs: list[RenderJob] = []
    for icon in catalog.icons:
        if only is not None and icon.id not in only:
            continue
        for name in effect_order(icon.effects):
            if effects is not None and name not in effects:
                continue
            jobs.append(_job(root, catalog, icon, name, template, negative))
            if limit is not None and len(jobs) >= limit:
                return jobs
    return jobs


def job_to_dict(job: RenderJob) -> dict[str, Any]:
    return {
        "icon_id": job.icon_id,
        "effect": job.effect,
        "seed": job.seed,
        "prompt": job.prompt,
        "negative": job.negative,
        "source": job.source,
        "png_path": job.png_path,
        "json_path": job.json_path,
        "golden_path": job.golden_path,
        "mesh_path": job.mesh_path,
        "color": job.color,
        "material": job.material,
        "controlnet_type": job.controlnet_type,
        "controlnet_weight": job.controlnet_weight,
        "resolution": job.resolution,
        "catalog_commit": job.catalog_commit,
        "scene_hash": job.scene_hash,
    }


def should_skip(root: Path, job: RenderJob, *, resume: bool) -> bool:
    """Skip when resume is on and sidecar+PNG still match catalog/scene/effect."""
    if not resume:
        return False
    png = root / job.png_path
    sidecar = root / job.json_path
    if not png.is_file() or not sidecar.is_file():
        return False
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    expected = {
        "catalog_commit": job.catalog_commit,
        "scene_hash": job.scene_hash,
        "effect": job.effect,
        "icon_id": job.icon_id,
    }
    return all(str(data.get(key)) == value for key, value in expected.items())
