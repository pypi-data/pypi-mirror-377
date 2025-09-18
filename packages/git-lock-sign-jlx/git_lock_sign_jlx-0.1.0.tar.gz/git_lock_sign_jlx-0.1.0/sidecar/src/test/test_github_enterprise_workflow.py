#!/usr/bin/env python3
"""
GitHub Enterprise Sidecar Workflow Test Script

This script:
1. Starts the sidecar server using uvicorn
2. Creates a git repository 
3. Provisions the repository using GitHub Enterprise (creates liuji1031-work repository)
4. Tests git operations (commit and push)

Usage:
    python test_github_enterprise_workflow.py
    
Prerequisites:
- GitHub Enterprise organization with GitHub App configured
- GitHub App credentials in environment (.env.github-enterprise)
- Python dependencies installed (uvicorn, requests, PyGithub, etc.)
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional

import requests

# Add the parent directory to the path to import our services
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitHubEnterpriseSidecarTest:
    """Test runner for GitHub Enterprise sidecar workflow testing."""
    
    def __init__(self, user_name: str = "liuji1031", user_email: str = "liuji1031@live.com", 
                 server_url: str = "http://localhost:8001"):
        self.user_name = user_name
        self.user_email = user_email
        self.server_url = server_url
        self.server_process: Optional[subprocess.Popen] = None
        self.test_repo_path: Optional[str] = None
        
    def setup_environment(self) -> bool:
        """Set up environment variables for GitHub Enterprise testing."""
        logger.info("🔧 Setting up GitHub Enterprise test environment...")
        
        # Load environment from .env.github-enterprise if it exists
        env_file = Path(__file__).parent / ".env.github-enterprise"
        if env_file.exists():
            logger.info(f"📋 Loading environment from {env_file}")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        else:
            logger.warning(f"⚠️ Environment file not found: {env_file}")
        
        # Check required environment variables for GitHub Enterprise
        required_vars = [
            "GITHUB_APP_ID",
            "GITHUB_APP_INSTALLATION_ID", 
            "GITHUB_ENTERPRISE_ORG"
        ]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error("❌ Missing required environment variables:")
            for var in missing_vars:
                logger.error(f"   - {var}")
            logger.error("Please set these variables in .env.github-enterprise file")
            return False
        
        # Set GitHub Enterprise as the git server
        os.environ["GIT_SERVER"] = "github_enterprise"
        
        # Ensure GitHub Enterprise URL is set (fallback to GitHub.com for testing)
        if not os.getenv("GITHUB_ENTERPRISE_URL") and not os.getenv("GIT_SERVER_URL"):
            os.environ["GIT_SERVER_URL"] = "https://github.com"
            logger.info("🔄 Set GIT_SERVER_URL to 'https://github.com' (default)")
        
        # Set git user info for this test
        os.environ["GIT_USER_NAME"] = self.user_name
        os.environ["GIT_USER_EMAIL"] = self.user_email
        
        # GitHub Enterprise specific settings
        os.environ["DEFAULT_REPO_PRIVATE"] = "true"
        os.environ["SINGLE_REPO_PER_USER"] = "true"
        
        logger.info(f"✅ Environment configured for GitHub Enterprise")
        logger.info(f"👤 User: {self.user_name} <{self.user_email}>")
        logger.info(f"🏢 Organization: {os.getenv('GITHUB_ENTERPRISE_ORG')}")
        logger.info(f"🌐 GitHub URL: {os.getenv('GITHUB_ENTERPRISE_URL') or os.getenv('GIT_SERVER_URL')}")
        
        return True
    
    def start_sidecar_server(self) -> bool:
        """Start the sidecar server using uvicorn."""
        logger.info("🚀 Starting sidecar server...")
        
        try:
            # Change to the sidecar directory
            sidecar_dir = Path(__file__).parent.parent.parent
            assert str(sidecar_dir).endswith("sidecar")
            logger.info(f"📁 Working directory: {sidecar_dir}")
            
            # Start uvicorn server
            cmd = [
                "python", "-m", "uvicorn", 
                "src.main:app", 
                "--reload", 
                "--port", "8001",
                "--host", "0.0.0.0"
            ]
            
            logger.info(f"💻 Running command: {' '.join(cmd)}")
            
            self.server_process = subprocess.Popen(
                cmd,
                cwd=sidecar_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for server to start
            logger.info("⏳ Waiting for server to start...")
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=5)
                    if response.status_code == 200:
                        logger.info(f"✅ Server started successfully at {self.server_url}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(2)
                logger.info(f"🔄 Attempt {attempt + 1}/{max_attempts}...")
            
            logger.error("❌ Server failed to start within timeout period")
            self._read_server_output()
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start server: {str(e)}")
            return False
    
    def stop_sidecar_server(self):
        """Stop the sidecar server."""
        if self.server_process:
            logger.info("🛑 Stopping sidecar server...")
            try:
                # Try graceful shutdown first
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.server_process.kill()
                    self.server_process.wait()
                logger.info("✅ Server stopped successfully")
            except Exception as e:
                logger.warning(f"⚠️ Error stopping server: {str(e)}")
    
    def _read_server_output(self):
        """Read and log server output for debugging."""
        if self.server_process and self.server_process.stdout:
            try:
                output = self.server_process.stdout.read()
                if output:
                    logger.info("📋 Server output:")
                    for line in output.split('\n'):
                        if line.strip():
                            logger.info(f"   {line}")
            except Exception as e:
                logger.warning(f"⚠️ Could not read server output: {str(e)}")
    
    def create_test_repository(self) -> bool:
        """Create a temporary git repository for testing."""
        logger.info("📁 Creating test repository...")
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="github_enterprise_test_")
            self.test_repo_path = temp_dir
            repo_path = Path(temp_dir)
            
            logger.info(f"📂 Test repository path: {repo_path}")
            
            # Initialize git repository
            subprocess.run(["git", "init", "-b", "main"], cwd=repo_path, check=True, capture_output=True)
            
            # Configure git user for this repo
            subprocess.run(
                ["git", "config", "user.name", self.user_name], 
                cwd=repo_path, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.email", self.user_email], 
                cwd=repo_path, check=True, capture_output=True
            )
            
            logger.info(f"✅ Git repository initialized with user: {self.user_name} <{self.user_email}>")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create test repository: {str(e)}")
            return False
    
    def make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make an API request to the sidecar server."""
        try:
            url = f"{self.server_url}{endpoint}"
            headers = {"Content-Type": "application/json"}
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.info(f"🌐 {method.upper()} {endpoint} -> HTTP {response.status_code}")
            
            if response.status_code < 400:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json()
                }
            else:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"detail": response.text}
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_data
                }
                
        except Exception as e:
            logger.error(f"❌ API request failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_github_enterprise_test(self) -> bool:
        """Run the complete GitHub Enterprise workflow test."""
        logger.info("🧪 Starting GitHub Enterprise workflow test...")
        
        try:
            # Ensure test_repo_path is set
            if not self.test_repo_path:
                logger.error("❌ Test repository path not set")
                return False
            
            # Step 1: Test git-init
            logger.info("\n📋 Step 1: Initialize git repository")
            test_file_path = os.path.join(self.test_repo_path, "test_notebook.ipynb")
            
            # Create a test notebook file
            test_notebook_content = {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": ["# GitHub Enterprise Test Notebook\n", "\n", "This notebook was created by the GitHub Enterprise test script."]
                    },
                    {
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": ["print('Hello GitHub Enterprise!')\n", "print(f'User: {self.user_name}')\n", "print(f'Email: {self.user_email}')"]
                    }
                ],
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python", 
                        "name": "python3"
                    },
                    "language_info": {
                        "name": "python",
                        "version": "3.11.0"
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 4
            }
            
            with open(test_file_path, 'w') as f:
                json.dump(test_notebook_content, f, indent=2)
            
            logger.info(f"📝 Created test notebook: {test_file_path}")
            
            init_response = self.make_api_request("POST", "/sidecar/git-init", {
                "notebook_path": test_file_path
            })
            
            if not init_response["success"]:
                logger.error(f"❌ Git init failed: {init_response.get('error')}")
                return False
            
            logger.info("✅ Git repository initialized successfully")
            
            # Step 2: Test provision (creates repository in GitHub Enterprise)
            logger.info("\n📋 Step 2: Provision repository in GitHub Enterprise")
            logger.info(f"🎯 Expected repository: {os.getenv('GITHUB_ENTERPRISE_ORG')}/{self.user_name}-work")
            
            provision_response = self.make_api_request("POST", "/sidecar/provision", {
                "notebook_path": test_file_path
            })
            
            if not provision_response["success"]:
                logger.error(f"❌ Repository provisioning failed: {provision_response.get('error')}")
                return False
            
            provision_data = provision_response["data"]
            logger.info("✅ Repository provisioned successfully")
            logger.info(f"🌐 Repository URL: {provision_data.get('repository_url', 'Not provided')}")
            
            # Step 3: Test commit operation
            logger.info("\n📋 Step 3: Commit notebook file")
            commit_response = self.make_api_request("POST", "/sidecar/commit", {
                "notebook_path": test_file_path,
                "message": "Initial commit: GitHub Enterprise test notebook"
            })
            
            if not commit_response["success"]:
                logger.error(f"❌ Commit failed: {commit_response.get('error')}")
                return False
            
            logger.info("✅ File committed successfully")
            
            # Step 4: Test push operation
            logger.info("\n📋 Step 4: Push to GitHub Enterprise")
            push_response = self.make_api_request("POST", "/sidecar/push", {
                "notebook_path": test_file_path,
                "message": "Push GitHub Enterprise test notebook"
            })
            
            if not push_response["success"]:
                logger.error(f"❌ Push failed: {push_response.get('error')}")
                return False
            
            push_data = push_response["data"]
            logger.info("✅ Files pushed successfully")
            logger.info(f"🌐 Repository URL: {push_data.get('repository_url', 'Not provided')}")
            
            # Step 5: Verify repository exists
            logger.info("\n📋 Step 5: Verification")
            repo_url = provision_data.get('repository_url') or push_data.get('repository_url')
            if repo_url:
                logger.info(f"🎉 SUCCESS! Repository created at: {repo_url}")
                logger.info(f"📝 Expected repository name: {self.user_name}-work")
                logger.info(f"🏢 Organization: {os.getenv('GITHUB_ENTERPRISE_ORG')}")
                logger.info("👀 Check the repository in your GitHub organization to verify the notebook was uploaded")
            else:
                logger.warning("⚠️ Repository URL not returned by API")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow test failed: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up test resources."""
        logger.info("🧹 Cleaning up test resources...")
        
        # Remove test repository
        if self.test_repo_path and os.path.exists(self.test_repo_path):
            try:
                import shutil
                shutil.rmtree(self.test_repo_path)
                logger.info(f"🗑️ Removed test repository: {self.test_repo_path}")
            except Exception as e:
                logger.warning(f"⚠️ Could not remove test repository: {str(e)}")
        
        # Stop server
        self.stop_sidecar_server()
    
    async def run_full_test(self) -> bool:
        """Run the complete test workflow."""
        success = False
        
        try:
            # Setup
            if not self.setup_environment():
                return False
            
            if not self.create_test_repository():
                return False
            
            if not self.start_sidecar_server():
                return False
            
            # Run tests
            success = await self.run_github_enterprise_test()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Test interrupted by user")
        except Exception as e:
            logger.error(f"❌ Test failed with error: {str(e)}")
        finally:
            # Always cleanup
            self.cleanup()
        
        return success


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="GitHub Enterprise Sidecar Workflow Test")
    parser.add_argument("--user-name", default="liuji1031", 
                        help="GitHub username (default: liuji1031)")
    parser.add_argument("--user-email", default="liuji1031@live.com",
                        help="User email address (default: liuji1031@live.com)")
    parser.add_argument("--server-url", default="http://localhost:8001",
                        help="Sidecar server URL (default: http://localhost:8001)")
    
    args = parser.parse_args()
    
    # Create and run test
    test_runner = GitHubEnterpriseSidecarTest(
        user_name=args.user_name,
        user_email=args.user_email,
        server_url=args.server_url
    )
    
    logger.info("🚀 GitHub Enterprise Sidecar Workflow Test")
    logger.info("=" * 60)
    
    success = await test_runner.run_full_test()
    
    if success:
        logger.info("\n🎉 All tests passed! GitHub Enterprise integration is working.")
        logger.info("✅ Repository should be available in your GitHub organization")
        sys.exit(0)
    else:
        logger.error("\n💔 Tests failed. Check the logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 