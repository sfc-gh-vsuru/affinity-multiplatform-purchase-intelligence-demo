# Custom Algo Optimization — Turning Purchase Data into Smarter Ad Decisions

---

## The Big Picture

Every ad platform — whether it buys ads, sells ad space, serves ads, or retargets shoppers — faces the same blind spot: **they can see the ad, but they can't see the cash register.**

A DSP knows it served an ad. An SSP knows it sold the impression. A publisher knows someone watched the video. A retargeting platform knows someone clicked.

**But did anyone actually buy anything?**

The answer lives in credit and debit card transaction data — 300 million cards, 160 million consumers, 5,300+ brands, refreshed daily. That's the missing half of every ad decision.

**Custom Algo Optimization** bridges these two worlds. Inside a secure, privacy-preserving environment, we connect ad exposure data with verified purchase outcomes — and then train machine learning models that turn that connection into action.

The result isn't a scored audience list. It's a set of **plain-language rules** that each platform can load into its existing systems today — no integration project, no identity dependency at decision time, no black box.

> *One purchase dataset. Four platform types. Four problems solved.*

---

## How It Works — Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   LAYER 1: THE DATA                                        │
│   Purchase outcomes + Ad platform signals                  │
│                                                             │
│   ┌─────────────────┐        ┌───────────────────────────┐ │
│   │  Purchase Data   │        │  Ad Platform Data          │ │
│   │                  │        │                            │ │
│   │  • Card swipes   │        │  • Ad impressions          │ │
│   │  • Real dollars  │        │  • Clicks & video views    │ │
│   │  • Brand & store │        │  • Device & location       │ │
│   │  • 300M+ cards   │        │  • Publisher & content     │ │
│   └────────┬─────────┘        └────────────┬───────────────┘ │
│            │                               │                │
│            ▼                               ▼                │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   LAYER 2: THE SECURE CONNECTION                    │   │
│   │   Data Clean Room — privacy-preserving match        │   │
│   │                                                     │   │
│   │   • Neither side sees the other's raw data          │   │
│   │   • Match on hashed identifiers only                │   │
│   │   • Output: "this ad viewer bought this product"    │   │
│   │                                                     │   │
│   └──────────────────────┬──────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   LAYER 3: THE INTELLIGENCE                         │   │
│   │   Machine learning → Actionable rules               │   │
│   │                                                     │   │
│   │   "When you see THIS combination of signals,        │   │
│   │    the viewer is 3x more likely to purchase."       │   │
│   │                                                     │   │
│   │   Output: BOOST (spend more) or SUPPRESS (save it)  │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## The Purchase Data — What Makes This Possible

A data provider covers roughly half of all US households through credit and debit card transaction records. This isn't survey data or modeled estimates — it's **verified card swipes** at the point of sale.

| What's in it | Why it matters |
|---|---|
| 12 million+ transactions | Real purchase behavior, not self-reported |
| 5,300+ tracked brands | Covers major retailers, restaurants, e-commerce |
| Prediction models per consumer | "Will this person buy this brand?" and "How much will they spend?" |
| Daily refresh | Not a static snapshot — living, breathing purchase signal |

This data has never been available to ad platforms before. They've been optimizing in the dark — guessing which ads drive purchases based on pixels and clicks. Now they can know.

---

## The Four Platform Solutions

Each solution targets a different type of ad platform. Same purchase data, same secure connection, same machine learning approach — but the output is tailored to how each platform actually makes decisions.

| Solution | Platform Type | The Question It Answers |
|---|---|---|
| **Solution 1** | Demand-Side Platform (ad buyer) | "Which impressions should I bid more on?" |
| **Solution 2** | Supply-Side Platform (ad seller) | "Which inventory actually drives purchases?" |
| **Solution 3** | Ad Server / Publisher | "Which content and formats lead to real sales?" |
| **Solution 4** | Retargeting Platform | "Which conversions are real — and who's next?" |

---

## Solution 1: The Ad Buyer (DSP)

### The Problem

A demand-side platform buys billions of ad impressions every day. For each one, it decides in milliseconds: **how much should I bid?**

Today, that bid decision is based on the platform's own conversion pixel. But a pixel only fires when someone takes an online action — it misses the vast majority of purchases that happen with a physical card swipe at a store, a restaurant, or through a different channel.

The result: the platform is bidding blind on the most valuable signal — **did someone actually buy something?**

### What We Do

1. **Connect** the platform's ad exposure data (who saw which ads, on what device, at what time, on which publisher) with verified purchase outcomes through a secure clean room

2. **Train** machine learning models on the combined data — the model learns which combinations of ad signals predict real purchases

3. **Generate rules** the platform's bidder can use immediately:
   - *"Desktop impressions on sports content in the top 20 metro areas → bid 1.8x more"*
   - *"Mobile impressions on news sites after midnight → bid 0.4x less"*

### What the Platform Gets

| Output | What it is |
|---|---|
| **394 bidding rules** | Plain-language conditions with bid multipliers — load directly into the existing bidder |
| **Prediction multipliers** | Per-individual bid adjustments based on purchase likelihood |
| **Four-quadrant strategy** | Net-New Prospects (bid aggressively), Conquesting (steal share), High-Value VIPs (expand wallet), Waste (suppress) |
| **Three delivery formats** | Audience + multiplier table, per-ID instruction file, value-based bidding feed |

### The Proof

The top 10% of ML-scored impressions purchase at **2.15x the baseline rate**. The model identifies where to concentrate spend — and equally important, where to stop wasting it.

A held-back test group (impressions the model never trained on) confirms these results hold up in the real world. This isn't overfitting — it's a genuine signal.

### Why Rules, Not Audiences

Traditional approach: hand the platform a list of user IDs to target. This requires identity resolution at bid time, creates privacy exposure, and locks the buyer into the data vendor.

Our approach: hand the platform **rules over dimensions it already has** at bid time (device type, publisher, geography, time of day, content genre). No identity needed. No integration project. No lock-in. The rules are human-readable and auditable — any buyer can inspect exactly what the model learned and decide whether to trust it.

---

## Solution 2: The Ad Seller (SSP)

### The Problem

A supply-side platform sells ad space on behalf of publishers. Its core challenge: **set the right floor price** for every piece of inventory.

Set the floor too high — the ad slot goes unsold. Set it too low — you leave money on the table.

Today, floor pricing is based on historical auction data and category estimates. The SSP knows what advertisers *paid* but not what those impressions *caused*. A $2 CPM impression that drives a $200 purchase is wildly underpriced. A $15 CPM impression that drives nothing is overpriced.

Without purchase data, the SSP is pricing blind.

### What We Do

1. **Connect** the SSP's bid-request data (publisher, ad format, device, geography, content) with verified purchase outcomes

2. **Score every inventory combination** by its ability to drive real purchases — creating a "yield multiplier" that separates high-performing supply from low-performing supply

3. **Generate floor recommendations and premium packages** backed by actual purchase evidence

### What the Platform Gets

| Output | What it is |
|---|---|
| **Inventory yield scores** | Purchase conversion rate for every publisher × format × device × geography combination |
| **Floor recommendations** | Suggested floor prices based on purchase-driving potential — not just auction history |
| **Premium packages** | Pre-built inventory bundles for advertisers, each backed by "this supply drives X% purchase rate" |
| **271 SSP pricing rules** | BOOST (set higher floor — this converts) and SUPPRESS (accept lower bids — this doesn't) |

### The Proof

The top 10% of ML-scored inventory converts at **2.5x the baseline rate**. The strongest predictor? The SSP's own floor price — meaning the platform's existing pricing signal, combined with purchase data, becomes dramatically more powerful.

### The Pitch to Advertisers

This changes what the SSP can say to its advertising clients. Instead of *"here's our inventory, trust us it's good"*, the SSP can say *"here's inventory that is proven to drive real purchases at 2.5x the average rate — here's the data."* That's a premium conversation backed by evidence.

---

## Solution 3: The Publisher / Ad Server

### The Problem

A publisher or ad server has the richest engagement data in the ecosystem — they know exactly what happened after the ad was shown. Did the viewer watch the whole video? Was the ad actually visible on screen? Did they click?

But engagement is not the same as purchase. A viewer who watches a 30-second video ad to completion might never buy the product. A viewer who barely glances at a banner might walk into the store that afternoon.

Publishers charge premium prices for high-engagement formats (especially connected TV). But they can't prove those formats drive actual sales — and without that proof, advertisers push back on the premium.

### What We Do

1. **Connect** the publisher's engagement data (viewability, video completion, creative format, placement, device) with verified purchase outcomes

2. **Score every combination** of creative format, publisher, placement, and device by real purchase conversion — not just engagement metrics

3. **Generate attribution evidence** the publisher can take directly to advertisers: *"this CTV app drives 3x the purchase rate of standard display"*

### What the Platform Gets

| Output | What it is |
|---|---|
| **Placement purchase scores** | Every placement × format × publisher ranked by verified purchase rate |
| **CTV attribution** | Connected TV platforms and apps ranked by actual purchase conversion — the proof CTV buyers need |
| **Engagement quality rules** | 191 rules separating engagement that leads to purchase from engagement that doesn't |
| **Advertiser-ready reports** | Per-campaign, full journey from ad view to card swipe |

### The Proof

The top 10% of ML-scored engagements convert at **3.45x the baseline rate** — the strongest lift of any platform type. The model's #1 signal is the purchase prediction score itself, followed by publisher name and geography. This validates what publishers have always believed: content quality matters — and now there's purchase data to prove it.

### Why This Matters for CTV

Connected TV is the fastest-growing and most expensive ad format. Advertisers are spending more on CTV but demanding proof it works. This solution provides exactly that — which CTV apps, which shows, which devices actually drive viewers to purchase. That evidence justifies the premium and defends CTV budgets.

---

## Solution 4: The Retargeting Platform

### The Problem

A retargeting platform tracks the full marketing funnel — from first website visit through product search, add-to-cart, and purchase. It attributes conversions through a tracking pixel.

But a pixel captures **intent**, not **outcome**. Someone who adds an item to a cart and then abandons the session might still buy the product in a store. Someone who completes an online checkout might return the item the next day.

The platform is also uniquely positioned in B2B: it can identify which *companies* are visiting an advertiser's website (industry, revenue, headcount). But it can't tell which of those companies will actually purchase — that requires real transaction data.

### What We Do

1. **Connect** the platform's conversion events and website visit data with verified purchase outcomes using email-based matching — the strongest deterministic match of any platform (80.6% match rate)

2. **Verify** which pixel-reported conversions represent actual card-swipe purchases — revealing which channels over-count and which under-count

3. **Generate funnel intelligence rules** from millions of engagement events: which behaviors predict real purchases before a conversion even fires

4. **Score B2B accounts** by combining website visitor firmographics (industry, revenue, headcount) with actual purchase propensity — something no other platform type can do

### What the Platform Gets

| Output | What it is |
|---|---|
| **Channel attribution** | Side-by-side: what the pixel reported vs what the card data verified, per channel |
| **120 funnel rules** | ML-derived rules from 10M events: "Channel=web AND Device=desktop → BOOST" |
| **B2B account scores** | 5,000 companies scored HOT / WARM / COLD by real purchase propensity |
| **CTV campaign validation** | 50 video campaigns ranked by verified purchase value and return on ad spend |
| **Audience segments** | 30 purchase-verified audience segments for immediate activation |

### The Proof

The top 10% of ML-scored conversions are **3.22x more likely** to represent real purchases. Five machine learning models cover the full spectrum: which conversions are real, how much they'll spend, who will purchase next, which companies are highest value, and where brand spend is heading.

The B2B account scoring is the standout — **no other platform type has this capability**. Visit frequency (how often employees visit the site) turns out to be a stronger purchase predictor than company size or revenue. The ML validates the sales funnel: companies further in their buying journey (qualified leads, active opportunities) have the highest purchase scores.

### The Match Rate Advantage

This platform matches at 80.6% — far above the DSP (44.8%), SSP (26.2%), or publisher (22.5%). The reason: email-based matching is deterministic. There's no probabilistic graph, no identity decay, no uncertainty. Every match is an individual-level link between an ad event and a card swipe.

---

## The Cross-Platform Story

The same purchase data, the same secure clean room technology, the same machine learning approach — but four completely different outputs, each shaped for how that platform actually operates.

```
                        ┌──────────────────┐
                        │   Purchase Data   │
                        │   300M+ cards     │
                        │   5,300+ brands   │
                        └────────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
          ┌─────────┴──┐  ┌─────┴─────┐  ┌──┴──────────┐
          │            │  │           │  │             │
          ▼            ▼  ▼           ▼  ▼             ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐
   │  Ad Buyer  │ │  Ad Seller │ │ Publisher  │ │ Retargeting  │
   │  (DSP)     │ │  (SSP)     │ │ (Ad Server)│ │  Platform    │
   ├────────────┤ ├────────────┤ ├────────────┤ ├──────────────┤
   │ 394 bid    │ │ 271 floor  │ │ 191 engage-│ │ 120 funnel   │
   │ rules      │ │ pricing    │ │ ment rules │ │ rules +      │
   │            │ │ rules      │ │            │ │ B2B scores   │
   ├────────────┤ ├────────────┤ ├────────────┤ ├──────────────┤
   │ "Bid more  │ │ "Price     │ │ "This CTV  │ │ "This pixel  │
   │  on this"  │ │  this      │ │  format    │ │  conversion  │
   │            │ │  higher"   │ │  works"    │ │  is real"    │
   └────────────┘ └────────────┘ └────────────┘ └──────────────┘
```

### What's different from everyone else

| What competitors do | What this solution does |
|---|---|
| Sell scored audience lists | Deliver interpretable rules over existing signals |
| Require identity at decision time | Rules use dimensions available at decision time — no identity needed |
| Black-box model outputs | Every rule is human-readable and auditable |
| Lock the buyer into the vendor | Rules drop into existing systems with no integration project |
| Single-platform applicability | Same approach works across DSPs, SSPs, publishers, and retargeting |

---

## Powered By

| Capability | Role in the Solution |
|---|---|
| **Data Clean Room** | The secure environment where purchase data meets ad data — neither side sees the other's raw information |
| **Identity Resolution** | Eight matching methods (email hash, device ID, IP, name+address variants) connect ad viewers to card holders without exposing personal information |
| **Machine Learning** | 12 models trained inside the clean room boundary — purchase outcomes as labels, ad signals as features, rules as output |
| **Interactive Dashboards** | Six applications that let each platform explore their data, understand the rules, and validate the results — built for demo conversations and ongoing analysis |

---

## The Numbers

| Metric | Value |
|---|---|
| Platforms covered | 4 (DSP, SSP, Ad Server, Retargeting) |
| ML models trained | 12 |
| Total rules generated | 976 across all platforms |
| Strongest ML separation | 3.45x (publisher) and 3.22x (retargeting) top-decile lift |
| Highest match rate | 80.6% (retargeting, email-based) |
| Purchase data coverage | ~50% of US households |
| Brands tracked | 5,300+ |
| B2B companies scored | 5,000 (retargeting only) |

---

*One purchase dataset. Four platform types. Four problems solved.*
*Rules, not audiences.*
