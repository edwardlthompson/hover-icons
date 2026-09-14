# Agent Instructions: Photorealistic FOSS Icon Pack

Save this file as `AGENT.md` (or `docs/AGENT_INSTRUCTIONS.md`) in the project root. An agent should treat this document as the source of truth for scaffolding and first builds.

## Mission

Build a **FOSS, GitHub-hosted icon pack** of **simple, instantly recognizable 2D icons** turned into **photo-realistic 3D objects**: bent from round tubing along the silhouette, empty in the middle, floating at a gentle angle, studio-lit, with a faint contact shadow. Keep silhouettes faithful to classic icons (e.g. camera, message bubble).

Provide a **base catalog** plus **effects** applied to the same meshes/renders:

- **tame** — satin/gloss plastic, no glow
- **neon** — rich saturated catalog-colored glow in the tubing (never white); the middle stays empty so the icon stays glanceable
- later: glass, metal, ceramic, etc. as extra material presets

An agent (or script) renders **every** icon from a **locked prompt template** + **YAML catalog** so results are **repeatable**.

## Bootstrap first

Use this repo as the project scaffolding:

**https://github.com/edwardlthompson/agent-project-bootstrap**

1. Clone or fork that bootstrap into the working directory (or use it as the parent template).
2. Follow **its** README / agent docs for repo layout, tooling, CI, license files, and how agents are expected to operate.
3. **Do not invent a parallel project structure.** Overlay the icon-pack folders and files below **on top of** the bootstrap layout. If the bootstrap already has `src/`, `scripts/`, `docs/`, `.github/`, keep those conventions.
4. After bootstrap is in place, apply everything in the rest of this file.

License intent: generated PNGs **CC0 or CC-BY**; original 2D sources keep **their** licenses. Document that clearly (bootstrap license files + a short `LICENSE-ASSETS.md`).

## Product rules (do not drift)

- **Contrast is king.** Icons must stay glanceable. Never flatten a face with full-surface emission or bloom. Neon is an edge tube only.
- Silhouette ≈ classic simple 2D icon (not a photoreal camera from life; a **3D version of the icon**).
- Same camera, lights, backdrop, scale, padding for **every** icon.
- Three-quarter view, **15° look-down** and **~30°** around the vertical (Apple: front + **right** side, so the icon faces slightly **left**), floating, infinite **dark** seamless studio.
- Key light **upper-left ~45°**, soft fill right, subtle rim, faint contact shadow.
- Square output (**1024×1024** first; optional 2048).
- No text, logos, extra objects, clutter.
- Android-friendly: leave safe padding for adaptive-icon masks later.

## Suggested overlay on bootstrap

Adapt names if the bootstrap already reserved them.

```
/
  AGENT.md                          # this file
  catalog/
    icons.yaml                      # master catalog
    sources/                        # simple 2D SVG/PNG (transparent)
      camera.svg
      messages.svg
      ...
  prompts/
    template.txt                    # master positive prompt
    negative.txt                    # identical negatives every run
  renders/
    base/                           # tame / neutral
    effects/
      neon/
      glass/                        # optional later
  meshes/                           # optional: glTF/blend if you go 3D-native
  scripts/
    render_icons.py                 # fill template + call renderer / agent
    validate_catalog.py
  docs/
    CONTRIBUTING.md
    STYLE.md

```

## Catalog format (`catalog/icons.yaml`)

One block per icon. The agent **never free-forms a prompt**; it only fills slots.

```yaml
pack:
  name: photoreal-simple-icons
  camera: "15-degree three-quarter, floating"
  backdrop: "infinite seamless dark studio"
  resolution: 1024
  controlnet:
    type: canny   # or depth
    weight: 0.75
  seed_strategy: "hash of icon id"   # or fixed integer per id

icons:
  - id: camera
    source: catalog/sources/camera.svg
    description: "classic simple camera: rounded rectangle body, large circular lens, small viewfinder bump on top"
    color: "#424242"
    effects:
      tame:
        material: "satin outline tubes, empty middle, soft gloss"
      neon:
        material: "gray neon gas in outline tubes, empty middle, never white"

  - id: messages
    source: catalog/sources/messages.svg
    description: "classic rounded speech-bubble outline with a small tail, empty middle"
    color: "#2196F3"
    effects:
      tame:
        material: "satin outline tubes, empty middle, soft gloss"
      neon:
        material: "blue neon gas in outline tubes, empty middle, never white"

```

Add icons only by **new YAML + source SVG**. Add effects only by **new material strings** (and output folders).

## Master prompt template (`prompts/template.txt`)

Fill `[ICON_DESCRIPTION]`, `[COLOR]`, `[MATERIAL_AND_EFFECT]`.

```
Photorealistic 3D render of a single [ICON_DESCRIPTION], colored [COLOR], [MATERIAL_AND_EFFECT].
The object is bent from round tubing along the classic 2D silhouette, with an empty middle and no filled face, keeping the exact outline and proportions.
It floats in mid-air at a gentle 15-degree look-down, three-quarter view from the right (front and right side visible, facing slightly left).
Studio product photography: single key light from upper-left at 45 degrees, soft fill from the right, subtle rim light, faint contact shadow on an infinite seamless dark studio backdrop.
Highly detailed surface with realistic reflections, subsurface scattering where appropriate, physically based materials.
8k, ultra-sharp, cinematic lighting, octane / redshift quality, no text, no extra objects, no background clutter.

```

## Negative prompt (`prompts/negative.txt`) — identical every time

```
flat, 2D, cartoon, illustration, sketch, low poly, deformed, extra limbs, text, watermark, logo, multiple objects, busy background, oversaturated, neon glow, blurry, noisy, cropped, out of frame

```

For the **neon** effect only: **remove** `neon glow` from the negative prompt (or the glow will be suppressed). All other negatives stay.

## Repeatability checklist (agent must enforce)

- Concatenate template + catalog fields only.
- ControlNet (Canny or Depth) on `source`, weight **0.7–0.85**.
- Seed = hash(`icon id` + `effect name`) or a stored integer per pair.
- Same resolution, aspect, padding.
- Same lighting language in every prompt.
- Log: icon id, effect, seed, ControlNet weight, git commit of catalog.

## Agent bootstrap sequence (run in order)

1. Clone/use **agent-project-bootstrap**; install whatever it requires.
2. Create overlay folders listed above if missing.
3. Write `prompts/template.txt` and `prompts/negative.txt` exactly as specified.
4. Create `catalog/icons.yaml` with **at least** `camera` and `messages`.
5. Add minimal simple SVGs under `catalog/sources/` (geometric, transparent, no gradients required).
6. Implement `scripts/render_icons.py` (or the bootstrap’s equivalent hook) that:
   - reads YAML
   - fills the template
   - calls the configured image/3D backend
   - writes `renders/base/.png` and `renders/effects//.png`
7. Render **camera / tame** first as the golden sample; then **camera / neon**; then **messages**.
8. Add `CONTRIBUTING.md`: drop SVG → add YAML block → run render script → PR.
9. Keep CI from bootstrap; add a job that validates YAML schema and that every `source` file exists.

## Backend note

This pack does **not** assume a specific GPU API. Use whatever the bootstrap (or the user’s environment) already wires: local SD + ControlNet, a hosted image API, or Blender/Cycles. The **prompt + catalog + ControlNet source** stay the same. Prefer a pipeline that can lock seed and ControlNet.

If only text-to-image is available, still pass the SVG as reference when the API allows; if not, put the description and “exact classic icon silhouette” in the prompt and keep all camera/light tokens identical.

## Out of scope until catalog works

- Full Android adaptive XML for every density
- Hundreds of icons
- Marketing site

First milestone: **bootstrap + two icons × two effects**, repeatable seeds, documented prompts.

## Style one-liner for humans

Simple 2D icon → same outline in 3D → glossy floating object → tame or neon (and later materials) from one catalog.
