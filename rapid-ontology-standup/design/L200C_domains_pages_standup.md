# L200-C — Domain, Subdomain & Pages Standup

## Design Document — Create, Version, and Govern UC Domains, Subdomains, and Pages with Genie Code

**Author:** Matthew Giglia
**Status:** Draft
**Last Updated:** 2026-09-01
**References:** L100 (System Overview), Governance Hub blog (Aug 2026), Tag Automations docs
**Input from:** L200-A Phase 1 (domain research markdown seeds Domains and Pages)

---

### Overview

L200-C covers the **governance and discovery layer** of the Rapid Ontology Standup: creating UC Domains, Subdomains, and Pages as version-controlled artifacts, promoting them through review gates, and enforcing domain tagging on production assets via tag automations.

This is an **advanced enablement** workstream — it extends the workshop-day output (L200-A/B) into a governed, self-sustaining domain structure. It is typically delivered as a follow-on FDE engagement after the customer has completed the interactive standup and understands the Genie Ontology.

**Key constraint:** As of Sep 2026, there is no DAB resource type for Domains or Pages. They must be created via the Catalog Explorer UI, Genie Code, or the REST API. This L200 defines a registration pattern analogous to L200-A's Metric View registration — source files in the repo, with a registration job that creates/updates UC objects via the API.

---

### Dependencies

| Dependency | Description |
|---|---|
| **Genie Code (Bundle Editor)** | For Page authoring (including bulk import from markdown) and Domain creation |
| **DAB Repo** | Monorepo — shared with L200-A/B bundles |
| **Feature Branch** | `<initials>-domain-<short-description>` |
| **L200-A Phase 1 output** | Domain research markdown seeds the initial Domains and Pages |
| **Governance Hub (Beta)** | For monitoring tag coverage and surfacing untagged assets |
| **Tag Automations (Beta)** | For enforcing domain tagging on production assets |
| **Unity Catalog** | Domains, Pages, and governed tags are UC features |

---

### Design

L200-C consists of **three phases**.

---

#### Phase 1: Define Domains, Subdomains, and Pages as Source Files

**Goal:** Create version-controlled source files for all Domains, Subdomains, and Pages, seeded from L200-A Phase 1 domain research.

**Genie Code Session:**

1. Open a new Genie Code session in the **bundle editor** (feature branch `<initials>-domain-initial-setup`).
2. Use `@` context to reference the L200-A Phase 1 domain research markdown (`docs/semantics/01_industry_domain_research.md`).
3. Prompt Genie Code to generate:
   - A **domain manifest** file (`fixtures/domains/domain_manifest.yml`) listing all Domains and Subdomains with their names, descriptions, and owners
   - Individual **Page source files** (`fixtures/pages/*.page.md`) for each business concept, structured with: name, description, synonyms, body, related assets, sources
4. Review inline — iterate with Genie Code until the domain structure and Page content are correct.

**Artifacts:**
- `fixtures/domains/domain_manifest.yml` — the domain/subdomain hierarchy
- `fixtures/pages/*.page.md` — one file per Page, structured for API registration

**Domain manifest example:**
```yaml
domains:
  - name: Supply Chain
    description: "Manufacturing, logistics, and inventory management"
    technical_owner: supply-chain-data-team@customer.com
    business_owner: vp-supply-chain@customer.com
    subdomains:
      - name: Manufacturing
        description: "Production lines, quality, and throughput"
      - name: Logistics
        description: "Shipping, warehousing, and distribution"
      - name: Inventory
        description: "Stock levels, reorder points, and demand planning"
```

---

#### Phase 2: Register and Deploy

**Goal:** Create Domains, Subdomains, and Pages in the dev/test UC environment via a registration job.

**Steps:**

1. **Create a registration notebook** (`src/register_domains_and_pages.py`) that:
   - Reads the domain manifest YAML
   - Creates Domains and Subdomains via the Databricks REST API (or Genie Code bulk import for Pages)
   - Reads each `*.page.md` file and creates/updates the corresponding UC Page
   - Tags Metric Views and Genie Agents with the appropriate domain governed tags
2. **Deploy the bundle to dev/test** — the registration job runs and creates the UC objects.
3. **Reviewer handoff** — the governance reviewer inspects:
   - Domain/subdomain structure in the Discover page
   - Page content and accuracy
   - Tag assignments on Metric Views and Agents
4. **Iterate** — if the reviewer identifies issues, update the source files and redeploy.

**Note:** Until Domains and Pages become DAB resource types, this registration pattern is the version-controlled alternative. The source files in `fixtures/` are the source of truth; the UC objects are the deployed artifacts.

---

#### Phase 3: Enforce Domain Tagging via Tag Automations

**Goal:** Ensure that all production assets receive domain governed tags automatically, and that untagged assets are surfaced for remediation.

**Steps:**

1. **Create governed tag keys** for domain classification (if not already created by the customer's governance team):
   - Tag key: `domain` with allowed values matching the domain manifest (e.g., `supply_chain`, `finance`, `marketing`)
   - Tag key: `subdomain` with allowed values matching the subdomain hierarchy

2. **Create tag automations** (Beta) that enforce:
   - **New assets promoted to prod must receive a domain tag** — flag any table, view, or metric view in the prod catalog that lacks a `domain` tag
   - **Certify assets that meet readiness criteria** — e.g., has a domain tag, has a description, has an owner
   - **Deprecate stale assets** — e.g., not queried in 90 days, no active lineage

3. **Monitor via Governance Hub** (Beta):
   - Track tag coverage across the estate
   - Surface untagged assets for remediation
   - Review classification findings for sensitive data

4. **Merge the feature branch** to `main`.

---

### Artifacts Summary

| Phase | Artifact | Location |
|---|---|---|
| 1 | Domain manifest YAML | `fixtures/domains/domain_manifest.yml` |
| 1 | Page source files | `fixtures/pages/*.page.md` |
| 2 | Registration notebook | `src/register_domains_and_pages.py` |
| 2 | Deployed Domains, Subdomains, Pages | UC Discover page |
| 3 | Tag automations, governed tag keys | UC governance configuration |

---

### Design Rules

1. **Source files are the source of truth** — UC Domains and Pages are deployed artifacts, not the authoritative definition. If a Page needs to change, update the source file and redeploy.
2. **One Page per file** — `fixtures/pages/{page_name}.page.md`
3. **Domain manifest is declarative** — the registration job creates/updates to match the manifest; it does not append.
4. **New prod assets must be tagged** — enforced via tag automations, monitored via Governance Hub.
5. **Pages should reference related Metric Views** — link each Page to the certified MVs that implement the concept it defines.

---

### Open Questions

1. **Pages REST API:** What are the exact endpoints for programmatic Page creation/update? Research needed before the registration notebook can be built.
2. **Domains REST API:** Same — what are the endpoints for Domain/Subdomain creation?
3. **Tag automation rule syntax:** What conditions are available for the automation rules? Can they reference the domain manifest or must they be configured in the UI?
