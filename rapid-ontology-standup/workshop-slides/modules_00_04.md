# Workshop Slides — Modules 00 through 04

**Location:** `docs/workshop-slides/`

---

## Module 00 — Opening

**File:** `docs/workshop-slides/00_opening.md`

### Presenter Notes
- **Duration:** 10 minutes
- **Key takeaway:** "By 5pm you'll have certified Metric Views, a curated Genie Agent, and a version-controlled repo you own."
- **Common question:** "Do we need to prepare anything?" → Prerequisites are on the last slide.

---

### Slide 1: Welcome

**Rapid Ontology Standup**
*One day to trusted, consistent answers from your data*

Today we're going to build your Genie Ontology together — the governed business context that powers accurate answers across dashboards, Genie, notebooks, and BI tools.

---

### Slide 2: What You'll Walk Away With

By the end of today:

- ✅ **Certified Metric Views** — your KPIs defined once, reusable everywhere
- ✅ **A curated Genie Agent** — ask questions in natural language, get trusted answers
- ✅ **Domain research + data model analysis** — reusable documentation of your data
- ✅ **A version-controlled repo** — everything in a DAB monorepo you own and can extend
- ✅ **The understanding to do it again** — you'll see every step, every decision

---

### Slide 3: How the Day Works

| Morning | Afternoon |
|---|---|
| Understand your data | Build and validate |
| Domain research → Data model analysis → Metric View generation | Deploy → Review → Certify → Create Agent → Curate → Benchmark |

**The pattern:** I teach a concept (slides) → we build it together (live in Genie Code) → repeat.

You're involved at every step. This isn't a black box.

---

### Slide 4: The Math Class Principle

*"First we do it the interactive way so you understand the motivation for what comes next."*

Today is the "by hand" phase. Once you understand how the semantic layer works and why each piece exists, the advanced topics — automation, testing, governance — will make intuitive sense.

---

### Transition to Setup
> "Let's get started. I'm going to clone the repo, create a feature branch, and open the bundle editor. You'll see everything I do on screen."

---
---

## Module 01 — UC Semantics Primer

**File:** `docs/workshop-slides/01_uc_semantics_primer.md`

### Presenter Notes
- **Duration:** 5 minutes
- **Key takeaway:** "UC Business Semantics is four things: Metric Views, Domains, Pages, and Certification. Together they form the human-modeled layer of the Genie Ontology."
- **Common question:** "How is this different from our Power BI semantic model?" → It's open (not locked to one tool), governed by UC, and consumed by Genie, dashboards, notebooks, and external BI tools simultaneously.

---

### Slide 1: The Problem with No Semantic Layer

Three analysts. Same question. Three different answers.

Why? Because the KPI definition lives in a dashboard, a spreadsheet, and someone's head — not in the data platform.

---

### Slide 2: UC Business Semantics — Four Components

![UC Semantics Feature Overview](https://www.databricks.com/sites/default/files/2026-08/feature-01-image-new.png)

| Component | What it does |
|---|---|
| **Metric Views** | Define KPIs once — measures, dimensions, joins, formats. Query engine handles the rest. |
| **Domains** | Organize assets by business purpose — not by catalog hierarchy. |
| **Pages** | Authoritative definitions of business terms. Genie cites them. |
| **Certification** | Trust signals — steers Genie toward assets your organization vouches for. |

**All GA as of August 2026.**

---

### Slide 3: Define Once, Use Everywhere

```
                    Metric View
                   (defined once)
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   Dashboards      Genie Agent      Notebooks
        │               │               │
        ▼               ▼               ▼
   External BI      SQL Queries      Alerts
```

One definition. Every consumer gets the same number. No more reconciliation fights.

---

### Transition to Demo
> "Let me show you what this looks like in practice. Here's the Discover page in your workspace — this is where Domains and Pages surface. And here's a certified Metric View in Catalog Explorer..."

---
---

## Module 02 — Genie Ontology

**File:** `docs/workshop-slides/02_genie_ontology.md`

### Presenter Notes
- **Duration:** 10 minutes
- **Key takeaway:** "The Genie Ontology combines what you define (UC Semantics) with what Genie learns from your platform. The more you curate, the better the answers."
- **Common question:** "Does Genie train on our data?" → No. It extracts, indexes, and ranks context snippets. It does not fine-tune the foundation model.

---

### Slide 1: Two Levels of Context

```
┌─────────────────────────────────────┐
│         Genie Ontology              │
│                                     │
│  ┌─────────────┐ ┌───────────────┐  │
│  │  Modeled    │ │   Inferred    │  │
│  │  Context    │ │   Context     │  │
│  │             │ │               │  │
│  │ Metric Views│ │ Dashboards    │  │
│  │ Domains     │ │ SQL queries   │  │
│  │ Pages       │ │ Agent configs │  │
│  │ Certified   │ │ Usage signals │  │
│  └─────────────┘ └───────────────┘  │
│                                     │
│  Modeled wins when both exist.      │
└─────────────────────────────────────┘
```

**What you define** takes precedence over **what Genie infers**. That's why building the semantic layer matters — it's the authoritative source.

---

### Slide 2: How Genie Finds the Right Answer

1. **Parse** your question — intent, entities, metrics, filters
2. **Search** the Ontology for relevant context
3. **Filter** by your UC permissions — you only see what you're authorized to see
4. **Rank** by authority (OntoRank) — not just similarity, but trustworthiness
5. **Generate** SQL and execute it
6. **Cite** the sources — you can verify where the answer came from

---

### Slide 3: OntoRank — Why Certification Matters

OntoRank doesn't just ask "what text looks similar?" It asks "which definition is most **authoritative**?"

Signals: provenance (governed MV > ad-hoc query), expert usage, certification, freshness, lineage.

**Practical implication:** When we certify your Metric Views at the end of today, Genie will prioritize them over any ad-hoc query or uncertified asset. That's the trust unlock.

---

### Transition to Demo
> "Let me show you Genie One in action. I'll ask a question and we'll look at the citations — you'll see exactly which sources Genie used to generate the answer..."

---
---

## Module 03 — Metric View Concepts

**File:** `docs/workshop-slides/03_metric_view_concepts.md`

### Presenter Notes
- **Duration:** 10 minutes
- **Key takeaway:** "A Metric View separates what to calculate from how to slice it. You define the metric once; the query engine generates the correct computation for any grouping."
- **Common question:** "Why not just use a regular view?" → A regular view locks in the aggregation and grouping at creation time. A Metric View lets users group by any available field at query time.

---

### Slide 1: Standard View vs. Metric View

| Standard View | Metric View |
|---|---|
| Aggregation locked at creation time | Aggregation computed at query time |
| One grouping per view | Any grouping, any filter |
| Need a new view for each slice | One definition serves all consumers |
| No semantic metadata | Display names, synonyms, formats built in |

---

### Slide 2: Anatomy of a Metric View

```yaml
version: 1.1
source: catalog.schema.orders        # ONE fact source

fields:                               # How to slice it
  - name: region
    display_name: "Region"
    synonyms: [territory, area]

measures:                             # What to calculate
  - name: total_revenue
    expr: SUM(order_total)
    display_name: "Total Revenue"
    format: { type: currency, currency_code: USD }
    synonyms: [revenue, sales]
```

**Fields** = dimensions (how to group/filter). **Measures** = aggregations (what to calculate).

---

### Slide 3: Agent Metadata — The Secret Sauce

Every field and measure gets three things:

- **`display_name`** — human-readable label ("Total Revenue" not "tot_rev")
- **`synonyms`** — alternative names Genie recognizes ("revenue", "sales", "total sales")
- **`format`** — how to display it (currency, percentage, date format)

**This is mandatory in our process, not optional.** It's what makes Genie accurate.

---

### Slide 4: Composability — Build on What You've Defined

```yaml
measures:
  - name: total_revenue
    expr: SUM(order_total)
  - name: order_count
    expr: COUNT(1)
  - name: avg_order_value                    # References the two above
    expr: MEASURE(total_revenue) / MEASURE(order_count)
```

If `total_revenue` changes (e.g., to exclude tax), `avg_order_value` automatically uses the updated definition. No copy-paste. No drift.

---

### Transition to Demo
> "Let me show you what a Metric View looks like in the Catalog Explorer YAML editor. Then we'll switch to the bundle editor and start generating these from your actual data..."

---
---

## Module 04 — Genie Code Workflow

**File:** `docs/workshop-slides/04_genie_code_workflow.md`

### Presenter Notes
- **Duration:** 5 minutes
- **Key takeaway:** "Genie Code in the bundle editor is our workspace for the day. Everything we create is version-controlled from the moment it's written."
- **Common question:** "Do we need any special skills or MCP connections?" → No. Genie Code has built-in skills. Web Search is Beta but available. No additional setup needed.

---

### Slide 1: Our Workspace for the Day

Everything happens in the **Genie Code bundle editor**:

- Version-controlled from the first keystroke
- Native awareness of the bundle structure, resources, and file paths
- `@` context to reference schemas, tables, and files in the repo
- Web Search (Beta) for industry research
- Agent mode for multi-step analysis

We're working on a **feature branch** — nothing touches `main` until we're ready.

---

### Slide 2: The @ Context Superpower

When I type `@` in Genie Code, I can reference:

- **Schemas** — "analyze everything in this schema"
- **Tables** — "look at this specific table"
- **Files in the repo** — "use the domain research we just wrote as context for the next step"

This is how each phase builds on the previous one — the output of Phase 1 becomes the input context for Phase 3.

---

### Slide 3: What We're About to Do

```
Phase 1: Domain Research          → docs/semantics/01_industry_domain_research.md
Phase 2: Data Model Analysis      → docs/semantics/02_data_model_analysis.md
Phase 3: Metric View YAML         → fixtures/metric_views/*.metric_view.yml
Phase 4: Deploy + Review + Certify → Unity Catalog (dev/test)
```

Each phase produces a concrete artifact. Each artifact becomes context for the next phase.

**Let's start with Phase 1 — researching your industry.**

---

### Transition to Live Demo
> "I'm going to open a new Genie Code session in the bundle editor and start with Web Search. We'll research the standard KPIs for your industry, then search for how your organization talks about its own domain..."
