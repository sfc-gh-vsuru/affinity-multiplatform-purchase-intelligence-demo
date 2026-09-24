import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import altair as alt

session = get_active_session()

st.set_page_config(page_title="Affinity Cross-Platform", layout="wide", page_icon="🌐")
st.title("🌐 Affinity Solutions — Cross-Platform Comparison")
st.caption("One data asset, four monetization paths: DSP + Retargeting + SSP + Ad Server")

tab1, tab2, tab3, tab4 = st.tabs(["Match Rates", "Platform Outputs", "ML Models", "The Pitch"])

with tab1:
    st.header("Match Rate Comparison Across Platforms")
    st.caption("Same Affinity purchase data, different match rates — driven by identity signals each platform carries.")

    summary = session.sql("""
        SELECT PLATFORM, SUM(MATCHED_COUNT) AS TOTAL_MATCHED,
          ROUND(SUM(PCT_OF_TOTAL_AFS),1) AS MATCH_RATE,
          SUM(CASE WHEN MATCH_LEVEL='INDIVIDUAL' THEN MATCHED_COUNT ELSE 0 END) AS INDIVIDUAL_MATCHES,
          SUM(CASE WHEN MATCH_LEVEL='HOUSEHOLD' THEN MATCHED_COUNT ELSE 0 END) AS HOUSEHOLD_MATCHES
        FROM (SELECT * FROM AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY
              UNION ALL SELECT * FROM AFFINITY_DEMO.CLEANROOM.ADROLL_MATCH_RATE_SUMMARY)
        GROUP BY PLATFORM ORDER BY MATCH_RATE DESC
    """).to_pandas()

    cols = st.columns(4)
    platform_info = {
        'ADROLL': ('Retargeting DSP', 'email SHA-256', '#e74c3c'),
        'TTD': ('DSP', '12 methods', '#3498db'),
        'PUBMATIC': ('SSP', '3 methods', '#9b59b6'),
        'KARGO': ('Ad Server', '2 methods', '#e67e22')
    }
    for i, (_, row) in enumerate(summary.iterrows()):
        info = platform_info.get(row['PLATFORM'], ('','','#999'))
        with cols[i % 4]:
            st.metric(f"{row['PLATFORM']} ({info[0]})", f"{row['MATCH_RATE']}%",
                      delta=f"{int(row['TOTAL_MATCHED']):,} matched | {info[1]}")
            st.progress(min(row['MATCH_RATE'] / 100, 1.0))

    st.subheader("Method-Level Comparison")
    st.caption("Stacked bars show which match methods contribute to each platform's total. Taller bar = more matched individuals.")
    all_methods = session.sql("""SELECT * FROM AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY
        UNION ALL SELECT * FROM AFFINITY_DEMO.CLEANROOM.ADROLL_MATCH_RATE_SUMMARY
        ORDER BY PLATFORM, WATERFALL_STEP""").to_pandas()

    stacked = alt.Chart(all_methods).mark_bar().encode(
        x=alt.X('PLATFORM:N', title='Platform', sort=['ADROLL','TTD','PUBMATIC','KARGO']),
        y=alt.Y('MATCHED_COUNT:Q', title='Matched Records', stack='zero'),
        color=alt.Color('MATCH_CODE:N', title='Match Method',
                        sort=alt.EncodingSortField(field='MATCHED_COUNT', order='descending')),
        order=alt.Order('MATCHED_COUNT:Q', sort='descending'),
        tooltip=['PLATFORM','MATCH_CODE','MATCH_LEVEL','MATCHED_COUNT']
    ).properties(height=400, title='Match Methods by Platform')
    st.altair_chart(stacked, use_container_width=True)

    st.dataframe(all_methods[['PLATFORM','MATCH_CODE','MATCH_LEVEL','MATCHED_COUNT','PCT_OF_TOTAL_AFS']], use_container_width=True)

with tab2:
    st.header("Same Data, Different Outputs")
    st.caption("Each platform gets tailored outputs from the same Affinity purchase outcomes — formatted for their use case.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔵 TTD (DSP)")
        st.markdown("**Bidding rules + multipliers**")
        ttd_rules = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ML.BIDDING_RULES").to_pandas()
        ttd_pred = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.TTD_CONSUMER.DEMO_OUTPUT_PREDICTION_MULTIPLIERS").to_pandas()
        st.metric("Bidding Rules", f"{int(ttd_rules['C'][0]):,}")
        st.metric("Prediction Multipliers", f"{int(ttd_pred['C'][0]):,}")
        st.caption("Drop into existing bidder. No identity at bid time.")

    with col2:
        st.subheader("🔴 AdRoll (Retargeting DSP)")
        st.markdown("**Funnel intelligence + B2B account scores**")
        ar_rules = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ADROLL_CONSUMER.ADROLL_FUNNEL_PURCHASE_RULES").to_pandas()
        ar_b2b = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ADROLL_B2B.ADROLL_ACCOUNT_SCORES").to_pandas()
        st.metric("Funnel Purchase Rules", f"{int(ar_rules['C'][0]):,}")
        st.metric("B2B Account Scores", f"{int(ar_b2b['C'][0]):,}")
        st.caption("Conversion enrichment + B2B firmographic scoring.")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🟣 PubMatic (SSP)")
        st.markdown("**Inventory yield scores + SSP rules**")
        pm_yields = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_INVENTORY_YIELD_SCORES").to_pandas()
        pm_rules = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_SSP_BIDDING_RULES").to_pandas()
        st.metric("Yield Scores", f"{int(pm_yields['C'][0]):,}")
        st.metric("SSP Bidding Rules", f"{int(pm_rules['C'][0]):,}")
        st.caption("Prove which inventory drives purchases. Set ML-backed floors.")

    with col4:
        st.subheader("🟠 Kargo (Ad Server)")
        st.markdown("**Engagement-to-purchase attribution**")
        kg_rules = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_ML_ENGAGEMENT_RULES").to_pandas()
        kg_ctv = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_CTV_ATTRIBUTION").to_pandas()
        st.metric("ML Engagement Rules", f"{int(kg_rules['C'][0]):,}")
        st.metric("CTV Attributions", f"{int(kg_ctv['C'][0]):,}")
        st.caption("Close the engagement-to-purchase loop. Justify CTV CPMs.")

    st.markdown("---")
    st.subheader("ML Models by Platform")
    st.caption("Total Snowflake ML models trained across all four platforms.")
    model_counts = session.sql("""SELECT 
        CASE WHEN MODEL_NAME LIKE 'ADROLL%' THEN 'AdRoll'
             WHEN MODEL_NAME LIKE 'PUBMATIC%' THEN 'PubMatic'
             WHEN MODEL_NAME LIKE 'KARGO%' THEN 'Kargo'
             WHEN MODEL_NAME LIKE 'BRAND%' THEN 'Shared'
             ELSE 'TTD' END AS PLATFORM,
        COUNT(*) AS MODELS
        FROM AFFINITY_DEMO.ML.MODEL_REGISTRY GROUP BY 1 ORDER BY MODELS DESC""").to_pandas()
    mcols = st.columns(len(model_counts))
    for i, (_, row) in enumerate(model_counts.iterrows()):
        mcols[i].metric(row['PLATFORM'], f"{int(row['MODELS'])} models")

with tab3:
    st.header("Snowflake ML Model Registry")
    st.caption("12 models across 4 platforms. Affinity delivers Default predictions; each platform trains Custom models using Snowflake ML.")

    platform_filter = st.selectbox("Filter by platform", ["All", "TTD", "AdRoll", "PubMatic", "Kargo", "Shared"])
    filter_clause = ""
    if platform_filter == "TTD":
        filter_clause = "WHERE MODEL_NAME NOT LIKE 'ADROLL%' AND MODEL_NAME NOT LIKE 'PUBMATIC%' AND MODEL_NAME NOT LIKE 'KARGO%' AND MODEL_NAME NOT LIKE 'BRAND%'"
    elif platform_filter == "AdRoll":
        filter_clause = "WHERE MODEL_NAME LIKE 'ADROLL%'"
    elif platform_filter == "PubMatic":
        filter_clause = "WHERE MODEL_NAME LIKE 'PUBMATIC%'"
    elif platform_filter == "Kargo":
        filter_clause = "WHERE MODEL_NAME LIKE 'KARGO%'"
    elif platform_filter == "Shared":
        filter_clause = "WHERE MODEL_NAME LIKE 'BRAND%'"

    registry = session.sql(f"SELECT * FROM AFFINITY_DEMO.ML.MODEL_REGISTRY {filter_clause} ORDER BY CREATED_AT").to_pandas()
    for _, row in registry.iterrows():
        with st.expander(f"{row['MODEL_NAME']} ({row['MODEL_TYPE']})", expanded=(platform_filter != "All")):
            st.markdown(f"**{row['DESCRIPTION']}**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Target", row['TARGET_TYPE'])
            c2.metric("Training Data", row['TRAINING_DATA'])
            c3.metric("Features", row['FEATURES'])
            st.info(f"Key metric: {row['KEY_METRIC']}")

    st.markdown("---")
    st.subheader("Top Decile Lift Comparison")
    st.caption("Top decile performance across platform classifiers. Higher lift = better model separation.")
    lift_data = pd.DataFrame({
        'Platform': ['AdRoll', 'TTD', 'PubMatic', 'Kargo'],
        'Top Decile Lift': [3.22, 2.15, 2.5, 3.45],
        'Top 30% Capture': [61.4, 51.5, 56.5, 66.4]
    })
    lift_bar = alt.Chart(lift_data).mark_bar().encode(
        x=alt.X('Platform:N', sort='-y', title=''),
        y=alt.Y('Top Decile Lift:Q', title='Top Decile Lift (x)'),
        color=alt.Color('Platform:N', scale=alt.Scale(
            domain=['AdRoll','TTD','PubMatic','Kargo'], range=['#e74c3c','#3498db','#9b59b6','#e67e22']), legend=None),
        tooltip=['Platform', 'Top Decile Lift', 'Top 30% Capture']
    ).properties(height=250, title='Top Decile Lift by Platform Classifier')
    st.altair_chart(lift_bar, use_container_width=True)

with tab4:
    st.header("The Pitch: One Data Asset, Four Paths")
    st.markdown("""
    ### What Affinity brings
    - **300M+ cards** linked to **160M consumers**
    - **5,300+ brands**, online and offline, across all 50 states
    - **Two pre-computed models**: propensity (12-month) + predicted spend (30-day)

    ### Why it matters for each platform type

    | | DSP (TTD) | Retargeting (AdRoll) | SSP (PubMatic) | Ad Server (Kargo) |
    |---|---|---|---|---|
    | **Problem** | Can't see what ads caused purchases | Pixel captures intent, not outcome | Can't prove which inventory works | Can't attribute purchases to engagement |
    | **Affinity adds** | Purchase outcomes as labels + features | Card-swipe truth behind conversions | Purchase-backed inventory scoring | Engagement-to-purchase closed loop |
    | **Output** | Bidding rules + multipliers | Funnel rules + B2B account scores | Yield scores + floor recommendations | Attribution reports + CTV proof |
    | **ML models** | 2 classifiers + forecast | 4 classifiers + forecast | 2 classifiers | 2 classifiers |
    | **Unique angle** | 4-quadrant bidding strategy | B2B firmographic scoring | Floor price optimization | CTV purchase attribution |
    | **Match method** | 12 methods (name, email, MAID, IP) | Email SHA-256 (deterministic) | 3 methods (email, MAID, IP) | 2 methods (RampID, IP) |
    | **Match rate** | 44.8% | 80.6% | 26.2% | 22.5% |

    ### The differentiator
    > **Rules, not audiences.** Interpretable bidding predicates that need no identity
    > at bid time, survive privacy scrutiny, and drop into existing systems.
    > Competitors sell scored audiences. We sell the strategy.
    """)
