# Project Memory — wb-metric-views

## Overview

Bundle for authoring and registering Unity Catalog metric views as part of the `wanderBricksSemantics-care` monorepo. Teaching project demonstrating how Genie Code builds the UC Semantic Layer.

**Bundle root:** `/Users/matthew.giglia@databricks.com/wanderBricksSemantics-care/wb-metric-views/`  
**Monorepo root:** `/Users/matthew.giglia@databricks.com/wanderBricksSemantics-care/`  
**Sibling bundle:** `wb-genie-agent` (Genie Space consuming these metric views)  
**Schema name:** `wb_metric_views_care` (the `_care` suffix isolates this workshop instance from other `wanderBricksSemantics` deployments)

---

## Git Workflow

* **NEVER commit or merge directly to `main`.** All work is done in feature branches.
* Branch naming: `mg-genie-<short-description>` (e.g., `mg-genie-project-init`, `mg-genie-add-revenue-metrics`).
* Push the feature branch, then provide a PR title/description for manual merge.
* Commits use conventional-commit style: `feat:`, `fix:`, `docs:`, `chore:`, etc.

---

## Session Summaries

After meaningful work sessions, write a summary in `fixtures/sessions/`.

**Format:** `YYYY-MM-DD_short-description.md`  
**Dates:** Always use `datetime.now()` — never guess.

**Content structure:**

```markdown
# Session: <short description>
**Date:** YYYY-MM-DD

## Problems
- What issue(s) were addressed

## Root Causes
- Why the problem occurred (if applicable)

## Changes
- What was added/modified/removed

## Decisions
- Key choices made and rationale

## Files Modified
- List of files touched
```

**INDEX.md:** Maintain `fixtures/sessions/INDEX.md` in reverse-chronological order (newest first). Each entry links to the session file with a one-line summary.

---

## Targets

| Target | Mode | Workspace | Default |
| --- | --- | --- | --- |
| dev | development | fevm-hls-fde | yes |
| prod | production | fevm-hls-fde | no |

---

## Conventions

* Notebook paths default to `.ipynb`; use `.sql` only with `warehouse_id`.
* First notebook cell: `%pip install --upgrade databricks-sdk` + `dbutils.library.restartPython()`.

### Resource References

**Always** reference deployed resources via their bundle interpolation — never hardcode IDs, names, or raw variables:

```yaml
${resources.<resource_type>.<resource_key>.<value_name>}
```

Examples:

```yaml
# Schemas
${resources.schemas.wb_metric_views_schema.name}
${resources.schemas.wb_metric_views_schema.id}

# Jobs
${resources.jobs.register_metric_views.id}

# Pipelines (example — none defined yet)
${resources.pipelines.<pipeline_key>.id}

# SQL Warehouses (example — none defined yet)
${resources.sql_warehouses.<warehouse_key>.id}

# Volumes (example — none defined yet)
${resources.volumes.<volume_key>.id}
```

This ensures dependency ordering, avoids drift between targets, and makes refactors safe. Use `${var.*}` only within the resource definition itself (e.g., the schema resource reads `${var.catalog}`) — downstream consumers always go through `${resources.*}`.

---

## Current Phase

**Phase 3 ready** — all research and semantic documentation complete. Next work is YAML generation.

| Phase | Status | Artifacts |
| --- | --- | --- |
| Phase 1 — Industry domain research | ✅ Complete | `docs/research/01_industry_domain_research.md` |
| Phase 2 — Data model analysis | ✅ Complete | `docs/research/02_data_model_analysis.md` |
| Phase 2.5 — Semantic glossary | ✅ Complete | `docs/semantics/` (4 files) |
| Phase 3 — Metric view YAML generation | 🔜 Next | `fixtures/metric_views/*.metric_view.yml` |

**Phase 3 authoring order:** `mv_bookings` → extend `mv_properties` → `mv_payments` → `mv_reviews` → `mv_host_performance` → `mv_page_views`.

---

## Documentation Structure

```
docs/
├── research/
│   ├── 01_industry_domain_research.md   # Hospitality/STR KPI and industry research
│   └── 02_data_model_analysis.md        # Full 16-table analysis: PK audit, FK map, DQ flags, MV candidates
└── semantics/
    ├── 01_domain_context.md             # WanderBricks business type, subdomain taxonomy, non-achievable KPIs, Genie gap guidance
    ├── 02_kpi_glossary.md               # 30 KPIs × 6 subdomains — formulas, synonyms, MV mappings, RULE-N refs
    ├── 03_dimension_hierarchies.md      # 5 hierarchies: Geography, Time (dual-date), Guest, Property, Channel
    └── 04_business_rules.md             # RULE-01..14 — DQ flags, status filters, column semantic distinctions
```

**Semantic glossary usage:**
- Cite RULE-N IDs in every metric view YAML `description:` field that touches an affected table.
- Sync metric view `synonyms:` arrays with `docs/semantics/02_kpi_glossary.md` synonyms lists.
- Read `04_business_rules.md` before authoring any new metric view YAML.

---

## Metric View Candidates

### Tier 1 — Immediately Buildable

| MV Name | Source Fact | Key Joins |
| --- | --- | --- |
| `mv_bookings` | `bookings` | `properties`, `users`, `destinations` |
| `mv_properties` *(extend)* | `properties` | `destinations`, `hosts` |
| `mv_payments` | `payments` | `bookings` (bridge) |
| `mv_reviews` | `reviews` (`is_deleted=false`) | `bookings`, `properties`, `destinations` |
| `mv_host_performance` | `bookings` | `properties` → `hosts` |
| `mv_page_views` | `page_views` | `properties`, `destinations` |

### Tier 2 — Requires Base View First

| MV Name | Blocker |
| --- | --- |
| `mv_booking_funnel` | Needs `v_property_user_sessions` (no direct FK from `page_views` to `bookings`) |
| `mv_customer_support` | Needs `v_support_ticket_summary` (ARRAY<STRUCT> messages, STRING date) |
| `mv_amenity_adoption` | Needs `v_property_amenity_flat` (M:M bridge) |

---

## Known Stray Workspace Files (to clean up)

These workspace objects have doubled paths and are NOT in git. Delete when convenient.

| Asset ID | Path |
| --- | --- |
| `58077670920109` | `...wb-metric-views/wb-metric-views/docs/research/02_data_model_analysis.md` |
| `58077670920118` | `...wb-metric-views/wb-metric-views/docs/semantics/01_domain_context.md` |

---

## Metric View Registration Pattern

* Metric view YAML definitions live in `fixtures/metric_views/` and follow the `*.metric_view.yml` naming convention.
* A generic registration job discovers all metric view YAML files and registers them into the target schema.
* The registration task passes `catalog_use` from `${var.catalog}` and `schema_use` from `${resources.schemas.wb_metric_views_schema.name}`.
* The registration notebook must be target-flexible: inject catalog and schema at runtime, derive the metric view name from the file name, and publish the metric view into the target location.
* Start with simple verification metric views against the WanderBricks properties sample before expanding to richer semantic-layer definitions.

---

## Dev Mode Naming

When deployed to a `mode: development` target, Databricks auto-prefixes resource names with `dev_<username>_`. The actual deployed schema name will be:

```
hls_fde_dev.dev_matthew_giglia_wb_metric_views_care
```

Always confirm actual deployed names via `bundle summary` (or `${resources.*}` interpolation at runtime) rather than assuming the literal YAML `name:` value. Ad hoc queries in notebooks must use the prefixed name; the registration job resolves it correctly through widget parameters.