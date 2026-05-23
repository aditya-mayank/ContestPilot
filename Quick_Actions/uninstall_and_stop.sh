#!/usr/bin/env bash
cd "$(dirname "$0")/.."
echo "========================================="
echo "    ContestPilot - Uninstall & Stop"
echo "========================================="
./run.sh --stop-all
read -p "Press Enter to continue..."
