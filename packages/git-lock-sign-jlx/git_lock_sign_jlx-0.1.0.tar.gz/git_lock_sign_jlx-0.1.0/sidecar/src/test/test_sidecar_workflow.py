#!/usr/bin/env python3
"""
Comprehensive Sidecar Workflow Test Script

This script:
1. Starts the sidecar server using uvicorn
2. Creates a new user with configurable name and email
3. Initializes a git repository 
4. Provisions the repository using the configured git server
5. Creates a test.txt file with "Hello World"
6. Commits and pushes the file to the remote repository

Usage:
    python test_sidecar_workflow.py --user-name "sidecar-dev-1" --user-email "sidecar-dev-1@test.org"
    
Prerequisites:
- Git server (GitLab or Gitea) running and configured
- Admin token available (set GIT_SERVER_ADMIN_TOKEN environment variable)
- Python dependencies installed (uvicorn, requests, etc.)
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


class SidecarTestRunner:
    """Test runner for sidecar workflow testing."""
    
    def __init__(self, user_name: str, user_email: str, 
                 server_url: str = "http://localhost:8001"):
        self.user_name = user_name
        self.user_email = user_email
        self.server_url = server_url
        self.server_process: Optional[subprocess.Popen] = None
        self.test_repo_path: Optional[str] = None
        
    def setup_environment(self) -> bool:
        """Set up environment variables for the test."""
        logger.info("🔧 Setting up test environment...")
        
        # Check required environment variables
        required_vars = ["GIT_SERVER_ADMIN_TOKEN"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error("❌ Missing required environment variables:")
            for var in missing_vars:
                logger.error(f"   - {var}")
            logger.error("Please set these variables and try again.")
            return False
        
        # Set git server configuration (default to gitea if not specified)
        if not os.getenv("GIT_SERVER"):
            os.environ["GIT_SERVER"] = "gitea"
            logger.info("🔄 Set GIT_SERVER to 'gitea' (default)")
        
        if not os.getenv("GIT_SERVER_URL"):
            os.environ["GIT_SERVER_URL"] = "http://localhost:3000"
            logger.info("🔄 Set GIT_SERVER_URL to 'http://localhost:3000' (default)")
        
        # Set git user info for this test
        os.environ["GIT_USER_NAME"] = self.user_name
        os.environ["GIT_USER_EMAIL"] = self.user_email
        
        # Disable SSL verification for localhost testing
        os.environ["GIT_SSL_VERIFY"] = "false"
        
        logger.info(f"✅ Environment configured for user: {self.user_name} <{self.user_email}>")
        logger.info(f"🌐 Git server: {os.getenv('GIT_SERVER')} at {os.getenv('GIT_SERVER_URL')}")
        
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
            logger.info(f"📁 Working directory: {sidecar_dir}")
            
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
                    response = requests.get(f"{self.server_url}/docs", timeout=5)
                    if response.status_code == 200:
                        logger.info(f"✅ Server started successfully at {self.server_url}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
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
            temp_dir = tempfile.mkdtemp(prefix="sidecar_test_")
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
            
            logger.info("✅ Test repository created and configured")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create test repository: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error creating repository: {str(e)}")
            return False
    
    def cleanup_test_repository(self):
        """Clean up the temporary test repository."""
        if self.test_repo_path:
            try:
                import shutil
                shutil.rmtree(self.test_repo_path)
                logger.info(f"🧹 Cleaned up test repository: {self.test_repo_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup {self.test_repo_path}: {e}")
    
    def make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make an API request to the sidecar server."""
        url = f"{self.server_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
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
    
    async def run_workflow_test(self) -> bool:
        """Run the complete workflow test."""
        logger.info("🧪 Starting sidecar workflow test...")
        
        try:
            # Ensure test_repo_path is set
            if not self.test_repo_path:
                logger.error("❌ Test repository path not set")
                return False
            
            # Step 1: Test git-init
            logger.info("\n📋 Step 1: Initialize git repository")
            test_file_path = os.path.join(self.test_repo_path, "test.txt")
            
            init_response = self.make_api_request("POST", "/sidecar/git-init", {
                "notebook_path": test_file_path
            })
            
            if not init_response["success"]:
                logger.error(f"❌ Git init failed: {init_response.get('error')}")
                return False
            
            logger.info("✅ Git repository initialized successfully")
            
            # Step 2: Test provision
            logger.info("\n📋 Step 2: Provision repository on git server")
            provision_response = self.make_api_request("POST", "/sidecar/provision", {
                "notebook_path": test_file_path
            })
            
            if not provision_response["success"]:
                logger.error(f"❌ Repository provisioning failed: {provision_response.get('error')}")
                return False
            
            repo_data = provision_response["data"]
            logger.info("✅ Repository provisioned successfully")
            if repo_data.get("repository_url"):
                logger.info(f"🌐 Repository URL: {repo_data['repository_url']}")
            
            # Step 3: Create test file
            logger.info("\n📋 Step 3: Create test.txt file")
            with open(test_file_path, 'w') as f:
                f.write("Hello World\n")
            
            logger.info(f"📝 Created {test_file_path} with content: 'Hello World'")
            
            # Step 4: Test commit
            logger.info("\n📋 Step 4: Commit the test file")
            commit_response = self.make_api_request("POST", "/sidecar/commit", {
                "notebook_path": test_file_path,
                "commit_message": f"Add test.txt file - created by {self.user_name}",
                "auto_commit": False
            })
            
            if not commit_response["success"]:
                logger.error(f"❌ Commit failed: {commit_response.get('error')}")
                return False
            
            commit_data = commit_response["data"]
            logger.info("✅ File committed successfully")
            if commit_data.get("commit_hash"):
                logger.info(f"📝 Commit hash: {commit_data['commit_hash']}")
            
            # Step 5: Test push
            logger.info("\n📋 Step 5: Push changes to remote repository")
            push_response = self.make_api_request("POST", "/sidecar/push", {
                "notebook_path": test_file_path,
                "auto_push": False,
                "auto_commit_before_push": False
            })
            
            if not push_response["success"]:
                logger.error(f"❌ Push failed: {push_response.get('error')}")
                return False
            
            push_data = push_response["data"]
            logger.info("✅ Changes pushed successfully")
            if push_data.get("repository_url"):
                logger.info(f"🌐 Repository URL: {push_data['repository_url']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow test failed with exception: {str(e)}")
            return False
    
    async def run_complete_test(self) -> bool:
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
            
            # Run the workflow test
            success = await self.run_workflow_test()
            
        except Exception as e:
            logger.error(f"❌ Test failed with exception: {str(e)}")
            
        finally:
            # Cleanup
            self.stop_sidecar_server()
            self.cleanup_test_repository()
        
        return success


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sidecar Workflow Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_sidecar_workflow.py --user-name "dev-user" --user-email "dev@test.org"
  python test_sidecar_workflow.py -u "sidecar-dev-1" -e "sidecar-dev-1@test.org"
  
Prerequisites:
  - Set GIT_SERVER_ADMIN_TOKEN environment variable
  - Ensure git server (GitLab/Gitea) is running
  - Install required dependencies (uvicorn, requests, etc.)
        """
    )
    
    parser.add_argument(
        "--user-name", "-u",
        required=True,
        help="Git user name (e.g., 'sidecar-dev-1')"
    )
    
    parser.add_argument(
        "--user-email", "-e", 
        required=True,
        help="Git user email (e.g., 'sidecar-dev-1@test.org')"
    )
    
    parser.add_argument(
        "--server-url",
        default="http://localhost:8001",
        help="Sidecar server URL (default: http://localhost:8001)"
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    print("🧪 Sidecar Workflow Test Script")
    print("================================")
    print()
    
    # Parse arguments
    args = parse_arguments()
    
    print("This script will:")
    print("1. 🚀 Start the sidecar server using uvicorn")
    print(f"2. 👤 Create user '{args.user_name}' with email '{args.user_email}'")
    print("3. 📁 Initialize a git repository")
    print("4. 🔧 Provision repository on the configured git server")
    print("5. 📝 Create test.txt file with 'Hello World' content")
    print("6. 💾 Commit the file to git")
    print("7. 📤 Push changes to the remote repository")
    print()
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    required_vars = ["GIT_SERVER_ADMIN_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Please set these variables and try again:")
        print("export GIT_SERVER_ADMIN_TOKEN='your_admin_token_here'")
        return 1
    
    print("✅ All prerequisites satisfied")
    print()
    
    # Create test runner
    test_runner = SidecarTestRunner(
        user_name=args.user_name,
        user_email=args.user_email,
        server_url=args.server_url
    )
    
    # Run the test
    try:
        print("🚀 Starting test execution...")
        success = await test_runner.run_complete_test()
        
        print()
        if success:
            print("🎉 Test completed successfully!")
            print("✅ All workflow steps passed")
            print(f"🌐 Check your git server for the '{args.user_name}/work' repository")
            print("📝 The test.txt file should contain 'Hello World'")
            return 0
        else:
            print("❌ Test failed! Check the logs above for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        test_runner.stop_sidecar_server()
        test_runner.cleanup_test_repository()
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        test_runner.stop_sidecar_server()
        test_runner.cleanup_test_repository()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main())) 