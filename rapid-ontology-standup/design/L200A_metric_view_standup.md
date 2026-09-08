# L200-A — Metric View Standup

## Design Document — Research, Author, and Certify Governed Metric Views with Genie Code

**Author:** Matthew Giglia
**Status:** Draft
**Last Updated:** 2026-09-01
**References:** L100 (pending), go/aireadysemantics, UC Business Semantics GA Blog
**Reference Implementation:** `github.com/mkgs-databricks-demos/wanderBricksSemtantics` → `wb-metric-views` bundle
**Handoff to:** L200-B (Genie Agent Standup) — certified Metric Views are the handoff artifact

---

### Overview

L200-A covers the **Metric View creation workstream** of the Rapid Ontology Standup: from industry domain research through data model analysis, YAML generation, deployment to dev/test, governance review, and certification. It operates in the `wb-metric-views` bundle on its own feature branch.

A Metric View is "done" when it is **certified**. Certified Metric Views are the handoff artifact to L200-B (Genie Agent Standup), which wires them into a Genie Agent for consumption.

---

### Dependencies

| Dependency | Description |
|---|---|
| **Genie Code (Bundle Editor)** | All sessions run in the Genie Code bundle editor on the `wb-metric-views` bundle |
| **DAB Repo** | Monorepo with `wb-metric-views` as the target bundle |
| **Feature Branch** | `<initials>-mv-<short-description>` (e.g., `mg-mv-supply-chain-kpis`) — never work directly on `main` |
| **Unity Catalog** | Customer's data must be registered in UC |
| **UC Semantics (GA)** | Metric Views, Domains, Pages |
| **SQL Warehouse** | Serverless or Pro warehouse for Genie Code execution and MV registration |
| **Genie Code Web Search (Beta)** | For industry domain research; fallback: Tavily MCP or manual research |
| **Genie Code Permissions** | Set to "Always allow" in the active thread |

---

### Foundational Constraint: Repo-First, DAB-Native, Branch-Controlled

All work is performed inside the `wb-metric-views` bundle using the Genie Code bundle editor.

**Before Phase 1 begins:**
1. Create (or clone) the DAB monorepo for the customer engagement
2. Create a feature branch on the `wb-metric-views` bundle (e.g., `<initials>-mv-initial-semantics`)
3. Open the bundle in the Genie Code bundle editor

**Git workflow:** Feature branches named `<initials>-mv-<short-description>` (e.g., `mg-mv-add-revenue-metrics`), conventional commits (`feat:`, `fix:`, `docs:`), push branch → PR → merge to `main`.

---

### Design

L200-A consists of **four phases** plus an ongoing feedback intake from L200-B.

---

#### Phase 1: Industry Domain Research

**Goal:** Build a domain glossary of industry terms, sub-domains, and notable concepts that will seed UC Pages and Domains.

**Genie Code Session:**

1. Open a new Genie Code session in the **bundle editor** (feature branch active).
2. Prompt Genie Code to use **Web Search** to research the customer's industry:
   - Industry domains and sub-domains
   - Standard KPIs and metrics for the vertical
   - Regulatory or compliance terminology
   - Common dimensional hierarchies (e.g., product → category → line for manufacturing)
3. Then prompt Genie Code to search for the **customer's own marketing material and public-facing documents** to learn how the customer talks about their domain.
4. Have Genie Code write the combined output to a **markdown file in the repo**.

**Artifact:** `docs/semantics/01_industry_domain_research.md`

**Key Principle:** If UC Pages or Domains are not yet enabled, write to markdown first. The content can be bulk-imported into Pages later.

**Fallback:** If Genie Code Web Search (Beta) is not available, use a Tavily MCP connection or perform the research manually.

---

#### Phase 2: Deep Exploratory Data Model Analysis

**Goal:** Produce an "ERD on steroids" — a comprehensive analysis of the customer's data model.

**Genie Code Session:**

1. Use `@` context to reference the schema(s) targeted for semantic layer creation.
2. Prompt Genie Code to perform a **deep exploratory analysis** covering:
   - **PK/FK candidates** — primary keys, foreign keys, composite key candidates
   - **Referential and entity integrity** — orphaned records, null FK rates
   - **Granularity analysis** — what does one row represent in each table?
   - **Join candidates** — which tables can be joined, on what keys, with what cardinality?
   - **Lineage via INFORMATION_SCHEMA** — how often is each table updated? What reads from it?
   - **Data profiling** — value distributions, null rates, distinct counts for key columns
   - **Composite key identification** — tables that require multi-column keys
   - **Star/snowflake schema detection** — identify fact tables vs. dimension tables
3. Have Genie Code write this analysis to a **markdown file**.

**Artifact:** `docs/semantics/02_data_model_analysis.md`

**Why this matters:** Each Metric View has exactly ONE fact source. Understanding which tables are facts vs. dimensions, and what joins connect them, is the prerequisite for correct Metric View design.

---

#### Phase 3: Metric View YAML Generation

**Goal:** Generate candidate Metric View YAML files directly — the practitioner reviews inline in the Genie Code session ("makes sense, or let's iterate"), then commits to the feature branch.

**Genie Code Session:**

1. Use `@` context to reference **both** the Phase 1 domain research markdown and the Phase 2 data model analysis markdown.
2. Prompt Genie Code to generate **candidate Metric Views as individual YAML files** that:
   - Answer the most common industry KPIs identified in Phase 1
   - Map to the fact/dimension relationships identified in Phase 2
   - Follow the naming convention: `{subdomain}_{kpi_group}`
   - Flag any KPIs that span multiple fact tables (requiring base views first)
3. **Review inline as the practitioner** — scan each generated YAML for "makes sense, or let's iterate." Iterate with Genie Code until the definitions look right.
4. Each YAML file should follow the Metric View YAML 1.1 specification:

```yaml
version: 1.1
comment: "Online Marketing Conversion Metrics for the Digital Commerce subdomain"
source: "{catalog}.{schema}.fact_web_sessions"
joins:
  - name: dim_date
    source: "{catalog}.{schema}.dim_date"
    on: source.session_date = dim_date.date_key
  - name: dim_channel
    source: "{catalog}.{schema}.dim_channel"
    on: source.channel_id = dim_channel.channel_id
fields:
  - name: session_date
    expr: source.session_date
    display_name: "Session Date"
    format:
      type: date
      date_format: year_month_day
      leading_zeros: true
    synonyms: [date, event date]
  - name: channel_name
    expr: dim_channel.channel_name
    display_name: "Marketing Channel"
    synonyms: [channel, traffic source, acquisition channel]
measures:
  - name: total_sessions
    expr: COUNT(DISTINCT source.session_id)
    display_name: "Total Sessions"
    synonyms: [visits, traffic, session count]
  - name: conversion_rate
    expr: MEASURE(converted_sessions) / NULLIF(MEASURE(total_sessions), 0)
    display_name: "Conversion Rate"
    format:
      type: percentage
      decimal_places:
        type: exact
        places: 2
    synonyms: [CVR, conversion percentage]
```

5. Format the YAML files for the bundle registration pattern:
   - One file per Metric View: `{view_name}.metric_view.yml`
   - Stored in `fixtures/metric_views/`
   - Use `{catalog}` and `{schema}` placeholders for runtime injection

**Artifact:** `fixtures/metric_views/*.metric_view.yml`

**Design Decisions:**
- **Agent metadata is mandatory, not optional.** Every measure and dimension gets `display_name` and `synonyms`. Every date field gets `format`.
- **Comments at three levels:** Metric View level, dimension level, and measure level.
- **One fact source per Metric View.** If a KPI spans multiple fact tables, create a base SQL view first (Phase 3b), then build the Metric View on top.

---

#### Phase 4: Deploy to Dev/Test, Review, and Certify

**Goal:** Deploy Metric View YAMLs to a dev/test target, get governance/domain expert approval, and certify.

**Steps:**

1. **Deploy the bundle to the dev (or test) target** — the registration job discovers all `*.metric_view.yml` files and executes `CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML` for each.

2. **Reviewer handoff:** Provide the data governance professional or domain analytics expert with:
   - The **current Metric View YAML definition** — the full file
   - A **summary of changes** — what changed between this iteration and the previous one, and why (PR description, diff, or Genie Code-generated changelog)
   - This applies to **every iteration**, not just the first deployment.

3. **Iterate** — if the reviewer identifies issues (wrong aggregation logic, missing dimensions, incorrect joins), go back to Phase 3 and update the YAML. Redeploy to dev/test. Repeat until approved.

4. **Create UC Domains and Sub-Domains** (if enabled):
   - Map to the domain/sub-domain structure from Phase 1
   - Tag Metric Views with the appropriate domain governed tags
   - Assign stewards

5. **Create UC Pages** (if enabled):
   - Bulk import from the Phase 1 markdown using Genie Code's bulk import feature
   - Each Page gets: definition, business context, related assets (link to Metric Views), sources

6. **Certify** — apply the `certified` system tag to approved Metric Views. Certification is the completion signal — it means the Metric View is ready for consumption by L200-B (Genie Agent Standup).

7. **Merge the feature branch** to `main`.

**Completion criteria:** A Metric View is "done" when it is certified and merged to `main`.

---

### Feedback Intake from L200-B (Genie Agent Standup)

During Genie Agent curation (L200-B), the Agent process may discover that Genie is misinterpreting a Metric View due to semantic issues. The Agent process sends **semantics feedback requests** back to L200-A.

#### What the Agent process CAN suggest (semantics only)

| Feedback Type | Example |
|---|---|
| **Better or additional synonyms** | "Users ask for 'sales' but the synonym list only has 'revenue' — add 'sales' and 'total sales'" |
| **Improved display names** | "The display name 'Rev' is ambiguous — suggest 'Total Revenue (USD)'" |
| **Better comments** | "The measure comment says 'revenue' but doesn't clarify it includes returns" |
| **Missing format specifications** | "This currency measure has no format — suggest `type: currency, currency_code: USD`" |
| **Synonym conflicts across Metric Views** | "Two MVs both use the synonym 'margin' for different measures — one needs disambiguation" |

#### What the Agent process CANNOT suggest (formula/logic changes)

| Off-Limits | Why |
|---|---|
| Changing a measure's `expr` (aggregation logic) | Formula change — owned by the MV author/reviewer |
| Adding or removing dimensions | Data model change |
| Changing join logic or cardinality | Structural change |
| Adding or removing filters | Changes what data the measure includes |

**Flow:** Agent practitioner files a semantics feedback request (GitHub issue, PR comment, or session summary note) → MV practitioner creates a new feature branch on `wb-metric-views` → applies the semantic fix → redeploys to dev/test → re-certifies → merges → Agent picks up the updated MV on next deploy.

---

### Artifacts Summary

| Phase | Artifact | Location |
|---|---|---|
| 1 | Industry Domain Research | `docs/semantics/01_industry_domain_research.md` |
| 2 | Data Model Analysis ("ERD on steroids") | `docs/semantics/02_data_model_analysis.md` |
| 3 | Metric View YAML files (reviewed inline) | `fixtures/metric_views/*.metric_view.yml` |
| 4 | Deployed + certified Metric Views, Domains, Pages | Dev/test → prod UC catalog via bundle deploy |

---

### Metric View Design Rules

1. Each Metric View has exactly **one fact source**
2. Use **LEFT OUTER JOINs** to dimension tables
3. Add and validate **one KPI at a time** before adding the next
4. Include measures in the same Metric View only if they share the **same source AND same dimension tables**
5. Use `MEASURE()` for composability — measures referencing other measures within the same Metric View
6. Agent metadata (display_name, synonyms, format) is **mandatory, not optional**
7. Comments at **three levels**: Metric View, dimension, measure

---

### Testing Strategy

| Test Type | When | Method |
|---|---|---|
| **Per-measure validation** | Phase 3 (after each measure) | Compare query output to known-good results |
| **Governance/domain expert review** | Phase 4 (each iteration) | YAML definition + change summary |
| **Certification gate** | Phase 4 (final) | `certified` system tag applied after approval |

---

### Open Questions

1. **forEach loader pattern:** Preferred pattern is a `for_each` task over a SQL warehouse for concurrency. Current repos use a Python notebook loop due to timing — TODO for next iteration.
2. **UC Pages availability:** Pages are in Beta (Aug 2026). If not enabled, domain research stays in markdown.
3. **Materialization:** When should we recommend Metric View materialization (Preview)? Likely post-standup when query patterns are known.
