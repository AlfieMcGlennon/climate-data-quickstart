#!/usr/bin/env bash
# One-time setup for the climate-data-quickstart app on macOS/Linux.
# Creates a virtual environment and installs the required packages.

set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv ..."
    python3 -m venv .venv
fi

echo "Activating virtual environment ..."
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Upgrading pip ..."
python -m pip install --upgrade pip > /dev/null

echo "Installing requirements (this may take a few minutes) ..."
python -m pip install -r requirements.txt

echo
echo "Setup complete. Run ./run_app.sh to launch the app."
