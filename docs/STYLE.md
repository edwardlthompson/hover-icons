# Style (Hover Icons)

Simple 2D icon → same outline in 3D → glossy floating object → tame or neon (and later materials) from one catalog.

Read [`AGENT.md`](../AGENT.md) for the full brief.

## Silhouette

The render is a **3D version of the icon**, not a photograph of a real object. Keep proportions and outline of the source SVG. No extra objects, text, logos, or clutter.

## Locked studio

Use the same camera, lights, backdrop, scale, and padding for every icon:

- Three-quarter view, about **15°** tilt, floating
- Infinite **light-gray** seamless backdrop
- Key light **upper-left ~45°**, soft fill from the right, subtle rim, faint contact shadow
- Square **1024×1024** (optional 2048 later)
- Android-safe padding (about 18–25% inset) for adaptive-icon masks later

## Effects

- **tame** — satin/gloss plastic, no glow
- **neon** — thin inner emissive glow / faint bloom, still readable
- Later: glass, metal, ceramic as extra material presets on the **same** mesh

Add icons only with a new YAML block plus source SVG. Add effects only with a new material string and output folder.
