# wb-metric-views

Declarative Automation Bundle for authoring and registering **Unity Catalog metric views** as part of the Rapid Genie Ontology Standup workshop.

This bundle belongs to the `wanderBricksSemantics-care` monorepo. Its sibling bundle `wb-genie-agent` consumes these metric views in a Genie Space.

## What It Does

1. **Defines** metric views as YAML files in `fixtures/metric_views/` (e.g., `mv_properties.metric_view.yml`).
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
│   ├── metric_views/                  # *.metric_view.yml definitions
│   │   └── mv_properties.metric_view.yml
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

## Current Metric Views

| Metric View | Source Table | Dimensions | Measures |
| --- | --- | --- | --- |
| `mv_properties` | `samples.wanderbricks.properties` | property_type, bedrooms, bathrooms, created_at | total_properties, avg_base_price, total_guest_capacity |

## Adding a New Metric View

1. Create a new `<name>.metric_view.yml` file in `fixtures/metric_views/`.
2. Follow the YAML structure in `mv_properties.metric_view.yml` as a template.
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