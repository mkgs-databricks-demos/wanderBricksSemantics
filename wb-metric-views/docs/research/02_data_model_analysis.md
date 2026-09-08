# Phase 2 — WanderBricks Data Model Analysis

**Author:** Genie Code (wb-metric-views, L200-A Phase 2)  
**Date:** 2026-09-08  
**Schema:** `samples.wanderbricks`  
**Status:** Initial investigation complete — ready for Phase 3 (YAML generation)  
**References:** L100 Rapid Ontology Standup, L200-A Metric View Standup  
**Next artifact:** `fixtures/metric_views/*.metric_view.yml`

---

## 1. Schema Inventory

16 tables total. Classified by analytical role.

| Table | Rows | Role | Grain |
| --- | --- | --- | --- |
| `bookings` | 72,247 | **Fact — Core** | One row per booking reservation |
| `payments` | 49,638 | **Fact — Transaction** | One row per payment event |
| `reviews` | 99,793 | **Fact — Event** | One row per review submission |
| `booking_updates` | 83,068 | **Fact — CDC Stream** | One row per booking state-change event |
| `page_views` | 500,000 | **Fact — Behavioral** | One row per property page view |
| `clickstream` | 100,000 | **Fact — Behavioral** | One row per site interaction event |
| `properties` | 18,163 | **Dimension — Core** | One row per property listing |
| `users` | 124,509 | **Dimension — Core** | One row per registered user |
| `hosts` | 19,384 | **Dimension — Core** | One row per host |
| `destinations` | 42 | **Dimension — Lookup** | One row per destination market |
| `countries` | 168 | **Dimension — Lookup** | One row per country |
| `amenities` | 38 | **Dimension — Reference** | One row per amenity type |
| `property_amenities` | 118,108 | **Bridge (M:M)** | Composite PK `(property_id, amenity_id)` |
| `property_images` | 54,186 | **Child — Attribute** | One row per listing image |
| `employees` | 73,006 | **Child — Operational** | One row per host employee |
| `customer_support_logs` | 1,900 | **Fact — Operational** | One row per support ticket |

---

## 2. Primary Key Audit

| Table | Declared PK | Type | Actually Unique? | Notes |
| --- | --- | --- | --- | --- |
| `bookings` | `booking_id` | bigint | ✅ Yes | Clean |
| `users` | `user_id` | bigint | ✅ Yes | Clean |
| `hosts` | `host_id` | bigint | ✅ Yes | Clean |
| `properties` | `property_id` | bigint | ✅ Yes | Clean |
| `destinations` | `destination_id` | bigint | ✅ Yes | Clean |
| `countries` | `country` | **string** | ✅ Yes | PK is the country name, not a code — fragile for joins |
| `amenities` | `amenity_id` | bigint | ✅ Yes | Clean |
| `property_images` | `image_id` | bigint | ✅ Yes | Clean |
| `employees` | `employee_id` | bigint | ✅ Yes | Clean |
| `customer_support_logs` | `ticket_id` | **string** | ✅ Yes | String PK — no numeric surrogate |
| `property_amenities` | `(property_id, amenity_id)` | bigint×bigint | ✅ Yes | Only composite PK in schema |
| `payments` | `payment_id` | bigint | ❌ **4,465 dupes** | PK non-functional — use `COUNT(*)`, never `COUNT(DISTINCT payment_id)` |
| `booking_updates` | `booking_update_id` | bigint | ❌ **7,943 dupes** | CDC stream table; not suitable as direct MV source |
| `reviews` | `review_id` | bigint | ❌ **98,793 dupes** | Only 1,000 distinct values across 99,793 rows — PK is meaningless |
| `page_views` | `view_id` | bigint | ❌ **495,000 dupes** | Only 5,000 distinct values across 500,000 rows — event log only |
| `clickstream` | *(none declared)* | — | N/A | Pure event log, no surrogate key |

> **Rule for metric views:** Use `COUNT(*)` (not `COUNT(DISTINCT <pk>)`) for `reviews`, `payments`, `page_views`, and `booking_updates`. The declared PKs on these four tables are non-functional.

---

## 3. Foreign Key Map & Referential Integrity

All orphan counts verified with LEFT JOIN checks.

```
countries (168)
    ← destinations.country          [string match — potential collision risk]
    ← users.country                 [string match — potential collision risk]
    ← hosts.country                 [string match — potential collision risk]
    ← employees.country             [string match — potential collision risk]

destinations (42)
    ← properties.destination_id     [0 orphans ✅]

hosts (19,384)
    ← properties.host_id            [0 orphans ✅]  (~80% of hosts have NO properties)
    ← employees.host_id             [all 19,384 hosts have employees]

properties (18,163)
    ← bookings.property_id          [0 orphans ✅]
    ← reviews.property_id           [0 orphans ✅]
    ← page_views.property_id        [all 18,163 properties appear]
    ← property_amenities            [all 18,163 properties covered]
    ← property_images               [all 18,163 properties covered]
    ← clickstream.property_id

users (124,509)
    ← bookings.user_id              [0 orphans ✅]
    ← reviews.user_id               [0 orphans ✅]
    ← page_views.user_id
    ← clickstream.user_id
    ← customer_support_logs.user_id

bookings (72,247)
    ← payments.booking_id           [8 orphaned payments — negligible]
    ← reviews.booking_id            [0 orphans ✅]
    ← booking_updates.booking_id

ameities (38)
    ← property_amenities.amenity_id [all 38 amenities in use]
```

**Countries join risk:** The `country` column is a free-text string FK across `users`, `hosts`, `employees`, and `destinations`. Any casing or spelling variation between tables will silently drop rows on join. Always verify before building cross-domain geographic aggregations.

---

## 4. Join Cardinality Summary

| Relationship | Cardinality | Notes |
| --- | --- | --- |
| `bookings` → `properties` | Many:1 | 97.6% of properties have been booked |
| `bookings` → `users` | Many:1 | Clean; 0 nulls on `user_id` |
| `payments` → `bookings` | ~1.08:1 | Mostly 1 payment per booking; some split payments |
| `reviews` → `bookings` | ~1.84:1 | Both guest + host reviews share same table with no reviewer_type column |
| `properties` → `hosts` | Many:1 | 3,817 hosts have properties (only 19.7% of all hosts) |
| `properties` → `destinations` | Many:1 | All 42 destinations in use; avg ~432 properties/destination |
| `property_amenities` → `properties` | ~6.5 amenities per property | All properties covered |
| `property_images` → `properties` | ~3 images per property | All properties covered |
| `employees` → `hosts` | ~3.8 employees per host | All hosts have employees |
| `booking_updates` → `bookings` | Variable | 66% of bookings have been updated at least once |
| `page_views` → `properties` | High-volume | 500K views across 18,163 properties |

---

## 5. Hub-and-Spoke Entity Relationship (Snowflake Schema)

```
                        [countries]
                             ↑  (string name FK)
     [employees]         [destinations]
          ↑                   ↑
       [hosts] ←──── [properties] ←── [property_images]
                          ↑      ↑
            [property_amenities] └── [page_views]
                  ↑                  [clickstream]
            [amenities]
                          ↑
  [users] ───────────── [BOOKINGS]  ← Central Fact
                          │   │
                     [reviews] [booking_updates]
                          │
                     [payments]

  [customer_support_logs] ←── users
```

`bookings` is the **central fact hub**. Three secondary fact tables (`payments`, `reviews`, `booking_updates`) hang directly off `bookings.booking_id`. Behavioral/event tables (`page_views`, `clickstream`) connect via `property_id` and `user_id` but have **no direct equi-join to bookings** — a conversion funnel join requires date-proximity logic, not a simple key join.

---

## 6. Key Business Metrics from Data Profiling

### Bookings
- **Date range:** December 2022 – July 2025 (2.5+ years of history)
- **Status mix:** pending 43.7% · confirmed 24.8% · cancelled 21.2% · completed 10.3%
- The `pending` majority is notable — may reflect recency artifact or business process issue
- Revenue measures should default to `status IN ('confirmed', 'completed')` unless pending revenue is explicitly included

### Supply / Properties
- **Property types:** Urban Year-Round 51% · Summer Getaway 39% · Historical Place 9% · Ski Resort 1%
- **Average prices:** Ski Resort $266 > Summer Getaway $199 > Urban $173 > Historical $147
- **Top destinations:** Phuket, Mallorca, Gold Coast, Paris, Abu Dhabi
- All properties have images (~3 avg) and amenities (~6.5 avg)

### Payments
- 63.6% of bookings have a payment record (gap = pending/cancelled bookings)
- **Status:** completed 91.5% · refunded 7.4% · failed 1.0%
- **Methods:** ~20% each across paypal, credit_card, apple_pay, bank_transfer, google_pay

### Reviews
- 75.2% of bookings have at least one review (54,302 / 72,247)
- Average 1.84 reviews per booking — suggests both guest and host reviews exist but there is **no `reviewer_type` column**
- **Average rating:** 3.01 / 5.0 (non-deleted reviews only)
- Soft-delete rate: 0.48% (`is_deleted = true`)

### Users
- **Type split:** business 50.2% · individual 49.8% (nearly even)
- `company_name` populated for business users only (sparse column)

### Hosts
- **80% of hosts have no listed property** — use `properties.host_id` as the denominator for host-level metrics, not `hosts.host_id`

### Amenity Categories
- Basic 12 · Outdoor 9 · Luxury 9 · Safety 8

---

## 7. Data Quality Flags

Document these in every metric view that touches the affected tables.

| # | Table | Issue | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| DQ-1 | `reviews` | `review_id` has 98,793 duplicates (1,000 distinct in 99,793 rows) | PK is non-functional | Always use `COUNT(*)` for review volume |
| DQ-2 | `reviews` | No `reviewer_type` column | Cannot distinguish guest vs host reviews | Flag as semantic gap; future: create base view with `booking_id` + `user_id` heuristic |
| DQ-3 | `reviews` | `rating IS NULL` for 476 rows (same rows as `is_deleted = true`) | Ratings must filter `WHERE is_deleted = false` | Add filter to all rating measures |
| DQ-4 | `payments` | `payment_id` has 4,465 duplicates | PK non-functional | Use `COUNT(*)` for payment volume; `SUM(amount)` is safe |
| DQ-5 | `payments` | 8 payments referencing non-existent `booking_id` | Negligible (0.016%) | No action required for MV purposes |
| DQ-6 | `page_views` | `view_id` has 495,000 duplicates (5,000 distinct in 500,000 rows) | PK non-functional | Use `COUNT(*)` exclusively for view volume |
| DQ-7 | `booking_updates` | `booking_update_id` has 7,943 duplicates; CDC stream | Not suitable as direct MV source | Exclude from direct MVs; use only for SCD/streaming pipelines |
| DQ-8 | `customer_support_logs` | `created_at` is `STRING` type (not timestamp/date) | Cannot use in date filters without cast | Always `CAST(created_at AS TIMESTAMP)` in any MV |
| DQ-9 | `customer_support_logs` | `messages` is `ARRAY<STRUCT>` | Cannot aggregate directly | Create flattened base view first |
| DQ-10 | `countries` (all tables) | `country` FK is a free-text string name | Silent join drops on casing/spelling mismatch | Verify join counts before using in any MV |
| DQ-11 | `bookings` | 43.7% of bookings are `pending` | Revenue/volume measures may be misleading without status filter | Document default filter; parameterize status scope |

---

## 8. Metric View Candidates

Ordered by readiness and business value. Follows L200-A design rule: one fact source per MV, LEFT OUTER JOINs to dimension tables.

### Tier 1 — Immediately Buildable

Single fact source, clean key joins, no pre-processing required.

| MV Name | Source Fact | Key Dimension Joins | Primary KPIs |
| --- | --- | --- | --- |
| `mv_properties` *(extend existing)* | `properties` | `destinations`, `hosts` | total_properties, avg_base_price, total_guest_capacity + extend with destination/host dims |
| `mv_bookings` | `bookings` | `properties`, `users`, `destinations` | total_bookings, confirmed_bookings, completed_bookings, cancelled_bookings, cancellation_rate, avg_length_of_stay, total_booking_value, avg_booking_value, guests_served |
| `mv_payments` | `payments` | `bookings` (bridge only) | total_revenue, total_refunds, refund_rate, avg_transaction_value, payment_method_mix |
| `mv_reviews` | `reviews` (+ `WHERE is_deleted = false`) | `bookings`, `properties`, `destinations` | avg_property_rating, total_reviews, review_rate, review_volume |
| `mv_host_performance` | `bookings` | `properties` → `hosts` | bookings_per_host, revenue_per_host, active_host_count, avg_host_portfolio_size |
| `mv_page_views` | `page_views` | `properties`, `destinations` | total_views, views_per_property, device_type_mix, referrer_mix |

### Tier 2 — Requires Base View First

| MV Name | Blocker | Base View Needed |
| --- | --- | --- |
| `mv_booking_funnel` (page views → bookings conversion) | No direct equi-join between `page_views` and `bookings`; requires date-proximity session logic | `v_property_user_sessions` |
| `mv_customer_support` | `messages` is ARRAY<STRUCT>; `created_at` is STRING | `v_support_ticket_summary` (flattened) |
| `mv_amenity_adoption` | M:M bridge through `property_amenities` | `v_property_amenity_flat` |

### Tables to Exclude from Direct MVs

| Table | Reason |
| --- | --- |
| `booking_updates` | CDC stream with duplicate PKs; use only for SCD/streaming pipelines |
| `property_images` | No KPI grain; reference asset only |
| `employees` | Operational roster; no booking-level KPI linkage |
| `clickstream` | No PK, event log only; suitable as source for a behavioral base view |

---

## 9. Known Semantic Gaps

These are business metrics commonly expected in hospitality analytics that the current schema cannot support directly:

| Gap | Description | Workaround |
| --- | --- | --- |
| **Occupancy rate** | No `available_nights` table or calendar — cannot calculate nights available vs. booked | Would require a date-spine + property availability table |
| **Reviewer type** | `reviews` has no `reviewer_type` (guest vs host) column | Heuristic: join on `user_id` vs booking `user_id`; flag in MV comment |
| **Net revenue** | No split between platform fee and host payout in `payments.amount` | `total_amount` on bookings vs `amount` on payments may serve as proxy |
| **Cancellation policy** | No cancellation policy or fee structure on properties or bookings | Cannot compute penalty-adjusted revenue |
| **Seasonal pricing** | `base_price` is a flat rate; no dynamic pricing or seasonal rate table | Cannot compute pricing yield or RevPAR |

---

## 10. Recommended Next Steps (Phase 3)

Priority order for YAML generation:

1. **`mv_bookings`** — Highest value; unlocks the core revenue and booking-performance story for the Genie Agent. Start here.
2. **Extend `mv_properties`** — Add `destinations` and `hosts` joins; the current fixture only covers the properties table itself.
3. **`mv_payments`** — Completes the revenue picture alongside `mv_bookings`.
4. **`mv_reviews`** — Guest satisfaction KPIs; straightforward once `is_deleted` filter is documented.
5. **`mv_host_performance`** — Derived from `bookings` → `properties` → `hosts`; no new source table.
6. **`mv_page_views`** — Demand-signal metrics; behavioral layer for the Genie Agent.

For each MV: validate one KPI at a time before adding the next (L200-A design rule #3).

---

*This document is the Phase 2 artifact for L200-A. Update in place as new findings surface. Link to Phase 3 artifact: `fixtures/metric_views/*.metric_view.yml`.*
