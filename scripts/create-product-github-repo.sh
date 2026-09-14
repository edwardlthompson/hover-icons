#!/usr/bin/env bash
# Create origin GitHub repo for this child. Never push to bootstrap-upstream.
# Usage: scripts/create-product-github-repo.sh [owner/name]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "What failed: gh CLI missing"
  echo "What to run: https://cli.github.com/ then gh auth login"
  exit 1
fi

OWNER="$(gh api user --jq .login)"
DEFAULT_NAME="$(basename "$ROOT" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9-' '-')"
DEFAULT_NAME="${DEFAULT_NAME#-}"
DEFAULT_NAME="${DEFAULT_NAME%-}"
REPO_SLUG="${1:-${GITHUB_REPO:-${OWNER}/${DEFAULT_NAME}}}"
if [[ "$REPO_SLUG" != */* ]]; then
  REPO_SLUG="${OWNER}/${REPO_SLUG}"
fi
REPO_NAME="${REPO_SLUG#*/}"

if git remote get-url bootstrap-upstream >/dev/null 2>&1; then
  UP_URL="$(git remote get-url bootstrap-upstream)"
  echo "OK   bootstrap-upstream stays ${UP_URL} (never push here)"
fi

if git remote get-url origin >/dev/null 2>&1; then
  ORIGIN_URL="$(git remote get-url origin)"
  if [[ "$ORIGIN_URL" == *agent-project-bootstrap* ]]; then
    echo "What failed: origin still points at the bootstrap template"
    echo "What to run: git remote rename origin bootstrap-upstream"
    exit 1
  fi
fi

DESC="$(python3 - <<'PY'
from pathlib import Path
text = Path("docs/GITHUB_ABOUT.md").read_text(encoding="utf-8")
for line in text.splitlines():
    if line.startswith("Hover Icons"):
        print(line.strip()[:350])
        break
PY
)"
[ -n "$DESC" ] || DESC="FOSS photorealistic 3D icon pack from a locked YAML catalog"

if gh repo view "$REPO_SLUG" >/dev/null 2>&1; then
  echo "OK   GitHub repo already exists: ${REPO_SLUG}"
else
  gh repo create "$REPO_SLUG" --public --description "$DESC" --disable-wiki --clone=false
  echo "OK   created https://github.com/${REPO_SLUG}"
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "OK   origin is $(git remote get-url origin)"
else
  git remote add origin "https://github.com/${REPO_SLUG}.git"
  echo "OK   added origin https://github.com/${REPO_SLUG}.git"
fi

gh repo edit "$REPO_SLUG" --description "$DESC" --homepage "https://${OWNER}.github.io/${REPO_NAME}/" >/dev/null
gh repo edit "$REPO_SLUG" --add-topic foss,icons,blender,python,cc0,3d >/dev/null || true
gh api --method PUT "repos/${REPO_SLUG}/automated-security-fixes" >/dev/null
gh api --method PUT "user/subscriptions/${REPO_SLUG}" -f subscribed=true -f ignored=false >/dev/null
echo "OK   Dependabot security updates + watch Issues"
echo "$REPO_SLUG"
