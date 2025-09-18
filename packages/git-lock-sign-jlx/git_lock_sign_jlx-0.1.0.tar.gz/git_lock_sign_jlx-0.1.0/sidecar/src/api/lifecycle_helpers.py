"""
Helper functions for the file lifecycle endpoint.

This module contains all helper functions related to file lifecycle operations,
including commit message generation, file deletion handling, rename operations, and auto-push.
"""

import logging
import os
import traceback
from typing import Any, Dict, Optional, Tuple

from ..models.requests import FileLifecycleCommitRequest
from ..services.config_service import ConfigService
from ..services.git_service import GitService
from ..services.git_service.commit_service import CommitMessageGenerator
from ..services.provider_services import ProviderService
from ..services.subprocess_util import SubprocessErrorMode, SubprocessResult
from ..services.logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


def generate_lifecycle_commit_message(request: FileLifecycleCommitRequest) -> str:
    """Generate commit message based on lifecycle event."""
    message_generator = CommitMessageGenerator()
    return message_generator.generate_lifecycle_commit_message(
        lifecycle_event=request.lifecycle_event,
        file_path=request.file_path,
        old_file_path=request.old_file_path
    )


def handle_file_deletion(request: FileLifecycleCommitRequest, git_service: GitService) -> None:
    """Handle file deletion staging."""
    try:
        # Translate JupyterLab path to sidecar path for delete operation
        sidecar_delete_path = git_service.translate_jupyterlab_path_to_sidecar(request.file_path)
        repo = git_service.get_repository(sidecar_delete_path)
        if repo:
            repo_root = str(repo.working_dir)
            rel_path = os.path.relpath(sidecar_delete_path, repo_root)
            
            # First check if the file is tracked by git
            status_result = git_service.run_git_command_with_separate_dirs(
                ["status", "--porcelain", rel_path],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check file git status"
            )
            
            git_status_line = status_result.stdout.strip() if status_result.success else ""
            logger.info(f"Git status for deletion: '{git_status_line}'")
            
            if not git_status_line:
                # File is not tracked by git - no commit needed
                logger.info(f"File {rel_path} is not tracked by git - skipping deletion commit")
                return None
            
            # Use git rm to stage the deletion (for files that are tracked)
            rm_result: SubprocessResult = git_service.run_git_command_with_separate_dirs(
                ["rm", rel_path],
                error_mode=SubprocessErrorMode.LENIENT,  # Use lenient mode 
                timeout=30,
                operation_name="stage file deletion"
            )
            
            if rm_result.success:
                logger.info(f"Staged file deletion: {rel_path}")
            else:
                logger.warning(f"Failed to stage file deletion: {rm_result.error_message}")
                # If git rm fails, the file likely wasn't tracked - no commit needed
                return None
    except Exception as e:
        logger.warning(f"Failed to stage file deletion: {str(e)}")
        # Continue with commit anyway - file might already be staged or deleted


def handle_file_rename_commits(request: FileLifecycleCommitRequest, 
                               git_service: GitService) -> Tuple[bool, Optional[str], Any]:
    """Handle file rename as two separate commits."""
    logger.info("Creating two commits for rename operation")
    
    # Validate old_file_path
    if not request.old_file_path:
        logger.error("old_file_path is required for rename events")
        raise ValueError("old_file_path is required for rename events")
    
    # Get repository root for staging operations
    repo = git_service.get_repository(request.file_path)
    if not repo:
        logger.error("Could not get repository for rename operation")
        raise ValueError("Could not get repository for rename operation")
    
    repo_root = str(repo.working_dir)
    
    # Translate JupyterLab paths to sidecar paths BEFORE calculating relative paths
    sidecar_new_path = git_service.translate_jupyterlab_path_to_sidecar(request.file_path)
    sidecar_old_path = git_service.translate_jupyterlab_path_to_sidecar(request.old_file_path)
    
    new_rel_path = os.path.relpath(sidecar_new_path, repo_root)
    old_rel_path = os.path.relpath(sidecar_old_path, repo_root)
    
    logger.info(f"Repository root: {repo_root}")
    logger.info(f"Old file path: {request.old_file_path} -> {sidecar_old_path} -> {old_rel_path}")
    logger.info(f"New file path: {request.file_path} -> {sidecar_new_path} -> {new_rel_path}")
    logger.info(f"Creating two commits for rename: {old_rel_path} -> {new_rel_path}")
    
    # FIRST COMMIT: Delete the old file (only if it was tracked)
    # First check if the old file is tracked by git
    status_result = git_service.run_git_command_with_separate_dirs(
        ["status", "--porcelain", old_rel_path],
        error_mode=SubprocessErrorMode.SILENT,
        timeout=10,
        operation_name="check old file git status for rename"
    )
    
    git_status_line = status_result.stdout.strip() if status_result.success else ""
    logger.info(f"Git status for old file in rename: '{git_status_line}'")
    
    # Create message generator for both deletion and creation commits
    message_generator = CommitMessageGenerator()
    
    if git_status_line:
        # Old file is tracked - create deletion commit
        delete_commit_message = message_generator.generate_lifecycle_commit_message(
            lifecycle_event="rename",
            file_path=request.file_path,
            old_file_path=request.old_file_path
        )
        
        logger.info(f"First commit (delete): {delete_commit_message}")
        
        # Stage only the deletion for the first commit
        stage_delete_result: SubprocessResult = git_service.run_git_command_with_separate_dirs(
            ["rm", old_rel_path],
            error_mode=SubprocessErrorMode.LENIENT,
            timeout=30,
            operation_name="stage file removal for rename"
        )
        if stage_delete_result.success:
            logger.info(f"Staged deletion of old file: {old_rel_path}")
        else:
            logger.warning(f"Failed to stage file deletion: {stage_delete_result.error_message}")
            # If staging fails, the old file likely wasn't tracked - skip deletion commit
            git_status_line = ""
    else:
        # Old file is not tracked by git - skip deletion commit
        logger.info(f"Old file {old_rel_path} is not tracked by git - skipping deletion commit for rename")
    
    # Stage the addition of the new file
    stage_add_result: SubprocessResult = git_service.run_git_command_with_separate_dirs(
        ["add", new_rel_path],
        error_mode=SubprocessErrorMode.STRICT,
        timeout=30,
        operation_name="stage file addition for rename"
    )
    if stage_add_result.success:
        logger.info(f"Staged addition of new file: {new_rel_path}")
    else:
        logger.warning(f"Failed to stage file addition: {stage_add_result.error_message}")
        raise ValueError(f"Failed to stage file addition: {stage_add_result.error_message}")
    
    # Create single rename commit message
    if git_status_line:
        # Old file was tracked - use rename message
        rename_commit_message = message_generator.generate_lifecycle_commit_message(
            lifecycle_event="rename",
            file_path=request.file_path,
            old_file_path=request.old_file_path
        )
        logger.info(f"Rename commit message: {rename_commit_message}")
    else:
        # Old file was not tracked - use create message since it's essentially a new file
        rename_commit_message = message_generator.generate_lifecycle_commit_message(
            lifecycle_event="create",
            file_path=request.file_path
        )
        logger.info(f"Create commit message (untracked rename): {rename_commit_message}")
    
    # Commit both the deletion (if applicable) and addition in a single commit
    logger.info(f"Committing rename using sidecar new file path: {sidecar_new_path}")
    commit_result = git_service.commit_notebook(sidecar_new_path, rename_commit_message)
    
    if not commit_result.success:
        logger.error(f"Rename commit failed: {commit_result.error}")
        raise ValueError(f"Rename commit failed: {commit_result.error}")
    
    logger.info(f"Rename commit successful: {commit_result.commit_hash}")
    
    return True, None, commit_result


async def handle_lifecycle_auto_push(request: FileLifecycleCommitRequest, sidecar_file_path: str, 
                                     services: Dict[str, Any]) -> None:
    """Handle auto-push for lifecycle events."""
    if not request.trigger_auto_push:
        return
    
    config_service: ConfigService = services["config_service"]
    logger.info(f"Triggering auto-push for lifecycle event: {request.lifecycle_event}")
    logger.info(f"Git server configured: {config_service.git_server}")
    
    try:

        provider_service: ProviderService = services[f"{config_service.git_server}_service"]
        logger.info(f"Using {config_service.git_server} service for auto-push.")
        push_result = await provider_service.push_notebook(sidecar_file_path)
        
        logger.info(f"Push result object: {push_result}")
        logger.info(f"Push result: success={getattr(push_result, 'success', 'N/A')}, error={getattr(push_result, 'error', 'N/A')}")
        
        # Check if push was successful
        if hasattr(push_result, 'success') and push_result.success:
            logger.info("✅ Lifecycle auto-push completed successfully")
            logger.info(f"Push message: {getattr(push_result, 'message', 'N/A')}")
            logger.info(f"Repository URL: {getattr(push_result, 'repository_url', 'N/A')}")
        else:
            error_msg = getattr(push_result, 'error', 'Unknown error')
            logger.error(f"❌ Lifecycle auto-push failed: {error_msg}")
            logger.error(f"Push result details: {push_result}")
            # Don't fail the commit response since commit was successful
    except Exception as e:
        logger.error(f"Error during lifecycle auto-push: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't fail the commit response since commit was successful
