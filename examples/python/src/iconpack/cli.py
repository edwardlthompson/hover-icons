"""CLI: validate catalog or render jobs. Never free-form prompts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from iconpack.backend_blender import blender_bin, run_blender
from iconpack.backend_dryrun import run_dry_run
from iconpack.catalog import Catalog, CatalogError, load_catalog
from iconpack.jobs import build_jobs
from iconpack.paths import repo_root


def _load(root: Path) -> tuple[Catalog, str, str]:
    catalog = load_catalog(root / "catalog" / "icons.yaml", root=root)
    template = (root / "prompts" / "template.txt").read_text(encoding="utf-8")
    negative = (root / "prompts" / "negative.txt").read_text(encoding="utf-8")
    return catalog, template, negative


def validate_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate icon catalog YAML and sources")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve() if args.root else repo_root()
        catalog = load_catalog(root / "catalog" / "icons.yaml", root=root)
    except (OSError, CatalogError, FileNotFoundError) as exc:
        print(f"What failed: catalog validation ({exc})", file=sys.stderr)
        print("What to run: python3 scripts/validate_catalog.py", file=sys.stderr)
        print("Why: every icon needs YAML + an existing source file.", file=sys.stderr)
        return 1
    print(f"OK   {len(catalog.icons)} icons in {catalog.pack.name}")
    return 0


def render_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fill locked prompts and render icon jobs")
    parser.add_argument("--backend", choices=("dry-run", "blender"), default="dry-run")
    parser.add_argument("--quality", choices=("draft", "release"), default="release")
    parser.add_argument("--only", default="", help="Comma-separated icon ids")
    parser.add_argument("--effects", default="", help="Comma-separated effect names")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve() if args.root else repo_root()
        catalog, template, negative = _load(root)
        only = {part.strip() for part in args.only.split(",") if part.strip()} or None
        effects = {part.strip() for part in args.effects.split(",") if part.strip()} or None
        jobs = build_jobs(
            root, catalog, template, negative, only=only, effects=effects, limit=args.limit
        )
        if args.backend == "dry-run":
            written = run_dry_run(root, jobs, resume=args.resume)
            print(f"OK   dry-run {len(written)} job files")
            return 0
        if not blender_bin():
            print("What failed: Blender binary not found", file=sys.stderr)
            print("What to run: install official Blender 4.2+; set BLENDER_BIN", file=sys.stderr)
            print("Why: --backend blender needs Cycles OptiX on a local GPU.", file=sys.stderr)
            return 2
        written = run_blender(root, jobs, resume=args.resume, quality=args.quality)
        print(f"OK   blender {len(written)} outputs")
        return 0
    except CatalogError as exc:
        print(f"What failed: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"What failed: {exc}", file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(f"What failed: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    return render_main()


if __name__ == "__main__":
    raise SystemExit(render_main())
