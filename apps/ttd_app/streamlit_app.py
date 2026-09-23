import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import altair as alt

session = get_active_session()

st.set_page_config(page_title="TTD Bid Optimization", layout="wide", page_icon="📊")
st.title("📊 TTD Bid Rule Explorer + Spend Efficiency")
st.caption("Affinity Solutions × The Trade Desk — Purchase-Outcome Bid Optimization")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Rule Explorer", "Quadrant Strategy", "Spend Efficiency",
    "ML Models + Features", "Prediction Accuracy", "Match Waterfall"
])

with tab1:
    st.header("Bidding Rules")
    st.caption("Each rule is an interpretable predicate (e.g. Site=espn.com AND Device=CTV). Filter by action or dimension to explore.")
    rules = session.sql("SELECT * FROM AFFINITY_DEMO.ML.BIDDING_RULES ORDER BY RAW_LIFT DESC").to_pandas()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rules", len(rules))
    col2.metric("BOOST", len(rules[rules['RULE_ACTION']=='BOOST']), delta="1.1x–2.0x")
    col3.metric("SUPPRESS", len(rules[rules['RULE_ACTION']=='SUPPRESS']), delta="0.4x–0.9x", delta_color="inverse")
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
    ).properties(height=300, title='Lift Distribution')
    st.altair_chart(chart, use_container_width=True)
    st.caption("Green = BOOST (bid more). Red = SUPPRESS (bid less). Gray = NEUTRAL. Wider spread = more actionable rules.")

with tab2:
    st.header("4-Quadrant Bidding Strategy")
    st.caption("Each matched individual x brand classified by predicted spend vs prior spend into a strategic action quadrant.")

    quads = session.sql("SELECT * FROM AFFINITY_DEMO.AI.QUADRANT_SUMMARY_V ORDER BY AVG_MULTIPLIER DESC").to_pandas()
    colors = {'NET_NEW_PROSPECTS': '🟢', 'CONQUESTING': '🔵', 'HIGH_LTV_VIPS': '🟡', 'WASTE_SUPPRESSION': '🔴'}
    cols = st.columns(4)
    for i, (_, row) in enumerate(quads.iterrows()):
        with cols[i % 4]:
            st.metric(
                f"{colors.get(row['QUADRANT'],'')} {row['QUADRANT'].replace('_',' ').title()}",
                f"{row['AVG_MULTIPLIER']}x multiplier",
                f"{int(row['AUDIENCE_SIZE']):,} individuals"
            )
            st.caption(f"**{row['STRATEGIC_OBJECTIVE']}**")
            st.caption(f"Predicted: ${row['AVG_PREDICTED_SPEND']:.0f} | Prior: ${row['AVG_PRIOR_SPEND']:.0f}")

    quad_chart = alt.Chart(quads).mark_bar().encode(
        x=alt.X('QUADRANT:N', sort='-y', title=''),
        y=alt.Y('AUDIENCE_SIZE:Q', title='Audience Size'),
        color=alt.Color('QUADRANT:N', legend=None, scale=alt.Scale(
            domain=['NET_NEW_PROSPECTS','CONQUESTING','HIGH_LTV_VIPS','WASTE_SUPPRESSION'],
            range=['#2ecc71','#3498db','#f39c12','#e74c3c']))
    ).properties(height=350, title='Audience Distribution by Quadrant')
    st.altair_chart(quad_chart, use_container_width=True)
    st.caption("Taller bar = larger audience in that quadrant. Green = highest-value acquisition targets. Red = suppress.")

    st.subheader("Delivery Shapes")
    st.caption("Same intelligence, three integration levels — from drop-in segments to full ROAS-proportional bidding.")
    d1, d2, d3 = st.columns(3)
    d1.metric("Audience + Multiplier", "Tiered segments", delta="Works today, no bidder change")
    per_id = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ML.DELIVERY_PER_ID_INSTRUCTION").to_pandas()
    d2.metric("Per-ID Bid Instruction", f"{int(per_id['C'][0]):,} IDs", delta="Refreshed weekly")
    vbb = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ML.DELIVERY_VALUE_BASED_BIDDING").to_pandas()
    d3.metric("Value-Based Bidding", f"{int(vbb['C'][0]):,} IDs", delta="ROAS-proportional")

with tab3:
    st.header("Spend Efficiency — Enriched vs Baseline")
    st.caption("Side-by-side proof: the group with Affinity rules vs a random holdout that didn't receive them.")
    holdout = session.sql("SELECT * FROM AFFINITY_DEMO.ML.VALIDATION_HOLDOUT_RESULTS").to_pandas()
    c1, c2 = st.columns(2)
    for _, row in holdout.iterrows():
        col = c1 if row['SET_NAME'] == 'Training' else c2
        with col:
            label = "With Affinity Rules" if row['SET_NAME'] == 'Training' else "Holdout (No Rules)"
            st.subheader(label)
            st.metric("Purchase Rate", f"{row['PURCHASE_RATE_PCT']}%")
            st.metric("Cost per Purchase", f"${row['COST_PER_PURCHASE']:.4f}")
            st.metric("ROAS", f"{row['ROAS']:.1f}x")

    st.subheader("Purchase Rate by Dimension")
    st.caption("Drill into which dimension values drive the highest purchase conversion. Switch dimensions to explore.")
    dim_choice = st.selectbox("Dimension", ["InventoryChannel", "MATCH_CODE", "GEO_DMA", "SupplySource"])
    q = f"""SELECT {dim_choice} AS DIM_VAL,
        ROUND(AVG(PURCHASED::FLOAT)*100,3) AS RATE,
        COUNT(*) AS IMPRESSIONS
        FROM AFFINITY_DEMO.ML.TRAINING_SET_TTD WHERE IS_HOLDOUT=0
        GROUP BY 1 ORDER BY RATE DESC"""
    dim_data = session.sql(q).to_pandas()
    bar = alt.Chart(dim_data).mark_bar().encode(
        x=alt.X('DIM_VAL:N', sort='-y', title=dim_choice),
        y=alt.Y('RATE:Q', title='Purchase Rate %'),
        tooltip=['DIM_VAL', 'RATE', 'IMPRESSIONS'],
        color=alt.value('#3498db')
    ).properties(height=350)
    st.altair_chart(bar, use_container_width=True)

with tab4:
    st.header("Snowflake ML Models")
    st.caption("Custom models trained on matched population using Snowflake ML. Affinity outcomes as labels, platform exposure data as features.")

    registry = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_REGISTRY").to_pandas()
    for _, row in registry.iterrows():
        with st.expander(f"**{row['MODEL_NAME']}** — {row['MODEL_TYPE']}", expanded=True):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Description:** {row['DESCRIPTION']}")
            c1.markdown(f"**Target:** {row['TARGET_TYPE']}")
            c2.markdown(f"**Training data:** {row['TRAINING_DATA']}")
            c2.markdown(f"**Features:** {row['FEATURES']}")
            st.success(f"**Key metric:** {row['KEY_METRIC']}")

    st.subheader("Model Performance — Decile Lift")
    st.caption("Population split into 10 equal groups by ML score. Green bars = top deciles where spend should concentrate.")
    deciles = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_VALIDATION_PURCHASE_DECILES ORDER BY DECILE").to_pandas()
    lift_chart = alt.Chart(deciles).mark_bar().encode(
        x=alt.X('DECILE:O', title='Decile (1=highest scored)'),
        y=alt.Y('PURCHASE_RATE_PCT:Q', title='Purchase Rate %'),
        color=alt.condition(alt.datum.DECILE <= 3, alt.value('#2ecc71'), alt.value('#bdc3c7')),
        tooltip=['DECILE', 'PURCHASE_RATE_PCT', 'CUMUL_CAPTURE_PCT', 'DECILE_LIFT']
    ).properties(height=350, title='Purchase rate by model score decile')
    st.altair_chart(lift_chart, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Top Decile Lift", f"{deciles.iloc[0]['DECILE_LIFT']}x")
    c2.metric("Top 30% Capture", f"{deciles.iloc[2]['CUMUL_CAPTURE_PCT']}%")
    c3.metric("Top vs Bottom", f"{round(deciles.iloc[0]['PURCHASE_RATE_PCT']/max(deciles.iloc[9]['PURCHASE_RATE_PCT'],0.01),1)}x separation")

    st.subheader("Precision-Recall Trade-off")
    st.caption("Higher threshold = fewer but more confident predictions. Each point is a different decision boundary.")
    pr = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_VALIDATION_PURCHASE_CONFUSION ORDER BY THRESHOLD").to_pandas()
    pr_chart = alt.Chart(pr).mark_point(size=100).encode(
        x=alt.X('RECALL_PCT:Q', title='Recall %'),
        y=alt.Y('PRECISION_PCT:Q', title='Precision %'),
        tooltip=['THRESHOLD', 'PRECISION_PCT', 'RECALL_PCT', 'TRUE_POS', 'FALSE_POS']
    ).properties(height=300, title='Higher threshold = more precise, lower coverage')
    st.altair_chart(pr_chart + pr_chart.mark_line(), use_container_width=True)

    st.markdown("---")
    st.subheader("Feature Importance")
    st.caption("Side-by-side: what drives purchase conversion vs spend amount. Longer bar = more influence on the model.")

    fi = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_VALIDATION_FEATURE_IMPORTANCE ORDER BY MODEL, RANK").to_pandas()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Purchase Classifier** — *where the ad ran*")
        pf = fi[fi['MODEL']=='PURCHASE_CLASSIFIER'].copy()
        bar1 = alt.Chart(pf).mark_bar().encode(
            x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
            y=alt.Y('FEATURE:N', sort='-x', title=''),
            color=alt.value('#3498db'),
            tooltip=['FEATURE', 'IMPORTANCE_SCORE', 'RANK']
        ).properties(height=350)
        st.altair_chart(bar1, use_container_width=True)

    with c2:
        st.markdown("**Spend Tier Classifier** — *who the person is*")
        sf = fi[fi['MODEL']=='SPEND_TIER_CLASSIFIER'].copy()
        bar2 = alt.Chart(sf).mark_bar().encode(
            x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
            y=alt.Y('FEATURE:N', sort='-x', title=''),
            color=alt.value('#e67e22'),
            tooltip=['FEATURE', 'IMPORTANCE_SCORE', 'RANK']
        ).properties(height=250)
        st.altair_chart(bar2, use_container_width=True)

with tab5:
    st.header("Prediction Accuracy")
    st.subheader("Propensity Tier Performance")
    st.caption("Higher Affinity propensity tiers should have higher actual hit rates. This table validates that the predictions hold up.")
    acc = session.sql("""SELECT COALESCE(PROPENSITY_TIER, 'General Population') AS TIER,
        COUNT(*) AS TOTAL, SUM(DID_PURCHASE) AS PURCHASED,
        ROUND(AVG(DID_PURCHASE::FLOAT)*100,2) AS HIT_RATE_PCT,
        ROUND(AVG(PREDICTED_SPEND_30D),2) AS AVG_PREDICTED,
        ROUND(AVG(CASE WHEN DID_PURCHASE=1 THEN ACTUAL_SPEND END),2) AS AVG_ACTUAL
        FROM AFFINITY_DEMO.ML.ACCURACY_PROOF GROUP BY PROPENSITY_TIER
        ORDER BY HIT_RATE_PCT DESC NULLS LAST""").to_pandas()
    st.dataframe(acc, use_container_width=True)

    st.subheader("Conversion Gap — What TTD's Pixel Missed")
    st.caption("Each bar is a brand where Affinity sees verified card swipes the TTD pixel never captured.")
    conv = session.sql("""SELECT BRAND_NAME, COUNT(*) AS PURCHASES,
        ROUND(SUM(PURCHASE_AMOUNT),2) AS TOTAL_VALUE
        FROM AFFINITY_DEMO.TTD_CONSUMER.DEMO_OUTPUT_CONVERSION_ENRICHMENT
        WHERE BRAND_NAME IS NOT NULL GROUP BY BRAND_NAME ORDER BY TOTAL_VALUE DESC LIMIT 15""").to_pandas()
    bar2 = alt.Chart(conv).mark_bar().encode(
        x=alt.X('TOTAL_VALUE:Q', title='Purchase Value ($)'),
        y=alt.Y('BRAND_NAME:N', sort='-x', title='Brand'),
        color=alt.value('#27ae60')
    ).properties(height=400, title='Top Brands by Affinity-Attributed Purchase Value')
    st.altair_chart(bar2, use_container_width=True)

with tab6:
    st.header("Match Waterfall — TTD")
    st.caption("12 match methods run in waterfall order. Blue = individual-level (strongest). Orange = household-level (broader reach).")
    match_data = session.sql("""SELECT * FROM AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY
        WHERE PLATFORM='TTD' ORDER BY WATERFALL_STEP""").to_pandas()

    total_matched = match_data['MATCHED_COUNT'].sum()
    st.metric("Overall Match Rate", f"{match_data['PCT_OF_TOTAL_AFS'].sum():.1f}%",
              delta=f"{total_matched:,} matched of 100K")

    waterfall = alt.Chart(match_data).mark_bar().encode(
        x=alt.X('MATCH_CODE:N', sort=alt.EncodingSortField(field='WATERFALL_STEP'), title='Method'),
        y=alt.Y('MATCHED_COUNT:Q', title='Matched'),
        color=alt.Color('MATCH_LEVEL:N', scale=alt.Scale(
            domain=['INDIVIDUAL','HOUSEHOLD'], range=['#3498db','#e67e22'])),
        tooltip=['MATCH_CODE', 'MATCH_LEVEL', 'MATCHED_COUNT', 'PCT_OF_MATCHED']
    ).properties(height=350, title='Match Waterfall by Method')
    st.altair_chart(waterfall, use_container_width=True)
    st.dataframe(match_data[['MATCH_CODE','MATCH_LEVEL','MATCHED_COUNT','PCT_OF_MATCHED','PCT_OF_TOTAL_AFS']], use_container_width=True)
