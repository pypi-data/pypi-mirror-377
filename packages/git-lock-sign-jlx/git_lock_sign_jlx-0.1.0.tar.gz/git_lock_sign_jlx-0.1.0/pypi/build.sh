#!/bin/bash
# Build script for the JupyterLab extension
# This compiles the frontend and creates distribution packages

set -e

echo "🏗️  Building git_lock_sign_jlx package..."

# Initialize conda and activate environment
echo "🐍 Activating conda environment 'jlx'..."
eval "$(conda shell.bash hook)"
conda activate jlx

# Go to the extension root directory
cd "$(dirname "$0")/.."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/
rm -rf git_lock_sign_jlx/labextension/

# Clean node modules and reinstall (optional, uncomment if needed)
# echo "🧹 Cleaning node modules..."
# rm -rf node_modules/
# jlpm install

# Build the package (this includes frontend compilation)
echo "📦 Building package with frontend compilation..."
python -m build

echo "✅ Build complete!"
echo ""
echo "Generated files:"
ls -la dist/
echo ""
echo "Next steps:"
echo "- Run ./test-local.sh to test the build"
echo "- Run ./publish-test.sh to upload to TestPyPI"
echo "- Run ./publish.sh to upload to PyPI"
