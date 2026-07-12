#!/usr/bin/env python3
"""TOC drift lint: every page-toc link must point at a real section id, and
every <section id> that contains an <h2> must appear in the page TOC
(full coverage established by pass 11). Pages without a page-toc are skipped.

Usage:
    python3 tools/lint-toc.py index.html lab/*.html

Exit 1 on any drift — safe for the pre-push hook / CI.
"""
import re
import sys

failed = False
for path in sys.argv[1:]:
    text = open(path, encoding="utf-8").read()
    if 'class="page-toc"' not in text:
        continue
    toc = re.search(r'<aside class="page-toc".*?</aside>', text, re.S)
    toc_ids = set(re.findall(r'href="#([^"]+)"', toc.group(0)))
    sections = re.findall(r'<section[^>]*\bid="([^"]+)"(.*?)</section>',
                          text, re.S)
    h2_ids = {sid for sid, body in sections if "<h2" in body}
    missing_target = toc_ids - {sid for sid, _ in sections}
    uncovered = h2_ids - toc_ids
    for sid in sorted(missing_target):
        print(f"{path}: TOC links #{sid} but no such <section id>")
        failed = True
    for sid in sorted(uncovered):
        print(f"{path}: section #{sid} has an <h2> but is missing from the TOC")
        failed = True

if failed:
    sys.exit(1)
print("TOCs in sync")
