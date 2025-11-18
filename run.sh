#!/usr/bin/env bash
set -euo pipefail

# Find repo root (where this script lives) and spark-analytics folder
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPARK_DIR="$ROOT_DIR/spark-analytics"

if [ ! -d "$SPARK_DIR" ]; then
  echo "❌ spark-analytics directory not found at: $SPARK_DIR"
  exit 1
fi

cd "$SPARK_DIR"

# Basic sanity check
if [ ! -f "requirements.txt" ]; then
  echo "❌ requirements.txt not found in $SPARK_DIR"
  exit 1
fi

# Detect python (Codespaces usually has python3)
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="${PYTHON_BIN:-python3}"
else
  PYTHON_BIN="${PYTHON_BIN:-python}"
fi

activate_venv() {
  if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  elif [ -f ".venv/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/Scripts/activate
  fi
}

setup_env() {
  echo "[*] Setting up virtual environment and dependencies in $SPARK_DIR..."

  if [ ! -d ".venv" ]; then
    echo "    - Creating .venv..."
    "$PYTHON_BIN" -m venv .venv
  else
    echo "    - .venv already exists, reusing it."
  fi

  activate_venv

  echo "    - Upgrading pip and installing requirements..."
  pip install --upgrade pip
  pip install -r requirements.txt

  echo "[✓] Environment ready."
}

run_batch() {
  echo "[*] Running batch analytics (main.py)..."
  activate_venv

  # Run main.py but don't let a failure kill the whole script
  if "$PYTHON_BIN" main.py; then
    echo "[✓] Batch analytics finished."
  else
    echo "[!] Batch analytics FAILED (non-zero exit code)."
    echo "[!] See the error above from Spark / main.py."
    echo "[!] Continuing to streaming anyway..."
  fi
}

run_streaming() {
  echo "[*] Starting streaming demo (processor + simulator)..."
  activate_venv

  mkdir -p streaming_input

  echo "    - Launching streaming processor in background..."
  "$PYTHON_BIN" streaming_processor.py &
  PROC_PID=$!

  sleep 5

  echo "    - Launching streaming data simulator in background..."
  "$PYTHON_BIN" streaming_data_simulator.py &
  SIM_PID=$!

  echo
  echo "[*] Streaming demo is running."
  echo "    - Processor PID : $PROC_PID"
  echo "    - Simulator PID : $SIM_PID"
  echo "Press Ctrl+C to stop both."

  trap 'echo; echo "[*] Stopping streaming jobs..."; kill "$PROC_PID" "$SIM_PID" 2>/dev/null || true; exit 0' INT

  wait "$PROC_PID" "$SIM_PID"
}

# Default behavior: run EVERYTHING
COMMAND="${1:-all}"

case "$COMMAND" in
  all)
    setup_env
    run_batch
    run_streaming
    ;;
  setup)
    setup_env
    ;;
  batch)
    run_batch
    ;;
  streaming)
    run_streaming
    ;;
  *)
    echo "Usage: ./run.sh [all|setup|batch|streaming]"
    echo "  all        (default) setup env + batch + streaming"
    echo "  setup      only create venv and install deps"
    echo "  batch      only run main.py"
    echo "  streaming  only run processor + simulator"
    ;;
esac