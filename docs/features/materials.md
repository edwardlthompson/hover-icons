# Feature: materials

> Glass, metal, and ceramic presets on the same cached meshes as tame/neon.

## Acceptance criteria

- ✅ Every catalog icon defines `glass`, `metal`, and `ceramic` material strings
- ✅ Dry-run jobs write `renders/effects/{glass,metal,ceramic}/{id}.json`
- ✅ `scripts/blender_batch.py` maps those names to Principled presets and rejects unknown effects
- ✅ CI still never runs Blender or writes fake goldens

## Smoke scenario

1. _Given_ the catalog and locked scene
2. _When_ `python3 scripts/render_icons.py --backend dry-run --effects glass`
3. _Then_ sidecars exist under `renders/effects/glass/` and prompts fill catalog slots only

## Container map

| Layer | Path |
|-------|------|
| Logic | `scripts/blender_batch.py` `_material` |
| View | N/A (same SVG meshes) |
| Tests | `examples/python/tests/test_iconpack.py`, `tests/test_blender_presets.py` |
| Wiring | `catalog/icons.yaml` effects keys |

## Tests

- Automated: yes — dry-run job paths + blender_batch source lock
- Coverage: extra effect folders, unknown effect rejected in Blender script

## Fallback validation

- Why tests are not feasible: N/A
- Command: `python3 scripts/render_icons.py --backend dry-run`

## Definition of Done

See `docs/FEATURE_MODULES.md`.
