#!/usr/bin/env python3
"""
Simple test script to debug GitHub Enterprise push operation.
"""

import asyncio
import logging
import os
import sys
import tempfile
import json
import subprocess
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.config_service import ConfigService
from services.provider_services import GitHubEnterpriseService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_push_debug():
    """Test the push operation with debug output."""
    try:
        # Load environment
        env_file = Path(__file__).parent / ".env.github-enterprise"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        logger.info("🔧 Initializing services...")
        config_service = ConfigService()
        github_service = GitHubEnterpriseService(config_service)
        
        # Create a temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"📁 Test directory: {temp_dir}")
            
            # Initialize git repository
            subprocess.run(["git", "init"], cwd=temp_dir, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
            subprocess.run(["git", "config", "user.email", "liuji1031@live.com"], cwd=temp_dir, check=True)
            
            # Create a test notebook
            notebook_path = os.path.join(temp_dir, "test.ipynb")
            test_notebook = {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": ["print('Hello from debug test!')"],
                        "metadata": {},
                        "outputs": [],
                        "execution_count": None
                    }
                ],
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 4
            }
            
            with open(notebook_path, 'w') as f:
                json.dump(test_notebook, f, indent=2)
            
            logger.info(f"📝 Created test notebook: {notebook_path}")
            
            # Add and commit the file
            subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, check=True)
            
            logger.info("📋 Step 1: Setup repository")
            setup_result = await github_service.setup_repository(temp_dir)
            logger.info(f"Setup result: success={setup_result.success}, repo_url={setup_result.repository_url}")
            
            if not setup_result.success:
                logger.error(f"Setup failed: {setup_result.error}")
                return
            
            logger.info("📋 Step 2: Push notebook")
            push_result = await github_service.push_notebook(notebook_path)
            logger.info(f"Push result: success={push_result.success}, repo_url={push_result.repository_url}")
            
            if not push_result.success:
                logger.error(f"Push failed: {push_result.error}")
            else:
                logger.info("✅ Push completed successfully!")
                
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_push_debug()) 