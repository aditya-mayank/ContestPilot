#!/usr/bin/env bash
cd "$(dirname "$0")/.."
echo "========================================="
echo "    ContestPilot - View Stats"
echo "========================================="
./run.sh --stats
read -p "Press Enter to continue..."
