#!/usr/bin/env bash
cd "$(dirname "$0")/.."
echo "========================================="
echo "    ContestPilot - Review Contests"
echo "========================================="
./run.sh --review
read -p "Press Enter to continue..."
