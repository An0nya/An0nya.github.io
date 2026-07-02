#!/usr/bin/env python3
"""Sync the shared site bar into every page that opts in with markers.

Single source of truth:  components/_site-bar.html
A page opts in by wrapping its <nav class="site-bar"> with:

    <!-- SITE-BAR:START — managed by tools/sync-nav.py; edit components/_site-bar.html -->
    ...(managed, do not hand-edit)...
    <!-- SITE-BAR:END -->

Usage:
    python3 tools/sync-nav.py           # stamp the fragment into all opted-in pages
    python3 tools/sync-nav.py --check   # report drift and exit 1 (for a pre-push hook)

Only files containing the START marker are touched, so drafts / bakeoff files
are left alone. The page-TOC sidebar is per-page and is NOT managed here.
"""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FRAGMENT_FILE = ROOT / "components" / "_site-bar.html"
START = "SITE-BAR:START"
END = "SITE-BAR:END"


def fragment_lines():
    return FRAGMENT_FILE.read_text(encoding="utf-8").rstrip("\n").split("\n")


def restamp(text, frag):
    """Replace the lines between each START/END marker with the fragment,
    indented to match the START marker. Returns (new_text, changed)."""
    lines = text.split("\n")
    out, i, changed = [], 0, False
    while i < len(lines):
        line = lines[i]
        if START in line:
            indent = line[: len(line) - len(line.lstrip())]
            block = [indent + f if f.strip() else "" for f in frag]
            j = i + 1
            while j < len(lines) and END not in lines[j]:
                j += 1
            if j >= len(lines):
                sys.exit(f"error: {START} without matching {END}")
            if lines[i + 1 : j] != block:
                changed = True
            out.append(line)          # START marker
            out.extend(block)         # managed fragment
            out.append(lines[j])      # END marker
            i = j + 1
        else:
            out.append(line)
            i += 1
    return "\n".join(out), changed


def main():
    check = "--check" in sys.argv
    frag = fragment_lines()
    drift = []
    for path in sorted(ROOT.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        if START not in text:
            continue
        new, changed = restamp(text, frag)
        if changed:
            drift.append(path.relative_to(ROOT))
            if not check:
                path.write_text(new, encoding="utf-8")

    if check:
        if drift:
            print("site bar OUT OF SYNC — run tools/sync-nav.py:")
            for d in drift:
                print(f"  {d}")
            sys.exit(1)
        print("site bar in sync")
    else:
        if drift:
            print("synced site bar into:")
            for d in drift:
                print(f"  {d}")
        else:
            print("nothing to sync — all pages already match")


if __name__ == "__main__":
    main()
