#!/usr/bin/env python3
"""Prose-density linter (a report, like sync-nav.py --check, not a build step).

The site's editorial rule for running body prose: per paragraph, max ONE
em-dash, max ONE styled "pop" (italic/bold/accent-highlight). Structural/
layout uses of dashes and styling (figure captions, header-grid fields,
kickers, marginalia, the page TOC, tables, headings, deks, nav/footer,
walkback headlines) are design grammar, not prose, and are exempt.

Observation/interpretation chips (span.olabel) are ALSO design grammar —
chips pair an observation with an interpretation by intent, so chip count
never flags a unit. It's still tallied per file, informationally, in the
summary line.

A <b>/<strong> element whose text is mostly numeric/quantitative (digits,
math symbols, Greek letters used as math, whitespace) is a data callout,
not prose styling, so it doesn't count toward the pop budget either — it's
tallied separately as Q. <em>/<i> and span.hl-* always count as pops
regardless of content.

v3 additions (owner calibration 2026-07-11 night):
  - LEAD rule: the page's first prose paragraph and the first paragraph after
    each <h2> flag at dash >= 1 (priming: the opener sets the reader's prior,
    so em-dashes there confirm "AI-written" for a suspicious reader).
  - qx budget: span.qx / standalone span.qv marks count against a budget
    proportional to the unit's quantitative-result density (numeric tokens N):
    N<=2 -> N, N in 3..4 -> 2, N>=5 -> 3. Over budget flags for demotion to
    bare prose numerals. Load-bearing sections may exceed — human call.

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

# HTML5 void elements: no end tag ever comes, so never push a Frame for them
# (an unpopped frame skews the stack and can mark the whole rest of the page
# exempt — this is why hrm/gemma31b scanned 0 units before v3.1).
VOID_TAGS = {"br", "img", "hr", "input", "meta", "link", "source", "wbr",
             "col", "area", "base", "embed", "track"}

# b/strong are the only tags eligible for the quant-callout discount; em/i
# always count as pops regardless of content (per owner calibration).
QUANT_ELIGIBLE_TAGS = {"b", "strong"}

MIN_UNIT_LEN = 40

# "Quantitative characters" for the pop-budget discount: digits, math/measure
# symbols, and Greek letters used as math notation. Whitespace also counts
# (doesn't count against the ratio) per owner calibration.
QUANT_CHARS = set("0123456789+−–%.,×≈±=:/<>αβΣΔσ")
QUANT_THRESHOLD = 0.6


def is_quant_text(text):
    if not text:
        return False
    total = len(text)
    quant = sum(1 for c in text if c in QUANT_CHARS or c.isspace())
    return (quant / total) >= QUANT_THRESHOLD


def classes_of(attrs):
    for name, value in attrs:
        if name == "class" and value:
            return set(value.split())
    return set()


class Frame:
    __slots__ = ("tag", "exempt", "qx")

    def __init__(self, tag, exempt, qx=False):
        self.tag = tag
        self.exempt = exempt
        self.qx = qx


class Unit:
    def __init__(self, tag, line, lead=False):
        self.tag = tag
        self.line = line
        self.lead = lead
        self.text_parts = []
        self.dash = 0
        self.pop = 0
        self.chip = 0
        self.quant = 0
        self.qx = 0

    def text(self):
        return re.sub(r"\s+", " ", "".join(self.text_parts)).strip()

    def num_tokens(self):
        # rough count of distinct quantitative results in the unit's text
        return len(re.findall(r"[+−–~≈±]?\d[\d.,]*", self.text()))

    def qx_budget(self):
        n = self.num_tokens()
        if n <= 2:
            return n
        if n <= 4:
            return 2
        return 3


class ProseLinter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # Frame stack, mirrors open tags
        self.units_stack = []    # currently-open prose units (p/li)
        self.finished = []       # completed units
        self.quant_stack = []    # open b/strong elements pending quant classification
        self.qx_depth = 0        # nesting depth of open span.qx (qv inside qx ≠ 2 marks)
        self.lead_pending = True # next non-exempt <p> is a lead unit (page open / post-h2)

    def _exempt(self):
        return self.stack[-1].exempt if self.stack else False

    def handle_starttag(self, tag, attrs):
        if tag in VOID_TAGS:
            return
        parent_exempt = self._exempt()
        classes = classes_of(attrs)
        trigger = tag in EXEMPT_TAGS or bool(classes & EXEMPT_CLASSES)
        exempt = parent_exempt or trigger

        is_qx = tag == "span" and "qx" in classes and not exempt
        self.stack.append(Frame(tag, exempt, qx=is_qx))

        if tag in UNIT_TAGS and not exempt:
            line, _ = self.getpos()
            lead = tag == "p" and self.lead_pending
            if lead:
                self.lead_pending = False
            self.units_stack.append(Unit(tag, line, lead=lead))
            return

        if parent_exempt or not self.units_stack:
            return

        if is_qx:
            # one qx statement = one mark, however many qv's it contains
            for u in self.units_stack:
                u.qx += 1
            self.qx_depth += 1
            return
        if tag == "span" and "qv" in classes and self.qx_depth == 0:
            # standalone qv (bare washed number) is its own mark
            for u in self.units_stack:
                u.qx += 1
            return

        if tag in QUANT_ELIGIBLE_TAGS:
            # Defer the pop/Q decision until we've seen the element's text.
            self.quant_stack.append({"units": list(self.units_stack), "text": []})
        elif tag in POP_TAGS:
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
        if tag in VOID_TAGS or not self.stack:
            return
        frame = self.stack.pop()
        if frame.qx:
            self.qx_depth -= 1

        if frame.tag == "h2":
            self.lead_pending = True

        if frame.tag in QUANT_ELIGIBLE_TAGS and self.quant_stack:
            entry = self.quant_stack.pop()
            text = "".join(entry["text"])
            if is_quant_text(text):
                for u in entry["units"]:
                    u.quant += 1
            else:
                for u in entry["units"]:
                    u.pop += 1

        if frame.tag in UNIT_TAGS and not frame.exempt and self.units_stack:
            u = self.units_stack.pop()
            if len(u.text()) >= MIN_UNIT_LEN:
                self.finished.append(u)

    def handle_data(self, data):
        if self.quant_stack:
            self.quant_stack[-1]["text"].append(data)
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
    dash_v = pop_v = lead_v = qx_v = 0
    chip_total = sum(u.chip for u in units)
    for u in units:
        # Chips are design grammar (observation/interpretation pairs by
        # intent) — they never flag a unit, only dash/pop/qx budgets do.
        over_qx = u.qx > u.qx_budget()
        lead_dash = u.lead and u.dash >= 1
        bad = u.dash > 1 or u.pop > 1 or over_qx or lead_dash
        if not bad:
            continue
        if u.dash > 1:
            dash_v += 1
        if u.pop > 1:
            pop_v += 1
        if lead_dash:
            lead_v += 1
        if over_qx:
            qx_v += 1
        snippet = u.text()[:80]
        line = (f"{path}:{u.line}  [D:{u.dash} P:{u.pop} Q:{u.quant} "
                f"X:{u.qx}/{u.qx_budget()}]  {snippet}…")
        if u.dash > 1:
            line += " → rewrite: comma / parens / colon / sentence break / bullets"
        elif lead_dash:
            line += " → LEAD unit (page/section opener): restructure the dash out"
        if over_qx:
            line += " → qx over budget: demote surplus to bare numerals"
        violations.append(line)

    for line in violations:
        print(line)
    print(
        f"{path}: {len(units)} units scanned, {len(violations)} violations "
        f"(dash:{dash_v} pop:{pop_v} lead:{lead_v} qx:{qx_v}) | "
        f"chips:{chip_total} (informational, never flags)"
    )


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: lint-prose.py PAGE.html [PAGE2.html ...]")
    for path in sys.argv[1:]:
        lint_file(path)


if __name__ == "__main__":
    main()
