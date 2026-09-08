# L200-G — Business Knowledge Corpus for Ontology Enrichment

## Design Document — Ingesting Institutional Knowledge to Power Richer UC Semantics, Knowledge Assistants, and Composite Agents

**Author:** Matthew Giglia
**Status:** Draft — Directional Architecture
**Last Updated:** 2026-09-01
**References:** L100 (Rapid Ontology Standup System Overview), Intelligent Document Processing docs, AI Search docs, Knowledge Assistant docs
**Note:** This L200 is directional. The build itself warrants a dedicated set of design documents scoped with a Databricks SA or FDE engagement.

---

### Overview

L200-A Phase 1 uses Genie Code Web Search to research the customer's industry — but that's generic. The customer's **own institutional knowledge** is far richer: training manuals, marketing material, user guides, internal wikis, legacy dashboards, source-to-target mapping documents, and existing reports. This knowledge contains the exact terminology, KPI definitions, business rules, and domain context that should feed the Genie Ontology.

L200-G defines the **directional architecture** for ingesting this institutional knowledge into a searchable, governed corpus that:

1. **Enriches ontology building** — Genie Code searches the corpus via AI Search MCP during L200-A sessions, producing more accurate Metric Views, Pages, and domain definitions
2. **Powers a Knowledge Assistant** — a document Q&A chatbot with citations for business users who need answers from unstructured sources
3. **Enables composite agents** — applications that combine Knowledge Assistant (unstructured docs) with Genie Agents (structured data + Metric Views) for a unified "ask anything" experience

This is an **advanced enablement** workstream that extends the Rapid Ontology Standup into the customer's full knowledge estate. It is best scoped as a **dedicated Databricks SA or FDE engagement** with its own solution design.

---

### The Knowledge Gap

| What L200-A uses today | What the customer actually has |
|---|---|
| Genie Code Web Search (generic industry terms) | Training manuals for new hires (how the business actually talks) |
| Customer's public-facing marketing material | Internal wikis with tribal knowledge and business rules |
| Schema inspection and data profiling | Source-to-target mapping documents with column meanings and join logic |
| — | Legacy PBI/Tableau dashboards with existing KPI definitions and DAX/LOD logic |
| — | User manuals with workflow descriptions and domain terminology |
| — | Existing reports with approved aggregation logic and filter conventions |

The gap is clear: the richest context for building the semantic layer is locked in unstructured documents that Genie Code can't reach without an ingestion pipeline and a search index.

---

### Directional Architecture

```
Customer Knowledge Sources
├── Training manuals (PDF, DOCX)
├── Marketing material (PPTX, PDF)
├── User manuals (PDF, DOCX)
├── Internal wikis (HTML, Confluence export)
├── Legacy dashboards (PBI .pbit, Tableau .twb)
├── Source-to-target mapping docs (Excel, PDF)
└── Existing reports (PDF, Excel)
         │
         ▼
    UC Volume (landing zone)
         │
         ▼
    Lakeflow Declarative Pipeline + Auto Loader
    ├── Bronze: raw binary files (streaming table, incremental)
    ├── Silver: ai_parse_document() → text, tables, structure
    ├── Silver: ai_extract() → business terms, KPIs, definitions
    ├── Silver: ai_classify() → document type, domain, subdomain
    └── Gold: ai_prep_search() → semantic chunks with context
         │
         ▼
    Delta table: search-ready chunks
         │
         ▼
    AI Search index (Delta Sync, auto-updating)
         │
         ├──→ Genie Code (via AI Search MCP)
         │         └── Richer ontology building in L200-A sessions
         │
         ├──→ Knowledge Assistant (document Q&A with citations)
         │         └── Standalone agent endpoint for business users
         │
         └──→ Composite Agent App
                   ├── Knowledge Assistant (unstructured docs)
                   ├── Genie Agent (structured data + MVs)
                   └── Unified "ask anything" experience
```

---

### Databricks Capabilities Used

#### Document Ingestion and Processing

| Stage | Capability | What it does |
|---|---|---|
| **Ingest** | Lakeflow Declarative Pipeline + Auto Loader | Incrementally ingests files from a UC Volume as a streaming table. New documents dropped into the Volume are automatically processed. |
| **Parse** | `ai_parse_document(content, map('version', '2.0'))` | Converts PDFs, DOCX, PPTX, images into structured elements: text, tables (as HTML), figures (with descriptions), section headers, page numbers, confidence scores. |
| **Extract** | `ai_extract(content, labels)` | Pulls structured fields from parsed text using a schema you define — business terms, KPI definitions, acronyms, column meanings, join logic. |
| **Classify** | `ai_classify(content, labels)` | Routes documents by type (training manual, marketing, user guide, legacy report) and by domain/subdomain — aligns with L200-C domain structure. |
| **Chunk** | `ai_prep_search(parsed)` (Beta) | Transforms parsed documents into semantic chunks enriched with document-level context (titles, section headers, page references). Output is formatted for AI Search indexing. |

#### Search and Retrieval

| Capability | What it does |
|---|---|
| **AI Search index** (Delta Sync) | Vector + hybrid search over the chunk table. Auto-updates as new documents are processed. Supports metadata filters (document type, domain, date, confidentiality). |
| **AI Search MCP** (Public Preview) | Exposes the search index to Genie Code as a tool. The practitioner searches the corpus during ontology building sessions. |
| **`vector_search()` SQL function** | Query the AI Search index directly from SQL — useful for pipeline-based retrieval and testing. |

#### Agent Composition

| Capability | What it does |
|---|---|
| **Knowledge Assistant** | No-code document Q&A chatbot with citations. Uses the Instructed Retriever approach. Supports SME feedback for quality improvement. Deploys as an agent endpoint. |
| **Genie Agent** | Natural-language SQL over structured data and Metric Views. The existing L200-B output. |
| **Supervisor Agent / Multi-Agent System** | Orchestrates Knowledge Assistant + Genie Agent as workers. Routes questions to the right agent based on intent. |
| **Databricks App** | Custom application combining both agents with a unified UI. |

---

### Three Consumption Patterns

#### Pattern 1: Genie Code + AI Search MCP (Ontology Enrichment)

**When:** During L200-A sessions — the practitioner needs customer-specific context that Web Search can't provide.

**How:** Add the AI Search index as an MCP tool in Genie Code settings. Then prompt:

> "Search the customer's training manuals for how they define 'active member.' Also search the source-to-target mapping documents for which tables contain member status and what the valid values are."

**What it feeds:**
- **L200-A Phase 1:** Customer-specific terminology, acronyms, domain definitions → UC Pages
- **L200-A Phase 2:** Source-to-target mappings provide join logic, column meanings, and business rules that schema inspection can't infer
- **L200-A Phase 3:** Legacy dashboard KPI definitions (extracted via `ai_extract` from PBI/Tableau exports) provide existing aggregation logic to preserve or deliberately change in new Metric Views
- **L200-D Workstream 3:** As new documents are added, the pipeline processes them automatically and the health check can surface new terms that don't yet have Pages or MVs

#### Pattern 2: Knowledge Assistant (Document Q&A)

**When:** Business users need answers from unstructured sources — policies, procedures, training material — with citations back to the source document and page.

**How:** Create a Knowledge Assistant from the AI Search index. Configure with the customer's document corpus. Deploy as an agent endpoint.

**What it provides:**
- Grounded answers with page-level citations
- SME feedback loop for quality improvement
- Standalone chatbot experience for business users
- Can be embedded in Slack, Teams, or custom apps via the agent endpoint

#### Pattern 3: Composite Agent App (Documents + Data)

**When:** Questions span both unstructured documents and structured data — "what's our churn policy?" (docs) + "what's our current churn rate?" (data).

**How:** Build a Supervisor Agent or Databricks App that orchestrates:
- Knowledge Assistant as a worker for document questions
- Genie Agent as a worker for structured data questions
- Routing logic that determines which worker handles each question

**Design note:** The composite app is a significant build that warrants its own dedicated design documents. L200-G provides the directional architecture; the implementation should be scoped as a separate engagement.

---

### How This Feeds Each L200

| L200 | What the corpus provides |
|---|---|
| **L200-A Phase 1** | Customer-specific terminology, acronyms, domain definitions from training manuals and marketing material |
| **L200-A Phase 2** | Source-to-target mappings with column meanings, join logic, and business rules |
| **L200-A Phase 3** | Legacy KPI definitions extracted from PBI/Tableau exports — existing aggregation logic to preserve or change |
| **L200-C** | Document classifications by domain/subdomain feed the domain structure; extracted business terms seed Pages |
| **L200-D** | Continuous ingestion of new documents surfaces new terms and definitions for the ontology health check |
| **L200-F** | Legacy dashboard results can serve as ground truth sources for MV testing |

---

### Bundle Options

The document ingestion pipeline and AI Search index need a home in the DAB monorepo. Three options, each with trade-offs:

| Option | Structure | Pros | Cons |
|---|---|---|---|
| **A: New `wb-knowledge-corpus` bundle** | Dedicated bundle with its own pipeline, fixtures, and resources | Clean separation; own lifecycle (documents added continuously, independent of MV development); clear ownership | Third bundle to manage; cross-bundle references needed |
| **B: Shared `wb-platform` bundle** | A platform-level bundle for cross-cutting resources (pipeline, AI Search, Knowledge Assistant) | Single place for infrastructure; avoids proliferation | Mixes concerns; harder to assign ownership |
| **C: Extend `wb-metric-views` bundle** | Add the pipeline and index to the existing MV bundle | Simplest; no new bundle; direct access to MV fixtures | Overloads the MV bundle with unrelated concerns; pipeline lifecycle differs from MV lifecycle |

**Recommendation:** Discuss with the customer's platform team during the engagement scoping. Option A is the cleanest for large implementations; Option C is pragmatic for smaller ones. The choice depends on team structure and operational model.

---

### Implementation Guidance

This section provides directional guidance for the dedicated engagement that builds the corpus.

#### Pipeline Design Considerations

- **Auto Loader** for incremental file ingestion — new documents dropped into the UC Volume are automatically picked up
- **Medallion architecture:** Bronze (raw binary), Silver (parsed + extracted + classified), Gold (search-ready chunks)
- **Separate handling for tables:** Tables extracted as HTML should get a text rendering for search AND optionally a typed relational table for SQL analytics
- **Document versioning:** Track `document_version` and `ingestion_timestamp` to handle updated documents
- **Metadata preservation:** Source path, page number, section header, document type, domain, confidentiality level — all needed for citations and filtering

#### AI Search Index Design Considerations

- **Hybrid search** (semantic + keyword) for exact terms like policy numbers, SKUs, and acronyms alongside semantic questions
- **Metadata filters** for document type, domain, effective date, confidentiality
- **Delta Sync** for automatic index updates as the chunk table changes
- **Separate embedding endpoints** for ingestion (high throughput) vs. query (low latency) if volume warrants it

#### Knowledge Assistant Design Considerations

- **Knowledge sources:** The AI Search index, or files in a UC Volume, or files in a table
- **SME feedback:** Business users and domain experts provide feedback directly in the Knowledge Assistant UI — this improves retrieval quality over time
- **Citations:** Every answer should cite the source document, page, and section
- **Access control:** The Knowledge Assistant respects Unity Catalog permissions on the underlying data

#### Composite Agent Design Considerations

- **Routing logic:** The supervisor must distinguish "document questions" from "data questions" — this can be intent-based (LLM classification) or keyword-based (simpler, more deterministic)
- **Context sharing:** The supervisor can pass document context to the Genie Agent — e.g., "the policy defines churn as no activity in 90 days; now query the data for customers matching that definition"
- **App stack:** Node.js (AppKit) + React + Lakebase for state management + OpenTelemetry for observability + MLflow 3 for traces

---

### Engagement Scoping Guidance

This build is best delivered as a **dedicated Databricks SA or FDE engagement**, preferably scoped after the customer has completed the L200-A/B workshop and understands the ontology. The engagement should cover:

1. **Document inventory:** What documents does the customer have? Where do they live? What formats? How often do they change?
2. **Pipeline design:** Medallion architecture, parsing configuration, extraction schema, classification labels
3. **Index design:** Hybrid vs. vector-only, metadata filters, embedding model selection, refresh cadence
4. **Agent design:** Knowledge Assistant configuration, composite agent routing logic, app architecture
5. **Integration with the ontology:** How the corpus feeds L200-A/C/D sessions — the MCP tool configuration, the Genie Code prompts, the feedback loop
6. **Governance:** Document access control, confidentiality classification, retention policies
7. **Testing:** Retrieval quality evaluation, citation accuracy, agent response quality

**Estimated scope:** 4-8 weeks depending on document volume, format diversity, and the complexity of the composite agent.

---

### Open Questions (for the dedicated engagement)

1. **Document access control:** Should the AI Search index enforce per-user document ACLs, or is the corpus available to all ontology practitioners? If per-user, the pipeline needs ACL metadata and the index needs filter-based access control.
2. **Legacy dashboard extraction:** Should `ai_extract` pull KPI definitions from PBI `.pbit` files, or should the Genie Code BI import feature (L200-E) handle the structured migration while L200-G focuses on the business context (names, descriptions, filter logic)?
3. **Refresh cadence:** How often are documents updated? Daily Auto Loader for active wikis vs. one-time batch for static training manuals?
4. **Language:** Are documents in multiple languages? `ai_parse_document` and Knowledge Assistant support multilingual content, but the extraction schema and classification labels may need localization.
