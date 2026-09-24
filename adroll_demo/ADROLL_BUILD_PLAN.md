# Affinity Solutions × AdRoll — DCR + ML Demo Build Plan

**Purpose:** Demonstrate how Affinity's purchase-outcome data combined with AdRoll's conversion and engagement data — inside a Snowflake Data Clean Room — produces ML-powered audience intelligence, attribution, and B2B account scoring that neither side can build alone.

**Target:** AdRoll / NextRoll partnership meetings
**Platform type:** DSP + Retargeting + B2B ABM (unique dual B2C/B2B angle)

> **Note:** AdRoll does not offer publicly documented raw impression-level log streams (like TTD REDS or Kargo LLD). Their customer-facing data is conversion-scoped via the Granular Conversion Report (GCR) and aggregate campaign metrics via GraphQL. This demo models their documented schemas. If impression-level access becomes available via enterprise arrangement, the schema can be extended.

---

## 1. What Makes AdRoll Different

| Dimension | AdRoll | TTD / PubMatic / Kargo |
|-----------|--------|------------------------|
| **Data grain** | Conversion-level (28-field GCR) + aggregate campaign metrics | Impression-level logs |
| **Identity** | Native `email_sha256` — strongest Affinity match key | Varies (name, MAID, IP, RampID) |
| **Event taxonomy** | 13 typed events (pageView → purchase) with product detail | Impressions + pixel conversions |
| **B2B angle** | Site Traffic Revealer: firmographics on every visitor | None |
| **CTV** | CTV campaign metrics (video quartiles, household) | TTD/Kargo have CTV |
| **Purchase events** | `purchase` event with `conversion_value`, `order_id`, product array | Pixel conversion (value only) |

**The demo story:**
> AdRoll sees the full conversion funnel — page views, product searches, add-to-carts, purchases — but only what their pixel captures. Affinity sees every card swipe at every register. The clean room joins them. Now AdRoll can: (1) discover purchases their pixel missed, (2) train ML models on true purchase outcomes, (3) score B2B accounts by actual purchasing behavior, and (4) prove CTV's impact on offline purchases.

---

## 2. Environment Layout

**Database:** `ADROLL_DEMO`

| Schema | Purpose |
|--------|---------|
| `AFS_PROVIDER` | Affinity purchase data, predictions, identity crosswalk |
| `ADROLL_CONSUMER` | AdRoll GCR, campaign metrics, audience data, S2S events |
| `ADROLL_B2B` | Site Traffic Revealer firmographics, account scores |
| `CLEANROOM` | Match crosswalks, match rate summaries |
| `ML` | Training sets, ML models, validation, rules |
| `AI` | Cortex AI features, strategy outputs |
| `APPS` | Streamlit apps and stages |

---

## 3. Data Schemas

### 3.1 Affinity Provider (reuse from existing demo)

Same as multi-platform demo: `TX_SRC_V`, `CC_EXT_V`, `PREDICTION_FEED_V`, `MID_*` tables.
Key difference: Affinity's primary join key for AdRoll is `email_sha256` (deterministic, high-confidence).

### 3.2 AdRoll Granular Conversion Report (GCR)

**Source:** NextRoll GraphQL Reporting API — `granularConversions` query
**Grain:** 1 row per attributed conversion event

| Column | Type | Description | Synthetic Notes |
|--------|------|-------------|-----------------|
| `ADROLL_CONVERSION_ID` | VARCHAR | Unique conversion event ID | UUID |
| `CONVERSION_TIME` | TIMESTAMP | When the conversion fired | Random within 90-day window |
| `CONVERSION_TYPE` | VARCHAR | `view_through` or `click_through` | 65% VTC / 35% CTC (industry avg) |
| `ATTRIBUTION_MODEL` | VARCHAR | `last_touch`, `first_touch`, `linear` | 80% last_touch (AdRoll default) |
| `ATTRIBUTION_CREDIT` | FLOAT | Fractional credit (0.0–1.0) | 1.0 for last_touch, split for linear |
| `TOUCHPOINT_TIMESTAMP` | TIMESTAMP | When the attributing impression/click occurred | 1–30 days before conversion |
| `CHANNEL` | VARCHAR | `web`, `facebook`, `instagram`, `native`, `ctv` | Weighted distribution |
| `CAMPAIGN_EID` | VARCHAR | Campaign identifier | ~50 campaigns |
| `CAMPAIGN_TYPE` | VARCHAR | `retargeting`, `prospecting`, `brand_awareness`, `ctv` | Weighted by channel |
| `CAMPAIGN_NAME` | VARCHAR | Human-readable campaign name | Generated from brand + type |
| `ADGROUP_EID` | VARCHAR | Ad group identifier | ~200 ad groups |
| `ADGROUP_NAME` | VARCHAR | Ad group name | Generated |
| `AD_EID` | VARCHAR | Ad creative identifier | ~500 ads |
| `AD_NAME` | VARCHAR | Ad name | Generated |
| `AD_SIZE` | VARCHAR | `300x250`, `728x90`, `160x600`, `320x50`, `970x250`, `video` | Weighted by channel |
| `SEGMENT_EID` | VARCHAR | Conversion segment (rule) ID | ~20 segments |
| `SEGMENT_NAME` | VARCHAR | e.g. "Checkout Complete", "Add to Cart" | Mapped to event types |
| `ATTRIBUTED_REVENUE` | FLOAT | Dollar value of this conversion | $5–$500 range, log-normal |
| `EXTERNAL_DATA` | VARCHAR | JSON string with custom data | Order details |
| `DEVICE` | VARCHAR | `desktop`, `mobile_phone`, `tablet`, `connected_tv` | Weighted |
| `COUNTRY` | VARCHAR | ISO-3166-1 alpha-2 | US-focused, 95% US |
| `CITY` | VARCHAR | City name | Top 20 US metros |
| `FIRST_TOUCH_TIMESTAMP` | TIMESTAMP | First touchpoint in the path | 1–90 days before conversion |
| `LAST_TOUCH_TIMESTAMP` | TIMESTAMP | Last touchpoint before conversion | Same as touchpoint_timestamp |
| `DAYS_TO_CONVERSION_FIRST_TOUCH` | INT | Days from first touch to conversion | 1–90 |
| `DAYS_TO_CONVERSION_LAST_TOUCH` | INT | Days from last touch to conversion | 0–30 |
| `REFERRER_URL` | VARCHAR | Page URL where conversion happened | E-commerce site domains |
| `EMAIL_SHA256` | VARCHAR | SHA-256 hashed email of converter | **Primary Affinity match key** |

**Target volume:** 2M conversion events (across 90-day window)

### 3.3 AdRoll S2S Event Log

**Source:** NextRoll Server-to-Server API event schema
**Grain:** 1 row per tracked event (broader than GCR — includes non-conversion events)

| Column | Type | Description |
|--------|------|-------------|
| `EVENT_ID` | VARCHAR | Unique event identifier |
| `ADVERTISABLE_EID` | VARCHAR | AdRoll advertiser account |
| `EVENT_NAME` | VARCHAR | One of 13 types (see taxonomy below) |
| `EVENT_TIMESTAMP` | TIMESTAMP | When the event occurred |
| `PAGE_LOCATION` | VARCHAR | Full URL where event fired |
| `IP_ADDRESS` | VARCHAR | User IP (truncated for privacy) |
| `DEVICE_TYPE` | VARCHAR | `desktop`, `mobile_phone`, `tablet`, `connected_tv` |
| `DEVICE_OS` | VARCHAR | `windows`, `macos`, `ios`, `android`, `linux` |
| `BROWSER` | VARCHAR | `chrome`, `safari`, `firefox`, `edge` |
| `EMAIL_SHA256` | VARCHAR | Hashed email (when available) |
| `DEVICE_ID` | VARCHAR | IDFA/GAID (mobile only) |
| `FIRST_PARTY_COOKIE` | VARCHAR | AdRoll pixel cookie |
| `CONVERSION_VALUE` | FLOAT | Monetary value (purchase events only) |
| `CURRENCY` | VARCHAR | ISO 4217 currency code |
| `ORDER_ID` | VARCHAR | Merchant order reference (purchase events only) |
| `PRODUCT_ID` | VARCHAR | Product SKU |
| `PRODUCT_GROUP` | VARCHAR | Product category/department |
| `PRODUCT_PRICE` | FLOAT | Individual product price |
| `PRODUCT_QUANTITY` | INT | Quantity |

**Event taxonomy and target distribution:**

| Event | Type | % of Total | Purchase Signal |
|-------|------|-----------|-----------------|
| `pageView` | B2C | 40% | Low |
| `homeView` | B2C | 10% | Low |
| `productSearch` | B2C | 15% | Medium |
| `addToCart` | B2C | 8% | High |
| `purchase` | B2C | 2% | Label (outcome) |
| `highValuePage` | B2B | 8% | Medium |
| `gatedContent` | B2B | 4% | High |
| `demoRequest` | B2B | 2% | Very High |
| `signupPlan` | B2B | 1% | Very High |
| `signupTrial` | B2B | 3% | High |
| `contactSales` | B2B | 2% | Very High |
| `liveChat` | B2B | 3% | Medium |
| `formFill` | B2B | 2% | Medium |

**Target volume:** 10M events (across 90-day window)

### 3.4 AdRoll Campaign Performance Metrics

**Source:** NextRoll GraphQL Reporting API — `metrics` query
**Grain:** 1 row per campaign × date

| Column | Type | Description |
|--------|------|-------------|
| `DATE_` | DATE | Reporting date |
| `CAMPAIGN_EID` | VARCHAR | Campaign identifier |
| `CAMPAIGN_NAME` | VARCHAR | Campaign name |
| `CAMPAIGN_TYPE` | VARCHAR | retargeting / prospecting / brand_awareness / ctv |
| `CHANNEL` | VARCHAR | web / facebook / instagram / native / ctv |
| `IMPRESSIONS` | INT | Total served ad views |
| `CLICKS` | INT | Total ad clicks |
| `COST` | FLOAT | Total media spend (USD) |
| `VIEW_THROUGHS` | INT | View-through conversions |
| `CLICK_THROUGHS` | INT | Click-through conversions |
| `VIEW_REVENUE` | FLOAT | Revenue from VTC |
| `CLICK_REVENUE` | FLOAT | Revenue from CTC |
| `VIDEO_IMPRESSIONS` | INT | CTV video impressions (CTV campaigns only) |
| `VIDEO_VIEWS` | INT | Video views started |
| `VIDEO_25_PCT` | INT | Reached 25% |
| `VIDEO_50_PCT` | INT | Reached 50% |
| `VIDEO_75_PCT` | INT | Reached 75% |
| `VIDEO_100_PCT` | INT | Completed view |

**Target volume:** ~50 campaigns × 90 days = ~4,500 rows

### 3.5 AdRoll Site Traffic Revealer (B2B Firmographics)

**Source:** NextRoll Site Traffic Revealer JavaScript API
**Grain:** 1 row per identified company visiting the advertiser's site

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| `DOMAIN` | VARCHAR | Company domain | e.g. `snowflake.com` |
| `COMPANY_NAME` | VARCHAR | Company name | e.g. `Snowflake Inc.` |
| `COMPANY_INDUSTRY` | VARCHAR | Industry (150 enumerated values) | e.g. `Software / Information Technology` |
| `COMPANY_REVENUE` | VARCHAR | Revenue bucket | 7 buckets: Micro ($0-1MM) → XXLarge ($1B+) |
| `COMPANY_SIZE` | VARCHAR | Employee bucket | 8 buckets: Micro (1-9) → XXLarge (10,000+) |
| `JOURNEY_STAGE` | VARCHAR | ABM journey stage | `Unaware`, `Aware`, `Engaged`, `MQL`, `Opportunity` |
| `ACCOUNT_LISTS` | VARCHAR | Target account list memberships | JSON array |
| `FIRST_VISIT_DATE` | DATE | First visit to advertiser site | Within 180-day window |
| `TOTAL_VISITS` | INT | Total page views from this company | 1–500 |
| `TOTAL_VISITORS` | INT | Unique visitors from this company | 1–50 |

**Target volume:** 5,000 identified companies

### 3.6 AdRoll Audience Segments

**Source:** NextRoll Audience API
**Grain:** 1 row per audience segment

| Column | Type | Description |
|--------|------|-------------|
| `SEGMENT_EID` | VARCHAR | Segment identifier |
| `SEGMENT_NAME` | VARCHAR | Audience name |
| `SEGMENT_TYPE` | VARCHAR | `url`, `crm`, `products_viewed`, `email_list`, `intent`, `composite` |
| `DURATION` | INT | Lookback window (days) |
| `IS_CONVERSION` | BOOLEAN | Is this a conversion audience? |
| `CONVERSION_VALUE` | FLOAT | Value per conversion |
| `ESTIMATED_SIZE` | INT | Approximate audience size |

**Target volume:** 50 segments

---

## 4. Synthetic Data — Realism Engineering

### 4.1 Propensity-Driven Purchase Labels

Same proven approach from the multi-platform demo. Key multipliers for AdRoll:

**Event-type multiplier** (strongest signal):
| Event | Multiplier | Rationale |
|-------|-----------|-----------|
| `purchase` (S2S) | 5.0 | Already purchased — highest repurchase propensity |
| `addToCart` | 3.5 | Cart = strong intent |
| `demoRequest` / `contactSales` / `signupPlan` | 3.0 | B2B high-intent |
| `productSearch` | 2.0 | Active shopping |
| `signupTrial` / `gatedContent` | 1.8 | B2B engagement |
| `liveChat` / `formFill` | 1.5 | Moderate engagement |
| `highValuePage` | 1.3 | Interest signal |
| `pageView` / `homeView` | 0.6 | Passive browsing |

**Channel multiplier:**
| Channel | Multiplier | Rationale |
|---------|-----------|-----------|
| `web` (retargeting) | 2.2 | Retargeted users = prior intent |
| `native` | 1.5 | Content-aligned |
| `facebook` | 1.3 | Social proof |
| `instagram` | 1.2 | Discovery |
| `ctv` | 1.8 | High-attention, household |

**Device multiplier:**
| Device | Multiplier |
|--------|-----------|
| `desktop` | 1.5 | Checkout-ready |
| `mobile_phone` | 1.3 | Proximity to purchase |
| `tablet` | 1.1 | Evening browsing |
| `connected_tv` | 1.8 | Household reach |

**Attribution type multiplier:**
| Type | Multiplier |
|------|-----------|
| `click_through` | 2.5 | Clicked the ad — active engagement |
| `view_through` | 0.8 | Saw the ad — passive |

**Conversion path depth multiplier:**
| Days to Conversion | Multiplier |
|-------------------|-----------|
| 0–3 days | 2.5 | Recent intent |
| 4–7 days | 1.8 | Active consideration |
| 8–14 days | 1.2 | Standard window |
| 15–30 days | 0.7 | Stale |

**Target purchase rate:** ~1.2% of matched events (realistic for e-commerce retargeting)

### 4.2 Conversion Funnel Realism

Events per user should follow a funnel shape:
- Users with `purchase` events MUST have prior `addToCart` (90%) or `productSearch` (10%) events
- Users with `addToCart` MUST have prior `pageView` or `productSearch`
- Cart-to-purchase rate: ~15% (e-commerce benchmark)
- Search-to-cart rate: ~25%
- Pageview-to-search rate: ~30%

### 4.3 B2B Firmographic Realism

- Company size distribution should follow power law (many small, few large)
- Industry distribution weighted toward AdRoll's core verticals: Software/IT, Marketing, Retail, Financial Services
- Journey stage progression: 40% Unaware, 25% Aware, 20% Engaged, 10% MQL, 5% Opportunity
- Companies with higher `TOTAL_VISITS` should correlate with further journey stages
- Revenue bucket should correlate with employee bucket

### 4.4 Deterministic Hash-Based Draws

Same pattern as multi-platform demo:
```sql
ABS(HASH(event_id, seed)) / 9223372036854775807.0 AS DRAW
```
This ensures reproducible purchase label assignment. Combined with the propensity multipliers above, the composite propensity becomes:

```sql
BASE_RATE * EVENT_MULT * CHANNEL_MULT * DEVICE_MULT * ATTRIBUTION_MULT * PATH_DEPTH_MULT
```

---

## 5. ML Models — Snowflake ML

### 5.1 Conversion Purchase Classifier

**Purpose:** Predict which AdRoll conversions correspond to real Affinity card-swipe purchases (vs pixel-only conversions that may not represent actual spend)

| Attribute | Value |
|-----------|-------|
| **Type** | `SNOWFLAKE.ML.CLASSIFICATION` |
| **Target** | `PURCHASED` (0/1) — did Affinity see a matching card swipe? |
| **Training data** | Matched GCR events joined with Affinity purchase labels |
| **Features** | channel, campaign_type, device, attribution_type, ad_size, days_to_conversion, attributed_revenue, city, segment_name |
| **Validation** | Decile lift, feature importance, holdout comparison |

### 5.2 Revenue Prediction Classifier

**Purpose:** Predict spend tier for converters — which conversions drive high-value purchases?

| Attribute | Value |
|-----------|-------|
| **Type** | `SNOWFLAKE.ML.CLASSIFICATION` |
| **Target** | `SPEND_TIER` (HIGH/MID/LOW/NONE) |
| **Training data** | Matched GCR events with Affinity spend data |
| **Features** | Same as above + Affinity propensity score, product_group |

### 5.3 Funnel Stage Predictor

**Purpose:** Predict which users in the S2S event stream will eventually purchase, based on their funnel behavior

| Attribute | Value |
|-----------|-------|
| **Type** | `SNOWFLAKE.ML.CLASSIFICATION` |
| **Target** | `WILL_PURCHASE` (0/1) — purchased within 30-day window |
| **Training data** | S2S events aggregated per user with funnel features |
| **Features** | event_count_by_type, days_since_first_event, device_diversity, total_product_views, has_cart_event, has_search_event, channel_diversity, avg_session_depth |

### 5.4 B2B Account Purchase Scorer

**Purpose:** Score B2B accounts (from Site Traffic Revealer) by actual purchasing behavior of their employees

| Attribute | Value |
|-----------|-------|
| **Type** | `SNOWFLAKE.ML.CLASSIFICATION` |
| **Target** | `ACCOUNT_HAS_PURCHASER` (0/1) — did anyone from this company purchase? |
| **Training data** | Firmographic data joined with matched Affinity purchases (email domain → company domain) |
| **Features** | company_industry, company_revenue, company_size, journey_stage, total_visits, total_visitors, funnel_depth_score |

### 5.5 Brand Spend Forecast

**Purpose:** Forecast future purchase value by brand using Affinity transaction history

| Attribute | Value |
|-----------|-------|
| **Type** | `SNOWFLAKE.ML.FORECAST` |
| **Target** | Weekly spend per brand |
| **Training data** | Affinity transaction aggregates × brand × week |

---

## 6. Output Tables

### 6.1 Conversion Enrichment

**Purpose:** Each AdRoll conversion annotated with Affinity purchase truth

| Column | Description |
|--------|-------------|
| `ADROLL_CONVERSION_ID` | Link to GCR |
| `BRAND_ID` | Affinity brand match |
| `BRAND_NAME` | Brand name |
| `AFFINITY_PURCHASE_AMOUNT` | True card-swipe value (vs pixel `attributed_revenue`) |
| `PIXEL_VS_CARD_DELTA` | Difference between pixel value and card value |
| `ML_PURCHASE_PROBABILITY` | Model-predicted probability |
| `SPEND_TIER` | ML-predicted HIGH/MID/LOW |

### 6.2 Funnel Purchase Rules

**Purpose:** ML-derived rules telling AdRoll which funnel behaviors predict purchases

| Column | Description |
|--------|-------------|
| `RULE_ID` | Unique rule |
| `PREDICATE` | e.g. "Channel=web AND EventType=addToCart AND Device=desktop" |
| `RAW_LIFT` | Purchase lift over baseline |
| `BID_MULTIPLIER` | Recommended multiplier |
| `RULE_ACTION` | BOOST / NEUTRAL / SUPPRESS |
| `SUPPORT` | Number of events supporting this rule |

### 6.3 B2B Account Scores

**Purpose:** Each company scored by purchase propensity

| Column | Description |
|--------|-------------|
| `DOMAIN` | Company domain |
| `COMPANY_NAME` | Company name |
| `COMPANY_INDUSTRY` | Industry |
| `COMPANY_SIZE` | Employee bucket |
| `JOURNEY_STAGE` | ABM stage |
| `PURCHASE_SCORE` | ML purchase probability (0–1) |
| `PREDICTED_ACCOUNT_VALUE` | ML predicted spend |
| `SCORE_TIER` | HOT / WARM / COLD |

### 6.4 CTV Attribution

**Purpose:** CTV campaign performance validated by Affinity card-swipe data

| Column | Description |
|--------|-------------|
| `CAMPAIGN_NAME` | CTV campaign |
| `VIDEO_IMPRESSIONS` | Total video impressions |
| `VIDEO_COMPLETIONS` | 100% video views |
| `MATCHED_PURCHASERS` | Viewers who purchased (Affinity) |
| `TOTAL_PURCHASE_VALUE` | Card-swipe value attributed |
| `CTV_ROAS` | Purchase value / CTV spend |
| `COMPLETION_TO_PURCHASE_RATE` | % of completers who purchased |

### 6.5 Channel Attribution Comparison

**Purpose:** Compare pixel-attributed revenue vs Affinity card-swipe revenue by channel

| Column | Description |
|--------|-------------|
| `CHANNEL` | web / facebook / instagram / native / ctv |
| `PIXEL_REVENUE` | AdRoll attributed_revenue sum |
| `CARD_SWIPE_REVENUE` | Affinity verified purchase value |
| `REVENUE_DELTA_PCT` | How much the pixel over/under-counted |
| `TRUE_ROAS` | Card-swipe revenue / spend |
| `PIXEL_ROAS` | Pixel revenue / spend |

---

## 7. Streamlit Dashboard — 6 Tabs

**App name:** `ADROLL_PURCHASE_INTELLIGENCE`

### Tab 1 — "The Opportunity"
- Side-by-side: What AdRoll sees (funnel events, pixel conversions) vs What Affinity sees (card swipes)
- Revenue gap chart: pixel revenue vs card-swipe revenue by channel
- Metrics: total conversions, total events, total transactions, matched individuals

### Tab 2 — "Conversion Enrichment"
- Before/after: AdRoll pixel value vs Affinity verified value per brand
- Channel attribution comparison chart (pixel ROAS vs true ROAS)
- ML conversion classifier confidence scores

### Tab 3 — "Funnel Intelligence"
- Funnel visualization: pageView → search → cart → purchase (with drop-off rates)
- ML-derived funnel rules (BOOST/SUPPRESS) with filters
- Lift distribution histogram
- Feature importance: what funnel behaviors predict purchases

### Tab 4 — "B2B Account Scoring"
- Account score distribution (HOT/WARM/COLD)
- Industry × purchase score heatmap
- Top 20 accounts by predicted value
- Journey stage vs purchase correlation chart

### Tab 5 — "CTV + Video Attribution"
- CTV campaign performance table with true ROAS
- Video completion → purchase rate chart
- CTV vs non-CTV ROAS comparison
- Note: impression-level data unavailable; attribution based on matched conversions

### Tab 6 — "ML Models + Features"
- Model registry (5 models)
- Decile lift charts (conversion classifier + funnel predictor)
- Side-by-side feature importance
- Holdout validation comparison

---

## 8. Build Phases

### Phase 1 — Environment + Source Data
- [ ] Create database `ADROLL_DEMO`, schemas, warehouses
- [ ] Generate Affinity provider tables (reuse patterns from multi-platform)
- [ ] Generate AdRoll GCR (2M rows) with propensity-driven purchase labels
- [ ] Generate AdRoll S2S events (10M rows) with funnel realism
- [ ] Generate campaign metrics (4,500 rows)
- [ ] Generate Site Traffic Revealer firmographics (5,000 companies)
- [ ] Generate audience segments (50 segments)

### Phase 2 — Clean Room + Identity
- [ ] Generate identity crosswalk (email_sha256 match — expect 55-65% match rate given email is deterministic)
- [ ] Generate match rate summary
- [ ] Generate ground truth labels

### Phase 3 — ML Training
- [ ] Build training sets for all 5 models
- [ ] Train Conversion Purchase Classifier
- [ ] Train Revenue Prediction Classifier
- [ ] Train Funnel Stage Predictor
- [ ] Train B2B Account Purchase Scorer
- [ ] Train Brand Spend Forecast
- [ ] Generate validation tables (deciles, feature importance, holdout, confusion)
- [ ] Register all models in model registry

### Phase 4 — Output Tables
- [ ] Build Conversion Enrichment
- [ ] Build Funnel Purchase Rules
- [ ] Build B2B Account Scores
- [ ] Build CTV Attribution
- [ ] Build Channel Attribution Comparison

### Phase 5 — Streamlit Dashboard
- [ ] Build 6-tab Streamlit app
- [ ] Add chart explainability captions
- [ ] Deploy to Streamlit in Snowflake
- [ ] Verify all tabs render without errors

---

## 9. Key Metrics to Validate (Real-World Benchmarks)

| Metric | Target Range | Source |
|--------|-------------|--------|
| Email SHA-256 match rate | 55–65% | AdRoll documents 50-70% CRM match |
| Cart-to-purchase rate | 12–18% | E-commerce benchmark |
| VTC vs CTC split | 60-70% VTC / 30-40% CTC | Industry standard |
| Pixel vs card-swipe revenue gap | 20–40% undercount by pixel | Affinity's value proposition |
| ML top decile lift | 2.0–3.5x | Comparable to other platform models |
| B2B account de-anonymization | 60–80% of corporate IP traffic | AdRoll documents 60-85% |
| CTV completion-to-purchase rate | 0.5–2.0% | CTV attribution benchmark |

---

## 10. Source Documentation

| Document | URL | What It Contains |
|----------|-----|------------------|
| NextRoll API Index | `apidocs.nextroll.com` | All API endpoints and schemas |
| GraphQL Reporting Schema | `apidocs.nextroll.com/graphql-reporting-api/schema.html` | Full type definitions |
| GraphQL Examples (GCR, CTV) | `apidocs.nextroll.com/graphql-reporting-api/examples.html` | 28-field GCR schema, CTV metrics |
| S2S Event API | `apidocs.nextroll.com/server-to-server-api/events.html` | 13 event types with product schema |
| Site Traffic Revealer | `apidocs.nextroll.com/site-traffic-revealer/examples.html` | 7 firmographic fields, full enums |
| Audience API | `apidocs.nextroll.com/audience-api/reference.html` | Segment types, CRM onboarding |
| Fivetran Connector | `fivetran.com/docs/connectors/applications/adroll` | Available reports and sync details |
