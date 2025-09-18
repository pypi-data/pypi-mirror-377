#!/bin/bash
# Test the built package locally
# This installs the wheel and verifies the extension works

set -e

echo "🧪 Testing git_lock_sign_jlx package locally..."

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

# Find the wheel file
WHEEL_FILE=$(find dist -name "*.whl" | head -1)
if [ -z "$WHEEL_FILE" ]; then
    echo "❌ No wheel file found in dist/. Run ./build.sh first."
    exit 1
fi

echo "📦 Found wheel: $WHEEL_FILE"

# Uninstall existing version if present
echo "🗑️  Uninstalling existing version..."
pip uninstall git-lock-sign-jlx -y || true

# Install from wheel
echo "📥 Installing from wheel..."
pip install "$WHEEL_FILE"

# Check if extension is installed
echo "🔍 Checking if extension is registered..."
jupyter labextension list

echo "✅ Local test complete!"
echo ""
echo "To verify in JupyterLab:"
echo "1. jupyter lab"
echo "2. Open a notebook"
echo "3. Check for git lock/sign buttons in toolbar"
echo ""
echo "If everything works:"
echo "- Run ./publish-test.sh to upload to TestPyPI"
echo "- Run ./publish.sh to upload to PyPI"
