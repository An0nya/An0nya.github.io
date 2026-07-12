#!/bin/sh
# Pre-push gate: fragment sync, TOC drift, prose-density budgets.
# Wired locally via .git/hooks/pre-push; mirrored in CI by
# .github/workflows/check.yml so pushes from other machines get caught too.
set -e
cd "$(dirname "$0")/.."
python3 tools/sync-nav.py --check
python3 tools/lint-toc.py index.html geometry.html lab/*.html
python3 tools/lint-prose.py --gate index.html geometry.html lab/*.html >/dev/null || {
  python3 tools/lint-prose.py --gate index.html geometry.html lab/*.html | grep -A20 'PROSE GATE FAILED'
  exit 1
}
echo "pre-push checks passed"
