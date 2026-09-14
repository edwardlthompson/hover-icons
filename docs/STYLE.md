# Style (Hover Icons)

Simple 2D icon → same outline in 3D → glossy floating object → tame or neon (and later materials) from one catalog.

Read [`AGENT.md`](../AGENT.md) for the full brief.

**Contrast is king. Icons must be glanceable.** Never flood a face with emission or bloom.

## Silhouette

The render is a **3D version of the icon**, not a photograph of a real object. Keep proportions and outline of the source SVG. No extra objects, text, logos, or clutter.

## Locked studio

Use the same camera, lights, backdrop, scale, and padding for every icon:

- Apple three-quarter: **15° look-down**, **~30°** around the vertical from the **right** (front + right side; the icon faces slightly **left**)
- Every posed icon fits the same 1.55×1.55 box and is centered in that box, then shares one camera and lights
- Rounded tubes along the 2D silhouette (no filled faces, no extra subdivision)
- Infinite **dark** seamless studio (floor + cyc) so neon can bounce light
- Glossy-enough floor so each icon shows a reflection and colored bounce
- Key light **upper-left ~45°**, soft fill from the right, subtle rim, faint contact shadow
- Square **1024×1024** (optional 2048 later)
- Android-safe padding (about 18–25% inset) for adaptive-icon masks later

## Effects

- **tame** — satin/gloss plastic, no glow
- **neon** — rich saturated catalog-colored glow in the tubing (never white); the middle stays empty so contrast survives
- **glass** — transmission, catalog color as a tint
- **metal** — metallic, tight highlights
- **ceramic** — glazed dielectric, softer specular

Add icons only with a new YAML block plus source SVG. Add effects only with a new material string and output folder.
