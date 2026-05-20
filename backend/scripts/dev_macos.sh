#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -d ".venv" ]]; then
  echo "Creating .venv..."
  python3 -m venv .venv
fi

source ".venv/bin/activate"

echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Initializing database..."
python3 scripts/setup_database.py

echo "Starting server on http://localhost:8000 ..."
PYTHONPATH="$PROJECT_ROOT/..${PYTHONPATH:+:$PYTHONPATH}" \
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
