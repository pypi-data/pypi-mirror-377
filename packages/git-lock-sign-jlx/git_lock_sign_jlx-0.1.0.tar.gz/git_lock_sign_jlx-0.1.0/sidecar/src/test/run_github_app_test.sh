#!/bin/bash
set -e

# Source the .env.github-enterprise file if it exists
if [ -f ".env.github-enterprise" ]; then
  set -a
  source .env.github-enterprise
  set +a
else
  echo "❌ .env.github-enterprise file not found."
  exit 1
fi

# Activate the correct conda environment
if command -v conda >/dev/null 2>&1; then
  eval "$(conda shell.bash hook)"
  conda activate jlx
fi

# Run the GitHub App test script
python3 "$(dirname "$0")/test_github_app.py"
