#!/usr/bin/env bash
set -euo pipefail

# Launcher script for running the bot consistently.
# Prefer venv python, fall back to system python.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -x "$SCRIPT_DIR/venv/bin/python" ]; then
  PY="$SCRIPT_DIR/venv/bin/python"
elif command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "No python interpreter found" >&2
  exit 1
fi

# Ensure project root is on PYTHONPATH so package imports work
export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"

# Run bot as module so package imports resolve
exec "$PY" -m app.bot
