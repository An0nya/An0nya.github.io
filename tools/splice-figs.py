#!/usr/bin/env python3
"""Re-splice figure SVGs from figures-src/ into a lab page (a build step,
like sync-nav.py).

Workflow: edit the standalone fig_XX_*.svg (and its .mobile.svg twin) in
figures-src/, then run this from the repo root:

    python3 tools/splice-figs.py lab/01_minicpm5_sigma_alpha.html

It replaces each inline <svg> inside the page's <figure> blocks with the
current file content, desktop and mobile variants both, preserving the
page-side role/aria-label attrs. Add pages by extending MAPS (figure id ->
filename stem). Figure *generators* (gen_fig_*.py) stay in
rys-tools/drafts/figures/ with their data; if one is re-run, copy its output
here before splicing.
"""
import os
import re
import sys

FIGDIR = os.path.join(os.path.dirname(__file__), "..", "figures-src")

MAPS = {
    "lab/01_minicpm5_sigma_alpha.html": {
        "fig1": "fig_01_residual_highway",
        "fig2": "fig_01_arithmetic_cliff",
        "fig3": "fig_01_split_curvature",
        "fig4": "fig_01_single_vs_split",
        "fig5": "fig_01_sigma_curve",
        "fig6": "fig_01_exposure",
    },
}


def main():
    page = sys.argv[1]
    if page not in MAPS:
        sys.exit(f"{page} not wired into MAPS yet — add its fig-id -> filename map first")
    mapping = MAPS[page]
    text = open(page).read()
    spliced = []

    def splice_figure(m):
        fid, body = m.group(1), m.group(2)
        stem = mapping.get(fid)
        if stem is None:
            return m.group(0)

        def sub_svg(mm):
            variant, old_svg = mm.group(1), mm.group(0)
            path = f"{FIGDIR}/{stem}{'.mobile' if variant == 'mobile' else ''}.svg"
            svg = open(path).read().strip()
            # keep the page-side a11y attrs (role="img" aria-label="...") across splices
            a11y = re.search(r'<svg[^>]*?(role="img" aria-label="[^"]*")', old_svg)
            if a11y and 'role="img"' not in svg:
                svg = svg.replace('<svg ', f'<svg {a11y.group(1)} ', 1)
            spliced.append(f"{fid}/{variant} <- {os.path.basename(path)}")
            return f'<div class="fig-{variant}">{svg}'

        body = re.sub(r'<div class="fig-(desktop|mobile)">\s*<svg.*?</svg>',
                      sub_svg, body, flags=re.S)
        return f'<figure class="figure" id="{fid}">{body}</figure>'

    text = re.sub(r'<figure class="figure" id="(fig\d+)">(.*?)</figure>',
                  splice_figure, text, flags=re.S)
    open(page, "w").write(text)
    print(f"spliced {len(spliced)} svgs into {page}:")
    for line in spliced:
        print(" ", line)


if __name__ == "__main__":
    main()
