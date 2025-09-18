#!/bin/bash
# Test conda environment setup
# This verifies that the conda environment is working correctly

set -e

echo "🧪 Testing conda environment setup..."

# Initialize conda and activate environment
echo "🐍 Initializing conda..."
eval "$(conda shell.bash hook)"

echo "🔧 Testing conda environment 'jlx'..."
if conda activate jlx; then
    echo "✅ Successfully activated 'jlx' environment"
    
    echo "📍 Current environment info:"
    echo "  - Python version: $(python --version)"
    echo "  - Pip version: $(pip --version)"
    echo "  - Environment path: $CONDA_PREFIX"
    
    echo ""
    echo "🔍 Checking for required tools..."
    
    # Check if jlpm is available
    if command -v jlpm &> /dev/null; then
        echo "  ✅ jlpm: $(jlpm --version)"
    else
        echo "  ❌ jlpm: Not found (install with 'npm install -g yarn')"
    fi
    
    # Check if jupyter is available
    if command -v jupyter &> /dev/null; then
        echo "  ✅ jupyter: $(jupyter --version | head -1)"
    else
        echo "  ❌ jupyter: Not found (install with 'pip install jupyterlab')"
    fi
    
    # Check if build tools would be available
    if python -c "import build" 2>/dev/null; then
        echo "  ✅ build: Available"
    else
        echo "  ❌ build: Not found (install with 'pip install build')"
    fi
    
    if python -c "import twine" 2>/dev/null; then
        echo "  ✅ twine: Available"
    else
        echo "  ❌ twine: Not found (install with 'pip install twine')"
    fi
    
    echo ""
    echo "✅ Environment test complete!"
    echo "If any tools are missing, run ./setup.sh to install them."
    
else
    echo "❌ Failed to activate 'jlx' environment"
    echo ""
    echo "Available environments:"
    conda info --envs
    echo ""
    echo "To fix this:"
    echo "1. Create the environment: conda create -n jlx python=3.9"
    echo "2. Or update scripts to use your environment name"
    exit 1
fi
