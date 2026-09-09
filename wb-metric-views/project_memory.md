# Project Memory — wb-metric-views

## Overview

Bundle for authoring and registering Unity Catalog metric views as part of the `wanderBricksSemantics-care` monorepo. Teaching project demonstrating how Genie Code builds the UC Semantic Layer.

**Bundle root:** `wanderBricksSemantics-care/wb-metric-views/` (absolute: `/Users/matthew.giglia@databricks.com/wanderBricksSemantics-care/wb-metric-views/`)  
**Monorepo root:** `wanderBricksSemantics-care/` (absolute: `/Users/matthew.giglia@databricks.com/wanderBricksSemantics-care/`)  
**Sibling bundle:** `wb-genie-agent` (Genie Space consuming these metric views)  
**Schema name:** `wb_metric_views_care` (the `_care` suffix isolates this workshop instance from other `wanderBricksSemantics` deployments)

> All file paths throughout this document are **relative to the bundle root** (`wb-metric-views/`) unless explicitly noted otherwise.

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

**Phase 3 complete** — 10 metric views authored, registered, and deployed.

| Phase | Status | Artifacts |
| --- | --- | --- |
| Phase 1 — Industry domain research | ✅ Complete | `docs/research/01_industry_domain_research.md` |
| Phase 2 — Data model analysis | ✅ Complete | `docs/research/02_data_model_analysis.md` |
| Phase 2.5 — Semantic glossary | ✅ Complete | `docs/semantics/` (4 files) |
| Phase 3 — Tier 1 MVs (direct table source) | ✅ Complete | `mv_bookings`, `mv_properties`, `mv_payments`, `mv_reviews`, `mv_host_performance`, `mv_page_views` |
| Phase 3 — Tier 2 MVs (SQL-as-source) | ✅ Complete | `mv_booking_funnel`, `mv_amenity_adoption`, `mv_customer_support` |
| Phase 3 — Advanced MVs (window, AI) | ✅ Complete | Window measures on `mv_bookings`, `mv_demand_forecast` (AI_FORECAST) |
| Phase 3 — NPS patterns | ✅ Complete | `sentiment_tier`/`nps_score` on `mv_reviews`, `host_quality_tier`/`host_nps` on `mv_host_performance` |
| Phase 4 — Deploy, review, certify | 🔜 Next | Governance review, UC tags, Genie Agent handoff to L200-B |

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

### Tier 1 — Direct Table Source (6 MVs)

| MV Name | Source Fact | Key Joins | Notable Features |
| --- | --- | --- | --- |
| `mv_bookings` | `bookings` | `properties`, `users`, `destinations`, `countries` | 17 base measures + `booking_month` dim + 7 window measures (trailing 30d, cumulative, MoM) |
| `mv_properties` | `properties` | `destinations`, `countries`, `hosts` | 13 dimensions, 7 measures including host portfolio metrics |
| `mv_payments` | `payments` | `bookings` | Cash-basis revenue; RULE-05/14 compliance |
| `mv_reviews` | `reviews` (`is_deleted=false`) | `bookings` → `properties` → `destinations` | `sentiment_tier` (NPS bucketing), `nps_score` (composable via MEASURE) |
| `mv_host_performance` | `bookings` | `properties` → `hosts` | `host_quality_tier` (NPS), `host_nps` (DISTINCT host-level) |
| `mv_page_views` | `page_views` | `properties`, `destinations` | Traffic demand signals; RULE-06 compliance |

### Tier 2 — SQL-as-Source (3 MVs)

| MV Name | SQL Pattern | Status |
| --- | --- | --- |
| `mv_booking_funnel` | LEFT JOIN page_views→bookings with 30-day attribution window | ✅ Registered (0 conversions due to sample data temporal gap — page_views Sept 2025 vs bookings end Jul 2025) |
| `mv_amenity_adoption` | JOIN property_amenities bridge → amenities dimension | ✅ Verified — 4 categories, luxury rate working |
| `mv_customer_support` | CAST(created_at), SIZE(messages), array indexing for sentiment | ✅ Verified — sentiment turnaround rate working |

### Advanced (1 MV)

| MV Name | Pattern | Status |
| --- | --- | --- |
| `mv_demand_forecast` | L200H Option A: inline AI_FORECAST TVF, dual-value (bookings + revenue) | ✅ Registered, pending AI_FORECAST preview enablement |

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