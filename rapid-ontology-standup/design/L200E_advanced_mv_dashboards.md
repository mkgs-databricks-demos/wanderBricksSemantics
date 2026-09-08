# L200-E — Advanced Metric View Modeling with AI/BI Dashboards

## Design Document — Complex MV Modeling, Dashboard Relationships, Local-to-UC Promotion, and Dashboard-as-DAB

**Author:** Matthew Giglia
**Status:** Draft
**Last Updated:** 2026-09-01
**References:** L100 (System Overview), Dashboard Data Modeling docs, Local Metric Views docs, Dashboard Relationships docs
**Input from:** L200-A (certified Metric Views as the base to extend)

---

### Overview

L200-E covers **advanced Metric View modeling patterns** that go beyond the Genie Code YAML generation in L200-A. It introduces the AI/BI dashboard as a complementary authoring surface for Metric Views, covers multi-fact semantic models via dashboard relationships, and establishes the pattern for deploying dashboards as DAB resources.

This is an **advanced enablement** workstream — it extends the base Metric Views from L200-A into more complex analytical models. It is typically delivered when the customer needs multi-fact analysis, cross-dataset measures, or wants to use the visual dashboard interface for iterative MV prototyping.

---

### Dependencies

| Dependency | Description |
|---|---|
| **AI/BI Dashboards** | For visual MV authoring, dashboard relationships, and local-to-UC promotion |
| **Certified Metric Views** | Output of L200-A — the base MVs to extend |
| **DAB Repo** | Monorepo — dashboard resources added alongside MV and Agent bundles |
| **Feature Branch** | `<initials>-dash-<short-description>` |
| **SQL Warehouse** | For dashboard execution and MV queries |

---

### Design

L200-E consists of **three phases**.

---

#### Phase 1: Visual MV Prototyping with Local Metric Views

**Goal:** Use the AI/BI dashboard visual interface to prototype new Metric Views iteratively — seeing the data while building — before promoting to Unity Catalog.

**When to use this path vs. Genie Code YAML (L200-A):**

| Scenario | Best path |
|---|---|
| Bulk generation of MVs from domain research | L200-A (Genie Code YAML) |
| Iterative, visual exploration of a single complex MV | **L200-E (dashboard local MV)** |
| Customer wants to see data while defining measures | **L200-E (dashboard local MV)** |
| Multi-fact model spanning multiple datasets | **L200-E (dashboard relationships)** |
| Extending an existing UC MV with dashboard-specific measures | **L200-E (extend UC MV)** |

**Workflow:**

1. Open an AI/BI dashboard (or create a new one).
2. In the Data tab, click **Add data** → create a metric view.
3. Select one or more tables as the data source.
4. Use the **visual interface** to define:
   - Fields (dimensions) with display names and synonyms
   - Measures with aggregation logic
   - Joins between tables
   - Filters and parameters
5. Build visualizations against the local MV to validate the measures produce correct results.
6. Iterate — the visual interface is the same as the UC MV editor, so the learning transfers.

**Key property:** Local metric views are **dashboard-scoped** — they don't create a UC object. This makes them safe for prototyping without polluting the governed catalog.

**Extending an existing UC MV:** You can also start from a certified UC Metric View and add dashboard-specific measures and fields on top. Read-only access to the UC MV is sufficient. This is useful when a dashboard needs a one-off calculation that doesn't belong in the governed layer.

---

#### Phase 2: Promote Local MVs to Unity Catalog

**Goal:** When a local MV is validated and ready for broader use, promote it to Unity Catalog so it becomes a governed, reusable asset.

**Workflow:**

1. In the Data tab, click the kebab menu next to the local metric view.
2. Select **Export to Metric View**.
3. Choose the target catalog and schema (should match the L200-A schema convention).
4. Click Create.

**Post-promotion checklist:**
- [ ] Add the promoted MV to the L200-A `fixtures/metric_views/` as a YAML file (extract via `SHOW CREATE TABLE` or `DESCRIBE TABLE EXTENDED ... AS JSON`)
- [ ] Ensure agent metadata (display_name, synonyms, format) meets the L200-A mandatory standard
- [ ] Submit for governance review (L200-A Phase 4 process)
- [ ] Certify after approval
- [ ] The Genie Agent (L200-B) picks up the new certified MV on next deploy

**Key rule:** Promotion is a **one-way operation** — the local MV becomes a UC MV. The UC MV is now the source of truth. Future changes go through the L200-A process (YAML in the repo → deploy → review → certify), not by editing the dashboard's local copy.

---

#### Phase 3: Multi-Fact Semantic Models with Dashboard Relationships

**Goal:** Build complex analytical models that span multiple fact and dimension tables using dashboard relationships, then use the patterns to inform UC MV design.

**Dashboard Relationships (Public Preview):**

Dashboard relationships define how datasets relate to one another. The query engine resolves joins at runtime — no pre-joining in SQL.

**Capabilities:**
- **Multi-fact models:** Multiple fact tables meeting at shared (conformed) dimensions
- **Snowflake schemas:** Dimensions can snowflake to further dimensions
- **Cross-dataset measures:** Measures that draw on multiple fact tables at once:
  ```
  Net Revenue      = SUM(Orders.revenue) - SUM(Returns.refund)
  Fulfillment Rate = SUM(Shipments.units) / SUM(Orders.units)
  Return Rate      = SUM(Returns.units) / SUM(Orders.units)
  ```
- **Runtime join resolution:** Filters and measures flow across connected datasets without pre-joining

**How this maps to UC Metric Views:**

| Dashboard concept | UC MV equivalent |
|---|---|
| Dashboard relationship (many-to-one) | MV join with `rely.at_most_one_match` |
| Dashboard relationship (snowflake) | MV nested joins |
| Cross-dataset measure | MV composability with `MEASURE()` across MVs (one MV as source of another) |
| Local MV on a single dataset | Standard UC MV |

**Key constraint:** Dashboard relationships are **dashboard-scoped** — they cannot be directly promoted to UC. The patterns they establish (which facts share which dimensions, which cross-dataset measures are valuable) inform the UC MV design, but the UC implementation uses MV joins and composability, not dashboard relationships.

**Workflow for translating dashboard relationships to UC MVs:**

1. Build the multi-fact model in the dashboard using relationships.
2. Validate cross-dataset measures produce correct results.
3. For each fact table in the model, create a UC MV (via L200-A) with the appropriate joins.
4. For cross-fact measures, use MV composability: create a "parent" MV that sources from a "child" MV and adds the cross-fact logic.
5. Alternatively, create a base SQL view that pre-joins the facts, then build a UC MV on top.

---

#### Dashboards as DAB Resources

**All AI/BI dashboards should be deployed as DAB resources** — version-controlled, diffable, deployable across targets.

**DAB resource definition:**
```yaml
resources:
  dashboards:
    supply_chain_dashboard:
      display_name: 'Supply Chain Analytics'
      file_path: ../src/dashboards/supply_chain.lvdash.json
      warehouse_id: ${var.warehouse_id}
      permissions:
        - level: CAN_READ
          group_name: account users
```

**The `.lvdash.json` file** contains the serialized dashboard definition including datasets, visualizations, local metric views, and dashboard relationships. Use `databricks bundle generate` to export an existing dashboard to the DAB format.

**Workflow:**
1. Build and validate the dashboard in the UI.
2. Export to DAB: `databricks bundle generate dashboard --existing-id <dashboard_id>`
3. Commit the `.lvdash.json` file to the repo.
4. Future changes: edit in the UI → re-export → commit → PR → merge.

---

### Artifacts Summary

| Phase | Artifact | Location |
|---|---|---|
| 1 | Local metric views (dashboard-scoped, for prototyping) | Dashboard Data tab |
| 2 | Promoted UC metric views | `fixtures/metric_views/*.metric_view.yml` (via L200-A process) |
| 3 | Dashboard with relationships and cross-dataset measures | `src/dashboards/*.lvdash.json` |
| — | Dashboard DAB resource definition | `resources/dashboards/*.dashboard.yml` |

---

### Design Rules

1. **Two authoring paths, one governed output:** Genie Code YAML (L200-A) and dashboard local MVs (L200-E) both produce UC Metric Views. The UC MV is always the source of truth after promotion.
2. **Local MVs are for prototyping** — don't leave production metrics as local MVs. Promote to UC when validated.
3. **Dashboard relationships inform MV design** — they are not a substitute for UC MVs. The dashboard model is a prototype; the UC implementation is the governed artifact.
4. **Dashboards are DAB resources** — version-controlled via `.lvdash.json`, deployed via bundle.
5. **Post-promotion, changes go through L200-A** — the dashboard's local copy is no longer the source of truth after promotion.

---

### Open Questions

1. **Dashboard relationship → UC MV translation tooling:** Can Genie Code automate the translation of a dashboard relationship model into UC MV YAML? This would close the loop between the visual prototyping path and the governed YAML path.
2. **`.lvdash.json` merge conflicts:** Dashboard JSON files are large and not human-readable. What's the best practice for handling merge conflicts when multiple people edit the same dashboard?
3. **Dashboard-scoped vs. UC-scoped Genie Agents:** When a dashboard has an auto-generated Genie Agent, does it use the dashboard's local MVs or the UC MVs? How does this interact with the L200-B Agent?
