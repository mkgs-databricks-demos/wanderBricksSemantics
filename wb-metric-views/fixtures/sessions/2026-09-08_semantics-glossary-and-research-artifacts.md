# Session: Semantics Glossary, Research Artifacts, and Phase 2 Data Model Analysis
**Date:** 2026-09-08

## Problems
- No structured business domain context, KPI definitions, or data quality rules existed for the WanderBricks semantic layer — metric view YAML `description:` and `synonyms:` fields would be inconsistent without a canonical reference.
- No data model analysis had been written down — the 16-table `samples.wanderbricks` schema had not been profiled for PK integrity, FK map, row counts, or metric view suitability.
- Industry KPI definitions (ADR, RevPAR, ALOS, NPS, etc.) were not mapped to WanderBricks-specific formulas, so it was unclear which standard KPIs were achievable and which were not.

## Root Causes
- N/A — no failures. This session was planned exploratory and documentation work (Phase 1 research + Phase 2 data model analysis + Phase 2.5 semantic glossary authoring).

## Changes

### Phase 1 — Industry Domain Research
- Executed 5-angle web search covering: core hotel KPIs (STR, AHLA), vacation rental / OTA KPIs (AirDNA, Airbnb, Key Data), hospitality analytics dimensions (Databricks, Snowflake), booking funnel metrics (PhocusWire, Skift), and guest satisfaction analytics (ReviewPro, Medallia, Revinate).
- Created [`docs/research/01_industry_domain_research.md`](#file-58077670920113) — full synthesis of hospitality/STR industry KPI research with WanderBricks applicability notes.

### Phase 2 — Data Model Analysis
- Profiled all 16 tables in `samples.wanderbricks` via SQL queries: row counts, PK uniqueness audit, FK referential integrity checks, join cardinality, and key business metrics.
- Identified 11 data quality flags (DQ-1 through DQ-11) including non-functional PKs on `reviews`, `payments`, `page_views`; `booking_updates` as a CDC stream; `customer_support_logs.created_at` as STRING; `countries` string FK fragility.
- Created [`docs/research/02_data_model_analysis.md`](#file-58077670920112) — full 16-table analysis with PK audit, FK map, hub-and-spoke ER diagram, business metrics summary, DQ flags, metric view candidates (Tier 1 + Tier 2), and known semantic gaps.

### Phase 2.5 — Semantics Glossary (this session)
- Reviewed all research output and identified 4 semantic subdocuments needed (not one monolithic file).
- Created `docs/semantics/` directory and four files:
  - [`01_domain_context.md`](#file-58077670920120) — WanderBricks business type (STR marketplace, not hotel), subdomain taxonomy, 10 non-achievable KPIs with reasons, Genie semantic gap guidance, reporting cadences.
  - [`02_kpi_glossary.md`](#file-58077670920121) — 30 KPI entries across 6 subdomains (Supply & Inventory, Booking & Demand, Revenue & Payments, Guest Experience, Host Performance, Booking Funnel), each with definition, WanderBricks SQL formula, Genie synonyms, target metric view, and RULE-N cross-references.
  - [`03_dimension_hierarchies.md`](#file-58077670920122) — 5 dimension hierarchies (Geography, Time dual-date pattern, Guest Segmentation, Property Attributes, Channel/Source) with exact column paths and caveats.
  - [`04_business_rules.md`](#file-58077670920123) — 14 named rules (RULE-01 through RULE-14) covering revenue status filters, all 11 DQ flags promoted to named rules, and column semantic distinctions (base_price vs ADR, booking date vs stay date, total_amount vs payments.amount).
- Committed and pushed all 8 files (6 new + 2 pre-existing modified) to `mg-genie-care-metric-views` with commit `docs: add semantics glossary and research artifacts for wb-metric-views`.

## Decisions
- **4-file semantics structure** over a single monolithic document — each file serves a different consumer: `02_kpi_glossary.md` (YAML authors), `03_dimension_hierarchies.md` (dimensions block design), `04_business_rules.md` (Genie default safety), `01_domain_context.md` (onboarding/framing).
- **14 named rules** (RULE-01..14) to be cited by ID in every metric view YAML `description:` field that touches an affected table.
- **Dual-date pattern** (booking date vs stay date) documented as mandatory for all booking-based metric views — not optional.
- **Non-achievable KPIs** (RevPAR, NPS, Occupancy Rate, GOPPAR, TRevPAR) explicitly documented with Genie response guidance rather than silently excluded.
- **Phase 3 order confirmed:** mv_bookings first → extend mv_properties → mv_payments → mv_reviews → mv_host_performance → mv_page_views.
- **Stray workspace files to clean up:** assetIds `58077670920109` and `58077670920118` (doubled-path artifacts from `createAsset` calls that used full workspace path instead of relative path) — exist only as workspace objects, not in git.

## Files Modified
- [`docs/research/01_industry_domain_research.md`](#file-58077670920113) — created
- [`docs/research/02_data_model_analysis.md`](#file-58077670920112) — created
- [`docs/semantics/01_domain_context.md`](#file-58077670920120) — created
- [`docs/semantics/02_kpi_glossary.md`](#file-58077670920121) — created
- [`docs/semantics/03_dimension_hierarchies.md`](#file-58077670920122) — created
- [`docs/semantics/04_business_rules.md`](#file-58077670920123) — created
- [`README.md`](#file-58077670920028) — updated structure tree and documentation section
- [`project_memory.md`](#file-58077670920036) — updated with docs/ structure, current phase, metric view candidates
- [`fixtures/sessions/INDEX.md`](#file-58077670920035) — updated
