# Workshop Slides — Modules 05 through 09

**Location:** `docs/workshop-slides/`

---

## Module 05 — Data Model Analysis

**File:** `docs/workshop-slides/05_data_model_analysis.md`

### Presenter Notes
- **Duration:** 5 minutes (presented after Phase 1 demo, before Phase 2 demo)
- **Key takeaway:** "Each Metric View has exactly one fact source. Understanding which tables are facts vs. dimensions is the prerequisite for correct MV design."
- **Common question:** "What if our tables aren't in a star schema?" → That's fine. Genie Code will identify the relationships. We may need base views for complex joins.

---

### Slide 1: Why This Step Matters

A Metric View has **one fact source**. If we pick the wrong table, or miss a join, the measures aggregate incorrectly.

The data model analysis tells us:
- Which tables are **facts** (events, transactions) vs. **dimensions** (lookups, reference)
- What **joins** connect them (and at what cardinality)
- What the **granularity** is (what does one row represent?)
- Whether the data has **integrity issues** we need to handle

---

### Slide 2: What Genie Code Will Analyze

| Analysis | What it reveals |
|---|---|
| PK/FK candidates | How tables relate to each other |
| Granularity | One row = one order? One row = one line item? |
| Referential integrity | Orphaned records, null FK rates |
| Join cardinality | Many-to-one? One-to-many? |
| Data profiling | Value distributions, null rates, distinct counts |
| Lineage | How often is each table updated? What reads from it? |

This is the "full-spectrum" analysis — not just a schema dump.

---

### Slide 3: Star Schema → Metric View

```
        ┌──────────┐
        │ dim_date  │
        └─────┬────┘
              │
┌──────────┐  │  ┌──────────┐
│dim_product├──┼──┤ fact_sales│ ← This is the MV source
└──────────┘  │  └──────────┘
              │
        ┌─────┴────┐
        │dim_region │
        └──────────┘
```

The fact table is the MV source. Dimensions are LEFT OUTER JOINs. Fields come from dimensions. Measures come from the fact.

---

### Transition to Live Demo
> "Now I'm going to @ context your schema and ask Genie Code to perform the full-spectrum analysis. Watch how it identifies the fact tables, the join candidates, and the granularity..."

---
---

## Module 06 — YAML Deep Dive

**File:** `docs/workshop-slides/06_yaml_deep_dive.md`

### Presenter Notes
- **Duration:** 10 minutes (presented after lunch, before Phase 3 demo)
- **Key takeaway:** "The YAML is the source of truth. Agent metadata is mandatory. Composability keeps definitions DRY."
- **Common question:** "Can we edit the YAML later?" → Yes. It's version-controlled. Changes go through the same review process.

---

### Slide 1: The YAML Is the Source of Truth

```
fixtures/metric_views/
├── mv_sales.metric_view.yml        ← This is the definition
├── mv_inventory.metric_view.yml
└── mv_customer.metric_view.yml
```

- One file per Metric View
- `{catalog}` and `{schema}` placeholders for target flexibility
- View name derived from filename
- Version-controlled in the DAB repo

---

### Slide 2: Joins — Star and Snowflake

**Star schema** (most common):
```yaml
joins:
  - name: customer
    source: "{catalog}.{schema}.dim_customer"
    on: source.customer_id = customer.customer_id
    rely:
      at_most_one_match: true    # Optimizer hint
```

**Snowflake** (nested joins):
```yaml
joins:
  - name: customer
    source: "{catalog}.{schema}.dim_customer"
    on: source.customer_id = customer.customer_id
    joins:
      - name: nation
        source: "{catalog}.{schema}.dim_nation"
        on: customer.nation_key = nation.nation_key
```

Reference nested columns: `customer.nation.nation_name`

---

### Slide 3: Window Measures — Time-Series KPIs

```yaml
measures:
  - name: rolling_7d_customers
    expr: COUNT(DISTINCT customer_id)
    window:
      - order: order_date
        range: trailing 7 day
        semiadditive: last
```

Rolling averages, cumulative totals, period-over-period — without the consumer writing window functions.

`semiadditive: last` → returns the most recent value when the date field isn't in the GROUP BY.

---

### Slide 4: Format Specifications

| Type | Example | What it does |
|---|---|---|
| `currency` | `{ type: currency, currency_code: USD }` | $1,234.56 |
| `percentage` | `{ type: percentage, decimal_places: { type: exact, places: 1 } }` | 45.2% |
| `number` | `{ type: number, abbreviation: compact }` | 1.2K |
| `date` | `{ type: date, date_format: locale_short_month }` | Sep 1, 2026 |

Formats flow to dashboards and Genie automatically. Define once.

---

### Transition to Live Demo
> "Now I'm going to @ context both the domain research and the data model analysis, and ask Genie Code to generate the Metric View YAMLs. Watch how it uses the industry KPIs from Phase 1 and the join relationships from Phase 2..."

---
---

## Module 07 — Genie Agent Concepts

**File:** `docs/workshop-slides/07_genie_agent_concepts.md`

### Presenter Notes
- **Duration:** 10 minutes (presented after L200-A Phase 4, before L200-B Phase 1)
- **Key takeaway:** "The Genie Agent is the consumption surface. It scopes Genie's context to your domain and only references certified Metric Views."
- **Common question:** "Can business users create their own Agents?" → Yes, via Genie One. But governed Agents should be created as DAB resources with review gates.

---

### Slide 1: What Is a Genie Agent?

A domain-specific environment where your team asks questions in natural language and gets SQL-backed, governed answers.

![Genie Agents](https://docs.databricks.com/aws/en/_images/genie-agents-hero.png)

- Scoped to your business domain (≤30 items)
- Powered by your certified Metric Views
- Curated with instructions, example SQL, and benchmarks
- The **space description** is the routing signal — Genie One uses it to find the right Agent

---

### Slide 2: What Goes IN the Agent

| Include | Don't include |
|---|---|
| ✅ Certified Metric Views | ❌ Raw base tables |
| ✅ Space description | ❌ Uncertified views |
| ✅ Example SQL for common questions | ❌ Every table in the schema |
| ✅ Structured instructions | ❌ Prose instructions for things SQL expressions can handle |
| ✅ Benchmarks for quality testing | |

**Rule:** Only Metric Views. Never raw tables. The MV pre-defines the aggregation logic; raw tables force Genie to guess.

---

### Slide 3: The Knowledge Store

The Agent's knowledge store enhances Genie's understanding:

- **Table/column descriptions** — scoped to the Agent (doesn't change UC metadata)
- **Join relationships** — auto-populated from PK/FK, or manually defined
- **SQL expressions** — reusable measures, filters, and fields
- **Prompt matching** — matches user terms to actual data values (up to 100M rows)

Knowledge mining automatically suggests updates from your interactions.

---

### Slide 4: Benchmarks — How We Know It's Working

A benchmark = a question + the correct SQL answer.

- 2-4 phrasings per question (tests natural language variation)
- Ground truth SQL that produces the known-correct result
- Run after every change — if a previously passing benchmark fails, the new change is the cause

**Our target: ≥85-90% accuracy on in-scope questions.**

---

### Transition to Live Demo
> "Now I'm going to create the Genie Agent as a DAB resource and wire in the certified Metric Views we just built. Watch how the Agent definition references the MVs, not the raw tables..."

---
---

## Module 08 — Curation Patterns

**File:** `docs/workshop-slides/08_curation_patterns.md`

### Presenter Notes
- **Duration:** 10 minutes (presented before L200-B Phase 2)
- **Key takeaway:** "Fix semantics in the Metric View, not in the Agent instructions. The MV is the governed source of truth."
- **Common question:** "What if Genie gets the wrong answer?" → We diagnose whether it's a MV issue (synonyms, comments, formats) or an Agent issue (missing instruction, wrong join). MV fixes go through the MV process; Agent fixes are applied directly.

---

### Slide 1: The Side-by-Side Pattern

```
┌─────────────────┐    ┌─────────────────┐
│   Genie Agent    │    │   Genie Code    │
│   (left panel)   │    │  (right panel)  │
│                  │    │                  │
│  Ask questions   │    │  Evaluate the    │
│  See answers     │    │  answers, propose│
│  Test variations │    │  improvements    │
└─────────────────┘    └─────────────────┘
```

**New Genie Code session** — separate from the building session. Evaluate the Agent fresh.

---

### Slide 2: Where to Fix What

| Problem | Fix it in | Example |
|---|---|---|
| Wrong aggregation logic | **Metric View** (L200-A) | SUM vs. COUNT DISTINCT |
| Missing synonym | **Metric View** agent metadata | Users say "sales" but MV only has "revenue" |
| Ambiguous column | **Agent** knowledge store | Two date columns — add descriptions |
| Missing business rule | **Agent** instruction | "When user asks about 'performance,' they mean cases, not dollars" |
| Wrong join | **Metric View** (L200-A) | Missing or incorrect join condition |

**Bias toward fixing the Metric View.** The MV is the governed source of truth. Agent instructions are a last resort.

---

### Slide 3: The Feedback Loop

```
Agent curation discovers a MV issue
        │
        ▼
File a semantics feedback request
(synonyms, display names, comments, formats ONLY)
        │
        ▼
MV practitioner fixes on a mv-* branch
        │
        ▼
Redeploy → re-certify → merge
        │
        ▼
Agent redeploys → picks up the updated MV
```

**What the Agent process CANNOT suggest:** formula changes, dimension changes, join changes, filter changes. Those are owned by the MV author/reviewer.

---

### Transition to Live Demo
> "Now I'm going to open the Genie Agent and Genie Code side by side. I'll ask test questions, and we'll diagnose any issues together — deciding whether to fix the MV or the Agent..."

---
---

## Module 09 — What's Next

**File:** `docs/workshop-slides/09_whats_next.md`

### Presenter Notes
- **Duration:** 10 minutes (presented at the end of the day)
- **Key takeaway:** "Today was the foundation. There's a clear roadmap for governance, automation, testing, and advanced modeling — all building on what you learned today."
- **Common question:** "Can we do this for other domains?" → Absolutely. Create a new feature branch and repeat the process. The methodology is the same; only the data changes.

---

### Slide 1: What You Built Today

✅ Industry domain research — how your organization talks about its data
✅ Full-spectrum data model analysis — every table, every join, every relationship
✅ Certified Metric Views — your KPIs defined once, governed in Unity Catalog
✅ A curated Genie Agent — natural-language access to trusted answers
✅ A version-controlled repo — reproducible, auditable, extensible

**You own all of this.** It's in your repo, on your feature branch, deployed to your catalog.

---

### Slide 2: Extending to New Domains

To add a new business domain:

1. Create a new feature branch (`<initials>-mv-<domain>`)
2. Repeat Phases 1-4 with the new schema
3. Create a new Genie Agent for the domain
4. Genie One routes questions to the right Agent via the space description

**Same methodology. Same repo. New data.**

---

### Slide 3: The Roadmap

| Topic | What it adds | When |
|---|---|---|
| **Governed domains & pages** | Formal business glossary, auto-tagging, compliance monitoring | Next engagement |
| **Production automation** | Scheduled ontology maintenance, new metric candidates surfaced automatically | Next engagement |
| **Deterministic testing** | CI/CD quality gates — every metric validated before production | Next engagement |
| **Dashboard modeling** | Multi-fact semantic models, governed dashboard deployment | When dashboard needs arise |
| **Knowledge corpus** | Your training manuals and wikis searchable by Genie | Dedicated engagement |
| **AI-enriched metrics** | Forecasts and ML predictions in the semantic layer | Dedicated engagement |

Each topic has a detailed design document ready. We scope the next steps based on what matters most to your organization.

---

### Slide 4: Thank You

**Today you learned it by hand. Next, we automate it.**

The semantic layer you built today is the foundation for everything that comes next — consistent answers, trusted AI, and self-service analytics at scale.

Questions?
