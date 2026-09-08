# WanderBricks Business Domain Context

**Project:** wb-metric-views  
**Status:** Living document — update as schema or business rules change  
**References:** `docs/research/01_industry_domain_research.md`, `docs/research/02_data_model_analysis.md`  
**Next artifact:** `docs/semantics/02_kpi_glossary.md`

---

## 1. What Kind of Business Is WanderBricks?

WanderBricks is a **short-term rental (STR) / vacation rental marketplace** — structurally closest to Airbnb and Vrbo, not a traditional hotel chain. This distinction shapes every metric definition in this semantic layer.

| Dimension | Traditional Hotel Chain | WanderBricks (STR Marketplace) |
| --- | --- | --- |
| Inventory owner | Company / brand | Independent hosts (supply-side) |
| Pricing model | Revenue management system | Host-set flat `base_price` |
| Profitability metric | GOPPAR, EBITDA | Revenue per booking, host earnings |
| Occupancy denominator | Available room-nights (known) | Available listing-nights (**unknown — no calendar table**) |
| Guest satisfaction | Survey-based NPS / GSS (0–10 scale) | Star-rating reviews per booking (1–5 scale) |
| Benchmarking | STR STAR report — ADR/RGI vs comp set | AirDNA market comparables |
| Channel mix | Direct website, GDS, OTA, metasearch | Platform marketplace + listing referrers |

---

## 2. Metric View Subdomain Taxonomy

All metric views in `wb_metric_views_care` are organized into four subdomains. This taxonomy drives the `mv_` naming convention and Genie Agent topic grouping.

| Subdomain | Metric Views | Key Stakeholders | Primary Fact Source |
| --- | --- | --- | --- |
| **Supply & Inventory** | `mv_properties` | Product, Operations | `properties` |
| **Booking & Demand** | `mv_bookings`, `mv_host_performance` | Revenue, Sales, Ops | `bookings` |
| **Revenue & Payments** | `mv_payments` | Finance | `payments` |
| **Guest Experience** | `mv_reviews`, `mv_page_views` | Marketing, Product, CX | `reviews`, `page_views` |

> **L100 rule:** One Genie Agent covers all four subdomains unless total MV count exceeds 30. WanderBricks is well within that limit.

---

## 3. KPIs That Cannot Be Computed from the WanderBricks Schema

These industry-standard metrics are **not achievable** from the current `samples.wanderbricks` schema. Do not create metric views for these without first adding the missing data source.

| Industry KPI | Why Unavailable | Missing Data |
| --- | --- | --- |
| **Occupancy Rate** | No available-nights denominator | Property availability calendar (`available_nights` table) |
| **RevPAR** | Depends on Occupancy Rate | Same — no availability calendar |
| **TRevPAR** | No ancillary revenue line items | F&B, spa, parking, fee tables |
| **GOPPAR / EBITDA** | No cost data in schema | Operating expense tables |
| **MPI / ARI / RGI** | No competitive set data | External STR/AirDNA market benchmarks |
| **NPS** | Wrong rating scale | Survey instrument — WanderBricks uses 1–5 star, not 0–10 recommend scale |
| **Review Response Rate** | No host-response column | `reviews.response_text` or `reviews.responded_at` |
| **Reviewer Type Split** | No `reviewer_type` column | Column on `reviews` to distinguish guest vs host reviews |
| **Cancellation Penalty Revenue** | No cancellation policy data | Policy + fee structure on `properties` or `bookings` |
| **Dynamic / Seasonal Pricing** | `base_price` is flat per property | Rate calendar or pricing event table |

---

## 4. Semantic Gaps — Genie Agent Response Guidance

When a Genie user asks for a metric that is not directly computable, the agent should surface the nearest available proxy and explain the gap clearly.

| User Intent | Best Available Proxy | Explanation to Surface |
| --- | --- | --- |
| "Occupancy rate" | `bookings_per_property`, `total_bookings` | No available-nights calendar — only booked nights are known |
| "RevPAR" | `revenue_per_property` | Closest proxy: realized revenue ÷ active properties — NOT true RevPAR |
| "NPS" | `avg_property_rating`, `positive_review_rate` | Reviews use 1–5 scale; NPS requires 0–10 recommendation survey |
| "Host satisfaction" or "host reviews" | `avg_property_rating` (mixed) | No `reviewer_type` column — guest and host reviews coexist in same table |
| "Net revenue" or "host payout" | `total_collected_revenue` | No split between platform fee and host payout in `payments.amount` |
| "Dynamic pricing" or "seasonal rates" | `avg_base_price` by season | `base_price` is a flat host-set asking rate; no dynamic pricing data |
| "Repeat guest rate" | Derivable via window function | `RANK() OVER (PARTITION BY user_id ORDER BY created_at)` > 1 = repeat guest |

---

## 5. Reporting Cadences — Industry Standards

Source: Key Data Dashboard, Revinate Benchmark Report.

| Cadence | Metrics Typically Reported |
| --- | --- |
| **Daily** | Bookings made today, revenue today, cancellations, page views |
| **Weekly** | Booking volume trend, realized rate trend, review score, lead time |
| **Monthly** | Total bookings, total revenue, cancellation rate, review rate, avg rating, payment mix |
| **Quarterly** | Host performance, supply growth, destination mix, refund rate |
| **Trailing 12 months** | Revenue proxy, ALOS, repeat guest rate |

> **Industry standard:** Compare to **prior year same period** for seasonally adjusted views.  
> All date-based metrics must support both **booking date** (`bookings.created_at`) and **stay date** (`bookings.check_in`) filtering. See `03_dimension_hierarchies.md §2`.

---

*This document is the domain framing artifact for wb-metric-views. Update in place when new tables, business rules, or metric view subdomains are added. Reference alongside `02_kpi_glossary.md` when reviewing metric view YAML descriptions.*
