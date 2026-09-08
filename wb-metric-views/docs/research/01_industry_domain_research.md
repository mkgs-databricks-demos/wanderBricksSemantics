# Phase 1 — WanderBricks Industry Domain Research

**Author:** Genie Code (wb-metric-views, L200-A Phase 1)  
**Date:** 2026-09-08  
**Status:** Initial research complete — ready to seed Phase 3 YAML generation  
**Sources:** STR Global, Hospitality Net, AirDNA, Key Data Dashboard, Airbnb, PhocusWire, Skift, Revinate, Medallia, TrustYou  
**References:** L100 Rapid Ontology Standup, L200-A Metric View Standup  
**Next artifact:** `fixtures/metric_views/*.metric_view.yml`

---

## 1. Industry Context — What Kind of Business is WanderBricks?

WanderBricks is a **short-term rental / vacation rental marketplace**, structurally closest to Airbnb and Vrbo rather than a traditional hotel chain. This distinction matters for metric design:

| Dimension | Traditional Hotel Chain | Short-Term Rental Platform (WanderBricks) |
| --- | --- | --- |
| Inventory owner | Company / brand | Independent hosts (supply-side) |
| Pricing | Hotel revenue management | Host-set base price |
| Profitability metric | GOPPAR, EBITDA | Revenue per booking, host payout |
| Occupancy denominator | Available room-nights (known) | Available listing-nights (unknown without calendar data) |
| Guest satisfaction | Survey-based NPS / GSS | Star-rating reviews per booking |
| Comp set benchmarking | STR STAR report, ADR/RGI index | AirDNA market comparables |
| Channel mix | Direct website, GDS, OTA, metasearch | Platform marketplace, direct listing |

**Implication for metric views:** WanderBricks cannot compute classic hotel KPIs like RevPAR or occupancy rate without a property availability calendar. The schema has no `available_nights` table. See Section 7 (Data Model Gaps) for details.

---

## 2. Core Hospitality KPIs — Traditional Hotel Industry

Source: [STR Global Benchmarking Guide](https://str.com/sites/default/files/The-Ultimate-Guide-to-Hotel-Benchmarking.pdf), [Hospitality Net](https://www.hospitalitynet.org/explainer/4119794/the-hospitality-industrys-key-historical-metrics)

### 2.1 The Three Topline KPIs (The "Holy Trinity")

| KPI | Formula | Definition |
| --- | --- | --- |
| **Occupancy Rate** | `Occupied Rooms ÷ Available Rooms × 100` | Share of available rooms/nights that were sold. |
| **ADR** (Average Daily Rate) | `Room Revenue ÷ Rooms Sold` | Average room revenue per sold night. Measures pricing power. |
| **RevPAR** (Revenue per Available Room) | `Room Revenue ÷ Available Rooms` or `ADR × Occupancy` | Revenue per available room-night. The "gold standard" lodging performance KPI per STR. |

### 2.2 Total Revenue and Profitability KPIs

| KPI | Formula | Definition |
| --- | --- | --- |
| **TRevPAR** | `Total Revenue ÷ Available Rooms` | Like RevPAR but includes F&B, spa, parking, fees, and all ancillaries. Whole-hotel view. |
| **GOP** (Gross Operating Profit) | `Total Revenue − Operating Expenses` | Operating profit before fixed charges (interest, taxes, D&A). USALI-standard. |
| **GOPPAR** | `GOP ÷ Available Rooms` | Profit-oriented counterpart to RevPAR. Often considered a stronger indicator of hotel health. |
| **EBITDA** | `Operating Profit + D&A` | Standard valuation and lender/investor metric. |
| **EBITDA Margin** | `EBITDA ÷ Total Revenue × 100` | Operating efficiency; normalizes across property sizes. |
| **GOP Margin** | `GOP ÷ Total Revenue × 100` | Share of revenue remaining after operating costs. |
| **Labor Cost %** | `Labor Expense ÷ Revenue × 100` | Critical driver of GOPPAR / EBITDA performance. |

### 2.3 Market Share / Competitive Index KPIs

Used to benchmark against a competitive set (comp set). Above 100 = outperforming comp set.

| KPI | Formula | Definition |
| --- | --- | --- |
| **MPI** (Market Penetration Index) | `Your Occupancy ÷ Comp Set Occupancy × 100` | Occupancy share vs comp set. |
| **ARI** (Average Rate Index) | `Your ADR ÷ Comp Set ADR × 100` | Pricing performance vs comp set. |
| **RGI** (Revenue Generation Index) | `Your RevPAR ÷ Comp Set RevPAR × 100` | Revenue performance vs comp set. STR's most-used market-share metric. |

---

## 3. Short-Term Rental / OTA Platform KPIs

Source: [AirDNA Performance Dashboard](https://help.airdna.co/en/articles/10011518-performance-dashboard), [Key Data Dashboard](https://www.keydatadashboard.com/fr-fr/blog/vacation-rental-data-101-top-kpis), [Airbnb Host Resources](https://www.airbnb.com/resources/hosting-homes/a/how-search-works-on-airbnb-460)

These are the metrics most directly applicable to WanderBricks.

### 3.1 Supply Metrics

| KPI | Formula | Definition |
| --- | --- | --- |
| **Active Listings / Inventory** | `COUNT(active properties)` | Total properties available for booking. Supply-side health. |
| **Listings by Type** | `COUNT by property_type` | Distribution across Urban, Seasonal, Historical, Ski, etc. |
| **Avg Listing Price (ADR)** | `Total Revenue ÷ Booked Nights` | AirDNA includes cleaning fees in ADR; exclude service fees. |
| **Avg Capacity** | `AVG(max_guests)` | Average guest capacity across supply. |

### 3.2 Demand / Booking Metrics

| KPI | Formula | Definition |
| --- | --- | --- |
| **Total Bookings** | `COUNT(booking_id)` | Volume of booking transactions. |
| **Confirmed Bookings** | `COUNT WHERE status = 'confirmed'` | Bookings that have been accepted. |
| **Completed Bookings** | `COUNT WHERE status = 'completed'` | Bookings that resulted in a stay. |
| **Cancellation Rate** | `Cancelled Bookings ÷ Total Bookings × 100` | Platform health indicator. Airbnb Superhost standard: < 1%. |
| **Booking Conversion Rate** | `Bookings ÷ Property Page Views × 100` | Share of listing views that convert to a booking. Airbnb tracks this at search→listing→booking funnel steps. |
| **Average Length of Stay (ALOS)** | `AVG(check_out − check_in)` in days | Average booking duration. Key Revenue Management lever. |
| **Average Booking Lead Time** | `AVG(check_in − booking_created_at)` in days | How far ahead guests book. Affects revenue management and pricing strategy. |
| **Guests Served** | `SUM(guests_count)` | Total guest-nights served across confirmed/completed bookings. |
| **Bookings per Property** | `Total Bookings ÷ Active Properties` | Listing productivity / demand intensity. |

### 3.3 Revenue Metrics

| KPI | Formula | Definition |
| --- | --- | --- |
| **Total Booking Value (GBV)** | `SUM(total_amount)` | Gross booking value across all statuses. High-level demand signal only. |
| **Actual Revenue** | `SUM(total_amount) WHERE status = 'completed'` | Revenue from completed stays. The **canonical revenue metric** — use for all realized-revenue reporting. |
| **Forecasted Revenue** | `SUM(total_amount) WHERE status IN ('confirmed','pending')` | Expected revenue from upcoming bookings not yet completed. Independently reportable for pipeline/forecast views. |
| **Confirmed Revenue** | `SUM(total_amount) WHERE status = 'confirmed'` | Subset of forecasted: accepted bookings awaiting stay completion. |
| **Pending Revenue** | `SUM(total_amount) WHERE status = 'pending'` | Subset of forecasted: bookings awaiting host confirmation. Highest uncertainty (43.7% of volume). |
| **Total Collected Revenue** | `SUM(payments.amount) WHERE payment_status = 'completed'` | Cash collected via payment processor. May differ from Actual Revenue due to payment timing. |
| **Avg Booking Value (ABV)** | `Total Revenue ÷ Total Bookings` | Average transaction size. Compute separately per revenue tier (actual vs forecasted). |
| **Revenue per Property** | `Total Revenue ÷ Active Properties` | Productivity per listing. Rough proxy for RevPAR without occupancy denominator. |
| **Refund Rate** | `Refunded Payments ÷ Total Payments × 100` | Platform financial health; tied to cancellations. |
| **Payment Method Mix** | `COUNT by payment_method ÷ Total × 100` | Distribution across credit card, PayPal, Apple Pay, etc. |
| **RevPAR** *(requires calendar data)* | `Total Revenue ÷ Available Listing Nights` | Not computable from WanderBricks schema — no availability calendar. |

### 3.4 Host Performance Metrics

| KPI | Formula | Definition |
| --- | --- | --- |
| **Active Hosts** | `COUNT(DISTINCT host_id) FROM bookings JOIN properties` | Hosts with at least one booking. Use `properties.host_id`, NOT `hosts.host_id` (80% of hosts have no listings). |
| **Verified Host Rate** | `Verified Hosts ÷ Active Hosts × 100` | Quality and trust signal. |
| **Avg Host Rating** | `AVG(hosts.rating)` | Platform-assigned host quality score (1.0–5.0). |
| **Listings per Host** | `COUNT(property_id) ÷ COUNT(DISTINCT host_id)` | Portfolio size; identifies professional vs casual hosts. |
| **Bookings per Host** | `Total Bookings ÷ Active Hosts` | Host productivity. |
| **Revenue per Host** | `Total Revenue ÷ Active Hosts` | Host earnings performance. |
| **Employee Count per Host** | `COUNT(employees) ÷ Active Hosts` | Operational scale; ~3.8 avg in WanderBricks. |

---

## 4. Guest Satisfaction and Review KPIs

Source: [Revinate 2025 Benchmark Report](https://www.revinate.com/press-releases/2025-hospitality-benchmark-report-release), [Medallia Benchmarks](https://docs.medallia.com/en/medallia-experience-cloud/reporting/reporting/dashboards/industry-benchmarks), [TrustYou Analytics](https://www.trustyou.com/blog/cxp/new-year-new-set-of-tiles-fresh-insights-into-the-trustyou-analytics-dashboard)

| KPI | Formula | Definition |
| --- | --- | --- |
| **Average Property Rating** | `AVG(rating) WHERE is_deleted = false` | Core satisfaction score (1.0–5.0). WanderBricks avg: 3.01. |
| **Positive Review Rate** | `COUNT(rating >= 4) ÷ COUNT(*) × 100` | Share of reviews that are 4 or 5 stars. Medallia tracks this explicitly. |
| **Review Volume** | `COUNT(*) WHERE is_deleted = false` | Total active reviews. Velocity indicator for platform health. |
| **Review Rate** | `Reviewed Bookings ÷ Completed Bookings × 100` | Share of stays that generate a review. WanderBricks: ~75.2%. |
| **NPS** (Net Promoter Score) | `% Promoters (9–10) − % Detractors (0–6)` | Standard loyalty KPI. **Not directly computable** — WanderBricks reviews have a 1–5 star rating, not a 0–10 recommend scale. Requires survey instrument. |
| **Review Velocity** | `New Reviews ÷ Time Period` | Rate of new review generation; trend indicator. |
| **Review Response Rate** | `Responded Reviews ÷ Total Reviews × 100` | **Not computable** — WanderBricks schema has no host-response column. |
| **Rating Distribution** | `COUNT by rating_bucket / total × 100` | 1-star through 5-star breakdown. Surfaces bimodal distributions. |

> **WanderBricks Note:** Reviews have no `reviewer_type` column. The avg of 1.84 reviews per booking suggests both guest and host reviews exist in the same table. This is a semantic gap — cannot distinguish guest satisfaction from host satisfaction without inference heuristics.

---

## 5. Booking Funnel and Demand Generation KPIs

Source: [PhocusWire hotel conversion rates](https://www.phocuswire.com/Hotel-website-conversion-rates-Fastbooking), [Skift Hotel Distribution Outlook 2024](https://research.skift.com/reports/hotel-distribution-outlook-2024)

### 5.1 Upper Funnel (Traffic)

| KPI | Formula | Definition |
| --- | --- | --- |
| **Total Page Views** | `COUNT(*) FROM page_views` | Raw traffic to property listings. |
| **Views per Property** | `Total Views ÷ Active Properties` | Demand intensity per listing. |
| **Device Mix** | `COUNT by device_type ÷ Total × 100` | Desktop / mobile / tablet split. WanderBricks has `device_type` in page_views. |
| **Referrer Mix** | `COUNT by referrer ÷ Total × 100` | Source attribution: google, direct, email, ad. Available in both `page_views` and `clickstream.metadata.referrer`. |

### 5.2 Mid Funnel (Engagement)

| KPI | Formula | Definition |
| --- | --- | --- |
| **Click-through Events** | `COUNT WHERE event = 'click'` FROM clickstream | User engagement with property elements. |
| **Search Events** | `COUNT WHERE event = 'search'` | Active search intent signals. |
| **Filter Events** | `COUNT WHERE event = 'filter'` | Refinement intent — high-intent users. |

### 5.3 Bottom Funnel (Conversion)

| KPI | Formula | Definition |
| --- | --- | --- |
| **Booking Conversion Rate** | `Bookings ÷ Page Views × 100` | Requires date-proximity join (no direct `booking_id` FK in page_views). |
| **Channel Attribution** | `COUNT by referrer per confirmed booking` | Which referrer sources drive completed bookings. |

> **WanderBricks Note:** `page_views` and `clickstream` have no direct `booking_id` FK. A conversion funnel join requires date-proximity session logic (`user_id` + `property_id` + date proximity). This is a Tier 2 metric view requiring a `v_property_user_sessions` base view.

---

## 6. Standard Reporting Dimensions and Hierarchies

Source: [Databricks UC Semantics](https://docs.databricks.com/aws/en/uc-semantics), [Snowflake Pick'N Stays Demo](https://www.snowflake.com/en/developers/guides/hotel-personalization-picknstays)

Modern hospitality semantic layers organize dimensions into four hierarchical families:

### 6.1 Geography Hierarchy
```
property → destination / city → state / province → country → continent
```
- WanderBricks has: `destinations` (42 destinations with state/country) + `countries` (168 with continent)
- Joins: `properties.destination_id → destinations.destination_id → countries.country`
- **Risk:** The `destinations.country` → `countries.country` join is a free-text string match. Verify before using.

### 6.2 Time Hierarchy
```
date → week → month → quarter → season → year
```
Hospitality always distinguishes two date dimensions:
- **Booking Date** (`bookings.created_at`): when the reservation was made — for demand and lead-time analysis
- **Stay Date** (`bookings.check_in`): when the guest arrives — for occupancy and revenue attribution

Both are needed for revenue management. Commonly derived fields:
- `booking_lead_time_days` = `check_in − created_at` (computable in WanderBricks)
- `length_of_stay_days` = `check_out − check_in` (computable in WanderBricks)
- `day_of_week`, `month`, `quarter`, `season` (derivable from either date)

### 6.3 Guest Segmentation
```
individual / business → origin country → new vs returning → loyalty tier
```
- WanderBricks has: `users.user_type` (individual / business, ~50/50 split), `users.country`
- Missing: loyalty tier, repeat guest flag (derivable with window function on `booking_id` count per `user_id`), customer lifetime value

### 6.4 Property Attributes
```
property type → amenity tier → star rating → destination
```
- WanderBricks has: `property_type` (4 types), `base_price`, `bedrooms`, `bathrooms`, `max_guests`
- Amenity tier derivable: join `property_amenities` → `amenities.category` (Basic / Luxury / Outdoor / Safety)
- Missing: formal star rating, brand/flag classification

### 6.5 Channel / Source
```
direct → OTA → metasearch → paid → organic → email
```
- WanderBricks has: `referrer` in `page_views` and `clickstream.metadata.referrer` (google, direct, email, ad)
- Not present: booking-level channel attribution — no `channel` column on `bookings`

---

## 7. WanderBricks Schema Mapping — Achievable vs. Not Achievable

| Industry KPI | Achievable? | WanderBricks Source | Notes |
| --- | --- | --- | --- |
| Occupancy Rate | ❌ Partial | N/A | No `available_nights` calendar in schema. Only booked nights are known. |
| ADR | ✅ | `bookings.total_amount` / `DATEDIFF(check_out, check_in)` | Revenue per booked night. |
| RevPAR | ❌ | N/A | Requires availability calendar. |
| Total Bookings | ✅ | `bookings` | Tier 1 — `mv_bookings` |
| Cancellation Rate | ✅ | `bookings.status = 'cancelled'` | Tier 1 — `mv_bookings` |
| Avg Length of Stay | ✅ | `DATEDIFF(check_out, check_in)` | Tier 1 — `mv_bookings` |
| Avg Booking Lead Time | ✅ | `DATEDIFF(check_in, created_at)` | Tier 1 — `mv_bookings` |
| Total Revenue (collected) | ✅ | `payments.amount WHERE status='completed'` | Tier 1 — `mv_payments` |
| Total Booking Value (gross) | ✅ | `bookings.total_amount` | Tier 1 — `mv_bookings` |
| Refund Rate | ✅ | `payments.status = 'refunded'` | Tier 1 — `mv_payments` |
| Payment Method Mix | ✅ | `payments.payment_method` | Tier 1 — `mv_payments` |
| Avg Property Rating | ✅ | `reviews.rating WHERE is_deleted = false` | Tier 1 — `mv_reviews` |
| Positive Review Rate | ✅ | `COUNT(rating >= 4) / COUNT(*)` | Tier 1 — `mv_reviews` |
| Review Rate | ✅ | `reviewed bookings / completed bookings` | Tier 1 — `mv_reviews` |
| NPS | ❌ | N/A | No 0–10 recommendation scale. Reviews are 1–5 star only. |
| Review Response Rate | ❌ | N/A | No host-response column in reviews. |
| Active Listings / Supply | ✅ | `properties` | Tier 1 — extend `mv_properties` |
| Avg Listing Price | ✅ | `properties.base_price` | Tier 1 — `mv_properties` |
| Bookings per Property | ✅ | `COUNT(bookings) / COUNT(properties)` | Tier 1 — `mv_bookings` |
| Active Hosts | ✅ | `DISTINCT host_id FROM bookings JOIN properties` | Tier 1 — `mv_host_performance` |
| Host Portfolio Size | ✅ | `COUNT(properties) GROUP BY host_id` | Tier 1 — `mv_host_performance` |
| Page Views / Traffic | ✅ | `page_views` | Tier 1 — `mv_page_views` |
| Referrer Mix | ✅ | `page_views.referrer` | Tier 1 — `mv_page_views` |
| Device Mix | ✅ | `page_views.device_type` | Tier 1 — `mv_page_views` |
| Booking Conversion Rate | ⚠️ Partial | `page_views` + `bookings` | Tier 2 — requires session-logic base view |
| Guest Segmentation (B vs I) | ✅ | `users.user_type` | Available as dimension join |
| Destination Geography | ✅ | `destinations` + `countries` | Available as dimension join — verify string FK |
| GOPPAR / EBITDA | ❌ | N/A | No cost data in schema. |
| Repeat Guest Rate | ⚠️ Derivable | Window function on `bookings.user_id` | Not a native column; derive with `RANK() OVER (PARTITION BY user_id ORDER BY created_at)` |

---

## 8. Recommended Domain Taxonomy for Metric View Organization

Based on industry patterns and the WanderBricks schema, we recommend organizing metric views by **four subdomains**:

| Subdomain | Metric Views | Key Stakeholders |
| --- | --- | --- |
| **Supply & Inventory** | `mv_properties` (extend) | Product, Operations |
| **Booking & Demand** | `mv_bookings`, `mv_host_performance` | Revenue, Sales, Ops |
| **Revenue & Payments** | `mv_payments` | Finance |
| **Guest Experience** | `mv_reviews`, `mv_page_views` (future) | Marketing, Product, CX |

For the L200-B Genie Agent: one agent covering all four subdomains unless total MV count exceeds 30 items (L100 design rule).

---

## 9. Key Industry Synonyms and Business Terminology

These synonyms should be included in every metric view's `synonyms:` arrays to make the Genie Agent answer natural-language questions correctly.

| Canonical Term | Common Synonyms |
| --- | --- |
| `total_bookings` | reservations, trips booked, booking volume, booking count |
| `cancellation_rate` | cancel rate, cancellation percentage, booking cancellations |
| `avg_length_of_stay` | ALOS, average stay, average nights, trip length, average duration |
| `avg_booking_lead_time` | booking window, lead time, advance booking time, booking horizon |
| `total_booking_value` | gross booking value, GBV, total revenue, booking revenue |
| `total_collected_revenue` | net revenue, collected revenue, payments received, paid amount |
| `avg_booking_value` | ABV, average transaction value, average booking price |
| `refund_rate` | refund percentage, chargeback rate, cancellation refund rate |
| `avg_property_rating` | average rating, review score, listing rating, guest rating, star rating |
| `positive_review_rate` | positive reviews, high rating rate, 4+ star rate, good reviews |
| `review_rate` | review coverage, reviewed stays, percent reviewed |
| `total_properties` | active listings, inventory, property count, listings |
| `avg_base_price` | average price, average listing price, average nightly rate |
| `active_hosts` | hosting count, active hosts, host count |
| `bookings_per_property` | listing productivity, demand per listing |
| `total_page_views` | listing views, property views, page traffic, view count |
| `check_in` | arrival date, stay date, arrival |
| `created_at` (bookings) | booking date, reservation date, date booked |
| `destination` | location, city, market, travel destination |
| `property_type` | listing type, accommodation type, property category |

---

## 10. Reporting Cadences — Industry Standards

| Cadence | Metrics Typically Reported |
| --- | --- |
| **Daily** | Bookings made today, revenue today, cancellations today, page views |
| **Weekly** | Booking volume trend, ADR trend, review score, lead time |
| **Monthly** | Total bookings, total revenue, cancellation rate, review rate, avg rating, payment method mix |
| **Quarterly** | Host performance, supply growth, destination mix, refund rate |
| **Trailing 12 months** | Full-year RevPAR proxy, ALOS, repeat guest rate |

Key Data Dashboard specifically recommends comparing to **prior year same period** for seasonally adjusted views. All date-based metrics should support both **booking date** and **stay date** filtering.

---

## 11. Open Questions for Phase 3 (YAML Generation)

| # | Question | Impact |
| --- | --- | --- |
| 1 | Should `avg_adr` use `bookings.total_amount / DATEDIFF` (booking-level) or `payments.amount / DATEDIFF` (collected revenue)? | Changes which revenue source anchors the rate. |
| 2 | ~~Should revenue metrics default to `status IN ('confirmed', 'completed')` or include `pending`?~~ **RESOLVED:** Actual Revenue = `completed` only. Forecasted Revenue = `confirmed` + `pending`, independently reportable. | Pending = 43.7% of bookings — large difference. |
| 3 | Is there a WanderBricks definition of "active property" (e.g., must have had a booking in last 90 days)? | Affects supply count denominators. |
| 4 | Can we infer reviewer type (guest vs host) from `reviews.user_id` vs `bookings.user_id`? | Enables separate guest and host satisfaction scores. |
| 5 | ~~Should Avg Base Price measure asking price (`properties.base_price`) or realized rate (`total_amount / nights`)?~~ **RESOLVED:** Both. `avg_base_price` (asking price) on `mv_properties` (supply). `avg_realized_rate` (`total_amount / DATEDIFF`) on `mv_bookings` (demand). Genie agent synonyms and descriptions must clearly distinguish asking vs realized. | Different business meaning for supply vs demand teams. |
| 6 | Is there a future plan to add an availability calendar table? | Would unlock occupancy rate and RevPAR — highest-value missing KPIs. |

---

*This document is the Phase 1 artifact for L200-A. Update in place as new research surfaces. Reference alongside `docs/research/02_data_model_analysis.md` when generating Phase 3 YAML.*
