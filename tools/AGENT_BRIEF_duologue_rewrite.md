# Duologue rewrite brief (lab/duologue.html) — read fully before touching anything

## Mission
Rewrite the prose of `lab/duologue.html` so a reader feels what the owner felt reading
the run logs: genuine fun. The project put pairs of local models in conversation through
a tool-call harness and watched them fail in inventive, occasionally magnificent ways —
"endless madness each agent got up to." The errors were instructive to resolve AND the
results were fun to read. The current page carries the findings but under-sells the
experience. Your job: keep every finding and number, and let the material's absurdity
through. This is a portfolio page for a hiring audience — the humor must come from the
DOCUMENTED material (what the models actually did), never from narrator mugging,
exclamation marks, or manufactured whimsy. Dry, specific, deadpan beats wacky.

## Read fully, in this order, before any edit
1. `/Users/anya/.claude/projects/-Users-anya-Projects/memory/reference_writing_voice.md`
   — the owner's voice spec (fact-mode vs values-mode). Everything you write must pass it.
2. `/Users/anya/Downloads/duologue_failure_samples.md` — 21 curated, SOURCED failure-mode
   sections + file index + "Still needed" gaps, distilled from the real run logs. This is
   your ONLY source of new material. Note its sourcing conventions at the top.
3. `lab/duologue.html` — the current page, in full.
4. Skim `lab/nanbeige.html` hero/section grammar only if you need a DS reference; the
   duologue page is already on the design system — do not restructure its scaffolding.

## Hard rules
- NEW MATERIAL COMES ONLY FROM THE SAMPLES FILE. Every anecdote, behavior, and quote must
  trace to a numbered section of `duologue_failure_samples.md`. Log excerpts you quote on
  the page must be VERBATIM from that file (ellipses allowed, marked). No invented
  dialogue, no composite anecdotes, no "presumably it was thinking…" interiority.
  If you want a beat the samples don't support: FLAG it in your report, don't write it.
- EVERY EXISTING FINDING, NUMBER, CONFIG NAME, MODEL NAME, AND LINK SURVIVES. You may
  reorganize prose within sections and rewrite sentences freely, but the technical record
  (what failed, why, what fixed it, the ▲/✕ lexicon results, the no-convergence framing)
  is inviolable. The dek's epistemic honesty ("no convergence claim") must survive intact.
- Do NOT touch: `<head>` contents, the `<!-- @dsCard ... -->` comment, SITE-BAR/FOOTER
  managed blocks, any inline `<svg>`, any `<script>`, `tokens/`, `components/`.
- Keep all existing section `id`s. You may ADD a section if the material demands it —
  then add its TOC entry and re-run lint-toc. Do not rename or remove anchors.
- Figures and their captions: captions may be rewritten ONLY if the underlying claim is
  unchanged; when in doubt, leave the caption and FLAG.
- Do NOT commit, branch-switch, or push. You are on branch `wave4-duologue`; leave
  changes in the working tree.

## Two audit findings to address while you're in there
1. Zoo table (~line 341–342): Qwen3.5-9B-RYS's fix is marked "open — candidate: scan
   reasoning_content" while the row above lists that same scan as the SOLVED fix for the
   `<think>`-hiding failure. Samples §3 and §18 cover this model — §18 documents a
   grammar-level JSON bug on multi-byte symbol strings, which looks like a DIFFERENT root
   cause. If the samples give you clear evidence the failures are distinct (or the same),
   fix the table clause with that evidence and cite the section in your report. If the
   evidence is ambiguous, leave the table and FLAG.
2. Caveat (~line 590) says "a verbatim turn-by-turn excerpt would strengthen it." If your
   rewrite lands verbatim excerpts (it should), update that caveat honestly — don't leave
   a stale self-criticism the page no longer deserves, don't over-claim either.

## Quality bar (deslop discipline applies to YOUR OWN output)
- lint-prose: `python3 tools/lint-prose.py lab/duologue.html` before and after. The page
  is currently on the ALLOWED allowlist; your target is 0 violations so the orchestrator
  can remove it from the allowlist. Do not add: em-dash chains, "isn't just X, it's Y",
  triadic flourishes, symmetrical paragraph endings.
- Density: every sentence earns its bytes. A verbatim log excerpt beats three sentences
  describing it.

## Receipts (mandatory, in this order)
1. BEFORE editing — number-multiset snapshot:
   `python3 -c "import re,sys;t=open(sys.argv[1]).read();t=re.sub(r'<style.*?</style>|<script.*?</script>','',t,flags=re.S);t=re.sub(r'<[^>]+>',' ',t);print('\n'.join(sorted(re.findall(r'\d+(?:\.\d+)?',t))))" lab/duologue.html > /tmp/nums_before_duologue.txt`
   plus the lint-prose summary line.
2. AFTER — same snapshot to `/tmp/nums_after_duologue.txt`, then diff. Unlike a pure
   migration, ADDED numbers are expected (quoted log material) — every + line must cite
   its samples-file section; every − line must be individually justified (a number may
   only disappear if its sentence was redundant restatement and the number survives
   elsewhere on the page — otherwise it goes back).
3. QUOTE-PROVENANCE TABLE: every verbatim excerpt now on the page → samples-file section
   number. This is the fabrication check; it must be complete.
4. `python3 tools/lint-prose.py lab/duologue.html` (target 0) · `python3 tools/lint-toc.py`
   · `./tools/prepush-check.sh` — paste outputs.
5. `git diff --stat` — paste.

## Report format (final message)
Receipts above, raw. Then: one-paragraph summary of what changed structurally; the
Qwen3.5 table resolution with evidence citation (or FLAG); list of judgment calls, one
line each; FLAGs (beats you wanted but couldn't source, caption doubts, dsCard drift —
if your rewrite changes the page's framing enough that the index card's description no
longer matches, say so, the owner syncs cards separately).
