# ADR-0006: Blender/Cycles as production renderer

- **Status:** Accepted
- **Date:** 2026-09-13
- **Deciders:** Hover Icons maintainers

## Context

[`AGENT.md`](../../AGENT.md) allows local SD + ControlNet, a hosted image API, or Blender/Cycles. The pack must keep classic icon silhouettes, identical camera/lights for every ID, and eventually render 4000+ icons × multiple materials. This host has an RTX 4090. GitHub Actions has no GPU.

ADR-0001 remains the child architecture-pick template (MVVM / Clean / Hexagonal) required by bootstrap gates. This ADR is the **renderer** decision.

## Decision

- **Production:** Blender/Cycles OptiX (CUDA fallback) on a local GPU. SVG → extrude/bevel → cached `meshes/{id}.glb` → material presets (`tame`, `neon`, later glass/metal/ceramic).
- **CI:** `RENDER_BACKEND=dry-run`. Validate YAML, fill prompts, log seeds. Never require CUDA, Blender, or PNGs.
- **SDXL / ControlNet:** deferred. Catalog still records ControlNet type/weight. Silhouette lock is the mesh.

## Consequences

- Prompt template stays locked and is logged on every job even when Blender does not consume it for shading.
- `bpy` is not in `uv.lock`; Blender is a subprocess via `BLENDER_BIN`.
- One Blender process per GPU. Batch throughput comes from OptiX, denoise, mesh cache, and `--resume`.
- NVIDIA drivers are local optional glue, not a FOSS production dependency.

## Alternatives considered

- SDXL + Canny ControlNet: seed-lockable but silhouette drift at catalog scale; ~8s/frame and poor batching on 4090.
- Hosted image APIs: secrets, cost, and weaker repeatability.
- Distro Blender packages: often no OptiX; rejected as the default install path.
