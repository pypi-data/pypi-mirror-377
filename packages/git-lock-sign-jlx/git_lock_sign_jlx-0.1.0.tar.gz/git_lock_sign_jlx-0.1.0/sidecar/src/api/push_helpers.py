"""
Helper functions for the push endpoint.

This module contains all helper functions related to push operations,
including auto-commit before push, debouncing checks, and push execution.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict

from ..models.requests import PushRequest
from ..services.config_service import ConfigService
from ..services.git_service import GitService
from ..services.git_service.commit_service import CommitMessageGenerator
from ..services.provider_services import ProviderService
from ..services.subprocess_util import SubprocessErrorMode
from ..services.logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


def generate_smart_auto_commit_message(notebook_path: str, git_service: GitService) -> str:
    """Generate auto-commit message based on the type of operation (delete, update, etc.)."""
    message_generator = CommitMessageGenerator()
    return message_generator.generate_smart_auto_commit_message(notebook_path, git_service)


async def handle_auto_commit_before_push(request: PushRequest, services: Dict[str, Any]) -> None:
    """Handle auto-commit before push if enabled."""
    if not request.auto_commit_before_push:
        return
    
    git_service: GitService = services["git_service"]
    
    # Longer delay to ensure file system changes are visible to git
    time.sleep(0.5)  # Increased to 500ms delay
    
    # Check if the file exists on disk before attempting any operations
    file_exists = os.path.exists(request.notebook_path)
    
    if git_service.has_uncommitted_changes(request.notebook_path):
        logger.info(f"Found uncommitted changes for {request.notebook_path} (file exists: {file_exists})")
        
        # If the file doesn't exist, this is likely a deletion that wasn't properly committed
        if not file_exists:
            logger.info("File doesn't exist on disk - checking if this is a deletion that needs to be staged")
            
            # Try to get repository info for better detection
            try:
                repo = git_service.get_repository(request.notebook_path)
                if repo:
                    repo_root = str(repo.working_dir)
                    notebook_rel_path = os.path.relpath(request.notebook_path, repo_root)
                    
                    # Check if this file was tracked in git before
                    log_result = git_service.run_git_command_with_separate_dirs(
                        ["log", "--oneline", "-1", "--", notebook_rel_path],
                        error_mode=SubprocessErrorMode.SILENT,
                        timeout=10,
                        operation_name="check if deleted file was tracked"
                    )
                    
                    if log_result.success and log_result.stdout.strip():
                        logger.info(f"File {notebook_rel_path} was tracked in git but doesn't exist - treating as deletion")
                        
                        # Stage the deletion
                        rm_result = git_service.run_git_command_with_separate_dirs(
                            ["rm", notebook_rel_path],
                            error_mode=SubprocessErrorMode.LENIENT,
                            timeout=10,
                            operation_name="stage file deletion"
                        )
                        
                        if rm_result.success:
                            logger.info("Successfully staged file deletion")
                        else:
                            logger.warning(f"Failed to stage deletion: {rm_result.stderr}")
            except Exception as e:
                logger.warning(f"Error checking deletion status: {str(e)}")
        else:
            # File exists - check content normally
            try:
                with open(request.notebook_path, encoding="utf-8") as f:
                    file_content = f.read()
                
                # Parse as JSON to check cells
                try:
                    nb_content = json.loads(file_content)
                    # cells = nb_content.get("cells", [])
                except json.JSONDecodeError:
                    # Could not parse notebook JSON
                    pass
            except Exception:
                # Could not read file content
                pass
        
        # Generate smart auto-commit message based on operation type
        commit_message = generate_smart_auto_commit_message(request.notebook_path, git_service)
        
        # Use simple commit to avoid interfering with user's saved content
        try:
            commit_result = git_service.commit_notebook(request.notebook_path, commit_message)
            
            if commit_result.success:
                logger.info("✅ Auto-commit before push completed successfully")
                logger.info(f"Commit message used: {commit_message}")
            else:
                logger.warning(f"⚠️ Auto-commit before push failed: {commit_result.error}")
        except Exception as e:
            logger.error(f"❌ Auto-commit before push error: {str(e)}")


def should_debounce_push(request: PushRequest, services: Dict[str, Any]) -> bool:
    """Check if push should be debounced."""
    if not request.auto_push:
        return False
    
    debounce_service = services["debounce_service"]
    config_service: ConfigService = services["config_service"]
    
    debounce_key = f"push:{request.notebook_path}"
    return debounce_service.should_debounce(
        debounce_key, config_service.push_debounce_seconds
    )


async def execute_push_operation(request: PushRequest, services: Dict[str, Any]) -> Any:
    """Execute the actual push operation for the configured git server."""
    config_service: ConfigService = services["config_service"]
    git_server = config_service.git_server
    
    provider_service: ProviderService = services[f"{git_server}_service"]
    return await provider_service.push_notebook(request.notebook_path)
