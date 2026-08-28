---
name: slides
description: Build a presentation as a pair of artifacts — a slides markdown (source of truth with speaker notes) plus a fully-local reveal.js deck (vendored assets, no CDN, custom token-based theme). Use this whenever the user asks for slides, a deck, a presentation, a talk, a keynote, "una presentazione", or wants to present/explain something to an audience — even if they only say "I need to present X to the team" or "prepare a talk on Y" without the word "slides".
---

# Slides: markdown source + local reveal.js deck

Every presentation is TWO files that tell the same story:

1. **`<topic>.md`** — the source of truth. Reviewable, diffable, greppable; carries the speaker
   notes; survives tooling changes. This is what gets reviewed and committed.
2. **`<topic>-deck/index.html`** — the projectable reveal.js build. Fully local: vendored
   reveal.js, no CDN, no network at present-time. Opens from `file://`.

The markdown leads; the deck follows. When content changes, change the markdown first, then
mirror it into the deck.

## Workflow

1. **Pin the brief** before writing anything: topic, audience (and what they already know),
   duration, language, where the files go. Budget ≈ 40–60 seconds per slide; prepare an
   **appendix** of backup slides for Q&A rather than cramming the main track.
2. **Outline** the slide list (one line each) and get it agreed if the user is available.
3. **Write the markdown** (format below).
4. **Build the deck** from the bundled templates (recipe below).
5. **Verify** with the checklist at the end.

## The markdown format

- An intro block before slide 1: what this deck is, who it is for, where the projectable build
  lives and how to drive it ("arrows navigate, `S` opens the speaker view, `Esc` overview").
- One section per slide: `## Slide N — Title`, then the slide's content (real markdown: lists,
  tables, fenced code), then the notes:

  ```markdown
  > **Speaker notes:** what to say, what to point at, the one sentence to land, timing hints.
  ```

- Appendix slides after the main track under a `# Appendix` heading (`## A1 — …`, `## A2 — …`).
- Cross-references between slides use numbers in the markdown ("see slide 17") — renumber them
  when inserting slides.

## Building the deck

```
<topic>-deck/
├── index.html          ← from assets/index-template.html
├── theme.css           ← from assets/theme-template.css, adapted
└── reveal/             ← vendored by scripts/fetch-reveal.sh
    ├── reveal.js  reveal.css  reset.css  notes.js  LICENSE
```

1. Vendor reveal.js: `bash <skill>/scripts/fetch-reveal.sh <topic>-deck/reveal` (pinned
   version; keeps the MIT LICENSE alongside — required when committing vendored code). If the
   network is blocked, say so and ask the user to provide a reveal.js dist; never link a CDN.
2. Copy `theme-template.css` → `theme.css` and **adapt it to the subject** (see below).
3. Build `index.html` from `index-template.html`: one `<section>` per markdown slide, the
   appendix as ONE `<section>` containing nested `<section>`s (reveal renders it as a vertical
   stack — down-arrow territory, visually separate from the main track).
4. Mirror each markdown speaker-notes block into `<aside class="notes">` — that is what the
   `S` speaker view shows.
5. In the DECK, make cross-references descriptive ("the memory slide"), not numeric — deck
   slides show no numbers and numeric refs drift when slides are inserted. Numbers stay in the
   markdown only.

## The theme: adapt, don't copy

`theme-template.css` is a starting point, not a livery. It gives you the mechanics — design
tokens on `:root`, light + dark via `prefers-color-scheme`, an eyebrow/heading/code/table kit,
hand-built diagram boxes — with a placeholder palette. Before using it:

- **Derive the semantic colors from the content.** The template ships three category families
  (`--cat-a/b/c` with `.ca/.cb/.cc` classes and matching `.pill` chips). Use them only if the
  subject genuinely has 2–3 recurring categories worth color-coding on every slide (e.g. event
  families, actor types, severity tiers) — then rename them mentally to what they mean and keep
  the coding consistent across ALL slides, including code excerpts. If the subject has no such
  categories, drop the families and keep one accent.
- Pick display/body/mono faces that fit the subject (the template defaults to a serif display +
  system body + mono for data — a "technical report" voice; a product launch may want otherwise).
- Keep both themes legible: tokens only on `:root` + the dark media query, components always
  styled through tokens.

## Content rules

- **Real material only.** If slides show code, data, JSON, measurements — they come from real,
  regenerable sources (a run, a capture, a repo file), and the markdown intro says how to
  regenerate them. Invented examples erode the audience's trust the moment someone checks.
- **Presenter-driven density** by default: sparse slides, the notes carry the prose. Switch to
  self-contained density only if the user says the deck must work without a presenter.
- **One narrative when possible**: a single concrete story that grows beats a gallery of
  disconnected examples — each concept arrives when the story needs it.
- An "at a glance" overview slide before a long walkthrough (the whole thing in one screen, one
  line per item) orients the audience before the zoom-in.
- No AI-tool attribution or vendor links in the deliverables.

## Checklist before handing over

- `grep -c "^## Slide" <topic>.md` matches the deck's main `<section>` count (appendix counted
  separately).
- Every deck slide has its `<aside class="notes">`; every markdown slide has its notes block.
- No external URLs in `index.html`/`theme.css` (CDN fonts included) — the deck must open
  offline from `file://`.
- Wide content (tables, code) sits in scrollable containers; check the longest code block at
  1280×720.
- Tell the user how to drive it: open `index.html`; arrows navigate, `↓` enters the appendix
  stack, `S` speaker view with notes, `Esc` overview.
