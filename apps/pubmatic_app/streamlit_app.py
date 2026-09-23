import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import altair as alt

session = get_active_session()

st.set_page_config(page_title="PubMatic Inventory Yield", layout="wide", page_icon="📈")
st.title("📈 PubMatic Inventory Yield Scorer + ML-Powered Floor Optimizer")
st.caption("Affinity Solutions × PubMatic — Purchase-Driven Inventory Scoring with Snowflake ML")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Yield Heatmap", "Floor Optimizer", "Premium Packages",
    "SSP Bidding Rules", "ML Models + Features", "Identity Coverage"
])

with tab1:
    st.header("Inventory Yield by Supply Dimensions")
    st.caption("Each cell shows purchase conversion rate for a publisher x format combination. Green = high yield, Red = low yield.")
    yields = session.sql("""SELECT SITE_DOMAIN, AD_FORMAT, DEVICE_TYPE_LABEL,
        SUM(IMPRESSIONS) AS IMPRESSIONS, SUM(PURCHASES) AS PURCHASES,
        ROUND(AVG(PURCHASE_RATE)*100,3) AS PURCHASE_RATE_PCT,
        ROUND(AVG(YIELD_MULTIPLIER),2) AS AVG_YIELD
        FROM AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_INVENTORY_YIELD_SCORES
        GROUP BY 1,2,3 ORDER BY AVG_YIELD DESC""").to_pandas()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Inventory Segments", len(yields))
    c2.metric("Highest Yield", f"{yields['AVG_YIELD'].max():.2f}x")
    c3.metric("Lowest Yield", f"{yields['AVG_YIELD'].min():.2f}x")

    heatmap = alt.Chart(yields.head(50)).mark_rect().encode(
        x=alt.X('AD_FORMAT:N', title='Ad Format'),
        y=alt.Y('SITE_DOMAIN:N', sort='-color', title='Publisher'),
        color=alt.Color('AVG_YIELD:Q', scale=alt.Scale(scheme='redyellowgreen'), title='Yield Multiplier'),
        tooltip=['SITE_DOMAIN','AD_FORMAT','AVG_YIELD','IMPRESSIONS','PURCHASES']
    ).properties(height=500, title='Purchase Yield: Publisher x Format')
    st.altair_chart(heatmap, use_container_width=True)

with tab2:
    st.header("Floor Price Recommendations")
    st.caption("ML-backed floor adjustments. Each row is an inventory segment with a recommended floor price and projected revenue lift.")
    floors = session.sql("SELECT * FROM AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_FLOOR_RECOMMENDATIONS ORDER BY EXPECTED_REVENUE_LIFT_PCT DESC LIMIT 50").to_pandas()
    st.dataframe(floors, use_container_width=True, height=400)

    if len(floors) > 0:
        bar = alt.Chart(floors.head(20)).mark_bar().encode(
            x=alt.X('EXPECTED_REVENUE_LIFT_PCT:Q', title='Expected Revenue Lift %'),
            y=alt.Y('DIMENSIONS:N', sort='-x', title='Inventory Segment'),
            color=alt.value('#8e44ad')
        ).properties(height=500, title='Top 20 Floor Optimization Opportunities')
        st.altair_chart(bar, use_container_width=True)
        st.caption("Longer bar = bigger revenue opportunity. These are the segments where adjusting floors has the most impact.")

with tab3:
    st.header("Premium Inventory Packages")
    st.caption("Pre-built bundles backed by purchase conversion evidence. Sell these to advertisers with proof of real card-swipe outcomes.")
    packages = session.sql("SELECT * FROM AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_PURCHASE_INVENTORY_PACKAGES ORDER BY PURCHASE_RATE DESC").to_pandas()
    st.dataframe(packages, use_container_width=True)

# ── NEW TAB: SSP Bidding Rules ──────────────────────────────────────────────
with tab4:
    st.header("SSP Bidding Rules — ML-Powered")
    st.caption("Purchase-backed rules: BOOST = set higher floors (inventory converts). SUPPRESS = accept lower bids (doesn't convert).")

    rules = session.sql("SELECT * FROM AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_SSP_BIDDING_RULES ORDER BY RAW_LIFT DESC").to_pandas()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rules", len(rules))
    col2.metric("BOOST", len(rules[rules['RULE_ACTION']=='BOOST']), delta="Higher floors")
    col3.metric("SUPPRESS", len(rules[rules['RULE_ACTION']=='SUPPRESS']), delta="Lower floors", delta_color="inverse")
    col4.metric("NEUTRAL", len(rules[rules['RULE_ACTION']=='NEUTRAL']))

    c1, c2 = st.columns(2)
    action_filter = c1.selectbox("Action", ["All", "BOOST", "NEUTRAL", "SUPPRESS"])
    dim_filter = c2.selectbox("Dimension", ["All"] + sorted(rules['DIM'].unique().tolist()))
    filtered = rules.copy()
    if action_filter != "All":
        filtered = filtered[filtered['RULE_ACTION'] == action_filter]
    if dim_filter != "All":
        filtered = filtered[filtered['DIM'] == dim_filter]

    st.dataframe(filtered[['RULE_ID','PREDICATE','DIM','RAW_LIFT','BID_MULTIPLIER','SUPPORT','RULE_ACTION','CI_LOWER','CI_UPPER']], use_container_width=True, height=400)

    chart = alt.Chart(rules).mark_bar().encode(
        x=alt.X('RAW_LIFT:Q', bin=alt.Bin(maxbins=30), title='Lift over Baseline'),
        y=alt.Y('count()', title='Rules'),
        color=alt.Color('RULE_ACTION:N', scale=alt.Scale(
            domain=['BOOST','NEUTRAL','SUPPRESS'], range=['#2ecc71','#95a5a6','#e74c3c']))
    ).properties(height=300, title='Lift Distribution — SSP Inventory Rules')
    st.altair_chart(chart, use_container_width=True)
    st.caption("Green = BOOST (premium floor). Red = SUPPRESS (discount). Gray = NEUTRAL. Wider spread = more actionable rules.")

    st.markdown("---")
    st.subheader("Publisher Multipliers — Floor Tier Allocation")
    st.caption("Every publisher x format x device x geo segment classified into PREMIUM, STANDARD, or DISCOUNT floor tiers.")
    pub_mult = session.sql("""SELECT FLOOR_TIER, COUNT(*) AS SEGMENTS, 
        ROUND(AVG(YIELD_MULTIPLIER),2) AS AVG_YIELD,
        SUM(IMPRESSIONS) AS TOTAL_IMPRESSIONS, SUM(PURCHASES) AS TOTAL_PURCHASES
        FROM AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_PUBLISHER_MULTIPLIERS
        GROUP BY FLOOR_TIER ORDER BY AVG_YIELD DESC""").to_pandas()

    cols = st.columns(3)
    tier_colors = {'PREMIUM': '🟢', 'STANDARD': '🟡', 'DISCOUNT': '🔴'}
    for i, (_, row) in enumerate(pub_mult.iterrows()):
        with cols[i % 3]:
            st.metric(
                f"{tier_colors.get(row['FLOOR_TIER'],'')} {row['FLOOR_TIER']}",
                f"{int(row['SEGMENTS'])} segments",
                f"Avg yield: {row['AVG_YIELD']}x"
            )

# ── NEW TAB: ML Models + Features ───────────────────────────────────────────
with tab5:
    st.header("Snowflake ML Models — PubMatic")
    st.caption("Two models trained on 2.5M matched impressions using Snowflake ML. Affinity purchase outcomes as labels, OpenRTB fields as features.")

    registry = session.sql("""SELECT * FROM AFFINITY_DEMO.ML.MODEL_REGISTRY 
        WHERE MODEL_NAME LIKE 'PUBMATIC%' ORDER BY CREATED_AT""").to_pandas()
    for _, row in registry.iterrows():
        with st.expander(f"**{row['MODEL_NAME']}** — {row['MODEL_TYPE']}", expanded=True):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Description:** {row['DESCRIPTION']}")
            c1.markdown(f"**Target:** {row['TARGET_TYPE']}")
            c2.markdown(f"**Training data:** {row['TRAINING_DATA']}")
            c2.markdown(f"**Features:** {row['FEATURES']}")
            st.success(f"**Key metric:** {row['KEY_METRIC']}")

    st.subheader("Model Performance — Decile Lift")
    st.caption("Population split into 10 equal groups by ML score. Green bars = top deciles where inventory should be premium-priced.")
    deciles = session.sql("SELECT * FROM AFFINITY_DEMO.ML.PUBMATIC_VALIDATION_DECILES ORDER BY DECILE").to_pandas()
    lift_chart = alt.Chart(deciles).mark_bar().encode(
        x=alt.X('DECILE:O', title='Decile (1=highest scored)'),
        y=alt.Y('PURCHASE_RATE_PCT:Q', title='Purchase Rate %'),
        color=alt.condition(alt.datum.DECILE <= 3, alt.value('#2ecc71'), alt.value('#bdc3c7')),
        tooltip=['DECILE', 'PURCHASE_RATE_PCT', 'CUMUL_CAPTURE_PCT', 'DECILE_LIFT']
    ).properties(height=350, title='Purchase rate by ML score decile — PubMatic Yield Classifier')
    st.altair_chart(lift_chart, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Top Decile Lift", f"{deciles.iloc[0]['DECILE_LIFT']}x")
    c2.metric("Top 30% Capture", f"{deciles.iloc[2]['CUMUL_CAPTURE_PCT']}%")
    c3.metric("Top vs Bottom", f"{round(deciles.iloc[0]['PURCHASE_RATE_PCT']/max(deciles.iloc[9]['PURCHASE_RATE_PCT'],0.01),1)}x separation")

    st.markdown("---")
    st.subheader("Feature Importance")
    st.caption("Side-by-side: what drives yield vs spend. Longer bar = more influence. BIDFLOOR is #1 — the SSP's own pricing signal matters most.")

    fi = session.sql("SELECT * FROM AFFINITY_DEMO.ML.PUBMATIC_FEATURE_IMPORTANCE ORDER BY MODEL, RANK").to_pandas()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Yield Classifier** — *which inventory converts*")
        pf = fi[fi['MODEL']=='PUBMATIC_YIELD_CLASSIFIER'].copy()
        bar1 = alt.Chart(pf).mark_bar().encode(
            x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
            y=alt.Y('FEATURE:N', sort='-x', title=''),
            color=alt.value('#8e44ad'),
            tooltip=['FEATURE', 'IMPORTANCE_SCORE', 'RANK']
        ).properties(height=350)
        st.altair_chart(bar1, use_container_width=True)

    with c2:
        st.markdown("**Spend Classifier** — *how much they spend*")
        sf = fi[fi['MODEL']=='PUBMATIC_SPEND_CLASSIFIER'].copy()
        bar2 = alt.Chart(sf).mark_bar().encode(
            x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
            y=alt.Y('FEATURE:N', sort='-x', title=''),
            color=alt.value('#e67e22'),
            tooltip=['FEATURE', 'IMPORTANCE_SCORE', 'RANK']
        ).properties(height=300)
        st.altair_chart(bar2, use_container_width=True)

    st.markdown("---")
    st.subheader("Spend Efficiency — Enriched vs Holdout")
    st.caption("Training group (with Affinity rules) vs holdout (without). Compare purchase rate, cost per purchase, and ROAS.")
    holdout = session.sql("SELECT * FROM AFFINITY_DEMO.ML.PUBMATIC_HOLDOUT_RESULTS").to_pandas()
    h1, h2 = st.columns(2)
    for _, row in holdout.iterrows():
        col = h1 if row['SET_NAME'] == 'Training' else h2
        with col:
            label = "With Affinity Rules" if row['SET_NAME'] == 'Training' else "Holdout (No Rules)"
            st.subheader(label)
            st.metric("Purchase Rate", f"{row['PURCHASE_RATE_PCT']}%")
            st.metric("Cost per Purchase", f"${row['COST_PER_PURCHASE']:.2f}")
            st.metric("ROAS", f"{row['ROAS']:.1f}x")

with tab6:
    st.header("Identity Coverage — SSP Reality")
    match = session.sql("SELECT * FROM AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY WHERE PLATFORM='PUBMATIC' ORDER BY WATERFALL_STEP").to_pandas()
    total = match['PCT_OF_TOTAL_AFS'].sum()
    st.metric("PubMatic Match Rate", f"{total:.1f}%", delta=f"{int(match['MATCHED_COUNT'].sum()):,} individuals matched")
    st.caption("Match relies on MAID, UID2/RampID, and IP. Every matched individual now has Affinity purchase data attached.")

    bar = alt.Chart(match).mark_bar().encode(
        x=alt.X('MATCH_CODE:N', sort=alt.EncodingSortField(field='WATERFALL_STEP')),
        y=alt.Y('MATCHED_COUNT:Q', title='Matched'),
        color=alt.Color('MATCH_LEVEL:N', scale=alt.Scale(domain=['INDIVIDUAL','HOUSEHOLD'], range=['#3498db','#e67e22']))
    ).properties(height=300)
    st.altair_chart(bar, use_container_width=True)
    st.dataframe(match, use_container_width=True)
