-- ============================================================================
-- Affinity Solutions DCR + ML Demo — Streamlit App Deployment
-- Run AFTER 02_load_data.sql and upload_data.sh
-- Creates all 5 Streamlit in Snowflake apps from staged source files
-- ============================================================================

USE DATABASE AFFINITY_DEMO;
USE SCHEMA APPS;

-- 1. Pipeline End-to-End (the main story app)
CREATE OR REPLACE STREAMLIT PIPELINE_END_TO_END
  ROOT_LOCATION = '@AFFINITY_DEMO.APPS.STREAMLIT_STAGE/pipeline_app'
  MAIN_FILE = '/streamlit_app.py'
  QUERY_WAREHOUSE = 'AFFINITY_DEMO_WH'
  TITLE = 'Affinity DCR + ML Pipeline — End to End'
  COMMENT = 'The complete story: Problem > DCR > Identity > Enrichment > ML > Output';

-- 2. TTD Bid Explorer
CREATE OR REPLACE STREAMLIT TTD_BID_EXPLORER
  ROOT_LOCATION = '@AFFINITY_DEMO.APPS.STREAMLIT_STAGE/ttd_app'
  MAIN_FILE = '/streamlit_app.py'
  QUERY_WAREHOUSE = 'AFFINITY_DEMO_WH'
  TITLE = 'TTD Bid Rule Explorer + ML Models'
  COMMENT = 'Affinity x TTD: rules, quadrants, efficiency, ML models, accuracy, waterfall';

-- 3. PubMatic Yield Scorer
CREATE OR REPLACE STREAMLIT PUBMATIC_YIELD_SCORER
  ROOT_LOCATION = '@AFFINITY_DEMO.APPS.STREAMLIT_STAGE/pubmatic_app'
  MAIN_FILE = '/streamlit_app.py'
  QUERY_WAREHOUSE = 'AFFINITY_DEMO_WH'
  TITLE = 'PubMatic Inventory Yield Scorer + ML-Powered Floor Optimizer'
  COMMENT = 'Affinity x PubMatic: yield heatmap, floor optimization, SSP bidding rules, ML models, identity';

-- 4. Kargo Attribution Dashboard
CREATE OR REPLACE STREAMLIT KARGO_ATTRIBUTION_DASHBOARD
  ROOT_LOCATION = '@AFFINITY_DEMO.APPS.STREAMLIT_STAGE/kargo_app'
  MAIN_FILE = '/streamlit_app.py'
  QUERY_WAREHOUSE = 'AFFINITY_DEMO_WH'
  TITLE = 'Kargo Engagement-to-Purchase Attribution + CTV + ML'
  COMMENT = 'Affinity x Kargo: attribution, CTV, creative formats, ML engagement rules, ML models, identity';

-- 5. Cross-Platform Comparison
CREATE OR REPLACE STREAMLIT CROSS_PLATFORM_COMPARISON
  ROOT_LOCATION = '@AFFINITY_DEMO.APPS.STREAMLIT_STAGE/crossplatform_app'
  MAIN_FILE = '/streamlit_app.py'
  QUERY_WAREHOUSE = 'AFFINITY_DEMO_WH'
  TITLE = 'Affinity Cross-Platform + ML Models'
  COMMENT = 'One data asset, three paths: DSP+SSP+Ad Server with ML model registry';

-- Verify
SHOW STREAMLITS IN SCHEMA AFFINITY_DEMO.APPS;

SELECT 'All 5 Streamlit apps deployed successfully.' AS STATUS;
