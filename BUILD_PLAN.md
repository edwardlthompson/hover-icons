# Build Plan

<!-- remaining-tally -->
**Remaining:** AGENT 0 · AUTO 0 · HUMAN 0 · ADB 0 · **0 open**
<!-- /remaining-tally -->

Live board for Hover Icons. Finished work: [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md).

**Who:** `AGENT` code · `HUMAN` person · `ADB` device · `AUTO` CI/scripts
**State:** 🔲 open · ✅ done · ❌ blocked — reason

Format: `🔲 [AGENT] Short task`. Sequential `[AGENT]` first. Parallel scopes: [`docs/PARALLEL_AGENT_SCOPES.md`](docs/PARALLEL_AGENT_SCOPES.md). `/build` tries HUMAN/ADB after automation; failures go to `HUMAN_BACKLOG.md`.

## Product (do not drift)

Read [`AGENT.md`](AGENT.md) before any sprint row. That file is the original brief. Do not open `docs/INITIALIZATION_PROMPT.md` as the daily product spec.

**One-liner:** Simple 2D icon → same outline in 3D → glossy floating object → tame or neon (and later materials) from one catalog.

**This repo is an icon pack, not the bootstrap Golden Path app.** `examples/python/src/hello/` is CI glue. Do not implement About/donate chrome as the product.

**First milestone:** bootstrap + camera + messages × tame + neon, locked template, repeatable seeds.

**Product rules:** silhouette = classic 2D icon; same camera/lights/backdrop; 15° three-quarter; key 45° upper-left; 1024²; no text; Android-safe padding.

**Never:** free-form prompts; skip the catalog; invent a parallel tree; treat hello CLI as the app.

## Smoke gate (hard stop)

After every `[AGENT]` row: `python3 scripts/agent-run.py watch-agent-gates --once --autofix --scope auto`

After the **last** `[AGENT]`/`[AUTO]` row in a sprint is ✅, do **not** start the next sprint until this exits 0:

```bash
python3 scripts/agent-run.py smoke-sprint --require
```

Details: [`docs/SPRINT_SMOKE.md`](docs/SPRINT_SMOKE.md). Fail → leave the last row open or ❌; fix; re-run.

---

## Product sprints

### Sprint 0 — Customize

<!-- agent_count_target: 2 -->

### Sequential (must complete in order)

1. ✅ [AGENT] Clone bootstrap, rename `origin` to `bootstrap-upstream`, write `AGENT.md` verbatim, run non-interactive python init (no prune)
2. ✅ [AGENT] Restamp BUILD_PLAN Product block, `docs/spec.md`, `AGENTS.md` pointer, `.cursor/rules/product.mdc`, `AGENT_MEMORY.md`

### Parallel (safe after Sequential step 2)

| Task | Owner | Isolated scope |
|------|-------|----------------|
| Product-brief CI check | AGENT | `scripts/check-product-brief.sh` |
| Cursor product rule | AGENT | `.cursor/rules/product.mdc` |

### Sprint 1 — Catalog lock

<!-- agent_count_target: 2 -->

### Sequential (must complete in order)

1. ✅ [AGENT] Lock `catalog/icons.yaml` with camera and messages plus verbatim `prompts/template.txt` and `prompts/negative.txt`

### Parallel (safe after Sequential step 1)

| Task | Owner | Isolated scope |
|------|-------|----------------|
| Geometric CC0 SVGs | AGENT | `catalog/sources/` |
| Asset license + style docs | AGENT | `LICENSE-ASSETS.md` |

### Sprint 2 — Dry-run renderer

<!-- agent_count_target: 2 -->

### Sequential (must complete in order)

1. ✅ [AGENT] Lock `iconpack` job schema: fill slots only, seed hash, neon negative strip

### Parallel (safe after Sequential step 1)

| Task | Owner | Isolated scope |
|------|-------|----------------|
| Dry-run backend + CLIs | AGENT | `scripts/render_icons.py` |
| Catalog validate + tests | AGENT | `examples/python/tests/test_iconpack.py` |

### Sprint 3 — 4090 goldens

<!-- agent_count_target: 2 -->

### Sequential (must complete in order)

1. ✅ [AGENT] Lock Blender scene contract in `scripts/blender_batch.py` (15° camera, 45° key, 1024, padding)

### Parallel (safe after Sequential step 1)

| Task | Owner | Isolated scope |
|------|-------|----------------|
| Mesh cache + tame/neon materials | AGENT | `meshes/` |
| Render backend docs | AGENT | `docs/RENDER_BACKEND.md` |

### Waiting on a person

1. ✅ [AUTO] Create the GitHub product repo (`edwardlthompson/hover-icons`); do not push to `bootstrap-upstream`
2. ✅ [AUTO] Run `scripts/setup-github-repo.sh` and enable Dependabot alerts
3. ✅ [HUMAN] Install official Blender 4.2+ with OptiX; set `BLENDER_BIN` in `.env`
4. ✅ [AUTO] Opened [`docs/help/BATCH_COMMANDS.md`](docs/help/BATCH_COMMANDS.md) in the IDE (cheat sheet is in-repo; `/tour` keeps it discoverable)

### Open PRs (synced)

> Auto-managed on product repos too. Do not hand-edit rows inside the markers.

<!-- open-prs-sync:begin -->
_No open Dependabot or Release Please PRs._
<!-- open-prs-sync:end -->

### Template gaps (synced)

> Auto-managed Monday cron + `sync-template-gaps-build-plan`. Do not hand-edit inside markers. Plan-only — run `/upgrade` then name item numbers.

<!-- template-gaps-sync:begin -->
_No template gaps; .template-version matches upstream (or template maintainer N/A)._
<!-- template-gaps-sync:end -->

---

## Ongoing Maintenance

Not a checklist. GitHub Monday cron (`.github/workflows/weekly-health-check.yml`) already runs CI wait, security triage, parent template-gap BUILD_PLAN sync, radar, `update-deps` dry-run, Dependabot leftover list, open-PR BUILD_PLAN sync, and latest-release SBOM. `/ship` owns pre-release and the release tag.

---

## Archive

Older sprints: [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md).
