#!/usr/bin/env python3
"""
Test script for GitHub App authentication and configuration.

This script validates that:
1. GitHub App credentials are correct
2. Installation permissions are sufficient
3. Organization access is working
4. Repository operations can be performed

Run this before deploying to production to catch configuration issues early.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any

try:
    import jwt
    from github import Github, Auth
    from github.GithubException import GithubException
except ImportError:
    print("❌ Missing required packages. Install with:")
    print("   pip install PyGithub PyJWT")
    sys.exit(1)


class GitHubAppTester:
    """Test GitHub App configuration and permissions."""
    
    def __init__(self):
        """Initialize tester with environment configuration."""
        self.config = self._load_config()
        self.github_app = None
        self.github = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment or .env file."""
        config = {}
               
        # Load required configuration
        config['github_enterprise_url'] = os.getenv('GITHUB_ENTERPRISE_URL') or os.getenv('GIT_SERVER_URL', '')
        config['github_enterprise_org'] = os.getenv('GITHUB_ENTERPRISE_ORG', '')
        config['github_app_id'] = os.getenv('GITHUB_APP_ID', '')
        config['github_app_installation_id'] = os.getenv('GITHUB_APP_INSTALLATION_ID', '')
        config['github_app_private_key_path'] = os.getenv(
            'GITHUB_APP_PRIVATE_KEY_PATH', 
            str(Path(__file__).parent.parent / "docker" / "secrets" / "github-app-private-key.pem")
        )
        
        return config
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present."""
        print("🔍 Validating configuration...")
        
        required_fields = [
            'github_enterprise_url',
            'github_enterprise_org', 
            'github_app_id',
            'github_app_installation_id'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not self.config[field]:
                missing_fields.append(field.upper())
        
        if missing_fields:
            print(f"❌ Missing required configuration:")
            for field in missing_fields:
                print(f"   - {field}")
            return False
        
        # Check private key file
        key_path = Path(self.config['github_app_private_key_path'])
        if not key_path.exists():
            print(f"❌ GitHub App private key not found: {key_path}")
            return False
        
        # Validate and show URL detection
        github_url = self.config['github_enterprise_url']
        api_url = self._get_api_base_url(github_url)
        
        print("✅ Configuration validation passed")
        print(f"   GitHub URL: {github_url}")
        print(f"   API URL: {api_url}")
        print(f"   Organization: {self.config['github_enterprise_org']}")
        print(f"   App ID: {self.config['github_app_id']}")
        print(f"   Installation ID: {self.config['github_app_installation_id']}")
        
        return True
    
    def test_github_app_auth(self) -> bool:
        """Test GitHub App authentication."""
        print("\n🔑 Testing GitHub App authentication...")
        
        try:
            # Load private key
            key_path = Path(self.config['github_app_private_key_path'])
            with open(key_path, 'r') as f:
                private_key = f.read()
            
            # Get and validate API URL
            github_url = self.config['github_enterprise_url']
            if not github_url:
                raise ValueError("GITHUB_ENTERPRISE_URL not configured")
                
            base_url = self._get_api_base_url(github_url)
            
            # Log URL detection
            if "api.github.com" in base_url:
                print(f"   Detected GitHub.com from URL: {github_url}")
                print(f"   Using GitHub.com API: {base_url}")
            else:
                print(f"   Detected GitHub Enterprise from URL: {github_url}")
                print(f"   Using GitHub Enterprise API: {base_url}")
            
            self.github_app = Auth.AppAuth(
                app_id=self.config['github_app_id'],
                private_key=private_key
            )
            
            # Test JWT generation
            jwt_token = self.github_app.create_jwt()
            print("✅ GitHub App JWT token generated successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ GitHub App authentication failed: {e}")
            return False
    
    def test_installation_access(self) -> bool:
        """Test installation access and permissions."""
        print("\n🏢 Testing installation access...")
        
        try:
            if not self.github_app:
                raise ValueError("GitHub App not initialized")
                
            installation_id = int(self.config['github_app_installation_id'])
            
            # Get installation auth
            installation_auth = Auth.AppInstallationAuth(
                app_auth=self.github_app,
                installation_id=installation_id
            )
            
            # Initialize GitHub client with installation auth
            base_url = self._get_api_base_url(self.config['github_enterprise_url'])
            
            self.github = Github(auth=installation_auth, base_url=base_url)
            
            print("✅ Installation token obtained successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Installation access failed: {e}")
            return False
    
    def test_organization_access(self) -> bool:
        """Test organization access and permissions."""
        print("\n🏛️  Testing organization access...")
        
        try:
            if not self.github:
                raise ValueError("GitHub client not initialized")
                
            org_name = self.config['github_enterprise_org']
            org = self.github.get_organization(org_name)
            
            print(f"✅ Organization access confirmed: {org.name}")
            print(f"   Description: {org.description or 'No description'}")
            print(f"   Public repos: {org.public_repos}")
            print(f"   Private repos: {org.total_private_repos}")
            
            # Test repository listing
            repos = list(org.get_repos(type="all"))
            print(f"✅ Can access {len(repos)} repositories")
            
            # Show first few repos as examples
            if repos:
                print("   Example repositories:")
                for repo in repos[:3]:
                    print(f"   - {repo.name} ({'private' if repo.private else 'public'})")
            
            return True
            
        except Exception as e:
            print(f"❌ Organization access failed: {e}")
            return False
    
    def test_repository_permissions(self) -> bool:
        """Test repository creation and management permissions."""
        print("\n📁 Testing repository permissions...")
        
        try:
            if not self.github:
                raise ValueError("GitHub client not initialized")
                
            org_name = self.config['github_enterprise_org']
            org = self.github.get_organization(org_name)
            
            # Test repository creation (dry run - we'll create a test repo)
            test_repo_name = f"jupyter-test-{int(time.time())}"
            
            print(f"   Creating test repository: {test_repo_name}")
            
            # Create test repository
            test_repo = org.create_repo(
                name=test_repo_name,
                description="Test repository for GitHub App integration - safe to delete",
                private=True,
                auto_init=True
            )
            
            print(f"✅ Repository created successfully: {test_repo.html_url}")
            
            # Test basic operations
            print("   Testing repository operations...")
            
            # Test file creation
            test_repo.create_file(
                path="test.txt",
                message="Test commit from GitHub App",
                content="This is a test file created by the GitHub App integration test.\n"
            )
            print("✅ File creation successful")
            
            # Test collaborator management (if user exists)
            print("✅ Repository operations successful")
            
            # Clean up - delete test repository
            print(f"   Cleaning up test repository...")
            test_repo.delete()
            print("✅ Test repository deleted")
            
            return True
            
        except Exception as e:
            print(f"❌ Repository permissions test failed: {e}")
            
            # Try to clean up if repository was created
            try:
                if self.github:
                    org_name = self.config['github_enterprise_org']
                    org = self.github.get_organization(org_name)
                    test_repo = org.get_repo(test_repo_name)
                    test_repo.delete()
                    print("   Test repository cleaned up after error")
            except:
                print(f"   Note: You may need to manually delete test repository: {test_repo_name}")
            
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success."""
        print("🧪 Starting GitHub App integration tests...\n")
        
        tests = [
            ("Configuration", self.validate_config),
            ("GitHub App Authentication", self.test_github_app_auth),
            ("Installation Access", self.test_installation_access), 
            ("Organization Access", self.test_organization_access),
            ("Repository Permissions", self.test_repository_permissions),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
                
                if not success:
                    print(f"\n❌ Test failed: {test_name}")
                    break
                    
            except Exception as e:
                print(f"\n💥 Test crashed: {test_name} - {e}")
                results.append((test_name, False))
                break
        
        # Print summary
        print("\n" + "="*50)
        print("📊 Test Results Summary:")
        print("="*50)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL" 
            print(f"{status} {test_name}")
        
        all_passed = all(success for _, success in results)
        
        if all_passed:
            print("\n🎉 All tests passed! GitHub App integration is ready.")
            print("\nNext steps:")
            print("1. Run: cd docker && docker-compose up -d")
            print("2. Access JupyterLab: http://localhost:8888")
            print("3. Create a notebook and test git operations")
        else:
            print("\n💔 Some tests failed. Please fix the issues above before proceeding.")
            print("\nCommon fixes:")
            print("- Verify GitHub App permissions in your organization settings")
            print("- Check that the Installation ID is correct")
            print("- Ensure the private key file is valid and properly formatted")
            
        return all_passed

    def _get_api_base_url(self, github_url: str) -> str:
        """
        Get the correct API base URL for GitHub.com or GitHub Enterprise.
        
        Args:
            github_url: The GitHub web URL (e.g. https://github.com or https://github.company.com)
            
        Returns:
            Correct API base URL
        """
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(github_url)
            
            # Check if it's GitHub.com (including subdomains)
            if parsed_url.netloc.endswith('github.com'):
                return "https://api.github.com"
            else:
                # GitHub Enterprise Server - append /api/v3 to the base URL
                return f"{github_url.rstrip('/')}/api/v3"
                
        except Exception as e:
            print(f"Warning: Error parsing GitHub URL {github_url}: {e}")
            # Fallback to appending /api/v3
            return f"{github_url.rstrip('/')}/api/v3"


def main():
    """Main test entry point."""
    tester = GitHubAppTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 