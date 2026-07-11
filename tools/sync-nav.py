#!/usr/bin/env python3
"""Sync shared fragments (site bar, footer) into every page that opts in with markers.

Single source of truth per fragment:  components/_site-bar.html, components/_footer.html
A page opts in by wrapping its <nav class="site-bar"> with:

    <!-- SITE-BAR:START — managed by tools/sync-nav.py; edit components/_site-bar.html -->
    ...(managed, do not hand-edit)...
    <!-- SITE-BAR:END -->

and/or its <footer> with:

    <!-- FOOTER:START — managed by tools/sync-nav.py; edit components/_footer.html -->
    ...(managed, do not hand-edit)...
    <!-- FOOTER:END -->

Usage:
    python3 tools/sync-nav.py           # stamp the fragments into all opted-in pages
    python3 tools/sync-nav.py --check   # report drift and exit 1 (for a pre-push hook)

Only files containing a START marker are touched, so drafts / bakeoff files
are left alone. The page-TOC sidebar is per-page and is NOT managed here.
"""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FRAGMENTS = [
    (ROOT / "components" / "_site-bar.html", "SITE-BAR:START", "SITE-BAR:END", "site bar"),
    (ROOT / "components" / "_footer.html", "FOOTER:START", "FOOTER:END", "footer"),
]


def fragment_lines(fragment_file):
    return fragment_file.read_text(encoding="utf-8").rstrip("\n").split("\n")


def restamp(text, frag, start, end):
    """Replace the lines between each START/END marker with the fragment,
    indented to match the START marker. Returns (new_text, changed)."""
    lines = text.split("\n")
    out, i, changed = [], 0, False
    while i < len(lines):
        line = lines[i]
        if start in line:
            indent = line[: len(line) - len(line.lstrip())]
            block = [indent + f if f.strip() else "" for f in frag]
            j = i + 1
            while j < len(lines) and end not in lines[j]:
                j += 1
            if j >= len(lines):
                sys.exit(f"error: {start} without matching {end}")
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
    drift = {}  # fragment label -> list of paths touched
    for path in sorted(ROOT.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        touched = False
        for fragment_file, start, end, label in FRAGMENTS:
            if start not in text:
                continue
            frag = fragment_lines(fragment_file)
            text, changed = restamp(text, frag, start, end)
            if changed:
                drift.setdefault(label, []).append(path.relative_to(ROOT))
                touched = True
        if touched and not check:
            path.write_text(text, encoding="utf-8")

    if check:
        if drift:
            print("fragments OUT OF SYNC — run tools/sync-nav.py:")
            for label, paths in drift.items():
                print(f"  {label}:")
                for d in paths:
                    print(f"    {d}")
            sys.exit(1)
        print("fragments in sync")
    else:
        if drift:
            for label, paths in drift.items():
                print(f"synced {label} into:")
                for d in paths:
                    print(f"  {d}")
        else:
            print("nothing to sync — all pages already match")


if __name__ == "__main__":
    main()
