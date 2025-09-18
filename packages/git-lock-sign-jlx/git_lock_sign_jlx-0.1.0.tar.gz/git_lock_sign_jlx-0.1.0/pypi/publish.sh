#!/bin/bash
# Publish to PyPI (production)
# This uploads to pypi.org for public release

set -e

echo "🚀 Publishing git_lock_sign_jlx to PyPI..."

# Initialize conda and activate environment
echo "🐍 Activating conda environment 'jlx'..."
eval "$(conda shell.bash hook)"
conda activate jlx

# Go to the extension root directory
cd "$(dirname "$0")/.."

# Check if dist exists
if [ ! -d "dist" ]; then
    echo "❌ No dist directory found. Run ./build.sh first."
    exit 1
fi

# Check if files exist in dist
if [ -z "$(ls -A dist/)" ]; then
    echo "❌ No files in dist/. Run ./build.sh first."
    exit 1
fi

echo "📦 Files to upload:"
ls -la dist/

echo ""
echo "⚠️  WARNING: This will publish to PRODUCTION PyPI!"
echo "Make sure you've tested on TestPyPI first."
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

# Upload to PyPI
echo "🚀 Uploading to PyPI..."
twine upload dist/*

echo "✅ Upload to PyPI complete!"
echo ""
echo "🔗 View on PyPI: https://pypi.org/project/git-lock-sign-jlx/"
echo ""
echo "🎉 Your package is now publicly available!"
echo "Users can install with: pip install git-lock-sign-jlx"
