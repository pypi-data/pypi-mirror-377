"""
Helper functions for the session initialization endpoint.

This module contains all helper functions related to session initialization,
including directory setup, repository initialization, git remote setup, and sync operations.
"""

import logging
import os
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException

from ..services.config_service import ConfigService
from ..services.git_service import GitService
from ..services.logger_util import default_logger_config
from ..services.provider_services import ProviderService
from ..services.subprocess_util import SubprocessErrorMode, SubprocessResult

logger = logging.getLogger(__name__)
default_logger_config(logger)


def setup_directory_structure(config_service: ConfigService) -> Tuple[str, str]:
    """Set up directory structure for session initialization."""
    git_metadata_dir = config_service.git_metadata_directory
    work_tree_dir = config_service.work_tree_directory

    logger.info("📁 Setting up separate git directory structure:")
    logger.info(f"📁   Git metadata: {git_metadata_dir}")
    logger.info(f"📁   Work tree: {work_tree_dir}")

    try:
        os.makedirs(git_metadata_dir, exist_ok=True)
        os.makedirs(work_tree_dir, exist_ok=True)
        logger.info("✅ Created directory structure for separate git setup")
    except Exception as e:
        logger.error(f"❌ Failed to create directory structure: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create directory structure: {e}"
        )

    return git_metadata_dir, work_tree_dir


def initialize_or_get_repository(
    git_service: GitService, actual_repo_path: str
) -> str:
    """Initialize git repository or get existing one."""
    repo = git_service.get_repository(actual_repo_path)
    if repo:
        repo_path = actual_repo_path  # Always use work tree path
        logger.info(
            f"✅ Found existing git repository with work tree at: {repo_path}"
        )
        return repo_path
    else:
        logger.info(
            "📁 No git repository found - initializing new repository with separate structure"
        )
        try:
            repo_path = git_service.init_repository(actual_repo_path)
            logger.info(
                f"✅ Initialized git repository with work tree at: {repo_path}"
            )
            return repo_path
        except Exception as e:
            logger.error(f"Failed to initialize git repository: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize repository: {str(e)}",
            )


async def setup_git_remote_and_sync(
    git_server: str,
    repo_path: str,
    user_registered: bool,
    repository_url: Optional[str],
    services: Dict[str, Any],
) -> Tuple[bool, Optional[Any]]:
    """Set up git remote and perform session sync if user was already registered."""
    if not user_registered or not repository_url:
        return False, None

    logger.info(
        "🔄 User is already registered - setting up git remote and performing session sync"
    )

    try:
        git_service: GitService = services["git_service"]

        # Get authenticated push URL and set up local git remote
        auth_push_url = None
        remote_name = "origin"
        provider_service: ProviderService = services[f"{git_server}_service"]
        auth_push_url = await provider_service.get_fresh_push_url_for_sync(
            repo_path
        )

        # Set up git remote with embedded authentication
        if auth_push_url:
            setup_git_remote(git_service, auth_push_url, remote_name)

            # Push .gitignore commit if it exists (now that remote is configured)
            logger.info(
                "🔄 Attempting to push .gitignore commit after remote setup..."
            )
            git_service.push_gitignore_commit_if_exists()

            # Now perform sync with the authenticated remote
            logger.info(
                f"🔄 Performing session sync with authenticated remote '{remote_name}'"
            )

            sync_result = await git_service.sync_with_remote_on_session_start(
                repo_path,
                provider_service=provider_service,
                remote_name=remote_name,
            )

            if sync_result.success:
                logger.info(
                    "✅ Session sync completed successfully - files should now be present"
                )
            else:
                logger.warning(f"⚠️ Session sync failed: {sync_result.error}")

            return True, sync_result
        else:
            logger.warning(
                "⚠️ Could not get authenticated push URL for session sync"
            )
            return True, None

    except Exception as e:
        logger.warning(
            f"⚠️ Error during git remote setup and session sync: {str(e)}"
        )
        return True, None


def setup_git_remote(
    git_service: GitService, auth_push_url: str, remote_name: str
) -> None:
    """Set up git remote with embedded authentication."""
    logger.info(
        f"🔗 Setting up git remote '{remote_name}' with embedded authentication"
    )
    clean_url = auth_push_url

    # Check if remote already exists
    remote_check = git_service.run_git_command_with_separate_dirs(
        ["remote", "get-url", remote_name],
        error_mode=SubprocessErrorMode.LENIENT,
        timeout=10,
        operation_name="check if remote exists",
    )

    if remote_check.success:
        # Remote exists, update it with clean URL
        logger.info(
            f"🔄 Updating existing remote '{remote_name}' with clean URL"
        )
        update_result: SubprocessResult = (
            git_service.run_git_command_with_separate_dirs(
                ["remote", "set-url", remote_name, clean_url],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name="update git remote URL",
            )
        )
        if update_result.success:
            logger.info(
                f"✅ Successfully updated remote '{remote_name}' with clean URL"
            )
        else:
            logger.warning(
                f"⚠️ Failed to update remote: {update_result.error_message}"
            )
    else:
        # Remote doesn't exist, add it with clean URL
        logger.info(f"➕ Adding new remote '{remote_name}' with clean URL")
        add_result: SubprocessResult = (
            git_service.run_git_command_with_separate_dirs(
                ["remote", "add", remote_name, clean_url],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name="add git remote",
            )
        )
        if add_result.success:
            logger.info(
                f"✅ Successfully added remote '{remote_name}' with clean URL"
            )
        else:
            logger.warning(
                f"⚠️ Failed to add remote: {add_result.error_message}"
            )


def build_session_init_message(
    server_name: str, sync_attempted: bool, sync_result: Optional[Any]
) -> str:
    """Build success message for session initialization."""
    message_parts = [f"{server_name} session initialized successfully"]

    if sync_attempted:
        if sync_result and sync_result.success:
            message_parts.append("Repository synced with remote history")
        else:
            message_parts.append("Repository initialized but sync had warnings")

    return ". ".join(message_parts)
