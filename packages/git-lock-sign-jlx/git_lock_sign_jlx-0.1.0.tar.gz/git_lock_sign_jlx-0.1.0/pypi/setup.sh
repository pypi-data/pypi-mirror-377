#!/bin/bash
# Setup script for PyPI publishing
# This installs the required build tools

set -e

echo "🚀 Setting up PyPI publishing tools..."

# Initialize conda for script usage
echo "🐍 Initializing conda environment..."
# Source conda configuration
eval "$(conda shell.bash hook)"

# Activate the jlx environment
echo "🔧 Activating conda environment 'jlx'..."
conda activate jlx

# Install required packages
echo "📦 Installing build and publishing tools..."
pip install --upgrade pip
pip install build twine

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run ./build.sh to build the package"
echo "2. Run ./test-local.sh to test locally"
echo "3. Run ./publish-test.sh to publish to TestPyPI"
echo "4. Run ./publish.sh to publish to PyPI"
