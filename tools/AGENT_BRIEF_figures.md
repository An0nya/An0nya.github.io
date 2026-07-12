# Figure-build agent brief (hrm.html Fig 1 + Fig 2)

You are building the two missing figures for `lab/hrm.html` (currently
`.fig-stub` placeholders) as inline SVGs in the site's figure pattern, FROM
REAL DATA ONLY. The data lives in `~/Projects/hrm-mlx/figs/` — that repo is
READ-ONLY for you; never write there.

## Hard rules
- NO DATA INVENTION. Every numeric coordinate, axis tick, and plotted value
  in your SVGs must derive from a JSON value (or be pure layout geometry:
  margins, viewBox, gridline positions at round axis ticks). If a value you
  want isn't in the JSONs, FLAG it — do not estimate it.
- Do NOT alter the existing `.nb-figcap` caption text in hrm.html by one
  character, even where it disagrees with the data (there is a known
  discrepancy — see FLAG-0 below). Captions are the owner's.
- Files you may edit: `figures-src/fig_hrm_*.svg` (new), `lab/hrm.html`
  (stub replacement only), `tools/splice-figs.py` (MAPS entry only).
- Do not commit. Branch is wave2-migrations; do not switch.
- Follow the site figure pattern — copy the skeleton from any recent
  `figures-src/fig_09_*.svg` + its usage in `lab/self-improving-memory.html`:
  desktop + `.mobile.svg` companion, `var(--token,#fallback)` colors ONLY
  (tokens from `tokens/colors.css`; no raw hex outside fallbacks),
  `<title>` + `<desc>` in each SVG, mono/serif font vars, page-side wrapper
  `<figure class="figure" id="figN"><div class="nb-plate"><div class="fig-desktop">…
  <div class="fig-mobile">…` matching the reference page.
- Owner is protanopic: series may NEVER be distinguished by a red↔green hue
  pair; differentiate by dash/shape/weight plus cool-palette tokens
  (--accent / --fourth / --neg / --pos are all cool or violet in the default
  skin — verify in tokens/colors.css before using).

## FLAG-0 (pre-known, restate in your report)
The Fig 1 caption says "cos→0.71" at the final layer. The regenerated data
(`exp_baseline_geometry.json`) and the original matplotlib PNG both show the
final adjacent-cos ≈0.872 (H) / ≈0.898 (L); nothing in the baseline data hits
0.71. Draw the DATA, flag the caption number for the owner. Do not edit the
caption.

## Fig 1 — depth geometry (replaces the `#fig1`-area stub at ~line 229)
Data: `~/Projects/hrm-mlx/figs/exp_baseline_geometry.json`
- `unrolled`: 129 states → 128 `adj_cos` + `delta_norm` pairs with `labels`
  (`c{H}.L{l}.l{layer}` / `c{H}.H.l{layer}`) — this is the "128 unrolled
  layers" the caption describes. Main panel: adjacent-layer cosine line
  (left axis) + ‖Δ‖ line (right axis, distinguished by dash+token, not hue
  alone) across all 128 transitions. Mark pass boundaries (label changes,
  e.g. c0.L0→c0.L1) with subtle vertical rules so the injection-point dips
  read as structure, not noise.
- `H_last` / `L_last`: 15 adj pairs each (last-pass per-module depth) —
  small secondary panel or overlay strip supporting the caption's "L is
  noisier per layer than H" claim. Your choice of composition; keep it
  honest to the values.
- Mobile variant: same data, stacked/reflowed, fewer tick labels — never
  fewer data points.

## Fig 2 — the 35-config sweep (replaces the `#fig2`-area stub at ~line 323)
Data: per-config `~/Projects/hrm-mlx/figs/exp_<config>_interlingua.json` +
`exp_<config>_battery.json` (34 interlingua, 29 battery files; page says 35
configs — plot the intersection that has BOTH files, report the exact count
and the missing-config list, FLAG the shortfall vs 35).
- x = interlingua strength = max over `math_per_cycle` values (the code
  calls this "the headline metric"; state this formula in your report).
- y = battery score = mean of per-item `rate` over the items present in
  that config's battery.json (report the formula and per-config item counts;
  if item sets differ across configs, FLAG it and say how you handled it).
- Mark configs that solved age-sort (`age_sort.rate == 1.0`) with a distinct
  marker SHAPE (not hue alone), per the caption ("solved-the-age-sort
  configs marked").
- Label at least the configs the caption names (rys_l, ratio_hi_l,
  combo_rys_anchor) if present in the data; a few more labels for anchor
  points are fine, all from real config names.
- Include a compact per-config (x, y, solved) table in your REPORT so the
  owner can spot-check every point against the JSONs.

## Wiring
After both SVG pairs exist in `figures-src/`:
1. Replace each `.fig-stub` div in `lab/hrm.html` with the standard figure
   block (ids `fig1`, `fig2`), keeping the existing `.nb-figcap` divs
   exactly where and as they are.
2. Add to `tools/splice-figs.py` MAPS:
   `"lab/hrm.html": {"fig1": "fig_hrm_depth_geometry", "fig2": "fig_hrm_sweep"}`
   (then name your files to match).
3. `python3 tools/splice-figs.py lab/hrm.html` and confirm 4 splices.

## Receipts (mandatory)
1. Per-figure: the full provenance list — every plotted value → its JSON
   path (the fig2 table covers fig2; for fig1 state series lengths and
   min/max per series and that all points came from the arrays verbatim).
2. `python3 tools/lint-prose.py lab/hrm.html` before/after (no increase);
   `python3 tools/lint-toc.py`; `./tools/prepush-check.sh` at the end.
3. `git diff --stat` for all touched files.
4. Confirm caption text unchanged: `git diff lab/hrm.html | grep -c '^[-+].*nb-figcap'` → 0.
5. Screenshot-free receipt: list every `<text>` string in each SVG so the
   owner can eyeball label sanity from the report.

## Report
Receipts, the two formulas, per-config table, judgment calls (composition,
token choices with protan note), FLAGs (FLAG-0 restated + count shortfall +
anything else).
