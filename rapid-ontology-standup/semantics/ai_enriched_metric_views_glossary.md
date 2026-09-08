# Semantics — AI-Enriched Metric Views Glossary

## UC Page Candidates for AI Functions, Forecasting, and ML-Enriched Semantic Definitions

**Project:** Rapid Ontology Standup
**Location:** `docs/semantics/ai_enriched_metric_views_glossary.md`
**Date:** 2026-09-01
**Domain:** Databricks Platform
**Subdomain:** AI Functions, Forecasting, ML Integration, Semantic Layer

Each entry is structured for UC Pages: definition, business context, data usage, related terms, source.

---

### ai_forecast

- **Definition:** A built-in SQL table-valued function for time-series forecasting. Accepts a table of historical observations and produces forecasted values with upper and lower prediction intervals. Supports multiple groups, up to 100 value columns per group, configurable prediction intervals, holiday regions, external covariates, and non-negative constraints. Version 2 (recommended) uses a research-optimized time series foundation model.
- **Business Context:** Enables governed forecast KPIs in the semantic layer — but indirectly. Because `ai_forecast` is a table-valued function (it generates rows, not aggregates), it cannot be used inside a metric view measure. The correct pattern is to materialize forecast output to a Delta table on a schedule, then build a metric view on top of that table. This keeps forecasts deterministic, auditable, and fast.
- **Data Usage:** Called as `AI_FORECAST(TABLE(input), horizon => ..., time_col => ..., value_col => ...)`. Returns `{value}_forecast`, `{value}_upper`, `{value}_lower` columns. Requires Pro or Serverless SQL warehouse. Version 2 requires the Predictive AI Functions preview.
- **Related Terms:** Metric View, Window Measure, Materialization, Lakeflow Job, Time Series
- **Source:** https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_forecast

---

### ai_query

- **Definition:** A general-purpose built-in SQL function that invokes any Model Serving endpoint from SQL or Python. Supports foundation models (LLMs), custom ML models, and external model endpoints. Returns structured or unstructured results with configurable return types and error handling.
- **Business Context:** The bridge between ML models and the semantic layer. By wrapping `ai_query` in a Unity Catalog SQL function, teams create governed, reusable model invocations that can be shared, permissioned, and audited. The key design rule: precompute predictions in a batch job and expose results through a metric view — never call `ai_query` inside an interactive dashboard query or metric view measure.
- **Data Usage:** Called as `ai_query(endpoint, request, returnType => ...)`. Supports `named_struct` for structured input, `failOnError => false` for graceful batch processing. Wrappable in UC SQL functions via `CREATE FUNCTION ... RETURN ai_query(...)`.
- **Related Terms:** Model Serving, UC Function, Metric View, Batch Inference, Unity AI Gateway
- **Source:** https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_query

---

### ai_top_drivers

- **Definition:** A built-in SQL table-valued function (Beta) for contribution analysis. Ranks dimension values — or pairs of values — that contribute most to a change in a metric between a control group and a test group. Supports sum, avg, count, min, max aggregations and auto-selects top 20 correlated dimensions if not specified.
- **Business Context:** Answers "why did this metric change?" automatically. Useful for root-cause analysis on forecast misses, revenue drops, or cost spikes. Like `ai_forecast`, it's a table-valued function — use it in analysis notebooks or scheduled jobs, not inside metric view definitions. Persist results to a Delta table for dashboard consumption.
- **Data Usage:** Called as `ai_top_drivers(input => TABLE(...), metric => ..., is_test => ..., dimensions => ...)`. Returns ranked segments with change magnitude. Requires a boolean `is_test` column to distinguish control from test periods.
- **Related Terms:** Metric View, Contribution Analysis, Root Cause Analysis, Lakeflow Job
- **Source:** https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_top_drivers

---

### UC SQL Function (wrapping ai_query)

- **Definition:** A Unity Catalog SQL function that wraps an `ai_query` call to a Model Serving endpoint, creating a governed, reusable, permissioned interface to an ML model. Created via `CREATE FUNCTION ... RETURNS ... RETURN ai_query(...)`. Governed by UC privileges (`EXECUTE` to invoke, `CREATE FUNCTION` to create).
- **Business Context:** The governance layer for ML model invocations. Without a UC function wrapper, `ai_query` calls are ad-hoc — no permission control, no lineage, no audit trail. With a UC function, the model invocation becomes a first-class catalog object that can be shared across teams, versioned, and monitored. In the Rapid Ontology Standup, UC functions are the recommended way to expose custom ML models to the semantic layer.
- **Data Usage:** Functions appear in UC lineage graphs. Invocations are logged for audit. Can be called from SQL, notebooks, Lakeflow pipelines, and Genie Agents (as trusted assets). Use naming conventions for versioning (e.g., `predict_churn_risk_v2`).
- **Related Terms:** ai_query, Model Serving, Unity Catalog, Metric View, Genie Agent Trusted Asset
- **Source:** https://docs.databricks.com/aws/en/udf/unity-catalog

---

### Precompute-Then-Govern Pattern

- **Definition:** The architectural pattern for combining AI Functions with Metric Views: run AI Functions (forecasts, predictions, classifications, explanations) in a scheduled batch pipeline, materialize the results to Delta tables, then build governed Metric Views on top of those tables. The AI invocation happens in the pipeline; the Metric View defines the KPI.
- **Business Context:** This pattern exists because AI Functions have latency, cost, and non-determinism that are incompatible with interactive query expectations. A metric view should return in seconds, not wait for a model endpoint. By precomputing, the results are deterministic (same forecast for the same run), auditable (stored in Delta with timestamps and run IDs), and fast (metric view queries hit a table, not an endpoint).
- **Data Usage:** Pipeline: source data → AI Function → Delta table → Metric View. The Delta table is the contract between the AI pipeline and the semantic layer. Include `forecast_run_id`, `model_version`, `generated_at` for reproducibility.
- **Related Terms:** ai_forecast, ai_query, Metric View, Lakeflow Job, Delta Table, Materialization
- **Source:** Internal architecture pattern (Rapid Ontology Standup L200-H)

---

### Model Serving Endpoint

- **Definition:** A Databricks-managed REST endpoint that serves ML models for real-time or batch inference. Supports MLflow models registered in Unity Catalog, foundation models via Foundation Model APIs, and external model providers via Unity AI Gateway. Queryable via REST API, MLflow Deployment API, `ai_query()`, or UC SQL functions.
- **Business Context:** The runtime for custom ML models that feed the semantic layer. A churn model, demand forecaster, or risk classifier is registered in UC, deployed to a Model Serving endpoint, wrapped in a UC SQL function, and invoked in a batch pipeline. The endpoint handles scaling, versioning, and monitoring; the UC function handles governance.
- **Data Usage:** Endpoints are created from UC-registered models. Support autoscaling, GPU/CPU compute, and traffic splitting for A/B testing. Monitored via endpoint logs, OpenTelemetry, and AI Gateway inference tables. Governed by UC permissions on the registered model.
- **Related Terms:** ai_query, UC Function, MLflow, Unity Catalog, Unity AI Gateway
- **Source:** https://docs.databricks.com/aws/en/machine-learning/model-serving

---

### Tagging Strategy & Implementation Priority

| Term | Priority | Workstream |
|---|---|---|
| ai_forecast | **P0** — Core forecasting capability | L200-H pipeline design |
| ai_query | **P0** — ML model invocation | L200-H UC function pattern |
| ai_top_drivers | **P1** — Metric change analysis | L200-H analysis enrichment |
| UC SQL Function (ai_query wrapper) | **P0** — Governance layer | L200-H function design |
| Precompute-Then-Govern Pattern | **P0** — Architecture principle | L200-H system design |
| Model Serving Endpoint | **P0** — ML runtime | L200-H infrastructure |
