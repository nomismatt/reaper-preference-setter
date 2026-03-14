#!/bin/bash
# Build standalone executable for the current platform.
# Run this on each target OS (macOS, Windows, Linux) to produce
# a native executable that requires no Python installation.
#
# Prerequisites:
#   pip install pyinstaller

set -e

echo "Building REAPER Preference Setter..."

pyinstaller \
    --onefile \
    --console \
    --name "REAPER Preference Setter" \
    configure_reaper.py

echo ""
echo "Build complete!"
echo "Executable: dist/REAPER Preference Setter"
echo ""
echo "To create a GitHub release with this binary:"
echo "  gh release create v1.0 'dist/REAPER Preference Setter' --title 'v1.0' --notes 'Initial release'"
