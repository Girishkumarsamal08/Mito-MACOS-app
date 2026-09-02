#!/bin/bash
echo "=== Starting MITO Assistant Engine & GUI ==="
CD_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$CD_DIR"

if [ -f "$CD_DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$CD_DIR/.venv/bin/python3"
elif [ -f "$CD_DIR/darling_env/bin/python3" ]; then
    PYTHON_BIN="$CD_DIR/darling_env/bin/python3"
else
    PYTHON_BIN="python3"
fi

echo "Using Python: $PYTHON_BIN"
exec "$PYTHON_BIN" Main.py
