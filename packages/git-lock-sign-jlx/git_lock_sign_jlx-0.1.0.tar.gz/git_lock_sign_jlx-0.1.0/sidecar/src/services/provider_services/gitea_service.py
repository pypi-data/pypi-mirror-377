"""Service for Gitea remote repository operations."""

import logging
import re
from typing import Any, Dict, Optional, TYPE_CHECKING
from urllib.parse import urlparse, urlunparse

import requests

from ..config_service import ConfigService
from ..git_service.models import NotebookPushResult
from ..logger_util import default_logger_config
from .provider_service import ProviderService, ProviderSetupResult

if TYPE_CHECKING:
    from ..git_service import GitService

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GiteaService(ProviderService):
    """Service for managing Gitea remote repository operations."""

    def __init__(self, config_service: ConfigService, git_service: "GitService"):
        """Initialize the Gitea service."""
        super().__init__(config_service, git_service)

    async def setup_repository(self, repo_path: str) -> ProviderSetupResult:
        """
        Set up Gitea repository by creating user and repository via API.

        Args:
            repo_path: Path to the git repository

        Returns:
            ProviderSetupResult with setup details
        """
        try:
            logger.info("Setting up Gitea repository for: %s", repo_path)

            # Get git user info from the repository
            user_info = {"name":self.config_service.git_user_name, "email":self.config_service.git_user_email}
            if not user_info["name"] or not user_info["email"]:
                return ProviderSetupResult(
                    success=False,
                    error="Git user name and email must be configured",
                )
            repo_name = (
                "work"
                if self.config_service.single_repo_per_user
                else repo_path.split("/")[-1]
            )

            # Create user and repository in Gitea
            provision_result = self.provision_repository(
                user_info["name"], user_info["email"], repo_name
            )

            if not provision_result["success"]:
                return ProviderSetupResult(
                    success=False, error=provision_result["error"]
                )

            # Cache the push URL and repository URL for this repository
            self._push_url_cache[repo_path] = provision_result["push_url"]
            self._push_url_cache[f"{repo_path}_repo_url"] = (
                provision_result.get("repo_url")
            )

            logger.info("Gitea repository setup completed for: %s", repo_path)

            # Log the repository URL for user reference
            if provision_result.get("repo_url"):
                logger.info(
                    "🌐 Repository URL: %s", provision_result["repo_url"]
                )
                logger.info(
                    "📋 User can access repository at: %s",
                    provision_result["repo_url"],
                )

            return ProviderSetupResult(
                success=True,
                repository_url=provision_result.get("repo_url"),
                push_url=provision_result["push_url"],
            )

        except Exception as e:
            logger.error("Error setting up Gitea repository: %s", str(e))
            return ProviderSetupResult(
                success=False,
                error=f"Failed to setup Gitea repository: {str(e)}",
            )

    # Push functionality moved to git_service.push_notebook_with_provider()
    # This service now focuses only on Gitea-specific provisioning and token management
    
    async def push_notebook(self, notebook_path: str) -> NotebookPushResult:
        """
        Delegate push operations to git_service using the new consolidated architecture.
        
        Args:
            notebook_path: Path to the notebook file
            
        Returns:
            NotebookPushResult with push details
        """
        return await self.git_service.push_notebook_with_provider(notebook_path, self)



    async def _get_or_provision_push_url(self, repo_root: str) -> Optional[str]:
        """Get cached push URL or provision new repository."""
        # Try cached URL first
        push_url = self._push_url_cache.get(repo_root)
        if push_url:
            return push_url

        # No cached URL, need to provision
        logger.info("No cached push URL, calling provision API")
        setup_result = await self.setup_repository(repo_root)

        if not setup_result.success:
            logger.error("Failed to provision repository: %s", setup_result.error)
            return None

        return setup_result.push_url


    def _is_auth_error(self, error_msg: str) -> bool:
        """Check if error indicates authentication failure."""
        auth_indicators = [
            "HTTP Basic: Access denied",
            "authentication failed",
            "invalid credentials",
        ]
        return any(indicator in str(error_msg) for indicator in auth_indicators)


    def provision_repository(
        self, user_name: str, user_email: str, repo_name: str = "work"
    ) -> Dict[str, Any]:
        """
        Provision a repository for the user on the Gitea server.

        This will create the user and repository if they don't exist.

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
            logger.info(
                "=== GiteaService: Starting repository provisioning ==="
            )
            logger.info("User: %s <%s>", user_name, user_email)

            # Validate configuration
            is_valid, errors = self.config_service._validate_config()
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Configuration error: {'; '.join(errors)}",
                }

            # Use "work" as the standard repository name (matches the test script)
            logger.info("Repository name: %s", repo_name)

            # Create user and repository in Gitea
            provision_result = self._create_user_and_repository(
                user_name, user_email, repo_name
            )

            if not provision_result["success"]:
                return provision_result

            # Extract push URL and repo URL from response
            push_url = provision_result.get("push_url")
            repo_url = provision_result.get("repo_url")

            if not push_url:
                return {
                    "success": False,
                    "error": "Provision API did not return push_url",
                }

            logger.info("Repository provisioned successfully")
            logger.info("Push URL: %s", self._mask_token_in_url(push_url))

            return {
                "success": True,
                "push_url": push_url,
                "repo_url": repo_url,
                "repo_data": provision_result.get("repo_data", {}),
                "user_data": provision_result.get("user_data", {}),
            }

        except Exception as e:
            logger.error("Error provisioning repository: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to provision repository: {str(e)}",
            }

    def _create_user_and_repository(
        self, user_name: str, user_email: str, repo_name: str
    ) -> Dict[str, Any]:
        """
        Create user and repository in Gitea using direct API calls.

        Args:
            user_name: Git user name
            user_email: Git user email
            repo_name: Repository name

        Returns:
            API response dictionary
        """
        try:
            # Clean up user name for Gitea
            user_name = self._clean_user_name(user_name)

            # Get Gitea API configuration
            gitea_url = self.config_service.git_server_url
            admin_token = self.config_service.git_server_admin_token

            if not gitea_url or not admin_token:
                return {
                    "success": False,
                    "error": "Gitea server URL or admin token not configured",
                }

            # Step 1: Create user if it doesn't exist
            user_result = self._create_gitea_user(
                user_name, user_email, gitea_url, admin_token
            )
            if not user_result["success"]:
                return user_result

            # Step 2: Create repository for the user
            repo_result = self._create_gitea_repository(
                user_name, repo_name, gitea_url, admin_token
            )
            if not repo_result["success"]:
                return repo_result

            # Step 3: Generate push URL with token
            push_url = self._generate_push_url(
                user_name, repo_name, gitea_url, admin_token
            )
            repo_url = f"{gitea_url}/{user_name}/{repo_name}"

            return {
                "success": True,
                "push_url": push_url,
                "repo_url": repo_url,
                "repo_data": repo_result.get("repo_data", {}),
                "user_data": user_result.get("user_data", {}),
            }

        except Exception as e:
            logger.error("Error creating user and repository: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to create user and repository: {str(e)}",
            }

    def _create_gitea_user(
        self, user_name: str, user_email: str, gitea_url: str, admin_token: str
    ) -> Dict[str, Any]:
        """Create user in Gitea using admin API."""
        try:
            # Check if user already exists
            check_url = f"{gitea_url}/api/v1/users/{user_name}"
            headers = {"Authorization": f"token {admin_token}"}

            check_response = requests.get(
                check_url, headers=headers, timeout=30, verify=False
            )

            if check_response.status_code == 200:
                logger.info("User %s already exists in Gitea", user_name)
                return {
                    "success": True,
                    "user_data": check_response.json(),
                }

            # Create new user
            create_url = f"{gitea_url}/api/v1/admin/users"
            user_payload = {
                "username": user_name,
                "email": user_email,
                "password": self._generate_password(),  # Generate random password
                "must_change_password": False,
                "send_notify": False,
                "source_id": 0,
                "login_name": user_name,
                "full_name": user_name,
            }

            create_response = requests.post(
                create_url,
                json=user_payload,
                headers=headers,
                timeout=30,
                verify=False,
            )

            if create_response.status_code == 201:
                logger.info("Successfully created user %s in Gitea", user_name)
                return {
                    "success": True,
                    "user_data": create_response.json(),
                }
            else:
                error_msg = f"HTTP {create_response.status_code}"
                try:
                    error_data = create_response.json()
                    if "message" in error_data:
                        error_msg = error_data["message"]
                except Exception:
                    error_msg = f"HTTP {create_response.status_code}: {create_response.text}"

                return {
                    "success": False,
                    "error": f"Failed to create Gitea user: {error_msg}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating Gitea user: {str(e)}",
            }

    def _create_gitea_repository(
        self, user_name: str, repo_name: str, gitea_url: str, admin_token: str
    ) -> Dict[str, Any]:
        """Create repository in Gitea using admin API."""
        try:
            # Check if repository already exists
            check_url = f"{gitea_url}/api/v1/repos/{user_name}/{repo_name}"
            headers = {"Authorization": f"token {admin_token}"}

            check_response = requests.get(
                check_url, headers=headers, timeout=30, verify=False
            )

            if check_response.status_code == 200:
                logger.info(
                    "Repository %s/%s already exists in Gitea",
                    user_name,
                    repo_name,
                )
                return {
                    "success": True,
                    "repo_data": check_response.json(),
                }

            # Create new repository
            create_url = f"{gitea_url}/api/v1/admin/users/{user_name}/repos"
            repo_payload = {
                "name": repo_name,
                "description": "Auto-created repository for notebook work",
                "private": False,
                "auto_init": False,  # Don't initialize with README to avoid unrelated histories
                "gitignores": "",
                "license": "",
                "readme": "",
                "default_branch": "main",
            }

            create_response = requests.post(
                create_url,
                json=repo_payload,
                headers=headers,
                timeout=30,
                verify=False,
            )

            if create_response.status_code == 201:
                logger.info(
                    "Successfully created repository %s/%s in Gitea",
                    user_name,
                    repo_name,
                )
                return {
                    "success": True,
                    "repo_data": create_response.json(),
                }
            else:
                error_msg = f"HTTP {create_response.status_code}"
                try:
                    error_data = create_response.json()
                    if "message" in error_data:
                        error_msg = error_data["message"]
                except Exception:
                    error_msg = f"HTTP {create_response.status_code}: {create_response.text}"

                return {
                    "success": False,
                    "error": f"Failed to create Gitea repository: {error_msg}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating Gitea repository: {str(e)}",
            }

    def _generate_push_url(
        self, user_name: str, repo_name: str, gitea_url: str, admin_token: str
    ) -> str:
        """Generate push URL with embedded token for the repository."""
        # For Gitea, we use the admin token with the correct username
        # This gives us permission to access any repository while maintaining the correct user context
        logger.info(f"🔑 Using admin token with username {user_name} for Gitea push URL")
        
        # Format: http://username:admin_token@gitea.example.com/user/repo.git
        # The admin token gives us permission, but the username in the URL path must match the repository owner
        push_url = f"http://{user_name}:{admin_token}@{urlparse(gitea_url).netloc}/{user_name}/{repo_name}.git"
        return push_url

    def _create_user_token(
        self, user_name: str, gitea_url: str, admin_token: str
    ) -> Dict[str, Any]:
        """Create a personal access token for the user."""
        try:
            # Create token for the user
            token_url = f"{gitea_url}/api/v1/users/{user_name}/tokens"
            headers = {"Authorization": f"token {admin_token}"}

            token_payload = {
                "name": "notebook-access-token",
                "scopes": ["repo", "write:repo", "read:repo"],
            }

            response = requests.post(
                token_url,
                json=token_payload,
                headers=headers,
                timeout=30,
                verify=False,
            )

            if response.status_code == 201:
                token_data = response.json()
                return {
                    "success": True,
                    "token": token_data["sha1"],  # Gitea returns token as sha1
                }
            else:
                logger.warning("Failed to create user token: %s", response.text)
                return {
                    "success": False,
                    "error": "Could not create user token",
                }

        except Exception as e:
            logger.warning("Error creating user token: %s", str(e))
            return {"success": False, "error": str(e)}

    def _generate_password(self, length: int = 16) -> str:
        """Generate a random password for Gitea user creation."""
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def check_user_registration(self, user_email: str) -> bool:
        """
        Check if a user is already registered in Gitea by email address.
        
        Args:
            user_email: User email to check
            
        Returns:
            True if user exists in Gitea, False otherwise
        """
        try:
            gitea_url = self.config_service.git_server_url
            admin_token = self.config_service.git_server_admin_token
            
            if not gitea_url or not admin_token:
                logger.warning("Gitea URL or admin token not configured - cannot check user registration")
                return False
            
            # Search for user by email using admin emails search API
            search_url = f"{gitea_url}/api/v1/admin/emails/search"
            headers = {"Authorization": f"token {admin_token}"}
            params = {"q": user_email}
            
            response = requests.get(
                search_url, headers=headers, params=params, timeout=30, verify=False
            )
            
            if response.status_code == 200:
                search_results = response.json()
                logger.info(f"🔍 Gitea API response type: {type(search_results)}, content: {search_results}")
                
                # Gitea API returns a list directly, not wrapped in a dictionary
                if isinstance(search_results, list):
                    # Check if any results match the exact email
                    user_exists = any(
                        result.get("email", "").lower() == user_email.lower() 
                        for result in search_results
                    )
                else:
                    # Fallback: try to handle wrapped response format
                    user_exists = any(
                        result.get("email", "").lower() == user_email.lower() 
                        for result in search_results.get("data", [])
                    )
                logger.info(f"User with email '{user_email}' {'exists' if user_exists else 'does not exist'} in Gitea")
                return user_exists
            else:
                logger.warning(f"Failed to search users by email: HTTP {response.status_code}")
                return False
            
        except Exception as e:
            logger.warning(f"Failed to check if user {user_email} is registered in Gitea: {str(e)}")
            return False

    async def get_fresh_push_url_for_sync(self, repo_path: str) -> Optional[str]:
        """
        Generate a fresh push URL for session sync operations.
        For Gitea, we use the cached push URL as tokens don't typically expire.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            Push URL for sync operations, or None if not found
        """
        try:
            logger.info("🔄 Getting push URL for Gitea session sync...")
            
            # For Gitea, tokens don't typically expire, so we can use the cached URL
            cached_url = self._push_url_cache.get(repo_path)
            if cached_url:
                logger.info("✅ Using cached push URL for Gitea session sync")
                return cached_url
            else:
                logger.warning("⚠️ No cached push URL found for Gitea session sync")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get fresh push URL for Gitea sync: {str(e)}")
            return None

    def _clean_user_name(self, user_name: str) -> str:
        """Clean up user name for Gitea API call.

        Rules:
        - Only non-accented letters, digits, '_', '-' and '.' allowed.
        - Must not start with '-', '_', or '.'.
        - Must not end with '-', '_', or '.'.
        """
        # Replace any character not in [a-zA-Z0-9_.-] with '_'
        cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", user_name)

        # Remove leading '-', '_', or '.'
        cleaned = re.sub(r"^[-_.]+", "", cleaned)

        # Remove trailing '-', '_', or '.'
        cleaned = re.sub(r"[-_.]+$", "", cleaned)

        return cleaned

    def _clean_url(self, url: str) -> str:
        """
        Clean URL by removing embedded credentials.
        
        Args:
            url: URL that may contain embedded credentials
            
        Returns:
            Clean URL without credentials
        """
        try:
            # Parse the URL (using already imported urlparse)
            parsed = urlparse(url)
            
            # Remove username and password from netloc
            if '@' in parsed.netloc:
                # Split netloc into host:port and credentials
                credentials, host_port = parsed.netloc.split('@', 1)
                # Reconstruct URL without credentials
                clean_parsed = parsed._replace(netloc=host_port)
                return urlunparse(clean_parsed)
            
            return url
            
        except Exception as e:
            logger.warning(f"Failed to clean URL {url}: {e}")
            return url


    def _mask_token_in_url(self, url: str) -> str:
        """
        Mask the token in a URL for logging purposes.

        Args:
            url: URL potentially containing a token

        Returns:
            URL with token masked
        """
        try:
            parsed = urlparse(url)
            if "@" in parsed.netloc:
                # URL contains credentials, mask them
                netloc_parts = parsed.netloc.split("@")
                if len(netloc_parts) >= 2:
                    masked_netloc = "***:***@" + netloc_parts[-1]
                    return url.replace(parsed.netloc, masked_netloc)
            return url
        except Exception:
            return url  # Return original if parsing fails
