import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import altair as alt

session = get_active_session()

st.set_page_config(page_title="Kargo Attribution", layout="wide", page_icon="📺")
st.title("📺 Kargo Engagement-to-Purchase Attribution + CTV Dashboard")
st.caption("Affinity Solutions x Kargo — Closing the Loop from Engagement to Purchase with Snowflake ML")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Attribution Funnel", "CTV Scoreboard", "Creative Formats",
    "ML Engagement Rules", "ML Models + Features", "Identity Coverage"
])

with tab1:
    st.header("Engagement -> Purchase Attribution")
    st.caption("Placements ranked by total purchase value from matched Affinity card swipes. Color = creative format used.")
    placements = session.sql("""SELECT * FROM AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_PLACEMENT_PURCHASE_SCORES
        ORDER BY TOTAL_PURCHASE_VALUE DESC""").to_pandas()

    c1, c2, c3 = st.columns(3)
    c1.metric("Placements Scored", len(placements))
    c2.metric("Total Purchase Value", f"${placements['TOTAL_PURCHASE_VALUE'].sum():,.0f}")
    c3.metric("Avg Purchase Value", f"${placements['AVG_PURCHASE_VALUE'].mean():,.2f}")

    bar = alt.Chart(placements.head(15)).mark_bar().encode(
        x=alt.X('TOTAL_PURCHASE_VALUE:Q', title='Total Purchase Value ($)'),
        y=alt.Y('PLACEMENT_NAME:N', sort='-x', title='Placement'),
        color=alt.Color('CREATIVE_FORMAT:N', title='Format'),
        tooltip=['PLACEMENT_NAME','CREATIVE_FORMAT','TOTAL_EVENTS','TOTAL_PURCHASE_VALUE']
    ).properties(height=450, title='Top Placements by Purchase Attribution')
    st.altair_chart(bar, use_container_width=True)
    st.caption("Longer bar = more purchase value attributed. Color shows which creative format drove it.")

with tab2:
    st.header("CTV Scoreboard")
    st.caption("CTV platforms and apps ranked by purchase conversion -- the evidence to justify premium CTV CPMs.")
    ctv = session.sql("""SELECT * FROM AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_CTV_ATTRIBUTION
        WHERE DEVICE_PLATFORM IS NOT NULL ORDER BY TOTAL_PURCHASE_VALUE DESC""").to_pandas()

    if len(ctv) > 0:
        c1, c2 = st.columns(2)
        c1.metric("CTV Platforms", ctv['DEVICE_PLATFORM'].nunique())
        c2.metric("CTV Total Purchase Value", f"${ctv['TOTAL_PURCHASE_VALUE'].sum():,.0f}")

        bar = alt.Chart(ctv).mark_bar().encode(
            x=alt.X('TOTAL_PURCHASE_VALUE:Q', title='Purchase Value ($)'),
            y=alt.Y('DEVICE_PLATFORM:N', sort='-x', title='CTV Platform'),
            color=alt.value('#9b59b6'),
            tooltip=['DEVICE_PLATFORM','EVENTS','VIDEO_COMPLETIONS','TOTAL_PURCHASE_VALUE']
        ).properties(height=300, title='CTV Platforms by Purchase Attribution')
        st.altair_chart(bar, use_container_width=True)
        st.caption("Longer bar = more purchase value from that CTV platform's viewers.")

        st.subheader("CTV Apps")
        st.caption("Individual app-level breakdown. Some apps drive purchases, others don't.")
        apps = session.sql("""SELECT * FROM AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_CTV_ATTRIBUTION
            WHERE APP_NAME IS NOT NULL ORDER BY TOTAL_PURCHASE_VALUE DESC""").to_pandas()
        if len(apps) > 0:
            st.dataframe(apps, use_container_width=True)
    else:
        st.info("No CTV attribution data available.")

with tab3:
    st.header("Creative Format Comparison")
    st.caption("Kargo's proprietary formats ranked by purchase lift. Green = above baseline. Red = below. Dashed line = 1.0x baseline.")
    rules = session.sql("SELECT * FROM AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_ENGAGEMENT_QUALITY_RULES ORDER BY LIFT DESC").to_pandas()

    bar = alt.Chart(rules).mark_bar().encode(
        x=alt.X('LIFT:Q', title='Purchase Lift vs Baseline'),
        y=alt.Y('PREDICATE:N', sort='-x', title='Creative Format'),
        color=alt.condition(alt.datum.LIFT > 1, alt.value('#2ecc71'), alt.value('#e74c3c'))
    ).properties(height=300, title='Creative Format Purchase Lift')
    ref_line = alt.Chart(pd.DataFrame({'x': [1.0]})).mark_rule(color='gray', strokeDash=[4,4]).encode(x='x:Q')
    st.altair_chart((bar + ref_line), use_container_width=True)
    st.caption("Formats above the dashed line outperform baseline. Lead with these in advertiser pitches.")
    st.dataframe(rules, use_container_width=True)

# ── NEW TAB: ML Engagement Rules ────────────────────────────────────────────
with tab4:
    st.header("ML Engagement Rules -- Purchase-Backed")
    st.caption("191 rules generated from Snowflake ML. BOOST = this engagement converts. SUPPRESS = it doesn't. Filter to explore.")

    ml_rules = session.sql("SELECT * FROM AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_ML_ENGAGEMENT_RULES ORDER BY RAW_LIFT DESC").to_pandas()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BOOST", len(ml_rules[ml_rules['RULE_ACTION']=='BOOST']), delta="High-value")
    col2.metric("NEUTRAL", len(ml_rules[ml_rules['RULE_ACTION']=='NEUTRAL']), delta="Hold steady")
    col3.metric("SUPPRESS", len(ml_rules[ml_rules['RULE_ACTION']=='SUPPRESS']), delta="Low-value", delta_color="inverse")
    col4.metric("Total Rules", len(ml_rules))
    st.caption("BOOST + NEUTRAL + SUPPRESS = Total. Each rule is a predicate like 'Format=Runway AND Device=Connected TV'.")

    c1, c2 = st.columns(2)
    action_filter = c1.selectbox("Action", ["All", "BOOST", "NEUTRAL", "SUPPRESS"])
    dim_filter = c2.selectbox("Dimension", ["All"] + sorted(ml_rules['DIM'].unique().tolist()))
    filtered = ml_rules.copy()
    if action_filter != "All":
        filtered = filtered[filtered['RULE_ACTION'] == action_filter]
    if dim_filter != "All":
        filtered = filtered[filtered['DIM'] == dim_filter]

    st.dataframe(filtered[['RULE_ID','PREDICATE','DIM','RAW_LIFT','BID_MULTIPLIER','SUPPORT','RULE_ACTION','CI_LOWER','CI_UPPER']], use_container_width=True, height=400)

    chart = alt.Chart(ml_rules).mark_bar().encode(
        x=alt.X('RAW_LIFT:Q', bin=alt.Bin(maxbins=30), title='Lift over Baseline'),
        y=alt.Y('count()', title='Rules'),
        color=alt.Color('RULE_ACTION:N', scale=alt.Scale(
            domain=['BOOST','NEUTRAL','SUPPRESS'], range=['#2ecc71','#95a5a6','#e74c3c']))
    ).properties(height=300, title='Lift Distribution -- Engagement Rules')
    st.altair_chart(chart, use_container_width=True)
    st.caption("Green = BOOST (high engagement value). Red = SUPPRESS (low value). Gray = NEUTRAL. Wider spread = more actionable rules.")

# ── NEW TAB: ML Models + Features ───────────────────────────────────────────
with tab5:
    st.header("Snowflake ML Models -- Kargo")
    st.caption("Two models trained on 2.5M Kargo LLD events using Snowflake ML. Affinity purchase outcomes as labels, LLD fields as features.")

    registry = session.sql("""SELECT * FROM AFFINITY_DEMO.ML.MODEL_REGISTRY 
        WHERE MODEL_NAME LIKE 'KARGO%' ORDER BY CREATED_AT""").to_pandas()
    for _, row in registry.iterrows():
        with st.expander(f"**{row['MODEL_NAME']}** -- {row['MODEL_TYPE']}", expanded=True):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Description:** {row['DESCRIPTION']}")
            c1.markdown(f"**Target:** {row['TARGET_TYPE']}")
            c2.markdown(f"**Training data:** {row['TRAINING_DATA']}")
            c2.markdown(f"**Features:** {row['FEATURES']}")
            st.success(f"**Key metric:** {row['KEY_METRIC']}")

    st.subheader("Model Performance -- Decile Lift")
    st.caption("Population split into 10 equal groups by ML score. Green bars = top deciles where engagement drives the most purchases.")
    deciles = session.sql("SELECT * FROM AFFINITY_DEMO.ML.KARGO_VALIDATION_DECILES ORDER BY DECILE").to_pandas()
    lift_chart = alt.Chart(deciles).mark_bar().encode(
        x=alt.X('DECILE:O', title='Decile (1=highest scored)'),
        y=alt.Y('PURCHASE_RATE_PCT:Q', title='Purchase Rate %'),
        color=alt.condition(alt.datum.DECILE <= 3, alt.value('#2ecc71'), alt.value('#bdc3c7')),
        tooltip=['DECILE', 'PURCHASE_RATE_PCT', 'CUMUL_CAPTURE_PCT', 'DECILE_LIFT']
    ).properties(height=350, title='Purchase rate by ML score decile -- Kargo Engagement Classifier')
    st.altair_chart(lift_chart, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Top Decile Lift", f"{deciles.iloc[0]['DECILE_LIFT']}x")
    c2.metric("Top 30% Capture", f"{deciles.iloc[2]['CUMUL_CAPTURE_PCT']}%")
    c3.metric("Top vs Bottom", f"{round(deciles.iloc[0]['PURCHASE_RATE_PCT']/max(deciles.iloc[9]['PURCHASE_RATE_PCT'],0.01),1)}x separation")
    st.caption("Green bars are the engagement signals worth investing in. The model separates high-value from low-value engagement.")

    st.markdown("---")
    st.subheader("Feature Importance")
    st.caption("Side-by-side: what drives engagement conversion vs spend amount. Longer bar = more influence on the model.")

    fi = session.sql("SELECT * FROM AFFINITY_DEMO.ML.KARGO_FEATURE_IMPORTANCE ORDER BY MODEL, RANK").to_pandas()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Engagement Classifier** -- *which engagements convert*")
        pf = fi[fi['MODEL']=='KARGO_ENGAGEMENT_CLASSIFIER'].copy()
        bar1 = alt.Chart(pf).mark_bar().encode(
            x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
            y=alt.Y('FEATURE:N', sort='-x', title=''),
            color=alt.value('#e67e22'),
            tooltip=['FEATURE', 'IMPORTANCE_SCORE', 'RANK']
        ).properties(height=350)
        st.altair_chart(bar1, use_container_width=True)

    with c2:
        st.markdown("**Spend Classifier** -- *how much they spend*")
        sf = fi[fi['MODEL']=='KARGO_SPEND_CLASSIFIER'].copy()
        bar2 = alt.Chart(sf).mark_bar().encode(
            x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
            y=alt.Y('FEATURE:N', sort='-x', title=''),
            color=alt.value('#9b59b6'),
            tooltip=['FEATURE', 'IMPORTANCE_SCORE', 'RANK']
        ).properties(height=300)
        st.altair_chart(bar2, use_container_width=True)

    st.markdown("---")
    st.subheader("Holdout Validation")
    st.caption("Training group vs holdout (20% random sample held back). Confirms the model generalizes.")
    holdout = session.sql("SELECT * FROM AFFINITY_DEMO.ML.KARGO_HOLDOUT_RESULTS").to_pandas()
    h1, h2 = st.columns(2)
    for _, row in holdout.iterrows():
        col = h1 if row['SET_NAME'] == 'Training' else h2
        with col:
            label = "With Affinity Rules" if row['SET_NAME'] == 'Training' else "Holdout (No Rules)"
            st.subheader(label)
            st.metric("Purchase Rate", f"{row['PURCHASE_RATE_PCT']}%")
            st.metric("Impressions", f"{int(row['IMPRESSIONS']):,}")
            st.metric("Purchases", f"{int(row['PURCHASES']):,}")

with tab6:
    st.header("Identity Coverage -- Ad Server Reality")
    st.caption("Kargo relies on RampID and IP -- just 2 methods. CTV leans on IP for household-level matches.")
    match = session.sql("SELECT * FROM AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY WHERE PLATFORM='KARGO' ORDER BY WATERFALL_STEP").to_pandas()
    total = match['PCT_OF_TOTAL_AFS'].sum()
    st.metric("Kargo Match Rate", f"{total:.1f}%", delta=f"{int(match['MATCHED_COUNT'].sum()):,} individuals matched")
    st.caption("22.5% match rate = 22,000+ purchase-validated individuals in a space where advertisers had zero purchase data before.")

    bar = alt.Chart(match).mark_bar().encode(
        x=alt.X('MATCH_CODE:N', sort=alt.EncodingSortField(field='WATERFALL_STEP')),
        y=alt.Y('MATCHED_COUNT:Q', title='Matched'),
        color=alt.Color('MATCH_LEVEL:N', scale=alt.Scale(domain=['INDIVIDUAL','HOUSEHOLD'], range=['#3498db','#e67e22']))
    ).properties(height=300)
    st.altair_chart(bar, use_container_width=True)
    st.caption("Blue = individual-level match. Orange = household-level. CTV environments rely heavily on IP (household).")
    st.dataframe(match, use_container_width=True)
