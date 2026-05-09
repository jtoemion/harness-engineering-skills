#!/bin/bash
# Antigravity Mode Detector
# Returns QUICK or FULL based on .memory/ directory existence
# Usage: ./detect-mode.sh from project root

if [ -d ".memory" ]; then
    echo "FULL"
else
    echo "QUICK"
fi