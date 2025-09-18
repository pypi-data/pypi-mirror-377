#!/bin/bash
set -e

# Fix permissions for mounted volumes
echo "Fixing permissions for mounted directories..."

# Ensure /tmp/.git-metadata is writable by jovyan user
if [ -d "/tmp/.git-metadata" ] && [ ! -w "/tmp/.git-metadata" ]; then
    echo "Fixing permissions for /tmp/.git-metadata"
    sudo chown -R jovyan:jovyan /tmp/.git-metadata
fi

# Ensure /tmp/work is writable by jovyan user  
if [ -d "/tmp/work" ] && [ ! -w "/tmp/work" ]; then
    echo "Fixing permissions for /tmp/work"
    sudo chown -R jovyan:jovyan /tmp/work
fi

echo "Starting sidecar application..."
exec "$@"
