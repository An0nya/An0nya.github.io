# Density-pass agent brief (read fully before touching the page)

You are editing ONE page of a published research-notes site (an0nya.github.io,
"the vivisection lab"). The owner (Anya) wrote/edited some of this prose; the
rest is lightly-edited AI drafts. Your job: bring the page under the editorial
density rules below WITHOUT changing any factual claim, number, or finding.

## Hard rules
- Edit ONLY the page file you were assigned. Nothing else.
- NEVER invent, alter, round, or "fix" a number, metric name, config name, or
  finding. If a sentence is unclear without data you don't have, FLAG it in
  your report instead of guessing.
- Do NOT commit. Leave changes in the working tree.
- Do NOT touch: `<style>`, `<script>`, `<svg>`, `<table>`, `<figure>`,
  `<nav>`, `<footer>`, headings, `.dek`, `.nb-kicker`, `.nb-record`,
  `.nb-marginalia`, `.page-toc`, `.fig-note`, `.wbhead` spans. Those regions
  are design grammar — their dashes/styling are intentional.

## The density rules (running body prose: <p> and <li> only)
1. **Em-dash budget: max ONE per paragraph. ZERO in lead units** (the page's
   first prose paragraph, and the first paragraph after each `<h2>`).
   Rewrite via comma, parentheses, colon, sentence break, or bullets.
   RESTRUCTURE the sentence — don't just swap the dash for a semicolon and
   keep the same cornered syntax. The tell is dash-shaped sentence structure,
   not the glyph.
2. **Pop budget: max ONE styled pop per paragraph** (`<em>/<i>/<b>/<strong>`,
   `span.hl-*`). Chips (`span.olabel`) are exempt. Choose the ONE pop so a
   skimming reader takes away the paragraph's actual point — the finding, not
   an adjective. Demote the rest to plain text (subtractive: delete tags,
   keep words, unless the word itself is filler — then cut it).
3. **qx/qv budget** — quantitative-result highlighting:
   - `.qx` wraps a whole quantitative statement (washed background);
     `.qv` wraps ONLY the number inside it (mono+bold). A bare standalone
     number can be a lone `.qv`. Symbols/words (α =, Σα, "strict") stay in
     base font INSIDE the qx wash. Pattern:
     `<span class="qx">α = <span class="qv">0.5 → 1.5</span></span>`
   - Budget per paragraph is proportional to how many quantitative results it
     contains: 1 result → may mark 1; 2 → may mark 2; 3–4 → mark at most 2;
     5+ → mark at most 3. Mark the ones a skimmer must take away; demote the
     rest to bare prose numerals (no markup at all).
   - A qx/qv mark counts as the paragraph's quantitative highlight, separate
     from the prose-pop budget, but don't stack a qx AND a bold pop on the
     same clause.
   - `<code>` is for IDENTIFIERS only (config names, filenames, flags) —
     never a highlighting device. If a code-wrapped config carries the
     paragraph's headline number, keep the name in `<code>` and wrap only the
     value in `.qv`.
4. **Leftover mixed bolds** (bold spans mixing words+numbers, flagged SKIP by
   tools/convert-quant.py): make the call yourself — convert to qx/qv if it's
   a quantitative result, demote to plain if it's emphasis inflation, keep as
   the paragraph's one pop only if it's genuinely the takeaway. Flag only the
   genuinely ambiguous ones.

## Deslop (do this in the same pass, subtractively)
While inside a paragraph anyway, strip AI-tell phrasing. Delete, don't
replace: hedging doublets ("both X and Y" where one suffices), throat-clears
("Notably," "Crucially," "It's worth noting"), triadic flourishes ("not X,
not Y, but Z" — unless the rhythm is genuinely load-bearing), empty
intensifiers ("genuinely", "actually", "fundamentally") unless they carry an
epistemic distinction. Keep the owner's voice: direct, dry, technical, first
person singular, lowercase-comfortable. When a sentence is fine, LEAVE IT.
Under-editing beats over-editing; the owner reviews every diff.

## Verification receipts (mandatory, in this order)
1. BEFORE editing: `python3 tools/lint-prose.py <your-page>` — paste the
   summary line into your report.
2. Edit.
3. AFTER: run the same command — paste the FULL output (violations + summary).
   Target: dash and lead violations → 0; pop violations → 0 or explained;
   qx violations → 0 or flagged as load-bearing.
4. `git diff --stat <your-page>` — paste output.
5. Confirm untouched regions: `git diff <your-page> | grep -c '^[-+].*<svg\|^[-+].*<style\|^[-+].*<script'` should be 0 — paste it.

## Report format (final message)
- Receipts (all four, raw).
- Bullet list of judgment calls you made (pop choices, qx demotions, SKIP-bold
  dispositions) — one line each.
- FLAGGED items needing the owner: quote the sentence, say why.
