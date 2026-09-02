#!/bin/bash
echo "=== Starting MITO Assistant Backend Engine ==="
CD_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$CD_DIR"

export MITO_HEADLESS=1

if [ -f "$CD_DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$CD_DIR/.venv/bin/python3"
elif [ -f "$CD_DIR/darling_env/bin/python3" ]; then
    PYTHON_BIN="$CD_DIR/darling_env/bin/python3"
else
    PYTHON_BIN="python3"
fi

echo "Using Python: $PYTHON_BIN"
exec "$PYTHON_BIN" Main.py
