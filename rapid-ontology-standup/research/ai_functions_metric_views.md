# Research — AI Functions in Metric View Definitions

## Using ai_forecast, ai_query, ai_top_drivers, and UC Functions with Metric Views (Sep 2026)

**Project:** Rapid Ontology Standup
**Location:** `docs/research/ai_functions_metric_views.md`
**Date:** 2026-09-01

---

### The Opportunity

Metric Views define governed KPIs as SQL. AI Functions are SQL-native. The combination enables a new class of **AI-enriched semantic definitions** — metric views that incorporate forecasts, ML model predictions, anomaly classifications, and metric change analysis alongside traditional aggregations, all governed through Unity Catalog.

---

### Key AI Functions Relevant to Metric Views

#### ai_forecast (Public Preview, v2 recommended)

A table-valued function for time-series forecasting. Supports multiple groups and up to 100 value columns per group. Returns `{value}_forecast`, `{value}_upper`, `{value}_lower` columns.

**Key capabilities:**
- Research-optimized time series foundation model (v2)
- Built-in holiday support with `holiday_region`
- External covariates (future and past-only) with `covariate_col`
- Non-negative forecasts with `positive_only`
- Prediction interval width (configurable confidence)
- Per-group parameter customization
- Requires Pro or Serverless SQL warehouse

**Critical design principle:** `ai_forecast` is a table-valued function that generates rows — it is NOT an aggregate function. It cannot be used directly inside a metric view `measures` block. Instead, **materialize the forecast output to a Delta table**, then build a metric view on top of that table.

#### ai_query (GA)

A general-purpose function that invokes any Model Serving endpoint from SQL. Supports foundation models, custom ML models, and external model endpoints.

**Key capabilities:**
- Query custom ML models: `ai_query('churn-model', request => struct(*), returnType => 'FLOAT')`
- Query foundation models for text enrichment
- Wrappable in Unity Catalog SQL functions for reuse and governance
- `failOnError => false` for graceful error handling in batch

**Critical design principle:** `ai_query` invokes an endpoint per row. Do NOT call it inside a metric view measure or inside an interactive dashboard query. Instead, **precompute the enrichment in a batch job** and expose the results through a metric view.

#### ai_top_drivers (Beta)

A table-valued function for contribution analysis. Ranks dimension values that contribute most to a metric change between a control group and a test group.

**Key capabilities:**
- Compares two time periods or cohorts
- Auto-selects top 20 correlated dimensions if not specified
- Supports sum, avg, count, min, max aggregations
- Returns ranked segments with change magnitude

**Design principle:** Like `ai_forecast`, this is a table-valued function — not an aggregate. Use it in analysis notebooks or scheduled jobs, not inside metric view definitions.

---

### Architecture: The Precompute-Then-Govern Pattern

The fundamental pattern for combining AI Functions with Metric Views:

```
Source data (Delta tables)
   ↓
AI Function pipeline (scheduled Lakeflow Job)
├── ai_forecast() → forecast Delta table
├── ai_query('custom-model') → prediction Delta table
├── ai_top_drivers() → driver analysis Delta table
└── UC Function wrapping ai_query → explanation Delta table
   ↓
Conformed actuals + predictions table
   ↓
Metric View (governed KPI definitions)
   ↓
Dashboards, Genie Agents, notebooks, alerts
```

**Why precompute:**
- AI Functions have latency (endpoint calls, model inference)
- Repeated calls in interactive queries are expensive and unpredictable
- Results should be deterministic and auditable (same forecast for the same run)
- Cost control — batch inference is cheaper than per-query inference
- Metric views should be fast — they define KPIs, not invoke models

---

### Pattern 1: Forecast Metrics via ai_forecast

**Pipeline:** Materialize forecasts to a Delta table on a schedule.

```sql
CREATE OR REPLACE TABLE prod.forecasting.demand_forecast AS
SELECT * FROM AI_FORECAST(
  TABLE(prod.forecasting.daily_demand),
  horizon => date_add(current_date(), 30),
  time_col => 'ds',
  value_col => 'demand',
  group_col => ARRAY('product_id', 'region'),
  prediction_interval_width => 0.95,
  global_floor => 0
);
```

**Conformed table:** Union actuals and forecasts with a `record_type` discriminator.

**Metric View:** Define governed measures over the conformed table.

```yaml
version: 1.1
source: prod.forecasting.demand_actuals_forecasts
measures:
  - name: Actual Demand
    expr: SUM(actual_demand)
  - name: Forecast Demand
    expr: SUM(forecast_demand)
  - name: Forecast Range
    expr: MEASURE(Forecast Upper Bound) - MEASURE(Forecast Lower Bound)
  - name: Forecast Volatility Ratio
    expr: MEASURE(Forecast Range) / NULLIF(MEASURE(Forecast Demand), 0)
    format: { type: percentage }
```

**Composability:** Build a risk metric view on top of the forecast metric view.

---

### Pattern 2: Custom ML Predictions via ai_query + UC Function

**Step 1:** Register the ML model in Unity Catalog and deploy to Model Serving.

**Step 2:** Wrap `ai_query` in a UC SQL function for governance and reuse.

```sql
CREATE OR REPLACE FUNCTION prod.ai.predict_churn_risk(
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

**Step 3:** Batch-score in a scheduled job, writing to a prediction table.

```sql
CREATE OR REPLACE TABLE prod.ml.churn_predictions AS
SELECT
  customer_id,
  prod.ai.predict_churn_risk(customer_id, tenure_months, monthly_spend, support_tickets) AS churn_probability,
  current_timestamp() AS scored_at
FROM prod.gold.customer_features;
```

**Step 4:** Build a metric view over the prediction table.

```yaml
version: 1.1
source: prod.ml.churn_predictions
joins:
  - name: customers
    source: prod.gold.customers
    on: source.customer_id = customers.customer_id
measures:
  - name: Avg Churn Risk
    expr: AVG(churn_probability)
    format: { type: percentage }
  - name: High Risk Customers
    expr: COUNT(DISTINCT CASE WHEN churn_probability > 0.7 THEN customer_id END)
  - name: At Risk Revenue
    expr: SUM(CASE WHEN churn_probability > 0.7 THEN customers.monthly_spend ELSE 0 END)
    format: { type: currency, currency_code: USD }
```

---

### Pattern 3: Metric Change Analysis via ai_top_drivers

**Use case:** "Why did revenue drop in March?" — automated contribution analysis.

**Pipeline:** Run `ai_top_drivers` in a scheduled job comparing the current period to the prior period.

```sql
SELECT * FROM ai_top_drivers(
  input => TABLE(
    SELECT region, product, channel, revenue,
      CASE WHEN month = '2026-03' THEN true ELSE false END AS is_test
    FROM prod.gold.monthly_revenue
    WHERE month IN ('2026-02', '2026-03')
  ),
  metric => 'revenue',
  is_test => 'is_test',
  dimensions => ARRAY('region', 'product', 'channel'),
  aggregation => 'sum'
)
```

**Output:** Ranked dimension values with their contribution to the metric change. Persist to a Delta table for dashboard consumption.

---

### What NOT to Do

| Anti-pattern | Why it's bad |
|---|---|
| `ai_forecast()` inside a metric view source | TVF generates rows — not compatible with MV aggregation semantics |
| `ai_query()` inside a metric view measure | Invokes an endpoint per query execution — latency, cost, non-determinism |
| `ai_top_drivers()` inside a metric view | TVF — same issue as ai_forecast |
| Calling a UC function wrapping `ai_query` in a dashboard dataset | Per-render endpoint calls — unpredictable latency and cost |
| Skipping the precompute step for "simplicity" | Trades governed, auditable results for fragile, expensive, non-reproducible ones |

---

### UC Function Governance

UC SQL functions wrapping `ai_query` are governed objects:
- **Permissions:** `EXECUTE` grant required; `CREATE FUNCTION` requires catalog/schema usage
- **Lineage:** Functions appear in UC lineage graphs
- **Audit:** Function invocations are logged
- **Sharing:** Functions can be shared across teams via UC grants
- **Versioning:** Use function naming conventions (e.g., `predict_churn_risk_v2`) or schema-level versioning

---

### Sources

- ai_forecast function: https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_forecast
- ai_query function: https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_query
- ai_top_drivers function: https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_top_drivers
- Use ai_query: https://docs.databricks.com/aws/en/large-language-models/ai-query
- UC SQL and Python UDFs: https://docs.databricks.com/aws/en/udf/unity-catalog
- Metric View advanced techniques: https://docs.databricks.com/aws/en/uc-semantics/metric-views/advanced-techniques
- Model Serving endpoints: https://docs.databricks.com/aws/en/machine-learning/model-serving
- AI Functions overview: https://docs.databricks.com/aws/en/large-language-models/ai-functions
