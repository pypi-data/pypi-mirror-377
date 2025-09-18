"""
Remote repository operations service.

Handles git remote operations including add, remove, update, push, fetch, and merge.
"""

import logging
from typing import Optional

from ..config_service import ConfigService
from ..subprocess_util import SubprocessErrorMode
from .core_service import GitCoreService
from .models import GitOperationResult
from ..logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitRemoteService:
    """Handles remote repository operations."""

    def __init__(self, core_service: GitCoreService, config_service: Optional[ConfigService] = None):
        """Initialize the remote service."""
        self.core = core_service
        self.config_service = config_service

    def add_remote(self, remote_name: str, remote_url: str) -> GitOperationResult:
        """
        Add a git remote.

        Args:
            remote_name: Name of the remote
            remote_url: URL of the remote repository

        Returns:
            GitOperationResult with operation details
        """
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["remote", "add", remote_name, remote_url],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name=f"add remote {remote_name}"
            )

            if result.success:
                logger.info("Added remote %s: %s", remote_name, remote_url)
                return GitOperationResult(
                    success=True,
                    message=f"Remote {remote_name} added successfully"
                )
            else:
                return GitOperationResult(
                    success=False,
                    message=f"Failed to add remote {remote_name}",
                    error=result.stderr
                )

        except Exception as e:
            logger.error("Error adding remote %s: %s", remote_name, str(e))
            return GitOperationResult(
                success=False,
                message=f"Error adding remote {remote_name}",
                error=str(e)
            )

    def remove_remote(self, remote_name: str) -> GitOperationResult:
        """
        Remove a git remote.

        Args:
            remote_name: Name of the remote to remove

        Returns:
            GitOperationResult with operation details
        """
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["remote", "remove", remote_name],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name=f"remove remote {remote_name}"
            )

            if result.success:
                logger.info("Removed remote %s", remote_name)
                return GitOperationResult(
                    success=True,
                    message=f"Remote {remote_name} removed successfully"
                )
            else:
                return GitOperationResult(
                    success=False,
                    message=f"Failed to remove remote {remote_name}",
                    error=result.stderr
                )

        except Exception as e:
            logger.error("Error removing remote %s: %s", remote_name, str(e))
            return GitOperationResult(
                success=False,
                message=f"Error removing remote {remote_name}",
                error=str(e)
            )

    def update_remote_url(self, remote_name: str, remote_url: str) -> GitOperationResult:
        """
        Update the URL of a git remote.

        Args:
            remote_name: Name of the remote
            remote_url: New URL of the remote repository

        Returns:
            GitOperationResult with operation details
        """
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["remote", "set-url", remote_name, remote_url],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name=f"update remote {remote_name} URL"
            )

            if result.success:
                logger.info("Updated remote %s URL to: %s", remote_name, remote_url)
                return GitOperationResult(
                    success=True,
                    message=f"Remote {remote_name} URL updated successfully"
                )
            else:
                return GitOperationResult(
                    success=False,
                    message=f"Failed to update remote {remote_name} URL",
                    error=result.stderr
                )

        except Exception as e:
            logger.error("Error updating remote %s URL: %s", remote_name, str(e))
            return GitOperationResult(
                success=False,
                message=f"Error updating remote {remote_name} URL",
                error=str(e)
            )

    # Push operations moved to GitPushService for better separation of concerns

    # Push with retry functionality moved to GitPushService

    # Fetch, branch, and merge operations moved to GitPushService

    # All push-related helper methods moved to GitPushService
