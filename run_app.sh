#!/usr/bin/env bash
# Launches the climate-data-quickstart Streamlit app on macOS/Linux.

set -e

cd "$(dirname "$0")"

if [ ! -f ".venv/bin/activate" ]; then
    echo ".venv not found. Run ./setup.sh first to install dependencies." >&2
    exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate
streamlit run app/main.py
