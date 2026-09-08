# Workshop Slides — Rapid Ontology Standup

## Module Index and Presenter Guide

**Location:** `docs/workshop-slides/`
**Date:** 2026-09-01
**Duration:** Full day (9:00–5:00)
**Format:** Modular slide sets — one file per phase. Each module teaches a concept, then transitions to a live Genie Code demo.

---

### How to Use These Slides

Each module is a self-contained markdown file with:
- **Presenter notes** at the top (duration, prerequisites, key takeaway, common questions)
- **Slides** as H3 headings (`### Slide N: Title`)
- **Transition to live demo** at the bottom — the bridge from teaching to doing
- **Simplified diagrams** optimized for projection (not the full design-doc versions)
- **Databricks documentation images** referenced by URL where they illustrate a concept better than text

**Delivery pattern:** Teach (slides) → Demo (live Genie Code in the bundle editor) → Repeat.

The practitioner projects the slides, talks through the concept, then switches to the Databricks workspace for the live demo. The customer sees both the "why" and the "how."

---

### Module Schedule

| # | Module | Duration | Teaches | Then demos |
|---|---|---|---|---|
| 00 | Opening | 10 min | Agenda, outcomes, what you'll walk away with | Setup: clone repo, feature branch |
| 01 | UC Semantics Primer | 5 min | What is UC Business Semantics? The four components. | Show Discover page, certified MV in Catalog Explorer |
| 02 | Genie Ontology | 10 min | Two-level context, OntoRank, how Genie uses it | Show Genie One answering a question with citations |
| 03 | Metric View Concepts | 10 min | What is a MV? Measures vs. fields. Agent metadata. | Show a MV definition in the YAML editor |
| 04 | Genie Code Workflow | 5 min | Bundle editor, @ context, Web Search | **L200-A Phase 1:** domain research (live) |
| 05 | Data Model Analysis | 5 min | What to look for: PK/FK, granularity, star schema | **L200-A Phase 2:** data model analysis (live) |
| 06 | YAML Deep Dive | 10 min | Composability, window measures, joins, formats | **L200-A Phase 3:** YAML generation (live) |
| 07 | Genie Agent Concepts | 10 min | What is a Genie Agent? Knowledge store, routing. | **L200-B Phase 1:** create Agent (live) |
| 08 | Curation Patterns | 10 min | Side-by-side eval, feedback loop, what to fix where | **L200-B Phase 2:** curation (live) |
| 09 | What's Next | 10 min | Advanced topics roadmap, how to extend independently | **L200-B Phase 3:** benchmarks + handoff (live) |

**Total slide time:** ~85 minutes across the day (the rest is live Genie Code work)

---

### Timing Map Against the Workshop Schedule

| Time | Activity | Slides | Live Demo |
|---|---|---|---|
| 9:00–9:30 | Opening + setup | Module 00 | Clone repo, create branch |
| 9:30–9:45 | UC Semantics + Ontology | Modules 01 + 02 | Show Discover page, Genie One |
| 9:45–10:00 | MV Concepts + Genie Code Workflow | Modules 03 + 04 | Show YAML editor |
| 10:00–10:30 | — | — | **L200-A Phase 1:** domain research |
| 10:30–10:40 | Data Model Analysis concepts | Module 05 | — |
| 10:40–12:00 | — | — | **L200-A Phase 2:** data model analysis |
| 12:00–12:30 | Lunch | — | — |
| 12:30–12:40 | YAML Deep Dive | Module 06 | — |
| 12:40–2:00 | — | — | **L200-A Phase 3:** YAML generation |
| 2:00–3:00 | — | — | **L200-A Phase 4:** deploy, review, certify |
| 3:00–3:10 | Genie Agent Concepts | Module 07 | — |
| 3:10–3:30 | — | — | **L200-B Phase 1:** create Agent |
| 3:30–3:40 | Curation Patterns | Module 08 | — |
| 3:40–4:30 | — | — | **L200-B Phase 2:** side-by-side curation |
| 4:30–4:40 | What's Next | Module 09 | — |
| 4:40–5:00 | — | — | **L200-B Phase 3:** benchmarks + handoff |

---

### Customization Guide

**For a half-day workshop (L200-A only):**
Use modules 00–06. Skip 07–09. End with a modified "What's Next" that positions L200-B as the follow-up.

**For a 1-hour intro (no live demo):**
Use modules 00–02 only. End with the customer pitch deck's "Let's Schedule It" slide.

**For a train-the-trainer session:**
Use all modules but add the internal field deck's readiness checklist (Slide 8) as a pre-assessment.
