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

**First milestone (done):** camera + messages × tame + neon, locked template, repeatable seeds. Goldens: `renders/golden/`.

**Product rules:** silhouette = classic 2D icon; **contrast is king** (glanceable; neon = edge tube only); same camera/lights/backdrop; Apple 15° look-down / 30° right three-quarter (faces slightly left); key 45° upper-left; 1024²; no text; Android-safe padding.

**Never:** free-form prompts; skip the catalog; invent a parallel tree; treat hello CLI as the app.

## Smoke gate (hard stop)

After every `[AGENT]` row: `python3 scripts/agent-run.py watch-agent-gates --once --autofix --scope auto`

After the last `[AGENT]`/`[AUTO]` row in a sprint is ✅:

```bash
python3 scripts/agent-run.py smoke-sprint --require

```

Details: [`docs/SPRINT_SMOKE.md`](docs/SPRINT_SMOKE.md). Fail → leave the last row 🔲 or ❌; fix; re-run.

---

## Next

### Open PRs (synced)

<!-- parallel_exception: auto-synced GitHub PRs; not a parallel AGENT split -->

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

> **Sprints 0–3** archived in COMPLETED_TASKS.md @ `b1b72f8`.
> **Sprint 4** archived in COMPLETED_TASKS.md @ `b1b72f8` (local catalog follow-on).

| Sprint | Complete | Archive |
|--------|----------|---------|
| 0 Customize | 2026-09-13 | [COMPLETED_TASKS.md](COMPLETED_TASKS.md) |
| 1 Catalog lock | 2026-09-13 | [COMPLETED_TASKS.md](COMPLETED_TASKS.md) |
| 2 Dry-run renderer | 2026-09-13 | [COMPLETED_TASKS.md](COMPLETED_TASKS.md) |
| 3 4090 goldens | 2026-09-13 | [COMPLETED_TASKS.md](COMPLETED_TASKS.md) |
| 4 More icons and materials | 2026-09-13 | [COMPLETED_TASKS.md](COMPLETED_TASKS.md) |
Template Lightroom leftover stays in [`HUMAN_BACKLOG.md`](HUMAN_BACKLOG.md); it is not this pack.
