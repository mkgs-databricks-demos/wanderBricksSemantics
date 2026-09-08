# Semantics — Databricks Platform Primitives Glossary

## UC Page Candidates for Databricks Platform Concepts

**Project:** Rapid Ontology Standup
**Location:** `docs/semantics/databricks_platform_glossary.md`
**Date:** 2026-09-01
**Domain:** Databricks Platform
**Subdomain:** Infrastructure, Governance, Development Workflow

Each entry is structured for UC Pages: definition, business context, data usage, related terms, source.

---

### Genie One

- **Definition:** The unified, full-screen natural-language interface for business users to ask data questions. Genie One first searches available Genie Agents for a match, then searches across dashboards, queries, and metric views. Supports Chat (GA), Documents (GA), and Genie Research (multi-step reasoning with citations).
- **Business Context:** Genie One is the primary consumption surface for the semantic layer built by the Rapid Ontology Standup. It is where business users interact with the governed Metric Views and Genie Agents without writing SQL. The quality of Genie One answers is directly determined by the quality of the Genie Ontology.
- **Data Usage:** Routes questions using Agent name + description. Supports external document sources (Google Drive, SharePoint). Conversation context carries forward within a thread. Can create and edit Genie Agents from within a conversation.
- **Related Terms:** Genie Agent, Genie Code, Genie Ontology, Chat, Genie Research, Documents
- **Source:** https://docs.databricks.com/aws/en/genie-one/chat

---

### Genie Code

- **Definition:** The AI coding and data assistant for developers and technical practitioners in the Databricks workspace. Generates and runs code, builds pipelines and dashboards, debugs errors, and works directly with Unity Catalog metadata. Runs in notebooks, the SQL editor, Lakeflow Pipelines, AI/BI dashboards, MLflow, and the bundle editor.
- **Business Context:** Genie Code is the tool that drives the entire Rapid Ontology Standup — every phase runs as an interactive Genie Code session in the bundle editor. It is distinct from Genie One (which is for business users) and Genie Agents (which are domain-specific environments). Genie Code searches the same Genie Ontology as Genie One, so context curated once applies to both.
- **Data Usage:** Governed by UC permissions — can only access data the user has permissions for. Supports agent mode, web search (Beta), @ context referencing, file uploads, and MCP connections. Billed pay-as-you-go with a per-user free monthly allowance (as of Jul 2026).
- **Related Terms:** Genie One, Genie Agent, Bundle Editor, Genie Ontology, Agent Mode
- **Source:** https://docs.databricks.com/aws/en/genie-code

---

### Declarative Automation Bundle (DAB)

- **Definition:** A version-controlled project structure for defining and deploying Databricks resources (jobs, pipelines, schemas, dashboards, Genie Agents) as YAML configuration files. Deployed via the Databricks CLI or the workspace bundle editor. Supports multiple deployment targets (dev, test, prod) with variable overrides.
- **Business Context:** The DAB is the foundational constraint of the Rapid Ontology Standup — all work happens inside a DAB repo on a feature branch. This ensures every artifact (research, YAML, resource definitions, session summaries) is version-controlled from creation. The monorepo pattern (`wb-metric-views` + `wb-genie-agent`) maps each L200 workstream to its own bundle.
- **Data Usage:** `databricks.yml` defines the bundle configuration. `resources/*.yml` defines deployable resources. `${var.*}` for variables, `${resources.*}` for resource interpolation. Supports `include` for multi-file resource definitions.
- **Related Terms:** Bundle Editor, Feature Branch, Resource YAML, Target Configuration, databricks.yml
- **Source:** https://docs.databricks.com/aws/en/dev-tools/bundles/workspace-bundles

---

### Governed Tag

- **Definition:** A tag key in Unity Catalog where an administrator defines the set of allowed values, ensuring consistent tagging across the catalog. Governed tags are the mechanism that powers UC Domains — assigning an asset to a domain means tagging it with the domain's governed tag.
- **Business Context:** Governed tags enforce vocabulary consistency. Without them, teams might tag assets with "finance," "Finance," "FINANCE," or "fin" — all meaning the same thing but invisible to each other in search. Governed tags also power ABAC policies for row-level and column-level security.
- **Data Usage:** Created by metastore admins. Applied to tables, views, metric views, dashboards, and Genie Agents. Used by Domains for asset organization and by ABAC for access control policies.
- **Related Terms:** Domain, ABAC Policy, System Tag, Certification, Deprecation
- **Source:** https://docs.databricks.com/aws/en/data-governance/unity-catalog/tags

---

### Row Filter (Unity Catalog)

- **Definition:** A Unity Catalog access control that restricts which rows a user can see at query time. Implemented as a SQL UDF attached to a table that returns TRUE for rows the user is authorized to access. The UDF can reference `session_user()`, `is_account_group_member()`, and mapping tables for dynamic access control.
- **Business Context:** Row filters are the enforcement mechanism for multi-tenant data isolation in the Rapid Ontology Standup. When a Genie Agent queries a table with a row filter, the filter is applied per user — each user sees only their authorized rows, transparently. Row filters are also the reason metric view materialization cannot be used on FGAC-protected sources.
- **Data Usage:** Attached via `ALTER TABLE ... SET ROW FILTER`. Evaluated at query time using the session user's identity. All filters run with definer's rights except identity functions (`SESSION_USER()`, `IS_ACCOUNT_GROUP_MEMBER()`) which run as the invoker. For consistent filtering across many tables, ABAC policies are recommended over per-table row filters.
- **Related Terms:** ABAC Policy, Column Mask, session_user(), Mapping Table, FGAC
- **Source:** https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks

---

### ABAC Policy (Unity Catalog)

- **Definition:** Attribute-Based Access Control — centralized, tag-driven policies that dynamically filter rows and mask columns across your catalog. ABAC policies attach at the catalog or schema level and apply automatically based on governed tags, rather than requiring per-table configuration.
- **Business Context:** ABAC is the recommended approach for consistent row filtering and column masking across many tables. For multi-tenant customers with dozens or hundreds of tables, ABAC scales better than per-table row filters. However, ABAC policies on source tables prevent metric view materialization — the same constraint as per-table row filters.
- **Data Usage:** Policies are evaluated using the session user's identity (as of the ABAC GA release, Apr 2026). When a pipeline refreshes a materialized view, policies are evaluated using the pipeline owner's identity — add the pipeline owner to the EXCEPT clause to avoid permanently filtered materializations.
- **Related Terms:** Row Filter, Column Mask, Governed Tag, FGAC, Materialization
- **Source:** https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac

---

### Semantics Feedback Request

- **Definition:** A structured request from the Genie Agent curation process (L200-B) back to the Metric View authoring process (L200-A) to improve semantic metadata on a Metric View. Scoped to synonyms, display names, comments, and format specifications only — never formula or logic changes.
- **Business Context:** The feedback request is the formal artifact in the L200-A ↔ L200-B feedback loop. It ensures that semantic improvements discovered during Agent curation are routed to the correct workstream (MV authoring) rather than applied ad-hoc in the Agent's knowledge store. Filed as a GitHub issue, PR comment, or session summary note.
- **Data Usage:** Triggers a new `<initials>-mv-*` feature branch on `wb-metric-views`. The MV practitioner applies the semantic fix, redeploys to dev/test, re-certifies, and merges. The Agent picks up the updated MV on next deploy.
- **Related Terms:** L200-A, L200-B, Handoff Contract, Agent Metadata, Metric View
- **Source:** Internal process definition (Rapid Ontology Standup L200-B)
