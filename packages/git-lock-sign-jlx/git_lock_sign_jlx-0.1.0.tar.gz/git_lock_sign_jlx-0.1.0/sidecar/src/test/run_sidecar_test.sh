#!/bin/bash

# Simple wrapper script for running the sidecar workflow test

set -e

# Default values
DEFAULT_USER_NAME="sidecar-dev-1"
DEFAULT_USER_EMAIL="sidecar-dev-1@test.org"

# Parse command line arguments
USER_NAME="${1:-$DEFAULT_USER_NAME}"
USER_EMAIL="${2:-$DEFAULT_USER_EMAIL}"

echo "🧪 Running Sidecar Workflow Test"
echo "================================"
echo "User: $USER_NAME <$USER_EMAIL>"
echo ""

# Check if we're in the right directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_SCRIPT="$SCRIPT_DIR/test_sidecar_workflow.py"

if [ ! -f "$TEST_SCRIPT" ]; then
    echo "❌ ERROR: Test script not found at $TEST_SCRIPT"
    exit 1
fi

export GIT_SERVER_ADMIN_TOKEN=${GITEA_ADMIN_TOKEN}

# Check prerequisites
if [ -z "$GIT_SERVER_ADMIN_TOKEN" ]; then
    echo "❌ ERROR: GIT_SERVER_ADMIN_TOKEN environment variable not set!"
    echo ""
    echo "Please set the admin token first:"
    echo "export GIT_SERVER_ADMIN_TOKEN='your_admin_token_here'"
    echo ""
    echo "To get the admin token:"
    echo "1. Login to your git server (e.g., http://localhost:3000 for Gitea)"
    echo "2. Go to Settings > Applications > Generate New Token"
    echo "3. Copy the token and export it as shown above"
    exit 1
fi

# Activate conda environment if available
if command -v conda >/dev/null 2>&1; then
    echo "🐍 Activating conda environment 'jlx'..."
    eval "$(conda shell.bash hook)"
    conda activate jlx || echo "⚠️ Could not activate jlx environment, continuing anyway..."
fi

# Run the test script
echo "🚀 Starting test script..."
python "$TEST_SCRIPT" --user-name "$USER_NAME" --user-email "$USER_EMAIL" 