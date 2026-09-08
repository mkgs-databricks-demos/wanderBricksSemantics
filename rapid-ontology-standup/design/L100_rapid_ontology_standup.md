# L100 — Rapid Ontology Standup

## System Overview — Standing Up the Full Genie Ontology with Genie Code

**Author:** Matthew Giglia
**Status:** Draft
**Last Updated:** 2026-09-01
**References:** go/aireadysemantics, UC Business Semantics GA Blog, Genie Agents best practices
**Reference Implementation:** `github.com/mkgs-databricks-demos/wanderBricksSemtantics`

---

### Purpose

The Rapid Ontology Standup is a system of repeatable processes for building a customer's full Genie Ontology — Metric Views, Domains, Pages, Genie Agents, and the automation that sustains them — using interactive Genie Code sessions in a version-controlled DAB monorepo.

This document is the L100: the system-level overview that defines the component inventory, cross-cutting patterns, handoff contracts, and the sequencing logic that ties the L200s together. Every L200 references this document for shared conventions; it does not reinvent them.

---

### The Pedagogical Principle

The Rapid Ontology Standup is structured like a math class: **first you do it the interactive way so the customer understands the motivation for what comes next.**

**L200-A and L200-B are the "by hand" phase.** The practitioner drives each step conversationally in Genie Code, making decisions in real time, reviewing YAML inline, iterating with the customer. This is designed to be run as a **full-day customer workshop** — the customer sees every step, understands why each artifact exists, and builds confidence that the semantic layer is correct before anything is automated.

**L200-C through L200-E are the "calculator" phase.** They take the patterns learned in the workshop and extend them into governed domain management, production automation, and advanced modeling. These are **advanced topics for additional customer enablement or FDE engagements** — not prerequisites for the initial standup.

The sequencing is deliberate: a customer who has been through the L200-A/B workshop understands *why* a Metric View needs agent metadata, *why* the Genie Agent should only reference certified MVs, and *why* the feedback loop is scoped to semantics only. That understanding is the foundation for trusting the automated processes that come later.

| Phase | L200s | Delivery Format | Audience |
|---|---|---|---|
| **Interactive standup** | L200-A + L200-B | Full-day customer workshop (onsite or remote) | Customer data team + practitioner |
| **Advanced enablement** | L200-C, L200-D, L200-E | Follow-on engagements, FDE work, PS offerings | Customer platform team + practitioner |

---

### Component Inventory

| L200 | Name | Scope | Bundle | Input | Output |
|---|---|---|---|---|---|
| **A** | Metric View Standup | Research, data model analysis, YAML generation, deploy/review/certify | `wb-metric-views` | Customer's UC-registered data | Certified Metric Views |
| **B** | Genie Agent Standup | Agent creation, side-by-side curation, benchmarks, UAT, handoff | `wb-genie-agent` | Certified Metric Views from L200-A | Curated, benchmarked Genie Agent |
| **C** | Domain, Subdomain & Pages Standup | Create/version/promote Domains, Subdomains, and UC Pages as DAB resources | TBD (new bundle or shared) | Domain research from L200-A Phase 1 | Governed Domains, Pages, auto-tagging |
| **D** | Ontology Automation & Production Ops | Automate MV registration, certified MV auto-inclusion, continuous ontology maintenance | Cross-bundle | Outputs of L200-A/B/C | Self-sustaining production ontology |
| **E** | Advanced Metric View Modeling with AI/BI Dashboards | Complex MV modeling, dashboard relationships, local-to-UC MV promotion, dashboard-as-DAB | `wb-metric-views` + dashboard resources | Certified Metric Views from L200-A | Advanced MVs, governed dashboards |

---

### Dependency Graph

```
L200-A (Metric View Standup)
   │
   │ certified Metric Views
   ├──────────────────────────→ L200-B (Genie Agent Standup)
   │                                │
   │ domain research (Phase 1)      │ semantics feedback (synonyms,
   ├──────→ L200-C (Domains &       │ display names, comments, formats)
   │        Pages Standup)      ←───┘
   │
   │ all outputs
   ├──────────────────────────→ L200-D (Automation & Production Ops)
   │
   │ certified Metric Views
   └──────────────────────────→ L200-E (Advanced MV Modeling + Dashboards)
```

**L200-A is the root.** Everything else depends on it. L200-B can start as soon as L200-A produces its first certified Metric Views. L200-C can start as soon as L200-A Phase 1 (domain research) is complete. L200-D and L200-E are post-workshop extensions.

---

### Cross-Cutting Patterns

The following patterns apply to **all L200s**. Individual L200s reference this section rather than redefining them.

#### Repo-First, DAB-Native, Branch-Controlled

- All work happens inside a **Declarative Automation Bundle (DAB) monorepo**
- All Genie Code sessions run in the **bundle editor** on the active feature branch
- **Never commit directly to `main`** — all work in feature branches
- Feature branch naming: `<initials>-<workstream>-<short-description>`
  - `<initials>-mv-*` → L200-A (Metric Views)
  - `<initials>-agent-*` → L200-B (Genie Agent)
  - `<initials>-domain-*` → L200-C (Domains & Pages)
  - `<initials>-ops-*` → L200-D (Automation)
  - `<initials>-dash-*` → L200-E (Dashboards)
- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`
- Push branch → PR → merge to `main`

#### Resource References

Always use bundle interpolation — never hardcode IDs:
```yaml
${resources.schemas.metric_views_schema.name}
${resources.jobs.register_metric_views.id}
${var.catalog}  # Only in resource definitions
```

#### Target Configuration

```yaml
variables:
  catalog:
    default: customer_dev
targets:
  dev:
    mode: development
  test:
    mode: production
    variables:
      catalog: customer_test
  prod:
    mode: production
    variables:
      catalog: customer_prod
```

#### Session Summaries

After meaningful work sessions, write a summary to `fixtures/sessions/YYYY-MM-DD_short-description.md`:
- Problems
- Root Causes
- Changes
- Decisions
- Files Modified

Maintain `fixtures/sessions/INDEX.md` in reverse-chronological order.

#### Genie Code Session Management

- Set permissions to **"Always allow"** in each thread
- Use **separate sessions** for building vs. evaluating (L200-B Phase 2 evaluation must not carry context from the creation session)

---

### Handoff Contracts

| From | To | Artifact | Contract |
|---|---|---|---|
| **L200-A** | **L200-B** | Certified Metric Views | Agent includes all certified MVs for the domain. Standing rule, not one-time. |
| **L200-B** | **L200-A** | Semantics feedback requests | Synonyms, display names, comments, formats only. Never formula/logic changes. |
| **L200-A Phase 1** | **L200-C** | Domain research markdown | Seeds Domains, Subdomains, and Pages. |
| **L200-A/B/C** | **L200-D** | All outputs | Automation wraps the manual processes into production pipelines. |
| **L200-A** | **L200-E** | Certified Metric Views | Advanced modeling extends base MVs with dashboard relationships and complex joins. |

---

### The Workshop Day (L200-A + L200-B)

A typical full-day onsite workshop runs as follows:

| Time | Activity | L200 | Who's involved |
|---|---|---|---|
| **9:00–9:30** | Setup: clone repo, create feature branch, open bundle editor | Pre-work | Practitioner |
| **9:30–10:30** | Phase 1: Industry domain research via Genie Code Web Search | L200-A | Practitioner + customer domain experts |
| **10:30–12:00** | Phase 2: Full-spectrum data model analysis | L200-A | Practitioner (customer observes) |
| **12:00–12:30** | Lunch | — | — |
| **12:30–2:00** | Phase 3: Metric View YAML generation + inline review | L200-A | Practitioner + customer domain experts |
| **2:00–2:30** | Phase 4: Deploy to dev/test, reviewer walkthrough | L200-A | Practitioner + governance reviewer |
| **2:30–3:00** | Phase 4 continued: Domains, Pages, certification | L200-A | Practitioner + customer |
| **3:00–3:30** | Phase 1: Create Genie Agent as DAB resource, deploy | L200-B | Practitioner |
| **3:30–4:30** | Phase 2: Side-by-side curation (2 iterations) | L200-B | Practitioner + customer |
| **4:30–5:00** | Phase 3: Run benchmarks, discuss handoff and next steps | L200-B | All |

**What the customer walks away with:**
- A version-controlled DAB repo with all artifacts
- Certified Metric Views registered in their dev/test catalog
- A curated Genie Agent they can immediately use
- Domain research and data model analysis as reusable documentation
- Understanding of the process — the motivation for automation

---

### Design Rules (System-Wide)

#### Metric View Rules (L200-A)
1. One fact source per Metric View
2. LEFT OUTER JOINs to dimension tables
3. Validate one KPI at a time
4. Same source AND same dimension tables → same Metric View
5. `MEASURE()` for composability
6. Agent metadata (display_name, synonyms, format) is **mandatory**
7. Comments at three levels: MV, dimension, measure
8. FGAC and materialization are mutually exclusive

#### Genie Agent Rules (L200-B)
1. Include all certified Metric Views for the domain
2. Max 30 items per Agent; split by subdomain only if needed
3. Always include a space description (routing signal)
4. Domain-aligned, not report-aligned
5. Remove raw tables — only Metric Views
6. Semantics feedback only — never formula/logic changes
7. Defined as a DAB resource — not created in the UI
8. One Agent per domain; MVs for subdomains and cross-subdomains

#### Governance Rules (L200-C, when written)
1. New assets promoted to prod must receive a domain governed tag
2. Untagged assets should be surfaced and remediated
3. Domains, Subdomains, and Pages managed as DAB resources with review gates

---

### Multi-Tenant Considerations (System-Wide)

When the customer has multi-tenant or sub-customer data isolation requirements:

- **UC row filters / ABAC policies** are the enforcement mechanism — not prompt-level filtering
- **FGAC on source tables prevents metric view materialization** — design rule #8
- **Session scoping** (locking a Genie session to one customer) requires application-layer context narrowing — see L200-B Multi-Tenant Session Scoping section
- **Authentication:** OAuth U2M or per-tenant service principals — never a shared SP for tenant isolation

---

### Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Repo structure** | DAB monorepo with one bundle per workstream | Each L200 maps to a bundle; shared conventions in L100 |
| **Metric View spec** | YAML 1.1 | Required for agent metadata, one-to-many joins, parameters, window offset |
| **Registration pattern** | Python notebook loop (interim); `for_each` over SQL warehouse (target) | Concurrency for parallel MV registration — open design question in L200-D |
| **Genie Agent definition** | DAB resource YAML | Version-controlled, diffable, deployable across targets |
| **Agent topology** | One Agent per domain; MVs for subdomains | Keeps Agent focused; split only at >30 items |
| **Feedback loop scope** | Semantics only (synonyms, display names, comments, formats) | Formula/logic changes owned by MV author/reviewer |
| **Multi-tenant enforcement** | UC row filters / ABAC | Platform-level enforcement; not bypassable by prompt |

---

### Open Questions (System-Level)

| # | Question | Assigned to |
|---|---|---|
| 1 | `for_each` loader pattern: exact implementation for concurrent MV registration over SQL warehouse | L200-D |
| 2 | Certified MV auto-inclusion: can the Agent resource YAML dynamically discover certified MVs, or does a pre-deploy script update the YAML? | L200-D |
| 3 | Databricks governance tools for untagged asset detection: what's available from the recent announcement? How does it integrate with the domain tagging workflow? | L200-C (research phase) |
| 4 | AI/BI dashboard local MV → UC MV promotion flow: how do dashboard relationships map to MV joins? | L200-E (research phase) |
| 5 | Dashboard-as-DAB-resource: what's the current YAML schema for deploying AI/BI dashboards via DAB? | L200-E (research phase) |

---

### Document Inventory

#### Design Documents
| Doc | Location |
|---|---|
| L100 — System Overview (this document) | `docs/design/L100_rapid_ontology_standup.md` |
| L200-A — Metric View Standup | `docs/design/L200A_metric_view_standup.md` |
| L200-B — Genie Agent Standup | `docs/design/L200B_genie_agent_standup.md` |
| L200-C — Domain, Subdomain & Pages Standup | `docs/design/L200C_domains_pages_standup.md` (to write) |
| L200-D — Ontology Automation & Production Ops | `docs/design/L200D_ontology_automation.md` (to write) |
| L200-E — Advanced MV Modeling + Dashboards | `docs/design/L200E_advanced_mv_dashboards.md` (to write) |

#### Research Documents
| Doc | Location |
|---|---|
| Genie Ontology Architecture | `docs/research/genie_ontology_architecture.md` |
| Genie Agent Consumption Patterns | `docs/research/genie_agent_consumption_patterns.md` |

#### Semantics (Glossary) Documents
| Doc | Location |
|---|---|
| Genie Ontology Glossary (15 terms) | `docs/semantics/genie_ontology_glossary.md` |
| Databricks Platform Primitives (7 terms) | `docs/semantics/databricks_platform_glossary.md` |
| Genie Agent Curation (6 terms) | `docs/semantics/genie_agent_curation_glossary.md` |

#### Diagrams
| Doc | Location |
|---|---|
| 01 — L200-A Metric View Standup Flow | `docs/diagrams/01_metric_view_standup_flow.md` |
| 02 — L200-B Genie Agent Standup Flow | `docs/diagrams/02_genie_agent_standup_flow.md` |
| 03 — L200-A ↔ L200-B Handoff and Feedback Loop | `docs/diagrams/03_handoff_and_feedback_loop.md` |
| 04 — Multi-Tenant Session Scoping Architecture | `docs/diagrams/04_multi_tenant_session_scoping.md` |
| 05 — Genie Ontology Two-Level Context Architecture | `docs/diagrams/05_genie_ontology_architecture.md` |
