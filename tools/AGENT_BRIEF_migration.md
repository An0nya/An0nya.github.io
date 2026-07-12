# Design-migration agent brief (read fully before touching any page)

You are migrating page(s) of a published research-notes site (an0nya.github.io,
"the vivisection lab") from an older one-off design to the sitewide design
language. This is a STRUCTURE/STYLE migration — the content (every claim,
number, link, and the owner's voice) must survive intact.

## Read these FIRST, fully
- `lab/nanbeige.html` — the canonical lab-page template (head boilerplate,
  local `<style>` baseline, hero pattern, section grammar).
- `lab/self-improving-memory.html` — second reference; same standard.
- `components/components.css` + `tokens/` — what the design system provides.
  DS components you'll need: `.nb-kicker`, `.nb-record` (`__title`, `__grid`,
  `__field`, `__k`, `__v`), `.nb-stats`/`.nb-stat` (`__num`, `__label`),
  `.nb-marginalia` (`__label`, `__body`), `.nb-table`, `.nb-plate`, `.walkback`.

## The hero spec (what "hero to spec" means)
Immediately inside `<main>`:
1. `<div class="nb-kicker" style="margin-bottom:var(--sp-5)">Observation
   notebook · Anya · 2026 · <2–4 word branch nugget></div>` — no `<em>` tail
   after the nugget. ("Observation" may be "Methods" where the page is a
   methods page; these targets are all Observation.)
2. `<header class="nb-record">` with `nb-record__title` (the page's title
   sentence — old `<h1>` text verbatim, styling tags dropped) and
   `nb-record__grid` with 2–3 `nb-record__field` rows, keys typically
   Specimen / Status / Source. Fold the old hero's scattered facts (topbar
   lines, spec figures, run counts) into these fields — RELOCATE, never delete.
3. `<p class="dek">` — existing dek text verbatim.
4. Old `.stats-strip`/`.stat` blocks → DS `.nb-stats`/`.nb-stat` with
   `nb-stat__num`/`nb-stat__label`; numbers and label text verbatim.
No `<h1>`, no `.topbar`, no old `.hero`/`.kicker` scaffolding survives.
Draft banners (`.draft-banner`) stay where they are.

## Hard rules
- Edit ONLY the page file(s) you were assigned. Nothing else — not
  components/, not tokens/, not tools/.
- NEVER invent, alter, round, or "fix" a number, metric name, config name,
  claim, or finding. Prose text is copied, not rewritten. This is NOT a
  density/deslop pass — leave the prose exactly as found, even where it
  violates density rules.
- Do NOT touch: the `<!-- @dsCard ... -->` comment, `<head>` meta/title/
  canonical/description/favicon, the SITE-BAR:START..END and FOOTER:START..END
  managed blocks, the `.page-toc` aside (update nothing there; do not rename
  section `id`s, so its anchors keep working), any inline `<svg>` figure,
  any `<script>` block.
- `hl-pos`/`hl-neg`/`hl-acc` spans: keep the spans, redefine the class(es) in
  the local `<style>` to weight-only — `font-weight: 600;` — no color. (The
  colored versions are being retired sitewide; reference: nanbeige's
  `.hl-acc`.)
- Local `<style>`: rebuild it starting from nanbeige's local block as the
  baseline, then append ONLY the page-specific one-offs this page still
  needs, converted to tokens (`var(--sp-*)`, `var(--fs-*)`, `var(--measure)`,
  colors via existing vars — no raw hex, no raw px where a token exists;
  bottom page padding is `var(--sp-9)`, not 120px).
- Do NOT commit, branch, or push. Leave changes in the working tree.
- If an instruction can't be verified against the actual file contents,
  STOP on that item and FLAG it in your report instead of improvising.

## Verification receipts (mandatory, in this order)
1. BEFORE editing — number-multiset snapshot:
   `python3 -c "import re,sys;t=open(sys.argv[1]).read();t=re.sub(r'<style.*?</style>|<script.*?</script>','',t,flags=re.S);t=re.sub(r'<[^>]+>',' ',t);print('\n'.join(sorted(re.findall(r'\d+(?:\.\d+)?',t))))" lab/PAGE.html > /tmp/nums_before_PAGE.txt`
   Also: `python3 tools/lint-prose.py lab/PAGE.html` — paste the summary line.
2. Edit.
3. AFTER — same snapshot to `/tmp/nums_after_PAGE.txt`, then
   `diff /tmp/nums_before_PAGE.txt /tmp/nums_after_PAGE.txt`.
   Target: EMPTY diff. Every non-empty diff line must be individually
   explained in your report (e.g. "+2026: new spec kicker date"). An
   unexplained missing number = you deleted content; put it back.
4. `python3 tools/lint-prose.py lab/PAGE.html` — violation count must not
   INCREASE vs step 1. `python3 tools/lint-toc.py` — must pass.
5. `git diff --stat lab/PAGE.html` — paste output.
6. `git diff lab/PAGE.html | grep -c '^[-+].*<svg'` → must be 0 — paste it.

## Report format (final message)
- Receipts (raw), incl. the full nums diff + per-line explanations.
- The kicker nugget you chose and the nb-record field contents (quoted).
- Bullet list of class-mapping / relocation judgment calls, one line each.
- FLAGGED items needing the owner: quote, say why.

---

## Per-page task blocks

### lab/gemma31b.html — FULL migration (the big one)
Current state: `<html lang="en" class="lab">`, a 567-line local `<style>`
that is its own complete design system (body reset, 19px serif, 76px h1,
warm-token aliases `--bg-2/--ink-2/--rule-2/--shadow`, `.kicker`, `.rule`,
`.mono/.small/.tiny/.muted`, `.hl-pos`(sage)/`.hl-neg`(wine), 120px bottom
padding). Job:
- Drop `class="lab"` from `<html>` (body already has `cat-intervention`).
- Inventory every class actually used in the body (grep). Map each: DS
  equivalent where one exists (`.kicker`→`.nb-kicker`, stats→`.nb-stats`,
  tables→`.nb-table`, marginalia→`.nb-marginalia`, pulls→`.nb-pull`, ...);
  otherwise a token-converted one-off in the new local `<style>`; delete
  rules for classes no longer used. The old body-reset/typography rules all
  go — the page adopts sitewide type via `/styles.css`.
- Hero → spec (see above). Propose a 2–4 word kicker nugget from the page's
  own framing (it's the "model that wouldn't break" negative-result sweep) —
  FLAG the nugget for owner sign-off.
- `hl-pos`/`hl-neg` → weight-only 600 (keep spans).
- Figures: inline SVGs untouched; their wrappers may be re-classed to
  `.nb-plate`/`.figure` per the nanbeige pattern.
- Section `id`s unchanged; `.page-toc` untouched.

### lab/hrm.html — hero migration + hl flatten
Colors/tokens already migrated; only the hero is old style.
- Replace the `.hero` section (topbar with dot/specimen line/right line, the
  old freeform `.nb-kicker` text line, `<h1>HRM:<br><em>a false dawn</em>.</h1>`,
  `.stats-strip`) with the spec hero. Title text: "HRM: a false dawn."
  (verbatim words, tags dropped). Topbar facts (Specimen · HRM-Text-1B ·
  recurrent · MLX bf16; 35 configs · 5 waves · then the verification that
  killed it) → nb-record grid fields. Old kicker sentence "A recurrent
  reasoner, and a result that didn't survive" → fold into the Status field
  or keep as grid content — do not delete it. New spec kicker nugget: 2–4
  words from the page's framing; FLAG for sign-off.
- `.draft-banner` above the hero stays exactly where it is.
- Stats-strip values (2×3, 128, 35, 5/6, 0/3 + labels) → `.nb-stats` verbatim.
- The `.nb-marginalia` "The patient" block stays (already DS), position after
  the dek/stats per the reference pages' flow.
- `.hl-neg` local def → weight-only 600 (keep spans). The §6 "can make it
  worse" highlight STAYS IN PROSE (owner: no listify), just color→weight.
- Remove now-dead local CSS (`.hero`, `.topbar`, `.stats-strip`, h1 rules...).

### lab/gemma12b.html — hero migration
Already has kicker + nb-record title + dek; missing the grid, and carries an
old stats-strip + old `.marginalia/.mlabel/.mbody` classes.
- Kicker: trim to `Observation notebook · Anya · 2026 · the vivarium, first
  specimen` — the `<em>` model-spec tail (`Gemma-4-12B-mxfp4 · base · 48
  layers · day-zero scan`) MOVES into the new `nb-record__grid` Specimen
  field (verbatim figures). Add Status/Source fields from facts already on
  the page (e.g. day-zero scan status, probe-set count) — relocate only,
  invent nothing; if you can't fill a field from on-page facts, use fewer
  fields and FLAG it.
- `.stats-strip` → `.nb-stats` (values verbatim).
- Hero `.marginalia/.mlabel/.mbody` → `.nb-marginalia`/`__label`/`__body`;
  remove the dead local CSS for the old classes if nothing else uses them.
- Everything below the hero: untouched.
