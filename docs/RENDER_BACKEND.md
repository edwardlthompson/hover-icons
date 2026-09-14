# Render backends

CI never runs Blender, CUDA, or photoreal PNG generation. GitHub Actions uses **dry-run** only.

## dry-run (default)

```bash
python3 scripts/render_icons.py --backend dry-run

```

Fills the locked prompt template from `catalog/icons.yaml`, computes seeds, and writes JSON sidecars. It does **not** write fake goldens.

## blender (local RTX 4090)

Production path: SVG outline → round tube mesh (empty middle) → tame/neon material → Cycles OptiX (or CUDA fallback). One Blender process owns the GPU. Meshes are cached in `meshes/{id}.glb` so 4000+ icons can re-render new effects without remeshing.

**[HUMAN]** Install the official Linux tarball from blender.org (4.2 LTS or newer). Distro/Flatpak builds often cannot see OptiX. Set `BLENDER_BIN` in `.env`.

```bash
"$BLENDER_BIN" --background -E CYCLES --python-expr "import bpy; print('ok')"
python3 scripts/render_icons.py --backend blender --quality release --only camera --effects tame

```

If OptiX fails, set `CYCLES_DEVICE=CUDA`. Do not silently fall back to CPU Cycles.

`--resume` skips a PNG whose sidecar still matches catalog commit, scene hash, and effect. `--quality draft` uses EEVEE; goldens and published packs use `--quality release`.

Icons hover in a locked 1.55×1.55 box centered above a dark glossy studio. The camera uses the Apple product-icon lock: 15° look-down, 30° right three-quarter (front + right side; faces slightly left), aimed at the box center. Icons stand upright in the box. After posing, every icon is uniform-scaled to fit the box and centered on its middle so tall and wide silhouettes share the same camera and lights. **tame** is satin plastic with emission off. **neon** is a rich saturated catalog-colored glow in the outline tubes (never white; the middle stays empty — contrast is king). Edges are round tubes bent along the 2D silhouette, with an empty middle and no filled faces. Edge emission can bounce onto the dark floor. Extra catalog effects `glass`, `metal`, and `ceramic` reuse `meshes/{id}.glb`. They write `renders/effects/{effect}/{id}.png` (gitignored) plus JSON sidecars. CI still never runs Blender.

## What is not in git

Bulk `renders/base/*.png` and `renders/effects/**/*.png` are gitignored. Commit only `renders/golden/` (first four icons) plus JSON sidecars. Do not enable Git LFS without `[HUMAN]` approval.

## ControlNet fields

The catalog still stores Canny type and weight 0.75. Dry-run logs them. Production silhouette lock is the mesh, not Canny (see `docs/adr/0006-blender-production-renderer.md`).
