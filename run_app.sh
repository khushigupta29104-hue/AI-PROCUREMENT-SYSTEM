#!/usr/bin/env bash
# run_app.sh -- convenience launcher for Linux/Mac
set -e
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi
streamlit run frontend/app.py
