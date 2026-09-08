# Semantics — Genie Ontology Glossary

## UC Page Candidates for the Genie Ontology Domain

**Project:** Rapid Ontology Standup
**Location:** `docs/semantics/genie_ontology_glossary.md`
**Date:** 2026-09-01
**Domain:** Databricks Platform / Genie Ontology
**Subdomain:** UC Semantics, Genie Agents, Context Architecture

Each entry below is structured for direct import as a Unity Catalog Page: definition, business context, data usage, related terms, and source.

---

### Genie Ontology

- **Definition:** The unified context layer that gives Genie One and Genie Code a business-aware map of the organization. Combines human-modeled context (UC Semantics) with automatically inferred context from platform assets and usage.
- **Business Context:** The Ontology is what makes Genie answers accurate and consistent. Without it, Genie would rely solely on raw schema and column names. With it, Genie resolves business terms, selects authoritative sources, and cites its reasoning.
- **Data Usage:** Powers all Genie surfaces (One, Code, Agents). Context curated once applies everywhere. Permission-filtered — users only see snippets from assets they can access.
- **Related Terms:** UC Semantics, Modeled Context, Inferred Context, OntoRank, Metric View, Domain, Page, Genie Agent
- **Source:** https://docs.databricks.com/aws/en/genie-one/chat#ontology

---

### Modeled Context

- **Definition:** The human-governed layer of the Genie Ontology. Business context that people explicitly define and certify through Unity Catalog Semantics features: Metric Views, Domains, Pages, and Certification/Deprecation signals.
- **Business Context:** Modeled context takes precedence over inferred context when both exist for the same concept. This is the layer that the Rapid Ontology Standup builds — it is the "can't-get-it-wrong" business meaning that organizations curate and govern.
- **Data Usage:** Created via SQL DDL (Metric Views), Catalog Explorer UI (Domains, Pages), or Genie Code (all). Stored as UC securable objects with standard privileges, lineage, and audit.
- **Related Terms:** UC Semantics, Metric View, Domain, Page, Certification, Deprecation, Genie Ontology
- **Source:** https://docs.databricks.com/aws/en/uc-semantics

---

### Inferred Context

- **Definition:** A map of snippets that Genie automatically extracts and maintains from existing assets and usage, including metric views, dashboards, SQL queries, Genie Agents, table/column metadata, notebooks, and pipelines. Each snippet receives an authority score via OntoRank.
- **Business Context:** Fills gaps where no modeled context exists. Learns from platform activity but does NOT fine-tune the foundation model — it extracts, indexes, ranks, and maintains context snippets. "Learned context" is a reasonable shorthand but should not be confused with model retraining.
- **Data Usage:** Automatically generated and maintained. Gated by UC permissions. Examples: metric definitions ("active user = distinct user deduplicated across platforms"), authoritative source routing ("revenue questions → Finance Genie Agent"), business rules ("qualified lead = demo booked").
- **Related Terms:** Genie Ontology, OntoRank, Modeled Context, Snippet
- **Source:** https://docs.databricks.com/aws/en/genie-code/use-genie-code#genie-ontology

---

### OntoRank

- **Definition:** The authority-ranking mechanism within the Genie Ontology. Scores each snippet based on provenance, expert authorship, expert consumption, usage frequency, certified asset linkage, freshness, and graph relationships (PageRank-style authority propagation).
- **Business Context:** OntoRank is what distinguishes Genie from a simple RAG system. Vector similarity asks "what text looks most similar?" — OntoRank asks "which definition is both relevant AND most authoritative within this organization?" This is why certifying assets and building Metric Views (high-provenance sources) directly improves answer quality.
- **Data Usage:** Applied at query time during ontology retrieval. Not directly tunable by customers. Scoring equation and feature weights are not published.
- **Related Terms:** Genie Ontology, Inferred Context, Certification, Authority Score
- **Source:** https://docs.databricks.com/aws/en/genie-one/chat#ontology

---

### Metric View

- **Definition:** A reusable SQL object in Unity Catalog that defines governed business KPIs by separating measure definitions (what to calculate) from fields/dimensions (how to slice it). Defined in YAML 1.1, queried via the `MEASURE()` function, and consumed across dashboards, Genie Agents, notebooks, SQL, and external BI tools.
- **Business Context:** The core implementation of UC Semantics. Unlike standard views that lock in aggregations at creation time, Metric Views let you define a metric once and query it at runtime with any available grouping. The query engine generates the correct computation dynamically. This is the primary output of the Rapid Ontology Standup.
- **Data Usage:** Created via `CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML`. Supports star/snowflake joins, composability via `MEASURE()`, window measures (trailing, cumulative, period-over-period), parameters, materialization, and agent metadata (display_name, synonyms, format). One fact source per Metric View.
- **Related Terms:** UC Semantics, Measure, Field/Dimension, Agent Metadata, Materialization, Composability, YAML 1.1
- **Source:** https://docs.databricks.com/aws/en/uc-semantics/metric-views

---

### Domain (UC Semantics)

- **Definition:** A business-aligned organization layer that groups data assets by purpose so users can browse and find data in the Discover page. Built on governed tags — assigning an asset to a domain means tagging it with the domain's governed tag. Large domains can be divided into subdomains using a `{parentDomain}/{subdomain}` naming pattern.
- **Business Context:** Domains complement catalogs — catalogs are the governance/organization unit for data objects; domains are a semantic discovery layer on top. Each domain can have designated Technical Owners and Business Owners. Domains also organize Pages by business area.
- **Data Usage:** Assets can belong to multiple domains/subdomains. Domains support draft and published states. Applied to tables, dashboards, Genie Agents, and metric views via governed tags or the Discover page UI.
- **Related Terms:** Subdomain, Governed Tag, Discover Page, Page, UC Semantics
- **Source:** https://docs.databricks.com/aws/en/uc-semantics/domains

---

### Page (UC Semantics)

- **Definition:** A governed, authoritative definition of a business concept — a critical term, entity, or acronym. Pages are built into the Discover page and organized by domain and subdomain. Each Page contains structured fields (name, description, synonyms), a freeform rich-text body, related assets, and sources.
- **Business Context:** Pages are the "can't-get-it-wrong" definitions. When Genie One answers a question about a concept defined in a Page, it prioritizes the Page's definition over inferred context and cites the Page so users can verify. Formerly known as "Glossary." Available in Beta as of Aug 2026.
- **Data Usage:** Created manually in the Page editor or generated with Genie Code (including bulk import from existing documents). Published Pages are available in all Genie One conversations; draft Pages only to the owner. Page data does not support CMK encryption — do not include PII or regulated data in Page content.
- **Related Terms:** Domain, Genie Ontology, Modeled Context, UC Semantics, Glossary (deprecated name)
- **Source:** https://docs.databricks.com/aws/en/uc-semantics/pages

---

### Certification (UC Semantics)

- **Definition:** A system tag applied to a data asset to signal that it meets the organization's standards. Certification steers Genie One toward the assets the organization vouches for and gives users confidence in the data they consume. Applied via the `certified` system tag.
- **Business Context:** Certification is the trust signal that amplifies OntoRank authority. A certified Metric View or Genie Agent will rank higher than an uncertified one for the same concept. In the Rapid Ontology Standup, certification is applied in Phase 7 after validation passes.
- **Related Terms:** Deprecation, OntoRank, System Tag, UC Semantics
- **Source:** https://docs.databricks.com/aws/en/data-governance/unity-catalog/certify-deprecate-data

---

### Deprecation (UC Semantics)

- **Definition:** A system tag applied to a data asset to warn that it is outdated and should not be used. Deprecation steers users and AI away from stale or superseded definitions.
- **Business Context:** The counterpart to certification. When a Metric View is replaced by a newer version, deprecating the old one prevents Genie from using it as a source. Appears as a visual warning next to the asset in the workspace.
- **Related Terms:** Certification, System Tag, UC Semantics
- **Source:** https://docs.databricks.com/aws/en/data-governance/unity-catalog/certify-deprecate-data

---

### Genie Agent

- **Definition:** A domain-specific environment where data teams configure trusted data, metrics, and business rules that power Genie One answers. Formerly known as "Genie Space." Supports up to 30 tables/views/metric views, a knowledge store, instructions, example SQL, benchmarks, and agent mode.
- **Business Context:** Genie Agents are the consumption surface for the semantic layer. They scope Genie's context to a specific business domain, reducing hallucination and improving accuracy. The space description is critical — multi-agent systems use it to route questions to the correct Agent.
- **Data Usage:** Based on data registered in Unity Catalog. The knowledge store includes agent-level table/column descriptions, synonyms, join relationships, SQL expressions, and prompt matching settings. Knowledge store configurations are scoped to the agent and do not affect UC metadata.
- **Related Terms:** Knowledge Store, Instructions, Example SQL, Benchmarks, Trusted Assets, Agent Mode, Prompt Matching, Genie One
- **Source:** https://docs.databricks.com/aws/en/genie-agents/concepts

---

### Knowledge Store (Genie Agent)

- **Definition:** A collection of curated semantic definitions within a Genie Agent that enhances Genie's understanding of the data. Includes agent-level table and column descriptions, synonyms, join relationships, SQL expressions, and prompt matching settings.
- **Business Context:** The knowledge store is where Phase 6 (Side-by-Side Curation) of the Rapid Ontology Standup adds its refinements. Well-curated knowledge store entries become inferred context snippets that improve all Genie surfaces. Knowledge mining automatically suggests updates based on UC metadata (PK/FK → join relationships) and author interactions (thumbs-up → SQL expression candidates).
- **Data Usage:** Scoped to the agent — does not affect Unity Catalog metadata. Includes: table descriptions, column descriptions, column synonyms, hidden columns, join relationships, SQL expressions (measures, filters, fields), and prompt matching configuration.
- **Related Terms:** Genie Agent, SQL Expression, Join Relationship, Prompt Matching, Inferred Context
- **Source:** https://docs.databricks.com/aws/en/genie-agents/tune-quality

---

### Prompt Matching (Genie Agent)

- **Definition:** A feature that allows Genie to match values in user questions to actual data values in columns, correcting spelling issues and resolving ambiguity. Automatically provided when tables are added to a Genie Agent; manageable per column.
- **Business Context:** Prompt matching is what lets a user type "new york" and have Genie match it to "New York" or "NY" in the data. It scans up to 100M rows for entity matching. Disabling it on irrelevant columns reduces noise.
- **Data Usage:** Configured per column in the Genie Agent knowledge store. Does not modify source data.
- **Related Terms:** Knowledge Store, Genie Agent, Entity Matching
- **Source:** https://docs.databricks.com/aws/en/genie-agents/best-practices

---

### Agent Metadata (Metric View)

- **Definition:** Semantic metadata defined in the Metric View YAML that improves AI accuracy and dashboard display. Includes display names (human-readable labels), synonyms (alternative names for AI discovery, max 10 per field/measure), and format specifications (number, currency, percentage, byte, date, date_time).
- **Business Context:** Agent metadata is what makes the difference between Genie guessing from column names and Genie understanding business terminology. In the Rapid Ontology Standup, agent metadata is mandatory on every field and measure — not optional.
- **Data Usage:** Defined in YAML 1.1. Requires DBR 17.3+. Automatically populates downstream tools: AI/BI dashboards use display names and formats; Genie Agents import synonyms for discovery.
- **Related Terms:** Metric View, Display Name, Synonym, Format Specification, YAML 1.1
- **Source:** https://docs.databricks.com/aws/en/uc-semantics/agent-metadata

---

### Composability (Metric View)

- **Definition:** The ability to build new measures that reference existing measures using the `MEASURE()` function, rather than rewriting aggregation logic. Works within a single Metric View and across Metric Views when one is used as the source for another.
- **Business Context:** Composability is what makes Metric Views maintainable at scale. If the `total_revenue` definition changes (e.g., to exclude tax), every composed measure that references it (`avg_order_value = MEASURE(total_revenue) / MEASURE(order_count)`) automatically uses the updated logic.
- **Data Usage:** Reference patterns: earlier fields in new fields; fields and earlier measures in new measures. Always use `MEASURE()` — never repeat aggregation logic manually.
- **Related Terms:** Metric View, MEASURE() Function, Atomic Measure, Composed Measure
- **Source:** https://docs.databricks.com/aws/en/uc-semantics/metric-views/advanced-techniques

---

### Window Measure (Metric View)

- **Definition:** A measure with windowed, cumulative, or semiadditive aggregation. Supports trailing/leading windows, cumulative running totals, and period-over-period calculations. Defined via the `window` array on a measure in the YAML.
- **Business Context:** Window measures enable time-series KPIs like rolling 7-day active users, month-over-month growth, and year-to-date revenue without requiring the consumer to write window functions. The `semiadditive: last` property handles the common case where a time-series measure should return the most recent value when the time field is not in the GROUP BY.
- **Data Usage:** Window options: `order` (field that orders the window), `range` (trailing/leading/cumulative/current), `semiadditive` (last), `offset` (DBR 18.1+), `inclusive`/`exclusive` modifiers (DBR 18.1+).
- **Related Terms:** Metric View, Trailing Window, Cumulative Total, Period-over-Period, Semiadditive
- **Source:** https://docs.databricks.com/aws/en/uc-semantics/metric-views/advanced-techniques

---

### Materialization (Metric View)

- **Definition:** Pre-computation of aggregations via Lakeflow-managed materialized views. The query optimizer automatically rewrites queries to use the best materialization (exact match or rollup match). Two types: unaggregated (materializes the joined/filtered dataset) and aggregated (pre-built answer table for specific dimension/measure combos).
- **Business Context:** Materialization is the performance layer. It lets you define metrics once and have the platform handle caching and pre-aggregation transparently. Currently in Preview (DBR 17.3+). Rollup match is not available with one-to-many joins or non-additive measures (COUNT DISTINCT, MEDIAN).
- **Data Usage:** Configured in the `materialization` block of the YAML. Options: `schedule` (refresh cadence), `mode` (relaxed/strict), `materialized_views` (array of unaggregated/aggregated definitions with dimensions, measures, cluster_by, partition_by). Source cannot have RLS, column masking, or ABAC policies.
- **Related Terms:** Metric View, Aggregated Materialization, Unaggregated Materialization, Rollup Match, Exact Match, Additive Measure
- **Source:** https://docs.databricks.com/aws/en/uc-semantics/metric-views/materialization

---

### Tagging Strategy & Implementation Priority

| Term | Priority | Phase in Rapid Ontology Standup |
|---|---|---|
| Metric View | **P0** — Primary output | Phase 3 (YAML generation) |
| Genie Agent | **P0** — Consumption surface | Phase 5 (DAB resource) |
| Domain / Subdomain | **P1** — Organization layer | Phase 4 (if enabled) |
| Page | **P1** — Authoritative definitions | Phase 4 (if enabled) |
| Certification | **P1** — Trust signal | Phase 7 (after validation) |
| Agent Metadata | **P0** — Mandatory on all MVs | Phase 3 (inline in YAML) |
| Knowledge Store | **P0** — Curation target | Phase 6 (side-by-side eval) |
| Prompt Matching | **P1** — Accuracy improvement | Phase 6 (curation checklist) |
| Materialization | **P2** — Performance optimization | Post-standup (when query patterns are known) |
