# Render backends

CI never runs Blender, CUDA, or photoreal PNG generation. GitHub Actions uses **dry-run** only.

## dry-run (default)

```bash
python3 scripts/render_icons.py --backend dry-run
```

Fills the locked prompt template from `catalog/icons.yaml`, computes seeds, and writes JSON sidecars. It does **not** write fake goldens.

## blender (local RTX 4090)

Production path: SVG → extrude/bevel mesh → tame/neon material → Cycles OptiX (or CUDA fallback). One Blender process owns the GPU. Meshes are cached in `meshes/{id}.glb` so 4000+ icons can re-render new effects without remeshing.

**[HUMAN]** Install the official Linux tarball from blender.org (4.2 LTS or newer). Distro/Flatpak builds often cannot see OptiX. Set `BLENDER_BIN` in `.env`.

```bash
"$BLENDER_BIN" --background -E CYCLES --python-expr "import bpy; print('ok')"
python3 scripts/render_icons.py --backend blender --quality release --only camera --effects tame
```

If OptiX fails, set `CYCLES_DEVICE=CUDA`. Do not silently fall back to CPU Cycles.

`--resume` skips a PNG whose sidecar still matches catalog commit, scene hash, and effect. `--quality draft` uses EEVEE; goldens and published packs use `--quality release`.

## What is not in git

Bulk `renders/base/*.png` and `renders/effects/**/*.png` are gitignored. Commit only `renders/golden/` (first four icons) plus JSON sidecars. Do not enable Git LFS without `[HUMAN]` approval.

## ControlNet fields

The catalog still stores Canny type and weight 0.75. Dry-run logs them. Production silhouette lock is the mesh, not Canny (see `docs/adr/0006-blender-production-renderer.md`).
