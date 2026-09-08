# Research — Genie Ontology Architecture

## How the Databricks Genie Ontology Works (Sep 2026)

**Project:** Rapid Ontology Standup
**Location:** `docs/research/genie_ontology_architecture.md`
**Date:** 2026-09-01
**Status:** Public Preview (AWS, Azure, GCP)

---

### What Is the Genie Ontology?

The Genie Ontology is the unified context layer that gives Genie One and Genie Code a business-aware map of the organization. It is not a static knowledge graph — it is a two-level context system that combines human-governed definitions with automatically extracted organizational knowledge, ranked by authority and filtered by permissions.

The Ontology powers all three Genie surfaces: Genie One (conversational analytics for business users), Genie Code (agentic coding for practitioners), and Genie Agents (domain-specific environments curated by data teams). Context curated once applies to all surfaces.

---

### Two-Level Context Architecture

The Ontology brings together two categories of context:

#### Level 1: Modeled Context (Unity Catalog Semantics)

This is the human-governed layer — what data and business owners explicitly define and certify. It consists of four components:

| Component | What It Does |
|---|---|
| **Metric Views** | Reusable SQL objects that define governed KPIs. Separate measure definitions from dimensions. Query engine generates correct computation at runtime. |
| **Domains & Subdomains** | Business-aligned organization layer. Groups assets by purpose (not catalog hierarchy). Built on governed tags. Surfaces in the Discover page. |
| **Pages** | Authoritative definitions of business concepts, terms, entities, acronyms. Organized by domain. When Genie answers a question about a concept defined in a Page, it prioritizes the Page's definition over inferred context and cites the Page. |
| **Certification & Deprecation** | Trust signals. Certification steers Genie toward assets the organization vouches for. Deprecation warns that an asset is outdated. Applied via system tags. |

**Key property:** Modeled context takes precedence over inferred context when both exist for the same concept. Published Pages are available in all Genie One conversations; draft Pages only to the Page owner.

#### Level 2: Inferred Context (Learned Organizational Knowledge)

A map of snippets that Genie automatically extracts and maintains from existing assets and usage. Sources include:

- Metric views
- Dashboards and their SQL
- SQL queries (popular, frequently used)
- Genie Agents (instructions, example SQL, knowledge store)
- Table and column metadata
- Notebooks and pipelines
- Usage patterns and lineage signals

Examples of inferred snippets:
- **Metric definition:** "An 'active user' is a distinct user, deduplicated across all platforms."
- **Authoritative source:** "Revenue questions should be answered using the curated Finance Genie Agent."
- **Business rule:** "A 'qualified lead' only counts once a demo is booked."

**Key property:** Inferred context fills gaps where no modeled context exists. It learns from platform activity but does NOT fine-tune the foundation model on your data — it extracts, indexes, ranks, and maintains context snippets.

---

### OntoRank: Authority Ranking

Each snippet receives an authority score. This is not just semantic similarity — it is an authority-weighted ranking that considers:

| Signal | Description |
|---|---|
| **Provenance** | Where the snippet was generated from (governed metric view > ad-hoc query) |
| **Expert authorship** | Was it created by a recognized domain expert? |
| **Expert consumption** | Do domain experts use this asset? |
| **Usage frequency** | How often is the source asset queried? |
| **Certified asset linkage** | Is the source certified? |
| **Freshness** | How recently was the source updated? |
| **Graph relationships** | Authority propagation through usage and lineage graphs (PageRank-style) |

**The critical distinction:**
- Vector similarity asks: "What text looks most similar to the question?"
- OntoRank asks: "Which business definition is both relevant AND most authoritative within this organization?"

Databricks has not published the exact scoring equation or feature weights. Customers cannot currently tune OntoRank weights directly.

---

### Runtime Resolution Flow

When a user asks a question:

1. **Parse** — Identify intent, entities, metrics, filters, time ranges, ambiguity
2. **Retrieve** — Search ontology for candidate snippets and related assets
3. **Permission-filter** — Remove snippets whose source assets the user cannot access (UC permissions gate snippets)
4. **Rank** — Combine question relevance with OntoRank authority
5. **Resolve conflicts** — Prefer governed/higher-authority definitions where multiple exist
6. **Select execution assets** — Choose metric view, table, dashboard query, Genie Agent, SQL example, or function
7. **Generate and execute** — Produce SQL or agent action; warehouse/runtime executes
8. **Return with citations** — Response exposes citations to ontology sources and underlying assets

---

### What the Ontology Is — and Is Not

#### It is:
- A distributed semantic/context layer over Unity Catalog and platform activity
- A combination of curated semantics and automatically inferred organizational knowledge
- A permission-aware retrieval and ranking system
- A way to reuse business context across Genie One, Genie Code, and Genie Agents
- A mechanism for improving accuracy and latency by precomputing organizational context

#### It is not:
- A fully customer-modeled enterprise knowledge graph with an exposed schema
- A replacement for metric-view engineering or data-quality controls
- A guarantee that the highest-ranked definition is mathematically correct
- A substitute for lineage, tests, reconciliation, or semantic ownership
- A published, transparent ranking algorithm whose weights customers can tune

**The critical distinction:** Ontology determines "What does this business term probably mean, and which source should be trusted?" Execution and data quality determine "Is the computed result actually correct?"

---

### Implications for the Rapid Ontology Standup

1. **Metric Views are the highest-authority modeled context** — they should be the primary output of the standup, not just table comments
2. **Pages take precedence over inferred context** — investing in Pages for ambiguous terms pays off immediately in Genie accuracy
3. **Certification amplifies authority** — certifying Metric Views and Genie Agents after validation (Phase 7) directly improves OntoRank scores
4. **Domains organize the Discover experience** — they are not just labels; they scope how Genie One routes questions
5. **The knowledge store in Genie Agents feeds inferred context** — well-curated instructions, example SQL, and SQL expressions become snippets that improve all Genie surfaces
6. **Removing raw tables from the Agent matters** — it prevents low-authority, unaggregated data from competing with governed Metric Views in the ranking

---

### Sources

- Unity Catalog semantics documentation (AWS): https://docs.databricks.com/aws/en/uc-semantics
- Chat in Genie One — Genie Ontology section: https://docs.databricks.com/aws/en/genie-one/chat
- Use Genie Code — Genie Ontology section: https://docs.databricks.com/aws/en/genie-code/use-genie-code
- Pages documentation: https://docs.databricks.com/aws/en/uc-semantics/pages
- Genie Agents concepts: https://docs.databricks.com/aws/en/genie-agents/concepts
- Tune Genie Agent quality: https://docs.databricks.com/aws/en/genie-agents/tune-quality
- Flag data as certified or deprecated: https://docs.databricks.com/aws/en/data-governance/unity-catalog/certify-deprecate-data
- UC Business Semantics GA blog (Aug 2026): https://www.databricks.com/blog/redefining-semantics-data-layer-future-bi-and-ai
