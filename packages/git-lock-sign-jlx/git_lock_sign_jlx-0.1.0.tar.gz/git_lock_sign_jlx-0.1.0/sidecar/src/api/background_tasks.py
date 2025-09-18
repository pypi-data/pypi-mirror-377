"""
Background task functions for the API.

This module contains all background task functions that are executed asynchronously,
including debounced commit and push operations.
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict

from ..services.config_service import ConfigService
from ..services.git_service import GitService
from ..services.git_service.commit_service import CommitMessageGenerator
from ..services.logger_util import default_logger_config
from ..services.provider_services import ProviderService
from ..services.subprocess_util import SubprocessErrorMode

logger = logging.getLogger(__name__)
default_logger_config(logger)


async def execute_debounced_commit(
    notebook_path: str, commit_message: str, services: Dict[str, Any]
) -> None:
    """Execute a debounced commit operation."""
    try:
        git_service: GitService = services["git_service"]
        await asyncio.sleep(services["config_service"].commit_debounce_seconds)

        result = git_service.commit_notebook(notebook_path, commit_message)

        if result.success:
            logger.info(
                f"Debounced commit completed successfully for {notebook_path}: {result.commit_hash}"
            )
        else:
            logger.error(
                f"Debounced commit failed for {notebook_path}: {result.message}"
            )
            if result.error:
                logger.error(f"Commit error details: {result.error}")

    except Exception as e:
        logger.error(f"Debounced commit failed with exception: {str(e)}")


async def execute_debounced_push(
    notebook_path: str,
    services: Dict[str, Any],
    auto_commit_before_push: bool = False,
) -> None:
    """Execute a debounced push operation."""
    try:
        # If auto_commit_before_push is enabled, check for uncommitted changes and commit them
        if auto_commit_before_push:
            git_service: GitService = services["git_service"]

            logger.info(
                "Debounced push: Auto-commit before push enabled - checking for uncommitted changes"
            )

            # Longer delay to ensure file system changes are visible to git
            logger.info("Debounced push: Waiting for file system sync...")
            time.sleep(0.5)  # Increased to 500ms delay

            # Additional debugging: check file timestamps
            try:
                if os.path.exists(notebook_path):
                    file_stat = os.stat(notebook_path)
                    logger.info(
                        f"Debounced push: File modification time before git check: {file_stat.st_mtime}"
                    )
                    logger.info(
                        f"Debounced push: File size before git check: {file_stat.st_size} bytes"
                    )
                else:
                    logger.error(
                        f"Debounced push: File does not exist at expected path: {notebook_path}"
                    )
            except Exception as e:
                logger.warning(
                    f"Debounced push: Could not check file stats: {str(e)}"
                )

            # Additional debugging: check overall repository status
            try:
                repo = git_service.get_repository(notebook_path)
                if repo:
                    overall_status_result = (
                        git_service.run_git_command_with_separate_dirs(
                            ["status", "--porcelain"],
                            error_mode=SubprocessErrorMode.SILENT,
                            timeout=10,
                            operation_name="check debounced push git status",
                        )
                    )

                    if overall_status_result.success:
                        overall_status = overall_status_result.stdout.strip()
                        if overall_status:
                            logger.info(
                                "Debounced push: Overall git status shows changes:"
                            )
                            for line in overall_status.split("\n"):
                                logger.info(f"Debounced push:  {line}")
                        else:
                            logger.info(
                                "Debounced push: Overall git status shows repository is clean"
                            )
                    else:
                        logger.warning(
                            f"Debounced push: Could not get overall git status: {overall_status_result.error_message}"
                        )
            except Exception as e:
                logger.warning(
                    f"Debounced push: Error checking overall git status: {str(e)}"
                )

            if git_service.has_uncommitted_changes(notebook_path):
                # Check if the file exists on disk before attempting operations
                file_exists = os.path.exists(notebook_path)
                logger.info(
                    f"Debounced push: Found uncommitted changes for {notebook_path} (file exists: {file_exists})"
                )

                # If the file doesn't exist, this might be a deletion that needs to be staged
                if not file_exists:
                    logger.info("Debounced push: File doesn't exist on disk - checking if this is a deletion")
                    
                    try:
                        repo = git_service.get_repository(notebook_path)
                        if repo:
                            repo_root = str(repo.working_dir)
                            notebook_rel_path = os.path.relpath(notebook_path, repo_root)
                            
                            # Check if this file was tracked in git before
                            log_result = git_service.run_git_command_with_separate_dirs(
                                ["log", "--oneline", "-1", "--", notebook_rel_path],
                                error_mode=SubprocessErrorMode.SILENT,
                                timeout=10,
                                operation_name="check if deleted file was tracked"
                            )
                            
                            if log_result.success and log_result.stdout.strip():
                                logger.info(f"Debounced push: File {notebook_rel_path} was tracked but doesn't exist - staging deletion")
                                
                                # Stage the deletion
                                rm_result = git_service.run_git_command_with_separate_dirs(
                                    ["rm", notebook_rel_path],
                                    error_mode=SubprocessErrorMode.LENIENT,
                                    timeout=10,
                                    operation_name="stage file deletion"
                                )
                                
                                if rm_result.success:
                                    logger.info("Debounced push: Successfully staged file deletion")
                                else:
                                    logger.warning(f"Debounced push: Failed to stage deletion: {rm_result.stderr}")
                    except Exception as e:
                        logger.warning(f"Debounced push: Error checking deletion status: {str(e)}")

                # Generate smart auto-commit message based on operation type
                message_generator = CommitMessageGenerator()
                commit_message = message_generator.generate_smart_auto_commit_message(
                    notebook_path, git_service
                )

                # Use simple commit to avoid interfering with user's saved content
                try:
                    logger.info(
                        "Debounced push: Performing simple auto-commit of saved changes"
                    )
                    commit_result = git_service.commit_notebook(
                        notebook_path, commit_message
                    )

                    if commit_result.success:
                        logger.info(
                            f"Debounced push: Auto-commit successful: {commit_result.commit_hash}"
                        )
                        logger.info(f"Debounced push: Commit message used: {commit_message}")
                    else:
                        logger.warning(
                            f"Debounced push: Auto-commit failed: {commit_result.error}"
                        )
                        # Continue with push anyway - this is best effort

                except Exception as e:
                    logger.warning(
                        f"Debounced push: Error during auto-commit: {str(e)}"
                    )
                    # Continue with push anyway - this is best effort
            else:
                logger.info(
                    "Debounced push: No uncommitted changes found - proceeding directly to push"
                )

        await asyncio.sleep(services["config_service"].push_debounce_seconds)

        # Determine which git server to use based on configuration
        config_service: ConfigService = services["config_service"]
        git_server = config_service.git_server


        provider_service: ProviderService = services[f"{git_server}_service"]

        result = await provider_service.push_notebook(notebook_path)

        if result.success:
            logger.info(
                f"Debounced push completed successfully for {notebook_path}"
            )
        else:
            logger.error(
                f"Debounced push failed for {notebook_path}: {result.error}"
            )

    except Exception as e:
        logger.error(f"Debounced push failed: {str(e)}")
