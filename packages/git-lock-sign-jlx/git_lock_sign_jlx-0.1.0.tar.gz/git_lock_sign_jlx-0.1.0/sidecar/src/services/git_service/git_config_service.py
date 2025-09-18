"""
Git configuration service.

Handles git configuration, user information, and environment setup.
"""

import logging
import os
from typing import Optional

from ..config_service import ConfigService
from ..subprocess_util import SubprocessErrorMode
from .core_service import GitCoreService
from .models import GitOperationResult, UserInfoResult
from ..logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitConfigService:
    """Handles git configuration and user information."""

    def __init__(self, core_service: GitCoreService, config_service: Optional[ConfigService] = None):
        """Initialize the config service."""
        self.core = core_service
        self.config_service = config_service

    def get_user_info(self, notebook_path: str) -> UserInfoResult:
        """
        Get git user information with simplified logic.
        
        Logic (matching legacy service):
        1. Get user info from config service or environment variables
        2. Try to get local git config from notebook_path directory
        3. If local config matches expected values -> return
        4. If local config doesn't exist or doesn't match -> configure local git
        5. Return expected values
        
        Args:
            notebook_path: Path to the notebook file or directory
            
        Returns:
            UserInfoResult with user details
        """
        try:
            # Translate JupyterLab path to sidecar path
            sidecar_path = self.core.translate_jupyterlab_path_to_sidecar(notebook_path)
            
            # Determine working directory
            if os.path.isfile(sidecar_path):
                cwd = os.path.dirname(sidecar_path)
            else:
                cwd = sidecar_path
                
            logger.info("[get_user_info] Using cwd: %s", cwd)
            
            # Step 1: Get expected user info from config service or environment
            if self.config_service and self.config_service.git_user_email != "NOT_SET":
                config_email = self.config_service.git_user_email
                config_name = self.config_service.git_user_name
                gpg_key_id = self.config_service.gpg_key_id
                logger.info("[get_user_info] Using config service values: %s <%s>", config_name, config_email)
            else:
                # Fallback to environment variables
                config_email = os.getenv("GIT_USER_EMAIL", "user@example.com")
                config_name = os.getenv("GIT_USER_NAME", "JupyterLab User")
                gpg_key_id = os.getenv("GPG_KEY_ID")
                logger.info("[get_user_info] Using environment variables: %s <%s>", config_name, config_email)
            
            # Step 2: Try to get local git config
            local_name_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local git user name"
            )
            local_email_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local git user email"
            )
            
            local_name = local_name_result.stdout.strip() if local_name_result.success else None
            local_email = local_email_result.stdout.strip() if local_email_result.success else None
            
            logger.info("[get_user_info] Local git name: '%s' (success=%s)", local_name, local_name_result.success)
            logger.info("[get_user_info] Local git email: '%s' (success=%s)", local_email, local_email_result.success)
            
            # Step 3: Check if local config matches expected values
            config_matches = (local_name == config_name and local_email == config_email)
            
            if config_matches:
                logger.info("[get_user_info] Local git config matches expected values - no action needed")
            else:
                # Step 4: Configure local git with expected values
                logger.info("[get_user_info] Local git config doesn't match or doesn't exist - configuring with expected values")
                self.core._configure_git_user(cwd)
            
            # Step 5: Return expected values (ensures consistency)
            return UserInfoResult(name=config_name, email=config_email, gpg_key_id=gpg_key_id)
            
        except Exception as e:
            logger.error("Error getting user info: %s", str(e))
            # Fallback to config service values or environment on error
            if self.config_service and self.config_service.git_user_email != "NOT_SET":
                return UserInfoResult(
                    name=self.config_service.git_user_name,
                    email=self.config_service.git_user_email,
                    gpg_key_id=self.config_service.gpg_key_id
                )
            else:
                return UserInfoResult(
                    name=os.getenv("GIT_USER_NAME", "JupyterLab User"),
                    email=os.getenv("GIT_USER_EMAIL", "user@example.com"),
                    gpg_key_id=os.getenv("GPG_KEY_ID")
                )

    def get_git_config(self, config_key: str, repo_path: Optional[str] = None) -> Optional[str]:
        """
        Get a git configuration value.

        Args:
            config_key: Git configuration key
            repo_path: Optional repository path

        Returns:
            Configuration value, or None if not found
        """
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["config", config_key],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name=f"get git config {config_key}"
            )

            if result.success:
                return result.stdout.strip()
            else:
                return None

        except Exception as e:
            logger.error("Error getting git config %s: %s", config_key, str(e))
            return None

    def set_git_config(self, config_key: str, config_value: str, repo_path: Optional[str] = None) -> GitOperationResult:
        """
        Set a git configuration value.

        Args:
            config_key: Git configuration key
            config_value: Configuration value
            repo_path: Optional repository path

        Returns:
            GitOperationResult with operation details
        """
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["config", config_key, config_value],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name=f"set git config {config_key}"
            )

            if result.success:
                logger.info("Set git config %s = %s", config_key, config_value)
                return GitOperationResult(
                    success=True,
                    message=f"Git config '{config_key}' set successfully"
                )
            else:
                logger.error("Failed to set git config %s: %s", config_key, result.stderr)
                return GitOperationResult(
                    success=False,
                    message=f"Failed to set git config '{config_key}'",
                    error=result.stderr
                )

        except Exception as e:
            logger.error("Error setting git config %s: %s", config_key, str(e))
            return GitOperationResult(
                success=False,
                message=f"Failed to set git config '{config_key}'",
                error=str(e)
            )

    def _enforce_environment_user_config(self, repo_path: str) -> bool:
        """
        Enforces that local git config matches config service or environment variables.
        Returns True if config was updated, False if already correct.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            True if config was updated, False if already correct
        """
        try:
            # Get expected values from config service or environment
            if self.config_service and self.config_service.git_user_email != "NOT_SET":
                expected_name = self.config_service.git_user_name
                expected_email = self.config_service.git_user_email
            else:
                expected_name = os.getenv("GIT_USER_NAME")
                expected_email = os.getenv("GIT_USER_EMAIL")
                if not expected_name or not expected_email:
                    logger.warning("Cannot enforce user config: config service and environment variables not set")
                    return False
            
            # Check current local config
            current_name_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get current local git name"
            )
            
            current_email_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get current local git email"
            )
            
            current_name = current_name_result.stdout.strip() if current_name_result.success else None
            current_email = current_email_result.stdout.strip() if current_email_result.success else None
            
            # If mismatch, force update to expected values
            config_updated = False
            
            if current_name != expected_name:
                result = self.set_git_config("user.name", expected_name, repo_path)
                if result.success:
                    logger.info("🔧 Updated local git user.name: %s -> %s", current_name, expected_name)
                    config_updated = True
                else:
                    return False
            
            if current_email != expected_email:
                result = self.set_git_config("user.email", expected_email, repo_path)
                if result.success:
                    logger.info("🔧 Updated local git user.email: %s -> %s", current_email, expected_email)
                    config_updated = True
                else:
                    return False
            
            if config_updated:
                logger.info("✅ Local git config now matches expected values")
            else:
                logger.info("✅ Local git config already matches expected values")
            
            return config_updated
            
        except Exception as e:
            logger.error("Failed to enforce user config: %s", str(e))
            return False
