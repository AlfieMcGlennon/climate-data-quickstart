#!/usr/bin/env bash
# One-time setup for the climate-data-quickstart app on macOS/Linux.
# Creates a virtual environment and installs the required packages.
# Re-run safely: if the venv already exists it is reused.

set -e

cd "$(dirname "$0")"

echo
echo "  Climate data quickstart - setup"
echo "  ================================"
echo

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "  Python 3 not found. Install Python 3.10+ first:"
    echo "    macOS: brew install python@3.12"
    echo "    Ubuntu/Debian: sudo apt install python3 python3-venv"
    echo
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "  Creating virtual environment in .venv ..."
    python3 -m venv .venv
fi

echo "  Activating virtual environment ..."
# shellcheck disable=SC1091
source .venv/bin/activate

echo "  Upgrading pip ..."
python -m pip install --upgrade pip > /dev/null

echo "  Installing packages (this may take a few minutes) ..."
if ! python -m pip install -r requirements.txt; then
    echo
    echo "  Package installation failed."
    echo "  If cartopy fails on system dependencies, try:"
    echo "    conda env create -f environment.yml"
    echo
    exit 1
fi

echo
echo "  ================================"
echo "  Setup complete."
echo
echo "  To launch the app, run: ./run_app.sh"
echo "  ================================"
echo
