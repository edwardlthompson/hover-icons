#!/usr/bin/env bash
# Fail if the original icon-pack brief has drifted out of AGENT.md / BUILD_PLAN.md.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() {
  echo "FAIL: $1" >&2
  echo "What failed: product brief anti-amnesia check" >&2
  echo "What to run: bash scripts/check-product-brief.sh" >&2
  echo "Why: AGENT.md and BUILD_PLAN.md must keep the original icon-pack idea." >&2
  exit 1
}

if [ ! -f AGENT.md ]; then
  fail "AGENT.md is missing (original brief)"
fi

if ! grep -q "photoreal-simple-icons" AGENT.md; then
  fail "AGENT.md must name pack photoreal-simple-icons"
fi

if ! grep -q "Simple 2D icon" BUILD_PLAN.md; then
  fail "BUILD_PLAN.md must keep the style one-liner"
fi

for token in camera messages tame neon; do
  if ! grep -q "$token" BUILD_PLAN.md; then
    fail "BUILD_PLAN.md must mention ${token}"
  fi
done

if ! grep -q "do not drift" BUILD_PLAN.md; then
  fail "BUILD_PLAN.md must keep the Product (do not drift) block"
fi

if ! grep -q "AGENT.md" AGENTS.md; then
  fail "AGENTS.md must point at AGENT.md"
fi

echo "OK   product brief intact (AGENT.md + BUILD_PLAN one-liner / camera / messages / tame / neon)"
