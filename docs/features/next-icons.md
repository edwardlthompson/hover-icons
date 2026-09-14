# Feature: next-icons

> Add catalog icons only via YAML + SVG. Extra pairs after camera/messages: home, heart, phone, email.

## Acceptance criteria

- ✅ `catalog/icons.yaml` lists `home`, `heart`, `phone`, and `email` with tame + neon
- ✅ Sources exist at `catalog/sources/{home,heart,phone,email}.svg`
- ✅ `scripts/validate_catalog.py` fails if a `source` is missing
- ✅ Dry-run jobs include the new ids; no free-form prompts

## Smoke scenario

1. _Given_ the catalog on disk
2. _When_ `python3 scripts/validate_catalog.py` and `python3 scripts/render_icons.py --backend dry-run`
3. _Then_ phone and email jobs appear in `renders/index.json` without PNG fakes

## Container map

| Layer | Path |
|-------|------|
| Logic | `examples/python/src/iconpack/catalog.py` |
| View | `catalog/sources/` |
| Tests | `examples/python/tests/test_iconpack.py` |
| Wiring | `catalog/icons.yaml` |

## Tests

- Automated: yes — `examples/python/tests/test_iconpack.py`
- Coverage: catalog ids, job order, missing source

## Fallback validation

- Why tests are not feasible: N/A
- Command: `python3 scripts/validate_catalog.py`

## Definition of Done

See `docs/FEATURE_MODULES.md`.
