#!/bin/bash
# Clean build artifacts
# This removes all build files and caches

set -e

echo "🧹 Cleaning build artifacts..."

# Go to the extension root directory
cd "$(dirname "$0")/.."

# Remove build directories
echo "🗑️  Removing build directories..."
rm -rf dist/
rm -rf build/
rm -rf *.egg-info/
rm -rf git_lock_sign_jlx/labextension/

# Clean Python cache
echo "🗑️  Removing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Clean npm/yarn cache (optional)
echo "🗑️  Cleaning npm build cache..."
rm -rf lib/
rm -rf .cache/
rm -rf tsconfig.tsbuildinfo

echo "✅ Clean complete!"
echo ""
echo "Next steps:"
echo "- Run ./build.sh to create a fresh build"
