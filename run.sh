#!/usr/bin/env bash

# Orchestrator for:
#  1) Batch analytics (main.py)
#  2) ML pipeline (ml_pipeline.py)
#  3) Spark Structured Streaming demo (streaming_processor + streaming_data_simulator)
#
# Usage (from repo root):
#   chmod +x run.sh
#   ./run.sh

set -Eeuo pipefail

# --------------------------
# Resolve paths
# --------------------------
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SPARK_DIR="$PROJECT_ROOT/spark-analytics"
VENV_DIR="$SPARK_DIR/.venv"
REQUIREMENTS_FILE="$SPARK_DIR/requirements.txt"

echo "============================================================"
echo "ENVIRONMENT SETUP"
echo "============================================================"
echo "Project root   : $PROJECT_ROOT"
echo "Spark folder   : $SPARK_DIR"
echo "Virtualenv     : $VENV_DIR"
echo "Requirements   : $REQUIREMENTS_FILE"
echo

# --------------------------
# Pick Python (python3 > python)
# --------------------------
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  echo "❌ No python or python3 found on PATH. Please install Python."
  exit 1
fi

echo "Using Python   : $PYTHON"
echo

# --------------------------
# Create virtualenv if missing
# --------------------------
if [ ! -d "$VENV_DIR" ]; then
  echo "🔹 Creating virtualenv at $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
  echo
else
  echo "🔹 Virtualenv already exists at $VENV_DIR"
  echo
fi

# --------------------------
# Activate virtualenv (Unix + Windows Git Bash)
# --------------------------
if [ -f "$VENV_DIR/bin/activate" ]; then
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
  # shellcheck disable=SC1090
  source "$VENV_DIR/Scripts/activate"
else
  echo "❌ Could not find activate script in:"
  echo "   - $VENV_DIR/bin/activate"
  echo "   - $VENV_DIR/Scripts/activate"
  exit 1
fi

echo "✅ Virtualenv activated."
echo

# --------------------------
# Install dependencies
# --------------------------
echo "============================================================"
echo "DEPENDENCY INSTALL"
echo "============================================================"

pip install --upgrade pip >/dev/null

if [ -f "$REQUIREMENTS_FILE" ]; then
  echo "🔹 Installing from requirements.txt ..."
  pip install -r "$REQUIREMENTS_FILE"
else
  echo "⚠️  No requirements.txt found at $REQUIREMENTS_FILE"
  echo "   Installing pyspark only as a fallback..."
  pip install pyspark
fi

echo

# --------------------------
# Verify pyspark is installed
# --------------------------
echo "🔍 Verifying pyspark import ..."
$PYTHON - <<'PYCODE'
try:
    import pyspark  # noqa: F401
    print("✅ pyspark import OK.")
except Exception as e:
    import sys
    print("❌ pyspark import FAILED:", e, file=sys.stderr)
    sys.exit(1)
PYCODE
echo

cd "$SPARK_DIR" || {
  echo "❌ Failed to cd into $SPARK_DIR"
  exit 1
}

# --------------------------
# STEP 1: Batch analytics (main.py)
# --------------------------
echo "============================================================"
echo "STEP 1: Batch analytics (main.py)"
echo "============================================================"
if [ -f "main.py" ]; then
  $PYTHON main.py || {
    echo "[!] Batch analytics FAILED (see error above)."
  }
else
  echo "⚠️  main.py not found in $SPARK_DIR, skipping batch analytics."
fi
echo

# --------------------------
# STEP 2: ML pipeline (ml_pipeline.py)
# --------------------------
echo "============================================================"
echo "STEP 2: ML pipeline (ml_pipeline.py)"
echo "============================================================"
if [ -f "ml_pipeline.py" ]; then
  $PYTHON ml_pipeline.py --save || {
    echo "[!] ML pipeline FAILED (see error above)."
  }
else
  echo "⚠️  ml_pipeline.py not found in $SPARK_DIR, skipping ML pipeline."
fi
echo

# Print ML outputs (if any)
ML_OUT_DIR="$SPARK_DIR/analytics_output/ml_outputs"
if [ -d "$ML_OUT_DIR" ]; then
  echo "🔎 ML outputs saved under: $ML_OUT_DIR"
  echo "Files:"
  ls -lh "$ML_OUT_DIR" || true
  echo
  echo "Showing first 10 lines of CSVs (if present):"
  for f in "$ML_OUT_DIR"/*.csv; do
    [ -e "$f" ] || continue
    echo "---- $f ----"
    head -n 10 "$f" || true
    echo
  done
fi

# --------------------------
# STEP 3: Complex analytics & visualizations (complex_queries_job.py)
# --------------------------
echo "============================================================"
echo "STEP 3: Complex analytics & visualizations (complex_queries_job.py)"
echo "============================================================"
if [ -f "complex_queries_job.py" ]; then
  $PYTHON complex_queries_job.py || {
    echo "[!] Complex analytics job FAILED (see error above)."
  }
else
  echo "⚠️  complex_queries_job.py not found; skipping analytics visualization step."
fi
echo

# Print complex query results and visuals summary
QUERY_OUT_DIR="$SPARK_DIR/analytics_output/query_results"
VISUALS_OUT_DIR="$SPARK_DIR/analytics_output/visuals"
if [ -d "$QUERY_OUT_DIR" ]; then
  echo "🔎 Query results saved under: $QUERY_OUT_DIR"
  ls -lh "$QUERY_OUT_DIR" || true
  echo
  echo "Showing first 10 lines of CSVs:"
  for f in "$QUERY_OUT_DIR"/*.csv; do
    [ -e "$f" ] || continue
    echo "---- $f ----"
    head -n 10 "$f" || true
    echo
  done
fi

if [ -d "$VISUALS_OUT_DIR" ]; then
  echo "🖼️  Visualizations saved under: $VISUALS_OUT_DIR"
  ls -lh "$VISUALS_OUT_DIR" || true
  echo
fi

# --------------------------
# STEP 4: Spark Structured Streaming demo
# --------------------------
echo "============================================================"
echo "STEP 4: Spark Structured Streaming demo"
echo "============================================================"

if [ ! -f "streaming_processor.py" ] || [ ! -f "streaming_data_simulator.py" ]; then
  echo "⚠️  Streaming scripts not found (streaming_processor.py / streaming_data_simulator.py)."
  echo "    Skipping streaming demo."
  exit 0
fi

echo "    - Launching streaming processor in background..."
$PYTHON streaming_processor.py &
PROCESSOR_PID=$!

echo "    - Launching streaming data simulator in background..."
$PYTHON streaming_data_simulator.py &
SIMULATOR_PID=$!

echo
echo "[*] Streaming demo is running."
echo "    - Processor PID : $PROCESSOR_PID"
echo "    - Simulator PID : $SIMULATOR_PID"
echo "Press Ctrl+C to stop both."
echo

# Clean shutdown on Ctrl+C
trap "echo; echo '[*] Stopping streaming jobs...'; kill $PROCESSOR_PID $SIMULATOR_PID 2>/dev/null || true; exit 0" SIGINT

# Keep script alive so background jobs keep running
while true; do
  sleep 5
done
