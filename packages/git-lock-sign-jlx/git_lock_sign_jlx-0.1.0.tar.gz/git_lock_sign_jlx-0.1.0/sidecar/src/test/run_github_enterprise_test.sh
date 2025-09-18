#!/bin/bash
set -e

echo "🚀 GitHub Enterprise Sidecar Workflow Test"
echo "==========================================="

# Change to the test directory
cd "$(dirname "$0")"

# Check if .env.github-enterprise exists
if [ ! -f ".env.github-enterprise" ]; then
    echo "❌ .env.github-enterprise file not found."
    echo "   Please create this file with your GitHub Enterprise configuration:"
    echo ""
    echo "   GIT_SERVER=github_enterprise"
    echo "   GIT_SERVER_URL=https://github.com/JupyterTestOrg"
    echo "   GITHUB_ENTERPRISE_URL=https://github.com/JupyterTestOrg"
    echo "   GITHUB_ENTERPRISE_ORG=JupyterTestOrg"
    echo "   GITHUB_APP_ID=your_app_id"
    echo "   GITHUB_APP_INSTALLATION_ID=your_installation_id"
    echo "   GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem"
    echo ""
    exit 1
fi

# Source the .env.github-enterprise file
echo "📋 Loading configuration from .env.github-enterprise"
set -a
source .env.github-enterprise
set +a

# Validate required variables
required_vars=(
    "GITHUB_APP_ID"
    "GITHUB_APP_INSTALLATION_ID" 
    "GITHUB_ENTERPRISE_ORG"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please set these variables in .env.github-enterprise file"
    exit 1
fi

# Check if GitHub App private key exists
private_key_path="${GITHUB_APP_PRIVATE_KEY_PATH:-../../../docker/secrets/github-app-private-key.pem}"
if [ ! -f "$private_key_path" ]; then
    echo "❌ GitHub App private key not found: $private_key_path"
    echo "   Please ensure your private key is available at the specified path"
    exit 1
fi

# Activate the correct conda environment if available
if command -v conda >/dev/null 2>&1; then
    echo "🐍 Activating conda environment 'jlx'"
    eval "$(conda shell.bash hook)"
    if conda env list | grep -q "jlx"; then
        conda activate jlx
    else
        echo "⚠️ Conda environment 'jlx' not found, using current environment"
    fi
fi

# Check Python dependencies
echo "🔍 Checking Python dependencies..."
python3 -c "
import sys
required_packages = ['requests', 'uvicorn', 'fastapi', 'github']
missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f'❌ Missing Python packages: {missing}')
    print('   Install with: pip install ' + ' '.join(missing))
    sys.exit(1)
else:
    print('✅ All required Python packages are available')
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Show configuration summary
echo ""
echo "📊 Configuration Summary:"
echo "   GitHub URL: ${GITHUB_ENTERPRISE_URL:-${GIT_SERVER_URL:-'Not set'}}"
echo "   Organization: ${GITHUB_ENTERPRISE_ORG}"
echo "   App ID: ${GITHUB_APP_ID}"
echo "   Installation ID: ${GITHUB_APP_INSTALLATION_ID}"
echo "   Test User: liuji1031@live.com"
echo "   Expected Repository: ${GITHUB_ENTERPRISE_ORG}/liuji1031-work"
echo ""

# Run the test
echo "🧪 Running GitHub Enterprise workflow test..."
echo ""

# Set PYTHONPATH to ensure imports work
export PYTHONPATH="$(pwd)/../..:$PYTHONPATH"

# Run the Python test script
python3 test_github_enterprise_workflow.py \
    --user-name "liuji1031" \
    --user-email "liuji1031@live.com" \
    --server-url "http://localhost:8001"

test_result=$?

echo ""
if [ $test_result -eq 0 ]; then
    echo "🎉 GitHub Enterprise test completed successfully!"
    echo ""
    echo "✅ Next steps:"
    echo "   1. Check your GitHub organization: https://github.com/${GITHUB_ENTERPRISE_ORG}"
    echo "   2. Look for repository: liuji1031-work"
    echo "   3. Verify the test notebook was uploaded"
    echo ""
    echo "🚀 You can now test the full JupyterLab extension!"
else
    echo "💔 GitHub Enterprise test failed."
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "   1. Check your GitHub App permissions"
    echo "   2. Verify the Installation ID is correct"
    echo "   3. Ensure the private key file is valid"
    echo "   4. Check the sidecar service logs above"
    echo ""
fi

exit $test_result 