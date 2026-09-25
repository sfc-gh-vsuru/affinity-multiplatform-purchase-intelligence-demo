# Affinity Solutions — Multi-Platform DCR + AI/ML Demo Build Plan

**Target date:** Ad Week, **2026-10-05**
**Build environment:** Snowflake SE demo account (see README.md for setup)
**Status:** Phases 0-5 COMPLETE for TTD/PubMatic/Kargo. AdRoll platform added. Ready for Ad Week rehearsal.

---

## 1. What we are building, and why

### The high-level scope

Show that Affinity's purchase-outcome data and prediction model deliver value
**across the entire ad ecosystem** — DSPs, retargeting platforms, SSPs, and ad servers/publishers — via
Snowflake Data Clean Rooms and AI/ML. One Affinity provider side, four platform
consumers, same matching waterfall, platform-tailored outputs.

### Demo structure — 1 + 4

| Demo | Audience | Core message |
|---|---|---|
| **Cross-platform Affinity AI** | Affinity prospects, Snowflake field | The same purchase-outcome data powers every platform type through a single DCR architecture |
| **TTD-specific** | The Trade Desk | Bidding rules + prediction multipliers that drop into your existing bidder; fills the `OfflineProviderID` socket you already built |
| **PubMatic-specific** | PubMatic | Inventory scoring — prove which supply drives real purchases, set informed floor prices, package premium inventory |
| **Kargo-specific** | Kargo | Engagement-to-purchase attribution — close the loop between viewability/video events and actual sales, especially for CTV |
| **AdRoll-specific** | AdRoll / NextRoll | Conversion enrichment (pixel vs card swipe), funnel intelligence, B2B account scoring via Site Traffic Revealer, CTV attribution |

Each platform demo has its own **schemas, UDFs, and Streamlit app** so it can be
shown standalone to that prospect. The cross-platform demo ties them together.

### The problem each platform faces

**DSP (TTD):** Knows what it *bought* but not what it *caused*. Conversion data is
limited to advertiser pixels; most purchases are card swipes the pixel never sees.

**SSP (PubMatic):** Sells impressions but cannot prove which inventory drives
real-world outcomes. Floor pricing is guesswork; premium packaging has no
purchase-based evidence.

**Ad server / publisher (Kargo):** Has rich engagement signals — viewability, video
quartiles, click-through — but no purchase outcomes. Cannot prove ROI to
advertisers or justify premium CPMs for CTV inventory.

**Retargeting DSP (AdRoll):** Tracks full-funnel events (pageView through purchase)
and attributes conversions via pixel — but a pixel captures *intent*, not *outcome*.
Did the person actually swipe a card? AdRoll also has a unique B2B angle via Site
Traffic Revealer (firmographic data on site visitors), but no way to score those
companies by actual purchase propensity without Affinity.

Affinity has the missing half for all four: deterministic card-transaction
outcomes covering ~50% of US households. **A Data Clean Room is the only place
this join can happen.** That is the demo.

### What we build

1. **Affinity as DCR provider** — synthetic mirror of production purchase data,
   prediction feed, transactions, cards, merchants, brand/category taxonomy.
2. **Four platform consumers**, each with platform-native schemas:
   - **TTD (DSP):** advertiser CRM, identity spine, REDS impression/conversion feeds
   - **PubMatic (SSP):** OpenRTB 2.6 flattened bid-request impression log
   - **Kargo (ad server):** LLD-schema event log (impressions, clicks, video events)
   - **AdRoll (retargeting DSP):** Granular Conversion Report, S2S events, campaign metrics, Site Traffic Revealer (B2B)
3. **A shared match waterfall** — eight methods, individual and household level.
   Runs identically for each consumer; identity fields differ per platform.
4. **A normalized impression model** — platform-specific source tables mapped to
   a common feature space for ML training.
5. **Platform-tailored AI/ML outputs** — §5. The ML pipeline is shared; the
   output is translated to each platform's native field names and use case.

### Why it matters commercially

The ML output is deliberately **not** a scored audience. It is a compact set of
**500–700 interpretable rules** — predicates over dimensions each platform already
has at request/decision time — that drop into existing workflows.

| Scored audiences | Platform-native rules |
|---|---|
| Require identity resolution at decision time | Need no identity at decision time |
| Are an opaque model output | Are human-readable and auditable |
| Face growing privacy scrutiny | Survive it |
| Lock the buyer into the vendor | Drop into existing bidder / yield engine / ad server |

Competing outcome-data vendors sell scored audiences. Rules are the differentiated
position, and they are only credible if we can show how they were derived — across
DSP, SSP, and ad server simultaneously.

### Platform-specific insights that shape each pitch

**TTD:** The Conversions feed already carries `OfflineProviderID` and
`OfflineConversionTime` — a purpose-built slot for exactly this data. The pitch
is *"fill the socket you already built."*

**PubMatic:** OpenRTB bid requests carry `imp.bidfloor` and rich inventory context
(`site`, `content`, `device`). Affinity outcomes let PubMatic prove which
combinations of those fields actually drive purchases — turning floor pricing from
guesswork into evidence.

**Kargo:** LLD carries `kargo_ramp_id` (LiveRamp) alongside rich engagement events
(video quartiles, viewability via MOAT). Affinity closes the loop from engagement
to purchase, with special CTV value via `device_platform` and `app_bundle_id`.

**AdRoll:** The Granular Conversion Report (GCR) carries `email_sha256` — a
deterministic match key that produces the highest match rate of any platform
(80.6%). AdRoll's Site Traffic Revealer provides B2B firmographic data (industry,
revenue, headcount, journey stage) on 5,000+ companies visiting advertiser sites.
Combined with Affinity purchase data, this enables B2B account scoring that no
other platform can offer. The pitch is *"your pixel says they converted — our
cards say whether they actually bought."*

---

## 2. Architecture

### Topology — Affinity is the provider, three platform consumers

```
PROVIDER — AFFINITY                      CONSUMERS
┌────────────────────────┐
│  Purchase data         │               ┌─────────────────────────────────┐
│  (TX / CC / MID /      │──────────────▶│  TTD (DSP)                      │
│   taxonomy views)      │               │  CRM + spine + REDS feeds       │
│                        │               │  → bidding rules + multipliers  │
│  Prediction feed       │               └─────────────────────────────────┘
│  (30-day spend model)  │
│                        │               ┌─────────────────────────────────┐
│  Shared:               │──────────────▶│  PubMatic (SSP)                 │
│   hash → match         │               │  OpenRTB impression log         │
│   waterfall            │               │  → inventory yield scores       │
│   crosswalk            │               └─────────────────────────────────┘
│                        │
│                        │               ┌─────────────────────────────────┐
│                        │──────────────▶│  Kargo (Ad server / publisher)  │
│                        │               │  LLD event log                  │
│                        │               │  → engagement-to-purchase attr  │
│                        │               └─────────────────────────────────┘
│                        │
│                        │               ┌─────────────────────────────────┐
│                        │──────────────▶│  AdRoll (Retargeting DSP)       │
│                        │               │  GCR + S2S + Site Traffic Rev.  │
│                        │               │  → funnel rules + B2B scores    │
└────────────────────────┘               └─────────────────────────────────┘
```

Properties to preserve, because they are what makes it a clean room:

- Crosswalk output lands **only** on the consumer side.
- PII is hashed before matching and destroyed early. Hash types: MD5, SHA256, SHA512.
- Matching runs at **individual or household** level, one-time or recurring.
- Both accounts require **Enterprise or Business Critical** edition.

### Build approach: rebuild the matching layer in SFDCR

Affinity ships a real Native App for matching (`CONSUMER PURCHASE CONNECT`), whose
internal shape we mirror:

```
CONSUMER_PURCHASE_CONNECT
├── CLEANROOM              CLEANSING_HASHING, GET_CONNECT_ID,
│                          SINGLE_ID_MATCHING, WATERFALL_MATCHING
├── CLEANROOM_DATA
├── SAMPLE_DATA            SAMPLE_CLIENT_{CLEAR,HASHED}_* views,
│                          CC_EXT_V, CC_SRC_V, CUSTOMER_CC_MAP_V,
│                          MID_EXT_V, MID_SRC_V, TX_SRC_V
└── SPROCS
```

**We rebuild this ourselves in Snowflake Data Clean Rooms rather than installing
the app.** Three reasons:

1. The app's internals are not ours to instrument, and the demo depends on showing
   the waterfall working — match rates per method, the effect of reordering.
2. Installing it requires Affinity-side provisioning we do not control.
3. **The ML layer cannot be bolted onto a black box.** Rebuilding the matching half
   is what makes §5 possible, and §5 is the point.

Installing the real app alongside, for credibility, is a stretch goal if
provisioning lands in time. It is not on the critical path.

### Environment layout — Snowflake demo account

```
AFFINITY_DEMO
├── AFS_PROVIDER         Affinity synthetic source views, prediction feed
├── TTD_CONSUMER         advertiser CRM, identity spine, REDS feeds
├── PUBMATIC_CONSUMER    OpenRTB flattened impression log, identity via EIDs
├── KARGO_CONSUMER       LLD event log, identity via RampID/IFA/IP
├── ADROLL_CONSUMER      GCR conversions, S2S events, campaign metrics, funnel rules
├── ADROLL_B2B           Site Traffic Revealer firmographics, B2B account scores
├── CLEANROOM            hashing, match waterfall, crosswalk (shared logic)
├── NORMALIZED           platform-agnostic impression/conversion model for ML
├── ML                   training sets, 12 models, bidding rules, yield scores
├── AI                   semantic views, agent objects
├── APPS                 platform-specific Streamlit apps and UDFs
│   ├── PIPELINE_APP     End-to-end pipeline story (6 tabs)
│   ├── TTD_APP          TTD bid-rule explorer + spend efficiency dashboard
│   ├── PUBMATIC_APP     PubMatic inventory yield scorer + floor optimizer
│   ├── KARGO_APP        Kargo engagement-to-purchase attribution + CTV dashboard
│   ├── ADROLL_APP       AdRoll conversion enrichment + B2B scoring + CTV
│   └── CROSSPLATFORM_APP  Cross-platform comparison (all 4 platforms)
└── UTIL                 data generators, REDS enum lookup tables, OpenRTB enums
```

Warehouses: one large for generation, one medium for demo-time querying. ML Jobs
use their own compute. Confirm account edition is Enterprise or Business Critical
before Phase 0 completes.

---

## 3. Datasets to generate

Five dataset groups, all synthetic. Affinity field definitions come verbatim from
`Affinity Solutions_DCR_Data Dictionary US_2025_v3.xlsx`; TTD from REDS
documentation; PubMatic from OpenRTB 2.6; Kargo from Kargo LLD Schema V0.

### 3.1 Affinity provider data

| View | Grain | Key fields |
|---|---|---|
| `TX_SRC_V` | one row per transaction | `TXID`, `MEMBCCID`, `MTID`, `TRANS_AMOUNT`, `TRANS_DATE`, `TRANS_TIME`, `TRANS_TIME_ZONE`, `CNP_FLAG` |
| `CC_SRC_V` | one row per card | `MEMBCCID`, `CARDTYPE` (Debit/Credit), `ISSUE_DATE`, `ZIP` |
| `CC_EXT_V` | one row per card, enriched | `MEMBCCID`, `HHID`, `INDID`, demographics (`AGE`, `AGE_BUCKET`, `GENDER`, `INCOME`, `INCOME_BUCKET`, `ETHNICITY`, `HOMEOWNER_BUCKET`, `POLITICS_BUCKET`, `WEALTH_BUCKET`, `ADULTS_IN_HH`, `HAS_CHILDREN`, `IS_BUSINESS_OWNER`), geo (`CBSA_ID`, `CBSA_NAME`, `CC_ZIP`, `CC_STATE`, census/FIPS) |
| `MID_SRC_V` | one row per merchant terminal | `MTID`, `MERCHDESC`, `LOCATION`, `MERCHADDR1/2`, `MERCHCITY`, `MERCHSTATE`, `MERCHZIP`, `MERCHCOUNTRY` |
| `MID_BRANDS` | per `MTID` | `BRAND_ID`, `STORE_ID`, + `_PAYMENT` / `_DISTRIBUTION` variants |
| `MID_CATEGORIES` | per `MTID` | `AFSCATID`, `AFSCATID_PAYMENT`, `AFSCATID_DISTRIBUTION` |
| `MID_MCCS_V` | per `MTID` | `MCC` (4-digit) |
| `MID_GEOGRAPHY_V` | per `MTID` | `CHANNEL` (ONLINE / B&M / NULL), `MERCHANT_LOCATIONID`, `MERCHANT_ZIP`, `MERCHANT_STATE`, `MERCHANT_DMA`, `MERCHANT_CBSA`, `MERCHANT_CENSUSBLOCKGROUP` |
| `AFFINITY_BRANDS_V` | brand taxonomy | `BRAND_ID`, `BRAND_NAME`, `AFSCATID` |
| `AFFINITY_STORES_V` | sub-brand taxonomy | `STORE_ID`, `STORE_NAME`, `BRAND_ID`, `STORE_TYPE` (D/P) |
| `AFFINITY_CATEGORIES_V` | category taxonomy | `AFSCATID`, `CATEGORY_NAME` |
| `AFFINITY_MCCS_V` | MCC lookup | `MCC`, `NAME` |
| `AFFINITY_LOCATIONS_V` | store locations | `BRAND_ID`, `MERCHANT_LOCATIONID`, `ADDRESS`, `CITY`, `STATE`, `ZIP` |
| `CUSTOMER_CC_MAP_V` | Affinity ↔ consumer crosswalk | `INDID`, `HHID`, `CLIENT_AFS_INDID`, `CLIENT_AFS_HHID` |
| `PREDICTION_FEED_V` | one row per individual × brand | `INDID`, `HHID`, `BRAND_ID`, `PREDICTED_SPEND_30D` (weekly, 30-day horizon), `SPEND_PREDICTION_DATE`, `PERCENTILE_RANK`, `CONFIDENCE_SCORE`, `PROPENSITY_SCORE` (quarterly, 12-month horizon), `PROPENSITY_TIER` (TOP_1PCT / TOP_5PCT / TOP_10PCT / NULL), `PROPENSITY_DATE` |

> **SPECIFIED — from Affinity's "Outcome Layer for Bid Optimization" document.**
> Two pre-computed model outputs per individual × brand:
>
> | | Propensity score | Predicted spend |
> |---|---|---|
> | Question | Will this person buy this brand? | How many dollars will they spend? |
> | Horizon | Next 12 months | Next 30 days |
> | Refresh | Quarterly | Weekly |
> | Delivered as | Score + top 1%/5%/10% tiers | Dollar value per person per brand |
> | Role in bid | Whether impression is worth buying | What buying it is worth |
>
> 5,300+ tracked brands, daily transaction refresh, ~160M consumers.
> Production scale is far larger; our dev tier (58K individuals, 113 brands) is
> representative of the shape.

**ID formats — match exactly:**

| Field | Format | Example |
|---|---|---|
| `TXID` | `tx-` + 32 hex | `tx-acf761ed82a6482aa05ea7f684f801e9` |
| `MEMBCCID` | `cc-` + UUID | `cc-29bfb255-a1f8-4185-84f3-ed71035ae280` |
| `MTID` | `mt-` + 32 hex | `mt-0e3fcbe7fa387b315cb3856b21fb0922` |
| `MERCHANT_LOCATIONID` | `loc-` + 32 hex | `loc-95da22c7401cf71505b802de274a4a05` |
| `INDID` / `HHID` | bare 32 hex | `5633747cdce04681e3920ab2430e6e8b` |
| `CLIENT_AFS_INDID` / `_HHID` | bare 32 hex | `c2e69ebe1e084e713b027ed954243625` |
| `BRAND_ID` | 7-digit int | `1144673` |
| `STORE_ID` | 8-digit int starting 5 | `50000059` |
| `AFSCATID` | 1–3 digit int | `85` |

Realism details that matter:

- `MERCHDESC` are raw card-network descriptors, not clean names —
  `AMAZON RETA* ZC2L95IF2`, `VENMO *P2P TRANSFER`, `43529630 SHOPIFY.COM/C`.
  **This messiness is deliberate and load-bearing** — it is the input to the
  Cortex AI use case in §5.2.
- `HHID == INDID` for single-person households.
- A non-trivial share of `CC_EXT_V` demographic and census columns are NULL.
- An individual can hold **more than one card** — always join through `MEMBCCID`.

### 3.2 TTD consumer data (DSP) — three parts, not one

TTD's REDS is fully specified from TTD's published documentation, and TTD's own
sample data workbook is saved locally as `REDS_sample_data.xlsx`. Seed generator
distributions from that file rather than inventing value formats.

#### 3.2.1 The identity constraint that drives this design

REDS carries **exactly one identifier per event**, as a column trio:

| Column | Meaning | Example |
|---|---|---|
| `CombinedIdentifier` | the ID string — one per event, never a composite | `RDNcJKezWx2xwzd8YjWZ7KPax/fBH12ORMHxqGH5YDU=` |
| `CombinedIdentifierType` | `TDID`, `DAID`, `RampID`, `RawUID2`, `UID2Token`, `EUID`, `RawEUID` | `UID2` |
| `CombinedIdentifierForm` | `Originating` \| `Legacy` \| `Removed: Restriction` \| `Hashed: Restriction` | `Originating` |

Checked against the eight Affinity match methods:

| Affinity method | Needs | In REDS? |
|---|---|---|
| Exact / Fuzzy (`EXCT`, `FZY1–5`) | name + `ZIP11` | ❌ no name fields at all |
| Hashed email (`HEM1`) | `HEM` | ❌ no email. `RawUID2` is a *salted* hash — not an Affinity HEM |
| MAID individual / household (`MDI1`, `MDH1`) | `MAID` | ⚠️ only where type is `DAID` |
| Lastname + Zip11 (`HHD1`) | `LASTNAME`, `ZIP11` | ❌ no lastname |
| Zip11 household (`HHD2`) | `ZIP11` | ❌ `Zip` is 5-digit — ZIP11 ≠ ZIP5 |
| IP household (`IPA1`) | `IP` | ✅ `IPAddress` |

**An impression log cannot be the matching input.** At most three of eight methods
would fire, and only `IPA1` on every row.

So the consumer side has three datasets, which is also the correct real-world
design:

```
  Advertiser 1P CRM  ──►  match waterfall (all 8 methods)
  (name, email, addr)        └─► CLIENT_AFS_INDID / CLIENT_AFS_HHID
        │
        │ identity spine: CRM key ↔ TDID / DAID / UID2 / RampID
        ▼
  REDS Impressions  ──►  joined on CombinedIdentifier
  (bid-time features)
```

This is exactly what TTD's Originating ID feature exists to support — per TTD,
OGIDs *"eliminate graph cross-walking, increasing match rates and conversion
coverage."* Showing `Originating` vs `Legacy` match rates is a natural demo beat.

#### 3.2.2 Advertiser CRM

The matching input. Name, address, email, MAID, at the coverage mix agreed at the
§6 checkpoint. Feeds the waterfall; hashed per §3.3.

#### 3.2.3 Identity spine

CRM key ↔ `CombinedIdentifier`, with `CombinedIdentifierType` and
`CombinedIdentifierForm` populated to a realistic channel mix — CTV and in-app
skew `DAID`, web skews `TDID`, logged-in inventory skews `UID2`. Deliberate gaps
here are what force `IPA1` fallback and make the waterfall visibly necessary.

#### 3.2.4 REDS Impressions — the ML feature space

Generate to TTD's **current 3-0-0 column names**. Load TTD's enum tables (`OS`
101–268, `Browser` 1–15, `DeviceType` 1–8, `OSFamily` 1–7, `InventoryChannel` 0–7,
`AudioFeedId` 1–7, `ContentDuration` bands, `TTDNativeContextTypeId`,
`UserHourOfWeek` 0–167) into `UTIL` as generator lookups.

**Keys / hierarchy** — `LogEntryTime`, `ImpressionId`, `PartnerId`,
`AdvertiserId`, `CampaignId`, `AdGroupId`, `CreativeId`, `AudienceId`,
`PrivateContractId`, plus `*IdInteger` variants

**Supply path** — `SupplyVendorId`, `SupplyVendorName`, `SupplyVendorPublisherId`,
`DealId`, `Site`, `ImpressionPlacementId` (GPID), `AdsTxtSellerType`,
`AuctionType`, `SupplyType` (`OpenPath` = publisher-direct), `SellingParty*`

**Creative / channel** — `AdFormat`, `InventoryChannel`, `RenderingContext`,
`NativePlacementTypeId`, `TTDNativeContextTypeId`

**Device** — `DeviceType`, `OSFamily`, `OS`, `Browser`, `DeviceMake`,
`DeviceModel`, `UserAgent`, `Carrier`

**Geo** — `IPAddress`, `Zip` (5-digit), `City`, `Region`, `CountryLong`,
`NielsenDMA`, `Latitude` / `Longitude` (2dp)

**Time** — `UserHourOfWeek`, 0–167, encoding day × hour in the *user's* timezone.
Use it directly; do not invent separate daypart columns.

**Economics** — `MediaCostInBucks`, `FeeFeaturesCost`, `DataUsageTotalCost`,
`TTDCostInUSDollars`, `PartnerCostInUSDollars`, `AdvertiserCostInUSDollars`, plus
currency and FX columns

**Content / CTV** — `ContentGenre1`–`5`, `MatchedGenre`, `ContentRating`,
`ContentNetwork`, `ContentChannel`, `ContentDuration`,
`ContentProductionQuality`, `LiveStream`, `TVQualityIndex` (1–100),
`AudioFeedId`, `AudioContentSeries`

**Targeting signal** — `Recency` (minutes since user seen on targeted element),
`ReferrerCategories`, `MatchedLanguageCode`, `AudienceUnlimitedTierName`

Do not generate `TradingModeName` or `ImpressionCostInUSDollars` — both deprecated
and always null. Skip the third-party viewability feeds entirely; they are S3-only
and not deliverable via Snowflake.

#### 3.2.5 REDS Conversions

`LogEntryTime`, `ConversionId`, `AdvertiserId`, `ConversionType` (tracking-tag ID),
`IPAddress`, `ReferrerUrl`, `MonetaryValue`, `MonetaryValueCurrency`, `OrderId`,
`TD1`–`TD10`, `ProcessedTime`, `UserAgent`, `CombinedIdentifier`,
`CombinedIdentifierType`, `OfflineConversionTime`, `OfflineProviderID`.

Two generation rules with intent behind them:

- **Populate `MonetaryValue`, `OrderId` and `TD1`–`TD10` sparsely.** They are empty
  in TTD's own sample because they depend on advertiser pixel implementation. That
  gap *is* the Affinity value proposition — TTD sees the pixel fire but often not
  the basket. Make it visible rather than tidy.
- **Populate `OfflineProviderID` on a thin slice**, to show the integration socket
  Affinity would occupy.

**Conversions do not join to Impressions on impression ID.** Join on
`CombinedIdentifier` **and** `CombinedIdentifierType` together, always carrying
`LogEntryTime`.

### 3.3 PubMatic consumer data (SSP) — OpenRTB flattened impression log

PubMatic is an SSP. It sees bid requests (OpenRTB 2.6), not post-impression
outcomes. The consumer dataset is a **flattened impression log** derived from
OpenRTB bid-request objects, representing what PubMatic would share into a DCR.

**No conversion feed exists on the SSP side.** Affinity purchase outcomes are the
*entire* label — this is the core value proposition for SSPs.

#### 3.3.1 PubMatic impression log

| Column | OpenRTB source | Type | Description |
|---|---|---|---|
| `AUCTION_ID` | `BidRequest.id` | VARCHAR | Unique bid request ID |
| `TIMESTAMP` | generated | TIMESTAMP | Auction timestamp |
| `SITE_DOMAIN` | `site.domain` | VARCHAR | Publisher domain |
| `SITE_PAGE` | `site.page` | VARCHAR | Page URL |
| `SITE_CAT` | `site.cat` | VARCHAR | IAB content category |
| `PUBLISHER_ID` | `publisher.id` | VARCHAR | Exchange-specific publisher ID |
| `PUBLISHER_NAME` | `publisher.name` | VARCHAR | Publisher name |
| `IMP_ID` | `imp.id` | VARCHAR | Impression ID within request |
| `AD_FORMAT` | `imp.banner`/`video`/`native` presence | VARCHAR | `banner`, `video`, `audio`, `native` |
| `BANNER_W` | `banner.w` | INTEGER | Banner width (DIPS) |
| `BANNER_H` | `banner.h` | INTEGER | Banner height (DIPS) |
| `BANNER_POS` | `banner.pos` | INTEGER | Ad position on screen |
| `VIDEO_PLACEMENT` | `video.placement` | INTEGER | In-stream, out-stream, etc. |
| `VIDEO_STARTDELAY` | `video.startdelay` | INTEGER | Pre/mid/post-roll |
| `BIDFLOOR` | `imp.bidfloor` | FLOAT | Minimum bid CPM |
| `BIDFLOORCUR` | `imp.bidfloorcur` | VARCHAR | Floor currency |
| `DEAL_ID` | `deal.id` | VARCHAR | PMP deal ID (nullable) |
| `DEVICE_TYPE` | `device.devicetype` | INTEGER | AdCOM device type enum |
| `DEVICE_MAKE` | `device.make` | VARCHAR | e.g. "Apple" |
| `DEVICE_MODEL` | `device.model` | VARCHAR | e.g. "iPhone" |
| `DEVICE_OS` | `device.os` | VARCHAR | e.g. "iOS" |
| `DEVICE_UA` | `device.ua` | VARCHAR | User agent string |
| `DEVICE_CARRIER` | `device.carrier` | VARCHAR | Carrier/ISP |
| `DEVICE_IP` | `device.ip` | VARCHAR | IPv4 address |
| `GEO_ZIP` | `geo.zip` | VARCHAR | 5-digit zip |
| `GEO_CITY` | `geo.city` | VARCHAR | City |
| `GEO_REGION` | `geo.region` | VARCHAR | State/region |
| `GEO_METRO` | `geo.metro` | VARCHAR | Nielsen DMA |
| `GEO_LAT` | `geo.lat` | FLOAT | Latitude (2dp) |
| `GEO_LON` | `geo.lon` | FLOAT | Longitude (2dp) |
| `GEO_COUNTRY` | `geo.country` | VARCHAR | ISO-3166-1 alpha-3 |
| `USER_EID_SOURCE` | `user.eids[].source` | VARCHAR | Identity provider (e.g. `uidapi.com`, `liveramp.com`) |
| `USER_EID_UID` | `user.eids[].uids[].id` | VARCHAR | User ID from that provider |
| `USER_EID_ATYPE` | `user.eids[].uids[].atype` | INTEGER | Agent type |
| `DEVICE_IFA` | `device.ifa` | VARCHAR | IDFA/GAID (nullable) |
| `CONTENT_TITLE` | `content.title` | VARCHAR | Content title |
| `CONTENT_GENRE` | `content.genre` | VARCHAR | Content genre |
| `CONTENT_NETWORK` | `content.network.name` | VARCHAR | CTV network |
| `CONTENT_CHANNEL` | `content.channel.name` | VARCHAR | CTV channel |
| `CONTENT_LIVESTREAM` | `content.livestream` | INTEGER | 0/1 live |
| `CONTENT_LEN` | `content.len` | INTEGER | Content duration (seconds) |
| `AUCTION_TYPE` | `BidRequest.at` | INTEGER | 1=first price, 2=second price |
| `SECURE` | `imp.secure` | INTEGER | HTTPS required |
| `WINNING_PRICE` | generated | FLOAT | Clearing price (post-auction, for log) |

#### 3.3.2 Identity mapping for PubMatic

| Affinity method | PubMatic field | Coverage notes |
|---|---|---|
| `MDI1` / `MDH1` (MAID) | `DEVICE_IFA` | In-app only; null for web |
| `IPA1` (IP) | `DEVICE_IP` | Always present |
| `HEM1` (hashed email) | `USER_EID_UID` where source = `uidapi.com` | UID2-based; logged-in web |
| RampID | `USER_EID_UID` where source = `liveramp.com` | Where available |

**Note:** PubMatic has no name/address fields — `EXCT`, `FZY*`, `HHD1`, `HHD2`
methods will not fire. Match rates will be lower, driven by MAID, UID2/RampID,
and IP. This is realistic and worth showing — it demonstrates why SSP-side
matching is harder and why Affinity's broad identity coverage matters.

### 3.4 Kargo consumer data (ad server / publisher) — LLD event log

Kargo delivers Log Level Data (LLD) as daily gzipped CSVs. Schema from
`Log Level Data Process Request Form and FAQ_KARGO.xlsx`, LLD Schema V0 tab.

#### 3.4.1 Kargo LLD event table

| Column | Type | Description |
|---|---|---|
| `AUCTION_ID` | VARCHAR | Kargo auction tracking ID |
| `AUCTION_TYPE` | VARCHAR | `Direct`, `Preferred`, `Private`, `PG`, `PMP`, `Unknown` |
| `EVENT_TIMESTAMP` | TIMESTAMP | `YYYY-MM-DD HH:MM:SS` |
| `EVENT_TYPE` | VARCHAR | `impression`, `click`, `video_load`, `video_start`, `video_skip`, `video_firstquartile`, `video_midpoint`, `video_thirdquartile`, `video_complete` |
| `MOAT_INVIEW_MEASURABLE` | INTEGER | 0/1 — viewability measured by MOAT |
| `MOAT_INVIEW_VIEWABLE` | INTEGER | 0/1 — viewable per IAB standard |
| `ADVERTISER_ID` | VARCHAR | Kargo advertiser ID |
| `ADVERTISER_NAME` | VARCHAR | Advertiser name |
| `DEMAND_TYPE` | VARCHAR | `campaign` or `deal_group` |
| `CAMPAIGN_DEAL_GROUP_ID` | INTEGER | Campaign (Direct) / deal group (PMP) ID |
| `CAMPAIGN_DEAL_GROUP_NAME` | VARCHAR | Campaign / deal group name |
| `PLACEMENT_ID` | INTEGER | Kargo placement ID |
| `PLACEMENT_NAME` | VARCHAR | Placement name |
| `PLACEMENT_TYPE` | VARCHAR | `standard`, `added_value`, `branded_takeover`, `social_canvas` |
| `LINE_ITEM_DEAL_ID` | VARCHAR | Line item / deal ID |
| `LINE_ITEM_DEAL_NAME` | VARCHAR | Line item / deal name |
| `PUBLISHER_ID` | INTEGER | Kargo publisher ID |
| `PUBLISHER_NAME` | VARCHAR | Publisher name |
| `PUBLISHER_DOMAIN` | VARCHAR | Publisher domain |
| `AD_SLOT_NAME` | VARCHAR | Ad slot name + platform (e.g. "Hover (Mobile Web)") |
| `MEDIA_TYPE` | VARCHAR | `banner`, `video`, `native` |
| `CREATIVE_ID` | VARCHAR | Kargo creative ID |
| `CREATIVE_NAME` | VARCHAR | Creative name |
| `CREATIVE_SIZE` | VARCHAR | e.g. `300x250`, `320x50` |
| `CREATIVE_FORMAT` | VARCHAR | e.g. `ABA Display`, `Runway`, `Breakaway` |
| `KARGO_RAMP_ID` | VARCHAR | LiveRamp Kargo-specific RampID; `kg-` prefix = no mapping; null = no cookie/IFA |
| `IFA` | VARCHAR | Device IDFA/GAID; null for non-video/display |
| `DEVICE_TYPE` | VARCHAR | `Computer`, `Mobile`, `Tablet`, etc. |
| `DEVICE_PLATFORM` | VARCHAR | CTV platform (e.g. `Roku`, `LG Smart TV`, `XUMO`) |
| `APP_STORE_URL` | VARCHAR | App store URL (CTV) |
| `APP_STORE_ID` | VARCHAR | App store ID (CTV) |
| `APP_NAME` | VARCHAR | App name (CTV) |
| `APP_BUNDLE_ID` | VARCHAR | App bundle ID (CTV) |
| `OS` | VARCHAR | Operating system |
| `SOCIAL_BROWSER` | VARCHAR | Social media platform if in-app browser |
| `BROWSER` | VARCHAR | Browser type |
| `LANGUAGE` | VARCHAR | Content language |
| `IP_ADDRESS` | VARCHAR | Device IP address |
| `DMA` | VARCHAR | Nielsen DMA |
| `CITY` | VARCHAR | City (IP-derived) |
| `STATE_REGION` | VARCHAR | State/province (IP-derived) |
| `COUNTRY_CODE` | VARCHAR | 2-letter country code |
| `POSTAL_CODE` | VARCHAR | Postal code (IP-derived) |
| `CARRIER` | VARCHAR | Phone carrier |
| `COMPANY` | VARCHAR | Internet carrier company |
| `HOME_BIZ` | VARCHAR | `home` or `business` (IP-derived) |
| `CONNECTION_TYPE` | VARCHAR | `wifi`, `mobile`, `wired`, `cable`, `xdsl`, `broadband` |

#### 3.4.2 Identity mapping for Kargo

| Affinity method | Kargo field | Coverage notes |
|---|---|---|
| RampID | `KARGO_RAMP_ID` | Primary; `kg-` prefix rows have no LiveRamp mapping |
| `MDI1` / `MDH1` (MAID) | `IFA` | Video/CTV only; null for display |
| `IPA1` (IP) | `IP_ADDRESS` | Always present |

**No name, email, or address fields.** Like PubMatic, only MAID, RampID, and IP
methods fire. CTV inventory will lean heavily on `IPA1` due to limited IFA
availability on CTV devices.

#### 3.4.3 What makes Kargo data distinctive

- **Event-level granularity** — not just impressions but clicks and video quartile
  events. This enables engagement-weighted labels (e.g., a video completion +
  purchase is stronger signal than an impression + purchase).
- **Viewability built in** — `MOAT_INVIEW_MEASURABLE` / `MOAT_INVIEW_VIEWABLE`
  allow viewability-conditioned analysis without a separate feed.
- **CTV-specific fields** — `DEVICE_PLATFORM`, `APP_NAME`, `APP_BUNDLE_ID` enable
  CTV-specific rule derivation, which is the highest-value inventory segment.
- **No economics fields** — Kargo LLD has no cost data. Rules optimize on
  purchase conversion rate and engagement quality, not spend efficiency.

### 3.5 AdRoll consumer data (retargeting DSP) — conversion-scoped, not impression-scoped

AdRoll/NextRoll is a retargeting DSP. Unlike TTD (impression logs) or PubMatic
(bid requests), AdRoll's primary data export is **conversion-scoped** — the
Granular Conversion Report (GCR). Impression-level log data is not publicly
available from AdRoll's API. This is a deliberate design choice by NextRoll and
shapes the entire AdRoll demo around conversions, funnel events, and B2B signals.

#### 3.5.1 Granular Conversion Report (GCR)

The GCR is AdRoll's primary analytics export. Schema from `apidocs.nextroll.com`
GraphQL Reporting API.

| Column | Type | Description |
|---|---|---|
| `CONVERSION_ID` | VARCHAR | Unique conversion event ID |
| `CONVERSION_TIMESTAMP` | TIMESTAMP | When the conversion occurred |
| `EMAIL_SHA256` | VARCHAR | SHA-256 hashed email — **primary match key** |
| `ADVERTISER_EID` | VARCHAR | AdRoll advertiser entity ID |
| `CAMPAIGN_EID` | VARCHAR | Campaign entity ID |
| `CAMPAIGN_NAME` | VARCHAR | Campaign display name |
| `ADGROUP_EID` | VARCHAR | Ad group entity ID |
| `ADGROUP_NAME` | VARCHAR | Ad group display name |
| `AD_EID` | VARCHAR | Ad entity ID |
| `AD_NAME` | VARCHAR | Ad display name |
| `CHANNEL` | VARCHAR | `web`, `social`, `email`, `native`, `display`, `video`, `ctv` |
| `DEVICE_TYPE` | VARCHAR | `desktop`, `mobile`, `tablet`, `ctv`, `other` |
| `GEO_COUNTRY` | VARCHAR | Country code |
| `GEO_REGION` | VARCHAR | State/region |
| `GEO_CITY` | VARCHAR | City |
| `GEO_DMA` | VARCHAR | Nielsen DMA |
| `ATTRIBUTED_REVENUE` | FLOAT | Pixel-reported conversion value ($) |
| `ATTRIBUTION_TYPE` | VARCHAR | `click_through`, `view_through` |
| `ATTRIBUTION_WINDOW_DAYS` | INTEGER | 1, 7, 14, or 28 days |
| `CONVERSION_TYPE` | VARCHAR | `purchase`, `signup`, `lead`, `addToCart`, `pageView` |
| `LANDING_PAGE_URL` | VARCHAR | Destination URL |
| `REFERRER_URL` | VARCHAR | Referring URL |
| `OS` | VARCHAR | Operating system |
| `BROWSER` | VARCHAR | Browser name |
| `IP_ADDRESS` | VARCHAR | Device IP address |
| `USER_AGENT` | VARCHAR | Full user agent string |
| `IS_NEW_VISITOR` | BOOLEAN | First-time vs returning visitor |
| `SESSION_DURATION_SEC` | INTEGER | Session length in seconds |

**Key design difference from TTD/PubMatic/Kargo:** The GCR is conversion-scoped,
not impression-scoped. Each row represents a conversion event, not an ad impression.
This means the ML layer works on conversions (verifying which are real purchases)
rather than on impressions (predicting which will lead to purchases).

#### 3.5.2 Server-to-Server (S2S) Events

AdRoll's S2S Event API tracks 13 event types across the full marketing funnel.
Schema from `apidocs.nextroll.com`.

| Column | Type | Description |
|---|---|---|
| `EVENT_ID` | VARCHAR | Unique event ID |
| `EVENT_TIMESTAMP` | TIMESTAMP | When the event occurred |
| `EVENT_TYPE` | VARCHAR | One of 13 types (see below) |
| `EMAIL_SHA256` | VARCHAR | SHA-256 hashed email |
| `ADVERTISER_EID` | VARCHAR | AdRoll advertiser entity ID |
| `SESSION_ID` | VARCHAR | Session tracking ID |
| `DEVICE_TYPE` | VARCHAR | Device category |
| `CHANNEL` | VARCHAR | Marketing channel |
| `GEO_COUNTRY` | VARCHAR | Country code |
| `GEO_REGION` | VARCHAR | State/region |
| `GEO_CITY` | VARCHAR | City |
| `GEO_DMA` | VARCHAR | Nielsen DMA |
| `IP_ADDRESS` | VARCHAR | Device IP |
| `PAGE_URL` | VARCHAR | Page URL |
| `REFERRER_URL` | VARCHAR | Referring URL |
| `PRODUCT_ID` | VARCHAR | Product identifier (for commerce events) |
| `PRODUCT_NAME` | VARCHAR | Product name |
| `PRODUCT_PRICE` | FLOAT | Product price |
| `QUANTITY` | INTEGER | Product quantity |

**13 event types:**
`pageView`, `productView`, `productSearch`, `addToCart`, `removeFromCart`,
`startCheckout`, `purchase`, `signup`, `login`, `demoRequest`, `contactSales`,
`signupTrial`, `custom`

**B2C events:** pageView → productSearch → productView → addToCart → startCheckout → purchase
**B2B events:** pageView → demoRequest / contactSales / signupTrial

#### 3.5.3 Campaign Metrics

Aggregated campaign performance data from AdRoll's GraphQL Reporting API.

| Column | Type | Description |
|---|---|---|
| `DATE` | DATE | Reporting date |
| `CAMPAIGN_EID` | VARCHAR | Campaign entity ID |
| `CAMPAIGN_NAME` | VARCHAR | Campaign display name |
| `CAMPAIGN_TYPE` | VARCHAR | `retargeting`, `brand_awareness`, `prospecting` |
| `ADGROUP_EID` | VARCHAR | Ad group entity ID |
| `CHANNEL` | VARCHAR | Marketing channel |
| `DEVICE_TYPE` | VARCHAR | Device category |
| `IMPRESSIONS` | INTEGER | Impressions served |
| `CLICKS` | INTEGER | Clicks recorded |
| `CTR` | FLOAT | Click-through rate |
| `SPEND` | FLOAT | Ad spend ($) |
| `CONVERSIONS` | INTEGER | Attributed conversions |
| `ATTRIBUTED_REVENUE` | FLOAT | Pixel-reported revenue |
| `CPA` | FLOAT | Cost per acquisition |
| `ROAS` | FLOAT | Return on ad spend |
| `VIDEO_COMPLETIONS` | INTEGER | Video completions (CTV/video campaigns) |
| `VIDEO_COMPLETION_RATE` | FLOAT | Video completion rate |

#### 3.5.4 Site Traffic Revealer (B2B firmographics)

AdRoll's unique B2B capability — identifies companies visiting the advertiser's
website using reverse IP lookup and firmographic databases. Schema from
`apidocs.nextroll.com`.

| Column | Type | Description |
|---|---|---|
| `DOMAIN` | VARCHAR | Company domain |
| `COMPANY_NAME` | VARCHAR | Company display name |
| `COMPANY_INDUSTRY` | VARCHAR | Industry vertical (~150 values: Technology, Healthcare, Finance, etc.) |
| `COMPANY_REVENUE` | VARCHAR | Revenue bucket: `<$1M`, `$1M-$10M`, `$10M-$50M`, `$50M-$100M`, `$100M-$500M`, `$500M-$1B`, `>$1B` |
| `COMPANY_SIZE` | VARCHAR | Employee count bucket: `1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1001-5000`, `5001-10000`, `>10000` |
| `JOURNEY_STAGE` | VARCHAR | ABM funnel stage: `Unaware`, `Aware`, `Engaged`, `MQL`, `Opportunity` |
| `FIRST_VISIT_DATE` | DATE | First recorded visit |
| `TOTAL_VISITS` | INTEGER | Total site visits |
| `TOTAL_VISITORS` | INTEGER | Unique visitors |
| `CONTACT_EMAIL_SHA256` | VARCHAR | SHA-256 hashed contact email (when available) |

**What makes this unique:** No other platform in the demo (TTD, PubMatic, Kargo)
has B2B firmographic data. This enables a completely new use case — scoring
companies by actual purchase propensity rather than just web engagement.

#### 3.5.5 Identity mapping for AdRoll

| Affinity method | AdRoll field | Coverage notes |
|---|---|---|
| `HEM1` (hashed email) | `EMAIL_SHA256` in GCR + S2S | **Primary.** Deterministic, highest confidence. Present on ~80% of conversions. |
| `IPA1` (IP) | `IP_ADDRESS` | Fallback for non-logged-in events |

**No MAID, no name/address, no RampID.** AdRoll identity is email-centric.
`HEM1` alone produces an 80.6% match rate against Affinity's base — the strongest
of any platform because email SHA-256 is deterministic (not probabilistic like
IP or device graph).

#### 3.5.6 What makes AdRoll data distinctive

- **Conversion-scoped, not impression-scoped** — ML works on "which conversions
  are real purchases" rather than "which impressions lead to purchases." Different
  question, different model architecture.
- **Email SHA-256 as primary identity** — deterministic matching. No graph
  resolution, no probabilistic decay. Strongest match rate of any platform.
- **Full-funnel S2S events** — 13 typed events from pageView through purchase,
  including B2B signals (demoRequest, contactSales, signupTrial). Enables funnel
  intelligence rules.
- **B2B firmographics** — Site Traffic Revealer is unique to AdRoll. Industry,
  revenue, headcount, journey stage on 5,000+ companies. Combined with Affinity
  purchase data, this powers account-level scoring.
- **No impression-level data** — unlike TTD (REDS), PubMatic (OpenRTB logs), and
  Kargo (LLD), AdRoll does not provide impression-level log streams publicly.
  The demo uses conversion-level and campaign-aggregate data per documented API schemas.
- **CTV attribution via campaign metrics** — CTV campaigns are attributed through
  matched conversion events, not impression logs. Video completion rates and ROAS
  are derived from campaign-level aggregates.

### 3.6 Normalized impression model

A platform-agnostic view that maps each platform's fields to a common feature
space for ML training. Lives in `NORMALIZED` schema.

| Normalized field | TTD source | PubMatic source | Kargo source | AdRoll source |
|---|---|---|---|---|
| `PLATFORM` | `'TTD'` | `'PUBMATIC'` | `'KARGO'` | `'ADROLL'` |
| `IMPRESSION_ID` | `ImpressionId` | `AUCTION_ID\|\|IMP_ID` | `AUCTION_ID` | `CONVERSION_ID` |
| `TIMESTAMP` | `LogEntryTime` | `TIMESTAMP` | `EVENT_TIMESTAMP` | `CONVERSION_TIMESTAMP` |
| `DEVICE_TYPE` | `DeviceType` (enum) | `DEVICE_TYPE` (enum) | `DEVICE_TYPE` (string) | `DEVICE_TYPE` (string) |
| `OS` | `OS` (enum) | `DEVICE_OS` | `OS` | `OS` |
| `BROWSER` | `Browser` (enum) | derived from `DEVICE_UA` | `BROWSER` | `BROWSER` |
| `GEO_ZIP` | `Zip` | `GEO_ZIP` | `POSTAL_CODE` | NULL |
| `GEO_DMA` | `NielsenDMA` | `GEO_METRO` | `DMA` | `GEO_DMA` |
| `GEO_STATE` | `Region` | `GEO_REGION` | `STATE_REGION` | `GEO_REGION` |
| `IP_ADDRESS` | `IPAddress` | `DEVICE_IP` | `IP_ADDRESS` | `IP_ADDRESS` |
| `SUPPLY_DOMAIN` | `Site` | `SITE_DOMAIN` | `PUBLISHER_DOMAIN` | `LANDING_PAGE_URL` (domain) |
| `AD_FORMAT` | `AdFormat` (enum) | `AD_FORMAT` | `MEDIA_TYPE` | `CHANNEL` |
| `CREATIVE_SIZE` | derived from format enums | `BANNER_W\|\|x\|\|BANNER_H` | `CREATIVE_SIZE` | NULL |
| `CONTENT_GENRE` | `ContentGenre1` | `CONTENT_GENRE` | NULL | NULL |
| `CONTENT_NETWORK` | `ContentNetwork` | `CONTENT_NETWORK` | NULL | NULL |
| `CTV_APP` | NULL | NULL | `APP_NAME` | NULL |
| `CTV_PLATFORM` | NULL | NULL | `DEVICE_PLATFORM` | NULL |
| `CARRIER` | `Carrier` | `DEVICE_CARRIER` | `CARRIER` | NULL |
| `VIEWABLE` | NULL (separate feed) | NULL | `MOAT_INVIEW_VIEWABLE` | NULL |
| `VIDEO_COMPLETION` | NULL (VideoEvents feed) | NULL | derived from `EVENT_TYPE` | `VIDEO_COMPLETION_RATE` |
| `USER_HOUR_OF_WEEK` | `UserHourOfWeek` (0-167) | derived from timestamp | derived from timestamp | derived from timestamp |
| `ATTRIBUTED_REVENUE` | NULL | NULL | NULL | `ATTRIBUTED_REVENUE` |
| `CHANNEL` | NULL | NULL | NULL | `CHANNEL` |
| `ATTRIBUTION_TYPE` | NULL | NULL | NULL | `ATTRIBUTION_TYPE` |

**Note:** AdRoll's normalized rows represent conversions, not impressions. The
`IMPRESSION_ID` maps to `CONVERSION_ID`. AdRoll-specific fields (`ATTRIBUTED_REVENUE`,
`CHANNEL`, `ATTRIBUTION_TYPE`) are NULL for other platforms and vice versa.

UDFs in `UTIL` handle enum translation (e.g., TTD `DeviceType` integer → string,
PubMatic AdCOM `devicetype` integer → string, Kargo string passthrough).

### 3.7 Matching input table

Consumer supplies only the fields its chosen match method requires. All hashed.

| Column | Required for |
|---|---|
| `ID` | **required** — returned unchanged as `CLIENT_INDID` |
| `ID2` | optional — returned unchanged as `CLIENT_HHID` |
| `FIRSTNAME` | Exact, Fuzzy |
| `LASTNAME` | Exact, Fuzzy, Lastname+Zip11 |
| `ZIP11` | Exact, Fuzzy, Lastname+Zip11, Zip11 |
| `ONELETTER_FNAME` | Fuzzy |
| `THREELETTER_FNAME` | Fuzzy |
| `ZIP9` | Fuzzy |
| `ZIP5` | Fuzzy |
| `HEM` | Hashed email |
| `MAID` | MAID individual, MAID household |
| `IP` | IP |

The dictionary's sample-values tab also carries a `HASH_TYPE` column (`SHA512`)
that is absent from its Data Dictionary tab. Include it; the discrepancy is worth
raising with Affinity.

---

## 4. The matching algorithm

Where the data dictionary v3 and the July deck disagree, **the dictionary is
authoritative** — the deck labels fuzzy variants 2A–2E, the dictionary names them
`FZY1`–`FZY5` with explicit field combinations.

### 4.1 Methods, codes, levels

| Order | Method | Required fields | Code | Level |
|---|---|---|---|---|
| 1 | Exact | `FIRSTNAME`, `LASTNAME`, `ZIP11` | `EXCT` | INDIVIDUAL |
| 2 | Fuzzy | `FIRSTNAME`, `LASTNAME`, `ZIP11`, `ONELETTER_FNAME`, `THREELETTER_FNAME`, `ZIP9`, `ZIP5` | `EXCT`, `FZY1`–`FZY5` | INDIVIDUAL |
| 3 | Hashed email | `HEM` | `HEM1` | INDIVIDUAL |
| 4 | MAID (individual) | `MAID` | `MDI1` | INDIVIDUAL |
| 5 | Lastname + Zip11 | `LASTNAME`, `ZIP11` | `HHD1` | HOUSEHOLD |
| 6 | Zip11 | `ZIP11` | `HHD2` | HOUSEHOLD |
| 7 | IP | `IP` | `IPA1` | HOUSEHOLD |
| 8 | MAID (household) | `MAID` | `MDH1` | HOUSEHOLD |

Methods run **individually** or as an **ordered waterfall**. In waterfall mode each
record takes the code of the **first** method that matched.

### 4.2 Fuzzy sub-codes

| Code | Fields compared |
|---|---|
| `EXCT` | `FIRSTNAME`, `LASTNAME`, `ZIP11` |
| `FZY1` | `FIRSTNAME`, `ZIP11` |
| `FZY2` | `THREELETTER_FNAME`, `LASTNAME`, `ZIP11` |
| `FZY3` | `ONELETTER_FNAME`, `LASTNAME`, `ZIP11` |
| `FZY4` | `THREELETTER_FNAME`, `ZIP11` |
| `FZY5` | `FIRSTNAME`, `LASTNAME`, `ZIP9` |

### 4.3 Waterfall ordering

Affinity Default is the §4.1 order. Custom lets the consumer pick attributes and
order. **Demo both** — match-rate lift from reordering is a strong interactive
moment.

### 4.4 Crosswalk output

| Column | Description |
|---|---|
| `CLIENT_INDID` | consumer individual ID, returned as supplied |
| `CLIENT_HHID` | consumer household ID, returned as supplied |
| `CLIENT_AFS_INDID` | synthetic Affinity individual ID → `CUSTOMER_CC_MAP_V` |
| `CLIENT_AFS_HHID` | synthetic Affinity household ID → `CUSTOMER_CC_MAP_V` |
| `MATCH_CODE` | which identifier combination matched |
| `MATCH_LEVEL` | `INDIVIDUAL` or `HOUSEHOLD` |
| `RETURN_CODE` | status; success = `CID-MT-00` |

`CLIENT_INDID` is **NULL on household-only matches**. Every downstream aggregation
and the ML label logic must handle that.

### 4.5 Join path to purchase outcomes

```
consumer customer table
  → MATCHING_OUTPUT.CLIENT_AFS_INDID
  → CUSTOMER_CC_MAP_V.CLIENT_AFS_INDID → CUSTOMER_CC_MAP_V.INDID
  → CC_EXT_V.INDID → CC_EXT_V.MEMBCCID
  → TX_SRC_V.MEMBCCID
```

Then to merchant context via `TX_SRC_V.MTID` → `MID_*` → taxonomy views.

---

## 5. AI/ML layer — what we build on top

This section is the reason the demo exists. Matching alone is Affinity's current
product; everything below is the extension being sold.

Five use cases, in priority order. §5.1 is the demo's centrepiece; §5.1b is the
lighter-weight entry point for platforms not ready to train their own model.

### Federated identity framing

All use cases below rest on Snowflake's federated identity story: Affinity's
predictions and outcomes are delivered on the **client's own keys** via a
graph-to-graph match on AFSID. No raw PII crosses account boundaries; the
client never sees Affinity's graph, and Affinity never sees the client's. This
is a key differentiator versus competitors who require data movement, and it
should be called out explicitly in the pitch narrative — ideally its own slide.

### 5.1 Primary — outcome-trained bidding rules

**The claim:** given Affinity purchase outcomes, we can derive bid logic that
improves spend efficiency, and express it as rules a bidder can load today.

#### Label

For each matched impression, did the matched individual or household make a
**qualifying purchase** within the attribution window?

Qualifying purchase is defined at the §6 checkpoint — category, minimum basket,
window length. Built from `TX_SRC_V` joined via §4.5, filtered to the campaign's
target categories through `MID_CATEGORIES` / `AFFINITY_CATEGORIES_V`.

Two label hygiene rules that decide whether the result is believable:

- **Household-level matches produce household-level labels.** A purchase attributed
  to an `HHD*` or `IPA1` match is weaker evidence than an `EXCT` match. Carry
  `MATCH_LEVEL` and `MATCH_CODE` into the training set and either weight by them or
  report results per match tier. Do not silently pool them.
- **Exclude purchases before the impression.** Obvious, and the most common way a
  demo like this accidentally reports a fake lift.

#### Features — bid-time available only

The hard constraint: **every feature must be knowable at bid request time.** A rule
the bidder cannot evaluate is worthless.

Eligible, from §3.2.4: supply path, creative/channel, device, geo,
`UserHourOfWeek`, content/CTV, `Recency`, `ReferrerCategories`.

**Explicitly excluded, and why:**

| Excluded | Reason |
|---|---|
| `MediaCostInBucks`, `*CostInUSDollars` | Realized post-auction. These are the **objective**, not features. Using them leaks. |
| `CombinedIdentifier` and anything derived from it | Requires identity resolution at bid time — the exact dependency we are eliminating |
| Affinity demographics from `CC_EXT_V` | Only known *after* matching. Valid for explaining results and for audience building (§5.4), **not** as rule features. |
| Click / video / conversion events | Post-impression |

That last one is worth stating on a slide: the model learns from
identity-resolved outcomes, but the rules it emits carry no identity dependency.

#### Method

1. **Baseline first.** Reproduce TTD's own published 8-step last-touch attribution
   over REDS `Conversions` alone, joining on `CombinedIdentifier` +
   `CombinedIdentifierType`. Using TTD's methodology as the control makes the lift
   claim very hard to argue with.
2. **Gradient-boosted model** on the enriched label, inside a **DCR ML Job** with a
   code spec. Purpose is twofold: an accuracy ceiling to measure rules against, and
   feature importance to constrain the rule search space.
3. **Rule mining** over the top features — candidate predicate combinations with
   minimum support, conversion rate versus baseline, and a multiple-testing
   correction. Keep the top 500–700 by lift subject to support and coverage floors.
4. **Bid multiplier with shrinkage.** Multiplier is a function of measured lift,
   shrunk toward 1.0 in inverse proportion to segment support. Without this, thin
   segments produce absurd multipliers and the rule set fails the first sanity
   check a DSP applies to it.
5. **Fidelity check.** Report how much of the model's AUC the rule set retains.
   Quantifying the interpretability cost is more persuasive than hiding it.

#### Rule output contract

Final shape confirmed at the §6 checkpoint. Working proposal:

| Field | Purpose |
|---|---|
| `RULE_ID` | stable identifier |
| `PREDICATE` | the condition, in a bidder-loadable representation |
| `BID_MULTIPLIER` | post-shrinkage |
| `SUPPORT` | impressions matching the predicate |
| `CONVERSION_RATE`, `BASELINE_RATE`, `LIFT` | the evidence |
| `CONFIDENCE_INTERVAL` | so a buyer can see the uncertainty |
| `MATCH_TIER` | which match quality the evidence rests on |
| `PRIORITY` | conflict resolution when rules overlap |
| `VALID_FROM` / `VALID_TO` | rules decay; say so explicitly |

#### The money slide

Counterfactual spend efficiency: same budget, default bidder versus rule-adjusted
bidder, on held-out impressions. Reported as cost per incremental purchase.

Show it three ways — baseline (TTD conversions only), enriched (plus Affinity),
and the delta. The delta is the product.

### 5.1b Prediction model as bid multipliers (Mode 2 — Default)

**The lighter path — works on day one.** Not every platform is ready to train a
custom model over resolved impressions (§5.1). Mode 2 surfaces Affinity's
pre-computed predictions directly as bid multipliers — no ML training on the
consumer side, no first-party data to assemble, no training window to wait out.

Per Affinity's document: "a new endpoint customer gets a working bid multiplier
immediately: the cold-start problem that usually stalls a consumption product
for the first two quarters simply does not arise."

#### How it works

1. After matching (§4), join the crosswalk to `PREDICTION_FEED_V` via
   `CLIENT_AFS_INDID` → `INDID`.
2. For each matched individual × target brand, read both prediction outputs:
   - **Propensity score** (12-month, quarterly) — *whether* this impression is
     worth buying. Delivered with ready-made TOP_1PCT / TOP_5PCT / TOP_10PCT tiers.
   - **Predicted spend** (30-day, weekly) — *what* buying it is worth. Dollar
     value per person per brand.
3. Classify each individual into one of four bidding quadrants:

   | Quadrant | Spend profile | Strategic objective | Bid strategy |
   |---|---|---|---|
   | **Net-New Prospects** | High predicted brand spend, low prior spend | Pure acquisition | Max multiplier (4x-5x) |
   | **Conquesting** | High category spend, low brand share-of-wallet | Share-of-wallet theft | High multiplier (3x) |
   | **High-LTV VIPs** | High predicted + high prior spend | Expansion & upsell | Value-based optimization |
   | **Waste Suppression** | Low predicted spend (brand & category) | Waste elimination | Negative bidding / suppression |

4. Deliver the multiplier table to the bidder keyed on the client's own IDs
   (via the identity spine), not on Affinity IDs.

This is the "default" tier — bundled, not sold separately. §5.1's custom model
is the "custom" tier for clients with data science capacity and first-party data.

#### Three delivery shapes (in increasing integration effort)

1. **Audience + multiplier table** — tiered propensity scores synced to the DSP
   or SSP as segments, with a bid multiplier per tier. Works in every buying
   platform today with no change to the bidder.
2. **Per-ID bid instruction** — a scored file giving a multiplier per
   addressable ID, refreshed on cadence, cached by the buying platform.
3. **Value-based bidding** — predicted spend converts the instruction from a
   flat CPA target into a bid proportional to the revenue the person is
   expected to generate — a ROAS problem with a credible input rather than a
   modeled one.

#### Validation — the same ruler for both Default and Custom

Whichever model produces the bid, the result is graded against the same observed
purchase data, with a holdout. Default and custom become comparable, and a client
can see whether their custom model actually beat the default rather than assuming
it did. **This validation layer is not optional** — it is what makes the product
defensible.

> **Incrementality warning (to surface in the demo):** Bidding hardest on the
> people most likely to buy anyway produces excellent attributed ROAS and very
> little incremental revenue. The holdout prevents this trap — showing we
> understand it is a selling point for sophisticated buyers.

#### Accuracy proof — Q3 predictions vs Q4 actuals

Snowflake team specifically requested this demo beat: show Affinity's Q3 predictions
against Q4 actual transaction data to prove model accuracy.

Generate two synthetic snapshots:
- **Q3 prediction snapshot** — `PREDICTION_FEED_V` with `PROPENSITY_DATE` in Q3
  and `SPEND_PREDICTION_DATE` in Q3
- **Q4 actuals** — `TX_SRC_V` transactions in Q4, aggregated to individual ×
  brand spend

Demo slide shows:
- Predicted vs actual spend scatter plot (top decile)
- Propensity tier accuracy: what % of TOP_1PCT / TOP_5PCT / TOP_10PCT actually
  purchased?
- Percentage of actual spend captured by top 10th percentile of predictions
  (target: ~90%, per Affinity's stated accuracy)
- Dollar accuracy distribution (target: within +/-10%)

#### Where it runs

Prediction delivery runs on the **consumer side** post-crosswalk, same as §5.3
and §5.4. The prediction model itself is Affinity IP and stays provider-side.

### 5.2 Cortex AI functions — merchant descriptor normalization

The highest-value, lowest-effort AI use case here, and it sits on data Affinity
already owns.

`MERCHDESC` arrives as raw card-network junk: `AMAZON RETA* ZC2L95IF2`,
`VENMO *P2P TRANSFER`, `43529630 SHOPIFY.COM/C`. Mapping those to a clean brand
and category is normally a manual rules-and-regex problem that never finishes.

Build it with Cortex AI functions over `MID_SRC_V`:

- **`AI_CLASSIFY`** — descriptor → `AFFINITY_CATEGORIES_V` category
- **`AI_EXTRACT`** — pull the brand token out of the noise
- **`AI_COMPLETE`** — resolve the ambiguous residue against `AFFINITY_BRANDS_V`
- **`AI_FILTER`** — separate genuine retail from P2P transfers, fees and
  intra-account movement, which must not count as purchases

Two reasons this earns its place beyond being a nice Cortex demo:

1. **It feeds §5.1.** Label quality depends on correctly identifying which
   transactions are in-category purchases. Misclassified descriptors are
   mislabeled training rows.
2. **It runs entirely provider-side on non-PII data**, so it demonstrates Cortex
   value with no clean-room governance complexity — an easy first win to show
   Affinity.

Show a before/after coverage number: share of transaction volume confidently
attributed to a brand, manual mapping versus Cortex.

### 5.3 Semantic View + Cortex Analyst — natural language over the results

A semantic layer over the matched population, purchase outcomes and rule set, so
the walkthrough can be driven by questions instead of SQL:

- *"Which CTV networks drove the most grocery purchases last quarter?"*
- *"What's the match rate by method, and which method contributes most incremental
  conversions?"*
- *"Show me the highest-lift rules for connected TV in the top ten DMAs."*

Build with verified queries for the scripted questions so the live demo is
deterministic. Consider Semantic Autopilot to accelerate the semantic layer.

Governance note: this runs on the **consumer-side** post-crosswalk model. It never
touches provider raw data.

### 5.4 Cortex Agent — audience construction

Affinity already has agent work in flight compressing audience building from days
to minutes. Align rather than duplicate: an agent over the semantic view of §5.3
that turns a natural-language brief — *"lapsed premium grocery buyers in CTV-heavy
DMAs"* — into a validated audience definition with size estimate and match-rate
projection.

This is where Affinity's post-match demographics from `CC_EXT_V` are legitimately
useful, since audience building happens offline where identity resolution is
available. Contrast that with §5.1's bid-time constraint — the two use cases have
genuinely different rules about what data is usable, and saying so out loud makes
the whole architecture more credible.

### 5.5 Stretch — online inference

Serving the model via Cortex REST APIs for real-time scoring. Realistically
post-Ad Week. Worth a forward-looking slide, not build time.

### 5.6 Where each piece runs — and why that matters

| Use case | Runs | Sees |
|---|---|---|
| §5.2 descriptor normalization | Provider side | Affinity merchant data only. No PII, no consumer data. |
| §5.1 rule derivation | **Inside a DCR ML Job** | Matched population under clean-room controls. Emits only aggregate rules. |
| §5.1b prediction as bid multipliers | Consumer side | Post-crosswalk predictions on client keys. No raw Affinity data. |
| §5.3 semantic layer / Analyst | Consumer side | Post-crosswalk model. No provider raw data. |
| §5.4 audience agent | Consumer side | Same. |

Being able to draw this table is itself part of the pitch: **nothing crosses a
boundary it should not, and the ML output is aggregate rules rather than
individual scores.** That is what makes the approach defensible to a privacy
reviewer, which is what makes it sellable.

### 5.7 Cut order under time pressure

Build in this order and drop from the bottom:

1. §5.1 rules with the baseline-versus-enriched comparison — **without this there
   is no demo**
2. §5.1b prediction as bid multipliers + Q3-vs-Q4 accuracy proof — **the entry
   point for the pitch; gated on Affinity's prediction spec**
3. §5.2 descriptor normalization — cheap, self-contained, improves §5.1
4. §5.3 semantic view with verified queries — carries the live narration
5. §5.4 agent — strong finish, first to cut
6. §5.5 — slide only

---

## 5A. Platform-specific demos — schemas, UDFs, Streamlit apps

Each platform gets a standalone demo that can be presented independently. These
share the Affinity provider side, the matching waterfall, and the normalized ML
pipeline, but each has **its own output schema, UDFs, and Streamlit app** tailored
to the platform's workflow and vocabulary.

### 5A.1 TTD demo — "Better bidding through purchase outcomes"

**Audience:** The Trade Desk, DSP buyers

**Value story:** TTD sees impressions and pixel conversions but misses offline
purchases. Affinity fills the gap, producing bidding rules and prediction-based
multipliers that drop into TTD's existing bidder — no identity resolution needed
at bid time.

#### Output schema (`TTD_CONSUMER.DEMO_OUTPUT`)

| Table | Description |
|---|---|
| `BIDDING_RULES` | 500-700 rules: `RULE_ID`, `PREDICATE` (in TTD REDS field names), `BID_MULTIPLIER`, `SUPPORT`, `LIFT`, `CONFIDENCE_INTERVAL`, `MATCH_TIER`, `VALID_FROM/TO` |
| `PREDICTION_MULTIPLIERS` | Per matched individual × brand: `CLIENT_ID`, `BRAND_ID`, `BID_MULTIPLIER`, `PERCENTILE_RANK`, `PREDICTED_SPEND_30D` |
| `CONVERSION_ENRICHMENT` | Affinity purchases attributed to REDS impressions: `ImpressionId`, `TXID`, `BRAND_NAME`, `TRANS_AMOUNT`, `MATCH_CODE` |
| `ACCURACY_PROOF` | Q3 prediction vs Q4 actuals: `INDID`, `BRAND_ID`, `PREDICTED_SPEND`, `ACTUAL_SPEND`, `PERCENTILE_RANK` |

#### UDFs (`TTD_CONSUMER.UDFS`)

| UDF | Purpose |
|---|---|
| `TRANSLATE_RULE_TO_TTD_JSON(predicate)` | Converts a generic rule predicate to TTD bidder-loadable JSON format |
| `REDS_ENUM_LOOKUP(enum_type, value)` | Translates TTD integer enums (DeviceType, OS, Browser) to readable names |
| `ATTRIBUTION_WINDOW_FILTER(impression_ts, purchase_ts, window_days)` | Applies configurable attribution window |
| `COMPUTE_BID_MULTIPLIER(lift, support, shrinkage_factor)` | Multiplier with shrinkage toward 1.0 |

#### Streamlit app (`APPS.TTD_APP`)

**"Bid Rule Explorer + Spend Efficiency Dashboard"**

Pages:
1. **Rule Explorer** — browse the 500-700 rules, filter by device/geo/content dimensions, see lift and support. Drill into the evidence behind any rule.
2. **Spend Efficiency** — counterfactual comparison: same budget, default vs rule-adjusted bidder on held-out impressions. Cost per incremental purchase.
3. **Prediction Accuracy** — Q3 vs Q4 scatter plot, top-decile capture rate, dollar accuracy distribution.
4. **Match Waterfall** — interactive: reorder methods, see match rate change in real time. Compare `Originating` vs `Legacy` identity match rates.
5. **Conversion Gap** — side-by-side: what TTD's pixel saw vs what Affinity's card data saw. The delta is the product.

### 5A.2 PubMatic demo — "Premium inventory identification through purchase signals"

**Audience:** PubMatic, SSP sellers

**Value story:** PubMatic sells impressions but can't prove which inventory drives
real purchases. Affinity data lets them score inventory by purchase-driving
potential — turning floor pricing from guesswork into evidence and enabling
premium packaging backed by outcome data.

#### Output schema (`PUBMATIC_CONSUMER.DEMO_OUTPUT`)

| Table | Description |
|---|---|
| `INVENTORY_YIELD_SCORES` | Per supply dimension combo: `SITE_DOMAIN`, `AD_FORMAT`, `DEVICE_TYPE`, `GEO_DMA`, `CONTENT_GENRE`, `PURCHASE_RATE`, `BASELINE_RATE`, `YIELD_MULTIPLIER`, `SUPPORT` |
| `FLOOR_RECOMMENDATIONS` | Recommended floor prices by inventory segment: `SEGMENT_ID`, `DIMENSIONS`, `CURRENT_AVG_FLOOR`, `RECOMMENDED_FLOOR`, `EXPECTED_REVENUE_LIFT` |
| `PURCHASE_INVENTORY_PACKAGES` | Pre-built inventory packages for advertisers: `PACKAGE_NAME`, `INCLUDED_DOMAINS`, `INCLUDED_FORMATS`, `PURCHASE_RATE`, `ESTIMATED_REACH` |
| `MATCH_SUMMARY` | Match rates by identity method (lower than TTD — this is the honest SSP story) |

#### UDFs (`PUBMATIC_CONSUMER.UDFS`)

| UDF | Purpose |
|---|---|
| `SCORE_INVENTORY(domain, format, device_type, geo)` | Returns yield multiplier for an inventory combination |
| `RECOMMEND_FLOOR(current_floor, yield_score, market_rate)` | Floor price recommendation based on purchase evidence |
| `OPENRTB_DEVICE_TYPE_LABEL(enum_val)` | AdCOM device type integer → readable label |
| `PACKAGE_INVENTORY(min_purchase_rate, max_domains)` | Builds a premium inventory package above purchase-rate threshold |

#### Streamlit app (`APPS.PUBMATIC_APP`)

**"Inventory Yield Scorer + Floor Optimizer"**

Pages:
1. **Yield Heatmap** — domains × ad formats, colored by purchase conversion rate. Shows which inventory actually drives outcomes.
2. **Floor Optimizer** — input current floor prices, see recommended floors based on purchase evidence. Revenue lift projection.
3. **Premium Packaging** — build purchaser-backed inventory packages by selecting dimension thresholds. Export package definitions.
4. **Identity Coverage** — match rate breakdown by method. Honest view of SSP-side identity limitations and why broad Affinity coverage matters.
5. **Advertiser Story** — for a selected vertical, show which publishers + placements drove the most purchases. The evidence PubMatic can take to advertisers.

### 5A.3 Kargo demo — "Engagement-to-purchase attribution for CTV and display"

**Audience:** Kargo, ad servers, publishers

**Value story:** Kargo has rich engagement data (viewability, video quartiles) but
no purchase outcomes. Affinity closes the loop: which creative formats,
placements, publishers and CTV apps actually drive purchases. Especially powerful
for CTV, where attribution is weakest and CPMs are highest.

#### Output schema (`KARGO_CONSUMER.DEMO_OUTPUT`)

| Table | Description |
|---|---|
| `ENGAGEMENT_PURCHASE_ATTRIBUTION` | Per event × matched purchase: `AUCTION_ID`, `EVENT_TYPE`, `PUBLISHER_DOMAIN`, `CREATIVE_FORMAT`, `TXID`, `BRAND_NAME`, `TRANS_AMOUNT`, `MATCH_CODE` |
| `PLACEMENT_PURCHASE_SCORES` | Per placement: `PLACEMENT_NAME`, `PLACEMENT_TYPE`, `CREATIVE_FORMAT`, `IMPRESSIONS`, `VIEWABLE_IMPRESSIONS`, `VIDEO_COMPLETIONS`, `PURCHASES`, `PURCHASE_RATE`, `VIEWABLE_PURCHASE_RATE` |
| `CTV_ATTRIBUTION` | CTV-specific: `DEVICE_PLATFORM`, `APP_NAME`, `APP_BUNDLE_ID`, `IMPRESSIONS`, `VIDEO_COMPLETIONS`, `PURCHASES`, `PURCHASE_RATE` |
| `ENGAGEMENT_QUALITY_RULES` | Rules in Kargo field names: `RULE_ID`, `PREDICATE`, `PURCHASE_RATE`, `LIFT`, `SUPPORT`, targeting creative format, placement type, publisher, DMA, device platform |

#### UDFs (`KARGO_CONSUMER.UDFS`)

| UDF | Purpose |
|---|---|
| `ENGAGEMENT_WEIGHT(event_type)` | Returns weight for engagement-based labels: video_complete > video_midpoint > impression > click |
| `CTV_PURCHASE_RATE(app_bundle, device_platform, dma)` | Purchase rate for a CTV inventory slot |
| `VIEWABILITY_CONDITIONED_LABEL(viewable, purchased)` | Label logic: viewable + purchased vs not-viewable (excluded from training) |
| `FORMAT_PURCHASE_LIFT(creative_format, baseline_rate)` | Lift of a Kargo creative format over baseline purchase rate |

#### Streamlit app (`APPS.KARGO_APP`)

**"Engagement-to-Purchase Attribution + CTV Dashboard"**

Pages:
1. **Attribution Funnel** — video_load → start → quartiles → complete → purchase. Drop-off rates at each stage, by creative format and placement.
2. **CTV Scoreboard** — CTV apps and platforms ranked by purchase conversion rate. The evidence Kargo needs to justify CTV CPMs.
3. **Publisher Leaderboard** — publishers ranked by purchase-driving ability. Split by viewable vs all impressions.
4. **Creative Format Comparison** — Kargo's proprietary formats (Runway, Breakaway, HighRise, etc.) ranked by purchase lift over standard banners.
5. **Advertiser Report** — for a selected campaign, full engagement-to-purchase journey. Exportable proof of ROI for advertiser conversations.

### 5A.4 AdRoll demo — "Conversion enrichment + B2B account scoring"

**Audience:** AdRoll / NextRoll, retargeting buyers

**Value story:** AdRoll sees conversion events and attributes revenue via pixel —
but a pixel captures intent, not outcome. Affinity verifies which conversions
represent actual card swipes, generates funnel intelligence rules, and — uniquely
for AdRoll — scores B2B accounts by real purchase propensity using Site Traffic
Revealer firmographics. CTV campaigns are validated by actual purchases, not just
impressions.

#### Output schema (`ADROLL_CONSUMER` + `ADROLL_B2B`)

| Table | Schema | Description |
|---|---|---|
| `ADROLL_FUNNEL_PURCHASE_RULES` | `ADROLL_CONSUMER` | 120 ML-derived rules: `RULE_ID`, `PREDICATE`, `DIM`, `DIM_VALUE`, `SUPPORT`, `PURCHASE_RATE`, `RAW_LIFT`, `SHRUNK_LIFT`, `BID_MULTIPLIER`, `CI_LOWER/UPPER`, `RULE_ACTION` (BOOST/NEUTRAL/SUPPRESS) |
| `ADROLL_CHANNEL_ATTRIBUTION` | `ADROLL_CONSUMER` | Per channel: `CHANNEL`, `CONVERSIONS`, `PIXEL_REVENUE`, `CARD_SWIPE_REVENUE`, `REVENUE_DELTA_PCT`, `VERIFIED_PURCHASES`, `TRUE_PURCHASE_RATE_PCT` |
| `ADROLL_CTV_ATTRIBUTION` | `ADROLL_CONSUMER` | 50 CTV campaigns: `CAMPAIGN_NAME`, `VIDEO_IMPRESSIONS`, `VIDEO_COMPLETIONS`, `CTV_SPEND`, `MATCHED_PURCHASERS`, `TOTAL_PURCHASE_VALUE`, `CTV_ROAS`, `COMPLETION_TO_PURCHASE_RATE` |
| `ADROLL_AUDIENCE_SEGMENTS` | `ADROLL_CONSUMER` | Audience segments: `SEGMENT_EID`, `SEGMENT_NAME`, `SEGMENT_TYPE`, `DURATION`, `IS_CONVERSION`, `CONVERSION_VALUE`, `ESTIMATED_SIZE` |
| `ADROLL_ACCOUNT_SCORES` | `ADROLL_B2B` | 5,000 B2B accounts: `DOMAIN`, `COMPANY_NAME`, `COMPANY_INDUSTRY`, `COMPANY_REVENUE`, `COMPANY_SIZE`, `JOURNEY_STAGE`, `TOTAL_VISITS`, `PURCHASE_SCORE`, `PREDICTED_ACCOUNT_VALUE`, `SCORE_TIER` (HOT/WARM/COLD) |
| `ADROLL_SITE_TRAFFIC_REVEALER` | `ADROLL_B2B` | Raw firmographic data: 10 fields per company including `CONTACT_EMAIL_SHA256` for Affinity matching |

#### ML models — 5 AdRoll-specific models

| Model | Type | Purpose | Key metric |
|---|---|---|---|
| `ADROLL_CONVERSION_CLASSIFIER` | `SNOWFLAKE.ML.CLASSIFICATION` | Predicts which pixel conversions are real card-swipe purchases | Top decile 3.22x lift |
| `ADROLL_REVENUE_CLASSIFIER` | `SNOWFLAKE.ML.CLASSIFICATION` | Classifies conversions into revenue tiers (HIGH/MEDIUM/LOW) | Revenue-tier separation |
| `ADROLL_FUNNEL_PREDICTOR` | `SNOWFLAKE.ML.CLASSIFICATION` | Predicts future purchase from pre-conversion funnel behavior | COMPOSITE_PROPENSITY is #1 feature |
| `ADROLL_B2B_ACCOUNT_SCORER` | `SNOWFLAKE.ML.CLASSIFICATION` | Scores companies by purchase propensity using firmographic + visit data | TOTAL_VISITS is #1 feature |
| `ADROLL_BRAND_FORECAST` | `SNOWFLAKE.ML.FORECAST` | Brand-level spend forecasting from AdRoll-attributed conversions | Directional brand ranking |

#### ML validation tables

| Table | Schema | Description |
|---|---|---|
| `ADROLL_CONVERSION_DECILES` | `ML` | 10 decile bins with purchase rate and lift. Top decile: 3.22x lift. |
| `ADROLL_FEATURE_IMPORTANCE` | `ML` | Feature importance for Conversion Classifier and Funnel Predictor side-by-side. Conversion: ATTRIBUTED_REVENUE #1. Funnel: COMPOSITE_PROPENSITY #1. |
| `ADROLL_HOLDOUT_RESULTS` | `ML` | Training vs holdout: purchase rate, revenue, conversion counts. Confirms model generalizes. |

#### Streamlit app (`APPS.ADROLL_APP`)

**"AdRoll Purchase Intelligence — Conversion + B2B + CTV"**

Tabs:
1. **The Opportunity** — side-by-side (AdRoll events vs Affinity transactions), channel revenue comparison (pixel vs card swipe). The gap is invisible revenue.
2. **Conversion Enrichment** — channel attribution table, true purchase rate by channel, match coverage metric (80.6% via email SHA-256).
3. **Funnel Intelligence** — 120 ML-derived funnel rules (BOOST/NEUTRAL/SUPPRESS), filters by action and dimension, lift histogram. Rules drop directly into AdRoll's bidding engine.
4. **B2B Account Scoring** — HOT/WARM/COLD tiers across 5,000 companies. Industry × purchase score heatmap. Top 20 accounts by predicted value. Journey stage validation (MQL/Opportunity have highest scores). **Unique to AdRoll — no other platform has this.**
5. **CTV + Video Attribution** — 50 CTV campaigns ranked by verified purchase value. Completion-to-purchase rate. ROAS comparison. Note: impression-level CTV data not publicly available; attribution uses matched conversion events.
6. **ML Models + Features** — 5 model cards, decile lift chart (3.22x), feature importance side-by-side (Conversion vs Funnel), holdout validation.

### 5A.5 Cross-platform comparison view

An additional page in each Streamlit app (or a shared app) that shows the
**same Affinity outcome data producing different outputs for four platforms**:

- Side-by-side: TTD gets bidding rules, AdRoll gets funnel intelligence + B2B
  account scores, PubMatic gets yield scores, Kargo gets attribution reports —
  all from the same matched purchase outcomes.
- Match rate comparison across platforms (AdRoll highest at 80.6% via email,
  TTD 44.8%, PubMatic 26.2%, Kargo 22.5%).
- 12 ML models across all 4 platforms, with decile lift comparison.

This is the Affinity pitch: **one data asset, four monetization paths.**

---

## 6. ⛔ Checkpoint — inputs needed before generation

Phases 0 and 1 can start now. **Phase 2 onward is gated on these.**

1. **Volumes.** Proposed defaults to accept or override:

   | Tier | Individuals | Households | Cards | Transactions | Impressions (per platform) |
   |---|---|---|---|---|---|
   | Dev | 100 K | 65 K | 120 K | 12 M | 50 M |
   | Demo | 1 M | 650 K | 1.2 M | 120 M | 500 M |

2. **Match-rate targets per waterfall step** — for TTD (all 8 methods), and
   separately for PubMatic/Kargo (MAID, RampID/UID2, IP only — expect lower
   overall rates).
3. **Advertiser CRM identifier coverage** — share carrying name+address vs HEM vs
   MAID, and overlap. Note this is the CRM, not the impression log (§3.2.1).
4. **Identity spine coverage** (TTD only) — share of CRM records resolving to any
   TTD ID; the mix across `TDID` / `DAID` / `RawUID2` / `UID2Token` / `RampID` /
   `EUID`; the `Originating` vs `Legacy` split.
5. **Vertical and campaign** — which brands and categories the outcome signal
   centres on. Drives taxonomy content and makes the ML result legible.
6. **Qualifying purchase definition** (§5.1 label) — category scope, minimum
   basket, attribution window.
7. **Bidding rule output contract** — confirm or amend the §5.1 proposal.
8. **Demo scope** — which of §5.1, 5.1b, 5.2–5.4, and §5A.1–5A.3 are in for Ad Week.
9. **Prediction feed spec** — Affinity's raw data and prediction feed field
   definitions. Gates §5.1b and the accuracy proof.
10. **Platform demo scope** — confirm which of the three platform-specific Streamlit
    apps (§5A.1–5A.3) to build vs stub.

---

## 7. Phases

### Phase 0 — Environment ✅ COMPLETE

- [x] Connect to Snowflake account (see README.md for connection setup).
- [x] Confirm SFDCR is enabled in the account.
- [x] Create `AFFINITY_DEMO` database with 11 schemas; provision `AFFINITY_GEN_WH`
      (Large) and `AFFINITY_DEMO_WH` (Medium).
- [x] Load REDS enum lookup tables into `UTIL` (5 tables).
- [x] Load OpenRTB AdCOM enum tables into `UTIL` (5 tables).
- [x] Load Kargo + Affinity match method enums into `UTIL` (4 tables).

### Phase 1 — Affinity provider dataset ✅ COMPLETE

- [x] Taxonomy: 113 brands, 53 categories, 47 MCCs, 113 stores, 565 locations.
- [x] `CC_EXT_V`: 134K cards, 100K individuals, 87K households, multi-card, NULL patterns.
- [x] `TX_SRC_V`: 12M transactions, 18-month span, right-skewed amounts (median $37).
- [x] `MID_SRC_V`: 565 merchants with 8 garbling patterns for noisy MERCHDESC.
- [x] `MID_NORMALIZED` + view: Cortex AI descriptor normalization — 565/565 parsed.
- [x] `PREDICTION_FEED_V`: 1M rows, propensity (12-mo quarterly, TOP_1/5/10% tiers)
      + predicted spend (30-day weekly). Schema from Affinity's bid optimization doc.
- [x] `CUSTOMER_CC_MAP_V`: 100K individual crosswalk.

### Phase 2 — Consumer datasets ✅ COMPLETE

#### 2a. TTD consumer
- [x] `ADVERTISER_CRM`: 100K records with name/address/email(60%)/MAID(40%)/IP(70%).
- [x] `IDENTITY_SPINE`: 100K with TDID(50%)/DAID(35%)/UID2(30%)/RampID(20%)/EUID(15%), spine gaps.
- [x] `REDS_IMPRESSIONS`: 10M rows, 28 columns, 18-month span, CombinedIdentifier, OfflineProviderID(5%).
- [x] `REDS_CONVERSIONS`: 500K with MonetaryValue(30%), OrderId(20%), OfflineProviderID(8%).
- [x] `MATCHING_INPUT`: 100K hashed (SHA-512) with spine IDs.

#### 2b. PubMatic consumer
- [x] `OPENRTB_IMPRESSIONS`: 10M rows, 43 columns, EID/UID identity, CTV content subset, bidfloor.
- [x] `MATCHING_INPUT`: ~10M deduplicated identities.

#### 2c. Kargo consumer
- [x] `KARGO_LLD`: 10M rows, 47 columns, video event sequences, MOAT viewability, CTV fields(20%).
- [x] `MATCHING_INPUT`: ~10M with RampID(60%), MAID(20%), IP fallback.

#### 2d. Normalized impression model
- [x] `IMPRESSIONS_NORMALIZED` view: ~23M rows spanning all 3 platforms + AdRoll conversions.
- [x] 5 enum translation UDFs in `UTIL`.

#### 2e. AdRoll consumer
- [x] `ADROLL_GCR`: 2.2M conversions, 28 columns, email_sha256 identity, 7 channels.
- [x] `ADROLL_S2S_EVENTS`: 10M funnel events, 13 event types, B2B signals (demoRequest, contactSales, signupTrial).
- [x] `ADROLL_CAMPAIGN_METRICS`: Campaign-level aggregates, CTV video completions.
- [x] `ADROLL_SITE_TRAFFIC_REVEALER`: 5,000 companies, firmographic data (industry, revenue, size, journey stage).
- [x] `MATCHING_INPUT`: ~200K email SHA-256 identities.

### Phase 3 — Clean room and matching ✅ COMPLETE

- [x] `HASH_IDENTITY()` UDF, `MATCH_METHOD_ORDER` table (12 methods), `RUN_MATCH_WATERFALL()` proc.
- [x] Ground truth planted: TTD 60K, PubMatic 35K, Kargo 30K, AdRoll 200K overlaps.
- [x] `CROSSWALK_TTD`: 44,812 matched (44.8% rate, all 12 methods).
- [x] `CROSSWALK_PUBMATIC`: 26,231 matched (26.2%, 3 methods).
- [x] `CROSSWALK_KARGO`: 22,475 matched (22.5%, 2 methods).
- [x] `CROSSWALK_ADROLL`: 80,607 matched (80.6% of Affinity base, email SHA-256).
- [x] `CROSSWALK_ALL` view + `MATCH_RATE_SUMMARY` + `ADROLL_MATCH_RATE_SUMMARY` views.

### Phase 4 — AI/ML ✅ COMPLETE

#### ML Architecture — Affinity's model + Snowflake ML (the Default vs Custom story)

```
AFFINITY (Provider)                    SNOWFLAKE ML (Consumer Side)
┌─────────────────────┐
│  Affinity's Model     │
│  (Affinity IP)      │                ┌──────────────────────────────────────┐
│                     │                │  CUSTOM TIER — trained in Snowflake  │
│  ┌───────────────┐  │                │                                      │
│  │ Propensity    │──┼──DEFAULT──────▶│  PURCHASE_CLASSIFIER                 │
│  │ (12-mo, qtr)  │  │  Delivered     │  SNOWFLAKE.ML.CLASSIFICATION         │
│  │ TOP 1/5/10%   │  │  as-is to      │  12 features, 1.6M training rows     │
│  └───────────────┘  │  bidder         │  Top decile: 2.15x lift, 21.5%      │
│                     │                │  cumulative purchase capture          │
│  ┌───────────────┐  │                │                                      │
│  │ Pred. Spend   │──┼──DEFAULT──────▶│  SPEND_TIER_CLASSIFIER               │
│  │ (30-day, wk)  │  │  Converted     │  SNOWFLAKE.ML.CLASSIFICATION         │
│  │ $/person/brand│  │  to bid        │  7 features (prior spend, income,    │
│  └───────────────┘  │  multipliers   │  age, category)                      │
│                     │                │                                      │
│  ┌───────────────┐  │                │  BRAND_SPEND_FORECAST                 │
│  │ Transaction   │──┼──LABELS───────▶│  SNOWFLAKE.ML.FORECAST               │
│  │ History       │  │  Observed      │  112 brands × 11 months time series  │
│  │ (86B+ txns)   │  │  purchase      │  Directional brand-level forecasting │
│  └───────────────┘  │  outcomes      └──────────────────────────────────────┘
└─────────────────────┘
                                       ┌──────────────────────────────────────┐
         │                             │  OUTPUTS                             │
         │                             │                                      │
         └──── BOTH GRADED ON ────────▶│  Same holdout purchase data          │
               SAME RULER              │  Default vs Custom comparable        │
                                       │  Incrementality: holdout prevents    │
                                       │  the "bid on likely buyers" trap     │
                                       └──────────────────────────────────────┘
```

**Key insight for the pitch:** Affinity's predictions work as the *Default* tier on
day one — no training window, no first-party data required. Platforms that want
more train *Custom* models on their own data (exposure logs, CRM, conversions)
using Affinity outcomes as labels and predictions as features, via Snowflake ML.
Both are graded against the same observed purchase holdout, so a client can see
whether their custom model actually beat the default.

#### Model Registry — 12 Snowflake ML models

| Model | Platform | Type | Purpose | Key metric |
|---|---|---|---|---|
| `PURCHASE_CLASSIFIER` | TTD | `SNOWFLAKE.ML.CLASSIFICATION` | Impression → purchase (binary) | Top decile 2.15x lift |
| `SPEND_TIER_CLASSIFIER` | TTD | `SNOWFLAKE.ML.CLASSIFICATION` | Individual×brand → spend tiers | Category spend 23%, income 22% top features |
| `BRAND_SPEND_FORECAST` | Shared | `SNOWFLAKE.ML.FORECAST` | Brand-level monthly spend forecasting | Directional brand ranking, 112 brands |
| `PUBMATIC_YIELD_CLASSIFIER` | PubMatic | `SNOWFLAKE.ML.CLASSIFICATION` | Inventory → purchase conversion | Top decile 2.5x lift |
| `PUBMATIC_SPEND_CLASSIFIER` | PubMatic | `SNOWFLAKE.ML.CLASSIFICATION` | Inventory → spend tiers | BIDFLOOR #1 feature |
| `KARGO_ENGAGEMENT_CLASSIFIER` | Kargo | `SNOWFLAKE.ML.CLASSIFICATION` | Engagement → purchase | Top decile 3.45x lift |
| `KARGO_SPEND_CLASSIFIER` | Kargo | `SNOWFLAKE.ML.CLASSIFICATION` | Engagement → spend tiers | COMPOSITE_PROPENSITY #1 |
| `ADROLL_CONVERSION_CLASSIFIER` | AdRoll | `SNOWFLAKE.ML.CLASSIFICATION` | Conversion → real purchase | Top decile 3.22x lift |
| `ADROLL_REVENUE_CLASSIFIER` | AdRoll | `SNOWFLAKE.ML.CLASSIFICATION` | Conversion → revenue tier | Revenue-tier separation |
| `ADROLL_FUNNEL_PREDICTOR` | AdRoll | `SNOWFLAKE.ML.CLASSIFICATION` | Funnel behavior → future purchase | COMPOSITE_PROPENSITY #1 |
| `ADROLL_B2B_ACCOUNT_SCORER` | AdRoll | `SNOWFLAKE.ML.CLASSIFICATION` | Company firmographics → purchase score | TOTAL_VISITS #1 feature |
| `ADROLL_BRAND_FORECAST` | AdRoll | `SNOWFLAKE.ML.FORECAST` | AdRoll-attributed brand-level forecast | Directional brand ranking |

#### Feature importance (a demo highlight)

**Purchase Classifier** — what drives ad-to-purchase conversion:
```
MEDIA_COST ████████████████████ 18.5%    ← bid economics matter
SITE       ███████████████████  18.1%    ← publisher quality matters
MATCH_CODE ████████████████     15.8%    ← better identity = better outcome
GEO_DMA    ███████████████      15.0%    ← local retail density
DEVICE_TYPE █████████            6.9%    ← CTV > mobile > desktop
CONTENT    █████████            6.8%    ← sports/lifestyle > news
```

**Spend Tier Classifier** — what predicts how much someone will spend:
```
CATEGORY_SPEND ████████████████████████  23.2%  ← past category behavior
INCOME         ███████████████████████   22.1%  ← affluence
AGE            ██████████████████        17.8%  ← life stage
BRAND_SPEND    █████████████████         16.5%  ← brand loyalty
CATEGORY       ███████████████           14.8%  ← which vertical
```

#### Model validation — ML vs synthetic baseline

| Tier | Synthetic proof (flat) | ML model (real separation) |
|---|---|---|
| TOP_1PCT hit rate | 17.02% (no signal) | **2.50%** (4x general pop) |
| TOP_5PCT hit rate | 17.44% | **1.65%** (2.6x) |
| TOP_10PCT hit rate | 17.55% | **1.26%** (2x) |
| General hit rate | 17.15% | **0.62%** (baseline) |
| **Discrimination** | **None** | **Clear monotonic separation** |

#### Realistic signal engineering

Purchase propensity is driven by a `PROPENSITY_DRIVERS` table (42 dimension-level
multipliers) so that synthetic data exhibits realistic patterns:

| Metric | Value | Real-world benchmark |
|---|---|---|
| Overall purchase rate | 0.74% | 0.5–3% |
| Rule lift range | 0.44x – 2.03x | 0.3x – 5x |
| Rules: BOOST / NEUTRAL / SUPPRESS | 102 / 174 / 118 | ~25/50/25 |
| CTV vs Display purchase rate | 1.01% vs 0.48% (2.1x) | 1.5–3x |
| EXCT vs IPA1 match purchase rate | 0.95% vs 0.53% (1.8x) | Better identity = better targeting |
| Holdout consistency | Train 0.74% ≈ Holdout 0.75% | Should be close |

#### 4a. Cross-platform ML (shared) — all done
- [x] `TRAINING_SET_TTD`: 2M labeled impressions, 20% holdout, deterministic hash draws.
- [x] `PURCHASE_CLASSIFIER`: Snowflake ML Classification, 12 features, 1.6M training.
- [x] `SPEND_TIER_CLASSIFIER`: Snowflake ML Classification on 4 spend tiers, 500K training.
- [x] `BRAND_SPEND_FORECAST`: Snowflake ML Forecast, 112 brands multi-series.
- [x] `BIDDING_RULES`: 394 rules from SQL + `ML_BIDDING_RULES`: 63 rules from ML model.
- [x] `QUADRANT_MULTIPLIERS`: 1M rows — Net-New 23% @ 4.5x, Conquesting 19% @ 2.75x,
      VIPs 14% @ 2.52x, Waste 44% @ 0.46x.
- [x] `DELIVERY_AUDIENCE_MULTIPLIER`, `DELIVERY_PER_ID_INSTRUCTION` (573K),
      `DELIVERY_VALUE_BASED_BIDDING` (384K).
- [x] Model validation: `MODEL_VALIDATION_PURCHASE_DECILES`, `MODEL_VALIDATION_PURCHASE_CONFUSION`,
      `MODEL_VALIDATION_FEATURE_IMPORTANCE`, `MODEL_VALIDATION_TIER_COMPARISON`,
      `MODEL_VALIDATION_BRAND_FORECAST`, `MODEL_REGISTRY`.

#### 4b. Platform-specific outputs — all done
- [x] **TTD:** `DEMO_OUTPUT_BIDDING_RULES` (394), `DEMO_OUTPUT_PREDICTION_MULTIPLIERS`
      (456K), `DEMO_OUTPUT_CONVERSION_ENRICHMENT` (14.8K). 3 UDFs.
- [x] **PubMatic:** `DEMO_OUTPUT_INVENTORY_YIELD_SCORES`, `DEMO_OUTPUT_FLOOR_RECOMMENDATIONS`
      (200), `DEMO_OUTPUT_PURCHASE_INVENTORY_PACKAGES`. 2 UDFs.
- [x] **Kargo:** `DEMO_OUTPUT_ENGAGEMENT_PURCHASE_ATTR`, `DEMO_OUTPUT_PLACEMENT_PURCHASE_SCORES`,
      `DEMO_OUTPUT_CTV_ATTRIBUTION`, `DEMO_OUTPUT_ENGAGEMENT_QUALITY_RULES`. 2 UDFs.
- [x] **AdRoll:** `ADROLL_FUNNEL_PURCHASE_RULES` (120), `ADROLL_CHANNEL_ATTRIBUTION` (7 channels),
      `ADROLL_CTV_ATTRIBUTION` (50 campaigns), `ADROLL_AUDIENCE_SEGMENTS`,
      `ADROLL_ACCOUNT_SCORES` (5,000 companies). 5 ML models trained.

#### 4c. AdRoll-specific ML validation — all done
- [x] `ADROLL_CONVERSION_DECILES`: 3.22x top-decile lift (strongest after Kargo).
- [x] `ADROLL_FEATURE_IMPORTANCE`: Conversion Classifier (ATTRIBUTED_REVENUE #1) vs
      Funnel Predictor (COMPOSITE_PROPENSITY #1) — distinct feature profiles.
- [x] `ADROLL_HOLDOUT_RESULTS`: Training vs holdout confirms generalization.

### Phase 5 — AI layer, Streamlit apps, and rehearsal ✅ COMPLETE

- [x] `AI` schema views: `DEMO_ANALYTICS_V`, `BIDDING_RULES_V`, `QUADRANT_SUMMARY_V`,
      `PLATFORM_MATCH_RATES_V` — for Cortex Analyst and Streamlit.
- [x] **TTD Streamlit** (`APPS.TTD_BID_EXPLORER`): 5 tabs — Rule Explorer (394 rules
      with lift distribution), Quadrant Strategy (4-quadrant metrics + delivery shapes),
      Spend Efficiency (holdout comparison + dimension drill-down), Prediction Accuracy
      (tier hit rates + conversion gap), Match Waterfall.
- [x] **PubMatic Streamlit** (`APPS.PUBMATIC_YIELD_SCORER`): 6 tabs — Yield Heatmap
      (publisher × format), Floor Optimizer (200 recommendations), Premium Packages,
      SSP Bidding Rules (271), ML Models (2 models, 2.5x lift), Identity Coverage.
- [x] **Kargo Streamlit** (`APPS.KARGO_ATTRIBUTION_DASHBOARD`): 6 tabs — Attribution
      Funnel (placement scores), CTV Scoreboard (platform + app ranking), Creative Format
      Comparison (lift analysis), ML Engagement Rules (191), ML Models (2 models, 3.45x lift),
      Identity Coverage.
- [x] **AdRoll Streamlit** (`APPS.ADROLL_PURCHASE_INTELLIGENCE`): 6 tabs — The Opportunity
      (pixel vs card swipe), Conversion Enrichment (true purchase rate, 80.6% match),
      Funnel Intelligence (120 rules), B2B Account Scoring (5,000 companies, HOT/WARM/COLD),
      CTV + Video Attribution (50 campaigns), ML Models (5 models, 3.22x lift).
- [x] **Cross-Platform** (`APPS.CROSS_PLATFORM_COMPARISON`): 4 tabs — Match Rate Comparison
      (4 platforms, AdRoll 80.6% leading), Platform Outputs (2x2 grid), ML Models
      (12-model registry + decile lift comparison), The Pitch (one data asset, four paths).
- [x] **Pipeline** (`APPS.PIPELINE_END_TO_END`): 6-tab end-to-end story — The Problem,
      Data Clean Room (privacy boundaries), Identity Resolution (interactive waterfall),
      Affinity Enrichment (before/after), ML Training (models + feature importance),
      Actionable Output (rules + quadrants + delivery shapes).

### Phase 6 — Ad Week (Oct 5)

---

## 8. Open items

| # | Item | Status |
|---|---|---|
| 1 | DCR topology — Affinity is provider | ✅ Confirmed |
| 2 | Affinity field schema and matching algorithm | ✅ Fully specified from dictionary v3 |
| 3 | TTD REDS schema | ✅ Fully specified from TTD documentation |
| 4 | PubMatic schema — OpenRTB 2.6 flattened | ✅ Specified from OpenRTB 2.6 spec |
| 5 | Kargo schema — LLD V0 | ✅ Specified from Kargo LLD Schema V0 |
| 6 | Build approach — rebuild in SFDCR | ✅ Recommended, §2 |
| 7 | Partner scope — TTD + PubMatic + Kargo + AdRoll | ✅ All 4 platforms built (AdRoll added Sep 2026) |
| 8 | Volumes, match rates, coverage, label, rule contract | ✅ Dev tier built: 100K ind, 12M tx, 10M imp/platform |
| 9 | Demo scope across §5.1–5.4 and §5A.1–5A.3 | ⛔ §6 item 8 |
| 10 | Account edition and SFDCR enablement | ✅ Confirmed in Phase 0 |
| 11 | Affinity provisioning for the real app | ➖ Stretch only, not on critical path |
| 12 | `HASH_TYPE` dictionary discrepancy | Raise with Affinity |
| 13 | Prediction feed spec from Affinity | ✅ Received — `Affinity-Snowflake-Bid-Optimization.pdf`. Two model outputs (propensity + predicted spend), 4-quadrant strategy, 3 delivery shapes, validation holdout. `PREDICTION_FEED_V` updated. |
| 14 | Platform-specific Streamlit app scope | ⛔ §6 item 10 — confirm which apps to build vs stub |

---

## 9. Reference material

| Source | Provides |
|---|---|
| `Affinity Solutions_DCR_Data Dictionary US_2025_v3.xlsx` | Authoritative Affinity schema, match methods and codes, fuzzy sub-codes, join path, sample value formats |
| `AFS Matching DCR Deep Dive_7.10.25.pdf` | Topology, app object structure, install flow, DCR requirements, waterfall ordering |
| `REDS_sample_data.xlsx` | TTD's published sample — real value shapes for Impressions (60 cols), Conversions (25), Clicks (15), VideoEvents (22) |
| TTD REDS documentation | Full REDS schema, enum tables, identity model, cross-feed join rules, published attribution methodology |
| `OpenRTB-2-6_FINAL_PubMatic.pdf` | OpenRTB 2.6 spec — BidRequest, Imp, Banner, Video, Site, App, Device, Geo, User, EID/UID object schemas |
| `KARGO/` CSV files | Kargo LLD Schema V0 (47 fields), sample data, request form, FAQs |
| `apidocs.nextroll.com` (online) | AdRoll/NextRoll API documentation: GraphQL Reporting API, Granular Conversion Report schema (28 fields), S2S Event API (13 event types), Site Traffic Revealer (10 fields), campaign metrics |
| Fivetran AdRoll connector docs | Schema verification: GCR fields, S2S events, campaign metrics mapping |
| `Affinity-Snowflake-Bid-Optimization.pdf` | Affinity's spec: two prediction models (propensity 12-mo quarterly + predicted spend 30-day weekly), 4-quadrant bidding strategy, 3 delivery shapes, default-vs-custom framework, validation holdout, incrementality caveat, coverage caveats |

**TTD documentation access.** The `open.thetradedesk.com` docs host redirects every
request to an ad-tracking endpoint and is unusable. `partnersandbox.thetradedesk.com`
serves the same documentation anonymously:

```
https://partnersandbox.thetradedesk.com/v3/portal/reds/doc/<PageName>
```

Pages: `REDSFeedsSummary`, `REDSIncludedColumns`, `Impressions`, `Conversions`,
`Clicks`, `VideoEvents`, `REDSOriginatingIDs`, `IdToNameMapping`,
`REDSDataPrivacyRetention`, `REDSSnowflake`, `REDSAccessOptions`.

⚠️ **TTD retires this portal on 2026-09-15.** Everything needed is already captured
in this plan and in the local sample file. Do not plan to re-fetch after that date.

**Schema drift.** TTD's 2020 sample file uses `SupplyVendor`, `Metro` and
`MatchedFoldPosition`; current 3-0-0 docs use `SupplyVendorName`, `NielsenDMA` and
drop fold position. Generate to current 3-0-0 names.
