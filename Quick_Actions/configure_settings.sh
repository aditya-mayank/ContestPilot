#!/usr/bin/env bash
cd "$(dirname "$0")/.."
echo "========================================="
echo "    ContestPilot - Configure Settings"
echo "========================================="
./run.sh --config
read -p "Press Enter to continue..."
