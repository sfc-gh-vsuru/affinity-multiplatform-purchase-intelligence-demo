import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import altair as alt

session = get_active_session()

st.set_page_config(page_title="Affinity x AdRoll", layout="wide", page_icon="🎯")
st.title("🎯 Affinity Solutions x AdRoll — Purchase Intelligence Dashboard")
st.caption("Turning conversion data into verified purchase outcomes with Snowflake ML")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "The Opportunity", "Conversion Enrichment", "Funnel Intelligence",
    "B2B Account Scoring", "CTV + Video Attribution", "ML Models + Features"
])

# ── Tab 1: The Opportunity ──────────────────────────────────────────────────
with tab1:
    st.header("The Opportunity: Pixel vs Card Swipe")
    st.caption("AdRoll sees conversion events. Affinity sees verified card swipes. Together they reveal the full picture.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("What AdRoll Has")
        st.markdown("""
        - **10M tracked events** across 13 event types
        - **2.2M attributed conversions** with multi-touch attribution
        - **Full funnel:** pageView, productSearch, addToCart, purchase
        - **B2B signals:** demoRequest, contactSales, signupTrial
        - **CTV campaigns** with video completion tracking
        """)
        st.error("**Missing:** Did the person actually swipe a card? Pixel captures intent, not outcome.")
        gcr_count = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_GCR").to_pandas()
        event_count = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_S2S_EVENTS").to_pandas()
        c1, c2 = st.columns(2)
        c1.metric("Tracked Events", f"{int(event_count['C'][0]):,}")
        c2.metric("Attributed Conversions", f"{int(gcr_count['C'][0]):,}")

    with col2:
        st.subheader("What Affinity Has")
        st.markdown("""
        - **300M+ cards** linked to **160M consumers**
        - **5,300+ brands**, online and offline
        - **Daily refresh** of verified purchases
        - **Propensity + predicted spend** models
        """)
        st.error("**Missing:** Which ads drove these purchases. No exposure data.")
        tx_count = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.AFS_PROVIDER.TX_SRC_V").to_pandas()
        ind_count = session.sql("SELECT COUNT(DISTINCT INDID) AS c FROM AFFINITY_DEMO.AFS_PROVIDER.CC_EXT_V").to_pandas()
        c1, c2 = st.columns(2)
        c1.metric("Transactions", f"{int(tx_count['C'][0]):,}")
        c2.metric("Individuals", f"{int(ind_count['C'][0]):,}")

    st.markdown("---")
    st.subheader("Channel Revenue: Pixel vs Card Swipe")
    st.caption("Each bar pair shows what AdRoll's pixel attributed vs what Affinity verified. The gap is invisible revenue.")
    ch = session.sql("SELECT * FROM AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_CHANNEL_ATTRIBUTION ORDER BY CARD_SWIPE_REVENUE DESC").to_pandas()
    ch_melted = pd.melt(ch, id_vars=['CHANNEL'], value_vars=['PIXEL_REVENUE','CARD_SWIPE_REVENUE'], var_name='SOURCE', value_name='REVENUE')
    ch_melted['SOURCE'] = ch_melted['SOURCE'].map({'PIXEL_REVENUE': 'Pixel', 'CARD_SWIPE_REVENUE': 'Card Swipe'})
    bar = alt.Chart(ch_melted).mark_bar().encode(
        x=alt.X('CHANNEL:N', title='Channel'),
        y=alt.Y('REVENUE:Q', title='Revenue ($)'),
        color=alt.Color('SOURCE:N', scale=alt.Scale(domain=['Pixel','Card Swipe'], range=['#95a5a6','#2ecc71'])),
        column=alt.Column('SOURCE:N', title=''),
        tooltip=['CHANNEL','SOURCE','REVENUE']
    ).properties(height=300, width=200)
    st.altair_chart(bar, use_container_width=False)

# ── Tab 2: Conversion Enrichment ────────────────────────────────────────────
with tab2:
    st.header("Conversion Enrichment -- Pixel vs Verified")
    st.caption("AdRoll attributes revenue via pixel. Affinity verifies it with card swipes. The delta reveals over/under-counting.")

    ch = session.sql("SELECT * FROM AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_CHANNEL_ATTRIBUTION ORDER BY CARD_SWIPE_REVENUE DESC").to_pandas()
    st.dataframe(ch, use_container_width=True)

    st.subheader("True Purchase Rate by Channel")
    st.caption("What percentage of AdRoll's conversions represent verified card-swipe purchases?")
    rate_bar = alt.Chart(ch).mark_bar().encode(
        x=alt.X('CHANNEL:N', sort='-y', title='Channel'),
        y=alt.Y('TRUE_PURCHASE_RATE_PCT:Q', title='Verified Purchase Rate %'),
        color=alt.value('#3498db'),
        tooltip=['CHANNEL', 'TRUE_PURCHASE_RATE_PCT', 'VERIFIED_PURCHASES', 'CONVERSIONS']
    ).properties(height=300)
    st.altair_chart(rate_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Match Coverage")
    match = session.sql("SELECT * FROM AFFINITY_DEMO.CLEANROOM.ADROLL_MATCH_RATE_SUMMARY").to_pandas()
    if len(match) > 0:
        st.metric("Match Rate (Affinity Individuals)", f"{match['PCT_OF_TOTAL_AFS'].sum():.1f}%",
                  delta=f"{int(match['MATCHED_COUNT'].sum()):,} matched via email SHA-256")
        st.caption("Email-based matching is deterministic and high-confidence. Every match is an individual-level link.")

# ── Tab 3: Funnel Intelligence ──────────────────────────────────────────────
with tab3:
    st.header("Funnel Intelligence -- ML-Powered Rules")
    st.caption("ML-derived rules from 10M funnel events. BOOST = this behavior predicts purchases. SUPPRESS = it doesn't.")

    rules = session.sql("SELECT * FROM AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_FUNNEL_PURCHASE_RULES ORDER BY RAW_LIFT DESC").to_pandas()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BOOST", len(rules[rules['RULE_ACTION']=='BOOST']), delta="Invest more")
    col2.metric("NEUTRAL", len(rules[rules['RULE_ACTION']=='NEUTRAL']), delta="Hold steady")
    col3.metric("SUPPRESS", len(rules[rules['RULE_ACTION']=='SUPPRESS']), delta="Reduce spend", delta_color="inverse")
    col4.metric("Total Rules", len(rules))
    st.caption("BOOST + NEUTRAL + SUPPRESS = Total. Each rule is a predicate like 'Channel=web AND Device=desktop'.")

    c1, c2 = st.columns(2)
    action_filter = c1.selectbox("Action", ["All", "BOOST", "NEUTRAL", "SUPPRESS"])
    dim_filter = c2.selectbox("Dimension", ["All"] + sorted(rules['DIM'].unique().tolist()))
    filtered = rules.copy()
    if action_filter != "All":
        filtered = filtered[filtered['RULE_ACTION'] == action_filter]
    if dim_filter != "All":
        filtered = filtered[filtered['DIM'] == dim_filter]
    st.dataframe(filtered[['RULE_ID','PREDICATE','DIM','RAW_LIFT','BID_MULTIPLIER','SUPPORT','RULE_ACTION']], use_container_width=True, height=400)

    chart = alt.Chart(rules).mark_bar().encode(
        x=alt.X('RAW_LIFT:Q', bin=alt.Bin(maxbins=25), title='Lift over Baseline'),
        y=alt.Y('count()', title='Rules'),
        color=alt.Color('RULE_ACTION:N', scale=alt.Scale(
            domain=['BOOST','NEUTRAL','SUPPRESS'], range=['#2ecc71','#95a5a6','#e74c3c']))
    ).properties(height=300, title='Lift Distribution')
    st.altair_chart(chart, use_container_width=True)
    st.caption("Green = BOOST (invest more). Red = SUPPRESS (reduce spend). Wider spread = more actionable intelligence.")

# ── Tab 4: B2B Account Scoring ──────────────────────────────────────────────
with tab4:
    st.header("B2B Account Scoring -- Firmographics + Purchase Intelligence")
    st.caption("5,000 companies from AdRoll Site Traffic Revealer scored by actual purchase propensity using Snowflake ML.")

    scores = session.sql("SELECT * FROM AFFINITY_DEMO.ADROLL_B2B.ADROLL_ACCOUNT_SCORES ORDER BY PURCHASE_SCORE DESC").to_pandas()

    c1, c2, c3 = st.columns(3)
    c1.metric("HOT Accounts", len(scores[scores['SCORE_TIER']=='HOT']), delta="High purchase propensity")
    c2.metric("WARM Accounts", len(scores[scores['SCORE_TIER']=='WARM']), delta="Moderate signals")
    c3.metric("COLD Accounts", len(scores[scores['SCORE_TIER']=='COLD']), delta="Low signals", delta_color="inverse")

    st.subheader("Industry x Purchase Score")
    st.caption("Average purchase score by industry. Higher = more purchase-likely visitors from that industry.")
    ind_scores = scores.groupby('COMPANY_INDUSTRY').agg(
        AVG_SCORE=('PURCHASE_SCORE', 'mean'), ACCOUNTS=('DOMAIN', 'count')
    ).reset_index().sort_values('AVG_SCORE', ascending=False).head(15)
    heatbar = alt.Chart(ind_scores).mark_bar().encode(
        x=alt.X('AVG_SCORE:Q', title='Avg Purchase Score'),
        y=alt.Y('COMPANY_INDUSTRY:N', sort='-x', title=''),
        color=alt.Color('AVG_SCORE:Q', scale=alt.Scale(scheme='redyellowgreen'), legend=None),
        tooltip=['COMPANY_INDUSTRY', 'AVG_SCORE', 'ACCOUNTS']
    ).properties(height=400, title='Purchase Score by Industry')
    st.altair_chart(heatbar, use_container_width=True)

    st.subheader("Top 20 Accounts by Predicted Value")
    st.caption("Ranked by ML-predicted account purchase value. These are the accounts to prioritize in outreach.")
    top20 = scores.head(20)[['COMPANY_NAME','COMPANY_INDUSTRY','COMPANY_SIZE','JOURNEY_STAGE','PURCHASE_SCORE','PREDICTED_ACCOUNT_VALUE','SCORE_TIER']]
    st.dataframe(top20, use_container_width=True)

    st.markdown("---")
    st.subheader("Journey Stage vs Purchase Score")
    st.caption("Companies further in the journey (MQL, Opportunity) have higher purchase scores. The ML validates the ABM funnel.")
    journey = scores.groupby('JOURNEY_STAGE').agg(AVG_SCORE=('PURCHASE_SCORE','mean'), ACCOUNTS=('DOMAIN','count')).reset_index()
    stage_order = ['Unaware','Aware','Engaged','MQL','Opportunity']
    journey['STAGE_ORDER'] = journey['JOURNEY_STAGE'].map({s:i for i,s in enumerate(stage_order)})
    journey = journey.sort_values('STAGE_ORDER')
    jbar = alt.Chart(journey).mark_bar().encode(
        x=alt.X('JOURNEY_STAGE:N', sort=stage_order, title='Journey Stage'),
        y=alt.Y('AVG_SCORE:Q', title='Avg Purchase Score'),
        color=alt.Color('AVG_SCORE:Q', scale=alt.Scale(scheme='redyellowgreen'), legend=None),
        tooltip=['JOURNEY_STAGE','AVG_SCORE','ACCOUNTS']
    ).properties(height=300)
    st.altair_chart(jbar, use_container_width=True)

# ── Tab 5: CTV + Video Attribution ──────────────────────────────────────────
with tab5:
    st.header("CTV + Video Attribution")
    st.caption("CTV campaigns validated by Affinity card-swipe data. Proof that video views drive real purchases.")
    st.info("Note: Impression-level CTV data is not publicly available from AdRoll. Attribution is based on matched conversion events from CTV campaigns.")

    ctv = session.sql("SELECT * FROM AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_CTV_ATTRIBUTION ORDER BY TOTAL_PURCHASE_VALUE DESC").to_pandas()

    c1, c2, c3 = st.columns(3)
    c1.metric("CTV Campaigns", len(ctv))
    c2.metric("Total Purchase Value", f"${ctv['TOTAL_PURCHASE_VALUE'].sum():,.0f}")
    c3.metric("Avg CTV ROAS", f"{ctv['CTV_ROAS'].mean():.2f}x")

    st.subheader("CTV Campaigns by Purchase Value")
    st.caption("Longer bar = more verified purchase value from that CTV campaign's viewers.")
    ctv_bar = alt.Chart(ctv.head(15)).mark_bar().encode(
        x=alt.X('TOTAL_PURCHASE_VALUE:Q', title='Purchase Value ($)'),
        y=alt.Y('CAMPAIGN_NAME:N', sort='-x', title='Campaign'),
        color=alt.value('#9b59b6'),
        tooltip=['CAMPAIGN_NAME','VIDEO_IMPRESSIONS','VIDEO_COMPLETIONS','TOTAL_PURCHASE_VALUE','CTV_ROAS']
    ).properties(height=400, title='Top CTV Campaigns by Verified Purchase Value')
    st.altair_chart(ctv_bar, use_container_width=True)

    st.subheader("Video Completion to Purchase Rate")
    st.caption("What percentage of viewers who completed the video actually purchased? Higher = more effective creative.")
    comp_bar = alt.Chart(ctv.head(15)).mark_bar().encode(
        x=alt.X('COMPLETION_TO_PURCHASE_RATE:Q', title='Completion-to-Purchase Rate %'),
        y=alt.Y('CAMPAIGN_NAME:N', sort='-x', title=''),
        color=alt.value('#e67e22'),
        tooltip=['CAMPAIGN_NAME','COMPLETION_TO_PURCHASE_RATE','VIDEO_COMPLETIONS','MATCHED_PURCHASERS']
    ).properties(height=400)
    st.altair_chart(comp_bar, use_container_width=True)

# ── Tab 6: ML Models + Features ─────────────────────────────────────────────
with tab6:
    st.header("Snowflake ML Models -- AdRoll")
    st.caption("5 models trained using Snowflake ML. Affinity purchase outcomes as labels, AdRoll engagement data as features.")

    registry = session.sql("""SELECT * FROM AFFINITY_DEMO.ML.MODEL_REGISTRY 
        WHERE MODEL_NAME LIKE 'ADROLL%' ORDER BY CREATED_AT""").to_pandas()
    for _, row in registry.iterrows():
        with st.expander(f"**{row['MODEL_NAME']}** -- {row['MODEL_TYPE']}", expanded=True):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Description:** {row['DESCRIPTION']}")
            c1.markdown(f"**Target:** {row['TARGET_TYPE']}")
            c2.markdown(f"**Training data:** {row['TRAINING_DATA']}")
            c2.markdown(f"**Features:** {row['FEATURES']}")
            st.success(f"**Key metric:** {row['KEY_METRIC']}")

    st.subheader("Conversion Classifier -- Decile Lift")
    st.caption("Population split into 10 equal groups by ML score. Green bars = top deciles with highest purchase rate.")
    deciles = session.sql("SELECT * FROM AFFINITY_DEMO.ML.ADROLL_CONVERSION_DECILES ORDER BY DECILE").to_pandas()
    lift_chart = alt.Chart(deciles).mark_bar().encode(
        x=alt.X('DECILE:O', title='Decile (1=highest scored)'),
        y=alt.Y('PURCHASE_RATE_PCT:Q', title='Purchase Rate %'),
        color=alt.condition(alt.datum.DECILE <= 3, alt.value('#2ecc71'), alt.value('#bdc3c7')),
        tooltip=['DECILE', 'PURCHASE_RATE_PCT', 'CUMUL_CAPTURE_PCT', 'DECILE_LIFT']
    ).properties(height=350)
    st.altair_chart(lift_chart, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Top Decile Lift", f"{deciles.iloc[0]['DECILE_LIFT']}x")
    c2.metric("Top 30% Capture", f"{deciles.iloc[2]['CUMUL_CAPTURE_PCT']}%")
    c3.metric("Top vs Bottom", f"{round(deciles.iloc[0]['PURCHASE_RATE_PCT']/max(deciles.iloc[9]['PURCHASE_RATE_PCT'],0.01),1)}x separation")

    st.markdown("---")
    st.subheader("Feature Importance -- Conversion vs Funnel")
    st.caption("What drives purchase prediction in each model. Longer bar = more influence.")
    fi = session.sql("SELECT * FROM AFFINITY_DEMO.ML.ADROLL_FEATURE_IMPORTANCE WHERE MODEL IN ('ADROLL_CONVERSION_CLASSIFIER','ADROLL_FUNNEL_PREDICTOR') ORDER BY MODEL, RANK").to_pandas()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Conversion Classifier** -- *which conversions are real*")
        pf = fi[fi['MODEL']=='ADROLL_CONVERSION_CLASSIFIER'].copy()
        bar1 = alt.Chart(pf).mark_bar().encode(
            x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
            y=alt.Y('FEATURE:N', sort='-x', title=''),
            color=alt.value('#3498db'),
            tooltip=['FEATURE', 'IMPORTANCE_SCORE', 'RANK']
        ).properties(height=380)
        st.altair_chart(bar1, use_container_width=True)
    with c2:
        st.markdown("**Funnel Predictor** -- *who will purchase*")
        sf = fi[fi['MODEL']=='ADROLL_FUNNEL_PREDICTOR'].copy()
        bar2 = alt.Chart(sf).mark_bar().encode(
            x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
            y=alt.Y('FEATURE:N', sort='-x', title=''),
            color=alt.value('#e67e22'),
            tooltip=['FEATURE', 'IMPORTANCE_SCORE', 'RANK']
        ).properties(height=380)
        st.altair_chart(bar2, use_container_width=True)

    st.markdown("---")
    st.subheader("Holdout Validation")
    st.caption("Training set (with Affinity data) vs holdout (without). Confirms the model generalizes.")
    holdout = session.sql("SELECT * FROM AFFINITY_DEMO.ML.ADROLL_HOLDOUT_RESULTS").to_pandas()
    h1, h2 = st.columns(2)
    for _, row in holdout.iterrows():
        col = h1 if row['SET_NAME'] == 'Training' else h2
        with col:
            st.subheader("With Affinity" if row['SET_NAME'] == 'Training' else "Holdout")
            st.metric("Purchase Rate", f"{row['PURCHASE_RATE_PCT']}%")
            st.metric("Conversions", f"{int(row['CONVERSIONS']):,}")
            st.metric("Verified Purchases", f"{int(row['PURCHASES']):,}")
