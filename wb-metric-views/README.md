# wb-metric-views

Declarative Automation Bundle for authoring and registering **Unity Catalog metric views** as part of the Rapid Genie Ontology Standup workshop.

This bundle belongs to the `wanderBricksSemantics-care` monorepo. Its sibling bundle `wb-genie-agent` consumes these metric views in a Genie Space.

## What It Does

1. **Defines** metric views as YAML files in `fixtures/metric_views/` (10 metric views across 3 tiers).
2. **Registers** them into a target UC schema via a generic registration job and notebook.
3. **Queries** them using `MEASURE()` / `GROUP BY ALL` syntax.

## Structure

```
wb-metric-views/
├── databricks.yml              # Bundle config, catalog variable, dev/prod targets
├── project_memory.md           # Conventions, patterns, and session history
├── README.md
├── resources/
│   ├── wb_metric_views.schema.yml    # UC schema: wb_metric_views_care
│   └── register_metric_views.job.yml # Registration job
├── src/
│   └── register_metric_views         # Python notebook (discovers + registers metric views)
├── fixtures/
│   ├── metric_views/                  # *.metric_view.yml definitions (10 files)
│   │   ├── mv_bookings.metric_view.yml        # Core demand + revenue + window measures
│   │   ├── mv_properties.metric_view.yml      # Supply inventory + host metrics
│   │   ├── mv_payments.metric_view.yml        # Cash-basis revenue
│   │   ├── mv_reviews.metric_view.yml         # Satisfaction + NPS
│   │   ├── mv_host_performance.metric_view.yml # Host productivity + NPS
│   │   ├── mv_page_views.metric_view.yml      # Traffic demand
│   │   ├── mv_booking_funnel.metric_view.yml  # Tier 2: conversion funnel
│   │   ├── mv_amenity_adoption.metric_view.yml # Tier 2: amenity mix
│   │   ├── mv_customer_support.metric_view.yml # Tier 2: support metrics
│   │   └── mv_demand_forecast.metric_view.yml  # Advanced: AI forecast
│   └── sessions/                      # Session summaries
│       ├── INDEX.md
│       └── ...
└── docs/
    ├── research/
    │   ├── 01_industry_domain_research.md   # Hospitality/STR industry KPI research
    │   └── 02_data_model_analysis.md        # 16-table data model analysis and DQ flags
    └── semantics/
        ├── 01_domain_context.md             # Business domain framing and non-achievable KPIs
        ├── 02_kpi_glossary.md               # 30 KPIs with formulas, synonyms, and MV mappings
        ├── 03_dimension_hierarchies.md      # 5 dimension hierarchies with column paths
        └── 04_business_rules.md             # 14 named rules for metric view authoring
```

## Quick Start

1. **Deploy** — Click the deployment rocket 🚀 in the left sidebar, or run `databricks bundle deploy --target dev`.
2. **Run** — Hover over `Register Metric Views` in the Deployments panel and click Run, or run `databricks bundle run register_metric_views --target dev`.
3. **Query** — In a SQL cell or editor:
   ```sql
   SELECT `property_type`, MEASURE(`total_properties`) AS `total_properties`
   FROM <catalog>.<schema>.mv_properties
   GROUP BY ALL
   ```
   Use `bundle summary` to find the actual deployed schema name (dev mode auto-prefixes with `dev_<username>_`).

## Current Metric Views (10)

### Tier 1 — Direct Table Source

| Metric View | Source | Dims | Measures | Highlights |
| --- | --- | --- | --- | --- |
| `mv_bookings` | bookings | 12 | 24 | Window measures (trailing 30d, MoM, cumulative revenue) |
| `mv_properties` | properties | 13 | 7 | Host portfolio metrics, destinations snowflake |
| `mv_payments` | payments | 4 | 6 | Cash-basis revenue, refund/failure rates |
| `mv_reviews` | reviews | 6 | 5 | NPS-style `sentiment_tier` + `nps_score` |
| `mv_host_performance` | bookings | 8 | 8 | `host_quality_tier` + `host_nps` (host-level NPS) |
| `mv_page_views` | page_views | 5 | 4 | Traffic demand signals |

### Tier 2 — SQL-as-Source

| Metric View | SQL Pattern | Dims | Measures |
| --- | --- | --- | --- |
| `mv_booking_funnel` | 30-day page-view→booking attribution | 4 | 6 |
| `mv_amenity_adoption` | Bridge table flattening | 4 | 5 |
| `mv_customer_support` | ARRAY extraction, sentiment analysis | 6 | 5 |

### Advanced

| Metric View | Pattern | Status |
| --- | --- | --- |
| `mv_demand_forecast` | `AI_FORECAST` inline TVF (L200H Option A) | Pending feature enablement |

## Adding a New Metric View

1. Create a new `<name>.metric_view.yml` file in `fixtures/metric_views/`.
2. Follow the YAML structure in existing files as templates:
   - **Direct table source:** `mv_bookings.metric_view.yml` (joins, window measures)
   - **SQL-as-source:** `mv_customer_support.metric_view.yml` (CAST, ARRAY extraction)
   - **NPS pattern:** `mv_reviews.metric_view.yml` (CASE dimension + composable MEASURE)
   - **AI function:** `mv_demand_forecast.metric_view.yml` (inline TVF)
3. Deploy and run the registration job — it auto-discovers all `*.metric_view.yml` files.

## Documentation

### Semantic Layer Reference

- `docs/semantics/01_domain_context.md` — WanderBricks business domain, subdomain taxonomy, non-achievable KPIs
- `docs/semantics/02_kpi_glossary.md` — 30 KPIs with formulas, Genie synonyms, and metric view mappings
- `docs/semantics/03_dimension_hierarchies.md` — 5 dimension hierarchies with exact column paths
- `docs/semantics/04_business_rules.md` — 14 named rules (RULE-01..14) to cite in metric view YAML `description:` fields

### Research

- `docs/research/01_industry_domain_research.md` — Hospitality and STR industry KPI research
- `docs/research/02_data_model_analysis.md` — Full 16-table data model analysis with DQ flags and MV candidates

### Databricks

- [Declarative Automation Bundles in the workspace](https://docs.databricks.com/aws/en/dev-tools/bundles/workspace-bundles)
- [Declarative Automation Bundles Configuration reference](https://docs.databricks.com/aws/en/dev-tools/bundles/reference)
- [Unity Catalog Metric Views](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-metric-views)