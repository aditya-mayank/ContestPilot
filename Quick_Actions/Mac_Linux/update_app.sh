#!/usr/bin/env bash
cd "$(dirname "$0")/../.."
echo "========================================="
echo "    ContestPilot - Update App"
echo "========================================="

echo ""
echo "[1/3] Checking for updates..."
source .venv/bin/activate 2>/dev/null
python3 main.py --check-update

echo ""
echo "[2/3] Pulling latest from GitHub..."
git pull origin main

echo ""
echo "[3/3] Reinstalling dependencies..."
pip install -r requirements.txt -q

echo ""
echo "========================================="
echo " Done! ContestPilot has been updated."
echo "========================================="
read -p "Press Enter to continue..."
