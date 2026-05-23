#!/usr/bin/env bash
cd "$(dirname "$0")/.."
echo "========================================="
echo "    ContestPilot - Clear Calendar"
echo "========================================="
./run.sh --clear-calendar
read -p "Press Enter to continue..."
