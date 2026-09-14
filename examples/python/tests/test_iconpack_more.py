"""Extra catalog/CLI branch tests to keep coverage with hello at 90%."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from iconpack.backend_dryrun import run_dry_run
from iconpack.catalog import CatalogError, load_catalog
from iconpack.cli import main, render_main, validate_main
from iconpack.gitinfo import catalog_commit
from iconpack.jobs import build_jobs, should_skip
from iconpack.mesh_normalize import normalize_scale, padded_camera_distance, viewbox_size
from iconpack.paths import repo_root

REPO = Path(__file__).resolve().parents[3]


def test_repo_root_and_missing() -> None:
    assert repo_root(REPO / "catalog") == REPO
    with pytest.raises(FileNotFoundError):
        repo_root(Path("/tmp"))


def test_catalog_error_branches(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="mapping"):
        (tmp_path / "x.yaml").write_text("- nope\n", encoding="utf-8")
        load_catalog(tmp_path / "x.yaml", root=tmp_path)
    (tmp_path / "empty.yaml").write_text("pack: {}\nicons: []\n", encoding="utf-8")
    with pytest.raises(CatalogError):
        load_catalog(tmp_path / "empty.yaml", root=tmp_path)
    bad_weight = (REPO / "catalog" / "icons.yaml").read_text(encoding="utf-8")
    bad_weight = bad_weight.replace("weight: 0.75", "weight: 0.1")
    path = tmp_path / "w.yaml"
    path.write_text(bad_weight, encoding="utf-8")
    with pytest.raises(CatalogError, match="weight"):
        load_catalog(path, root=REPO)
    bad_color = (REPO / "catalog" / "icons.yaml").read_text(encoding="utf-8")
    bad_color = bad_color.replace('"#424242"', '"blue"')
    path.write_text(bad_color, encoding="utf-8")
    with pytest.raises(CatalogError, match="color"):
        load_catalog(path, root=REPO)


def test_missing_effect_and_icon_shape(tmp_path: Path) -> None:
    text = (REPO / "catalog" / "icons.yaml").read_text(encoding="utf-8")
    text = text.replace("neon:", "glass:")
    path = tmp_path / "icons.yaml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(CatalogError, match="tame and neon"):
        load_catalog(path, root=REPO)
    (tmp_path / "list.yaml").write_text(
        "pack: {name: x, camera: a, backdrop: b, resolution: 1024, "
        "controlnet: {type: canny, weight: 0.75}, seed_strategy: hash}\n"
        "icons:\n  - just-a-string\n",
        encoding="utf-8",
    )
    with pytest.raises(CatalogError, match="mapping"):
        load_catalog(tmp_path / "list.yaml", root=tmp_path)


def test_svg_attrs_and_pad_errors() -> None:
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="64"></svg>'
    assert viewbox_size(svg) == (128.0, 64.0)
    with pytest.raises(ValueError):
        normalize_scale(0.0, 0.0)
    with pytest.raises(ValueError):
        padded_camera_distance(pad_fraction=0.5)


def test_gitinfo_unknown(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def boom(*_args: object, **_kwargs: object) -> str:
        raise OSError("no git")

    monkeypatch.setattr("iconpack.gitinfo.subprocess.check_output", boom)
    assert catalog_commit(tmp_path) == "unknown"


def test_limit_and_dry_run_skip(tmp_path: Path) -> None:
    catalog = load_catalog(REPO / "catalog" / "icons.yaml", root=REPO)
    template = (REPO / "prompts" / "template.txt").read_text(encoding="utf-8")
    negative = (REPO / "prompts" / "negative.txt").read_text(encoding="utf-8")
    jobs = build_jobs(REPO, catalog, template, negative, limit=1)
    assert len(jobs) == 1
    job = jobs[0]
    png = tmp_path / job.png_path
    sidecar = tmp_path / job.json_path
    png.parent.mkdir(parents=True)
    png.write_bytes(b"x")
    sidecar.write_text(json.dumps({**job.__dict__, "catalog_commit": "nope"}), encoding="utf-8")
    assert not should_skip(tmp_path, job, resume=True)
    sidecar.write_text(json.dumps(job.__dict__), encoding="utf-8")
    assert should_skip(tmp_path, job, resume=True)
    written = run_dry_run(tmp_path, jobs, resume=True)
    assert written[0].startswith("skip:")


def test_cli_error_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert validate_main(["--root", str(tmp_path)]) == 1
    assert render_main(["--backend", "dry-run", "--root", str(tmp_path)]) == 2
    cat = tmp_path / "catalog"
    cat.mkdir()
    (cat / "icons.yaml").write_text("pack: {}\nicons: []\n", encoding="utf-8")
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "template.txt").write_text("x\n", encoding="utf-8")
    (tmp_path / "prompts" / "negative.txt").write_text("y\n", encoding="utf-8")
    assert render_main(["--backend", "dry-run", "--root", str(tmp_path)]) == 1
    monkeypatch.setenv("BLENDER_BIN", "/bin/true")
    monkeypatch.setattr("iconpack.cli.run_blender", lambda *_a, **_k: [])
    assert render_main(["--backend", "blender", "--root", str(REPO), "--limit", "1"]) == 0

    def boom(*_a: object, **_k: object) -> list[str]:
        raise RuntimeError("boom")

    monkeypatch.setattr("iconpack.cli.run_blender", boom)
    assert render_main(["--backend", "blender", "--root", str(REPO), "--limit", "1"]) == 1
    monkeypatch.setattr(
        "sys.argv",
        ["iconpack", "--backend", "dry-run", "--root", str(REPO), "--limit", "1"],
    )
    assert main() == 0
