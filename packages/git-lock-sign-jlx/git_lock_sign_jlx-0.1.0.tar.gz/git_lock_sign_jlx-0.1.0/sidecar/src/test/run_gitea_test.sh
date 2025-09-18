#!/bin/bash

# Gitea Test Runner
# This script runs the Gitea provisioning test with proper environment setup.

echo "🧪 Gitea Service Test Runner"
echo "============================"
echo

# Set working directory to the script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Gitea server is running
echo "🔍 Checking if Gitea server is accessible..."
if curl -s --connect-timeout 5 http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Gitea server is accessible at http://localhost:3000"
else
    echo "❌ ERROR: Cannot connect to Gitea server at http://localhost:3000"
    echo "   Please make sure Gitea is running before running this test."
    echo "   You can start it with: docker run -d --name=gitea -p 3000:3000 gitea/gitea:latest"
    exit 1
fi

export GIT_SERVER_ADMIN_TOKEN=${GITEA_ADMIN_TOKEN}
echo "GIT_SERVER_ADMIN_TOKEN: $GIT_SERVER_ADMIN_TOKEN"

# Check if admin token is set
if [ -z "$GIT_SERVER_ADMIN_TOKEN" ]; then
    echo "❌ ERROR: GIT_SERVER_ADMIN_TOKEN environment variable is not set!"
    echo
    echo "To get an admin token:"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Login as admin (or create an admin account)"
    echo "3. Go to Settings > Applications"
    echo "4. Click 'Generate New Token'"
    echo "5. Give it a name like 'test-token' and select appropriate scopes"
    echo "6. Copy the generated token"
    echo "7. Run: export GIT_SERVER_ADMIN_TOKEN='your_token_here'"
    echo "8. Then run this script again"
    echo
    exit 1
fi

echo "✅ Admin token is configured"
echo

# Activate conda environment if available
if command -v conda &> /dev/null; then
    echo "🐍 Activating conda environment 'jlx'..."
    # Source conda and activate environment
    eval "$(conda shell.bash hook)"
    conda activate jlx 2>/dev/null || echo "⚠️  Could not activate conda environment 'jlx', proceeding with system Python"
fi

# Run the test script
echo "🚀 Running Gitea provisioning test..."
echo
python3 ./test_gitea_provision.py

# Capture exit code
exit_code=$?

echo
if [ $exit_code -eq 0 ]; then
    echo "🎉 Test completed successfully!"
    echo "You can check the results at http://localhost:3000"
else
    echo "❌ Test failed with exit code $exit_code"
fi

exit $exit_code 