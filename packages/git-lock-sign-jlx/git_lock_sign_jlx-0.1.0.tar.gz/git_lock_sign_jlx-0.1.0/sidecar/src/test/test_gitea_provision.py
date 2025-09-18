#!/usr/bin/env python3
"""
Test script for Gitea service provisioning.

This script:
1. Provisions a new user (dev1) with email dev1@test.org
2. Creates a new repository under the user
3. Creates a test.txt file and pushes it to the remote

Prerequisites:
- Gitea server running at http://localhost:3000
- Admin token available (set GIT_SERVER_ADMIN_TOKEN environment variable)
"""

import asyncio
import logging
import os
import subprocess
import tempfile
from pathlib import Path

# Add the parent directory to the path to import our services
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.config_service import ConfigService
from services.provider_services import GiteaService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_test_environment():
    """Set up environment variables for the test."""
    # Set Gitea configuration
    os.environ["GIT_SERVER"] = "gitea"
    os.environ["GIT_SERVER_URL"] = "http://localhost:3000"
    
    # Check if admin token is set
    if not os.getenv("GIT_SERVER_ADMIN_TOKEN"):
        print("❌ ERROR: GIT_SERVER_ADMIN_TOKEN environment variable must be set!")
        print("   Get the admin token from your Gitea server and set it like:")
        print("   export GIT_SERVER_ADMIN_TOKEN='your_admin_token_here'")
        return False
    
    # Override git user info for this test
    os.environ["GIT_USER_NAME"] = "dev3"
    os.environ["GIT_USER_EMAIL"] = "dev3@test.org"
    
    # Disable SSL verification for localhost
    os.environ["GIT_SSL_VERIFY"] = "false"
    
    return True


def create_test_repository():
    """Create a temporary git repository with a test file."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="gitea_test_")
    repo_path = Path(temp_dir)
    
    logger.info(f"📁 Creating test repository in: {repo_path}")
    
    try:
        # Initialize git repository with main branch
        subprocess.run(["git", "init", "-b", "main"], cwd=repo_path, check=True)
        
        # Configure git user for this repo
        subprocess.run(
            ["git", "config", "user.name", "dev1"],
            cwd=repo_path,
            check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "dev1@test.org"],
            cwd=repo_path,
            check=True
        )
        
        # Create test.txt file
        test_file = repo_path / "test.txt"
        test_file.write_text("hello world!")
        
        logger.info(f"📝 Created test.txt with content: {test_file.read_text()}")
        
        # Add and commit the file
        subprocess.run(["git", "add", "test.txt"], cwd=repo_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit with test.txt"],
            cwd=repo_path,
            check=True
        )
        
        logger.info("✅ Repository created and file committed successfully")
        return str(repo_path)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to create test repository: {e}")
        return None


async def test_gitea_provisioning():
    """Main test function."""
    logger.info("🚀 Starting Gitea provisioning test...")
    
    # Set up environment
    if not setup_test_environment():
        return False
    
    # Create config service
    config = ConfigService()
    
    # Validate configuration
    is_valid, errors = config._validate_config()
    if not is_valid:
        logger.error(f"❌ Configuration errors: {errors}")
        return False
    
    logger.info(f"✅ Configuration valid. Server: {config.git_server_url}")
    
    # Create Gitea service
    gitea_service = GiteaService(config)
    
    # Create test repository
    repo_path = create_test_repository()
    if not repo_path:
        return False
    
    try:
        # Step 1: Provision user and repository
        logger.info("👤 Step 1: Provisioning user and repository...")
        
        setup_result = await gitea_service.setup_repository(repo_path)
        
        if not setup_result.success:
            logger.error(f"❌ Failed to setup repository: {setup_result.error}")
            return False
        
        logger.info("✅ User and repository provisioned successfully!")
        logger.info(f"🌐 Repository URL: {setup_result.repository_url}")
        
        # Step 2: Push the test file
        logger.info("📤 Step 2: Pushing test file to remote...")
        
        test_file_path = os.path.join(repo_path, "test.txt")
        push_result = await gitea_service.push_notebook(test_file_path)
        
        if not push_result.success:
            logger.error(f"❌ Failed to push file: {push_result.error}")
            return False
        
        logger.info("✅ Test file pushed successfully!")
        logger.info(f"🌐 Repository URL: {push_result.repository_url}")
        logger.info(f"📋 You can view the repository at: {push_result.repository_url}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {str(e)}")
        return False
    
    finally:
        # Cleanup temporary directory
        try:
            import shutil
            shutil.rmtree(repo_path)
            logger.info(f"🧹 Cleaned up temporary directory: {repo_path}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to cleanup {repo_path}: {e}")


def main():
    """Main entry point."""
    print("🧪 Gitea Service Test Script")
    print("============================")
    print()
    print("This script will:")
    print("1. 👤 Provision user 'dev1' with email 'dev1@test.org'")
    print("2. 📁 Create a repository under the user")
    print("3. 📝 Create a test.txt file with 'hello world!' content")
    print("4. 📤 Push the file to the Gitea repository")
    print()
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    if not os.getenv("GIT_SERVER_ADMIN_TOKEN"):
        print("❌ ERROR: GIT_SERVER_ADMIN_TOKEN not set!")
        print()
        print("To get the admin token:")
        print("1. Login to Gitea at http://localhost:3000")
        print("2. Go to Settings > Applications > Generate New Token")
        print("3. Set the token: export GIT_SERVER_ADMIN_TOKEN='your_token_here'")
        return 1
    
    print("✅ Admin token is set")
    print()
    
    # Run the test
    try:
        result = asyncio.run(test_gitea_provisioning())
        
        if result:
            print()
            print("🎉 Test completed successfully!")
            print("🌐 Check your Gitea server at http://localhost:3000")
            print("📁 Look for the 'dev1/work' repository")
            print("📝 The test.txt file should contain 'hello world!'")
            return 0
        else:
            print()
            print("❌ Test failed! Check the logs above for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main()) 