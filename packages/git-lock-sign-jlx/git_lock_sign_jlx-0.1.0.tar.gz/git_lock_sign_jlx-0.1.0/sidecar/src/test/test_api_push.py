#!/usr/bin/env python3
"""
Simple API test to check what the push endpoint returns.
"""

import json
import requests
import tempfile
import subprocess
import os
import time
from pathlib import Path

def test_push_api():
    """Test the push API endpoint directly."""
    
    # Create test environment
    env_file = Path(__file__).parent / ".env.github-enterprise"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Create temporary test repository
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Test directory: {temp_dir}")
        
        # Initialize git repository
        subprocess.run(["git", "init", "-b", "main"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "liuji1031@live.com"], cwd=temp_dir, check=True)
        
        # Create test notebook
        notebook_path = os.path.join(temp_dir, "test.ipynb")
        test_notebook = {
            "cells": [{"cell_type": "code", "source": ["print('API test')"]}],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        with open(notebook_path, 'w') as f:
            json.dump(test_notebook, f)
        
        # Add and commit initial version
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, check=True)
        
        base_url = "http://localhost:8001"
        
        print("📋 Step 1: Git init")
        response = requests.post(f"{base_url}/sidecar/git-init", json={"notebook_path": notebook_path})
        print(f"Git init response: {response.status_code} - {response.json()}")
        
        print("📋 Step 2: Provision")
        response = requests.post(f"{base_url}/sidecar/provision", json={"notebook_path": notebook_path})
        provision_data = response.json()
        print(f"Provision response: {response.status_code}")
        print(f"Provision repository_url: {provision_data.get('repository_url')}")
        
        # Modify the notebook to create changes to commit
        print("📋 Step 2.5: Modify notebook")
        modified_notebook = {
            "cells": [
                {"cell_type": "code", "source": ["print('API test - modified')", "print('New cell added')"]},
                {"cell_type": "markdown", "source": ["# This is a test notebook"]}
            ],
            "metadata": {"test": "modified"},
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        with open(notebook_path, 'w') as f:
            json.dump(modified_notebook, f, indent=2)
        
        print("📋 Step 3: Commit")
        response = requests.post(f"{base_url}/sidecar/commit", json={
            "notebook_path": notebook_path,
            "commit_message": "Test commit with changes"
        })
        commit_data = response.json()
        print(f"Commit response: {response.status_code} - {commit_data}")
        
        if not commit_data.get('success'):
            print("❌ Commit failed, cannot test push")
            return
        
        print("📋 Step 4: Push")
        response = requests.post(f"{base_url}/sidecar/push", json={
            "notebook_path": notebook_path,
            "auto_push": False,
            "auto_commit_before_push": False
        })
        
        push_data = response.json()
        print(f"Push response: {response.status_code}")
        print(f"Push full response: {json.dumps(push_data, indent=2)}")
        print(f"Push repository_url: {push_data.get('repository_url')}")
        
        if push_data.get('repository_url'):
            print(f"✅ SUCCESS! Repository URL returned: {push_data['repository_url']}")
        else:
            print(f"❌ Repository URL still None - {push_data.get('error', 'No error message')}")

if __name__ == "__main__":
    test_push_api() 