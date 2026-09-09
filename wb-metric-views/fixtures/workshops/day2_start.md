# Workshop Day 2 — Starting Point

**Branch:** `care-genie-day-2`  
**Starting from:** `mg-genie-care-metric-views` (instructor branch, Phase 2.5 complete)  
**Workshop:** Rapid Genie Ontology Standup — WanderBricksSemantics-care

---

## What Is Already Built

This branch represents the end of Day 1 / beginning of Day 2. The following work is complete and ready for you to use:

| Area | Location | Status |
| --- | --- | --- |
| Bundle scaffold + registration job | `databricks.yml`, `resources/`, `src/` | ✅ Deployed to dev |
| Metric view: `mv_properties` | `fixtures/metric_views/mv_properties.metric_view.yml` | ✅ Registered and queryable |
| Industry domain research | `docs/research/01_industry_domain_research.md` | ✅ Complete |
| Data model analysis (16 tables) | `docs/research/02_data_model_analysis.md` | ✅ Complete |
| Business semantic glossary | `docs/semantics/` (4 files) | ✅ Complete |

## Day 2 Objective — Phase 3: Metric View YAML Generation

You will author new metric view YAML files in `fixtures/metric_views/` and register them into your deployed UC schema.

**Authoring order (Tier 1 — immediately buildable):**

1. `mv_bookings` — core revenue and booking-performance story; highest value
2. Extend `mv_properties` — add `destinations` and `hosts` joins
3. `mv_payments` — completes the revenue picture
4. `mv_reviews` — guest satisfaction KPIs
5. `mv_host_performance` — derived from `bookings` → `properties` → `hosts`
6. `mv_page_views` — standalone traffic metrics

**Key reference files before you write any YAML:**
- `docs/semantics/04_business_rules.md` — read this first; cite RULE-N IDs in `description:` fields
- `docs/semantics/02_kpi_glossary.md` — use the `synonyms:` lists directly in your YAML
- `docs/semantics/03_dimension_hierarchies.md` — use the column paths for your `dimensions:` blocks
- `fixtures/metric_views/mv_properties.metric_view.yml` — use as a YAML structure template

## Your Working Branch

You are on a **shared read branch** (`care-genie-day-2`). Create your own local working branch before making any changes:

```
<your-initials>-genie-day2
```

For example: `jd-genie-day2`. Keep your branch local — do not push to the remote.
