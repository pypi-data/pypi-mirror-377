#!/bin/bash
# Check and update version before publishing
# This helps manage version numbers across package.json and pyproject.toml

set -e

echo "🔍 Checking version information..."

# Initialize conda and activate environment
echo "🐍 Activating conda environment 'jlx'..."
eval "$(conda shell.bash hook)"
conda activate jlx

# Go to the extension root directory
cd "$(dirname "$0")/.."

echo "📦 Current version in package.json:"
grep '"version"' package.json | head -1

echo "📋 Version sync in pyproject.toml:"
grep -A 1 '\[tool.hatch.version\]' pyproject.toml

echo ""
echo "🔗 Latest versions on PyPI:"
echo "Production: https://pypi.org/project/git-lock-sign-jlx/"
echo "Test: https://test.pypi.org/project/git-lock-sign-jlx/"

echo ""
echo "To update version:"
echo "1. Edit package.json version field"
echo "2. pyproject.toml will sync automatically"
echo "3. Run ./build.sh to rebuild with new version"

echo ""
echo "Version format should be: X.Y.Z (e.g., 0.1.1, 0.2.0, 1.0.0)"
