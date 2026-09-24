-- ============================================================================
-- Affinity Solutions DCR + ML Demo — Environment Setup
-- Run this FIRST. Creates database, schemas, warehouses, and file formats.
-- Requires: ACCOUNTADMIN or a role with CREATE DATABASE, CREATE WAREHOUSE
-- ============================================================================

-- 1. Warehouses
CREATE WAREHOUSE IF NOT EXISTS AFFINITY_DEMO_WH 
  WAREHOUSE_SIZE = 'MEDIUM' AUTO_SUSPEND = 300 AUTO_RESUME = TRUE
  COMMENT = 'Demo/Streamlit queries';

CREATE WAREHOUSE IF NOT EXISTS AFFINITY_GEN_WH 
  WAREHOUSE_SIZE = 'LARGE' AUTO_SUSPEND = 120 AUTO_RESUME = TRUE
  COMMENT = 'Data generation and ML training';

USE WAREHOUSE AFFINITY_GEN_WH;

-- 2. Database
CREATE DATABASE IF NOT EXISTS AFFINITY_DEMO COMMENT = 'Affinity Solutions DCR + ML Demo';
USE DATABASE AFFINITY_DEMO;

-- 3. Schemas
CREATE SCHEMA IF NOT EXISTS AFS_PROVIDER    COMMENT = 'Affinity Solutions provider-side data';
CREATE SCHEMA IF NOT EXISTS TTD_CONSUMER    COMMENT = 'The Trade Desk consumer-side data';
CREATE SCHEMA IF NOT EXISTS PUBMATIC_CONSUMER COMMENT = 'PubMatic SSP consumer-side data';
CREATE SCHEMA IF NOT EXISTS KARGO_CONSUMER  COMMENT = 'Kargo ad server consumer-side data';
CREATE SCHEMA IF NOT EXISTS ADROLL_CONSUMER COMMENT = 'AdRoll retargeting DSP consumer-side data';
CREATE SCHEMA IF NOT EXISTS ADROLL_B2B     COMMENT = 'AdRoll Site Traffic Revealer B2B firmographics';
CREATE SCHEMA IF NOT EXISTS CLEANROOM       COMMENT = 'Clean room crosswalks and match data';
CREATE SCHEMA IF NOT EXISTS ML              COMMENT = 'ML models, training sets, validation';
CREATE SCHEMA IF NOT EXISTS AI              COMMENT = 'Cortex AI / quadrant strategy';
CREATE SCHEMA IF NOT EXISTS APPS            COMMENT = 'Streamlit apps and stages';
CREATE SCHEMA IF NOT EXISTS UTIL            COMMENT = 'Enum and reference tables';

-- 4. File format for CSV loading
CREATE OR REPLACE FILE FORMAT AFFINITY_DEMO.APPS.CSV_FORMAT
  TYPE = 'CSV'
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  SKIP_HEADER = 1
  NULL_IF = ('', 'NULL')
  COMPRESSION = 'AUTO';

-- 5. Stages for data loading and Streamlit apps
CREATE OR REPLACE STAGE AFFINITY_DEMO.APPS.DATA_STAGE
  FILE_FORMAT = AFFINITY_DEMO.APPS.CSV_FORMAT
  COMMENT = 'Stage for loading CSV data files';

CREATE OR REPLACE STAGE AFFINITY_DEMO.APPS.STREAMLIT_STAGE
  COMMENT = 'Stage for Streamlit app source files';

-- Done. Next: run 02_load_data.sql
SELECT 'Environment setup complete.' AS STATUS;
