#!/bin/bash
# Publish to TestPyPI for testing
# This uploads to test.pypi.org for verification before real release

set -e

echo "🧪 Publishing git_lock_sign_jlx to TestPyPI..."

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

# Upload to TestPyPI
echo "🚀 Uploading to TestPyPI..."
twine upload --repository testpypi dist/*

echo "✅ Upload to TestPyPI complete!"
echo ""
echo "🔗 View on TestPyPI: https://test.pypi.org/project/git-lock-sign-jlx/"
echo ""
echo "To test installation from TestPyPI:"
echo "pip install --index-url https://test.pypi.org/simple/ git-lock-sign-jlx"
echo ""
echo "If everything works on TestPyPI:"
echo "- Run ./publish.sh to upload to real PyPI"
