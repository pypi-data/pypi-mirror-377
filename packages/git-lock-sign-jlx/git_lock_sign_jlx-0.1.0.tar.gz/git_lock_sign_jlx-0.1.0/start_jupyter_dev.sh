#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    # Use set -a to automatically export variables, then source the file
    set -a
    source .env
    set +a
    echo "✅ Environment variables loaded"
else
    echo "⚠️  No .env file found, using hardcoded defaults"
fi


echo "🔧 Environment Configuration:"
echo "   GIT_SERVER: $GIT_SERVER"
echo "   GIT_SERVER_URL: $GIT_SERVER_URL"
echo "   LOG_LEVEL: ${LOG_LEVEL:-INFO}"

# Accept the repo directory as the first argument, or use default if not provided
repo_dir="${1}"
cd "$repo_dir"

# check if conda env jlx is active, if not, activate it
if ! conda env list | grep -q "jlx"; then
    conda init bash
    conda activate jlx
fi

jupyter lab --log-level=INFO --ServerApp.jpserver_extensions="{'git_lock_sign_jlx': True}" --YDocExtension.disable_rtc=True
