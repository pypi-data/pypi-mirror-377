"""Service for GitLab remote repository operations."""

import logging
import os
import re
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, TYPE_CHECKING
from urllib.parse import urlparse, urlunparse

import gitlab
from gitlab.exceptions import GitlabGetError

from ..config_service import ConfigService
from ..git_service.models import NotebookPushResult
from .provider_service import ProviderService, ProviderSetupResult
from ..logger_util import default_logger_config

if TYPE_CHECKING:
    from ..git_service import GitService

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitLabService(ProviderService):
    """Service for managing GitLab remote repository operations."""

    def __init__(self, config_service: ConfigService, git_service: "GitService"):
        """Initialize the GitLab service."""
        super().__init__(config_service, git_service)
        self.config = config_service  # GitLab service uses 'config' instead of 'config_service'
        self._gl = None  # Lazy initialization
        self._admin_user_id = None  # Lazy initialization

    @property
    def gl(self):
        """Get GitLab connection with lazy initialization."""
        if self._gl is None:
            self._gl = self._get_gitlab_connection()
        return self._gl

    @property
    def admin_user_id(self):
        """Get admin user ID with lazy initialization."""
        if self._admin_user_id is None:
            admin_username = os.getenv("GIT_SERVER_ADMIN_USERNAME", "root")
            self._admin_user_id = self._get_admin_user_id(admin_username)
        return self._admin_user_id

    async def setup_repository(self, repo_path: str) -> ProviderSetupResult:
        """
        Set up GitLab repository by calling provision API and caching push URL.

        Args:
            repo_path: Path to the git repository

        Returns:
            ProviderSetupResult with setup details
        """
        try:
            logger.info("Setting up GitLab repository for: %s", repo_path)

            # Get git user info from the repository
            user_info = self._get_git_user_info(repo_path)
            if not user_info["name"] or not user_info["email"]:
                return ProviderSetupResult(
                    success=False, error="Git user name and email must be configured"
                )

            # Call provision API
            provision_result = self.provision_repository(
                user_info["name"], user_info["email"]
            )

            if not provision_result["success"]:
                return ProviderSetupResult(success=False, error=provision_result["error"])

            # Cache the push URL and repository URL for this repository
            self._push_url_cache[repo_path] = provision_result["push_url"]
            self._push_url_cache[f"{repo_path}_repo_url"] = provision_result.get(
                "repo_url"
            )

            logger.info("GitLab repository setup completed for: %s", repo_path)

            # Log the repository URL for user reference
            if provision_result.get("repo_url"):
                logger.info("🌐 Repository URL: %s", provision_result["repo_url"])
                logger.info(
                    "📋 User can access repository at: %s", provision_result["repo_url"]
                )

            return ProviderSetupResult(
                success=True,
                repository_url=provision_result.get("repo_url"),
                push_url=provision_result["push_url"],
            )

        except Exception as e:
            logger.error("Error setting up GitLab repository: %s", str(e))
            return ProviderSetupResult(
                success=False, error=f"Failed to setup GitLab repository: {str(e)}"
            )

    # Push functionality moved to git_service.push_notebook_with_provider()
    # This service now focuses only on GitLab-specific provisioning and token management
    
    async def push_notebook(self, notebook_path: str) -> NotebookPushResult:
        """
        Delegate push operations to git_service using the new consolidated architecture.
        
        Args:
            notebook_path: Path to the notebook file
            
        Returns:
            NotebookPushResult with push details
        """
        return await self.git_service.push_notebook_with_provider(notebook_path, self)

    def _is_auth_error(self, error_msg: str) -> bool:
        """
        Check if error indicates authentication failure for GitLab.
        
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
            "fatal: Authentication failed"
        ]
        return any(indicator in str(error_msg) for indicator in auth_indicators)

    def _get_repo_root(self, file_path: str) -> Optional[str]:
        """Get git repository root for a file path."""
        return self.git_service.get_repo_root(file_path)

    def _get_git_user_info(self, repo_path: str) -> Dict[str, Optional[str]]:
        """Get git user info from environment variables (preferred) or repository configuration."""
        try:
            # Environment variables take precedence - email is required, name is optional
            env_name = os.getenv("GIT_USER_NAME")
            env_email = os.getenv("GIT_USER_EMAIL")
            
            # If email is provided in environment, use environment variables
            if env_email and env_email.strip():
                env_email = env_email.strip()
                
                # Use provided name or derive from email if name is missing/empty
                if env_name and env_name.strip():
                    final_name = env_name.strip()
                    logger.info("Using provided GIT_USER_NAME: %s", final_name)
                else:
                    # Derive username from email (part before @)
                    final_name = env_email.split("@")[0]
                    logger.info("GIT_USER_NAME not provided, deriving from email: %s", final_name)
                
                logger.info("Using git user info from environment variables: %s <%s>", final_name, env_email)
                return {"name": final_name, "email": env_email}
            
            # Fall back to git config if environment email isn't set using GitService
            logger.info("GIT_USER_EMAIL not set, checking git config in: %s", repo_path)
            
            git_name = self.git_service.get_git_config("user.name", repo_path)
            git_email = self.git_service.get_git_config("user.email", repo_path)
            
            logger.info("Git config user info: %s <%s>", git_name, git_email)
            
            return {"name": git_name, "email": git_email}
            
        except Exception as e:
            logger.error("Error getting git user info: %s", str(e))
            return {"name": None, "email": None}

    def provision_repository(self, user_name: str, user_email: str) -> Dict[str, Any]:
        """
        Provision a repository for the user on the GitLab server.

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
            logger.info("=== GitLabService: Starting repository provisioning ===")
            logger.info("User: %s <%s>", user_name, user_email)

            # Validate configuration
            is_valid, errors = self.config._validate_config()
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Configuration error: {'; '.join(errors)}",
                }

            # Use "work" as the standard repository name (matches the test script)
            repo_name = "work"
            logger.info("Repository name: %s", repo_name)

            # Make provision API call
            provision_response = self._call_provision_api(
                user_name, user_email, repo_name
            )

            if not provision_response["success"]:
                return provision_response

            # Extract push URL and repo URL from response
            push_url = provision_response.get("push_url")
            repo_url = provision_response.get("repo_url")

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
                "repo_data": provision_response.get("repo_data", {}),
                "user_data": provision_response.get("user_data", {}),
            }

        except Exception as e:
            logger.error("Error provisioning repository: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to provision repository: {str(e)}",
            }

    # All push operations moved to git_service.push_notebook_with_provider()

    def _clean_user_name(self, user_name: str) -> str:
        """Clean up user name for API call.

        Rules:
        - Only non-accented letters, digits, '_', '-' and '.' allowed.
        - Must not start with '-', '_', or '.'.
        - Must not end with '-', '_', '.', '.git', or '.atom'.
        """
        # Replace any character not in [a-zA-Z0-9_.-] with '_'
        cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", user_name)

        # Remove leading '-', '_', or '.'
        cleaned = re.sub(r"^[-_.]+", "", cleaned)

        # Remove trailing '-', '_', or '.'
        cleaned = re.sub(r"[-_.]+$", "", cleaned)

        # Remove trailing '.git' or '.atom' (case-insensitive)
        cleaned = re.sub(r"(\.git|\.atom)$", "", cleaned, flags=re.IGNORECASE)

        return cleaned

    def _get_admin_user_id(self, admin_username: str = "root"):
        """Get the ID of the admin user."""
        users = self.gl.users.list(username=admin_username)
        if users:
            return users[0].id
        else:
            logger.error(f"Admin user {admin_username} not found")
            raise Exception(f"Admin user {admin_username} not found")
        return None

    def _call_provision_api(
        self, user_name: str, user_email: str, repo_name: str
    ) -> Dict[str, Any]:
        """
        Provision user and repository directly using GitLab API.

        Args:
            user_name: Git user name (becomes username in API)
            user_email: Git user email
            repo_name: Repository name (typically "work")

        Returns:
            Provision response dictionary
        """
        try:
            logger.info("=== GitLabService: Starting direct provisioning ===")
            logger.info("User: %s <%s>", user_name, user_email)
            logger.info("Repository: %s", repo_name)

            # Check if domain is allowed
            if not self._is_domain_allowed(user_email):
                domain = user_email.split("@")[-1].lower()
                return {
                    "success": False,
                    "error": f"Domain {domain} not allowed",
                }

            # Clean up user name
            user_name = self._clean_user_name(user_name)

            # Get provisioning configuration
            prov_config = self._get_provisioning_config()
            user_group = prov_config["user_group"]
            
            # Use single repo per user setting from config
            if self.config.single_repo_per_user:
                repo_name_to_use = "work"
            else:
                repo_name_to_use = repo_name

            # 1. Check/create main group
            group, err = self._get_or_create_group(user_group)
            if err:
                return err

            # 2. Ensure admin is owner of the group
            err = self._ensure_admin_is_owner(group, self.admin_user_id)
            if err:
                return err

            # 3. Check/create user
            user, user_created, err = self._get_or_create_user(user_email, user_name)
            if err:
                return err

            # Ensure user is not None (should never happen if err is None)
            if user is None:
                return {
                    "success": False,
                    "error": "Failed to get user instance",
                }

            # 4. Add user to main group (Guest level)
            err = self._add_user_to_group(group, user, access_level=10)
            if err:
                return err

            # 5. Check/create user subgroup
            user_subgroup, err = self._get_or_create_user_subgroup(group, user)
            if err:
                return err

            # 6. Add user to their subgroup (Guest level - they own their projects)
            err = self._add_user_to_group(user_subgroup, user, access_level=10)
            if err:
                return err

            # 7. Check/create project
            project, repo_created, repo_conflict, err = self._get_or_create_project(
                user_subgroup, repo_name_to_use
            )
            if err:
                return err

            # Ensure project is not None (should never happen if err is None)
            if project is None:
                return {
                    "success": False,
                    "error": "Failed to get project instance",
                }

            # 8. Create project access token for pushing
            token_name = "jlab_push_token"
            
            # Revoke old tokens with the same name
            for token in project.access_tokens.list(all=True):
                if token.name == token_name:
                    logger.info(f"Revoking old token {token.name} for project {project.name}")
                    token.delete()

            # Create new token
            expires_at = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
            logger.info(f"Creating new token {token_name} for project {project.name}")
            token = project.access_tokens.create(
                {
                    "name": token_name,
                    "scopes": ["write_repository"],
                    "expires_at": expires_at,
                }
            )
            push_token = token.token

            # 9. Create authenticated push URL
            parsed_url = urlparse(project.http_url_to_repo)
            authed_netloc = f"oauth2:{push_token}@{parsed_url.netloc}"
            authed_url_tuple = parsed_url._replace(netloc=authed_netloc)
            push_url_with_token = str(urlunparse(authed_url_tuple))

            # 10. Fix URLs to use correct GitLab server hostname
            push_url = self._fix_git_url(push_url_with_token)
            repo_url = self._fix_git_url(project.http_url_to_repo)

            logger.info("Direct provisioning completed successfully")
            logger.info("Push URL: %s", self._mask_token_in_url(push_url))

            return {
                "success": True,
                "push_url": push_url,
                "repo_url": repo_url,
                "repo_data": {
                    "id": project.id,
                    "name": project.name,
                    "url": repo_url,
                    "push_url_with_token": push_url,
                    "created": repo_created,
                    "conflict": repo_conflict,
                },
                "user_data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created": user_created,
                },
            }

        except Exception as e:
            logger.error(f"Direct provisioning failed: {e}")
            return {
                "success": False,
                "error": f"Failed to provision repository: {str(e)}",
            }


    # All remote setup and push operations moved to push_service
    

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

    def _fix_git_url(self, url: str) -> str:
        """
        Fix GitLab/Gitea URLs by replacing localhost with the configured GIT_SERVER_URL.
        
        Args:
            url: Original URL from provision API
            
        Returns:
            Fixed URL with correct hostname
        """
        if not url:
            return url
            
        try:
            # Get the configured GitLab server URL from environment
            gitlab_server_url = self.config.git_server_url
            
            # Parse both URLs
            original_url = urlparse(url)
            server_url = urlparse(gitlab_server_url)
            
            # replace with env variable regardless of the original URL contains 
            # localhost or 127.0.0.1
            # Extract username:password if present in original URL
            auth = ""
            if "@" in original_url.netloc:
                auth_part = original_url.netloc.split('@')[0]
                auth = f"{auth_part}@"
            
            # Replace hostname but keep port and auth info
            new_netloc = f"{auth}{server_url.netloc}"
            
            # Reconstruct URL with new hostname but original path and query
            parts = list(original_url)
            parts[1] = new_netloc  # Replace netloc (hostname:port)
            
            fixed_url = urlunparse(parts)
            logger.info(f"Fixed GitLab URL: {self._mask_token_in_url(url)} → {self._mask_token_in_url(fixed_url)}")
            return fixed_url
            
            
        except Exception as e:
            logger.warning(f"Error fixing GitLab URL: {e}")
            return url

    def _get_provisioning_config(self) -> Dict[str, Any]:
        """
        Get provisioning configuration with defaults.
        
        Returns:
            Configuration dictionary
        """
        return {
            "user_group": os.getenv("DEFAULT_USER_GROUP", "researchers"),
            "allowed_domains": [
                d.strip().lower()
                for d in os.getenv("ALLOWED_DOMAINS", "").split(",")
                if d.strip()
            ],
        }

    def _is_domain_allowed(self, email: str) -> bool:
        """
        Check if email domain is allowed for provisioning.
        
        Args:
            email: User email address
            
        Returns:
            True if domain is allowed or no restrictions are set
        """
        config = self._get_provisioning_config()
        allowed_domains = config["allowed_domains"]
        
        if not allowed_domains:
            # No domain restrictions
            return True
            
        domain = email.split("@")[-1].lower()
        return domain in allowed_domains

    def _get_gitlab_connection(self):
        """
        Get GitLab connection instance.
        
        Returns:
            GitLab API instance
        """
        try:
            # Use SSL verification setting from config
            ssl_verify = self.config.git_ssl_verify
            
            gl = gitlab.Gitlab(
                self.config.git_server_url,
                private_token=self.config.git_server_admin_token,
                ssl_verify=ssl_verify,
            )
            gl.auth()
            return gl
        except Exception as e:
            logger.error(f"Failed to connect to GitLab: {e}")
            raise

    def _get_or_create_group(self, group_name: str):
        """
        Get or create a GitLab group.
        
        Args:
            group_name: Name of the group to create
            
        Returns:
            Tuple of (group, error_response)
        """
        try:
            group = self.gl.groups.get(group_name)
            return group, None
        except GitlabGetError:
            logger.info(f"Group {group_name} does not exist. Creating it.")
            try:
                group = self.gl.groups.create({"name": group_name, "path": group_name})
                return group, None
            except Exception as e:
                logger.error(f"Failed to create group {group_name}: {e}")
                return None, {
                    "success": False,
                    "error": f"Failed to create group {group_name}: {e}",
                }

    def _ensure_admin_is_owner(self, group, admin_user_id: int):
        """
        Ensure admin user is owner of the group.
        
        Args:
            group: GitLab group instance
            admin_user_id: Admin user ID
            
        Returns:
            Error response or None
        """
        try:
            member = group.members.get(admin_user_id)
            if member.access_level < 50:
                logger.info(
                    f"Promoting admin {admin_user_id} to owner in group {group.name}"
                )
                member.access_level = 50
                member.save()
        except GitlabGetError:
            logger.info(
                f"Adding admin {admin_user_id} to group {group.name} as owner"
            )
            try:
                group.members.create({"user_id": admin_user_id, "access_level": 50})
            except Exception as e:
                logger.warning(f"Could not add admin to group: {e}")
                return {
                    "success": False,
                    "error": f"Could not add admin to group: {e}",
                }
        return None

    def _get_or_create_user(self, email: str, username: str):
        """
        Get or create a GitLab user.
        
        Args:
            email: User email
            username: Username
            
        Returns:
            Tuple of (user, user_created, error_response)
        """
        users = self.gl.users.list(search=email)
        if users:
            user = users[0]
            user_created = False
            logger.info(f"User {user.username} already exists with email {email}")
        else:
            logger.info(f"Creating user {username} with email {email}")
            temp_password = secrets.token_urlsafe(16)
            try:
                user = self.gl.users.create(
                    {
                        "email": email,
                        "password": temp_password,
                        "username": username,
                        "name": username.replace("_", " ").title(),
                        "skip_confirmation": True,
                        "force_password_change": True,
                    }
                )
                user_created = True
            except Exception as e:
                logger.error(f"Failed to create user {username}: {e}")
                return None, False, {
                    "success": False,
                    "error": f"Failed to create user {username}: {e}",
                }
        return user, user_created, None

    def _add_user_to_group(self, group, user, access_level: int = 30):
        """
        Add user to GitLab group.
        
        Args:
            group: GitLab group instance
            user: GitLab user instance
            access_level: Access level (30 = Developer, 10 = Guest)
            
        Returns:
            Error response or None
        """
        try:
            logger.info(f"Adding user {user.username} to group {group.name}")
            group.members.create({"user_id": user.id, "access_level": access_level})
        except Exception as e:
            if str(e).startswith("409"):  # 409: Member already exists
                return None
            logger.warning(f"Could not add user to group: {e}")
            return {
                "success": False,
                "error": f"Could not add user to group: {e}",
            }
        return None

    def check_user_registration(self, user_email: str) -> bool:
        """
        Check if a user is already registered in GitLab.
        
        Args:
            user_email: User email to check
            
        Returns:
            True if user exists in GitLab, False otherwise
        """
        try:
            if not self.gl:
                logger.warning("GitLab client not configured - cannot check user registration")
                return False
            
            # Search for user by email
            users = self.gl.users.list(search=user_email)
            
            user_exists = len(users) > 0
            if user_exists:
                user = users[0]
                logger.info(f"User '{user.username}' with email '{user_email}' exists in GitLab")
            else:
                logger.info(f"User with email '{user_email}' does not exist in GitLab")
            
            return user_exists
            
        except Exception as e:
            logger.warning(f"Failed to check if user {user_email} is registered in GitLab: {str(e)}")
            return False

    async def get_fresh_push_url_for_sync(self, repo_path: str) -> Optional[str]:
        """
        Generate a fresh push URL for session sync operations.
        For GitLab, we use the cached push URL as tokens are typically long-lived.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            Push URL for sync operations, or None if not found
        """
        try:
            logger.info("🔄 Getting push URL for GitLab session sync...")
            
            # For GitLab, tokens are typically long-lived, so we can use the cached URL
            cached_url = self._push_url_cache.get(repo_path)
            if cached_url:
                logger.info("✅ Using cached push URL for GitLab session sync")
                return cached_url
            else:
                logger.warning("⚠️ No cached push URL found for GitLab session sync")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get fresh push URL for GitLab sync: {str(e)}")
            return None

    def _get_or_create_user_subgroup(self, parent_group, user):
        """
        Get or create a user subgroup.
        
        Args:
            parent_group: Parent group instance
            user: User instance
            
        Returns:
            Tuple of (subgroup, error_response)
        """
        user_subgroup_path = f"{parent_group.name}/{user.username}"
        try:
            user_subgroup = self.gl.groups.get(user_subgroup_path)
            return user_subgroup, None
        except GitlabGetError:
            logger.info(
                f"Subgroup for user {user.username} does not exist. Creating it."
            )
            try:
                user_subgroup = self.gl.groups.create(
                    {
                        "name": user.username,
                        "path": user.username,
                        "parent_id": parent_group.id,
                    }
                )
                return user_subgroup, None
            except Exception as e:
                logger.error(
                    f"Failed to create subgroup for user {user.username}: {e}"
                )
                return None, {
                    "success": False,
                    "error": f"Failed to create subgroup for user {user.username}: {e}",
                }

    def _get_or_create_project(self, subgroup, repo_name: str):
        """
        Get or create a GitLab project.
        
        Args:
            subgroup: Subgroup instance
            repo_name: Repository name
            
        Returns:
            Tuple of (project, repo_created, repo_conflict, error_response)
        """
        project_path = f"{subgroup.full_path}/{repo_name}"
        try:
            logger.info(f"Checking for project {project_path}")
            project = self.gl.projects.get(project_path)
            return project, False, True, None
        except GitlabGetError:
            logger.info(f"Creating project {project_path}")
            try:
                project = self.gl.projects.create(
                    {"name": repo_name, "namespace_id": subgroup.id}
                )
                return project, True, False, None
            except Exception as e:
                logger.error(f"Failed to create project {project_path}: {e}")
                return None, False, False, {
                    "success": False,
                    "error": f"Failed to create project {project_path}: {e}",
                }
