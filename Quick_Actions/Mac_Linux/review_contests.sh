#!/usr/bin/env bash
cd "$(dirname "$0")/../.."
echo "========================================="
echo "    ContestPilot - Manual Attendance Review"
echo "========================================="
echo "(Contests are auto-verified, but you can use this to manually review or verify them)"
./run.sh --review
read -p "Press Enter to continue..."
