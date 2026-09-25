# Affinity Solutions x AdRoll — Solution Architecture

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                              ║
║               AFFINITY SOLUTIONS  x  ADROLL / NEXTROLL  —  PURCHASE INTELLIGENCE ARCHITECTURE                ║
║                                 Powered by Snowflake Data Clean Rooms + ML                                   ║
║                                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝


      ┌─ AFFINITY (Provider) ────────────────────────┐       ┌─ ADROLL / NEXTROLL (Consumer) ─────────────────────────┐
      │                                              │       │                                                        │
      │  ╔═══════════════════════════════════════╗   │       │   ╔═════════════════════════════════════════════════╗   │
      │  ║      AFS_PROVIDER  Schema             ║   │       │   ║       ADROLL_CONSUMER  Schema                   ║   │
      │  ║                                       ║   │       │   ║                                                 ║   │
      │  ║  ┌──────────────┐  ┌──────────────┐   ║   │       │   ║  ┌─────────────────┐  ┌───────────────────┐     ║   │
      │  ║  │ TX_SRC_V     │  │ CC_EXT_V     │   ║   │       │   ║  │ ADROLL_GCR      │  │ ADROLL_S2S_EVENTS │     ║   │
      │  ║  │ 12M txns     │  │ 134K cards   │   ║   │       │   ║  │ 2.2M convers.   │  │ 10M funnel events │     ║   │
      │  ║  │ daily swipes │  │ 100K indiv.  │   ║   │       │   ║  │ 28 fields       │  │ 13 event types    │     ║   │
      │  ║  │ $, date, MID │  │ demo, geo    │   ║   │       │   ║  │ email_sha256    │  │ email_sha256      │     ║   │
      │  ║  └──────────────┘  └──────────────┘   ║   │       │   ║  │ channel, device │  │ full B2C + B2B    │     ║   │
      │  ║  ┌──────────────┐  ┌──────────────┐   ║   │       │   ║  │ revenue ($)     │  │ funnel signals    │     ║   │
      │  ║  │ PREDICTION   │  │ CUSTOMER_    │   ║   │       │   ║  └─────────────────┘  └───────────────────┘     ║   │
      │  ║  │ _FEED_V      │  │ CC_MAP_V     │   ║   │       │   ║  ┌─────────────────┐                           ║   │
      │  ║  │ 1M rows      │  │ 100K xwalk   │   ║   │       │   ║  │ CAMPAIGN_METRICS │  B2C Funnel:              ║   │
      │  ║  │ propensity   │  │ INDID ↔ AFS  │   ║   │       │   ║  │ 94.5K rows      │  pageView → productSearch ║   │
      │  ║  │ pred. spend  │  │              │   ║   │       │   ║  │ CTV + video     │    → addToCart → purchase  ║   │
      │  ║  │ TOP 1/5/10%  │  │              │   ║   │       │   ║  │ ROAS, CPA       │  B2B Funnel:              ║   │
      │  ║  └──────────────┘  └──────────────┘   ║   │       │   ║  └─────────────────┘  demoRequest → contactSales║   │
      │  ║  ┌──────────────┐  ┌──────────────┐   ║   │       │   ║                         → signupTrial           ║   │
      │  ║  │ MID_SRC_V    │  │ Brand/Cat    │   ║   │       │   ╚═════════════════════════════════════════════════╝   │
      │  ║  │ 565 merchant │  │ Taxonomy     │   ║   │       │                                                        │
      │  ║  │ descriptors  │  │ 113 brands   │   ║   │       │   ╔═════════════════════════════════════════════════╗   │
      │  ║  └──────────────┘  │ 53 categories│   ║   │       │   ║       ADROLL_B2B  Schema                        ║   │
      │  ║                    │ 5,300+ prod   │   ║   │       │   ║       (Unique to AdRoll — no other platform)    ║   │
      │  ║                    └──────────────┘   ║   │       │   ║                                                 ║   │
      │  ╚═══════════════════════════════════════╝   │       │   ║  ┌─────────────────────────────────────────┐     ║   │
      │                                              │       │   ║  │ ADROLL_SITE_TRAFFIC_REVEALER            │     ║   │
      │  300M+ cards │ 160M consumers │ daily refresh │       │   ║  │ 5,000 companies visiting advertiser     │     ║   │
      │  ~50% of US households covered               │       │   ║  │ site — reverse IP + firmographic DB     │     ║   │
      │                                              │       │   ║  │                                         │     ║   │
      └────────────────────┬─────────────────────────┘       │   ║  │  Fields:                                │     ║   │
                           │                                 │   ║  │  • domain, company_name                 │     ║   │
                           │                                 │   ║  │  • industry (~150 values)               │     ║   │
                           ▼                                 │   ║  │  • revenue (7 buckets: <$1M to >$1B)    │     ║   │
                                                             │   ║  │  • size (8 buckets: 1-10 to >10,000)    │     ║   │
╔══════════════════════════════════════════════════════╗      │   ║  │  • journey_stage (Unaware → Opportunity)│     ║   │
║                                                      ║      │   ║  │  • total_visits, total_visitors         │     ║   │
║    ██████╗  █████╗ ████████╗ █████╗                   ║      │   ║  │  • contact_email_sha256                │     ║   │
║    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗                  ║      │   ║  └─────────────────────────────────────────┘     ║   │
║    ██║  ██║███████║   ██║   ███████║                  ║      │   ╚═════════════════════════════════════════════════╝   │
║    ██║  ██║██╔══██║   ██║   ██╔══██║                  ║      │                                                        │
║    ██████╔╝██║  ██║   ██║   ██║  ██║                  ║      └────────────────────────┬───────────────────────────────┘
║    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝                  ║                               │
║                                                      ║                               │
║     ██████╗██╗     ███████╗ █████╗ ███╗   ██╗        ║                               │
║    ██╔════╝██║     ██╔════╝██╔══██╗████╗  ██║        ║                               │
║    ██║     ██║     █████╗  ███████║██╔██╗ ██║        ║                               │
║    ██║     ██║     ██╔══╝  ██╔══██║██║╚██╗██║        ║                               │
║    ╚██████╗███████╗███████╗██║  ██║██║ ╚████║        ║                               │
║     ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝        ║                               │
║                                                      ║                               │
║    ██████╗  ██████╗  ██████╗ ███╗   ███╗             ║                               │
║    ██╔══██╗██╔═══██╗██╔═══██╗████╗ ████║             ║                               │
║    ██████╔╝██║   ██║██║   ██║██╔████╔██║             ║                               │
║    ██╔══██╗██║   ██║██║   ██║██║╚██╔╝██║             ║                               │
║    ██║  ██║╚██████╔╝╚██████╔╝██║ ╚═╝ ██║             ║                               │
║    ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝             ║                               │
║                                                      ║                               │
║  SNOWFLAKE DATA CLEAN ROOM — CLEANROOM Schema        ║                               │
║  ═════════════════════════════════════════════        ║                               │
║                                                      ║                               │
║  ┌────────────────────────────────────────────────┐  ║                               │
║  │           CONSUMER PURCHASE CONNECT             │  ║◄──────────────────────────────┘
║  │        (Affinity's Native App — mirrored)       │  ║
║  │                                                 │  ║
║  │  Cleanroom procs:  CLEANSING_HASHING            │  ║
║  │                    GET_CONNECT_ID                │  ║
║  │                    SINGLE_ID_MATCHING            │  ║
║  │                    WATERFALL_MATCHING            │  ║
║  └──────────────────────┬─────────────────────────┘  ║
║                         │                            ║
║                         ▼                            ║
║  ┌──────────────────────────────────────────────┐    ║
║  │         IDENTITY RESOLUTION WATERFALL         │    ║
║  │                                               │    ║
║  │  AdRoll Primary Match:                        │    ║
║  │  ┌─────────────────────────────────────────┐  │    ║
║  │  │  EMAIL SHA-256  (HEM1)                  │  │    ║
║  │  │  Deterministic • Highest confidence     │  │    ║
║  │  │  ══════════════════════════ 80.6% match │  │    ║
║  │  └─────────────────────────────────────────┘  │    ║
║  │                                               │    ║
║  │  Fallback:                                    │    ║
║  │  ┌─────────────────────────────────────────┐  │    ║
║  │  │  IP ADDRESS  (IPA1)                     │  │    ║
║  │  │  Household level • Non-logged-in events │  │    ║
║  │  └─────────────────────────────────────────┘  │    ║
║  │                                               │    ║
║  │  Why 80.6%? email_sha256 is deterministic —   │    ║
║  │  no graph, no probabilistic decay.            │    ║
║  │  Strongest match of any platform:             │    ║
║  │    AdRoll 80.6% > TTD 44.8% > PM 26.2%       │    ║
║  │                          > Kargo 22.5%        │    ║
║  └──────────────────────┬────────────────────────┘    ║
║                         │                            ║
║                         ▼                            ║
║  ┌──────────────────────────────────────────────┐    ║
║  │         CROSSWALK OUTPUT                      │    ║
║  │                                               │    ║
║  │  CROSSWALK_ADROLL  (80,578 matched pairs)     │    ║
║  │  ┌───────────────┐    ┌───────────────────┐   │    ║
║  │  │ ADROLL        │    │ AFFINITY          │   │    ║
║  │  │ email_sha256  │───▶│ CLIENT_AFS_INDID  │   │    ║
║  │  │ (consumer ID) │    │ CLIENT_AFS_HHID   │   │    ║
║  │  └───────────────┘    │ MATCH_CODE: HEM1  │   │    ║
║  │                       │ MATCH_LEVEL: IND  │   │    ║
║  │  No raw PII crosses   └───────────────────┘   │    ║
║  │  the boundary. Hash                           │    ║
║  │  in, ID out.                                  │    ║
║  └──────────────────────┬────────────────────────┘    ║
║                         │                            ║
╚═════════════════════════╪════════════════════════════╝
                          │
                          │  Matched population:
                          │  80,578 individuals with
                          │  both ad engagement +
                          │  verified card swipes
                          │
                          ▼
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                        ║
║                    SNOWFLAKE ML LAYER  —  ML Schema  (12 models total)                 ║
║                    All models trained inside clean room boundary                        ║
║                                                                                        ║
║  ┌─ TRAINING DATA ──────────────────────────────────────────────────────────────────┐   ║
║  │                                                                                  │   ║
║  │  TRAINING_SET_ADROLL_GCR     2.0M labeled conversions (GCR + purchase labels)    │   ║
║  │  TRAINING_SET_ADROLL_FUNNEL  200K labeled funnel events (S2S + purchase labels)  │   ║
║  │                                                                                  │   ║
║  │  Labels from:  CROSSWALK_ADROLL → CC_EXT_V → TX_SRC_V                           │   ║
║  │  Propensity:   COMPOSITE_PROPENSITY = BASE_RATE × dimension multipliers          │   ║
║  │  Assignment:   Deterministic hash draw vs propensity threshold                   │   ║
║  │                ABS(HASH(id, seed)) / 9223372036854775807.0                       │   ║
║  └──────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                        ║
║  ┌─ 5 ADROLL ML MODELS ────────────────────────────────────────────────────────────┐   ║
║  │                                                                                  │   ║
║  │  ┌────────────────────────────────────────────────────────────────────────────┐  │   ║
║  │  │  MODEL 1: ADROLL_CONVERSION_CLASSIFIER                                    │  │   ║
║  │  │  SNOWFLAKE.ML.CLASSIFICATION                                              │  │   ║
║  │  │                                                                            │  │   ║
║  │  │  Question: "Which pixel conversions are REAL card-swipe purchases?"        │  │   ║
║  │  │  Training:  2.0M GCR conversions with Affinity purchase labels             │  │   ║
║  │  │  Features:  attributed_revenue, channel, device, geo, attribution_type     │  │   ║
║  │  │  Result:    ★ 3.22x top-decile lift  │  Top 30% captures ~60% purchases   │  │   ║
║  │  │  #1 Feature: ATTRIBUTED_REVENUE (pixel $ predicts real $)                  │  │   ║
║  │  └────────────────────────────────────────────────────────────────────────────┘  │   ║
║  │                                                                                  │   ║
║  │  ┌────────────────────────────────────────────────────────────────────────────┐  │   ║
║  │  │  MODEL 2: ADROLL_REVENUE_CLASSIFIER                                       │  │   ║
║  │  │  SNOWFLAKE.ML.CLASSIFICATION                                              │  │   ║
║  │  │                                                                            │  │   ║
║  │  │  Question: "Among real purchasers, who spends HIGH / MEDIUM / LOW?"       │  │   ║
║  │  │  Used for: Value-based bidding — bid proportional to expected spend        │  │   ║
║  │  └────────────────────────────────────────────────────────────────────────────┘  │   ║
║  │                                                                                  │   ║
║  │  ┌────────────────────────────────────────────────────────────────────────────┐  │   ║
║  │  │  MODEL 3: ADROLL_FUNNEL_PREDICTOR                                         │  │   ║
║  │  │  SNOWFLAKE.ML.CLASSIFICATION                                              │  │   ║
║  │  │                                                                            │  │   ║
║  │  │  Question: "Who will purchase BEFORE they convert? (pre-conversion)"      │  │   ║
║  │  │  Training:  200K S2S funnel events with future-purchase labels             │  │   ║
║  │  │  Features:  event_type, channel, device, session_duration, page_depth      │  │   ║
║  │  │  #1 Feature: COMPOSITE_PROPENSITY (Affinity's score predicts behavior)     │  │   ║
║  │  │                                                                            │  │   ║
║  │  │  ★ This is the "predict before convert" model — AdRoll unique value        │  │   ║
║  │  └────────────────────────────────────────────────────────────────────────────┘  │   ║
║  │                                                                                  │   ║
║  │  ┌────────────────────────────────────────────────────────────────────────────┐  │   ║
║  │  │  MODEL 4: ADROLL_B2B_ACCOUNT_SCORER                                       │  │   ║
║  │  │  SNOWFLAKE.ML.CLASSIFICATION                                              │  │   ║
║  │  │                                                                            │  │   ║
║  │  │  Question: "Which companies will their employees actually purchase?"       │  │   ║
║  │  │  Input:     Site Traffic Revealer (5,000 companies) + Affinity purchase    │  │   ║
║  │  │  Features:  industry, revenue, size, journey_stage, total_visits           │  │   ║
║  │  │  Output:    HOT (806) / WARM (2,507) / COLD (1,687) account tiers         │  │   ║
║  │  │  #1 Feature: TOTAL_VISITS — engagement frequency > firmographics           │  │   ║
║  │  │                                                                            │  │   ║
║  │  │  ★ UNIQUE TO ADROLL — no other platform has B2B firmographic scoring       │  │   ║
║  │  └────────────────────────────────────────────────────────────────────────────┘  │   ║
║  │                                                                                  │   ║
║  │  ┌────────────────────────────────────────────────────────────────────────────┐  │   ║
║  │  │  MODEL 5: ADROLL_BRAND_FORECAST                                           │  │   ║
║  │  │  SNOWFLAKE.ML.FORECAST                                                    │  │   ║
║  │  │                                                                            │  │   ║
║  │  │  Question: "What will brand-level spend look like next month?"             │  │   ║
║  │  │  Input:     8,736 rows (brand × month time series)                         │  │   ║
║  │  │  Used for:  Campaign budget allocation and planning                        │  │   ║
║  │  └────────────────────────────────────────────────────────────────────────────┘  │   ║
║  │                                                                                  │   ║
║  └──────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                        ║
║  ┌─ VALIDATION ─────────────────────────────────────────────────────────────────────┐   ║
║  │                                                                                  │   ║
║  │  ADROLL_CONVERSION_DECILES    10 bins │ 3.22x top-decile lift                    │   ║
║  │  ADROLL_FEATURE_IMPORTANCE    40 features across 2 models (side-by-side)         │   ║
║  │  ADROLL_HOLDOUT_RESULTS       Training vs holdout — confirms generalization      │   ║
║  │  MODEL_REGISTRY               12 models across all 4 platforms                   │   ║
║  │                                                                                  │   ║
║  └──────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                        ║
╚══════════════════════════════════════════╤═══════════════════════════════════════════════╝
                                           │
                  ┌────────────────────────┼──────────────────────────┐
                  │                        │                          │
                  ▼                        ▼                          ▼
┌─────────────────────────┐  ┌──────────────────────────┐  ┌─────────────────────────────┐
│  FUNNEL INTELLIGENCE    │  │  CONVERSION ENRICHMENT   │  │  B2B ACCOUNT SCORING        │
│                         │  │                          │  │                             │
│  120 ML-derived rules   │  │  Channel Attribution     │  │  ADROLL_ACCOUNT_SCORES      │
│  BOOST / NEUTRAL /      │  │  ┌─────────┬──────────┐  │  │  5,000 companies scored     │
│  SUPPRESS               │  │  │ Channel │Pixel  vs │  │  │                             │
│                         │  │  │         │Card Swipe│  │  │  ┌──────────────────────┐    │
│  Each rule:             │  │  ├─────────┼──────────┤  │  │  │ HOT:  806 accounts   │    │
│  • Predicate            │  │  │ web     │ $1.2M vs │  │  │  │ WARM: 2,507 accounts │    │
│  • Lift (0.4x – 2.0x)  │  │  │         │ $1.8M    │  │  │  │ COLD: 1,687 accounts │    │
│  • Bid multiplier       │  │  │ social  │ $800K vs │  │  │  └──────────────────────┘    │
│  • Support (evidence)   │  │  │         │ $450K    │  │  │                             │
│  • Confidence interval  │  │  │ email   │ $500K vs │  │  │  Ranked by:                 │
│                         │  │  │         │ $900K    │  │  │  • Purchase score (ML)       │
│  Drops directly into    │  │  └─────────┴──────────┘  │  │  • Predicted account value   │
│  AdRoll's bidding       │  │                          │  │  • Industry × score chart    │
│  engine as predicates   │  │  True Purchase Rate %    │  │  • Journey stage validation  │
│                         │  │  by channel — reveals    │  │                             │
│  "Channel=web AND       │  │  over/under-counting     │  │  Firmographics + Affinity   │
│   Device=desktop"       │  │                          │  │  purchase data = scored ABM  │
│   → BOOST 1.4x         │  │  Match: 80.6% (email)    │  │                             │
└─────────────────────────┘  └──────────────────────────┘  └─────────────────────────────┘
                  │                        │                          │
                  └────────────────────────┼──────────────────────────┘
                                           │
                  ┌────────────────────────┤
                  │                        │
                  ▼                        ▼
┌─────────────────────────────┐  ┌──────────────────────────────────────────┐
│  CTV + VIDEO ATTRIBUTION    │  │  AUDIENCE SEGMENTS                       │
│                             │  │                                          │
│  ADROLL_CTV_ATTRIBUTION     │  │  ADROLL_AUDIENCE_SEGMENTS                │
│  50 CTV campaigns           │  │  30 segments                             │
│                             │  │                                          │
│  Per campaign:              │  │  Purchase-verified segments               │
│  • Video impressions        │  │  built from ML predictions               │
│  • Video completions        │  │  (retargeting, lookalike,                │
│  • CTV spend ($)            │  │   high-value, conquest)                  │
│  • Matched purchasers       │  │                                          │
│  • Purchase value ($)       │  │  Each segment has:                       │
│  • CTV ROAS                 │  │  • Estimated reach                       │
│  • Completion-to-purchase % │  │  • Conversion value                      │
│                             │  │  • Duration                              │
│  Note: Attribution uses     │  │                                          │
│  matched conversion events  │  │                                          │
│  (impression-level data     │  │                                          │
│  not publicly available)    │  │                                          │
└─────────────────────────────┘  └──────────────────────────────────────────┘
                  │                        │
                  └────────────────────────┘
                               │
                               ▼
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                        ║
║              STREAMLIT IN SNOWFLAKE  —  ADROLL_PURCHASE_INTELLIGENCE                   ║
║              Interactive dashboard  │  6 tabs  │  AFFINITY_DEMO.APPS                   ║
║              Warehouse: AFFINITY_DEMO_WH (Medium)                                      ║
║                                                                                        ║
║  ┌──────────────────────────────────────────────────────────────────────────────────┐   ║
║  │                                                                                  │   ║
║  │  ┌─Tab 1──────────┐ ┌─Tab 2──────────┐ ┌─Tab 3──────────┐                      │   ║
║  │  │ The Opportunity │ │ Conversion     │ │ Funnel         │                      │   ║
║  │  │                 │ │ Enrichment     │ │ Intelligence   │                      │   ║
║  │  │ • AdRoll vs     │ │                │ │                │                      │   ║
║  │  │   Affinity      │ │ • Channel      │ │ • 120 rules    │                      │   ║
║  │  │   side-by-side  │ │   attribution  │ │ • BOOST /      │                      │   ║
║  │  │ • Event counts  │ │   table        │ │   NEUTRAL /    │                      │   ║
║  │  │   vs txn counts │ │ • True purch.  │ │   SUPPRESS     │                      │   ║
║  │  │ • Channel       │ │   rate chart   │ │ • Filters by   │                      │   ║
║  │  │   revenue:      │ │ • 80.6% match  │ │   action, dim  │                      │   ║
║  │  │   Pixel vs      │ │   coverage     │ │ • Lift histo-  │                      │   ║
║  │  │   Card Swipe    │ │   (email SHA)  │ │   gram chart   │                      │   ║
║  │  └─────────────────┘ └────────────────┘ └────────────────┘                      │   ║
║  │                                                                                  │   ║
║  │  ┌─Tab 4──────────┐ ┌─Tab 5──────────┐ ┌─Tab 6──────────┐                      │   ║
║  │  │ B2B Account    │ │ CTV + Video    │ │ ML Models +    │                      │   ║
║  │  │ Scoring ★      │ │ Attribution    │ │ Features       │                      │   ║
║  │  │                 │ │                │ │                │                      │   ║
║  │  │ • HOT/WARM/    │ │ • 50 campaigns │ │ • 5 model      │                      │   ║
║  │  │   COLD tiers   │ │ • Purchase     │ │   registry     │                      │   ║
║  │  │ • Industry x   │ │   value chart  │ │   cards        │                      │   ║
║  │  │   score chart  │ │ • ROAS by      │ │ • Decile lift  │                      │   ║
║  │  │ • Top 20       │ │   campaign     │ │   chart 3.22x  │                      │   ║
║  │  │   accounts     │ │ • Completion-  │ │ • Feature imp. │                      │   ║
║  │  │ • Journey      │ │   to-purchase  │ │   side-by-side │                      │   ║
║  │  │   stage chart  │ │   rate         │ │ • Holdout      │                      │   ║
║  │  │   (ABM valid.) │ │                │ │   validation   │                      │   ║
║  │  └─────────────────┘ └────────────────┘ └────────────────┘                      │   ║
║  │                                                                                  │   ║
║  │  ★ = Unique to AdRoll (no other platform has B2B firmographic scoring)           │   ║
║  │                                                                                  │   ║
║  └──────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                        ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  CROSS-PLATFORM CONTEXT  —  Where AdRoll fits in the 4-platform story                  ║
║                                                                                        ║
║  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐                      ║
║  │    TTD     │ │  PubMatic  │ │   Kargo    │ │    AdRoll      │                      ║
║  │    DSP     │ │    SSP     │ │  Ad Server │ │  Retargeting   │                      ║
║  ├────────────┤ ├────────────┤ ├────────────┤ ├────────────────┤                      ║
║  │ Match      │ │ Match      │ │ Match      │ │ Match          │                      ║
║  │ 44.8%     │ │ 26.2%     │ │ 22.5%     │ │ ★ 80.6%       │                      ║
║  ├────────────┤ ├────────────┤ ├────────────┤ ├────────────────┤                      ║
║  │ Identity   │ │ Identity   │ │ Identity   │ │ Identity       │                      ║
║  │ MAID, IP,  │ │ UID2, IFA, │ │ RampID,   │ │ email SHA-256  │                      ║
║  │ UID2, Ramp │ │ RampID, IP │ │ IFA, IP   │ │ (deterministic)│                      ║
║  ├────────────┤ ├────────────┤ ├────────────┤ ├────────────────┤                      ║
║  │ ML Models  │ │ ML Models  │ │ ML Models  │ │ ML Models      │                      ║
║  │ 2 + shared │ │ 2          │ │ 2          │ │ ★ 5            │                      ║
║  │ 2.15x lift │ │ 2.5x lift  │ │ 3.45x lift │ │ 3.22x lift     │                      ║
║  ├────────────┤ ├────────────┤ ├────────────┤ ├────────────────┤                      ║
║  │ Output     │ │ Output     │ │ Output     │ │ Output         │                      ║
║  │ 394 bid    │ │ 271 SSP    │ │ 191 engage │ │ 120 funnel     │                      ║
║  │ rules +    │ │ rules +    │ │ rules +    │ │ rules +        │                      ║
║  │ quadrant   │ │ floor recs │ │ CTV attr   │ │ ★ B2B scores + │                      ║
║  │ multipliers│ │ + packages │ │            │ │ CTV + channel  │                      ║
║  └────────────┘ └────────────┘ └────────────┘ └────────────────┘                      ║
║                                                                                        ║
║  One data asset  →  Four platform types  →  Four problems solved                       ║
║  "Rules, not audiences."                                                               ║
║                                                                                        ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  SNOWFLAKE INFRASTRUCTURE                                                              ║
║                                                                                        ║
║  ┌─ Database ──────────────────────────────────────────────────────────────────────┐    ║
║  │  AFFINITY_DEMO                                                                  │    ║
║  │                                                                                  │    ║
║  │  Schemas (11):                                                                   │    ║
║  │  ├── AFS_PROVIDER ......... Affinity purchase data + predictions (14 tables)    │    ║
║  │  ├── TTD_CONSUMER ......... TTD REDS + CRM + identity spine                     │    ║
║  │  ├── PUBMATIC_CONSUMER .... OpenRTB impression log                              │    ║
║  │  ├── KARGO_CONSUMER ....... Kargo LLD events                                    │    ║
║  │  ├── ADROLL_CONSUMER ...... GCR + S2S + campaigns + ML outputs (8 tables)       │    ║
║  │  ├── ADROLL_B2B ........... Site Traffic Revealer + account scores (2 tables)   │    ║
║  │  ├── CLEANROOM ............ Crosswalks + match rate summaries (all platforms)    │    ║
║  │  ├── ML ................... 12 models, training sets, validation (40+ tables)    │    ║
║  │  ├── AI ................... Cortex AI views + quadrant strategy                  │    ║
║  │  ├── APPS ................. 6 Streamlit apps + stages                            │    ║
║  │  └── UTIL ................. Enum tables, generators                              │    ║
║  └──────────────────────────────────────────────────────────────────────────────────┘    ║
║                                                                                        ║
║  ┌─ Compute ───────────────┐  ┌─ Stages ───────────────────────────────────────────┐   ║
║  │ AFFINITY_GEN_WH (Large) │  │ @APPS.STREAMLIT_STAGE — 6 Streamlit app files      │   ║
║  │ Data gen + ML training  │  │ @APPS.DATA_STAGE — CSV data files for loading       │   ║
║  │                         │  │ @APPS.EXPORT_STAGE — Data export for git repo        │   ║
║  │ AFFINITY_DEMO_WH (Med.) │  └─────────────────────────────────────────────────────┘   ║
║  │ Streamlit + demo queries│                                                           ║
║  └─────────────────────────┘  ┌─ Security ──────────────────────────────────────────┐   ║
║                               │ • All data is synthetic (not real customer data)     │   ║
║  ┌─ ML Compute ────────────┐  │ • No raw PII crosses account boundaries             │   ║
║  │ SNOWFLAKE.ML.* uses     │  │ • Hash in, ID out (SHA-256 / SHA-512 / MD5)          │   ║
║  │ managed Snowflake       │  │ • Crosswalk lands only on consumer side              │   ║
║  │ compute — no warehouse  │  │ • ML output is aggregate rules, not individual scores│   ║
║  │ needed for model train  │  │ • Impression-level AdRoll data not available;         │   ║
║  └─────────────────────────┘  │   demo uses documented API-level schemas              │   ║
║                               └──────────────────────────────────────────────────────┘   ║
║                                                                                        ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝


  ┌─ DATA FLOW SUMMARY ──────────────────────────────────────────────────────────────────┐
  │                                                                                      │
  │                                                                                      │
  │   AFFINITY                CLEAN ROOM               ADROLL                            │
  │   ════════                ══════════               ══════                            │
  │                                                                                      │
  │   300M+ cards ──────►  Match on email  ◄──────  2.2M conversions (GCR)              │
  │   12M transactions      SHA-256 (HEM1)          10M funnel events (S2S)             │
  │   1M predictions        80.6% match rate        94.5K campaign metrics              │
  │   100K individuals      80,578 matched          5,000 companies (B2B)               │
  │                              │                                                       │
  │                              ▼                                                       │
  │                     ┌── ML TRAINING ──┐                                              │
  │                     │ 5 Snowflake ML  │                                              │
  │                     │ models trained  │                                              │
  │                     │ on matched data │                                              │
  │                     └────────┬────────┘                                              │
  │                              │                                                       │
  │                              ▼                                                       │
  │                     ┌── OUTPUTS ──────────────────────────────────┐                  │
  │                     │                                             │                  │
  │                     │  120 Funnel Rules (BOOST/NEUTRAL/SUPPRESS)  │                  │
  │                     │  Channel Attribution (pixel vs card swipe)  │                  │
  │                     │  B2B Account Scores (HOT/WARM/COLD)         │                  │
  │                     │  CTV Attribution (50 campaigns + ROAS)      │                  │
  │                     │  Audience Segments (30 purchase-verified)   │                  │
  │                     │                                             │                  │
  │                     └────────┬────────────────────────────────────┘                  │
  │                              │                                                       │
  │                              ▼                                                       │
  │                     ┌── STREAMLIT ────────────────────────────────┐                  │
  │                     │  6-tab interactive dashboard                │                  │
  │                     │  "Affinity x AdRoll Purchase Intelligence"  │                  │
  │                     └─────────────────────────────────────────────┘                  │
  │                                                                                      │
  └──────────────────────────────────────────────────────────────────────────────────────┘
```
