# Implementation Plan

> Active work lives in [`BUILD_PLAN.md`](../BUILD_PLAN.md). Product brief: [`AGENT.md`](../AGENT.md).
> Status: 🔲 open · ✅ done · ❌ blocked.

## Milestone — First catalog (two icons × two effects)

| Task | Owner | Tests / fallback |
|------|--------|------------------|
| Canon lock (`AGENT.md`, BUILD_PLAN Product block) | AGENT | `scripts/check-product-brief.sh` |
| Catalog YAML + SVGs + locked prompts | AGENT | `scripts/validate_catalog.py` |
| Dry-run render jobs + seeds | AGENT | `uv run pytest` in `examples/python` |
| Catalog CI job | AUTO | `.github/workflows/ci.yml` catalog job |
| Blender/Cycles OptiX goldens | AGENT | Local `--backend blender`; CI does not run this |
## Next feature

1. ✅ Add icons only via YAML + SVG (`home`, `heart`).
2. ✅ Add material presets (glass, metal, ceramic) as extra effect folders on cached meshes.
3. Run `python3 scripts/agent-run.py watch-agent-gates --once --autofix`

If automated tests are not feasible, write the justification and fallback command in the feature spec before marking the BUILD_PLAN row ✅.
