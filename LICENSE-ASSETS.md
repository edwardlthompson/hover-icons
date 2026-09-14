# Asset licenses

This file is why generated icons and original 2D sources are not mixed under a single SPDX line.

| Layer | License | What it covers |
|-------|---------|----------------|
| Repository code, scripts, CI, docs | MIT (`LICENSE`) | Everything except the rows below |
| Authored 2D sources in `catalog/sources/` | CC0 1.0 | Geometric SVGs created for this pack |
| Generated PNGs (when a renderer produces them) | CC0 1.0 | `renders/golden/` and later pack zips |
| Third-party 2D sources | **Keep the upstream license** | Do not relicense someone else's SVG as CC0 |

Blender, NVIDIA drivers, and optional later Stable Diffusion weights are **local renderer tooling**, not shipped in the pack. Do not copy model weights into this repo.

If you add a source SVG you did not author, record its license and URL in a comment in `catalog/icons.yaml` and in this file.
