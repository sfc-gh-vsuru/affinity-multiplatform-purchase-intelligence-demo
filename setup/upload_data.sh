#!/bin/bash
# ============================================================================
# Upload data files and Streamlit apps to Snowflake stages
# Run from the repo root directory
# Requires: Snowflake CLI (snow) configured with a connection
# Usage: ./setup/upload_data.sh [connection_name]
# ============================================================================

set -e

CONN=${1:-"default"}
echo "Using Snowflake connection: $CONN"

echo ""
echo "=== Uploading data files to @AFFINITY_DEMO.APPS.DATA_STAGE ==="
for dir in data/cleanroom data/ml data/ttd_consumer data/pubmatic_consumer data/kargo_consumer data/afs_provider; do
    schema=$(basename "$dir")
    echo "  Uploading $dir/ -> @AFFINITY_DEMO.APPS.DATA_STAGE/$schema/"
    snow stage copy "$dir/" "@AFFINITY_DEMO.APPS.DATA_STAGE/$schema/" --overwrite --connection "$CONN" 2>&1 | grep -E "UPLOADED|Error" || true
done

echo ""
echo "=== Uploading Streamlit apps to @AFFINITY_DEMO.APPS.STREAMLIT_STAGE ==="
for app in pipeline_app ttd_app pubmatic_app kargo_app crossplatform_app; do
    echo "  Uploading apps/$app/"
    snow stage copy "apps/$app/streamlit_app.py" "@AFFINITY_DEMO.APPS.STREAMLIT_STAGE/$app/" --overwrite --connection "$CONN" 2>&1 | grep -E "UPLOADED|Error" || true
done

echo ""
echo "=== Upload complete ==="
echo "Next: Run setup/02_load_data.sql in Snowflake, then setup/03_streamlit_apps.sql"
