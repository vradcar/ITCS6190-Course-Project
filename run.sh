#!/usr/bin/env bash

# Orchestrator for:
#  1) Batch analytics (main.py)
#  2) ML pipeline (ml_pipeline.py)
#  3) Spark Structured Streaming demo (streaming_processor + streaming_data_simulator)

# --------------------------
# Resolve paths
# --------------------------
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SPARK_DIR="$PROJECT_ROOT/spark-analytics"
VENV_DIR="$SPARK_DIR/.venv"

echo "============================================================"
echo "ENVIRONMENT SETUP"
echo "============================================================"
echo "Project root   : $PROJECT_ROOT"
echo "Spark folder   : $SPARK_DIR"
echo "Virtualenv     : $VENV_DIR"
echo

# --------------------------
# Activate virtualenv (if present)
# --------------------------
if [ -d "$VENV_DIR" ]; then
  echo "🔹 Activating virtualenv at $VENV_DIR"
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
else
  echo "⚠️  No virtualenv found at $VENV_DIR"
  echo "   You can create one with:"
  echo "     cd spark-analytics"
  echo "     python -m venv .venv"
  echo "     source .venv/bin/activate"
  echo "     pip install pyspark"
  echo
fi

# --------------------------
# Verify pyspark is installed
# --------------------------
if ! python -c "import pyspark" >/dev/null 2>&1; then
  echo "❌ pyspark is NOT available in the current Python environment."
  echo "   From the spark-analytics folder, run once:"
  echo "       source .venv/bin/activate      # if not already"
  echo "       python -m pip install --upgrade pip"
  echo "       python -m pip install pyspark"
  echo
  echo "After installing, re-run: ./run.sh"
  exit 1
fi

echo "✅ pyspark is available."
echo

cd "$SPARK_DIR" || exit 1

# --------------------------
# STEP 1: Batch analytics (main.py)
# --------------------------
echo "============================================================"
echo "STEP 1: Batch analytics (main.py)"
echo "============================================================"
python main.py
if [ $? -ne 0 ]; then
  echo "[!] Batch analytics FAILED (see error above)."
  echo "[!] Continuing to ML + streaming anyway..."
fi
echo

# --------------------------
# STEP 2: ML pipeline (ml_pipeline.py)
#       Uses your MLPipeline + DataLoader + JobClassifier + SkillExtractor + JobRecommender
# --------------------------
echo "============================================================"
echo "STEP 2: ML pipeline (ml_pipeline.py)"
echo "============================================================"
python ml_pipeline.py --save
if [ $? -ne 0 ]; then
  echo "[!] ML pipeline FAILED (see error above)."
  echo "[!] Continuing to streaming anyway..."
fi
echo

# --------------------------
# STEP 3: Spark Structured Streaming demo
# --------------------------
echo "============================================================"
echo "STEP 3: Spark Structured Streaming demo"
echo "============================================================"

echo "    - Launching streaming processor in background..."
python streaming_processor.py &
PROCESSOR_PID=$!

echo "    - Launching streaming data simulator in background..."
python streaming_data_simulator.py &
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
