import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import altair as alt

session = get_active_session()

st.set_page_config(page_title="Affinity DCR Pipeline", layout="wide", page_icon="🔒")
st.title("🔒 Affinity Solutions — End-to-End DCR + ML Pipeline")
st.caption("How purchase data and exposure logs combine securely to produce actionable bid intelligence")

steps = st.tabs([
    "1. The Problem",
    "2. Data Clean Room",
    "3. Identity Resolution",
    "4. Affinity Enrichment",
    "5. ML Training",
    "6. Actionable Output"
])

# ── Step 1: The Problem ──────────────────────────────────────────────────────
with steps[0]:
    st.header("The Opportunity: Two Powerful Halves, Better Together")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("What the Platform Has")
        st.markdown("""
        - **Impressions**: what was served, to whom, where, at what price
        - **Clicks & video events**: engagement signals
        - **Pixel conversions**: what the advertiser's tag happens to observe
        """)
        st.error("**Missing:** What happened next. Did the person actually buy?")

        imp_count = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.TTD_CONSUMER.REDS_IMPRESSIONS").to_pandas()
        conv_count = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.TTD_CONSUMER.REDS_CONVERSIONS").to_pandas()
        c1, c2 = st.columns(2)
        c1.metric("TTD Impressions", f"{int(imp_count['C'][0]):,}")
        c2.metric("Pixel Conversions", f"{int(conv_count['C'][0]):,}")
        st.caption(f"Conversion rate from pixel: {int(conv_count['C'][0])/int(imp_count['C'][0])*100:.1f}% — but most purchases are card swipes the pixel never sees.")

    with col2:
        st.subheader("What Affinity Has")
        st.markdown("""
        - **300M+ cards** linked to **160M consumers**
        - **5,300+ brands**, online and offline, across all 50 states
        - **Daily refresh** of observed, verified purchases
        - **Two prediction models**: propensity (12-mo) + predicted spend (30-day)
        """)
        st.error("**Missing:** Which ads these people saw. No exposure data.")

        tx_count = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.AFS_PROVIDER.TX_SRC_V").to_pandas()
        ind_count = session.sql("SELECT COUNT(DISTINCT INDID) AS c FROM AFFINITY_DEMO.AFS_PROVIDER.CC_EXT_V").to_pandas()
        c1, c2 = st.columns(2)
        c1.metric("Transactions", f"{int(tx_count['C'][0]):,}")
        c2.metric("Individuals", f"{int(ind_count['C'][0]):,}")

    st.markdown("---")
    st.markdown("""### Neither party can share raw data.
    **A Data Clean Room is the only place this join can happen.**
    The platform can't send impression logs to Affinity. Affinity can't send purchase records to the platform.
    Both need to contribute data to a governed environment where the join runs under strict controls.""")

# ── Step 2: Data Clean Room ──────────────────────────────────────────────────
with steps[1]:
    st.header("The Data Clean Room — What Stays Where")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.subheader("🔵 Affinity (Provider)")
        st.markdown("""
        **Contributes to the clean room:**
        - Transaction history (TX_SRC_V)
        - Card-individual-household linkage (CC_EXT_V)
        - Merchant taxonomy and brand mapping
        - Prediction feed (propensity + predicted spend)
        - Identity crosswalk (AFSID)

        **Never leaves Affinity's side:**
        - Raw PII (names, addresses)
        - Individual card numbers
        - Full transaction detail by person
        - Prediction model weights and IP
        """)
        st.info("Affinity sees: nothing about the platform's impressions, CRM, or identity spine.")

    with col2:
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("### 🔒")
        st.markdown("### Clean Room")
        st.markdown("Hashed identity join")
        st.markdown("Crosswalk only")
        st.markdown("No raw PII crosses")

    with col3:
        st.subheader("🟢 Platform (Consumer)")
        st.markdown("""
        **Contributes to the clean room:**
        - Impression/event logs (REDS, OpenRTB, or LLD)
        - Advertiser CRM and identity spine
        - Hashed identity fields for matching

        **Never leaves the platform's side:**
        - Advertiser campaign details
        - Bidding strategies and budget
        - First-party CRM attributes
        - Proprietary audience segments
        """)
        st.info("Platform sees: matched crosswalk + aggregate purchase outcomes. Never raw Affinity data.")

    st.markdown("---")
    st.subheader("Privacy Guarantees")
    guarantees = pd.DataFrame({
        'Guarantee': [
            'PII is hashed (SHA-512) before matching',
            'Crosswalk lands only on the consumer side',
            'ML output is aggregate rules, not individual scores',
            'Raw transactions never leave the provider account',
            'Matching runs inside the clean room under governance',
            'Both accounts require Enterprise or Business Critical edition'
        ],
        'Status': ['Enforced', 'Enforced', 'Enforced', 'Enforced', 'Enforced', 'Verified']
    })
    st.dataframe(guarantees, use_container_width=True)

# ── Step 3: Identity Resolution ──────────────────────────────────────────────
with steps[2]:
    st.header("Identity Resolution — Match Waterfall")
    st.caption("Each individual is matched by the highest-confidence method available. Select a platform to see its waterfall.")

    platform = st.selectbox("Select platform", ["TTD", "PUBMATIC", "KARGO"])

    match_data = session.sql(f"""SELECT * FROM AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY
        WHERE PLATFORM='{platform}' ORDER BY WATERFALL_STEP""").to_pandas()

    if len(match_data) > 0:
        total_rate = match_data['PCT_OF_TOTAL_AFS'].sum()
        total_matched = match_data['MATCHED_COUNT'].sum()
        ind_matched = match_data[match_data['MATCH_LEVEL']=='INDIVIDUAL']['MATCHED_COUNT'].sum()
        hh_matched = match_data[match_data['MATCH_LEVEL']=='HOUSEHOLD']['MATCHED_COUNT'].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Match Rate", f"{total_rate:.1f}%")
        c2.metric("Total Matched", f"{int(total_matched):,}")
        c3.metric("Individual", f"{int(ind_matched):,}")
        c4.metric("Household", f"{int(hh_matched):,}")

        waterfall = alt.Chart(match_data).mark_bar().encode(
            x=alt.X('MATCH_CODE:N', sort=alt.EncodingSortField(field='WATERFALL_STEP'), title='Method (in waterfall order)'),
            y=alt.Y('MATCHED_COUNT:Q', title='Matched Records'),
            color=alt.Color('MATCH_LEVEL:N', scale=alt.Scale(
                domain=['INDIVIDUAL','HOUSEHOLD'], range=['#3498db','#e67e22'])),
            tooltip=['MATCH_CODE', 'MATCH_LEVEL', 'MATCHED_COUNT', 'PCT_OF_MATCHED', 'PCT_OF_TOTAL_AFS']
        ).properties(height=400, title=f'{platform} Match Waterfall')
        st.altair_chart(waterfall, use_container_width=True)
        st.caption("Blue = individual-level match (strongest). Orange = household-level (broader reach). Methods run left-to-right; each person matched only once.")

        st.markdown("**No PII crosses the boundary.** All fields are hashed to SHA-512 before matching. The output is a crosswalk of synthetic IDs.")

    st.markdown("---")
    st.subheader("Cross-Platform Match Rate Comparison")
    all_match = session.sql("""SELECT PLATFORM, SUM(MATCHED_COUNT) AS MATCHED,
        ROUND(SUM(PCT_OF_TOTAL_AFS),1) AS RATE
        FROM AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY GROUP BY PLATFORM ORDER BY RATE DESC""").to_pandas()
    bar = alt.Chart(all_match).mark_bar().encode(
        x=alt.X('PLATFORM:N', sort='-y'),
        y=alt.Y('RATE:Q', title='Match Rate %'),
        color=alt.Color('PLATFORM:N', scale=alt.Scale(
            domain=['TTD','PUBMATIC','KARGO'], range=['#3498db','#9b59b6','#e67e22']), legend=None)
    ).properties(height=250)
    st.altair_chart(bar, use_container_width=True)
    st.caption("Match rate varies by platform identity richness. TTD has 12 methods; PubMatic/Kargo have fewer signals but still unlock purchase data they never had.")

# ── Step 4: Affinity Enrichment ──────────────────────────────────────────────
with steps[3]:
    st.header("Affinity Enrichment — Before vs After")
    st.caption("What changes when Affinity purchase data joins platform impression data.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Before: Platform Alone")
        st.markdown("""
        - Impression features: device, geo, site, content, time
        - Conversion: pixel-fired only (partial view)
        - **No purchase outcomes**
        - **No spend prediction**
        - Bidding: optimize toward proxy metrics (CTR, viewability)
        """)
        st.metric("Purchase visibility", "0%", delta="Pixel sees a fraction of actual sales")

    with col2:
        st.subheader("After: Platform + Affinity in DCR")
        st.markdown("""
        - Everything from before PLUS:
        - **Observed purchase outcomes** per matched individual x brand
        - **Propensity score** — will this person buy? (12-month, quarterly)
        - **Predicted spend** — how much? (30-day, weekly)
        - Bidding: optimize toward **actual purchases**
        """)
        pred_count = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.AFS_PROVIDER.PREDICTION_FEED_V").to_pandas()
        st.metric("Prediction coverage", f"{int(pred_count['C'][0]):,} individual x brand predictions")

    st.markdown("---")
    st.subheader("The Conversion Gap — What the Pixel Missed")
    st.caption("Each bar is a brand where Affinity sees verified card swipes the platform pixel never captured.")
    conv = session.sql("""SELECT BRAND_NAME, COUNT(*) AS PURCHASES,
        ROUND(SUM(PURCHASE_AMOUNT),2) AS TOTAL_VALUE
        FROM AFFINITY_DEMO.TTD_CONSUMER.DEMO_OUTPUT_CONVERSION_ENRICHMENT
        WHERE BRAND_NAME IS NOT NULL GROUP BY BRAND_NAME ORDER BY TOTAL_VALUE DESC LIMIT 12""").to_pandas()
    if len(conv) > 0:
        bar = alt.Chart(conv).mark_bar().encode(
            x=alt.X('TOTAL_VALUE:Q', title='Purchase Value ($)'),
            y=alt.Y('BRAND_NAME:N', sort='-x', title='Brand'),
            color=alt.value('#27ae60')
        ).properties(height=350, title='Purchases Affinity sees that the platform pixel does not')
        st.altair_chart(bar, use_container_width=True)

# ── Step 5: ML Training ──────────────────────────────────────────────────────
with steps[4]:
    st.header("ML Training — Snowflake ML on Enriched Data")
    st.caption("Supervised learning on enriched data. All training happens inside the clean room boundary — no data leaves.")

    st.subheader("Models Trained")
    registry = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_REGISTRY").to_pandas()
    for _, row in registry.iterrows():
        with st.expander(f"**{row['MODEL_NAME']}** — {row['MODEL_TYPE']}", expanded=True):
            c1, c2 = st.columns(2)
            c1.markdown(f"**{row['DESCRIPTION']}**")
            c2.markdown(f"Training: {row['TRAINING_DATA']} | Features: {row['FEATURES']}")
            st.success(row['KEY_METRIC'])

    st.subheader("Model Performance — Decile Lift")
    st.caption("Audience split into 10 equal groups by ML score. Higher decile = higher predicted purchase probability.")
    deciles = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_VALIDATION_PURCHASE_DECILES ORDER BY DECILE").to_pandas()
    lift = alt.Chart(deciles).mark_bar().encode(
        x=alt.X('DECILE:O', title='Decile (1=highest scored)'),
        y=alt.Y('PURCHASE_RATE_PCT:Q', title='Purchase Rate %'),
        color=alt.condition(alt.datum.DECILE <= 3, alt.value('#2ecc71'), alt.value('#bdc3c7')),
        tooltip=['DECILE', 'PURCHASE_RATE_PCT', 'CUMUL_CAPTURE_PCT', 'DECILE_LIFT']
    ).properties(height=300)
    st.altair_chart(lift, use_container_width=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Top Decile Lift", f"{deciles.iloc[0]['DECILE_LIFT']}x")
    c2.metric("Top 30% Capture", f"{deciles.iloc[2]['CUMUL_CAPTURE_PCT']}% of purchases")
    c3.metric("Top vs Bottom", f"{round(deciles.iloc[0]['PURCHASE_RATE_PCT']/max(deciles.iloc[9]['PURCHASE_RATE_PCT'],0.01),1)}x separation")
    st.caption("Green bars = top deciles where spend should concentrate. Gray bars = lower-priority segments.")

    st.subheader("Feature Importance — What Drives Purchases")
    st.caption("Which input features have the most influence on the model's purchase predictions.")
    fi = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_VALIDATION_FEATURE_IMPORTANCE WHERE MODEL='PURCHASE_CLASSIFIER' ORDER BY RANK").to_pandas()
    fi_chart = alt.Chart(fi).mark_bar().encode(
        x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
        y=alt.Y('FEATURE:N', sort='-x', title=''),
        color=alt.value('#3498db')
    ).properties(height=350)
    st.altair_chart(fi_chart, use_container_width=True)

# ── Step 6: Actionable Output ────────────────────────────────────────────────
with steps[5]:
    st.header("Actionable Output — What Drops Into the Bidder")
    st.caption("ML models produce rules and multipliers in the platform's native format. No identity needed at bid time.")

    st.subheader("Bidding Rules")
    rules = session.sql("SELECT * FROM AFFINITY_DEMO.ML.BIDDING_RULES ORDER BY RAW_LIFT DESC").to_pandas()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BOOST", len(rules[rules['RULE_ACTION']=='BOOST']), delta="Spend more")
    c2.metric("NEUTRAL", len(rules[rules['RULE_ACTION']=='NEUTRAL']), delta="Hold steady")
    c3.metric("SUPPRESS", len(rules[rules['RULE_ACTION']=='SUPPRESS']), delta="Spend less", delta_color="inverse")
    c4.metric("Total Rules", len(rules))
    st.caption("BOOST + NEUTRAL + SUPPRESS = Total. Each rule is an interpretable predicate like 'Site=espn.com AND Device=CTV'.")

    top_boost = rules[rules['RULE_ACTION']=='BOOST'].head(5)
    top_suppress = rules[rules['RULE_ACTION']=='SUPPRESS'].tail(5)
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("**Top BOOST rules** (spend more)")
        st.dataframe(top_boost[['PREDICATE','RAW_LIFT','BID_MULTIPLIER']], use_container_width=True)
    with b2:
        st.markdown("**Top SUPPRESS rules** (spend less)")
        st.dataframe(top_suppress[['PREDICATE','RAW_LIFT','BID_MULTIPLIER']], use_container_width=True)

    st.markdown("---")
    st.subheader("4-Quadrant Bid Strategy")
    st.caption("Each matched individual x brand is classified by predicted spend vs prior spend into a strategic action quadrant.")
    quads = session.sql("SELECT * FROM AFFINITY_DEMO.AI.QUADRANT_SUMMARY_V ORDER BY AVG_MULTIPLIER DESC").to_pandas()
    colors_map = {'NET_NEW_PROSPECTS': '🟢', 'CONQUESTING': '🔵', 'HIGH_LTV_VIPS': '🟡', 'WASTE_SUPPRESSION': '🔴'}
    cols = st.columns(4)
    for i, (_, row) in enumerate(quads.iterrows()):
        with cols[i % 4]:
            st.metric(
                f"{colors_map.get(row['QUADRANT'],'')} {row['QUADRANT'].replace('_',' ').title()}",
                f"{row['AVG_MULTIPLIER']}x",
                f"{int(row['AUDIENCE_SIZE']):,}"
            )

    st.markdown("---")
    st.subheader("Three Delivery Shapes")
    st.caption("Same intelligence, three integration levels — from drop-in segments to full ROAS-proportional bidding.")
    d1, d2, d3 = st.columns(3)
    d1.metric("Audience + Multiplier", "Tiered segments", delta="Works today, no bidder change")
    per_id = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ML.DELIVERY_PER_ID_INSTRUCTION").to_pandas()
    d2.metric("Per-ID Instruction", f"{int(per_id['C'][0]):,} IDs", delta="Refreshed weekly")
    vbb = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ML.DELIVERY_VALUE_BASED_BIDDING").to_pandas()
    d3.metric("Value-Based Bidding", f"{int(vbb['C'][0]):,} IDs", delta="ROAS-proportional")

    st.markdown("---")
    st.markdown("""### The differentiator
    > **Rules, not audiences.** Interpretable bidding predicates that need no identity
    > at bid time, survive privacy scrutiny, and drop into existing bidders.
    > Competitors sell scored audiences. This sells the strategy.""")
