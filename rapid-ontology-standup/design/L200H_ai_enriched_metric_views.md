# L200-H — AI-Enriched Metric Views

## Design Document — Forecasts, ML Predictions, and AI Functions in the Semantic Layer

**Author:** Matthew Giglia
**Status:** Draft — Directional Architecture
**Last Updated:** 2026-09-01
**References:** L100 (Rapid Ontology Standup System Overview), AI Functions docs, ai_forecast docs, Model Serving docs
**Note:** This L200 is directional. The specific models, endpoints, and forecast configurations are customer-specific and warrant a dedicated SA/FDE engagement for production implementation.

---

### Overview

L200-H defines the architecture for incorporating **AI-generated data** — time-series forecasts, ML model predictions, metric change analysis, and LLM-powered enrichments — into the governed semantic layer built by the Rapid Ontology Standup.

**Core design principle:** *"Forecast numerically in the pipeline, define KPIs semantically in metric views, invoke generative/custom AI in a controlled enrichment stage — not repeatedly inside every analytical query."*

This is an **advanced enablement** workstream that extends the base Metric Views from L200-A with predictive and analytical AI capabilities.

---

### Three Architecture Options (Progressive)

The right option depends on the customer's maturity, query volume, and auditability requirements. Present them as a progression — start with A for prototyping, graduate to B or C for production.

---

#### Option A: Inline TVF Source (Prototyping)

The metric view's source is a SQL query that calls `ai_forecast` or another TVF directly. No separate pipeline. Simplest to set up.

```yaml
version: 1.1
comment: "Demand forecast metrics — inline TVF source (prototyping)"

source: >
  SELECT * FROM AI_FORECAST(
    TABLE(
      SELECT
        DATE(order_date) AS ds,
        product_id,
        region,
        SUM(quantity) AS demand
      FROM {catalog}.{schema}.orders
      WHERE order_status = 'COMPLETE'
      GROUP BY 1, 2, 3
    ),
    horizon => date_add(current_date(), 30),
    time_col => 'ds',
    value_col => 'demand',
    group_col => ARRAY('product_id', 'region'),
    prediction_interval_width => 0.95
  )

fields:
  - name: forecast_date
    expr: ds
    display_name: "Forecast Date"
  - name: product
    expr: product_id
    display_name: "Product"
  - name: region
    expr: region
    display_name: "Region"

measures:
  - name: Forecast Demand
    expr: SUM(demand_forecast)
    display_name: "Forecast Demand"
    format: { type: number, decimal_places: { type: exact, places: 0 } }
  - name: Forecast Upper Bound
    expr: SUM(demand_upper)
    display_name: "Forecast Upper Bound"
  - name: Forecast Lower Bound
    expr: SUM(demand_lower)
    display_name: "Forecast Lower Bound"
  - name: Forecast Range
    expr: MEASURE(Forecast Upper Bound) - MEASURE(Forecast Lower Bound)
    display_name: "Forecast Range"
  - name: Forecast Volatility
    expr: MEASURE(Forecast Range) / NULLIF(MEASURE(Forecast Demand), 0)
    display_name: "Forecast Volatility"
    format: { type: percentage }
```

**Pros:** Single governed object. No pipeline to maintain. Quick to prototype.
**Cons:** Every query re-runs the forecast (latency, cost, non-determinism). No audit trail. Not suitable for production dashboards with frequent refreshes.

**Use when:** Prototyping during a workshop. Low query volume. Acceptable latency.

---

#### Option B: Inline TVF Source + Materialization (Preferred when supported)

Same as Option A, but with a `materialization` block. The materialization refresh runs the forecast once; subsequent queries hit the precomputed result. The metric view IS the gold layer.

```yaml
version: 1.1
comment: "Demand forecast metrics — materialized inline TVF"

source: >
  SELECT * FROM AI_FORECAST(
    TABLE(
      SELECT
        DATE(order_date) AS ds,
        product_id,
        region,
        SUM(quantity) AS demand
      FROM {catalog}.{schema}.orders
      WHERE order_status = 'COMPLETE'
      GROUP BY 1, 2, 3
    ),
    horizon => date_add(current_date(), 30),
    time_col => 'ds',
    value_col => 'demand',
    group_col => ARRAY('product_id', 'region'),
    prediction_interval_width => 0.95
  )

fields:
  - name: forecast_date
    expr: ds
    display_name: "Forecast Date"
  - name: product
    expr: product_id
    display_name: "Product"
  - name: region
    expr: region
    display_name: "Region"

measures:
  - name: Forecast Demand
    expr: SUM(demand_forecast)
    display_name: "Forecast Demand"
  - name: Forecast Upper Bound
    expr: SUM(demand_upper)
  - name: Forecast Lower Bound
    expr: SUM(demand_lower)
  - name: Forecast Range
    expr: MEASURE(Forecast Upper Bound) - MEASURE(Forecast Lower Bound)
  - name: Forecast Volatility
    expr: MEASURE(Forecast Range) / NULLIF(MEASURE(Forecast Demand), 0)
    format: { type: percentage }

materialization:
  schedule: EVERY 1 DAY
  mode: relaxed
  materialized_views:
    - name: daily_forecast
      type: aggregated
      dimensions: [forecast_date, product, region]
      measures: [Forecast Demand, Forecast Upper Bound, Forecast Lower Bound]
```

**Pros:** Single governed object. Forecast runs once per materialization refresh. Queries are fast (hit precomputed result). No separate pipeline. The MV is the gold layer AND the precomputed layer.
**Cons:** Requires validation that materialization accepts TVF sources on the customer's runtime version. No `forecast_run_id` or `model_version` audit trail. Forecast cadence is tied to materialization refresh cadence.

**Use when:** The customer wants the simplest production-ready pattern. Materialization supports the TVF source (validate during engagement). Audit trail requirements are modest.

**Validation required:** Test `CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML` with a TVF source and a `materialization` block on the customer's SQL warehouse. If materialization rejects the TVF source, fall back to Option C.

---

#### Option C: Pipeline → Delta Table → MV + Materialization (Production)

A scheduled Lakeflow Job runs `ai_forecast`, writes to a Delta table with full audit metadata. The metric view sources the Delta table. Materialization precomputes aggregations.

**Pipeline (Lakeflow Job):**

```sql
CREATE OR REPLACE TABLE {catalog}.{schema}.demand_forecast AS
SELECT
  product_id,
  region,
  ds AS forecast_date,
  demand_forecast,
  demand_upper,
  demand_lower,
  'v2' AS model_version,
  current_timestamp() AS generated_at,
  '{run_id}' AS forecast_run_id
FROM AI_FORECAST(
  TABLE({catalog}.{schema}.daily_demand),
  horizon => date_add(current_date(), 30),
  time_col => 'ds',
  value_col => 'demand',
  group_col => ARRAY('product_id', 'region'),
  prediction_interval_width => 0.95
)
```

**Conformed actuals + forecasts table:**

```sql
CREATE OR REPLACE TABLE {catalog}.{schema}.demand_actuals_forecasts AS
SELECT ds AS metric_date, product_id, region,
       demand AS actual_demand, NULL AS forecast_demand,
       NULL AS lower_bound, NULL AS upper_bound, 'actual' AS record_type
FROM {catalog}.{schema}.daily_demand
UNION ALL
SELECT forecast_date, product_id, region,
       NULL, demand_forecast, demand_lower, demand_upper, 'forecast'
FROM {catalog}.{schema}.demand_forecast
```

**Metric View:**

```yaml
version: 1.1
comment: "Demand actuals + forecast metrics — production pattern"
source: "{catalog}.{schema}.demand_actuals_forecasts"

fields:
  - name: metric_date
    expr: metric_date
    display_name: "Date"
  - name: product
    expr: product_id
    display_name: "Product"
  - name: region
    expr: region
    display_name: "Region"
  - name: record_type
    expr: record_type
    display_name: "Record Type"
    synonyms: [actual or forecast, data type]

measures:
  - name: Actual Demand
    expr: SUM(actual_demand)
    display_name: "Actual Demand"
  - name: Forecast Demand
    expr: SUM(forecast_demand)
    display_name: "Forecast Demand"
  - name: Forecast Upper Bound
    expr: SUM(upper_bound)
  - name: Forecast Lower Bound
    expr: SUM(lower_bound)
  - name: Forecast Range
    expr: MEASURE(Forecast Upper Bound) - MEASURE(Forecast Lower Bound)
  - name: Forecast Volatility
    expr: MEASURE(Forecast Range) / NULLIF(MEASURE(Forecast Demand), 0)
    format: { type: percentage }
  - name: Forecast Attainment
    expr: MEASURE(Actual Demand) / NULLIF(MEASURE(Forecast Demand), 0)
    display_name: "Forecast Attainment"
    format: { type: percentage }
    synonyms: [accuracy, hit rate]

materialization:
  schedule: EVERY 6 HOURS
  mode: relaxed
  materialized_views:
    - name: daily_demand_metrics
      type: aggregated
      dimensions: [metric_date, product, region, record_type]
      measures: [Actual Demand, Forecast Demand, Forecast Upper Bound, Forecast Lower Bound]
```

**Pros:** Full audit trail (`forecast_run_id`, `model_version`, `generated_at`). Deterministic — same forecast for the same run. Forecast cadence decoupled from query cadence. Supports backtesting and forecast accuracy analysis. Actuals and forecasts in one conformed table.
**Cons:** Requires a separate pipeline (Lakeflow Job as DAB resource). More infrastructure to maintain.

**Use when:** Production-grade implementations. Audit trail required. Forecast accuracy tracking needed. Multiple consumers (dashboards, Genie, alerts) need consistent numbers.

---

### Pattern 2: Custom ML Predictions via ai_query + UC Function

**Step 1:** Wrap `ai_query` in a UC SQL function for governance.

```sql
CREATE OR REPLACE FUNCTION {catalog}.{schema}.predict_churn_risk(
  customer_id STRING,
  tenure_months INT,
  monthly_spend DOUBLE,
  support_tickets INT
)
RETURNS DOUBLE
COMMENT 'Predicts churn probability using the governed churn model endpoint'
RETURN ai_query(
  'churn-risk-model-v2',
  named_struct(
    'customer_id', customer_id,
    'tenure_months', tenure_months,
    'monthly_spend', monthly_spend,
    'support_tickets', support_tickets
  ),
  returnType => 'DOUBLE',
  failOnError => false
);
```

**Step 2:** Batch-score in a scheduled job.

```sql
CREATE OR REPLACE TABLE {catalog}.{schema}.churn_predictions AS
SELECT
  customer_id,
  {catalog}.{schema}.predict_churn_risk(
    customer_id, tenure_months, monthly_spend, support_tickets
  ) AS churn_probability,
  current_timestamp() AS scored_at,
  'v2' AS model_version
FROM {catalog}.{schema}.customer_features;
```

**Step 3:** Build a metric view over the prediction table.

```yaml
version: 1.1
source: "{catalog}.{schema}.churn_predictions"
joins:
  - name: customers
    source: "{catalog}.{schema}.customers"
    on: source.customer_id = customers.customer_id
measures:
  - name: Avg Churn Risk
    expr: AVG(churn_probability)
    format: { type: percentage }
    synonyms: [average churn probability, mean churn risk]
  - name: High Risk Customers
    expr: COUNT(DISTINCT CASE WHEN churn_probability > 0.7 THEN customer_id END)
    display_name: "High Risk Customers"
  - name: At Risk Revenue
    expr: SUM(CASE WHEN churn_probability > 0.7 THEN customers.monthly_spend ELSE 0 END)
    format: { type: currency, currency_code: USD }
    display_name: "At Risk Revenue"
    synonyms: [revenue at risk, churn exposure]
```

**Key rule:** `ai_query` is NEVER called inside a metric view measure or an interactive query. It runs in a batch pipeline; the metric view reads the precomputed results.

---

### Pattern 3: Metric Change Analysis via ai_top_drivers

Run `ai_top_drivers` in a scheduled job to answer "why did this metric change?"

```sql
SELECT * FROM ai_top_drivers(
  input => TABLE(
    SELECT region, product, channel, revenue,
      CASE WHEN month = '2026-03' THEN true ELSE false END AS is_test
    FROM {catalog}.{schema}.monthly_revenue
    WHERE month IN ('2026-02', '2026-03')
  ),
  metric => 'revenue',
  is_test => 'is_test',
  dimensions => ARRAY('region', 'product', 'channel'),
  aggregation => 'sum'
)
```

Persist results to a Delta table. Expose through a metric view or directly in dashboards.

---

### Composable Metric View Stack

Build layered metric views for progressive abstraction:

```
mv_demand_base (Option A/B/C)
  ├── Actual Demand, Forecast Demand, Forecast Interval
  │
  └──→ mv_demand_kpis (composed from base)
        ├── Forecast Attainment, Volatility, Forecast Range
        │
        └──→ mv_executive_forecast (composed from KPIs)
              ├── Revenue at Risk, High Volatility Product Count
              └── Weighted Service Risk
```

Each layer uses `MEASURE()` to reference the layer below — no repeated aggregation logic.

---

### What NOT to Do

| Anti-pattern | Why it's bad | Correct pattern |
|---|---|---|
| `ai_forecast()` in a MV measure | TVFs generate rows, not aggregates — incompatible with measure semantics | Use as MV source (Option A/B) or pipeline output (Option C) |
| `ai_query()` in a MV measure | Endpoint call per query — latency, cost, non-determinism | Batch-score via UC function → Delta table → MV |
| `ai_query()` in a dashboard dataset | Per-render endpoint calls | Precompute in a pipeline |
| Skipping the UC function wrapper | No governance, no lineage, no audit | Always wrap `ai_query` in a UC SQL function |
| Forecast without `forecast_run_id` | Can't reproduce or compare past forecasts | Include run metadata in Option C |

---

### UC Function Governance

UC SQL functions wrapping `ai_query` are governed objects:
- **Permissions:** `EXECUTE` grant required to invoke; `CREATE FUNCTION` requires catalog/schema usage
- **Lineage:** Functions appear in UC lineage graphs
- **Audit:** Invocations are logged
- **Sharing:** Functions can be shared across teams via UC grants
- **Versioning:** Use naming conventions (e.g., `predict_churn_risk_v2`) or schema-level versioning
- **Genie Agent integration:** UC functions can be registered as trusted assets in Genie Agents

---

### Option Selection Guide

| Requirement | Option A | Option B | Option C |
|---|---|---|---|
| Quick prototyping | ✅ Best | ✅ Good | ❌ Overhead |
| Production dashboards | ❌ Too slow | ✅ If materialization works | ✅ Best |
| Audit trail (run ID, model version) | ❌ None | ❌ None | ✅ Full |
| Forecast accuracy tracking | ❌ No actuals | ❌ No actuals | ✅ Conformed table |
| Backtesting | ❌ | ❌ | ✅ Historical runs |
| Simplest architecture | ✅ Single MV | ✅ Single MV | ❌ Pipeline + MV |
| FGAC on source tables | ✅ (no materialization) | ❌ Blocked | ❌ Blocked on MV materialization |
| Custom ML models | ❌ (ai_forecast only) | ❌ | ✅ ai_query via UC function |

---

### Artifacts Summary

| Artifact | Location |
|---|---|
| Forecast metric view YAML (Option A/B) | `fixtures/metric_views/mv_demand_forecast.metric_view.yml` |
| Forecast pipeline job (Option C) | `resources/forecast_pipeline.job.yml` |
| UC function definitions | `src/create_uc_functions.sql` |
| Batch scoring job | `resources/batch_scoring.job.yml` |
| Conformed actuals + forecasts table DDL | `src/create_conformed_tables.sql` |
| Composed KPI metric views | `fixtures/metric_views/mv_demand_kpis.metric_view.yml` |

---

### Open Questions

1. **Option B validation:** Does metric view materialization accept a TVF (`ai_forecast`) in the source SQL on the customer's runtime version? This needs to be tested during the engagement.
2. **Forecast cadence vs. materialization cadence:** In Option B, the forecast re-runs on every materialization refresh. If the customer wants daily forecasts but hourly materialization refreshes, Option C is required to decouple them.
3. **ai_top_drivers in Genie Research:** Can Genie Research's multi-step reasoning invoke `ai_top_drivers` automatically when a user asks "why did revenue drop?" This would be a powerful integration but depends on Genie's tool selection.
