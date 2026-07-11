#!/usr/bin/env python3
"""Prose-density linter (a report, like sync-nav.py --check, not a build step).

The site's editorial rule for running body prose: per paragraph, max ONE
em-dash, max ONE styled "pop" (italic/bold/accent-highlight), ideally max ONE
observation/interpretation chip. Structural/layout uses of dashes and styling
(figure captions, header-grid fields, kickers, marginalia, the page TOC,
tables, headings, deks, nav/footer, walkback headlines) are design grammar,
not prose, and are exempt.

This tool only FLAGS violations for human review. It never edits a page.

Usage:
    python3 tools/lint-prose.py lab/01_minicpm5_sigma_alpha.html [more.html ...]

Exit code is always 0 — this is a report, not a gate.
"""
import re
import sys
from html.parser import HTMLParser

# Tags whose entire subtree is exempt structural content, never prose.
EXEMPT_TAGS = {"figcaption", "table", "nav", "footer",
               "h1", "h2", "h3", "h4", "h5", "h6"}

# Classes that mark an element (any tag) as exempt structural content.
# nb-kicker / nb-record / nb-marginalia / page-toc / fig-note: layout regions.
# dek: the standfirst line under the title, not a body paragraph.
# wbhead: the bold headline span inside a walkback <li> — the REST of that
#   <li> is still prose and stays in scope; only this inner span is skipped.
EXEMPT_CLASSES = {"nb-kicker", "nb-record", "nb-marginalia", "page-toc",
                   "fig-note", "dek", "wbhead"}

# Prose units: each <p> and each <li> that survives exemption stripping.
UNIT_TAGS = {"p", "li"}

# "Pop" = a styled emphasis in running prose.
POP_TAGS = {"em", "i", "b", "strong"}

MIN_UNIT_LEN = 40


def classes_of(attrs):
    for name, value in attrs:
        if name == "class" and value:
            return set(value.split())
    return set()


class Frame:
    __slots__ = ("tag", "exempt")

    def __init__(self, tag, exempt):
        self.tag = tag
        self.exempt = exempt


class Unit:
    def __init__(self, tag, line):
        self.tag = tag
        self.line = line
        self.text_parts = []
        self.dash = 0
        self.pop = 0
        self.chip = 0

    def text(self):
        return re.sub(r"\s+", " ", "".join(self.text_parts)).strip()


class ProseLinter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # Frame stack, mirrors open tags
        self.units_stack = []    # currently-open prose units (p/li)
        self.finished = []       # completed units

    def _exempt(self):
        return self.stack[-1].exempt if self.stack else False

    def handle_starttag(self, tag, attrs):
        parent_exempt = self._exempt()
        classes = classes_of(attrs)
        trigger = tag in EXEMPT_TAGS or bool(classes & EXEMPT_CLASSES)
        exempt = parent_exempt or trigger
        self.stack.append(Frame(tag, exempt))

        if tag in UNIT_TAGS and not exempt:
            line, _ = self.getpos()
            self.units_stack.append(Unit(tag, line))
            return

        if parent_exempt or not self.units_stack:
            return

        if tag in POP_TAGS:
            for u in self.units_stack:
                u.pop += 1
        elif tag == "span":
            if any(c.startswith("hl-") for c in classes) and not (classes & {"mono", "code"}):
                for u in self.units_stack:
                    u.pop += 1
            elif "olabel" in classes:
                for u in self.units_stack:
                    u.chip += 1

    def handle_startendtag(self, tag, attrs):
        # self-closing tags (e.g. <br/>) never carry text/pop/chip semantics here
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if not self.stack:
            return
        frame = self.stack.pop()
        if frame.tag in UNIT_TAGS and not frame.exempt and self.units_stack:
            u = self.units_stack.pop()
            if len(u.text()) >= MIN_UNIT_LEN:
                self.finished.append(u)

    def handle_data(self, data):
        if self._exempt() or not self.units_stack:
            return
        for u in self.units_stack:
            u.text_parts.append(data)
            u.dash += data.count("—")  # literal em-dash


def strip_preserving_lines(text, pattern):
    """Remove regex matches but keep the file's line count intact, so
    line numbers reported later still point at the right place."""
    def repl(m):
        return "\n" * m.group(0).count("\n")
    return re.sub(pattern, repl, text, flags=re.S)


def strip_noise(text):
    text = strip_preserving_lines(text, r"<!--.*?-->")
    text = strip_preserving_lines(text, r"<svg\b.*?</svg>")
    text = strip_preserving_lines(text, r"<style\b.*?</style>")
    text = strip_preserving_lines(text, r"<script\b.*?</script>")
    return text


def lint_file(path):
    raw = open(path, encoding="utf-8").read()
    cleaned = strip_noise(raw)

    parser = ProseLinter()
    parser.feed(cleaned)
    parser.close()

    units = parser.finished
    violations = []
    dash_v = pop_v = chip_v = 0
    for u in units:
        bad = u.dash > 1 or u.pop > 1 or u.chip > 1
        if not bad:
            continue
        if u.dash > 1:
            dash_v += 1
        if u.pop > 1:
            pop_v += 1
        if u.chip > 1:
            chip_v += 1
        snippet = u.text()[:80]
        violations.append(
            f"{path}:{u.line}  [D:{u.dash} P:{u.pop} C:{u.chip}]  {snippet}…"
        )

    for line in violations:
        print(line)
    print(
        f"{path}: {len(units)} units scanned, {len(violations)} violations "
        f"(dash:{dash_v} pop:{pop_v} chip:{chip_v})"
    )


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: lint-prose.py PAGE.html [PAGE2.html ...]")
    for path in sys.argv[1:]:
        lint_file(path)


if __name__ == "__main__":
    main()
