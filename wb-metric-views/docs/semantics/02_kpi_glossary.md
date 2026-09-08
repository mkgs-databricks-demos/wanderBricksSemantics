# WanderBricks KPI Glossary

**Project:** wb-metric-views  
**Status:** Living document — update when new metric views are added  
**References:** `docs/semantics/01_domain_context.md`, `docs/research/01_industry_domain_research.md`  
**Business rules:** See `docs/semantics/04_business_rules.md` for named rules referenced below.

Each entry includes: business definition, WanderBricks-specific SQL formula, Genie synonyms, target metric view, and relevant caveats.

---

## Subdomain 1 — Supply & Inventory

*Source fact: `properties`. Metric view: `mv_properties`.*

### `total_properties`
- **Definition:** Total number of property listings registered on the platform.
- **Formula:** `COUNT(property_id) FROM properties`
- **Synonyms:** active listings, inventory, property count, listing count, listings, supply
- **Metric View:** `mv_properties`
- **Notes:** Counts all registered properties regardless of booking activity. For "active" properties (booked at least once), join to `bookings.property_id`.

### `avg_base_price`
- **Definition:** Average host-set nightly asking price across properties. This is the **listed rate**, not realized revenue per night.
- **Formula:** `AVG(base_price) FROM properties`
- **Synonyms:** average listing price, average nightly rate, average asking price, average posted price, average host price
- **Metric View:** `mv_properties`
- **Notes:** ⚠️ **RULE-11:** `base_price` ≠ realized ADR. For realized average rate per booked night, use `avg_realized_rate` on `mv_bookings`. Clearly distinguish supply-side asking price vs demand-side earned rate in Genie descriptions and synonyms.

### `total_guest_capacity`
- **Definition:** Sum of maximum guest capacity across all properties.
- **Formula:** `SUM(max_guests) FROM properties`
- **Synonyms:** total capacity, max guests, platform capacity, total beds
- **Metric View:** `mv_properties`

### `avg_capacity_per_property`
- **Definition:** Average maximum number of guests per property.
- **Formula:** `AVG(max_guests) FROM properties`
- **Synonyms:** average guest capacity, average property size, average max guests
- **Metric View:** `mv_properties`

---

## Subdomain 2 — Booking & Demand

*Source fact: `bookings`. Metric view: `mv_bookings`.*

### `total_bookings`
- **Definition:** Total booking transactions across all statuses (pending, confirmed, cancelled, completed).
- **Formula:** `COUNT(*) FROM bookings`
- **Synonyms:** reservations, trips booked, booking volume, booking count, total reservations, bookings made
- **Metric View:** `mv_bookings`
- **Notes:** **RULE-01:** Includes all statuses. Status distribution: pending 43.7%, confirmed 24.8%, cancelled 21.2%, completed 10.3%. For revenue-qualified volume, use `confirmed_bookings` or `completed_bookings`.

### `confirmed_bookings`
- **Definition:** Bookings accepted by the host and awaiting stay completion.
- **Formula:** `COUNT(*) FROM bookings WHERE status = 'confirmed'`
- **Synonyms:** accepted bookings, active bookings, upcoming bookings, approved bookings
- **Metric View:** `mv_bookings`

### `completed_bookings`
- **Definition:** Bookings where the guest stay has been fully completed.
- **Formula:** `COUNT(*) FROM bookings WHERE status = 'completed'`
- **Synonyms:** completed stays, finished stays, realized bookings, fulfilled bookings
- **Metric View:** `mv_bookings`

### `cancelled_bookings`
- **Definition:** Bookings that were cancelled before the stay occurred.
- **Formula:** `COUNT(*) FROM bookings WHERE status = 'cancelled'`
- **Synonyms:** cancellations, booking cancellations, cancelled reservations
- **Metric View:** `mv_bookings`

### `cancellation_rate`
- **Definition:** Share of all bookings that were cancelled. Platform health indicator. Airbnb Superhost standard: < 1%.
- **Formula:** `COUNT(*) FILTER (WHERE status = 'cancelled') / COUNT(*) * 100 FROM bookings`
- **Synonyms:** cancel rate, cancellation percentage, booking cancellation rate, cancellation ratio
- **Metric View:** `mv_bookings`
- **Notes:** WanderBricks baseline: 21.2%. For an operational rate excluding unresolved pending bookings, filter to `status IN ('confirmed', 'cancelled', 'completed')` as denominator.

### `avg_length_of_stay`
- **Definition:** Average number of nights per booking. Key revenue management lever — longer stays increase property utilization without additional acquisition cost.
- **Formula:** `AVG(DATEDIFF(check_out, check_in)) FROM bookings`
- **Synonyms:** ALOS, average stay, average nights, trip length, average duration, average stay length, nights per booking
- **Metric View:** `mv_bookings`

### `avg_booking_lead_time`
- **Definition:** Average number of days between booking creation and check-in date. Affects pricing strategy and revenue management windows.
- **Formula:** `AVG(DATEDIFF(check_in, created_at)) FROM bookings`
- **Synonyms:** booking window, lead time, advance booking time, booking horizon, days in advance, booking lead time
- **Metric View:** `mv_bookings`

### `guests_served`
- **Definition:** Total guest-count across confirmed and completed bookings.
- **Formula:** `SUM(guests_count) FROM bookings WHERE status IN ('confirmed', 'completed')`
- **Synonyms:** total guests, guests hosted, people served, total travelers, travelers served
- **Metric View:** `mv_bookings`

### `bookings_per_property`
- **Definition:** Average number of bookings per active property. Measures listing demand intensity and productivity.
- **Formula:** `COUNT(*) FROM bookings / COUNT(DISTINCT property_id) FROM properties`
- **Synonyms:** listing productivity, demand per listing, bookings per listing, reservations per property
- **Metric View:** `mv_bookings`

### `avg_realized_rate`
- **Definition:** Average revenue earned per booked night. The WanderBricks equivalent of ADR (Average Daily Rate) — measures realized pricing power, not asking price.
- **Formula:** `AVG(total_amount / NULLIF(DATEDIFF(check_out, check_in), 0)) FROM bookings WHERE status IN ('confirmed', 'completed')`
- **Synonyms:** ADR, average daily rate, average nightly revenue, realized rate, revenue per night, earned rate, effective nightly rate
- **Metric View:** `mv_bookings`
- **Notes:** ⚠️ **RULE-11:** `avg_realized_rate` (demand metric) is NOT `avg_base_price` (supply metric). Asking price lives on `mv_properties`; earned rate lives on `mv_bookings`. Genie descriptions must clearly distinguish the two.

---

## Subdomain 3 — Revenue & Payments

*Source facts: `bookings` (booking value), `payments` (collected cash). Metric views: `mv_bookings`, `mv_payments`.*

### `total_booking_value`
- **Definition:** Gross booking value — sum of `total_amount` across all booking statuses. High-level demand signal only.
- **Formula:** `SUM(total_amount) FROM bookings`
- **Synonyms:** gross booking value, GBV, total booking revenue, gross revenue, total value, total demand
- **Metric View:** `mv_bookings`
- **Notes:** **RULE-01:** Includes pending (43.7%) and cancelled bookings. Not suitable as a revenue metric without status filter. Use `actual_revenue` for realized revenue.

### `actual_revenue`
- **Definition:** Revenue from completed stays only. The **canonical revenue metric** — use for all realized-revenue reporting.
- **Formula:** `SUM(total_amount) FROM bookings WHERE status = 'completed'`
- **Synonyms:** realized revenue, completed revenue, earned revenue, total earned, recognized revenue
- **Metric View:** `mv_bookings`
- **Notes:** Only 10.3% of bookings are in `completed` status. This is the strictest revenue filter. For cash-basis view, use `total_collected_revenue` on `mv_payments`.

### `forecasted_revenue`
- **Definition:** Expected revenue from upcoming bookings not yet completed (confirmed + pending statuses).
- **Formula:** `SUM(total_amount) FROM bookings WHERE status IN ('confirmed', 'pending')`
- **Synonyms:** pipeline revenue, expected revenue, future revenue, forward revenue, projected revenue
- **Metric View:** `mv_bookings`
- **Notes:** Pending bookings (43.7% of volume) carry high uncertainty — not yet host-accepted. Break out `confirmed_revenue` and `pending_revenue` separately when precision is required.

### `confirmed_revenue`
- **Definition:** Subset of forecasted revenue — accepted bookings awaiting stay completion.
- **Formula:** `SUM(total_amount) FROM bookings WHERE status = 'confirmed'`
- **Synonyms:** accepted revenue, upcoming revenue, committed revenue
- **Metric View:** `mv_bookings`

### `total_collected_revenue`
- **Definition:** Cash collected via payment processor for completed payments. May differ from `actual_revenue` due to payment timing and split-payment scenarios.
- **Formula:** `SUM(amount) FROM payments WHERE payment_status = 'completed'`
- **Synonyms:** net revenue, collected revenue, payments received, paid amount, cash collected, cash revenue
- **Metric View:** `mv_payments`
- **Notes:** ⚠️ **RULE-05 + RULE-14:** Use `COUNT(*)` for payment volume — `payment_id` has 4,465 duplicates. "Net revenue" is used as a synonym here, but it is ambiguous in other contexts (platform fee vs host payout net). Clarify with user when this phrase appears in a Genie query.

### `avg_booking_value`
- **Definition:** Average booking transaction size. Compute per revenue tier (actual vs forecasted) for meaningful comparisons.
- **Formula:** `SUM(total_amount) / COUNT(*) FROM bookings` (apply status filter per tier)
- **Synonyms:** ABV, average transaction value, average booking price, average order value
- **Metric View:** `mv_bookings`

### `revenue_per_property`
- **Definition:** Average realized revenue per active property. The nearest available **proxy for RevPAR** when no availability calendar exists.
- **Formula:** `SUM(total_amount WHERE status = 'completed') / COUNT(DISTINCT property_id) FROM bookings JOIN properties`
- **Synonyms:** RevPAR proxy, revenue per listing, revenue per active property, yield per property
- **Metric View:** `mv_bookings`
- **Notes:** This is **NOT RevPAR**. True RevPAR requires an available-nights denominator. Document this proxy distinction in metric view YAML `description:`. See `docs/semantics/01_domain_context.md §4`.

### `total_refunds`
- **Definition:** Total refunded payment amount.
- **Formula:** `SUM(amount) FROM payments WHERE payment_status = 'refunded'`
- **Synonyms:** refund amount, refunded payments, total refunded, refund total
- **Metric View:** `mv_payments`

### `refund_rate`
- **Definition:** Share of payments that were refunded. Tied to cancellation rate; platform financial health indicator.
- **Formula:** `COUNT(*) FILTER (WHERE payment_status = 'refunded') / COUNT(*) * 100 FROM payments`
- **Synonyms:** refund percentage, chargeback rate, cancellation refund rate, payment refund rate
- **Metric View:** `mv_payments`
- **Notes:** **RULE-05:** WanderBricks baseline: 7.4% refunded, 1.0% failed. Always use `COUNT(*)` — `payment_id` PK is non-functional.

### `avg_transaction_value`
- **Definition:** Average payment amount per completed payment record.
- **Formula:** `AVG(amount) FROM payments WHERE payment_status = 'completed'`
- **Synonyms:** average payment, average collected amount, average paid
- **Metric View:** `mv_payments`

---

## Subdomain 4 — Guest Experience

*Source fact: `reviews` (filtered). Metric view: `mv_reviews`.*

### `avg_property_rating`
- **Definition:** Average review rating for properties on the 1.0–5.0 scale. Core satisfaction score.
- **Formula:** `AVG(rating) FROM reviews WHERE is_deleted = false`
- **Synonyms:** average rating, review score, listing rating, guest rating, star rating, property score, review rating
- **Metric View:** `mv_reviews`
- **Notes:** ⚠️ **RULE-04:** Must filter `WHERE is_deleted = false` — 476 rows have `rating IS NULL` where `is_deleted = true`. WanderBricks platform avg: 3.01/5.0. ⚠️ **RULE-13:** No `reviewer_type` column — score reflects a mix of guest-written and host-written reviews.

### `review_volume`
- **Definition:** Total number of active (non-deleted) reviews.
- **Formula:** `COUNT(*) FROM reviews WHERE is_deleted = false`
- **Synonyms:** total reviews, number of reviews, review count, reviews received
- **Metric View:** `mv_reviews`
- **Notes:** ⚠️ **RULE-03:** Always use `COUNT(*)` — `review_id` has 98,793 duplicates (PK non-functional).

### `positive_review_rate`
- **Definition:** Share of reviews rated 4 or 5 stars. Measures platform-level positive sentiment.
- **Formula:** `COUNT(*) FILTER (WHERE rating >= 4) / COUNT(*) * 100 FROM reviews WHERE is_deleted = false`
- **Synonyms:** positive reviews, high rating rate, 4-star rate, 4+ star rate, good reviews, positive feedback rate, favorable reviews
- **Metric View:** `mv_reviews`

### `review_rate`
- **Definition:** Share of completed stays that generated at least one review.
- **Formula:** `COUNT(DISTINCT booking_id FROM reviews WHERE is_deleted = false) / COUNT(*) FILTER (WHERE status = 'completed') FROM bookings * 100`
- **Synonyms:** review coverage, reviewed stays, percent reviewed, review completion rate, stay review rate
- **Metric View:** `mv_reviews`
- **Notes:** WanderBricks baseline: ~75.2%. Avg of 1.84 reviews per booking — reflects both guest and host reviews sharing the same table (see RULE-13).

### `rating_distribution`
- **Definition:** Count and percentage breakdown of reviews by rating value (1, 2, 3, 4, 5).
- **Formula:** `COUNT(*) GROUP BY rating FROM reviews WHERE is_deleted = false`
- **Synonyms:** star distribution, rating breakdown, review distribution, rating mix, star breakdown
- **Metric View:** `mv_reviews`

---

## Subdomain 5 — Host Performance

*Source fact: `bookings` joined to `properties` → `hosts`. Metric view: `mv_host_performance`.*

### `active_host_count`
- **Definition:** Number of distinct hosts with at least one booking. Use `properties.host_id` as the join path — NOT `hosts.host_id` directly.
- **Formula:** `COUNT(DISTINCT p.host_id) FROM bookings b JOIN properties p ON b.property_id = p.property_id`
- **Synonyms:** active hosts, hosting count, host count, hosts with bookings, engaged hosts
- **Metric View:** `mv_host_performance`
- **Notes:** ⚠️ **RULE-02:** `hosts` has 19,384 rows but only 3,817 hosts have listings. Using `hosts.host_id` as denominator inflates by 5× and understates per-host productivity by the same factor.

### `bookings_per_host`
- **Definition:** Average number of bookings per active host. Measures host productivity.
- **Formula:** `COUNT(*) FROM bookings / COUNT(DISTINCT p.host_id) FROM bookings JOIN properties p`
- **Synonyms:** host productivity, reservations per host, host booking volume, bookings per active host
- **Metric View:** `mv_host_performance`

### `revenue_per_host`
- **Definition:** Average realized revenue per active host.
- **Formula:** `SUM(b.total_amount) FILTER (WHERE b.status = 'completed') / COUNT(DISTINCT p.host_id) FROM bookings b JOIN properties p`
- **Synonyms:** host earnings, earnings per host, average host revenue, revenue per active host
- **Metric View:** `mv_host_performance`

### `avg_host_portfolio_size`
- **Definition:** Average number of property listings per host (for hosts with at least one listing).
- **Formula:** `COUNT(property_id) / COUNT(DISTINCT host_id) FROM properties`
- **Synonyms:** listings per host, properties per host, host portfolio, host inventory, avg listings per host
- **Metric View:** `mv_host_performance`

---

## Subdomain 6 — Booking Funnel (Tier 2)

*Source facts: `page_views`, `clickstream`. Metric views: `mv_page_views` (Tier 1), `mv_booking_funnel` (Tier 2).*

> **Tier 2 note:** `page_views` and `clickstream` have **no direct `booking_id` FK**. Conversion-funnel joins require date-proximity session logic. `mv_booking_funnel` is blocked on `v_property_user_sessions` base view. `mv_page_views` (standalone traffic metrics) is Tier 1 and immediately buildable.

### `total_page_views`
- **Definition:** Total property listing page views (raw traffic volume).
- **Formula:** `COUNT(*) FROM page_views`
- **Synonyms:** listing views, property views, page traffic, view count, total views, property page views
- **Metric View:** `mv_page_views`
- **Notes:** ⚠️ **RULE-06:** Always use `COUNT(*)` — `view_id` has 495,000 duplicates across 500,000 rows (PK non-functional).

### `views_per_property`
- **Definition:** Average page views per active property. Measures listing-level demand intensity.
- **Formula:** `COUNT(*) FROM page_views / COUNT(DISTINCT property_id) FROM properties`
- **Synonyms:** views per listing, traffic per property, listing demand, page views per listing
- **Metric View:** `mv_page_views`

### `booking_conversion_rate`
- **Definition:** Share of property page views that resulted in a confirmed booking. Full-funnel demand efficiency metric.
- **Formula:** `COUNT(confirmed bookings) / COUNT(*) FROM page_views * 100` (requires date-proximity session join)
- **Synonyms:** conversion rate, booking rate, view-to-book rate, listing conversion rate
- **Metric View:** `mv_booking_funnel` (Tier 2 — not yet built)
- **Notes:** ⚠️ No direct `booking_id` FK on `page_views` or `clickstream`. Requires `v_property_user_sessions` base view using `user_id` + `property_id` + date-window proximity join. Blocked until base view is created.

---

*Update this glossary whenever a new KPI is added to a metric view YAML. Keep `synonyms:` arrays in fixture YAML files in sync with the synonyms documented here.*
