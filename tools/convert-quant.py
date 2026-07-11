#!/usr/bin/env python3
"""Convert bolded quantitative results to the qx/qv voice.

Policy (owner-calibrated 2026-07-11): a <b>/<strong> whose text is ≥60%
quantitative characters is a data callout, not prose styling. It becomes:
  - <span class="qv">…</span>            if the whole content is one numeric token
  - <span class="qx">… <span class="qv">N</span> …</span>  otherwise
    (wash bounds the whole statement, mono+bold bites only the numbers;
     notation like α = / Σα = stays in the base font inside the wash)

Bolds that contain digits but fall below the threshold are SKIPPED and
reported — those are human calls. Protected regions (svg/style/script/pre/
table/figure/nav/footer) are never touched.

Usage: python3 tools/convert-quant.py PAGE.html [...]   (edits in place)
"""
import re
import sys

QUANT = set('0123456789+−–%.,×≈±=:/<>~ \t\nαβΣΔσ-')
NUM_TOKEN = re.compile(
    r'[+−–~≈±]?\d[\d.,]*(?:\s?[%×°])?'          # a number w/ optional affixes
    r'(?:\s*[→/]\s*[+−–]?\d[\d.,]*(?:\s?[%×°])?)*'  # optional range/ratio tail
)
PROTECT = re.compile(
    r'<svg.*?</svg>|<style.*?</style>|<script.*?</script>|<pre.*?</pre>'
    r'|<table.*?</table>|<figure.*?</figure>|<nav.*?</nav>|<footer.*?</footer>'
    r'|<!--.*?-->', re.S)
BOLD = re.compile(r'<(b|strong)>([^<]+)</\1>')


def is_quant(text):
    t = re.sub(r'&[a-z]+;|&#\d+;', '', text)
    if not t.strip() or not any(c.isdigit() for c in t):
        return False
    return sum(c in QUANT for c in t) / len(t) >= 0.6


def convert(content):
    """Return the qx/qv replacement for a quant-bold's inner text."""
    spans, last = [], 0
    for m in NUM_TOKEN.finditer(content):
        spans.append(content[last:m.start()])
        spans.append(f'<span class="qv">{m.group(0)}</span>')
        last = m.end()
    spans.append(content[last:])
    inner = ''.join(spans)
    lone = re.fullmatch(r'\s*<span class="qv">.*</span>\s*', inner)
    if lone and inner.count('<span') == 1:
        return inner.strip()          # pure number: standalone qv
    return f'<span class="qx">{inner}</span>'


def process(path):
    src = open(path).read()
    guards = []

    def stash(m):
        guards.append(m.group(0))
        return f'\x00{len(guards) - 1}\x00'

    body = PROTECT.sub(stash, src)
    converted, skipped = [], []

    def swap(m):
        text = m.group(2)
        if is_quant(text):
            converted.append(text)
            return convert(text)
        if any(c.isdigit() for c in text):
            skipped.append(text)
        return m.group(0)

    body = BOLD.sub(swap, body)
    body = re.sub(r'\x00(\d+)\x00', lambda m: guards[int(m.group(1))], body)
    if converted:
        open(path, 'w').write(body)
    print(f'{path}: converted {len(converted)}, '
          f'skipped-mixed {len(skipped)}')
    for s in converted:
        print(f'  qx/qv ← <b>{s}</b>')
    for s in skipped:
        print(f'  SKIP (human call): <b>{s}</b>')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        process(p)
