# Metric View Design Plan — wb-metric-views

**Author:** Genie Code (L200-A Phase 3 planning)  
**Date:** 2026-09-09  
**Status:** Approved — all open questions resolved; ready for YAML generation  
**Branch:** `care-genie-day-2`  
**References:** `docs/semantics/*`, `docs/research/*`, `fixtures/metric_views/mv_properties.metric_view.yml`

---

## Scope

This document specifies every metric view to be authored in Phase 3, covering both Tier 1 (immediately buildable) and Tier 2 (requires base view). For each MV it details: source fact, joins, dimensions, measures, applicable business rules, open questions, and a pros/cons assessment for controversial design choices.

All designs follow L200-A rules:
* One fact source per MV
* LEFT OUTER JOINs to dimension tables
* Agent metadata mandatory (display_name, synonyms, format)
* Comments at three levels (MV, dimension, measure)
* Cite RULE-N IDs in description fields
* Sync synonyms with `docs/semantics/02_kpi_glossary.md`

---

## Authoring Order

| # | Metric View | Tier | Subdomain | Source Fact | Priority Rationale |
| --- | --- | --- | --- | --- | --- |
| 1 | `mv_bookings` | 1 | Booking & Demand | `bookings` | Core revenue and demand story; highest business value |
| 2 | `mv_properties` (extend) | 1 | Supply & Inventory | `properties` | Adds geography + host dimensions; enriches downstream analysis |
| 3 | `mv_payments` | 1 | Revenue & Payments | `payments` | Completes the cash-basis financial picture |
| 4 | `mv_reviews` | 1 | Guest Experience | `reviews` | Guest satisfaction KPIs; multiple DQ rules to demonstrate |
| 5 | `mv_host_performance` | 1 | Booking & Demand | `bookings` | Derived host productivity; demonstrates same-fact-different-lens pattern |
| 6 | `mv_page_views` | 1 | Guest Experience | `page_views` | Standalone traffic metrics; lowest complexity |
| 7 | `mv_booking_funnel` | 2 | Guest Experience | `page_views` + `bookings` | Blocked on `v_property_user_sessions` base view |
| 8 | `mv_customer_support` | 2 | Operational | `customer_support_logs` | Blocked on `v_support_ticket_summary` base view |
| 9 | `mv_amenity_adoption` | 2 | Supply & Inventory | `property_amenities` | Blocked on `v_property_amenity_flat` base view |

---

## Tier 1 — Detailed Specifications

---

### 1. `mv_bookings`

**Comment:** Core booking demand and revenue metrics for the WanderBricks marketplace. Revenue measures default to confirmed + completed bookings unless explicitly reporting gross demand (RULE-01). Booking date and stay date are independently filterable (RULE-12). The realized rate (`avg_realized_rate`) measures earned revenue per night and is NOT the same as the host-set asking price on mv_properties (RULE-11).

**Source:** `samples.wanderbricks.bookings`

**Joins:**

| Join Name | Source | On Condition | Rationale |
| --- | --- | --- | --- |
| `properties` | `samples.wanderbricks.properties` | `source.property_id = properties.property_id` | Property type, destination_id for geographic dims | `rely: at_most_one_match: true` |
| `users` | `samples.wanderbricks.users` | `source.user_id = users.user_id` | Guest segmentation (user_type, country) | `rely: at_most_one_match: true` |
| `destinations` | `samples.wanderbricks.destinations` | `properties.destination_id = destinations.destination_id` | Geographic hierarchy | `rely: at_most_one_match: true` |
| `countries` (nested under destinations) | `samples.wanderbricks.countries` | `destinations.country = countries.country` | Continent roll-up (0 orphans verified) | `rely: at_most_one_match: true` |

**Dimensions:**

| Name | Expression | Display Name | Format | Synonyms | Notes |
| --- | --- | --- | --- | --- | --- |
| `booking_date` | `source.created_at` | Booking Date | date: year_month_day | reservation date, date booked, booking created | RULE-12: dual date — when reservation was made |
| `stay_date` | `source.check_in` | Stay Date | date: year_month_day | check-in date, arrival date, check in, arrival | RULE-12: dual date — when guest arrives |
| `check_out_date` | `source.check_out` | Check-Out Date | date: year_month_day | departure date, check out, checkout | Needed for ALOS derivation context |
| `booking_status` | `source.status` | Booking Status | — | status, reservation status, booking state | 4 values: pending, confirmed, cancelled, completed |
| `guests_count` | `source.guests_count` | Number of Guests | number: 0 places | party size, guest count, travelers | Per-booking party size |
| `property_type` | `properties.property_type` | Property Type | — | listing type, accommodation type, property category | Via properties join |
| `destination_name` | `destinations.destination` | Destination | — | location, city, market, travel destination | Via properties → destinations |
| `destination_country` | `destinations.country` | Destination Country | — | country, nation | String FK — RULE-09 verified (0 orphans) |
| `continent` | `destinations.countries.continent` | Continent | — | region, world region | Via destinations → countries snowflake join |
| `user_type` | `users.user_type` | Guest Type | — | customer type, traveler type, user segment | individual / business (~50/50 split) |

**Measures:**

| Name | Expression | Display Name | Format | Synonyms | Rules |
| --- | --- | --- | --- | --- | --- |
| `total_bookings` | `COUNT(*)` | Total Bookings | number: 0 places, compact | reservations, trips booked, booking volume, booking count | RULE-01: all statuses |
| `confirmed_bookings` | `COUNT_IF(source.status = 'confirmed')` | Confirmed Bookings | number: 0 places, compact | accepted bookings, active bookings, upcoming bookings | — |
| `completed_bookings` | `COUNT_IF(source.status = 'completed')` | Completed Bookings | number: 0 places, compact | completed stays, finished stays, realized bookings | — |
| `cancelled_bookings` | `COUNT_IF(source.status = 'cancelled')` | Cancelled Bookings | number: 0 places, compact | cancellations, booking cancellations | — |
| `cancellation_rate` | `MEASURE(cancelled_bookings) / NULLIF(MEASURE(total_bookings), 0) * 100` | Cancellation Rate | percentage: 1 place | cancel rate, cancellation percentage | Composable via MEASURE() |
| `avg_length_of_stay` | `AVG(DATEDIFF(source.check_out, source.check_in))` | Avg Length of Stay | number: 1 place | ALOS, average stay, average nights, trip length | — |
| `avg_booking_lead_time` | `AVG(DATEDIFF(source.check_in, source.created_at))` | Avg Booking Lead Time | number: 1 place | booking window, lead time, days in advance | — |
| `guests_served` | `SUM(CASE WHEN source.status IN ('confirmed', 'completed') THEN source.guests_count ELSE 0 END)` | Guests Served | number: 0 places, compact | total guests, guests hosted, travelers served | RULE-01: revenue-qualified only |
| `total_booking_value` | `SUM(source.total_amount)` | Total Booking Value (GBV) | number: 2 places | gross booking value, GBV, total demand | RULE-01: all statuses; NOT a revenue metric |
| `actual_revenue` | `SUM(CASE WHEN source.status = 'completed' THEN source.total_amount ELSE 0 END)` | Actual Revenue | number: 2 places | realized revenue, earned revenue, recognized revenue | RULE-01: completed only; canonical revenue |
| `forecasted_revenue` | `SUM(CASE WHEN source.status IN ('confirmed', 'pending') THEN source.total_amount ELSE 0 END)` | Forecasted Revenue | number: 2 places | pipeline revenue, expected revenue, future revenue | RULE-01: pending carries high uncertainty |
| `confirmed_revenue` | `SUM(CASE WHEN source.status = 'confirmed' THEN source.total_amount ELSE 0 END)` | Confirmed Revenue | number: 2 places | accepted revenue, committed revenue | Subset of forecasted |
| `avg_booking_value` | `AVG(source.total_amount)` | Avg Booking Value | number: 2 places | ABV, average transaction value, average booking price | All statuses; can filter by status dim |
| `pending_revenue` | `SUM(CASE WHEN source.status = 'pending' THEN source.total_amount ELSE 0 END)` | Pending Revenue | number: 2 places | unconfirmed revenue, pending bookings value | RULE-01: highest uncertainty tier (43.7% of bookings) |
| `avg_realized_rate` | `AVG(CASE WHEN source.status IN ('confirmed', 'completed') THEN source.total_amount / NULLIF(DATEDIFF(source.check_out, source.check_in), 0) END)` | Avg Realized Rate (ADR) | number: 2 places | ADR, average daily rate, revenue per night, earned rate | RULE-11: NOT avg_base_price; RULE-01 |
| `bookings_per_booked_property` | `CAST(COUNT(*) AS DOUBLE) / NULLIF(COUNT(DISTINCT source.property_id), 0)` | Bookings per Property | number: 1 place | listing productivity, demand per listing, reservations per property | Denominator = booked properties (not all properties) |
| `revenue_per_booked_property` | `SUM(CASE WHEN source.status = 'completed' THEN source.total_amount ELSE 0 END) / NULLIF(COUNT(DISTINCT CASE WHEN source.status = 'completed' THEN source.property_id END), 0)` | Revenue per Property | number: 2 places | RevPAR proxy, yield per property, revenue per listing | NOT true RevPAR (requires available nights); RULE-01 completed only |

**Pros:**
* Highest business value — unlocks the core booking, revenue, and demand story in a single MV
* Demonstrates composable `MEASURE()` pattern (cancellation_rate reuses cancelled_bookings / total_bookings)
* Dual-date pattern (RULE-12) is a key teaching moment for the workshop
* Revenue tiers (actual/forecasted/confirmed/GBV) show how status filters change the story

**Cons:**
* 17 measures is a dense MV — risk of overwhelming Genie with too many options in one view
* `avg_realized_rate` uses a CASE+AVG pattern that may be hard for students to read at first
* `bookings_per_booked_property` and `revenue_per_booked_property` use booked-property denominators (not all-properties), which is a subtle but important distinction from the glossary definitions

**Open Questions:**

| # | Question | Recommendation |
| --- | --- | --- |
| B-1 | ~~Should we include `pending_revenue` as a separate measure alongside `forecasted_revenue`?~~ | **Approved.** Including `pending_revenue` as a 15th measure. Pending vs confirmed breakdown is high-value for pipeline analysis. |
| B-2 | ~~Should `avg_realized_rate` filter to `completed` only or `confirmed + completed`?~~ | **Resolved: confirmed + completed.** Completed-only (10.3%) is too small a sample for a stable rate. |
| B-3 | ~~Should we add `bookings_per_property`?~~ | **Resolved: Include** as `bookings_per_booked_property`. Both COUNT(*) and COUNT(DISTINCT property_id) come from the bookings source — expressible as a single-source ratio. Comment clarifies denominator is booked properties only. |
| B-4 | ~~Should we add `revenue_per_property` (RevPAR proxy)?~~ | **Resolved: Include** as `revenue_per_booked_property`. Same single-source ratio pattern. Comment explicitly states this is NOT true RevPAR. |

---

### 2. `mv_properties` (extend existing)

**Comment:** Property listing inventory and supply metrics for WanderBricks vacation rentals. Extended with destination geography and host dimensions. `base_price` is the host-set asking price — NOT the realized rate (RULE-11). Host dimensions use `properties.host_id` to identify active hosts only (RULE-02).

**Source:** `samples.wanderbricks.properties`

**Joins to add:**

| Join Name | Source | On Condition | Rationale |
| --- | --- | --- | --- |
| `destinations` | `samples.wanderbricks.destinations` | `source.destination_id = destinations.destination_id` | Geography hierarchy: destination, state, country | `rely: at_most_one_match: true` |
| `countries` (nested under destinations) | `samples.wanderbricks.countries` | `destinations.country = countries.country` | Continent roll-up (0 orphans verified) | `rely: at_most_one_match: true` |
| `hosts` | `samples.wanderbricks.hosts` | `source.host_id = hosts.host_id` | Host attributes: name, rating, verification, join year | `rely: at_most_one_match: true` |

**Dimensions to add (keeping existing 4):**

| Name | Expression | Display Name | Format | Synonyms | Notes |
| --- | --- | --- | --- | --- | --- |
| `destination_name` | `destinations.destination` | Destination | — | location, city, market, travel destination | 42 destinations |
| `destination_state` | `destinations.state_or_province` | State / Province | — | state, province, region | — |
| `destination_country` | `destinations.country` | Country | — | country, nation | RULE-09: 0 orphans verified |
| `continent` | `destinations.countries.continent` | Continent | — | region, world region | Via destinations → countries snowflake |
| `host_name` | `hosts.name` | Host Name | — | host, owner, property manager | High cardinality (3,817) — drill-only |
| `host_rating` | `hosts.rating` | Host Rating | number: 1 place | host score, host quality, owner rating | Platform-assigned, 1.0–5.0 |
| `is_verified_host` | `hosts.is_verified` | Verified Host | — | verified, identity verified, host verified | Boolean |
| `host_join_date` | `hosts.joined_at` | Host Join Date | date: year_month_day | host since, host tenure, joined date | Enables host vintage cohort analysis |
| `max_guests` | `source.max_guests` | Max Guests | number: 0 places | capacity, guest limit, sleeps | Already used in measure; useful as dim too |

**Measures to add (keeping existing 3):**

| Name | Expression | Display Name | Format | Synonyms | Rules |
| --- | --- | --- | --- | --- | --- |
| `avg_capacity_per_property` | `AVG(source.max_guests)` | Avg Capacity per Property | number: 1 place | average guest capacity, average property size | — |
| `avg_host_rating` | `AVG(hosts.rating)` | Avg Host Rating | number: 2 places | average host score, host quality score | Via hosts join |
| `verified_host_count` | `COUNT_IF(hosts.is_verified = true)` | Verified Hosts | number: 0 places | verified host count, identity verified hosts | RULE-02 context: active hosts only |
| `avg_host_portfolio_size` | `CAST(COUNT(source.property_id) AS DOUBLE) / NULLIF(COUNT(DISTINCT source.host_id), 0)` | Avg Listings per Host | number: 1 place | listings per host, properties per host, host portfolio | RULE-02: denominator is active hosts (have listings) |

**Pros:**
* Adds geographic drill-down (destination → state → country) that enriches every dashboard
* Host dimensions enable supply-side quality analysis (rating, verification)
* Minimal risk — extending an already-working MV

**Cons:**
* Adding `hosts` join surfaces `host_rating` (platform-assigned) next to review-based property ratings in mv_reviews — synonym collision risk ("rating" is ambiguous)
* Countries snowflake join added (destinations → countries) — 0 orphans verified, adds continent dimension

**Open Questions:**

| # | Question | Recommendation |
| --- | --- | --- |
| P-1 | ~~Should we add a snowflake join from `destinations.country` → `countries.country` → `countries.continent`?~~ | **Resolved: Include.** Verified 0 orphans on destinations → countries join. Adds `continent` dimension via nested snowflake join. |
| P-2 | ~~Should `host_name` be a dimension?~~ | **Resolved: Include.** Marked as drill-only in comment. Actual column: `hosts.name`. |
| P-3 | ~~Should we add `host_join_date` as a dimension?~~ | **Resolved: Include.** Actual column: `hosts.joined_at` (not `created_at`). Enables host vintage cohort analysis. |

---

### 3. `mv_payments`

**Comment:** Payment collection and refund metrics for WanderBricks. Source of truth for cash-basis revenue reporting. `payments.amount` represents cash collected by the payment processor and differs from `bookings.total_amount` (agreed booking value) due to payment timing, failures, and refunds (RULE-14). Payment volume uses COUNT(*) because `payment_id` has 4,465 duplicates (RULE-05).

**Source:** `samples.wanderbricks.payments`

**Joins:**

| Join Name | Source | On Condition | Rationale |
| --- | --- | --- | --- |
| `bookings` | `samples.wanderbricks.bookings` | `source.booking_id = bookings.booking_id` | Bridge to booking context: status, dates, property_id |

**Dimensions:**

| Name | Expression | Display Name | Format | Synonyms | Notes |
| --- | --- | --- | --- | --- | --- |
| `payment_date` | `source.payment_date` | Payment Date | date: year_month_day | transaction date, paid date, payment created | Actual column is `payment_date` |
| `payment_status` | `source.status` | Payment Status | — | transaction status, payment state | Actual column is `status`; values: completed, refunded, failed |
| `payment_method` | `source.payment_method` | Payment Method | — | payment type, transaction method, how paid | credit_card, paypal, apple_pay, bank_transfer, google_pay |
| `booking_status` | `bookings.status` | Booking Status | — | reservation status | Via bookings join; actual column is `status` |

**Measures:**

| Name | Expression | Display Name | Format | Synonyms | Rules |
| --- | --- | --- | --- | --- | --- |
| `total_payments` | `COUNT(*)` | Total Payments | number: 0 places, compact | payment count, transaction count, number of payments | RULE-05: COUNT(*) only |
| `total_collected_revenue` | `SUM(CASE WHEN source.status = 'completed' THEN source.amount ELSE 0 END)` | Total Collected Revenue | number: 2 places | net revenue, collected revenue, payments received, cash collected | RULE-14: cash-basis metric |
| `total_refunds` | `SUM(CASE WHEN source.status = 'refunded' THEN source.amount ELSE 0 END)` | Total Refunds | number: 2 places | refund amount, refunded payments, total refunded | — |
| `refund_rate` | `COUNT_IF(source.status = 'refunded') / NULLIF(COUNT(*), 0) * 100` | Refund Rate | percentage: 1 place | refund percentage, chargeback rate | RULE-05: baseline 7.4% |
| `failed_payment_rate` | `COUNT_IF(source.status = 'failed') / NULLIF(COUNT(*), 0) * 100` | Failed Payment Rate | percentage: 1 place | failure rate, payment failure percentage | Baseline 1.0% |
| `avg_transaction_value` | `AVG(CASE WHEN source.status = 'completed' THEN source.amount END)` | Avg Transaction Value | number: 2 places | average payment, average collected amount | Completed payments only |

**Pros:**
* Clean separation of cash-basis (payments) vs demand-basis (bookings) revenue reporting
* Payment method mix analysis is immediately useful for finance teams
* Demonstrates RULE-14 (bookings.total_amount ≠ payments.amount) as a teaching moment

**Cons:**
* Limited dimensionality — payments has no direct property or destination context
* 8 orphaned booking_ids (0.016%) will produce NULL booking dimensions on LEFT JOIN — negligible but worth noting
* Without a deeper join chain (payments → bookings → properties → destinations), geographic analysis of payments is not available in this MV

**Open Questions:**

| # | Question | Recommendation |
| --- | --- | --- |
| PAY-1 | ~~Should we extend the join chain through bookings → properties → destinations?~~ | **Resolved: Defer.** Geographic revenue analysis is available on mv_bookings. Keep mv_payments focused on cash-basis reporting. |
| PAY-2 | ~~Confirm column names on payments and bookings tables.~~ | **Resolved.** Payments: `status` (not `payment_status`), `payment_date` (not `created_at`). Bookings: `status` (confirmed). All expressions updated. |
| PAY-3 | ~~Should we add `net_collection_rate` cross-MV metric?~~ | **Resolved: Defer.** Cross-MV ratio — better as dashboard calculation. |

---

### 4. `mv_reviews`

**Comment:** Guest satisfaction and review metrics for WanderBricks. All measures filter `WHERE is_deleted = false` to exclude 476 soft-deleted rows with NULL ratings (RULE-04). Review volume uses COUNT(*) because `review_id` has 98,793 duplicates across 99,793 rows (RULE-03). Ratings reflect a mix of guest and host reviews — no `reviewer_type` column exists (RULE-13).

**Source:** `samples.wanderbricks.reviews`

**Filter:** `is_deleted = false` (applied via top-level YAML `filter:` field — confirmed supported in YAML 1.1; applies to ALL queries automatically)

**Joins:**

| Join Name | Source | On Condition | Rationale |
| --- | --- | --- | --- |
| `bookings` | `samples.wanderbricks.bookings` | `source.booking_id = bookings.booking_id` | Booking context: dates, status, property_id |
| `properties` | `samples.wanderbricks.properties` | `bookings.property_id = properties.property_id` | Property type for segmentation |
| `destinations` | `samples.wanderbricks.destinations` | `properties.destination_id = destinations.destination_id` | Geographic context |

**Dimensions:**

| Name | Expression | Display Name | Format | Synonyms | Notes |
| --- | --- | --- | --- | --- | --- |
| `review_date` | `source.created_at` | Review Date | date: year_month_day | review created, date reviewed | When the review was submitted |
| `rating` | `source.rating` | Rating | number: 0 places | star rating, review score, stars | 1–5 integer; useful as dimension for distribution |
| `property_type` | `properties.property_type` | Property Type | — | listing type, accommodation type | Via bookings → properties |
| `destination_name` | `destinations.destination` | Destination | — | location, city, market | Via bookings → properties → destinations |
| `booking_status` | `bookings.status` | Booking Status | — | reservation status | Enables filtering reviews by booking lifecycle |

**Measures:**

| Name | Expression | Display Name | Format | Synonyms | Rules |
| --- | --- | --- | --- | --- | --- |
| `review_volume` | `COUNT(*)` | Total Reviews | number: 0 places, compact | total reviews, review count, reviews received | RULE-03: COUNT(*) only; RULE-04: `filter:` handles is_deleted |
| `avg_property_rating` | `AVG(source.rating)` | Avg Property Rating | number: 2 places | average rating, review score, star rating, guest rating | RULE-13: mixed guest+host; `filter:` handles is_deleted |
| `positive_review_rate` | `COUNT_IF(source.rating >= 4) / NULLIF(COUNT(*), 0) * 100` | Positive Review Rate | percentage: 1 place | positive reviews, high rating rate, 4+ star rate, favorable reviews | Simplified by `filter:` |
| `low_review_rate` | `COUNT_IF(source.rating <= 2) / NULLIF(COUNT(*), 0) * 100` | Low Review Rate | percentage: 1 place | negative reviews, low rating rate, 1-2 star rate, poor reviews | Complement to positive_review_rate |

**Pros:**
* Demonstrates multiple DQ rules in a single MV (RULE-03, RULE-04, RULE-13) — excellent teaching content
* Rating as both dimension (for distribution) and measure input (for AVG) shows dual-purpose column pattern
* Join chain (reviews → bookings → properties → destinations) demonstrates 3-level snowflake joins

**Cons:**
* `review_rate` (reviewed bookings / completed bookings) is a cross-fact ratio — cannot express cleanly as a single MV measure because the denominator comes from bookings, not reviews
* RULE-13 (no reviewer_type) means all rating metrics are mixed perspective — Genie answers about "guest satisfaction" will be imprecise

**Open Questions:**

| # | Question | Recommendation |
| --- | --- | --- |
| R-1 | ~~Should we attempt the reviewer_type inference heuristic?~~ | **Resolved: Defer to Tier 2.** Heuristic is unverified. Document the gap in MV comment. Could become `v_reviews_typed` base view later. |
| R-2 | ~~Should we include `review_rate` (cross-fact denominator)?~~ | **Resolved: Exclude.** Denominator (`completed_bookings`) lives on mv_bookings. Dashboard-level KPI. |
| R-3 | ~~Can we use a source-level `filter:` instead of per-measure `is_deleted = false`?~~ | **Resolved: YES.** YAML 1.1 supports top-level `filter:` field. All measure expressions simplified — `filter: is_deleted = false` applies globally. |
| R-4 | ~~Should we add `rating_distribution` as an explicit measure?~~ | **Resolved: No.** Rating as dimension suffices. Users `GROUP BY rating` with `MEASURE(review_volume)`. |

---

### 5. `mv_host_performance`

**Comment:** Host productivity and performance metrics for WanderBricks. Uses `bookings` as the source fact and joins through `properties` to reach `hosts`. Active host denominator MUST use `properties.host_id` — never `hosts.host_id` directly, which includes 80% of hosts with no listings (RULE-02).

**Source:** `samples.wanderbricks.bookings`

**Joins:**

| Join Name | Source | On Condition | Rationale |
| --- | --- | --- | --- |
| `properties` | `samples.wanderbricks.properties` | `source.property_id = properties.property_id` | Bridge to host_id, property attributes |
| `hosts` | `samples.wanderbricks.hosts` | `properties.host_id = hosts.host_id` | Host attributes: name, rating, verified, join date |

**Dimensions:**

| Name | Expression | Display Name | Format | Synonyms | Notes |
| --- | --- | --- | --- | --- | --- |
| `booking_date` | `source.created_at` | Booking Date | date: year_month_day | reservation date, date booked | RULE-12 |
| `stay_date` | `source.check_in` | Stay Date | date: year_month_day | check-in date, arrival date | RULE-12 |
| `booking_status` | `source.status` | Booking Status | — | status, reservation status | Enables filtering by lifecycle |
| `host_name` | `hosts.name` | Host Name | — | host, owner, property manager | High cardinality — drill-only |
| `host_rating` | `hosts.rating` | Host Rating | number: 1 place | host score, owner rating | Platform-assigned 1.0–5.0 |
| `is_verified_host` | `hosts.is_verified` | Verified Host | — | verified, identity verified | Boolean |
| `host_join_date` | `hosts.joined_at` | Host Join Date | date: year_month_day | host since, host tenure, joined date | Host vintage cohort analysis |
| `property_type` | `properties.property_type` | Property Type | — | listing type, accommodation type | Via properties join |

**Measures:**

| Name | Expression | Display Name | Format | Synonyms | Rules |
| --- | --- | --- | --- | --- | --- |
| `active_host_count` | `COUNT(DISTINCT properties.host_id)` | Active Hosts | number: 0 places | host count, active hosts, hosting count, engaged hosts | RULE-02: properties.host_id |
| `total_host_bookings` | `COUNT(*)` | Total Host Bookings | number: 0 places, compact | bookings, reservations, host booking volume | All statuses |
| `host_revenue` | `SUM(CASE WHEN source.status = 'completed' THEN source.total_amount ELSE 0 END)` | Host Revenue | number: 2 places | host earnings, total host earnings | RULE-01: completed only |
| `bookings_per_host` | `MEASURE(total_host_bookings) / NULLIF(MEASURE(active_host_count), 0)` | Bookings per Host | number: 1 place | host productivity, reservations per host | Composable MEASURE() |
| `revenue_per_host` | `MEASURE(host_revenue) / NULLIF(MEASURE(active_host_count), 0)` | Revenue per Host | number: 2 places | host earnings, earnings per host, average host revenue | RULE-01 + RULE-02 |

**Pros:**
* Demonstrates the "same fact table, different analytical lens" pattern — bookings is also the source for mv_bookings
* RULE-02 (active host denominator) is a critical teaching point about dimension table traps
* Composable `MEASURE()` for ratios (bookings_per_host, revenue_per_host) builds on the cancellation_rate pattern from mv_bookings

**Cons:**
* Shares source fact with mv_bookings — risk of Genie routing ambiguity when user asks "bookings" without specifying host context
* `avg_host_portfolio_size` (from glossary: properties per host) is a properties-based metric, not a bookings-based metric — cannot compute from this source. Belongs on mv_properties.
* Limited to booking-derived host metrics; operational host metrics (employees, response times) are not available

**Open Questions:**

| # | Question | Recommendation |
| --- | --- | --- |
| H-1 | ~~Should `avg_host_portfolio_size` be on this MV or mv_properties?~~ | **Resolved: Moved to mv_properties.** Supply metric computed from properties table. Added to mv_properties extension spec. |
| H-2 | ~~Should we add `host_join_date` dimension?~~ | **Resolved: Include.** Actual column: `hosts.joined_at`. Added to both mv_host_performance and mv_properties. |
| H-3 | ~~Same source as mv_bookings — merge or keep separate?~~ | **Resolved: Keep separate.** Different lens, different audience, different dimension tables (L200-A Rule #4). MV comment and Genie Agent description differentiate routing. |

---

### 6. `mv_page_views`

**Comment:** Property listing traffic and demand-signal metrics for WanderBricks. Page view volume uses COUNT(*) because `view_id` has 495,000 duplicates across 500,000 rows (RULE-06). No direct booking_id FK exists — conversion funnel analysis requires the Tier 2 `mv_booking_funnel` base view.

**Source:** `samples.wanderbricks.page_views`

**Joins:**

| Join Name | Source | On Condition | Rationale |
| --- | --- | --- | --- |
| `properties` | `samples.wanderbricks.properties` | `source.property_id = properties.property_id` | Property type, destination_id |
| `destinations` | `samples.wanderbricks.destinations` | `properties.destination_id = destinations.destination_id` | Geographic context |

**Dimensions:**

| Name | Expression | Display Name | Format | Synonyms | Notes |
| --- | --- | --- | --- | --- | --- |
| `view_date` | `source.timestamp` | View Date | date: year_month_day | page view date, visit date, traffic date | Actual column is `timestamp` |
| `referrer` | `source.referrer` | Referrer Source | — | traffic source, referrer, acquisition source, channel | google, direct, email, ad |
| `device_type` | `source.device_type` | Device Type | — | device, platform, access method | Desktop, Mobile, Tablet |
| `property_type` | `properties.property_type` | Property Type | — | listing type, accommodation type | Via properties join |
| `destination_name` | `destinations.destination` | Destination | — | location, city, market | Via properties → destinations |

**Measures:**

| Name | Expression | Display Name | Format | Synonyms | Rules |
| --- | --- | --- | --- | --- | --- |
| `total_page_views` | `COUNT(*)` | Total Page Views | number: 0 places, compact | listing views, property views, page traffic, view count | RULE-06: COUNT(*) only |
| `unique_viewers` | `COUNT(DISTINCT source.user_id)` | Unique Viewers | number: 0 places, compact | unique visitors, distinct users, unique users | — |
| `views_per_property` | `MEASURE(total_page_views) / NULLIF(COUNT(DISTINCT source.property_id), 0)` | Views per Property | number: 1 place | views per listing, traffic per property, listing demand | Composable MEASURE() |
| `avg_views_per_user` | `MEASURE(total_page_views) / NULLIF(MEASURE(unique_viewers), 0)` | Avg Views per User | number: 1 place | pages per visitor, engagement depth, views per visitor | Composable MEASURE(); engagement intensity |

**Pros:**
* Lowest complexity Tier 1 MV — good for students who finish early or as a confidence builder
* Referrer and device dimensions enable channel/device mix analysis immediately
* Clean joins, no DQ traps beyond RULE-06

**Cons:**
* Limited standalone value without conversion funnel (Tier 2)
* `unique_viewers` uses COUNT(DISTINCT user_id) which may be slow on large datasets (500K rows in sample is fine)
* No session concept — each page view is independent, no session grouping

**Open Questions:**

| # | Question | Recommendation |
| --- | --- | --- |
| PV-1 | ~~Should we include `clickstream` events?~~ | **Resolved: Exclude.** Clickstream has no PK and is a pure event log. One-fact-source rule. Defer to Tier 2. |
| PV-2 | ~~Should we add `avg_views_per_user`?~~ | **Resolved: Include.** Added as composable MEASURE() ratio. Indicates engagement depth. |
| PV-3 | ~~Confirm timestamp column name on page_views.~~ | **Resolved.** Actual column is `timestamp` (not `viewed_at` or `created_at`). All expressions updated. |

---

## Tier 2 — Advanced Patterns (SQL-as-Source)

Originally blocked on prerequisite base views, but the Metric View YAML 1.1 `source:` field supports arbitrary SQL queries — including CTEs, JOINs, CAST operations, and EXPLODE. This means these MVs can inline the base view logic directly as a SQL source, eliminating the need for separate base views.

**Teaching value:** Tier 2 MVs demonstrate the SQL-as-source pattern, which is the advanced counterpart to the simple table-source pattern used in Tier 1. This makes them excellent workshop content for students who complete Tier 1 early.

**Build order:** After all Tier 1 MVs are certified. `mv_booking_funnel` first (highest analytical value), then `mv_amenity_adoption` (simplest SQL-as-source), then `mv_customer_support` (ARRAY handling).

---

### 7. `mv_booking_funnel`

**Pattern:** SQL-as-source (inlines session logic directly in YAML `source:` field)

**Problem:** `page_views` and `bookings` have no direct equi-join. Both share `user_id` and `property_id`, but there is no `booking_id` on page_views. Attributing a page view to a booking requires date-proximity session logic.

**Source SQL (inline in YAML `source:` field):**

```sql
SELECT
  pv.user_id,
  pv.property_id,
  pv.viewed_at,
  b.booking_id,
  b.created_at AS booking_date,
  b.status AS booking_status,
  DATEDIFF(b.created_at, pv.viewed_at) AS days_view_to_book
FROM samples.wanderbricks.page_views pv
LEFT JOIN samples.wanderbricks.bookings b
  ON pv.user_id = b.user_id
  AND pv.property_id = b.property_id
  AND pv.timestamp <= b.created_at
  AND DATEDIFF(b.created_at, pv.timestamp) <= 30  -- 30-day attribution window
```

**Target Measures:**
* `booking_conversion_rate` — page views that led to a booking within the attribution window
* `avg_days_to_book` — average time from first view to booking
* `channel_attribution` — which referrer sources drive confirmed bookings

**Pros:**
* Unlocks the highest-value funnel metric (conversion rate) that every marketing team asks for
* Attribution window is configurable — can start with 30 days and adjust

**Cons:**
* Date-proximity join is expensive on large datasets and can produce fan-out (one page view matching multiple bookings)
* Attribution logic is opinionated — 30-day window, last-touch vs first-touch, etc.
* Requires careful deduplication to avoid inflating conversion rates

**Recommendation:** Build as an advanced SQL-as-source MV after Tier 1 certification. Validate the join fan-out ratio before finalizing the source SQL.

---

### 8. `mv_customer_support`

**Pattern:** SQL-as-source (inlines CAST and SIZE operations directly in YAML `source:` field)

**Problems:**
* `customer_support_logs.created_at` is STRING, not TIMESTAMP (RULE-07)
* `customer_support_logs.messages` is ARRAY<STRUCT> — cannot aggregate directly (RULE-08)
* Only 1,900 rows — small volume but important for operational insight

**Source SQL (inline in YAML `source:` field):**

```sql
SELECT
  ticket_id,
  user_id,
  subject,
  status,
  CAST(created_at AS TIMESTAMP) AS created_at,
  SIZE(messages) AS message_count,
  messages[0].sender AS first_sender,
  messages[SIZE(messages) - 1].sender AS last_sender
FROM samples.wanderbricks.customer_support_logs
```

**Target Measures:**
* `total_tickets` — support volume
* `avg_messages_per_ticket` — resolution complexity
* `open_ticket_rate` — unresolved percentage

**Recommendation:** Lower priority. The SQL-as-source pattern handles CAST and SIZE cleanly. Build after mv_booking_funnel if time permits.

---

### 9. `mv_amenity_adoption`

**Pattern:** SQL-as-source (inlines M:M bridge flattening directly in YAML `source:` field)

**Problem:** `property_amenities` is a M:M bridge table with composite PK `(property_id, amenity_id)`. The SQL-as-source pattern flattens this inline.

**Source SQL (inline in YAML `source:` field):**

```sql
SELECT
  p.property_id,
  p.property_type,
  p.destination_id,
  a.amenity_id,
  a.amenity_name,
  a.category AS amenity_category
FROM samples.wanderbricks.properties p
JOIN samples.wanderbricks.property_amenities pa ON p.property_id = pa.property_id
JOIN samples.wanderbricks.amenities a ON pa.amenity_id = a.amenity_id
```

**Target Measures:**
* `amenity_coverage` — avg amenities per property
* `category_distribution` — amenity mix by category (Basic/Outdoor/Luxury/Safety)
* `luxury_amenity_rate` — share of properties with at least one luxury amenity

**Recommendation:** Lowest Tier 2 priority but simplest SQL-as-source pattern (just a 3-table JOIN). Good teaching example of the SQL-as-source technique before tackling the more complex booking_funnel or customer_support sources.

---

## Cross-Cutting Design Decisions

### Decision 1: Source Table References — Placeholders vs Hardcoded

The existing `mv_properties.metric_view.yml` uses a hardcoded source (`samples.wanderbricks.properties`). The L200-A design doc recommends `{catalog}.{schema}` placeholders for target flexibility.

| Option | Pro | Con |
| --- | --- | --- |
| **Hardcoded** (`samples.wanderbricks.*`) | Simple; source tables don't move; the registration target (output schema) is already parameterized | Cannot point to a different source catalog/schema in another target |
| **Placeholders** (`{catalog}.{schema}.*`) | Fully portable across targets | Source tables live in `samples.wanderbricks` which is a shared sample dataset — it's not per-target |

**Recommendation:** Keep source references hardcoded to `samples.wanderbricks.*`. The source data is a fixed sample dataset that doesn't change between dev and prod. Only the *output* schema (where the metric view is registered) varies by target — and that's already handled by the registration job parameters.

### Decision 2: CASE vs COUNT_IF for Status-Filtered Measures

| Option | Pro | Con |
| --- | --- | --- |
| `COUNT_IF(status = 'x')` | Readable, concise | Databricks-specific; not portable to other SQL dialects |
| `COUNT(CASE WHEN status = 'x' THEN 1 END)` | ANSI SQL portable | More verbose |
| `SUM(CASE WHEN status = 'x' THEN amount ELSE 0 END)` | Required for SUM-based measures | Cannot use COUNT_IF for SUM |

**Recommendation:** Use `COUNT_IF` for count-based status filters (clean, readable) and `CASE WHEN ... THEN ... ELSE 0 END` for SUM-based measures. This is a Databricks workshop — portability to other dialects is not a concern.

### Decision 3: Join Optimization with `rely`

All many-to-one dimension joins will include `rely: at_most_one_match: true`. This asserts the join cardinality for query optimization, enabling aggregation pushdown. Safe because all dimension table PKs have been verified as unique in the Phase 2 data model analysis.

### Decision 4: Top-Level `filter:` for Row-Level Predicates

When an MV needs a consistent row filter (e.g., `is_deleted = false` on reviews), use the YAML 1.1 `filter:` field rather than repeating the predicate in every measure expression. This is cleaner, less error-prone, and applies automatically to all queries.

**Applied to:** `mv_reviews` (`filter: is_deleted = false`)

### Decision 5: Synonym Collision Management

Several terms are ambiguous across MVs:

| Ambiguous Term | MV 1 | MV 2 | Resolution |
| --- | --- | --- | --- |
| "rating" | `avg_property_rating` (mv_reviews) | `avg_host_rating` (mv_properties) | Use "review rating" / "guest rating" for reviews; "host rating" / "host score" for hosts |
| "revenue" | `actual_revenue` (mv_bookings) | `total_collected_revenue` (mv_payments) | Use "booking revenue" / "earned revenue" for bookings; "collected revenue" / "cash revenue" for payments |
| "ADR" / "rate" | `avg_realized_rate` (mv_bookings) | `avg_base_price` (mv_properties) | ADR is ONLY on mv_bookings (RULE-11); mv_properties uses "listing price" / "asking price" |
| "total" (alone) | Multiple MVs | Multiple MVs | Never use "total" as a standalone synonym — always qualify: "total bookings", "total revenue", "total reviews" |

---

## Consolidated Open Question Register

All 19 open questions have been resolved. Schema-verified column names are reflected in all specs.

| ID | Question | MV | Resolution |
| --- | --- | --- | --- |
| B-1 | Include `pending_revenue`? | mv_bookings | **Include** — high-value pipeline analysis; added as measure #15 |
| B-2 | `avg_realized_rate` filter scope? | mv_bookings | **Confirmed+completed** — completed-only (10.3%) too small for stable rate |
| B-3 | Include `bookings_per_property`? | mv_bookings | **Include** as `bookings_per_booked_property` — single-source ratio; comment clarifies denominator |
| B-4 | Include `revenue_per_property` (RevPAR proxy)? | mv_bookings | **Include** as `revenue_per_booked_property` — comment states NOT true RevPAR |
| P-1 | Add countries snowflake join? | mv_properties | **Include** — 0 orphans verified; adds `continent` dimension |
| P-2 | `host_name` as dimension? | mv_properties | **Include** — drill-only; actual column `hosts.name` |
| P-3 | Add `host_join_date`? | mv_properties | **Include** — actual column `hosts.joined_at` |
| PAY-1 | Extend join chain to destinations? | mv_payments | **Defer** — geographic revenue available on mv_bookings |
| PAY-2 | Verify column names? | mv_payments | **Verified** — `payments.status`, `payments.payment_date`, `bookings.status` |
| PAY-3 | Add `net_collection_rate`? | mv_payments | **Defer** — cross-MV ratio; dashboard calculation |
| R-1 | Reviewer_type inference? | mv_reviews | **Defer to Tier 2** — unverified heuristic |
| R-2 | Include `review_rate`? | mv_reviews | **Exclude** — cross-fact denominator |
| R-3 | MV-level `filter:` for `is_deleted`? | mv_reviews | **YES** — YAML 1.1 `filter:` field confirmed; all measures simplified |
| R-4 | `rating_distribution` measure? | mv_reviews | **No** — rating as dimension suffices for GROUP BY |
| H-1 | `avg_host_portfolio_size` placement? | mv_host_performance | **Moved to mv_properties** — supply metric on properties source |
| H-2 | Add `host_join_date`? | mv_host_performance | **Include** — actual column `hosts.joined_at` |
| H-3 | Merge into mv_bookings? | mv_host_performance | **Keep separate** — different dimension tables (L200-A Rule #4) |
| PV-1 | Include clickstream? | mv_page_views | **Exclude** — separate source; one-fact-source rule |
| PV-2 | Add `avg_views_per_user`? | mv_page_views | **Include** — composable MEASURE() ratio |
| PV-3 | Confirm timestamp column? | mv_page_views | **Verified** — actual column is `timestamp` (not `viewed_at`) |

---

## Summary Statistics

| Metric | Count |
| --- | --- |
| Total Tier 1 MVs | 6 (1 existing + 5 new/extended) |
| Total Tier 2 MVs | 3 (SQL-as-source pattern — no separate base views needed) |
| Total measures across Tier 1 | ~48 (was ~42; added pending_revenue, bookings/revenue per property, avg_host_portfolio_size, avg_views_per_user) |
| Total dimensions across Tier 1 | ~42 (was ~38; added continent, host_join_date x2) |
| Business rules cited | RULE-01 through RULE-14 |
| Open questions resolved | 19/19 |
| Schema-verified column corrections | 7 (page_views.timestamp, payments.status, payments.payment_date, hosts.name, hosts.joined_at, destinations.destination, destinations.state_or_province) |
| New YAML features discovered | `filter:` (row-level predicate), `rely:` (join optimization), `source:` SQL (inline base views) |

---

*This document is the Phase 3 planning artifact for L200-A. All open questions resolved. Ready for YAML generation.*