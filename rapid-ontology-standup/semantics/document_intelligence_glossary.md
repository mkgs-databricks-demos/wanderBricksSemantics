# Semantics — Document Intelligence & Knowledge Corpus Glossary

## UC Page Candidates for Document Processing, AI Search, and Knowledge Retrieval

**Project:** Rapid Ontology Standup
**Location:** `docs/semantics/document_intelligence_glossary.md`
**Date:** 2026-09-01
**Domain:** Databricks Platform
**Subdomain:** Document Intelligence, AI Search, Knowledge Retrieval

Each entry is structured for UC Pages: definition, business context, data usage, related terms, source.

---

### Intelligent Document Processing (IDP)

- **Definition:** A unified, end-to-end workflow on the Databricks Lakehouse for converting unstructured content — PDFs, DOCX, images, presentations — into structured, enriched data. Consists of composable stages: ingest, parse, extract, classify, chunk, and index. Available via the Agent Bricks UI (no-code) or SQL AI Functions (at scale).
- **Business Context:** IDP is the ingestion layer for L200-G (Business Knowledge Corpus). It transforms the customer's institutional knowledge — training manuals, marketing material, user guides, legacy reports — into searchable, structured data that feeds ontology building, Knowledge Assistants, and composite agents.
- **Data Usage:** Implemented as a Lakeflow Declarative Pipeline with Auto Loader for incremental file ingestion. Follows the medallion architecture: Bronze (raw binary), Silver (parsed + extracted + classified), Gold (search-ready chunks).
- **Related Terms:** ai_parse_document, ai_extract, ai_classify, ai_prep_search, Lakeflow Pipeline, Auto Loader, AI Search
- **Source:** https://docs.databricks.com/aws/en/agents/agent-bricks/intelligent-document-processing

---

### ai_parse_document

- **Definition:** A built-in SQL AI function that converts raw unstructured files (PDF, DOCX, PPTX, images) into structured representations. Returns a VARIANT document structure containing pages and ordered elements: text, tables (as HTML), figures (with generated descriptions), titles, section headers, captions, footnotes, headers, and footers. Version 2.0 includes confidence scores and bounding boxes.
- **Business Context:** The first stage of the IDP pipeline. Parsing is what makes unstructured documents queryable — without it, a PDF is just a binary blob. The structured output feeds downstream extraction, classification, and chunking. Tables extracted as HTML can be further normalized into typed relational tables for SQL analytics.
- **Data Usage:** Called as `ai_parse_document(content, map('version', '2.0'))` on binary file content from a UC Volume or binary column. Supports PDF, JPG/JPEG, PNG, TIFF/TIF, DOC/DOCX, PPT/PPTX.
- **Related Terms:** IDP, ai_extract, ai_classify, ai_prep_search, UC Volume
- **Source:** https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_parse_document

---

### ai_extract

- **Definition:** A built-in SQL AI function that pulls structured fields from documents or plain text using a schema you define. Extracts entities like business terms, KPI definitions, acronyms, column meanings, contract clauses, or any domain-specific fields.
- **Business Context:** In the Rapid Ontology Standup, `ai_extract` is used to pull business terminology and KPI definitions from parsed training manuals, user guides, and legacy reports. The extracted terms directly seed UC Pages (L200-C) and inform Metric View naming and synonyms (L200-A).
- **Data Usage:** Called as `ai_extract(content, labels)` where labels define the extraction schema. Operates on parsed text output from `ai_parse_document`.
- **Related Terms:** IDP, ai_parse_document, ai_classify, UC Pages, Business Term
- **Source:** https://docs.databricks.com/aws/en/large-language-models/ai-functions

---

### ai_classify

- **Definition:** A built-in SQL AI function that assigns predefined categories to documents or text, supporting up to 500+ labels. Uses state-of-the-art research techniques maintained by Databricks.
- **Business Context:** Routes documents by type (training manual, marketing material, user guide, legacy report) and by domain/subdomain — aligning with the L200-C domain structure. Classification metadata becomes a filter dimension in the AI Search index, enabling scoped retrieval.
- **Data Usage:** Called as `ai_classify(content, labels)` where labels is an array of category strings. Returns the best-matching label.
- **Related Terms:** IDP, ai_parse_document, ai_extract, Domain, Governed Tag
- **Source:** https://docs.databricks.com/aws/en/large-language-models/ai-functions

---

### ai_prep_search

- **Definition:** A built-in SQL AI function (Beta) that transforms parsed documents or plain text into semantic chunks enriched with document-level context — titles, section headers, page references. The output is formatted for AI Search indexing, providing a consistent foundation for RAG and retrieval workloads.
- **Business Context:** The bridge between document parsing and searchable knowledge. Without proper chunking, retrieval quality degrades — chunks that are too large lose precision; chunks that are too small lose context. `ai_prep_search` handles this automatically with document-aware chunking.
- **Data Usage:** Called on the output of `ai_parse_document`. Produces a table of chunks with metadata (document_id, page_number, section_header, chunk_text). This table becomes the source for a Delta Sync AI Search index.
- **Related Terms:** IDP, ai_parse_document, AI Search, RAG, Semantic Chunking
- **Source:** https://docs.databricks.com/aws/en/large-language-models/ai-functions

---

### AI Search

- **Definition:** Databricks' managed vector and hybrid search service (formerly Vector Search). Builds indexes from Delta tables and supports vector, hybrid (semantic + keyword), and full-text retrieval. Delta Sync indexes automatically update as the source Delta table changes.
- **Business Context:** AI Search is the retrieval layer that makes the Business Knowledge Corpus searchable. It powers three consumption patterns: Genie Code searches the corpus via AI Search MCP during ontology building, Knowledge Assistant uses it for document Q&A, and composite agents use it for grounded answers. Hybrid search is important for exact terms (policy numbers, SKUs, acronyms) alongside semantic questions.
- **Data Usage:** Indexes are created from Delta tables with a primary key, an embedding source column (or pre-computed embeddings), and optional metadata columns for filtering. Supports Delta Sync (auto-updating) and triggered refresh modes. Queryable via Python SDK, REST API, SQL (`vector_search()`), or AI Search MCP.
- **Related Terms:** ai_prep_search, Knowledge Assistant, Genie Code MCP, Delta Sync, Hybrid Search, RAG
- **Source:** https://docs.databricks.com/aws/en/ai-search

---

### Knowledge Assistant

- **Definition:** A no-code Agent Bricks capability for creating production-oriented document Q&A chatbots with citations. Uses the Instructed Retriever approach to deliver high-quality answers grounded in the documentation you provide. Supports documents in multiple languages.
- **Business Context:** Knowledge Assistant is the "talk to your documents" experience — complementary to Genie Agents ("talk to your data"). It answers questions from training manuals, HR policies, product documentation, and support knowledge bases with page-level citations. In the Rapid Ontology Standup, it provides business users with access to institutional knowledge that isn't yet captured in Metric Views or Pages.
- **Data Usage:** Knowledge sources can be files in a UC Volume, files in a table, or an AI Search index. Deploys as an agent endpoint usable from AI Playground, Slack, Teams, or custom apps. Supports SME feedback for quality improvement. Uses default storage for temporary data transformations and model checkpoints.
- **Related Terms:** AI Search, Agent Bricks, RAG, Genie Agent, Composite Agent, Citations
- **Source:** https://docs.databricks.com/aws/en/agents/agent-bricks/knowledge-assistant

---

### Business Knowledge Corpus

- **Definition:** The searchable, governed collection of a customer's institutional knowledge — training manuals, marketing material, user guides, internal wikis, legacy dashboards, source-to-target mapping documents, and existing reports — ingested, parsed, and indexed on the Databricks Lakehouse.
- **Business Context:** The corpus is the "missing context" for ontology building. L200-A Phase 1 uses Web Search for generic industry terms, but the customer's own documents contain the exact terminology, KPI definitions, business rules, and domain context that should feed the Genie Ontology. The corpus closes this gap by making institutional knowledge searchable via AI Search MCP in Genie Code sessions.
- **Data Usage:** Built via the L200-G IDP pipeline (Auto Loader → ai_parse_document → ai_extract → ai_classify → ai_prep_search → AI Search index). Consumed by Genie Code (ontology enrichment), Knowledge Assistant (document Q&A), and composite agents (unified experience). Directional — warrants a dedicated SA/FDE engagement to build.
- **Related Terms:** IDP, AI Search, Knowledge Assistant, Genie Code MCP, L200-G, Genie Ontology
- **Source:** Internal architecture definition (Rapid Ontology Standup L200-G)

---

### Tagging Strategy & Implementation Priority

| Term | Priority | Workstream |
|---|---|---|
| IDP Pipeline | **P0** — Ingestion foundation | L200-G (dedicated engagement) |
| ai_parse_document | **P0** — Parsing stage | L200-G pipeline |
| ai_extract | **P1** — Business term extraction | L200-G pipeline, feeds L200-A/C |
| ai_classify | **P1** — Document routing | L200-G pipeline, feeds L200-C domains |
| ai_prep_search | **P0** — Chunking for retrieval | L200-G pipeline |
| AI Search | **P0** — Retrieval layer | L200-G, consumed by Genie Code + Knowledge Assistant |
| Knowledge Assistant | **P1** — Document Q&A | L200-G consumption pattern |
| Business Knowledge Corpus | **P0** — The assembled asset | L200-G output |
