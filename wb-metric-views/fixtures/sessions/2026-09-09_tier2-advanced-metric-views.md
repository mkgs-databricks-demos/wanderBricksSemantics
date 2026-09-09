# Session: Tier 2, Advanced Metric Views, and NPS Patterns
**Date:** 2026-09-09

## Problems

- Phase 3 Tier 1 metric views were complete (6 MVs) but Tier 2 (SQL-as-source) and advanced patterns (window measures, AI functions) had not yet been authored.
- The reviews metric view lacked an NPS-style sentiment analysis dimension.
- No demand forecasting capability existed in the semantic layer.
- The booking funnel required a SQL-as-source pattern with a date-proximity join, which had not been validated against the sample data's temporal characteristics.

## Root Causes

- Tier 2 MVs require SQL subqueries as their source (bridge table flattening, CAST operations, ARRAY extraction) which the Tier 1 direct-table pattern doesn't support.
- The `page_views.timestamp` column contains values from 2025-09-04 while `bookings.created_at` ends at 2025-07-30 — no temporal overlap exists in the sample data, so the booking funnel attribution window produces 0 conversions. The YAML is structurally correct and would work with production data.
- `AI_FORECAST` is a preview feature not enabled on this workspace (`UNSUPPORTED_FEATURE.AI_FUNCTION_PREVIEW`). The mv_demand_forecast MV is registered but not queryable until the feature is enabled.

## Changes

### NPS Additions (2 MVs updated)
- **mv_reviews** — Added `sentiment_tier` dimension (CASE on rating: Promoter/Passive/Detractor) and `nps_score` measure composing `positive_review_rate` and `low_review_rate` via MEASURE().
- **mv_host_performance** — Added `host_quality_tier` dimension (CASE on hosts.rating) and `host_nps` measure using COUNT(DISTINCT) for host-level NPS with proper RULE-02 denominator.

### Tier 2 Metric Views (3 new files)
- **mv_booking_funnel** — SQL-as-source: LEFT JOIN page_views to bookings on property_id + user_id within 30-day attribution window. 4 dimensions, 6 measures (view-to-book rate, attributed revenue, avg views per booking). Data limitation noted above.
- **mv_amenity_adoption** — SQL-as-source: flattens property_amenities bridge to amenities dimension. Joins to properties for property-level dims. 4 dimensions, 5 measures (amenity density, luxury rate).
- **mv_customer_support** — SQL-as-source: CAST(created_at AS TIMESTAMP), SIZE(messages) for message count, array indexing for initial/final sentiment extraction. Joins to users. 6 dimensions, 5 measures (sentiment turnaround rate, angry ticket rate).

### Window Measures (mv_bookings extended)
- Added `booking_month` dimension (DATE_TRUNC for MoM ordering).
- Added 7 window measures: `t30d_bookings` (trailing 30-day), `cumulative_revenue` (running total), `monthly_bookings` + `prev_month_bookings` (MoM pair), `mom_booking_change` (composable % change), `monthly_revenue` + `prev_month_revenue` + `mom_revenue_change` (revenue MoM pair).
- Window measures follow the skill's sanctioned pattern: `range: current` + `offset: -1 month` for period comparison, `semiadditive: last` on all windowed measures, % change is NOT a window measure but composes two via MEASURE().

### AI-Enriched Metric View (1 new file)
- **mv_demand_forecast** — L200H Option A (inline TVF): `AI_FORECAST` as source with dual-value forecast (daily_bookings, daily_revenue), 95% prediction intervals, volatility measure. Registered but requires AI_FORECAST preview enablement.

### Registration
- Deployed bundle to dev, ran registration job. All 10 metric views registered as METRIC_VIEW type.
- 9/10 queryable; mv_demand_forecast pending AI_FORECAST feature flag.

## Decisions

- **NPS thresholds:** Promoter = 4-5 stars, Passive = 3, Detractor = 1-2. Chosen to align with existing `positive_review_rate` (>=4) and `low_review_rate` (<=2) thresholds for internal consistency.
- **Host NPS uses COUNT(DISTINCT):** Unlike review NPS (which counts rows), host NPS counts distinct hosts per tier because host_rating is a per-host attribute, not per-booking.
- **Window measures added directly to mv_bookings** (not a layered MV): simpler for the workshop, avoids registration ordering dependencies, and keeps all booking metrics in one view.
- **AI forecast uses Option A** (inline TVF, prototyping): per L200H guidance, appropriate for workshop demos. Production would graduate to Option B (materialization) or Option C (pipeline -> Delta -> MV).
- **Booking funnel kept despite 0 conversions:** The YAML is correct; the sample data limitation is documented. Real production data would have temporal overlap.

## Files Modified

- `fixtures/metric_views/mv_reviews.metric_view.yml` — Added sentiment_tier dimension, nps_score measure
- `fixtures/metric_views/mv_host_performance.metric_view.yml` — Added host_quality_tier dimension, host_promoter_count, host_detractor_count, host_nps measures
- `fixtures/metric_views/mv_bookings.metric_view.yml` — Added booking_month dimension, 7 window measures
- `fixtures/metric_views/mv_booking_funnel.metric_view.yml` — **New** (Tier 2)
- `fixtures/metric_views/mv_amenity_adoption.metric_view.yml` — **New** (Tier 2)
- `fixtures/metric_views/mv_customer_support.metric_view.yml` — **New** (Tier 2)
- `fixtures/metric_views/mv_demand_forecast.metric_view.yml` — **New** (Advanced/AI)

## Known Issues

- Stray `mv_booking_funnel.metric_view.yml` in bundle root (outside `fixtures/metric_views/`). Not picked up by registration job but should be deleted manually.
- `booking_month` dimension returns TIMESTAMP type (from DATE_TRUNC) rather than DATE. Functionally correct but could be wrapped in CAST(... AS DATE) for cleaner typing.
