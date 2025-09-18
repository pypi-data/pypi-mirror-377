"""
Helper functions for the commit endpoint.

This module contains all helper functions related to commit operations,
including debouncing, auto-commit message generation, pre-push logic, and commit operations.
"""

import logging
from typing import Any, Dict

from ..models.requests import CommitRequest
from ..services.config_service import ConfigService
from ..services.git_service import GitService
from ..services.git_service.commit_service import CommitMessageGenerator
from ..services.git_service.models import GitOperationResult
from ..services.provider_services import ProviderService
from ..services.logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


def should_debounce_commit(request: CommitRequest, services: Dict[str, Any]) -> bool:
    """Check if commit should be debounced."""
    debounce_service = services["debounce_service"]
    config_service: ConfigService = services["config_service"]
    
    debounce_key = f"commit:{request.notebook_path}"
    return debounce_service.should_debounce(
        debounce_key, config_service.commit_debounce_seconds
    )


def generate_auto_commit_message(request: CommitRequest, config_service: ConfigService) -> str:
    """Generate auto-commit message based on configuration."""
    message_generator = CommitMessageGenerator(config_service)
    return message_generator.generate_auto_commit_message(
        cell_content_preview=request.cell_content_preview,
        execution_count=request.execution_count
    )


async def handle_pre_push_logic(request: CommitRequest, services: Dict[str, Any]) -> None:
    """Handle pre-push logic: Check for existing unpushed commits from OTHER files and push them first."""
    git_service: GitService = services["git_service"]
    config_service: ConfigService = services["config_service"]
    
    if git_service.has_unpushed_commits_from_other_files(request.notebook_path):
        try:
            git_server = config_service.git_server
            provider_service: ProviderService = services[f"{git_server}_service"]
            push_result = await provider_service.push_notebook(request.notebook_path)
            
            if not push_result.success:
                logger.warning(f"⚠️ Pre-commit auto-push failed: {push_result.error}")
        
        except Exception as e:
            logger.warning(f"⚠️ Pre-commit auto-push error: {str(e)}")


def perform_commit_operation(request: CommitRequest, commit_message: str, include_metadata: bool, services: Dict[str, Any]) -> Any:
    """Perform the actual commit operation based on parameters."""
    git_service: GitService = services["git_service"]
    
    if include_metadata and request.notebook_content:
        # Full commit with metadata
        notebook_service = services["notebook_service"]
        gpg_service = services["gpg_service"]
        
        return git_service.commit_notebook_with_metadata(
            request.notebook_path,
            commit_message,
            notebook_service,
            gpg_service,
            request.notebook_content,
        )
    elif request.notebook_content and not include_metadata:
        # CRITICAL FIX: Save notebook content to disk before simple commit
        notebook_service = services["notebook_service"]
        
        # Save the provided notebook content to disk
        save_success = notebook_service.save_notebook_content(
            request.notebook_path, request.notebook_content
        )
        
        if not save_success:
            # Return a proper GitOperationResult with error
            return GitOperationResult(
                success=False,
                message="Failed to save notebook content to disk",
                error="Failed to save notebook content to disk"
            )
        
        # Now do simple commit with the saved content
        return git_service.commit_notebook(request.notebook_path, commit_message)
    else:
        # Simple commit without metadata (and no content provided)
        return git_service.commit_notebook(request.notebook_path, commit_message)
