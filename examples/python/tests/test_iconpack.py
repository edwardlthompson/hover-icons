"""Tests for the locked icon-pack catalog and dry-run renderer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from iconpack.catalog import CatalogError, load_catalog
from iconpack.cli import render_main, validate_main
from iconpack.jobs import build_jobs, should_skip
from iconpack.mesh_normalize import normalize_scale, padded_camera_distance, viewbox_size
from iconpack.prompt import fill_template, negative_for_effect
from iconpack.seed import seed_for

REPO = Path(__file__).resolve().parents[3]


def test_slot_fill_only() -> None:
    template = "A [ICON_DESCRIPTION] in [COLOR] of [MATERIAL_AND_EFFECT].\n"
    filled = fill_template(template, "camera", "#424242", "satin plastic")
    assert "camera" in filled
    assert "#424242" in filled
    assert "satin plastic" in filled
    assert "[" not in filled


def test_neon_strips_glow_token() -> None:
    negative = "flat, 2D, neon glow, blurry"
    assert "neon glow" not in negative_for_effect(negative, "neon")
    assert "neon glow" in negative_for_effect(negative, "tame")


def test_seed_stable() -> None:
    assert seed_for("camera", "tame") == seed_for("camera", "tame")
    assert seed_for("camera", "tame") != seed_for("camera", "neon")
    assert 0 <= seed_for("camera", "tame") < 2**31


def test_load_real_catalog() -> None:
    catalog = load_catalog(REPO / "catalog" / "icons.yaml", root=REPO)
    assert catalog.pack.name == "photoreal-simple-icons"
    assert [icon.id for icon in catalog.icons] == ["camera", "messages"]


def test_missing_source(tmp_path: Path) -> None:
    yaml_text = (REPO / "catalog" / "icons.yaml").read_text(encoding="utf-8")
    yaml_text = yaml_text.replace("catalog/sources/camera.svg", "catalog/sources/missing.svg")
    path = tmp_path / "icons.yaml"
    path.write_text(yaml_text, encoding="utf-8")
    with pytest.raises(CatalogError, match="missing"):
        load_catalog(path, root=REPO)


def test_job_png_paths_and_order() -> None:
    catalog = load_catalog(REPO / "catalog" / "icons.yaml", root=REPO)
    template = (REPO / "prompts" / "template.txt").read_text(encoding="utf-8")
    negative = (REPO / "prompts" / "negative.txt").read_text(encoding="utf-8")
    jobs = build_jobs(REPO, catalog, template, negative)
    assert [(j.icon_id, j.effect) for j in jobs] == [
        ("camera", "tame"),
        ("camera", "neon"),
        ("messages", "tame"),
        ("messages", "neon"),
    ]
    assert jobs[0].png_path == "renders/base/camera.png"
    assert jobs[1].png_path == "renders/effects/neon/camera.png"


def test_unknown_effect_filter() -> None:
    catalog = load_catalog(REPO / "catalog" / "icons.yaml", root=REPO)
    template = (REPO / "prompts" / "template.txt").read_text(encoding="utf-8")
    negative = (REPO / "prompts" / "negative.txt").read_text(encoding="utf-8")
    jobs = build_jobs(REPO, catalog, template, negative, effects={"glass"})
    assert jobs == []


def test_resume_skip(tmp_path: Path) -> None:
    catalog = load_catalog(REPO / "catalog" / "icons.yaml", root=REPO)
    template = (REPO / "prompts" / "template.txt").read_text(encoding="utf-8")
    negative = (REPO / "prompts" / "negative.txt").read_text(encoding="utf-8")
    jobs = build_jobs(REPO, catalog, template, negative, only={"camera"}, effects={"tame"})
    job = jobs[0]
    png = tmp_path / job.png_path
    sidecar = tmp_path / job.json_path
    png.parent.mkdir(parents=True)
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    png.write_bytes(b"png")
    sidecar.write_text(
        json.dumps(
            {
                "catalog_commit": job.catalog_commit,
                "scene_hash": job.scene_hash,
                "effect": job.effect,
                "icon_id": job.icon_id,
            }
        ),
        encoding="utf-8",
    )
    assert should_skip(tmp_path, job, resume=True)
    assert not should_skip(tmp_path, job, resume=False)


def test_viewbox_normalize() -> None:
    svg = (REPO / "catalog" / "sources" / "camera.svg").read_text(encoding="utf-8")
    width, height = viewbox_size(svg)
    assert width == 256
    assert height == 256
    assert normalize_scale(width, height) == pytest.approx(2.0 / 256)
    assert padded_camera_distance() == pytest.approx(1.0 / 0.56)


def test_validate_and_dry_run() -> None:
    assert validate_main(["--root", str(REPO)]) == 0
    rc = render_main(
        ["--backend", "dry-run", "--root", str(REPO), "--only", "camera", "--effects", "tame"]
    )
    assert rc == 0
    sidecar = REPO / "renders" / "base" / "camera.json"
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert "Photorealistic 3D render" in data["prompt"]
    assert data["effect"] == "tame"
    assert "neon glow" in data["negative"]


def test_blender_missing_is_english_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BLENDER_BIN", raising=False)
    monkeypatch.setattr("iconpack.backend_blender.shutil.which", lambda _name: None)
    assert render_main(["--backend", "blender", "--root", str(REPO), "--only", "camera"]) == 2
