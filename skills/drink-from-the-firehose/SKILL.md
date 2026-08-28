---
name: drink-from-the-firehose
description: Guided onboarding walkthrough of a project — role-aware, quiz-driven, every claim carries its source.
disable-model-invocation: true
---

The firehose is the **scope**: every chapter below gets covered, for every newcomer. The
**pressure** is adaptive: someone who stumbles drinks a trickle (one concept, small
questions); someone who aces the checks drinks the full jet (density, harder questions).
Coverage is constant; pressure varies.

## 1 — Scan the manifest (before the first question)

Read the project's manifest, nothing deeper:

- Entry docs: README, AGENTS.md / CLAUDE.md — whichever exist.
- Directory tree: top two levels of each significant root.
- Build files: pom.xml, build.gradle, package.json, pyproject.toml, Cargo.toml, Makefile…
- Docs index: list the docs tree — ADRs, PRD, use cases, runbooks, guides.
- Entry points: main classes / CLI entry / src layout at a glance.

From the scan, build the chapter plan: the canonical spine below, plus the
project-specific chapters the scan surfaced (a distinctive subsystem, a plugin system,
a domain model worth its own stop). Design these deliberately — they are where the
walkthrough earns its keep on this project.

**Done when:** every chapter in the plan names at least one real file or doc path found
in the scan; a chapter with no source is merged or dropped, saying so.

## 2 — Kickoff (one exchange, in the user's language)

Speak the language the user invoked you in. One kickoff exchange, containing:

1. **Role** — menu: developer / designer / PM / user, plus free text. Any other answer
   (QA, tech writer, data scientist…) maps onto "what this person needs from this project".
2. **Calibration** — 2-3 closed questions on concrete exposure: the project's domain,
   its stack, this specific codebase. Ask about what they have touched, not whether they
   rate themselves expert.
3. **Artifact policy** — state it explicitly: heavy material leaves the chat as
   self-contained HTML/JS pages; the user may ask for *richer* artifacts at any time,
   or turn artifacts off entirely.
4. **The chapter plan**, announced.

**Done when:** role and calibration are recorded, the artifact policy was declared,
the plan was shown.

## 3 — Chapter loop

Canonical spine: ① what this project is and why it exists, ② the map (modules,
repositories), ③ where decisions and docs live, ④ build and test — what "green" means,
⑤ the load-bearing architecture, ⑥ how work happens (workflow, conventions), ⑦
role-specific deep dive, ⑧ close. The scan's project chapters slot in where they belong.

Announce position at every boundary ("Chapter 3/9: …").

**Teach.** Every factual claim carries its **receipt**: a file:line or a doc path. A
claim that lacks one gets verified in the code first, or is labelled aloud as inference
("my reading — not in the docs"). Synthesis connecting files is welcome, and labelled.
Sources follow the role: developer → code, tests, SPIs; PM → PRD, use cases, milestones;
designer → UX/UI surfaces; user → quickstart, usage.

Emit an HTML/JS artifact (published page, self-contained) only when the chapter needs
what chat cannot give: **navigation or scale** (module maps, dependency trees,
drill-downs), **visualization** (architectures, sequence diagrams, decision timelines),
or **interactivity** (explorers, quiz boards). Linear prose stays in chat. Announce it
before emitting ("this deserves a map — opening it as a page"). One artifact per chapter
is the norm; two is the ceiling.

**Quiz — the modern elenchus.** After each teaching chunk, check understanding with a
closed question (menu). On a wrong or half answer, ask: "want the answer now, or want to
reason it out?" The reasoning path asks a smaller question that leads toward the insight
— still in quiz format — shrinking until they land. Answers set the pressure: easy
misses → lower density, smaller steps; clean sweeps → raise it.

**Done when:** the user answered the chapter's checks correctly (or asked to move on),
and every claim made still carries its receipt.

## 4 — Close (when the user says so)

The walkthrough ends when the user declares it — no exam. Close with one final
self-contained artifact: the project map (modules, key paths), the receipts (links to
every doc and file visited), and pointers for what to explore alone next.

State lives in the conversation only — the "Chapter N/M" line is the progress record;
on a resumed session, re-orient from the last announced chapter. Write nothing to disk
except artifacts.
