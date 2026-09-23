import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import altair as alt

session = get_active_session()

st.set_page_config(page_title="Affinity Cross-Platform", layout="wide", page_icon="🌐")
st.title("🌐 Affinity Solutions — Cross-Platform Comparison")
st.caption("One data asset, three monetization paths: DSP + SSP + Ad Server")

tab1, tab2, tab3, tab4 = st.tabs(["Match Rates", "Platform Outputs", "ML Models", "The Pitch"])

with tab1:
    st.header("Match Rate Comparison Across Platforms")
    st.caption("Same Affinity purchase data, different match rates — driven by identity signals each platform carries.")

    summary = session.sql("""
        SELECT PLATFORM, SUM(MATCHED_COUNT) AS TOTAL_MATCHED,
          ROUND(SUM(PCT_OF_TOTAL_AFS),1) AS MATCH_RATE,
          SUM(CASE WHEN MATCH_LEVEL='INDIVIDUAL' THEN MATCHED_COUNT ELSE 0 END) AS INDIVIDUAL_MATCHES,
          SUM(CASE WHEN MATCH_LEVEL='HOUSEHOLD' THEN MATCHED_COUNT ELSE 0 END) AS HOUSEHOLD_MATCHES
        FROM AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY GROUP BY PLATFORM
        ORDER BY MATCH_RATE DESC
    """).to_pandas()

    cols = st.columns(3)
    platform_info = {
        'TTD': ('DSP', '12 methods', '#3498db'),
        'PUBMATIC': ('SSP', '3 methods', '#9b59b6'),
        'KARGO': ('Ad Server', '2 methods', '#e67e22')
    }
    for i, (_, row) in enumerate(summary.iterrows()):
        info = platform_info.get(row['PLATFORM'], ('','','#999'))
        with cols[i]:
            st.metric(f"{row['PLATFORM']} ({info[0]})", f"{row['MATCH_RATE']}%",
                      delta=f"{int(row['TOTAL_MATCHED']):,} matched | {info[1]}")
            st.progress(row['MATCH_RATE'] / 100)

    st.subheader("Method-Level Comparison")
    st.caption("Stacked bars show which match methods contribute to each platform's total. Taller bar = more matched individuals.")
    all_methods = session.sql("SELECT * FROM AFFINITY_DEMO.CLEANROOM.MATCH_RATE_SUMMARY ORDER BY PLATFORM, WATERFALL_STEP").to_pandas()

    stacked = alt.Chart(all_methods).mark_bar().encode(
        x=alt.X('PLATFORM:N', title='Platform', sort=['TTD','PUBMATIC','KARGO']),
        y=alt.Y('MATCHED_COUNT:Q', title='Matched Records', stack='zero'),
        color=alt.Color('MATCH_CODE:N', title='Match Method',
                        sort=alt.EncodingSortField(field='MATCHED_COUNT', order='descending')),
        order=alt.Order('MATCHED_COUNT:Q', sort='descending'),
        tooltip=['PLATFORM','MATCH_CODE','MATCH_LEVEL','MATCHED_COUNT']
    ).properties(height=400, title='Match Methods by Platform — All Methods Stacked')
    st.altair_chart(stacked, use_container_width=True)

    st.dataframe(all_methods[['PLATFORM','MATCH_CODE','MATCH_LEVEL','MATCHED_COUNT','PCT_OF_TOTAL_AFS']], use_container_width=True)

with tab2:
    st.header("Same Data, Different Outputs")
    st.caption("Each platform gets tailored outputs from the same Affinity purchase outcomes — formatted for their use case.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🔵 TTD (DSP)")
        st.markdown("**Bidding rules + multipliers**")
        ttd_rules = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.ML.BIDDING_RULES").to_pandas()
        ttd_pred = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.TTD_CONSUMER.DEMO_OUTPUT_PREDICTION_MULTIPLIERS").to_pandas()
        st.metric("Bidding Rules", f"{int(ttd_rules['C'][0]):,}")
        st.metric("Prediction Multipliers", f"{int(ttd_pred['C'][0]):,}")
        st.caption("Drop into existing bidder. No identity at bid time.")

    with col2:
        st.subheader("🟣 PubMatic (SSP)")
        st.markdown("**Inventory yield scores + SSP rules**")
        pm_yields = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_INVENTORY_YIELD_SCORES").to_pandas()
        pm_rules = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.PUBMATIC_CONSUMER.DEMO_OUTPUT_SSP_BIDDING_RULES").to_pandas()
        st.metric("Yield Scores", f"{int(pm_yields['C'][0]):,}")
        st.metric("SSP Bidding Rules", f"{int(pm_rules['C'][0]):,}")
        st.caption("Prove which inventory drives purchases. Set ML-backed floors.")

    with col3:
        st.subheader("🟠 Kargo (Ad Server)")
        st.markdown("**Engagement-to-purchase attribution**")
        kg_attr = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_ENGAGEMENT_PURCHASE_ATTR").to_pandas()
        kg_ctv = session.sql("SELECT COUNT(*) AS c FROM AFFINITY_DEMO.KARGO_CONSUMER.DEMO_OUTPUT_CTV_ATTRIBUTION").to_pandas()
        st.metric("Purchase Attributions", f"{int(kg_attr['C'][0]):,}")
        st.metric("CTV Attributions", f"{int(kg_ctv['C'][0]):,}")
        st.caption("Close the engagement-to-purchase loop. Justify CTV CPMs.")

with tab3:
    st.header("Snowflake ML Model Registry")
    st.caption("Affinity delivers Default predictions from day one. Platforms train Custom models using Snowflake ML on their own data.")

    registry = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_REGISTRY").to_pandas()
    for _, row in registry.iterrows():
        with st.expander(f"{row['MODEL_NAME']} ({row['MODEL_TYPE']})", expanded=True):
            st.markdown(f"**{row['DESCRIPTION']}**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Target", row['TARGET_TYPE'])
            c2.metric("Training Data", row['TRAINING_DATA'])
            c3.metric("Features", row['FEATURES'])
            st.info(f"Key metric: {row['KEY_METRIC']}")

    st.subheader("Model Performance — Decile Lift (TTD Purchase Classifier)")
    st.caption("Population split into 10 equal groups by ML score. Green bars = top deciles where spend should concentrate.")
    deciles = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_VALIDATION_PURCHASE_DECILES ORDER BY DECILE").to_pandas()
    lift_chart = alt.Chart(deciles).mark_bar().encode(
        x=alt.X('DECILE:O', title='Decile (1=highest scored)'),
        y=alt.Y('PURCHASE_RATE_PCT:Q', title='Purchase Rate %'),
        color=alt.condition(alt.datum.DECILE <= 3, alt.value('#2ecc71'), alt.value('#bdc3c7')),
        tooltip=['DECILE', 'PURCHASE_RATE_PCT', 'CUMUL_CAPTURE_PCT', 'DECILE_LIFT']
    ).properties(height=300, title='Top decile captures 21.5% of purchases with 2.15x lift')
    st.altair_chart(lift_chart, use_container_width=True)

    st.subheader("Feature Importance — What Drives Outcomes")
    st.caption("Longer bar = more influence on purchase prediction. Highlights which platform signals matter most.")
    fi = session.sql("SELECT * FROM AFFINITY_DEMO.ML.MODEL_VALIDATION_FEATURE_IMPORTANCE WHERE MODEL='PURCHASE_CLASSIFIER' ORDER BY RANK").to_pandas()
    bar = alt.Chart(fi).mark_bar().encode(
        x=alt.X('IMPORTANCE_SCORE:Q', title='Importance Score'),
        y=alt.Y('FEATURE:N', sort='-x', title=''),
        color=alt.value('#3498db')
    ).properties(height=350, title='Purchase Classifier — Feature Importance')
    st.altair_chart(bar, use_container_width=True)

with tab4:
    st.header("The Pitch: One Data Asset, Three Paths")
    st.markdown("""
    ### What Affinity brings
    - **300M+ cards** linked to **160M consumers**
    - **5,300+ brands**, online and offline, across all 50 states
    - **Two pre-computed models**: propensity (12-month) + predicted spend (30-day)

    ### Why it matters for each platform type

    | | DSP (TTD) | SSP (PubMatic) | Ad Server (Kargo) |
    |---|---|---|---|
    | **Problem** | Can't see what ads caused | Can't prove which inventory works | Can't attribute purchases to engagement |
    | **Affinity adds** | Purchase outcomes as labels + features | Purchase-backed inventory scoring | Engagement-to-purchase closed loop |
    | **Output** | Bidding rules + multipliers | Yield scores + floor recommendations | Attribution reports + CTV proof |
    | **ML models** | Purchase + Spend classifiers | Yield + Spend classifiers | Engagement quality rules |
    | **Match rate** | 44.8% (12 methods) | 26.2% (3 methods) | 22.5% (2 methods) |

    ### The differentiator
    > **Rules, not audiences.** Interpretable bidding predicates that need no identity
    > at bid time, survive privacy scrutiny, and drop into existing bidders.
    > Competitors sell scored audiences. We sell the strategy.
    """)
