#!/usr/bin/env bash
# Cross-platform launcher for macOS (12+) and Ubuntu
# - Uses local .venv if present, else creates one
# - Installs requirements
# - Ensures Tkinter availability notes

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Detect python
PYBIN=""
if command -v python3 >/dev/null 2>&1; then
  PYBIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYBIN="python"
else
  echo "Python 3 is required. Please install it." >&2
  exit 1
fi

# Create/Use venv
if [ -d ".venv" ]; then
  echo "Using existing .venv"
else
  echo "Creating venv in .venv"
  "$PYBIN" -m venv .venv
fi

# Activate venv
# shellcheck disable=SC1091
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install deps
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# Helpful hints for Tk (if tkinter import fails)
python - <<'PY'
try:
    import tkinter  # noqa: F401
    print("Tkinter OK")
except Exception as e:
    import sys
    print("WARNING: Tkinter not available:", e, file=sys.stderr)
    print("\nOn Ubuntu: sudo apt-get update && sudo apt-get install -y python3-tk", file=sys.stderr)
    print("On macOS (Homebrew Python): brew install python-tk@3.11 or use system Python with Tk.", file=sys.stderr)
PY

# Run the app
exec python main_gui.py
