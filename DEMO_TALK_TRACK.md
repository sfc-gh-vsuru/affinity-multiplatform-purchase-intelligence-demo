# Affinity Solutions — Demo Talk Track

**Event:** Ad Week 2026 | **Date:** October 5, 2026
**Presenter(s):** _____________
**Duration:** ~30 minutes full run; each platform section can stand alone (~6-8 min each)

---

## Key Terms (for presenters new to the domain)

| Term | Plain English |
|------|---------------|
| **DCR (Data Clean Room)** | A secure environment where two companies join their data without either side seeing the other's raw data |
| **Match Rate** | What % of Affinity's consumers could be linked to the platform's ad exposure data |
| **Decile Lift** | Split the audience into 10 equal groups by ML score. "2.5x lift" means the top group purchases 2.5x more than average |
| **Holdout** | A random sample held back from the model, used to prove the model works on data it hasn't seen |
| **ROAS** | Return on Ad Spend — dollars of purchase value per dollar of ad spend |
| **Propensity Score** | Affinity's prediction of how likely someone is to purchase a specific brand (0-100%) |
| **BOOST / SUPPRESS** | BOOST = bid more or set higher floor (this converts). SUPPRESS = bid less or lower floor (this doesn't convert) |
| **Feature Importance** | Which input signals (device, site, geo, etc.) the ML model relies on most to make predictions |

---

## Demo Flow — Recommended Order

| # | Dashboard | Audience | Duration | Purpose |
|---|-----------|----------|----------|---------|
| 1 | **Pipeline End-to-End** | Everyone | 8 min | Set the stage — the full story from problem to output |
| 2 | **TTD Bid Explorer** | TTD team / DSP buyers | 6 min | Deep-dive on bid rules, quadrants, ML models |
| 3 | **PubMatic Yield Scorer** | PubMatic team / SSP sellers | 5 min | Inventory yield, floor optimization, ML models |
| 4 | **Kargo Attribution** | Kargo team / CTV buyers | 5 min | Engagement-to-purchase attribution, CTV proof, ML models |
| 5 | **AdRoll Purchase Intelligence** | AdRoll / NextRoll team | 6 min | Conversion enrichment, funnel intelligence, B2B scoring, CTV |
| 6 | **Cross-Platform Comparison** | Internal / exec summary | 4 min | Side-by-side wrap-up across all 4 platforms |

> **Tip:** For a platform-specific meeting, start with Dashboard 1 (tabs 1-2 only for context), then jump to that platform's dashboard. End with Dashboard 6 tab 4 ("The Pitch").

> **Important:** The 4 platform dashboards (TTD, PubMatic, Kargo, AdRoll) are independent — no cross-references to each other. Each one is safe to present standalone with only Affinity branding.

---

## Dashboard 1: Pipeline End-to-End

**Streamlit app:** `AFFINITY_DEMO.APPS.PIPELINE_END_TO_END`
**Open this first. This is the story.**

### Tab 1 — "The Opportunity: Two Powerful Halves, Better Together"

**What you see:**
- Left column: what the platform has (impressions, clicks, pixel conversions)
- Right column: what Affinity has (300M+ cards, 160M consumers, 5,300+ brands)
- Two red callouts showing what each side is missing
- Metrics: TTD impression count, pixel conversion count, transaction count, individual count

**The story to tell:**
> "Every platform in the ad ecosystem has the same problem. They see *who saw the ad* but not *who bought the product*. Affinity sees the opposite — every card swipe at every register, but no idea what ad caused it. Neither side can share raw data. That's where the Data Clean Room comes in."

**Point out:**
- The pixel conversion rate metric — "This is what the platform thinks conversions look like. But most purchases happen at a register — the pixel never sees them."
- The transaction count vs pixel count gap — "Affinity sees orders of magnitude more purchase events than any pixel."

**Data sources:**
| Element | Table |
|---------|-------|
| TTD Impressions count | `AFFINITY_DEMO.TTD_CONSUMER.REDS_IMPRESSIONS` |
| Pixel Conversions count | `AFFINITY_DEMO.TTD_CONSUMER.REDS_CONVERSIONS` |
| Transaction count | `AFFINITY_DEMO.AFS_PROVIDER.TX_SRC_V` |
| Individual count | `AFFINITY_DEMO.AFS_PROVIDER.CC_EXT_V` |

---

### Tab 2 — "Data Clean Room"

**What you see:**
- Three-column privacy boundary layout: Affinity (Provider) | Clean Room | Platform (Consumer)
- Lists of what each side contributes vs what never leaves
- Privacy guarantees table (6 rows, all "Enforced")

**The story to tell:**
> "This is the architecture. Affinity puts hashed identifiers and purchase data into the clean room. The platform puts hashed impression logs. The join happens inside a governed environment — no raw personal data crosses. The output is a matched crosswalk of anonymous IDs that the platform can use, but can never reverse back to a real person."

**Point out:**
- The center column — "The clean room is the only place this join can happen. Both sides contribute, neither sees the other's raw data."
- The guarantees table — "Every row says Enforced. This isn't aspirational — it's the architecture."

**Data sources:**
| Element | Table |
|---------|-------|
| Privacy guarantees table | Hardcoded in app (reflects DCR architecture) |

---

### Tab 3 — "Identity Resolution"

**What you see:**
- Platform selector dropdown (TTD / PubMatic / Kargo)
- Match rate metrics: overall %, total matched, individual vs household split
- Waterfall bar chart — each match method in sequence, color-coded by match level
- Cross-platform comparison bar chart at bottom

**What is identity resolution?** Affinity knows people by card data. The platform knows them by ad IDs. Identity resolution is the step that links these two worlds — finding the same person on both sides using hashed email, device IDs, IP addresses, etc.

**The story to tell:**
> "Identity resolution is the key step. We run a waterfall of match methods — exact name, fuzzy name variants, hashed email, device ID, household-level IP. Each person gets matched by the best method available. The match rate tells us what percentage of Affinity's consumers we could link to platform data."

**Point out:**
- Toggle between platforms — "Watch how the waterfall changes shape. Each platform has different identity signals available."
- Individual vs Household colors — "Blue is individual-level (we matched a specific person). Orange is household-level (we matched the household, broader reach)."
- Cross-platform bar chart — "The same Affinity data, different match rates depending on what identity signals the platform carries."

**Data sources:**
| Element | Table |
|---------|-------|
| Match waterfall (per platform) | `AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY` |
| Cross-platform comparison | `AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY` (aggregated) |

---

### Tab 4 — "Affinity Enrichment"

**What you see:**
- Before vs After columns showing what changes when Affinity data joins
- "Purchase visibility: 0%" metric on the left
- Prediction coverage metric on the right
- Conversion Gap bar chart — top brands by purchase value the pixel missed

**What does "enrichment" mean here?** Before Affinity, the platform only knows about ad impressions and clicks. After Affinity, every matched individual gets purchase outcomes attached — did they actually buy? How much did they spend? What's their predicted future spend?

**The story to tell:**
> "Before Affinity, the platform optimizes toward proxy metrics — click-through rate, viewability, pixel fires. After Affinity, you optimize toward *actual purchases*. The conversion gap chart is the punchline: these are real purchases, by brand, that the platform's pixel never saw. This is invisible revenue."

**Point out:**
- The "0% purchase visibility" metric — "This is what the platform had before. Zero actual purchase data."
- The conversion gap chart — "Each bar is a brand where Affinity sees verified card swipes the pixel missed entirely."

**Data sources:**
| Element | Table |
|---------|-------|
| Prediction feed count | `AFFINITY_DEMO.AFS_PROVIDER.PREDICTION_FEED_V` |
| Conversion gap chart | `AFFINITY_DEMO.TTD_CONSUMER.DEMO_OUTPUT_CONVERSION_ENRICHMENT` |

---

### Tab 5 — "ML Training"

**What you see:**
- Model registry (models listed in expanders with details)
- Decile lift bar chart — purchase rate by model score decile
- Three model metrics: top decile lift, top 30% capture, top-vs-bottom separation
- Feature importance horizontal bar chart

**What does the ML do?** The enriched data (ad impressions + purchase outcomes) becomes a supervised learning problem. The ML model learns patterns like: "people who saw video ads on CTV in Houston were more likely to purchase." It then scores every future impression with a purchase probability.

**The story to tell:**
> "We take this enriched data and train Snowflake ML models directly inside the clean room boundary. No data leaves. The decile chart shows the result: we split the audience into 10 equal groups by model score. The top group — green bars — purchases at 2.15x the average rate. That's where ad spend should concentrate."

**Point out:**
- The decile chart green bars — "Green bars are your money. These are the segments to bid more on."
- Feature importance — "This tells the platform *why* the model works. Longer bar = that signal matters more for predicting purchases."

**Data sources:**
| Element | Table |
|---------|-------|
| Model registry | `AFFINITY_DEMO.ML.MODEL_REGISTRY` |
| Decile lift chart | `AFFINITY_DEMO.ML.MODEL_VALIDATION_PURCHASE_DECILES` |
| Feature importance | `AFFINITY_DEMO.ML.MODEL_VALIDATION_FEATURE_IMPORTANCE` |

---

### Tab 6 — "Actionable Output"

**What you see:**
- Bidding rules with BOOST/NEUTRAL/SUPPRESS counts (total should equal BOOST + NEUTRAL + SUPPRESS)
- Top 5 BOOST rules and top 5 SUPPRESS rules side by side
- 4-quadrant strategy metrics (Net-New Prospects, Conquesting, High-LTV VIPs, Waste Suppression)
- Three delivery shapes with record counts

**What are bidding rules?** Instead of giving the platform a list of scored users (which requires identity at bid time), we give them *rules* — "if the ad is on this site, on this device, in this metro area, multiply the bid by 1.6x." These are interpretable, privacy-safe, and work with existing systems.

**The story to tell:**
> "Everything we've built collapses into actionable rules. Each one is a predicate like 'Site=espn.com AND Device=CTV → bid 1.6x more.' No identity needed at bid time. These drop into existing bidders today.

> The 4-quadrant strategy tells you *where* to spend. Net-New Prospects get 4-5x multipliers — these are people Affinity predicts will buy but the brand has never reached. Waste Suppression gets suppressed — stop spending on people who won't convert.

> And we deliver in three shapes: a simple audience-plus-multiplier table that works today, per-ID bid instructions for deeper integration, and value-based bidding for platforms that support ROAS optimization."

**Point out:**
- BOOST vs SUPPRESS split — "More BOOST than SUPPRESS. The model finds more opportunity than waste."
- The differentiator callout — "Rules, not audiences. Competitors sell scored audience lists that need identity at bid time. We sell the strategy."

**Data sources:**
| Element | Table |
|---------|-------|
| Bidding rules | `AFFINITY_DEMO.ML.BIDDING_RULES` |
| Quadrant summary | `AFFINITY_DEMO.AI.QUADRANT_SUMMARY_V` |
| Per-ID delivery | `AFFINITY_DEMO.ML.DELIVERY_PER_ID_INSTRUCTION` |
| Value-based bidding | `AFFINITY_DEMO.ML.DELIVERY_VALUE_BASED_BIDDING` |

---

## Dashboard 2: TTD Bid Explorer

**Streamlit app:** `AFFINITY_DEMO.APPS.TTD_BID_EXPLORER`
**Show this when the audience is TTD or DSP-focused. 6 tabs.**

### Tab 1 — "Rule Explorer"

**What you see:** Metric cards (Total/BOOST/SUPPRESS/NEUTRAL), filters by action and dimension, filterable rule table, lift distribution histogram.

**The story:** All 394 rules in one place. Filter by action to see BOOST-only rules, or by dimension (geography, device, supply source). The histogram shows the distribution — green hump on right is opportunity, red tail on left is waste.

| Element | Table |
|---------|-------|
| All rule data | `AFFINITY_DEMO.ML.BIDDING_RULES` |

### Tab 2 — "Quadrant Strategy"

**What you see:** 4 quadrant cards with multipliers and audience sizes, bar chart of audience distribution, three delivery shapes.

**The story:** Each matched individual is classified into a strategic quadrant. Net-New Prospects (4-5x) = high predicted spend, never reached before. Conquesting (3x) = buying from competitors. High-LTV VIPs = already loyal, maintain. Waste Suppression = stop spending here.

| Element | Table |
|---------|-------|
| Quadrant metrics | `AFFINITY_DEMO.AI.QUADRANT_SUMMARY_V` |
| Delivery shapes | `AFFINITY_DEMO.ML.DELIVERY_PER_ID_INSTRUCTION`, `AFFINITY_DEMO.ML.DELIVERY_VALUE_BASED_BIDDING` |

### Tab 3 — "Spend Efficiency"

**What you see:** Side-by-side holdout comparison (with rules vs without), dimension drill-down by selectbox.

**What's a holdout?** We randomly held back 20% of the data and didn't apply Affinity's rules to it. Comparing the two groups proves the rules actually work — not just on training data.

**The story:** The enriched group has higher purchase rate, lower cost per purchase, better ROAS. The drill-down shows which specific dimensions drive the improvement.

| Element | Table |
|---------|-------|
| Holdout comparison | `AFFINITY_DEMO.ML.VALIDATION_HOLDOUT_RESULTS` |
| Dimension drill-down | `AFFINITY_DEMO.ML.TRAINING_SET_TTD` |

### Tab 4 — "ML Models + Features"

**What you see:** Model registry, decile lift chart with metrics, precision-recall chart, side-by-side feature importance.

**The story:** Two complementary models. The Purchase Classifier predicts *will they buy* — driven by where the ad ran (site, DMA, device). The Spend Tier Classifier predicts *how much* — driven by who the person is (prior spend, propensity). Feature importance shows which signals matter most for each model.

| Element | Table |
|---------|-------|
| Model registry | `AFFINITY_DEMO.ML.MODEL_REGISTRY` |
| Decile lift | `AFFINITY_DEMO.ML.MODEL_VALIDATION_PURCHASE_DECILES` |
| Precision-recall | `AFFINITY_DEMO.ML.MODEL_VALIDATION_PURCHASE_CONFUSION` |
| Feature importance | `AFFINITY_DEMO.ML.MODEL_VALIDATION_FEATURE_IMPORTANCE` |

### Tab 5 — "Prediction Accuracy"

**What you see:** Propensity tier performance table, conversion gap bar chart.

**The story:** The tier table validates Affinity's predictions — higher propensity tiers have higher actual purchase rates. The conversion gap chart shows brands where Affinity sees card swipes the pixel missed.

| Element | Table |
|---------|-------|
| Propensity tiers | `AFFINITY_DEMO.ML.ACCURACY_PROOF` |
| Conversion gap | `AFFINITY_DEMO.TTD_CONSUMER.DEMO_OUTPUT_CONVERSION_ENRICHMENT` |

### Tab 6 — "Match Waterfall"

**What you see:** Overall match rate (44.8%), waterfall bar chart with 12 methods, detail table.

**The story:** 12 match methods run in sequence. Exact name fires first, then fuzzy variants, then hashed email, device ID, household methods. 44.8% of Affinity's individuals get matched — every one now has purchase data attached.

| Element | Table |
|---------|-------|
| Match waterfall | `AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY` (PLATFORM='TTD') |

---

## Dashboard 3: PubMatic Yield Scorer

**Streamlit app:** `AFFINITY_DEMO.APPS.PUBMATIC_YIELD_SCORER`
**Show this when the audience is PubMatic or SSP-focused. 6 tabs.**

### Tab 1 — "Yield Heatmap"

**What you see:** Metric cards (segments, highest/lowest yield), heatmap of Publisher x Ad Format colored by yield multiplier.

**What is yield?** For an SSP (supply-side platform), the question isn't "who to bid on" but "which inventory drives purchases." Yield = how well a specific publisher + format combination converts to actual purchases.

**The story:** Each cell is a publisher-format combination. Green = high purchase yield (premium-price this). Red = low (don't overprice).

| Element | Table |
|---------|-------|
| Yield scores | `AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_INVENTORY_YIELD_SCORES` |

### Tab 2 — "Floor Optimizer"

**What you see:** Data table of floor recommendations, bar chart of top 20 opportunities by revenue lift %.

**What's a floor price?** The minimum bid an advertiser must pay to win an ad placement. Affinity's data helps set floors based on actual purchase conversion, not guesswork.

**The story:** Each row is an actionable floor price adjustment. The bar chart highlights the biggest revenue opportunities — segments where raising the floor is backed by purchase data.

| Element | Table |
|---------|-------|
| Floor recommendations | `AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_FLOOR_RECOMMENDATIONS` |

### Tab 3 — "Premium Packages"

**What you see:** Data table of pre-built inventory packages with purchase rates.

**The story:** Pre-packaged inventory bundles PubMatic can sell to advertisers, each backed by purchase conversion evidence. The purchase rate column is the proof point.

| Element | Table |
|---------|-------|
| Packages | `AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_PURCHASE_INVENTORY_PACKAGES` |

### Tab 4 — "SSP Bidding Rules"

**What you see:** 271 rules (BOOST/NEUTRAL/SUPPRESS), filters, rule table, lift histogram, publisher multiplier floor tiers (Premium/Standard/Discount).

**The story:** ML-generated rules for floor pricing. BOOST = set a higher floor, this inventory converts. SUPPRESS = accept lower bids, this doesn't convert. The publisher multipliers section shows 1,191 PREMIUM segments that earned higher floors and 1,339 DISCOUNT segments.

| Element | Table |
|---------|-------|
| SSP rules (271) | `AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_SSP_BIDDING_RULES` |
| Publisher multipliers | `AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_PUBLISHER_MULTIPLIERS` |

### Tab 5 — "ML Models + Features"

**What you see:** 2 PubMatic-specific ML models, decile lift chart (2.5x top decile), side-by-side feature importance, holdout comparison.

**The story:** Two Snowflake ML models trained on 2.5M matched PubMatic impressions. The Yield Classifier predicts which inventory converts. The Spend Classifier predicts how much purchasers spend. Top decile converts at 2.5x baseline. BIDFLOOR is the #1 feature — the SSP's own pricing signal is the strongest predictor, with Affinity's propensity score as #2.

| Element | Table |
|---------|-------|
| Model registry | `AFFINITY_DEMO.ML.MODEL_REGISTRY` (PUBMATIC%) |
| Decile lift | `AFFINITY_DEMO.ML.PUBMATIC_VALIDATION_DECILES` |
| Feature importance | `AFFINITY_DEMO.ML.PUBMATIC_FEATURE_IMPORTANCE` |
| Holdout | `AFFINITY_DEMO.ML.PUBMATIC_HOLDOUT_RESULTS` |

### Tab 6 — "Identity Coverage"

**What you see:** Match rate metric with matched individual count, waterfall bar chart (3 methods), detail table.

**The story:** PubMatic matches via hashed email, device ID, and IP. Every matched individual now has Affinity purchase data attached — data that was completely invisible before.

| Element | Table |
|---------|-------|
| Match waterfall | `AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY` (PLATFORM='PUBMATIC') |

---

## Dashboard 4: Kargo Attribution

**Streamlit app:** `AFFINITY_DEMO.APPS.KARGO_ATTRIBUTION_DASHBOARD`
**Show this when the audience is Kargo or CTV-focused. 6 tabs.**

### Tab 1 — "Attribution Funnel"

**What you see:** Metric cards (placements scored, total/avg purchase value), bar chart of top 15 placements by purchase value, color-coded by creative format.

**What is attribution?** Connecting an ad engagement (someone saw or clicked an ad) to a real purchase (they swiped a card). Kargo shows ads; Affinity sees purchases. The clean room connects them.

**The story:** Each bar is a placement. The length is the purchase value attributed to people who engaged with that placement and then bought something. The colors show which of Kargo's creative formats drove it.

| Element | Table |
|---------|-------|
| Placement scores | `AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_PLACEMENT_PURCHASE_SCORES` |

### Tab 2 — "CTV Scoreboard"

**What you see:** CTV platform metrics, bar chart ranking platforms by purchase value, app-level detail table.

**Why CTV matters:** CTV (Connected TV) ad prices are premium but hard to justify. This tab provides the purchase proof — which CTV platforms and apps actually drive card swipes.

**The story:** CTV platforms ranked by actual purchase value. Kargo can tell advertisers: "People who saw your ad on this platform bought $X of your product." That justifies premium CTV pricing.

| Element | Table |
|---------|-------|
| CTV attribution | `AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_CTV_ATTRIBUTION` |

### Tab 3 — "Creative Formats"

**What you see:** Bar chart of Kargo's proprietary formats ranked by purchase lift, dashed baseline at 1.0x, detail table.

**The story:** Formats above the dashed line outperform baseline — they drive more purchases than average. Formats below it underperform. Kargo's proprietary formats (Runway, Breakaway, Venti, etc.) can now be ranked by actual purchase outcomes, not just engagement metrics.

| Element | Table |
|---------|-------|
| Format lift | `AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_ENGAGEMENT_QUALITY_RULES` |

### Tab 4 — "ML Engagement Rules"

**What you see:** 191 ML-generated rules (BOOST/NEUTRAL/SUPPRESS), filters, rule table, lift histogram.

**The story:** ML-generated rules that tell Kargo which engagement patterns drive purchases. "Format=Runway AND Device=Connected TV" might be a BOOST rule — those engagements convert. "Event=video_load AND Device=Computer" might be SUPPRESS — low purchase signal. 86 BOOST rules, 67 SUPPRESS, 38 NEUTRAL.

| Element | Table |
|---------|-------|
| ML rules (191) | `AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_ML_ENGAGEMENT_RULES` |

### Tab 5 — "ML Models + Features"

**What you see:** 2 Kargo-specific ML models, decile lift chart (3.45x top decile), side-by-side feature importance, holdout comparison.

**The story:** Two Snowflake ML models trained on 2.5M Kargo LLD events. The Engagement Classifier predicts which engagements lead to purchases. Top decile converts at 3.45x baseline — the strongest lift of any platform. COMPOSITE_PROPENSITY (Affinity's score) is the #1 feature, followed by PUBLISHER_NAME and GEO_DMA.

| Element | Table |
|---------|-------|
| Model registry | `AFFINITY_DEMO.ML.MODEL_REGISTRY` (KARGO%) |
| Decile lift | `AFFINITY_DEMO.ML.KARGO_VALIDATION_DECILES` |
| Feature importance | `AFFINITY_DEMO.ML.KARGO_FEATURE_IMPORTANCE` |
| Holdout | `AFFINITY_DEMO.ML.KARGO_HOLDOUT_RESULTS` |

### Tab 6 — "Identity Coverage"

**What you see:** Match rate metric with matched individual count, waterfall bar chart (2 methods), detail table.

**The story:** Kargo matches via RampID and IP — just 2 methods. CTV environments rely heavily on IP for household-level matching. Every matched individual now has Affinity purchase data — data that was invisible before.

| Element | Table |
|---------|-------|
| Match waterfall | `AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY` (PLATFORM='KARGO') |

---

## Dashboard 5: AdRoll Purchase Intelligence

**Streamlit app:** `AFFINITY_DEMO.APPS.ADROLL_PURCHASE_INTELLIGENCE`
**Show this when the audience is AdRoll/NextRoll. 6 tabs. Unique B2B angle.**

### Tab 1 — "The Opportunity"

**What you see:** Side-by-side (AdRoll events + conversions vs Affinity transactions + individuals), channel revenue comparison (pixel vs card swipe).

**The story:** AdRoll's pixel captures conversion intent but not actual purchases. Affinity sees every card swipe. The channel revenue chart reveals the gap — how much each channel over- or under-counts.

| Element | Table |
|---------|-------|
| Channel attribution | `AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_CHANNEL_ATTRIBUTION` |

### Tab 2 — "Conversion Enrichment"

**What you see:** Channel attribution table, true purchase rate by channel bar chart, match coverage metric (80.6%).

**The story:** What percentage of AdRoll's conversions represent verified card-swipe purchases? The match rate is 80.6% — email SHA-256 is the strongest deterministic match of any platform.

| Element | Table |
|---------|-------|
| Channel comparison | `AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_CHANNEL_ATTRIBUTION` |
| Match rate | `AFFINITY_DEMO.CLEANROOM.ADROLL_MATCH_RATE_SUMMARY` |

### Tab 3 — "Funnel Intelligence"

**What you see:** 120 ML-derived funnel rules (BOOST/NEUTRAL/SUPPRESS), filters, rule table, lift histogram.

**The story:** ML-derived rules from 10M funnel events. Each rule tells AdRoll which engagement patterns predict real purchases. "Channel=web AND Device=desktop" might be BOOST. "Channel=instagram AND Attribution=view_through" might be SUPPRESS.

| Element | Table |
|---------|-------|
| Funnel rules (120) | `AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_FUNNEL_PURCHASE_RULES` |

### Tab 4 — "B2B Account Scoring"

**What you see:** HOT/WARM/COLD account tiers, industry x purchase score chart, top 20 accounts, journey stage vs purchase score.

**What is this?** AdRoll's Site Traffic Revealer identifies companies visiting the advertiser's site (firmographics: industry, revenue, size). The ML model scores each company by actual purchase propensity using Affinity data. This is unique to AdRoll — none of the other platforms have B2B firmographic scoring.

**The story:** 5,000 companies scored. 806 are HOT. The journey stage chart validates the ABM funnel — companies further along (MQL, Opportunity) have higher purchase scores. TOTAL_VISITS is the #1 feature, not firmographics — engagement frequency matters more than company size.

| Element | Table |
|---------|-------|
| Account scores | `AFFINITY_DEMO.ADROLL_B2B.ADROLL_ACCOUNT_SCORES` |

### Tab 5 — "CTV + Video Attribution"

**What you see:** 50 CTV campaigns with purchase value, ROAS, and completion-to-purchase rate charts.

**Note:** Impression-level CTV data is not publicly available from AdRoll. Attribution is based on matched conversion events.

**The story:** CTV campaigns validated by actual card swipes. Kargo buyers ask "prove CTV works." This is the proof — which campaigns drive real purchases, and at what ROAS.

| Element | Table |
|---------|-------|
| CTV attribution | `AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_CTV_ATTRIBUTION` |

### Tab 6 — "ML Models + Features"

**What you see:** 5 AdRoll-specific ML models, decile lift chart (3.22x), side-by-side feature importance (Conversion vs Funnel), holdout validation.

**The story:** 5 Snowflake ML models trained on AdRoll data. The Conversion Classifier (3.22x top decile lift) predicts which pixel conversions are real card swipes. The Funnel Predictor identifies future purchasers from engagement behavior before they convert. ATTRIBUTED_REVENUE is the #1 feature for conversion; COMPOSITE_PROPENSITY (Affinity's score) is #1 for the funnel model.

| Element | Table |
|---------|-------|
| Model registry | `AFFINITY_DEMO.ML.MODEL_REGISTRY` (ADROLL%) |
| Decile lift | `AFFINITY_DEMO.ML.ADROLL_CONVERSION_DECILES` |
| Feature importance | `AFFINITY_DEMO.ML.ADROLL_FEATURE_IMPORTANCE` |
| Holdout | `AFFINITY_DEMO.ML.ADROLL_HOLDOUT_RESULTS` |

---

## Dashboard 6: Cross-Platform Comparison

**Streamlit app:** `AFFINITY_DEMO.APPS.CROSS_PLATFORM_COMPARISON`
**Show this last as a wrap-up, or use tab 4 as a standalone closing slide. 4 tabs. Now covers all 4 platforms.****

### Tab 1 — "Match Rates"

**What you see:** 4 metric cards with progress bars (AdRoll 80.6%, TTD 44.8%, PubMatic 26.2%, Kargo 22.5%), stacked bar chart of all match methods by platform, detail table.

**The story:** One data asset — Affinity's 300M+ cards — four different match rates. AdRoll leads because email SHA-256 is deterministic. The same purchase data creates value at every layer of the ad stack.

| Element | Table |
|---------|-------|
| TTD/PubMatic/Kargo match data | `AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY` |
| AdRoll match data | `AFFINITY_DEMO.CLEANROOM.ADROLL_MATCH_RATE_SUMMARY` |

### Tab 2 — "Platform Outputs"

**What you see:** 2x2 grid: TTD + AdRoll on top, PubMatic + Kargo below. Each shows its unique outputs and record counts. ML model count by platform at bottom.

**The story:** Same input, four different outputs. TTD gets bidding rules. AdRoll gets funnel intelligence + B2B account scores. PubMatic gets yield scores. Kargo gets engagement attribution. Each platform gets exactly what it needs.

| Element | Table |
|---------|-------|
| TTD rules | `AFFINITY_DEMO.ML.BIDDING_RULES` |
| AdRoll funnel rules | `AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_FUNNEL_PURCHASE_RULES` |
| AdRoll B2B scores | `AFFINITY_DEMO.ADROLL_B2B.ADROLL_ACCOUNT_SCORES` |
| PubMatic yields | `AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_INVENTORY_YIELD_SCORES` |
| PubMatic SSP rules | `AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_SSP_BIDDING_RULES` |
| Kargo ML rules | `AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_ML_ENGAGEMENT_RULES` |
| Kargo CTV | `AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_CTV_ATTRIBUTION` |

### Tab 3 — "ML Models"

**What you see:** Full model registry (12 models) with platform filter dropdown, decile lift comparison bar chart across all 4 platforms.

**The story:** 12 Snowflake ML models trained across four platforms. Platform filter lets you drill into any platform's models. The decile lift comparison shows Kargo (3.45x) and AdRoll (3.22x) have the strongest ML separation.

| Element | Table |
|---------|-------|
| Model registry (12 models) | `AFFINITY_DEMO.ML.MODEL_REGISTRY` |

### Tab 4 — "The Pitch"

**What you see:** Markdown narrative with 5-column comparison table (DSP vs Retargeting vs SSP vs Ad Server) and differentiator callout.

**The story:** One data asset. Four platform types. Four problems solved. The differentiator: rules, not audiences.

**End on the quote:** *"Rules, not audiences."*

---

## Quick Reference — All Data Tables

| Schema | Table | Used In |
|--------|-------|---------|
| `AFS_PROVIDER` | `TX_SRC_V` | Pipeline tab 1 |
| `AFS_PROVIDER` | `CC_EXT_V` | Pipeline tab 1 |
| `AFS_PROVIDER` | `PREDICTION_FEED_V` | Pipeline tab 4 |
| `TTD_CONSUMER` | `REDS_IMPRESSIONS` | Pipeline tab 1 |
| `TTD_CONSUMER` | `REDS_CONVERSIONS` | Pipeline tab 1 |
| `TTD_CONSUMER` | `DEMO_OUTPUT_CONVERSION_ENRICHMENT` | Pipeline tab 4, TTD tab 5 |
| `TTD_CONSUMER` | `DEMO_OUTPUT_PREDICTION_MULTIPLIERS` | Cross-Platform tab 2 |
| `PUBMATIC_CONSUMER` | `DEMO_OUTPUT_INVENTORY_YIELD_SCORES` | PubMatic tab 1, Cross-Platform tab 2 |
| `PUBMATIC_CONSUMER` | `DEMO_OUTPUT_FLOOR_RECOMMENDATIONS` | PubMatic tab 2 |
| `PUBMATIC_CONSUMER` | `DEMO_OUTPUT_PURCHASE_INVENTORY_PACKAGES` | PubMatic tab 3 |
| `PUBMATIC_CONSUMER` | `DEMO_OUTPUT_SSP_BIDDING_RULES` | PubMatic tab 4 |
| `PUBMATIC_CONSUMER` | `DEMO_OUTPUT_PUBLISHER_MULTIPLIERS` | PubMatic tab 4 |
| `KARGO_CONSUMER` | `DEMO_OUTPUT_PLACEMENT_PURCHASE_SCORES` | Kargo tab 1 |
| `KARGO_CONSUMER` | `DEMO_OUTPUT_CTV_ATTRIBUTION` | Kargo tab 2, Cross-Platform tab 2 |
| `KARGO_CONSUMER` | `DEMO_OUTPUT_ENGAGEMENT_PURCHASE_ATTR` | Cross-Platform tab 2 |
| `KARGO_CONSUMER` | `DEMO_OUTPUT_ENGAGEMENT_QUALITY_RULES` | Kargo tab 3 |
| `KARGO_CONSUMER` | `DEMO_OUTPUT_ML_ENGAGEMENT_RULES` | Kargo tab 4 |
| `CLEANROOM` | `MATCH_RATE_SUMMARY` | Pipeline tab 3, TTD tab 6, PubMatic tab 6, Kargo tab 6, Cross-Platform tab 1 |
| `CLEANROOM` | `ADROLL_MATCH_RATE_SUMMARY` | AdRoll tab 2, Pipeline tab 3, Cross-Platform tab 1 |
| `CLEANROOM` | `CROSSWALK_ADROLL` | AdRoll identity matching |
| `CLEANROOM` | `GROUND_TRUTH_ADROLL` | AdRoll purchase labels |
| `ML` | `BIDDING_RULES` | Pipeline tab 6, TTD tab 1, Cross-Platform tab 2 |
| `ML` | `MODEL_REGISTRY` | Pipeline tab 5, TTD tab 4, PubMatic tab 5, Kargo tab 5, Cross-Platform tab 3 |
| `ML` | `MODEL_VALIDATION_PURCHASE_DECILES` | Pipeline tab 5, TTD tab 4, Cross-Platform tab 3 |
| `ML` | `MODEL_VALIDATION_FEATURE_IMPORTANCE` | Pipeline tab 5, TTD tab 4, Cross-Platform tab 3 |
| `ML` | `MODEL_VALIDATION_PURCHASE_CONFUSION` | TTD tab 4 |
| `ML` | `TRAINING_SET_TTD` | TTD tab 3 |
| `ML` | `VALIDATION_HOLDOUT_RESULTS` | TTD tab 3 |
| `ML` | `ACCURACY_PROOF` | TTD tab 5 |
| `ML` | `TRAINING_SET_PUBMATIC` | PubMatic tab 5 |
| `ML` | `PUBMATIC_VALIDATION_DECILES` | PubMatic tab 5 |
| `ML` | `PUBMATIC_FEATURE_IMPORTANCE` | PubMatic tab 5 |
| `ML` | `PUBMATIC_HOLDOUT_RESULTS` | PubMatic tab 5 |
| `ML` | `TRAINING_SET_KARGO` | Kargo tab 5 |
| `ML` | `KARGO_VALIDATION_DECILES` | Kargo tab 5 |
| `ML` | `KARGO_FEATURE_IMPORTANCE` | Kargo tab 5 |
| `ML` | `KARGO_HOLDOUT_RESULTS` | Kargo tab 5 |
| `ML` | `DELIVERY_PER_ID_INSTRUCTION` | Pipeline tab 6, TTD tab 2 |
| `ML` | `DELIVERY_VALUE_BASED_BIDDING` | Pipeline tab 6, TTD tab 2 |
| `AI` | `QUADRANT_SUMMARY_V` | Pipeline tab 6, TTD tab 2 |
| `ADROLL_CONSUMER` | `ADROLL_FUNNEL_PURCHASE_RULES` | AdRoll tab 3, Cross-Platform tab 2 |
| `ADROLL_CONSUMER` | `ADROLL_CHANNEL_ATTRIBUTION` | AdRoll tab 1, AdRoll tab 2 |
| `ADROLL_CONSUMER` | `ADROLL_CTV_ATTRIBUTION` | AdRoll tab 5 |
| `ADROLL_CONSUMER` | `ADROLL_AUDIENCE_SEGMENTS` | AdRoll reference |
| `ADROLL_B2B` | `ADROLL_ACCOUNT_SCORES` | AdRoll tab 4, Cross-Platform tab 2 |
| `ADROLL_B2B` | `ADROLL_SITE_TRAFFIC_REVEALER` | AdRoll firmographics source |
| `ML` | `ADROLL_CONVERSION_DECILES` | AdRoll tab 6 |
| `ML` | `ADROLL_FEATURE_IMPORTANCE` | AdRoll tab 6 |
| `ML` | `ADROLL_HOLDOUT_RESULTS` | AdRoll tab 6 |

All tables live in database `AFFINITY_DEMO`.
