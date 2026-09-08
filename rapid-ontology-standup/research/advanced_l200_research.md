# Research — L200-C, L200-D, L200-E Findings

## Pre-Research for the Advanced Enablement L200s (Sep 2026)

**Project:** Rapid Ontology Standup
**Location:** `docs/research/advanced_l200_research.md`
**Date:** 2026-09-01

---

### L200-C: Domain, Subdomain & Pages Standup

#### Governance Hub (Beta, Aug 2026)

Databricks announced **Governance Hub** on Aug 26, 2026 — an account-level control center for monitoring governance across the Databricks estate. Key capabilities relevant to L200-C:

- **Untagged asset discovery:** The Data page reports how many assets are tagged, owned, and classified, then identifies tables and schemas missing required tags or descriptions
- **Tag coverage monitoring:** The Tags page shows recent tag assignments, invalid values, and recommendations for important assets missing tags
- **Data Classification:** Agentic AI system that detects and tags sensitive data (PII, GDPR, HIPAA, GLBA, PCI categories) automatically at the column level
- **Agent-assisted remediation:** Genie can answer governance questions like "which sensitive-data tables lack masking policies" and surface recommendations

#### Tag Automations (Beta, Aug 2026)

**Automate tag assignment** encodes business rules as conditions, then assigns or removes governed tags on matching assets at scale. Databricks keeps tags accurate as data and metadata change. Key capabilities:

- **Certify trusted data** that meets readiness criteria
- **Deprecate stale data** no longer maintained or queried
- **Roll up column sensitivity** to a table-level sensitivity tier
- **Flag assets missing required tags** and notify their owners
- **Clean up outdated tags** that no longer apply

Automations can be created manually in Catalog Explorer or via Genie in natural language. They use governed tags, so every assigned tag conforms to the same allowed values and permissions as manual tagging.

**Implication for L200-C:** The "new assets promoted to prod must receive a domain governed tag" rule can be enforced via tag automations — not just as a process convention but as a platform-enforced automation. Untagged assets are surfaced by Governance Hub for remediation.

#### Governed Tags — Manual vs. Automated

| Feature | What it does | What it tags | How it works |
|---|---|---|---|
| **Manual tagging** | One object at a time in Catalog Explorer or SQL | Any securable | Human action |
| **Data Classification** | Detects sensitive data using built-in classifiers | Columns | AI + regex against data |
| **Custom classifiers (Beta)** | Detects org-specific data types (employee IDs, partner codes) | Columns | AI + regex against data |
| **Automate tag assignment (Beta)** | Certify, deprecate, flag missing tags, assign sensitivity tiers | Tables and volumes | Deterministic rules against metadata |

#### Pages and Domains as DAB Resources

**Current state:** Domains and Pages are managed via the Catalog Explorer UI or Genie Code. There is **no documented DAB resource type** for Domains or Pages as of Sep 2026. This means:

- Domains and Pages cannot be declared in `resources/*.yml` the way Genie Agents and dashboards can
- They must be created via the UI, Genie Code, or the REST API
- Version control for Pages would need to be managed as markdown source files in the repo, with a registration script (similar to the MV registration pattern) that creates/updates Pages via the API

**Design implication:** L200-C will need a registration pattern similar to L200-A's MV registration — markdown or structured files in `fixtures/pages/`, with a notebook or Genie Code Task that creates/updates Pages and Domains via the API. The DAB deploys the registration job; the job creates the UC objects.

---

### L200-D: Ontology Automation & Production Ops

#### Genie Code Task for Jobs (Beta, Aug 2026)

The **Genie Code task type** launches a new Genie Code chat with a prompt and produces a response autonomously. Key properties:

- Genie Code reads data, calls tools, and acts on the prompt **without requiring additional input or approval**
- Auto-approval cannot be disabled — job tasks always run with auto-approval on
- After the run completes, you can open the chat and continue to interact
- Can read upstream task outputs and call tools as needed
- Returns a link to the resulting Genie Code conversation

**Use cases for L200-D:**
- Summarize overnight job results and email a report
- Analyze incoming data and flag anomalies
- Investigate issues and propose fixes
- Generate weekly compliance audits
- **Surface new Page candidates or MV definition changes as new data is onboarded**

**Implication:** The Genie Code Task is the automation primitive for the "continuous ontology maintenance" vision. A scheduled job could: (1) scan for new tables in the catalog, (2) run a Genie Code Task to analyze them against the existing domain research, (3) propose new Metric View candidates or Page entries, (4) file the proposals as GitHub issues or session summaries for human review.

#### For Each Task

The **For each task** runs a nested task in a loop, passing different parameters to each iteration. Key properties:

- Nested tasks without dependencies can run **concurrently** (configurable concurrency value)
- Inputs are a JSON-formatted array of values
- The nested task references parameters via `{{input}}` or `{{input.<key>}}`
- The nested task is a standard Lakeflow Jobs task type (notebook, SQL, etc.)

**For MV registration:** The `for_each` pattern for concurrent MV registration would:
1. A discovery task lists all `*.metric_view.yml` files and outputs a JSON array
2. A `for_each` task iterates over the array
3. Each iteration runs a SQL task that executes `CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML` for one MV
4. Concurrency is set to the number of MVs (or a reasonable limit)

This replaces the current Python notebook loop with parallel SQL execution over a SQL warehouse.

#### Certified MV Auto-Inclusion

**Current state:** DAB resource YAML is static — you list table identifiers explicitly in the Genie Agent's `serialized_space` JSON. There is no dynamic "include all certified MVs" syntax.

**Automation pattern:** A pre-deploy Genie Code Task or notebook task could:
1. Query `INFORMATION_SCHEMA` or system tables for all metric views in the target schema with the `certified` system tag
2. Generate or update the `geniespace.json` file with the discovered MVs
3. The DAB deployment then uses the updated file

This makes the "include all certified MVs" rule self-enforcing on each deployment.

---

### L200-E: Advanced MV Modeling with AI/BI Dashboards

#### Dashboard Data Modeling Stack

AI/BI dashboards provide four layers of data modeling, from lightest to heaviest:

| Layer | What it does | Scope | Promotable to UC? |
|---|---|---|---|
| **Datasets** | SQL queries that supply data to visualizations | Dashboard | No (they are queries) |
| **Custom calculations** | One-off measures and fields on a single dataset | Single dataset | No |
| **Local metric views** | Fields, measures, joins defined in the dashboard visual interface | Dashboard | **Yes** — export to UC metric view |
| **Dashboard relationships** (Public Preview) | Multi-fact, multi-grain semantic model spanning multiple datasets | Dashboard | Not directly (model is dashboard-scoped) |

#### Local Metric Views → UC Metric Views

The promotion flow:
1. Create a local MV in the dashboard from one or more tables (visual interface — same as UC MV editor)
2. Define fields, measures, joins, filters, parameters
3. Iterate and validate within the dashboard
4. When ready: kebab menu → **Export to Metric View** → choose catalog and schema → Create
5. The local MV becomes a UC metric view, accessible by other dashboards, Genie Agents, notebooks, and SQL

**You can also extend a UC metric view** — add dashboard-specific measures and fields on top of an existing UC MV without modifying the original. Read-only access to the UC MV is sufficient.

**Implication for L200-E:** This is a second authoring path for Metric Views — complementary to the Genie Code YAML generation in L200-A. The dashboard path is better for visual, iterative modeling where the practitioner wants to see the data while building. The Genie Code path is better for bulk generation from domain research.

#### Dashboard Relationships (Public Preview)

Dashboard relationships define a semantic model spanning multiple fact and dimension tables:

- **Join logic:** Choose a join field in each dataset and set cardinality (many-to-one, etc.)
- **Runtime resolution:** The query engine resolves joins at query time — no pre-joining in SQL
- **Multi-fact support:** Multiple fact tables can meet at shared (conformed) dimensions
- **Snowflake support:** Dimensions can snowflake to further dimensions
- **Cross-dataset measures:** Define measures that draw on multiple fact tables at once:
  ```
  Net Revenue      = SUM(Orders.revenue) - SUM(Returns.refund)
  Fulfillment Rate = SUM(Shipments.units) / SUM(Orders.units)
  ```
  Each aggregates independently and combines at the shared dimension — no fan-out or double-counting.

**Implication for L200-E:** Dashboard relationships are the visual equivalent of complex MV join modeling. They're dashboard-scoped (not directly promotable to UC), but the patterns they establish can inform UC MV design. The cross-dataset measure pattern maps to MV composability with `MEASURE()`.

#### Dashboards as DAB Resources

Dashboards are a supported DAB resource type:

```yaml
resources:
  dashboards:
    sales_dashboard:
      display_name: 'Sales Analytics'
      file_path: ../src/sales_dashboard.lvdash.json
      warehouse_id: ${var.warehouse_id}
```

The `.lvdash.json` file contains the serialized dashboard definition. Use `databricks bundle generate` to export an existing dashboard to the DAB format.

**Implication for L200-E:** All dashboards should be DAB resources — version-controlled, diffable, deployable across targets. The `lvdash.json` file captures datasets, visualizations, local metric views, and dashboard relationships. This aligns with the foundational constraint (repo-first, DAB-native, branch-controlled).

#### Genie Agent as DAB Resource

Genie Agents are also a supported DAB resource type (requires the `direct` deployment engine):

```yaml
resources:
  genie_spaces:
    supply_chain_agent:
      title: 'Supply Chain Analytics'
      description: 'Ask questions about supply chain KPIs'
      warehouse_id: ${var.warehouse_id}
      file_path: ./supply_chain_agent.geniespace.json
      permissions:
        - level: CAN_RUN
          group_name: users
```

The `.geniespace.json` file contains the serialized Agent definition including data sources, column configs, instructions, and sample questions.

**Implication for L200-B:** This confirms the DAB resource pattern for Genie Agents. The `file_path` approach (external JSON) is cleaner than inline `serialized_space` for version control. The `geniespace.json` file should be generated or maintained by Genie Code during the curation process.

---

### Research Gaps Remaining

| Gap | Needed for | Action |
|---|---|---|
| Pages REST API for programmatic creation/update | L200-C registration pattern | Research the Pages API endpoints |
| Domains REST API for programmatic creation | L200-C registration pattern | Research the Domains API endpoints |
| `geniespace.json` schema documentation | L200-B DAB resource definition | Research the full JSON schema |
| Tag automation rule syntax and conditions | L200-C auto-tagging rules | Research the automation configuration |

---

### Sources

- Governance Hub blog: https://www.databricks.com/blog/introducing-governance-hub-intelligent-account-level-governance-over-your-databricks-estate
- ABAC/Governed Tags/Data Classification GA blog: https://www.databricks.com/blog/abac-row-filtering-and-column-masking-policies-governed-tags-and-data-classification-are-now
- Tag Automations: https://docs.databricks.com/aws/en/admin/governed-tags/automate-tag-assignment
- Governed Tags: https://docs.databricks.com/aws/en/admin/governed-tags
- Genie Code Task for Jobs: https://docs.databricks.com/aws/en/jobs/tasks/genie-code
- For Each Task: https://docs.databricks.com/aws/en/jobs/tasks/for-each
- DAB Resources (Genie Agent, Dashboard): https://docs.databricks.com/aws/en/dev-tools/bundles/resources
- Dashboard Data Modeling: https://docs.databricks.com/aws/en/dashboards/manage/data-modeling
- Local Metric Views: https://docs.databricks.com/aws/en/dashboards/manage/data-modeling/local-metric-views
- Dashboard Relationships: https://docs.databricks.com/aws/en/dashboards/manage/data-modeling/dashboard-relationships
