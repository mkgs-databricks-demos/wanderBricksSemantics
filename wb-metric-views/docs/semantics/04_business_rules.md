# WanderBricks Business Rules & Column Semantics

**Project:** wb-metric-views  
**Status:** Living document — update when new DQ flags or semantic rules are discovered  
**References:** `docs/research/02_data_model_analysis.md §7`, `docs/semantics/02_kpi_glossary.md`

These named rules **must be applied in every metric view YAML that touches the affected table or column**. Cite rules by ID in metric view `description:` fields so future authors understand the design decision.

---

## Section 1 — Revenue & Status Filter Rules

### RULE-01: Canonical Revenue Status Filter

> **All realized-revenue measures default to `status IN ('confirmed', 'completed')` unless explicitly reporting on gross demand or pending pipeline.**

| Measure | Status Filter | Use For |
| --- | --- | --- |
| `actual_revenue` | `status = 'completed'` | Realized / recognized revenue |
| `confirmed_revenue` | `status = 'confirmed'` | Committed bookings awaiting stay |
| `forecasted_revenue` | `status IN ('confirmed', 'pending')` | Revenue pipeline / forecast |
| `total_booking_value` (GBV) | All statuses | Gross demand signal only — NOT a revenue metric |

**Rationale:** 43.7% of WanderBricks bookings are `pending` (not yet host-accepted). Including pending in a default revenue measure overstates realized revenue by more than 4×.

**Valid status enum:** `pending` | `confirmed` | `cancelled` | `completed`

---

### RULE-02: Active Host Denominator

> **Always use `properties.host_id` as the active-host denominator — never `hosts.host_id` directly.**

| Source | Row Count | Meaning |
| --- | --- | --- |
| `COUNT(DISTINCT hosts.host_id)` | 19,384 | All registered hosts (80% have no listings) |
| `COUNT(DISTINCT properties.host_id)` | 3,817 | Hosts with active listings |

Using `hosts.host_id` as a denominator inflates the base by 5× and understates per-host productivity metrics by the same factor.

```sql
-- Correct: active hosts with listings
COUNT(DISTINCT p.host_id) FROM properties p

-- Wrong: all registered hosts (includes 80% with no properties)
COUNT(DISTINCT h.host_id) FROM hosts h
```

---

## Section 2 — Data Quality Rules (DQ Flags)

### RULE-03: Reviews — Non-Functional PK

> **Always use `COUNT(*)` for review volume. Never use `COUNT(DISTINCT review_id)`.**

`reviews.review_id` has 98,793 duplicates across 99,793 rows (only 1,000 distinct values). `COUNT(DISTINCT review_id)` returns ~1,000 regardless of any filter.

```sql
-- Correct
COUNT(*) FROM reviews WHERE is_deleted = false

-- Wrong: returns ~1,000 no matter what
COUNT(DISTINCT review_id) FROM reviews
```

---

### RULE-04: Reviews — Deleted Flag Filter

> **All rating and review volume measures must include `WHERE is_deleted = false`.**

476 rows have `is_deleted = true`. These rows have `rating IS NULL`. Including them in `AVG(rating)` returns NULL or suppresses values depending on the aggregator. Including them in `COUNT(*)` inflates volume by 0.48%.

```sql
-- Correct
AVG(rating) FROM reviews WHERE is_deleted = false

-- Wrong: includes NULL ratings from soft-deleted reviews
AVG(rating) FROM reviews
```

---

### RULE-05: Payments — Non-Functional PK

> **Always use `COUNT(*)` for payment volume. Never use `COUNT(DISTINCT payment_id)`.**

`payments.payment_id` has 4,465 duplicates. `SUM(amount)` is safe and reliable; only the count aggregate is affected.

---

### RULE-06: Page Views — Non-Functional PK

> **Always use `COUNT(*)` for page view volume. Never use `COUNT(DISTINCT view_id)`.**

`page_views.view_id` has 495,000 duplicates across 500,000 rows (only 5,000 distinct values). `COUNT(DISTINCT view_id)` returns ~5,000 regardless of filter.

---

### RULE-07: Customer Support Logs — STRING Date Column

> **Always `CAST(created_at AS TIMESTAMP)` when filtering or aggregating `customer_support_logs` by date.**

`customer_support_logs.created_at` is stored as `STRING`, not `TIMESTAMP` or `DATE`. Date range filters and `DATE_TRUNC` will silently fail or error without the cast.

```sql
-- Correct
WHERE CAST(created_at AS TIMESTAMP) >= '2024-01-01'

-- Wrong: string comparison, not date comparison
WHERE created_at >= '2024-01-01'
```

---

### RULE-08: Customer Support Logs — ARRAY Column

> **Do not aggregate `customer_support_logs.messages` directly. Create a flattened base view first.**

`messages` is `ARRAY<STRUCT<...>>`. A lateral explode (or `EXPLODE()`) is required before any message-level aggregation. This table is Tier 2 and blocked on a `v_support_ticket_summary` base view.

---

### RULE-09: Countries — String FK Join Fragility

> **Verify row counts on any join that uses `country` as a string FK key across tables.**

`countries.country` is a free-text string name (not an ISO code or numeric surrogate). Joins from `destinations`, `users`, `hosts`, and `employees` to `countries` via the country name string are vulnerable to silent row drops on casing or spelling mismatches.

```sql
-- Always verify: orphans should be 0
SELECT COUNT(*) FROM destinations d
LEFT JOIN countries c ON d.country = c.country
WHERE c.country IS NULL
```

Do this check for each table that joins on `country` before using that join in a metric view.

---

### RULE-10: Booking Updates — Exclude from Direct Metric Views

> **Do not use `booking_updates` as a direct metric view source table.**

`booking_updates.booking_update_id` has 7,943 duplicates. The table is a CDC stream representing booking state-change events (not a stable fact or dimension). It is suitable only for SCD / streaming pipeline patterns. Include in `docs/semantics/01_domain_context.md §3` under non-MV tables.

---

## Section 3 — Column Semantic Distinctions

### RULE-11: `base_price` vs Realized Rate — Asking Price ≠ ADR

> **`base_price` (asking price) and `avg_realized_rate` (earned rate) are fundamentally different metrics and must never share synonyms or be used interchangeably.**

| Column | Table | Meaning | Metric Name | Metric View |
| --- | --- | --- | --- | --- |
| `base_price` | `properties` | Host-set nightly asking price | `avg_base_price` | `mv_properties` |
| `total_amount / DATEDIFF(check_out, check_in)` | `bookings` | Revenue earned per booked night | `avg_realized_rate` | `mv_bookings` |

Genie synonyms for `avg_base_price` must NOT include "ADR" — ADR is the realized rate. "Average listing price" and "average asking price" are correct for `avg_base_price`.

---

### RULE-12: Booking Date vs Stay Date — Dual Date Dimensions

> **All booking-based metric views must expose both booking date and stay date as independent, independently-filterable dimensions.**

| Date | Column | Use |
| --- | --- | --- |
| **Booking date** | `bookings.created_at` | When was this reservation made? Demand trends, booking window, lead time |
| **Stay date** | `bookings.check_in` | When does the guest arrive? Revenue attribution, seasonal occupancy patterns |

Default Genie display: booking date. Revenue team typically requests stay-date attribution for period revenue totals. Both must be present as dimensions.

---

### RULE-13: Reviews — Reviewer Type Gap

> **`reviews` contains both guest-written and host-written reviews in a single table with no `reviewer_type` column. All rating averages reflect a mixed perspective.**

- Avg of 1.84 reviews per booking is consistent with both a guest review of the property AND a host review of the guest.
- `avg_property_rating` = mixed guest + host sentiment (cannot be separated without inference).
- **Heuristic for separation (not guaranteed):** If `reviews.user_id` matches `bookings.user_id` for the same `booking_id`, it is likely a guest review. If it does not match, it is likely a host review. This heuristic must be flagged in any metric view that applies it.
- Document this gap in every MV that surfaces a rating measure.

---

### RULE-14: `bookings.total_amount` vs `payments.amount` — Different Revenue Concepts

> **`bookings.total_amount` and `payments.amount` are not equivalent. Use the correct source based on reporting intent.**

| Column | Table | Meaning | Use For |
| --- | --- | --- | --- |
| `total_amount` | `bookings` | Agreed booking value at reservation time | Demand-side revenue reporting; booking-level analysis |
| `amount` | `payments` | Cash actually collected by payment processor | Cash-basis reporting; collections analysis |

Differences arise from: payment timing gaps, failed payments (1.0% of payments), refunded payments (7.4%), and potential split-payment rounding. For financial / cash-basis reporting, use `payments.amount`. For demand / booking-level reporting, use `bookings.total_amount`.

---

## Rule Reference Index

| Rule | Topic | Affected Table(s) |
| --- | --- | --- |
| RULE-01 | Revenue status filter (completed / confirmed / pending / GBV) | `bookings` |
| RULE-02 | Active host denominator (`properties.host_id` not `hosts.host_id`) | `hosts`, `properties` |
| RULE-03 | `reviews.review_id` non-functional PK — use `COUNT(*)` | `reviews` |
| RULE-04 | `reviews.is_deleted = false` filter required on all rating measures | `reviews` |
| RULE-05 | `payments.payment_id` non-functional PK — use `COUNT(*)` | `payments` |
| RULE-06 | `page_views.view_id` non-functional PK — use `COUNT(*)` | `page_views` |
| RULE-07 | `customer_support_logs.created_at` is STRING — always `CAST AS TIMESTAMP` | `customer_support_logs` |
| RULE-08 | `customer_support_logs.messages` is ARRAY — needs base view | `customer_support_logs` |
| RULE-09 | `countries` string FK join fragility — verify orphans first | `countries`, `destinations`, `users`, `hosts`, `employees` |
| RULE-10 | `booking_updates` is a CDC stream — exclude from direct MVs | `booking_updates` |
| RULE-11 | `base_price` (asking) ≠ `avg_realized_rate` (ADR) | `properties`, `bookings` |
| RULE-12 | Dual date dimensions — booking date AND stay date required | `bookings` |
| RULE-13 | `reviews` has no `reviewer_type` — rating is mixed guest+host | `reviews` |
| RULE-14 | `bookings.total_amount` ≠ `payments.amount` (different revenue concepts) | `bookings`, `payments` |

---

*When a new data quality issue or semantic distinction is discovered during Phase 3 YAML generation, add a new RULE-N entry here and cross-reference it in the affected metric view YAML `description:` field.*
