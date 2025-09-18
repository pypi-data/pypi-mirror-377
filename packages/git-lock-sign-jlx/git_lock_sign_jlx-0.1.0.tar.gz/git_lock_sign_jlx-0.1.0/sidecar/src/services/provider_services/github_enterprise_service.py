"""Service for GitHub Enterprise remote repository operations.

This service handles GitHub Enterprise-specific operations like user provisioning
and repository creation, while delegating all git operations to GitService.
"""

import logging
import os
import re
import time
from typing import Any, Dict, Optional, TYPE_CHECKING
from urllib.parse import urlparse, urlunparse

from github import Github, GithubIntegration, Auth
from github.GithubException import GithubException

from ..config_service import ConfigService
from ..logger_util import default_logger_config
from .provider_service import ProviderService, ProviderSetupResult

from ..git_service.models import NotebookPushResult

if TYPE_CHECKING:
    from ..git_service import GitService

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitHubEnterpriseService(ProviderService):
    """Service for managing GitHub Enterprise remote repository operations."""

    def __init__(self, config_service: ConfigService, git_service: "GitService"):
        """Initialize the GitHub Enterprise service."""
        super().__init__(config_service, git_service)
        self._github_app = None  # Lazy initialization
        self._installation_token_cache = {}  # Cache installation tokens

    @property
    def github_app(self) -> GithubIntegration:
        """Get GitHub App integration with lazy initialization."""
        if self._github_app is None:
            self._github_app = self._init_github_app()
        return self._github_app

    def _get_api_base_url(self, github_url: str) -> str:
        """
        Get the correct API base URL for GitHub.com or GitHub Enterprise.
        
        Args:
            github_url: The GitHub web URL (e.g. https://github.com or https://github.company.com)
            
        Returns:
            Correct API base URL
        """
        try:
            parsed_url = urlparse(github_url)
            
            # Check if it's GitHub.com (including subdomains)
            if parsed_url.netloc.endswith('github.com'):
                return "https://api.github.com"
            else:
                # GitHub Enterprise Server - append /api/v3 to the base URL
                return f"{github_url.rstrip('/')}/api/v3"
                
        except Exception as e:
            logger.warning("Error parsing GitHub URL %s: %s", github_url, e)
            # Fallback to appending /api/v3
            return f"{github_url.rstrip('/')}/api/v3"

    def _init_github_app(self) -> GithubIntegration:
        """Initialize GitHub App integration."""
        try:
            private_key_path = self.config_service.github_app_private_key_path
            if private_key_path is None:
                logger.error("GitHub App private key not found: %s", private_key_path)
                raise FileNotFoundError("GitHub App private key not found")
            
            if not os.path.exists(private_key_path):
                raise FileNotFoundError(f"GitHub App private key not found: {private_key_path}")

            with open(private_key_path, 'r') as key_file:
                private_key = key_file.read()

            # Validate GitHub Enterprise URL
            if not self.config_service.github_enterprise_url:
                raise ValueError("GitHub Enterprise URL not configured")
            
            # Get correct API URL based on GitHub type
            base_url = self._get_api_base_url(self.config_service.github_enterprise_url)
            
            # Log GitHub type detection
            if "api.github.com" in base_url:
                logger.info(f"Detected GitHub.com, using API URL: {base_url}")
            else:
                logger.info(f"Detected GitHub Enterprise, using API URL: {base_url}")

            return GithubIntegration(
                integration_id=self.config_service.github_app_id,
                private_key=private_key,
                base_url=base_url
            )
        except Exception as e:
            logger.error(f"Failed to initialize GitHub App: {e}")
            raise

    def _get_installation_token(self) -> str:
        """Get GitHub App installation token."""
        try:
            installation_id = self.config_service.github_app_installation_id
            if installation_id is None:
                logger.error("GitHub App installation ID not set")
                raise ValueError("GitHub App installation ID not set")
            
            # Check if we have a cached token that's still valid
            cache_key = f"installation_{installation_id}"
            if cache_key in self._installation_token_cache:
                token_info = self._installation_token_cache[cache_key]
                # Check if token expires in more than 5 minutes
                if token_info["expires_at"] > time.time() + 300:
                    return token_info["token"]

            # Get new installation token
            token = self.github_app.get_access_token(installation_id)
            
            # Cache the token (GitHub App tokens expire after 1 hour)
            self._installation_token_cache[cache_key] = {
                "token": token.token,
                "expires_at": time.time() + 3600  # 1 hour
            }
            
            return token.token
        except Exception as e:
            logger.error(f"Failed to get installation token: {e}")
            raise

    def check_user_registration(self, user_email: str) -> bool:
        """
        Check if a user is already registered in GitHub Enterprise organization.
        
        Args:
            user_email: User email to check
            
        Returns:
            True if user exists in the organization, False otherwise
        """
        try:
            # Resolve GitHub username from email
            github_user = self._resolve_github_user(user_email)
            
            if not github_user:
                logger.info("Could not resolve GitHub username for email: %s", user_email)
                return False
            
            # Get organization name
            org_name = self.config_service.github_enterprise_org
            
            if not org_name:
                logger.warning("GitHub Enterprise organization not configured - cannot check user registration")
                return False
            
            # Get installation token
            token = self._get_installation_token()
            
            # Create GitHub instance with installation token
            github_url = self.config_service.github_enterprise_url
            if not github_url:
                logger.warning("GitHub Enterprise URL not configured - cannot check user registration")
                return False
                
            api_base_url = self._get_api_base_url(github_url)
            
            g = Github(base_url=api_base_url, login_or_token=token)
            
            # Get organization
            org = g.get_organization(org_name)
            
            # Check if user is member of organization
            try:
                # Use get_members() to check if user is in the organization
                members = org.get_members()
                for member in members:
                    if member.login == github_user:
                        logger.info(f"User '{github_user}' is a member of GitHub Enterprise organization '{org_name}'")
                        return True
                
                logger.info(f"User '{github_user}' is not a member of GitHub Enterprise organization '{org_name}'")
                return False
                
            except Exception as e:
                # User is not a member or we don't have permission
                logger.info(f"User '{github_user}' is not a member of GitHub Enterprise organization '{org_name}' or permission denied: {str(e)}")
                return False
                
        except Exception as e:
            logger.warning(f"Failed to check if user {user_email} is registered in GitHub Enterprise: {str(e)}")
            return False

    async def get_fresh_push_url_for_sync(self, repo_path: str) -> Optional[str]:
        """
        Generate a fresh push URL with updated token for session sync operations.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            Fresh push URL with updated token, or None if failed
        """
        try:
            logger.info("🔄 Generating fresh push URL for session sync...")
            
            # Get git user info from the repository
            user_info = self._get_git_user_info(repo_path)
            if not user_info["name"] or not user_info["email"]:
                logger.error("Git user name and email must be configured")
                return None
            
            # Resolve GitHub username from email
            github_user = self._resolve_github_user(user_info["email"])
            if not github_user:
                logger.error(f"Could not resolve GitHub username for email: {user_info['email']}")
                return None
            
            # Determine repository name (should match existing repository)
            repo_name = (
                "work"
                if self.config_service.single_repo_per_user
                else repo_path.split("/")[-1]
            )
            
            # Get fresh installation token
            token = self._get_installation_token()
            
            # Get organization name
            org_name = self.config_service.github_enterprise_org
            github_url = self.config_service.github_enterprise_url
            
            if not org_name or not github_url:
                logger.error("GitHub Enterprise organization or URL not configured")
                return None
            
            # Build fresh push URL
            parsed_url = urlparse(github_url)
            if parsed_url.netloc.endswith('github.com'):
                # GitHub.com
                push_url = f"https://x-access-token:{token}@github.com/{org_name}/{github_user}-{repo_name}.git"
            else:
                # GitHub Enterprise Server
                push_url = f"https://x-access-token:{token}@{parsed_url.netloc}/{org_name}/{github_user}-{repo_name}.git"
            
            logger.info("✅ Generated fresh push URL for session sync")
            return push_url
            
        except Exception as e:
            logger.error(f"Failed to generate fresh push URL for sync: {str(e)}")
            return None

    async def setup_repository(self, repo_path: str) -> ProviderSetupResult:
        """
        Set up GitHub Enterprise repository by creating repository via GitHub App.

        Args:
            repo_path: Path to the git repository

        Returns:
            ProviderSetupResult with setup details
        """
        try:
            logger.info("Setting up GitHub Enterprise repository for: %s", repo_path)

            # Get git user info from the repository
            user_info = self._get_git_user_info(repo_path)
            if not user_info["name"] or not user_info["email"]:
                return ProviderSetupResult(
                    success=False,
                    error="Git user name and email must be configured",
                )

            # Determine repository name
            repo_name = (
                "work"
                if self.config_service.single_repo_per_user
                else repo_path.split("/")[-1]
            )

            # Resolve GitHub username from email
            github_user = self._resolve_github_user(user_info["email"])
            if not github_user:
                return ProviderSetupResult(
                    success=False,
                    error=f"Could not resolve GitHub username for email: {user_info['email']}",
                )

            # Create repository in organization
            provision_result = self._create_repository(github_user, repo_name, user_info)

            if not provision_result["success"]:
                return ProviderSetupResult(
                    success=False, error=provision_result["error"]
                )

            # Cache the push URL and repository URL for this repository
            self._push_url_cache[repo_path] = provision_result["push_url"]
            self._push_url_cache[f"{repo_path}_repo_url"] = provision_result.get("repo_url")

            logger.info("GitHub Enterprise repository setup completed for: %s", repo_path)

            # Log the repository URL for user reference
            if provision_result.get("repo_url"):
                logger.info("🌐 Repository URL: %s", provision_result["repo_url"])

            return ProviderSetupResult(
                success=True,
                repository_url=provision_result.get("repo_url"),
                push_url=provision_result["push_url"]
            )

        except Exception as e:
            logger.error("Error setting up GitHub Enterprise repository: %s", str(e))
            return ProviderSetupResult(
                success=False,
                error=f"Repository setup failed: {str(e)}"
            )

    def _resolve_github_user(self, email: str) -> Optional[str]:
        """
        Resolve GitHub username from email address and verify organization membership.
        
        Args:
            email: User email address
            
        Returns:
            GitHub username if found and verified as organization member, None otherwise
        """
        try:
            # Validate domain if configured
            if hasattr(self.config_service, 'allowed_domains') and self.config_service.allowed_domains:
                domain = email.split("@")[-1].lower()
                allowed_domains = [d.strip().lower() for d in self.config_service.allowed_domains.split(",") if d.strip()]
                if allowed_domains and domain not in allowed_domains:
                    logger.warning(f"Email domain {domain} not in allowed domains")
                    return None
            
            # Try to find organization member by email address
            github_username = self._find_organization_member_by_email(email)
            if github_username:
                logger.info(f"✅ Verified GitHub username: {github_username} for email: {email}")
                return github_username
            
            logger.warning(f"❌ No organization member found with email: {email}")
            return None
            
        except Exception as e:
            logger.error(f"Error resolving GitHub username: {e}")
            return None

    def _find_organization_member_by_email(self, email: str) -> Optional[str]:
        """
        Find organization member by email address.
        
        Uses the following search priority:
        1. GIT_USER_NAME environment variable (most reliable)
        2. Username extracted from email (fallback)
        3. GitHub API email search (least reliable)
        
        Args:
            email: Email address to search for
            
        Returns:
            GitHub username if found as organization member, None otherwise
        """
        try:
            token = self._get_installation_token()
            api_base_url = self._get_api_base_url(self.config_service.github_enterprise_url) if self.config_service.github_enterprise_url else None
            if not api_base_url:
                logger.error("Could not determine GitHub API URL")
                return None
                
            github = Github(auth=Auth.Token(token), base_url=api_base_url)
            
            if not self.config_service.github_enterprise_org:
                logger.error("GitHub Enterprise organization not configured")
                return None
            
            org = github.get_organization(self.config_service.github_enterprise_org)
            
            logger.info(f"🔍 Searching for organization member with email: {email}")
            
            # Method 1: Check GIT_USER_NAME environment variable (most reliable)
            git_user_name = self.config_service.git_user_name
            if git_user_name and git_user_name != "NOT_SET":
                logger.info(f"🔍 Checking configured GIT_USER_NAME: {git_user_name}")
                
                # Try to find user by the configured git username
                if self._verify_organization_membership(git_user_name):
                    logger.info(f"✅ Found organization member using GIT_USER_NAME: {git_user_name}")
                    return git_user_name
                else:
                    logger.info(f"⚠️ GIT_USER_NAME '{git_user_name}' is not a member of organization '{self.config_service.github_enterprise_org}'")
            else:
                logger.info("🔍 GIT_USER_NAME not configured, skipping git username check")
            
            # Method 2: Username extraction from email (reliable fallback)
            username_from_email = email.split("@")[0]
            github_username = re.sub(r'[^a-zA-Z0-9\-]', '-', username_from_email.lower())
            
            logger.info(f"🔍 Trying username extracted from email: {github_username}")
            
            # Verify this user exists and is organization member
            if self._verify_organization_membership(github_username):
                logger.info(f"✅ Found organization member using email username: {github_username}")
                return github_username
            else:
                logger.info(f"⚠️ Email username '{github_username}' is not a member of organization")

            # Method 3: Search through organization members by email (limited by privacy)
            try:
                members = org.get_members()
                for member in members:
                    # Check if member has public email that matches
                    if member.email and member.email.lower() == email.lower():
                        logger.info(f"✅ Found organization member by public email: {member.login} ({member.email})")
                        return member.login
                        
                logger.info("No member found with matching public email")
                
            except Exception as e:
                logger.warning(f"Could not iterate organization members: {e}")
            
            # Method 4: GitHub API user search (least reliable due to privacy settings)
            try:
                logger.info(f"🔍 Trying GitHub API search as last resort")
                
                # Try multiple search strategies
                search_queries = [
                    f"in:email {email}",
                    f'"{email}"',
                    email.split("@")[0],  # Search by username part
                    f"email:{email}",  # Alternative search syntax
                    f"user:{email.split('@')[0]}",  # Search by username
                    f"in:name {email.split('@')[0]}",  # Search by name
                    f"in:email *@{email.split('@')[1]}",  # Search by email domain
                ]
                
                # Collect all potential users from all search queries
                all_potential_users = set()
                
                for query in search_queries:
                    try:
                        logger.info(f"🔍 Trying search query: {query}")
                        search_results = github.search_users(query)
                        
                        results_list = list(search_results)
                        logger.info(f"🔍 Search query '{query}' returned {len(results_list)} results")
                        
                        for user in results_list:
                            logger.info(f"🔍 Found user via search: {user.login} ({user.name or 'No name'})")
                            all_potential_users.add(user.login)
                            
                    except Exception as e:
                        logger.warning(f"Search query '{query}' failed: {e}")
                        continue
                
                # Check all potential users for organization membership
                logger.info(f"🔍 Checking {len(all_potential_users)} potential users for organization membership")
                
                for username in all_potential_users:
                    if self._verify_organization_membership(username):
                        logger.info("✅ Found organization member via GitHub API search: %s", username)
                        logger.warning("⚠️ WARNING: Using GitHub API search result '%s', but GIT_USER_NAME configuration is recommended for reliability", username)
                        return username
                        
            except Exception:
                logger.warning("GitHub API user search failed")
            
            logger.warning("❌ Could not find organization member with email: %s", email)
            logger.info("📋 Search summary for email '%s':", email)
            logger.info("   - GIT_USER_NAME check: %s", 'Not configured' if not git_user_name or git_user_name == 'NOT_SET' else 'Failed (not a member)')
            logger.info("   - Email username extraction: Failed ('%s' not a member)", github_username)
            logger.info("   - Organization member email search: Failed (emails likely private)")
            logger.info("   - GitHub API user search: Failed (no matching organization members)")
            logger.info("💡 RECOMMENDATION: Set GIT_USER_NAME environment variable to the correct GitHub username")
            return None
            
        except Exception as e:
            logger.error("Error finding organization member by email: %s", e)
            return None

    def _verify_organization_membership(self, github_username: str) -> bool:
        """
        Verify that the GitHub user is a member of the organization.
        
        Args:
            github_username: GitHub username to verify
            
        Returns:
            True if user is organization member, False otherwise
        """
        try:
            token = self._get_installation_token()
            api_base_url = self._get_api_base_url(self.config_service.github_enterprise_url) if self.config_service.github_enterprise_url else None
            if not api_base_url:
                logger.error("Could not determine GitHub API URL")
                return False
                
            github = Github(auth=Auth.Token(token), base_url=api_base_url)
            
            if not self.config_service.github_enterprise_org:
                logger.error("GitHub Enterprise organization not configured")
                return False
            
            org = github.get_organization(self.config_service.github_enterprise_org)
            
            # Check if GitHub user exists
            try:
                user = github.get_user(github_username)
                logger.info(f"🔍 Found GitHub user: {user.login} ({user.name or 'No name'})")
            except GithubException as e:
                if e.status == 404:
                    logger.warning(f"❌ GitHub user '{github_username}' does not exist")
                    return False
                else:
                    logger.error(f"❌ Error fetching user '{github_username}': {e}")
                    return False
            
            # Check organization membership by iterating through members
            try:
                # Get all organization members and check if our user is among them
                members = org.get_members()
                for member in members:
                    if member.login.lower() == github_username.lower():
                        logger.info(f"✅ User '{github_username}' is a member of organization '{self.config_service.github_enterprise_org}'")
                        return True
                
                logger.warning(f"❌ User '{github_username}' is not a member of organization '{self.config_service.github_enterprise_org}'")
                return False
                    
            except GithubException as e:
                # Fallback: Check public membership if private membership check fails
                logger.info(f"⚠️ Cannot check private membership for '{github_username}', checking public membership")
                return self._check_public_membership(org, github_username)
                    
        except Exception as e:
            logger.error(f"❌ Error verifying organization membership: {e}")
            return False

    def _check_public_membership(self, org, github_username: str) -> bool:
        """
        Check if user is a public member of the organization (fallback method).
        
        Args:
            org: GitHub organization object
            github_username: GitHub username to check
            
        Returns:
            True if user is a public member, False otherwise
        """
        try:
            # Get public members (this is always allowed)
            public_members = org.get_public_members()
            for member in public_members:
                if member.login.lower() == github_username.lower():
                    logger.info(f"✅ User '{github_username}' found in public members of organization")
                    return True
            
            logger.warning(f"❌ User '{github_username}' not found in public members")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking public membership: {e}")
            return False

    def _create_repository(self, github_user: str, repo_name: str, user_info: Dict) -> Dict[str, Any]:
        """
        Create repository in GitHub Enterprise organization.
        
        Args:
            github_user: GitHub username
            repo_name: Repository name
            user_info: User information dictionary
            
        Returns:
            Dictionary with creation results
        """
        try:
            token = self._get_installation_token()
            
            # Get correct API URL
            api_base_url = self._get_api_base_url(self.config_service.github_enterprise_url) if self.config_service.github_enterprise_url else None
            if not api_base_url:
                raise ValueError("Could not determine GitHub API URL")
                
            github = Github(auth=Auth.Token(token), base_url=api_base_url)
            
            if not self.config_service.github_enterprise_org:
                raise ValueError("GitHub Enterprise organization not configured")
            
            org = github.get_organization(self.config_service.github_enterprise_org)
            
            # Generate unique repository name
            full_repo_name = f"{github_user}-{repo_name}"
            
            # Check if repository already exists
            try:
                existing_repo = org.get_repo(full_repo_name)
                logger.info(f"Repository {full_repo_name} already exists")
                
                # Return existing repository information
                return {
                    "success": True,
                    "repo_url": existing_repo.html_url,
                    "push_url": self._generate_push_url(existing_repo, token),
                    "clone_url": existing_repo.clone_url,
                    "existing": True
                }
            except GithubException as e:
                if e.status != 404:
                    raise e
                # Repository doesn't exist, proceed with creation
            
            # Create repository
            repo_data = {
                "name": full_repo_name,
                "description": f"Jupyter workspace for {user_info['name']} ({user_info['email']})",
                "private": self.config_service.default_repo_private,
                "auto_init": True,  # Initialize with README
                "gitignore_template": "Python",  # Add Python gitignore
            }
            
            # Use template if configured
            if self.config_service.repo_template:
                try:
                    template_repo = org.get_repo(self.config_service.repo_template)
                    repo = template_repo.create_fork(
                        organization=org,
                        name=full_repo_name
                    )
                    # Update description after fork
                    repo.edit(description=repo_data["description"], private=repo_data["private"])
                    logger.info(f"Created repository from template: {full_repo_name}")
                except GithubException as e:
                    logger.warning(f"Could not use template {self.config_service.repo_template}: {e}")
                    repo = org.create_repo(**repo_data)
                    logger.info(f"Created repository without template: {full_repo_name}")
            else:
                repo = org.create_repo(**repo_data)
                logger.info(f"Created repository: {full_repo_name}")
            
            # Add user as collaborator with admin permissions
            try:
                # Add collaborator using username string
                repo.add_to_collaborators(github_user, permission="admin")
                logger.info(f"Added {github_user} as admin collaborator")
            except GithubException as e:
                logger.warning(f"Could not add {github_user} as collaborator: {e}")
                # This is not a fatal error - repository is still created
            
            return {
                "success": True,
                "repo_url": repo.html_url,
                "push_url": self._generate_push_url(repo, token),
                "clone_url": repo.clone_url,
                "existing": False
            }
            
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            return {
                "success": False,
                "error": f"Repository creation failed: {str(e)}"
            }

    def _generate_push_url(self, repo, token: str) -> str:
        """
        Generate push URL with embedded token.
        
        Args:
            repo: GitHub repository object
            token: GitHub installation token
            
        Returns:
            Push URL with embedded authentication
        """
        try:
            # Use clone URL and embed token
            clone_url = repo.clone_url
            parsed_url = urlparse(clone_url)
            
            # Create authenticated URL
            auth_netloc = f"x-access-token:{token}@{parsed_url.netloc}"
            push_url = urlunparse((
                parsed_url.scheme,
                auth_netloc,
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            
            return push_url
            
        except Exception as e:
            logger.error(f"Error generating push URL: {e}")
            return repo.clone_url  # Fallback to clone URL

    def _get_git_user_info(self, repo_path: str) -> Dict[str, Optional[str]]:
        """
        Get git user information from repository or environment.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            Dictionary with user name and email
        """
        try:
            # Try environment variables first (for containerized environments)
            env_name = self.config_service.git_user_name
            env_email = self.config_service.git_user_email
            
            if env_name != "NOT_SET" and env_email != "NOT_SET":
                logger.info("Using git user info from environment")
                return {"name": env_name, "email": env_email}
            
            # Fallback to git config using GitService
            name = self.git_service.get_git_config("user.name", repo_path)
            email = self.git_service.get_git_config("user.email", repo_path)
            
            logger.info(f"Git user info - Name: {name}, Email: {email}")
            return {"name": name, "email": email}
            
        except Exception as e:
            logger.error("Error getting git user info: %s", str(e))
            return {"name": None, "email": None}

    def _is_auth_error(self, error_msg: str) -> bool:
        """
        Check if error indicates authentication failure for GitHub Enterprise.
        
        Args:
            error_msg: Error message to check
            
        Returns:
            True if error indicates authentication failure
        """
        auth_indicators = [
            "HTTP Basic: Access denied",
            "authentication failed",
            "invalid credentials",
            "Authentication failed",
            "remote: HTTP Basic: Access denied",
            "fatal: Authentication failed",
            "token is invalid",
            "Bad credentials",
            "401 Unauthorized"
        ]
        return any(indicator in str(error_msg) for indicator in auth_indicators)

    def _get_repo_root(self, file_path: str) -> Optional[str]:
        """Get git repository root for a file path."""
        return self.git_service.get_repo_root(file_path)

    # Push functionality moved to git_service.push_notebook_with_provider()
    # This service now focuses only on GitHub Enterprise-specific provisioning and token management

    def provision_repository(self, user_name: str, user_email: str) -> Dict[str, Any]:
        """
        Provision a repository for the user on GitHub Enterprise.
        
        This will create the repository if it doesn't exist.
        
        Args:
            user_name: Git user name
            user_email: Git user email
            
        Returns:
            Dictionary containing:
            - success: bool
            - push_url: str (URL with embedded token for pushing)
            - repo_url: str (Repository URL)
            - error: str (if success is False)
        """
        try:
            # Resolve GitHub username from email
            github_user = self._resolve_github_user(user_email)
            if not github_user:
                return {
                    "success": False,
                    "error": f"Could not resolve GitHub username for email: {user_email}"
                }
            
            # Create repository (default name "work")
            repo_name = "work"
            user_info = {"name": user_name, "email": user_email}
            
            result = self._create_repository(github_user, repo_name, user_info)
            
            if result["success"]:
                return {
                    "success": True,
                    "push_url": result["push_url"],
                    "repo_url": result["repo_url"],
                    "user_data": {"github_user": github_user},
                    "repo_data": result
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Failed to create repository")
                }
                
        except Exception as e:
            logger.error("Error provisioning GitHub Enterprise repository: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to provision repository: {str(e)}"
            }

    async def push_notebook(self, notebook_path: str) -> NotebookPushResult:
        """
        Delegate push operations to git_service using the new consolidated architecture.
        
        Args:
            notebook_path: Path to the notebook file
            
        Returns:
            NotebookPushResult with push details
        """
        return await self.git_service.push_notebook_with_provider(notebook_path, self)

    def get_cached_push_url(self, repo_path: str) -> Optional[str]:
        """
        Get cached push URL for repository.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            Cached push URL if available, None otherwise
        """
        return self._push_url_cache.get(repo_path)

    # All remote setup operations moved to push_service

    def get_cached_repository_url(self, repo_path: str) -> Optional[str]:
        """
        Get cached repository URL for repository.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            Cached repository URL if available, None otherwise
        """
        return self._push_url_cache.get(f"{repo_path}_repo_url") 