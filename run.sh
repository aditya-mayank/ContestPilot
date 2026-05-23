#!/usr/bin/env bash

echo "[ContestPilot] Starting up..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found."
    echo "Please install Python 3.10+ and ensure it's in your PATH."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[ContestPilot] Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "[ContestPilot] Installing dependencies..."
python3 -m pip install --upgrade pip -q
pip install -r requirements.txt -q

# Run the main program
echo "[ContestPilot] Running application..."
python3 main.py "$@"

if [ $# -eq 0 ]; then
    echo "[ContestPilot] Done."
    read -p "Press enter to continue..."
fi
