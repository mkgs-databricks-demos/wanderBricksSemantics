# WanderBricks Dimension Hierarchies

**Project:** wb-metric-views  
**Status:** Living document — update when schema adds new dimension tables  
**References:** `docs/research/01_industry_domain_research.md §6`, `docs/semantics/01_domain_context.md`  
**Business rules:** See `docs/semantics/04_business_rules.md` for RULE-02, RULE-09, RULE-11, RULE-12.

All metric views in `wb_metric_views_care` draw from five standard dimension hierarchies. Each `dimensions:` block in a metric view YAML should select columns from the appropriate hierarchy levels.

---

## Hierarchy 1 — Geography

### Drill Path
```
property → destination / city → country → continent
```

### WanderBricks Column Mapping

| Level | Table | Key Column(s) | Notes |
| --- | --- | --- | --- |
| Property | `properties` | `property_id`, `property_name`, `property_type`, `destination_id` | Grain anchor |
| Destination | `destinations` | `destination_id`, `destination_name`, `state`, `country` | 42 destinations |
| Country | `countries` | `country` (string PK), `continent` | 168 countries |

### Join Path
```sql
properties.destination_id
  → destinations.destination_id
  → destinations.country
    → countries.country
```

> ⚠️ **RULE-09 (String FK Risk):** `destinations.country` → `countries.country` is a free-text name match, not an ISO code join. Verify orphan count before using in any cross-table geographic aggregation:
> ```sql
> SELECT COUNT(*) FROM destinations d
> LEFT JOIN countries c ON d.country = c.country
> WHERE c.country IS NULL  -- should be 0
> ```

### Top Destinations (by property count)

| Rank | Destination | ~Properties |
| --- | --- | --- |
| 1 | Phuket | 1,788 |
| 2 | Mallorca | 1,626 |
| 3 | Gold Coast | 1,624 |
| 4 | Paris | 1,440 |
| 5 | Abu Dhabi | — |

---

## Hierarchy 2 — Time (Dual-Date Pattern)

### Hospitality Requires Two Independent Date Dimensions

Do not use a single date dimension for booking-based metric views. Both must be independently filterable.

| Date Dimension | Column | Business Use |
| --- | --- | --- |
| **Booking Date** | `bookings.created_at` | When the reservation was made — demand analysis, lead-time trends, booking window |
| **Stay Date** | `bookings.check_in` | When the guest arrives — revenue attribution, occupancy proxy, seasonal patterns |

> **Default display:** Booking date. **Revenue team preference:** Stay date for revenue attribution.

### Derived Time Fields

| Field | Expression | Use Case |
| --- | --- | --- |
| `length_of_stay_days` | `DATEDIFF(check_out, check_in)` | ALOS calculation; computable |
| `booking_lead_time_days` | `DATEDIFF(check_in, created_at)` | Lead time analysis; computable |
| `stay_month` | `MONTH(check_in)` | Seasonal demand patterns |
| `booking_month` | `MONTH(created_at)` | Booking timing patterns |
| `stay_day_of_week` | `DAYOFWEEK(check_in)` | Weekday vs weekend split |
| `stay_season` | Derived from `MONTH(check_in)` | Define: Dec–Feb = Winter, Mar–May = Spring, Jun–Aug = Summer, Sep–Nov = Fall |
| `booking_year` | `YEAR(created_at)` | Annual trend; data range 2022–2025 |
| `stay_quarter` | `QUARTER(check_in)` | Quarterly reporting |

> ⚠️ **RULE-12:** Every booking-based metric view must expose both `created_at` (booking date) and `check_in` (stay date) as independent dimensions.

---

## Hierarchy 3 — Guest Segmentation

### Drill Path
```
user_type (individual / business) → origin country → new vs returning
```

### WanderBricks Column Mapping

| Level | Table | Column | Values / Notes |
| --- | --- | --- | --- |
| User type | `users` | `user_type` | `individual` / `business` — ~50/50 split |
| Company | `users` | `company_name` | Sparse — populated for business users only |
| Origin country | `users` | `country` | String name — verify join with `countries` per RULE-09 |
| Repeat guest flag | `bookings` (derived) | — | `RANK() OVER (PARTITION BY user_id ORDER BY created_at) > 1` = returning guest |
| Customer lifetime | `bookings` (derived) | — | `SUM(total_amount) OVER (PARTITION BY user_id WHERE status = 'completed')` |

### Missing Guest Dimensions

| Missing | Workaround | Gap Severity |
| --- | --- | --- |
| Loyalty tier | None available — requires loyalty program data | High — important for retention analysis |
| Repeat guest flag | Derivable via window function (see above) | Medium — not a native column |
| Customer lifetime value | Derivable: `SUM(total_amount)` over `user_id` | Low — computable |
| Acquisition / booking channel | Not on `bookings` — only on `page_views.referrer` | High — channel attribution gap |

---

## Hierarchy 4 — Property Attributes

### Drill Path
```
property_type → amenity_tier → destination → price_tier
```

### WanderBricks Column Mapping

| Level | Table | Column | Values / Notes |
| --- | --- | --- | --- |
| Property type | `properties` | `property_type` | 4 values (see below) |
| Size | `properties` | `bedrooms`, `bathrooms`, `max_guests` | Numeric; tier-derivable |
| Price tier | `properties` | `base_price` | Numeric asking price; tier-derivable |
| Amenity tier | `amenities` | `category` | Basic / Outdoor / Luxury / Safety (via `property_amenities` bridge) |
| Destination | `destinations` | `destination_name`, `state`, `country` | See Hierarchy 1 |

### Property Type Distribution and Pricing

| Property Type | Share | Avg Base Price |
| --- | --- | --- |
| Urban Year-Round | 51% | $173/night |
| Summer Getaway | 39% | $199/night |
| Historical Place | 9% | $147/night |
| Ski Resort | 1% | $266/night |

### Amenity Categories

| Category | Count | Notes |
| --- | --- | --- |
| Basic | 12 | Core utilities (WiFi, kitchen, parking, etc.) |
| Outdoor | 9 | Pool, garden, BBQ, etc. |
| Luxury | 9 | Hot tub, home theater, concierge, etc. |
| Safety | 8 | Smoke detector, first aid, security camera, etc. |

All 18,163 properties are covered (avg ~6.5 amenities per property). Amenity tier requires bridge join: `properties` → `property_amenities` → `amenities.category`.

---

## Hierarchy 5 — Channel / Source

### Drill Path
```
referrer type → device type → session intent
```

### WanderBricks Column Mapping

| Level | Table | Column | Values |
| --- | --- | --- | --- |
| Referrer source | `page_views` | `referrer` | `google`, `direct`, `email`, `ad` |
| Device type | `page_views` | `device_type` | Desktop, Mobile, Tablet |
| Engagement event | `clickstream` | `event` | `click`, `search`, `filter`, `view_photo`, etc. |
| Booking-level channel | `bookings` | **(absent)** | No channel attribution column on `bookings` |

> ⚠️ **Booking-level channel attribution is not available.** There is no `channel` or `referrer` column on the `bookings` table. Determining which referrer source drove a completed booking requires a date-proximity session join from `page_views` to `bookings` via `user_id` + `property_id`. This is a Tier 2 capability blocked on `v_property_user_sessions`.

---

*When adding new dimension columns to a metric view YAML, verify the column maps to one of the five hierarchy families above. If it maps to a new hierarchy not yet documented here, update this file.*
