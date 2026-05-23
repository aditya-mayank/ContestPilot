#!/usr/bin/env bash
cd "$(dirname "$0")/.."
echo "========================================="
echo "    ContestPilot - Update App"
echo "========================================="
git pull origin main
read -p "Press Enter to continue..."
