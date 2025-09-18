"""
API Routes for CELN Sidecar Service - Clean Version

Handles all git operations for JupyterLab notebooks including:
- Git initialization
- Auto-commit on cell execution
- Auto-push on notebook save
- Manual git operations (lock, unlock, commit, push)

This file contains clean endpoint implementations that delegate to helper modules.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from ..models.requests import (
    CommitRequest,
    FileLifecycleCommitRequest,
    GitInitRequest,
    LockRequest,
    PushRequest,
    UnlockRequest,
)
from ..models.responses import (
    CommitResponse,
    GitInitResponse,
    LockResponse,
    PushResponse,
    StatusResponse,
    UnlockResponse,
    UserInfoResponse,
)
from ..services.config_service import ConfigService
from ..services.git_service import GitService
from ..services.provider_services import ProviderService

# Import helper modules
from . import background_tasks as bg_tasks
from . import commit_helpers
from . import lifecycle_helpers
from . import provision_helpers
from . import push_helpers
from . import session_helpers

logger = logging.getLogger(__name__)
router = APIRouter()


def get_services(request: Request):
    """Dependency to get services from app state."""
    return {
        "git_service": request.app.state.git_service,
        "gitlab_service": request.app.state.gitlab_service,
        "gitea_service": request.app.state.gitea_service,
        "github_enterprise_service": request.app.state.github_enterprise_service,
        "debounce_service": request.app.state.debounce_service,
        "config_service": request.app.state.config_service,
        "notebook_service": request.app.state.notebook_service,
        "gpg_service": request.app.state.gpg_service,
    }


# ============================================================================
# MAIN ENDPOINT IMPLEMENTATIONS
# ============================================================================

@router.post("/provision", response_model=GitInitResponse)
async def provision_repository(
    request: GitInitRequest, services: Dict[str, Any] = Depends(get_services)
) -> GitInitResponse:
    """
    Provision repository using the configured git server (GitLab, Gitea, or GitHub Enterprise).
    This is called by frontend after git-init to set up git server integration.
    """
    try:
        git_service: GitService = services["git_service"]
        config_service: ConfigService = services["config_service"]

        logger.info("🚀 Starting provision operation")

        # Ensure this is a git repository
        repo = git_service.get_repository(request.notebook_path)
        if not repo:
            raise HTTPException(status_code=400, detail="Not a git repository")

        repo_path = str(repo.working_dir)

        # Get user info to check if they're already registered
        user_info = git_service.get_user_info(request.notebook_path)

        # Determine which git server to use based on configuration
        git_server = config_service.git_server

        # Check if user is already registered and perform session sync if needed
        user_registered = provision_helpers.check_user_registration(git_server, user_info.email, services)
        sync_attempted = False
        sync_result = None

        # If user is already registered, attempt to sync with remote history
        if user_registered:
            sync_result = await provision_helpers.attempt_session_sync(git_server, repo_path, services)
            sync_attempted = True

        # Proceed with repository provisioning
        success, server_name, repository_url, error = await provision_helpers.provision_git_server(git_server, repo_path, services)

        if not success:
            logger.error(f"{server_name} provisioning failed: {error}")
            return GitInitResponse(
                success=False,
                message=f"{server_name} provisioning failed",
                repository_path=repo_path,
                repository_url=None,
                error=error,
            )

        # Build success message including sync information
        success_message = provision_helpers.build_provision_message(server_name, sync_attempted, sync_result)

        # Log successful provision
        logger.info(f"✅ {server_name} repository provisioned successfully")

        return GitInitResponse(
            success=True,
            message=success_message,
            repository_path=repo_path,
            repository_url=repository_url,
            error=None,
        )

    except Exception as e:
        logger.error(f"❌ Provision operation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Provisioning failed: {str(e)}"
        )


@router.post("/git-init", response_model=GitInitResponse)
async def git_init(
    request: GitInitRequest, services: Dict[str, Any] = Depends(get_services)
) -> GitInitResponse:
    """
    Initialize git repository if it doesn't exist.
    Sets up GitLab remote and user configuration.
    """
    try:
        git_service: GitService = services["git_service"]

        logger.info("🚀 Starting git init operation")

        # Check if already a git repository
        repo = git_service.get_repository(request.notebook_path)
        if repo:
            return GitInitResponse(
                success=True,
                message="Git repository already exists",
                repository_path=str(repo.working_dir),
                repository_url=None,
                error=None,
            )

        # Initialize git repository
        repo_path = git_service.init_repository(request.notebook_path)

        return GitInitResponse(
            success=True,
            message="Git repository initialized successfully. Call /provision to set up git server integration.",
            repository_path=repo_path,
            repository_url=None,
            error=None,
        )

    except Exception as e:
        logger.error(f"❌ Git init operation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Git initialization failed: {str(e)}"
        )


@router.post("/commit", response_model=CommitResponse)
async def commit_notebook(
    request: CommitRequest, services: Dict[str, Any] = Depends(get_services)
) -> CommitResponse:
    """Commit notebook changes with optional metadata."""
    try:
        git_service: GitService = services["git_service"]
        config_service: ConfigService = services["config_service"]

        logger.info("🚀 Starting commit operation")

        # Ensure .gitignore exists for this repository (for existing repos that might not have it)
        git_service.ensure_gitignore_exists(request.notebook_path)

        # Generate commit message for auto-commits if not provided
        commit_message = request.commit_message
        if not commit_message and request.auto_commit:
            commit_message = commit_helpers.generate_auto_commit_message(request, config_service)

        # Ensure we have a commit message (either provided or auto-generated)
        if not commit_message:
            return CommitResponse(
                success=False,
                message="Commit message is required",
                commit_hash=None,
                signed=False,
                debounced=False,
                metadata=None,
                content_hash=None,
                error="Commit message is required",
            )

        # Check environment variable for default metadata inclusion
        default_include_metadata = config_service.include_metadata

        # Use request parameter if provided, otherwise use environment default
        include_metadata = getattr(
            request, "include_metadata", default_include_metadata
        )

        # Check if this commit should be debounced
        if commit_helpers.should_debounce_commit(request, services):
            return CommitResponse(
                success=True,
                message="Commit skipped due to debouncing",
                commit_hash=None,
                signed=False,
                debounced=True,
                metadata=None,
                content_hash=None,
                error=None,
            )

        # Pre-push logic: Check for existing unpushed commits from OTHER files and push them first
        await commit_helpers.handle_pre_push_logic(request, services)

        # Perform the actual commit operation
        result = commit_helpers.perform_commit_operation(request, commit_message, include_metadata, services)

        return CommitResponse(
            success=result.success,
            message=result.message,
            commit_hash=result.commit_hash,
            signed=result.signed,
            debounced=False,
            metadata=result.metadata if include_metadata else None,
            content_hash=result.content_hash if include_metadata else None,
            error=result.error if not result.success else None,
        )

    except Exception as e:
        logger.error(f"❌ Commit operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}")


@router.post("/push", response_model=PushResponse)
async def push_notebook(
    request: PushRequest,
    background_tasks: BackgroundTasks,
    services: Dict[str, Any] = Depends(get_services),
) -> PushResponse:
    """
    Push committed changes to the configured git server (GitLab, Gitea, or GitHub Enterprise).
    Supports debouncing to prevent spam pushes.
    Can optionally auto-commit uncommitted changes before pushing.
    """
    try:
        logger.info("🚀 Starting push operation")

        # If auto_commit_before_push is enabled, check for uncommitted changes and commit them
        await push_helpers.handle_auto_commit_before_push(request, services)

        # Check if this is an auto-push that should be debounced
        if push_helpers.should_debounce_push(request, services):
            # Schedule debounced push
            background_tasks.add_task(
                bg_tasks.execute_debounced_push,
                request.notebook_path,
                services,
                request.auto_commit_before_push,
            )

            return PushResponse(
                success=True,
                message="Push scheduled",
                repository_url=None,
                debounced=True,
                error=None,
            )

        # Execute immediate push for manual operations
        result = await push_helpers.execute_push_operation(request, services)

        return PushResponse(
            success=result.success,
            message=result.message or "Push operation completed",
            repository_url=result.repository_url,
            debounced=False,
            error=result.error if not result.success else None,
        )

    except Exception as e:
        logger.error(f"❌ Push operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Push failed: {str(e)}")


@router.post("/lock", response_model=LockResponse)
async def lock_notebook(
    request: LockRequest, services: Dict[str, Any] = Depends(get_services)
) -> LockResponse:
    """Lock notebook with commit and signing."""
    try:
        git_service: GitService = services["git_service"]
        notebook_service = services["notebook_service"]
        gpg_service = services["gpg_service"]

        logger.info("🚀 Starting lock operation")

        result = git_service.lock_notebook(
            request.notebook_path,
            request.notebook_content,
            request.commit_message,
            notebook_service,
            gpg_service,
        )

        return LockResponse(
            success=result.success,
            message=result.message,
            metadata=result.metadata,
            commit_hash=result.commit_hash,
            signed=result.signed,
            error=result.error if not result.success else None,
        )

    except Exception as e:
        logger.error(f"Lock failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lock failed: {str(e)}")


@router.post("/unlock", response_model=UnlockResponse)
async def unlock_notebook(
    request: UnlockRequest, services: Dict[str, Any] = Depends(get_services)
) -> UnlockResponse:
    """Unlock notebook after signature verification."""
    try:
        git_service: GitService = services["git_service"]
        notebook_service = services["notebook_service"]
        gpg_service = services["gpg_service"]

        logger.info(f"Unlock request for: {request.notebook_path}")

        result = git_service.unlock_notebook(
            request.notebook_path,
            request.notebook_content,
            notebook_service,
            gpg_service,
        )

        return UnlockResponse(
            success=result.success,
            message=result.message,
            signature_valid=True,  # TODO: Return actual signature validation result
            error=result.error if not result.success else None,
        )

    except Exception as e:
        logger.error(f"Unlock failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unlock failed: {str(e)}")


@router.get("/status", response_model=StatusResponse)
async def get_status(
    notebook_path: str, services: Dict[str, Any] = Depends(get_services)
) -> StatusResponse:
    """Get repository and notebook status."""
    try:
        git_service: GitService = services["git_service"]

        status = git_service.get_status(notebook_path)

        return StatusResponse(
            success=True,
            is_git_repository=status.is_git_repository,
            is_locked=status.is_locked,
            repository_path=status.repository_path,
            signature_metadata=status.signature_metadata,
            last_commit_hash=status.last_commit_hash,
            error=None,
        )

    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Status check failed: {str(e)}"
        )


@router.get("/user-info", response_model=UserInfoResponse)
async def get_user_info(
    notebook_path: str, services: Dict[str, Any] = Depends(get_services)
) -> UserInfoResponse:
    """Get git user information for a specific notebook path."""
    try:
        git_service: GitService = services["git_service"]
        user_info = git_service.get_user_info(notebook_path)
        return UserInfoResponse(
            success=True,
            user_name=user_info.name,
            user_email=user_info.email,
            gpg_key_id=user_info.gpg_key_id,
            error=None,
        )
    except Exception as e:
        logger.error(f"User info failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"User info failed: {str(e)}"
        )


@router.get("/config")
async def get_config(
    services: Dict[str, Any] = Depends(get_services),
) -> Dict[str, Any]:
    """Get current sidecar configuration including metadata settings."""
    config_service = services["config_service"]

    # Use ConfigService for all configuration values to ensure consistency
    config = {
        "include_metadata": config_service.include_metadata,
        "commit_debounce_seconds": config_service.commit_debounce_seconds,
        "push_debounce_seconds": config_service.push_debounce_seconds,
        "cell_execution_detection_delay_ms": config_service.cell_execution_detection_delay_ms,
        "auto_save_interval_minutes": config_service.auto_save_interval_minutes,
        "enable_commit_button": config_service.enable_commit_button,
        "enable_push_button": config_service.enable_push_button,
        "enable_lock_button": config_service.enable_lock_button,
        "enable_file_creation_tracking": config_service.enable_file_creation_tracking,
        # "sidecar_host": config_service.sidecar_host,
        # "sidecar_port": config_service.sidecar_port,
        "auto_save_enabled": config_service.auto_save_enabled,
        "debug_mode": config_service.debug_mode,
        "health_check_interval_ms": config_service.health_check_interval_ms,
        "health_check_timeout_ms": config_service.health_check_timeout_ms,
        "api_request_timeout_ms": config_service.api_request_timeout_ms,
        "notification_auto_dismiss_ms": config_service.notification_auto_dismiss_ms,
        "create_work_subdirectory": config_service.create_work_subdirectory,
        "message": "Configuration loaded from environment variables with fallbacks",
        "success": True,
    }

    # Log the configuration for debugging
    logger.info("Config retrieved from sidecar endpoint")

    return config


@router.post("/sync", response_model=StatusResponse)
async def sync_with_remote(
    notebook_path: str, services: Dict[str, Any] = Depends(get_services)
) -> StatusResponse:
    """
    Manually sync local repository with remote history.
    
    This endpoint allows manual synchronization of the local repository
    with the remote to ensure they are identical. Useful when users want
    to force sync their local state with the remote.
    """
    try:
        git_service: GitService = services["git_service"]
        provider_service: ProviderService = services["provider_service"]
        
        logger.info(f"Manual sync request for: {notebook_path}")
        
        # Ensure this is a git repository
        repo = git_service.get_repository(notebook_path)
        if not repo:
            raise HTTPException(status_code=400, detail="Not a git repository")

        repo_path = str(repo.working_dir)
        
        # Perform the sync
        sync_result = await git_service.sync_with_remote_on_session_start(repo_path, provider_service)
        
        return StatusResponse(
            success=sync_result.success,
            is_git_repository=True,
            is_locked=False,  # Not relevant for sync operation
            repository_path=repo_path,
            signature_metadata=None,  # Not relevant for sync operation
            last_commit_hash=None,  # Could be updated to show new commit hash
            error=sync_result.error if not sync_result.success else None,
        )

    except Exception as e:
        logger.error(f"Manual sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/validate-sync", response_model=Dict[str, Any])
async def validate_sync_operation(
    workspace_path: str, services: Dict[str, Any] = Depends(get_services)
) -> Dict[str, Any]:
    """
    Validate sync operation to identify potential issues before proceeding.
    
    This endpoint allows users to check the state of their repository before
    performing a sync operation, helping them understand what will happen.
    
    Args:
        workspace_path: Path to the workspace directory
        
    Returns:
        Validation results with warnings, critical issues, and recommendations
    """
    try:
        git_service: GitService = services["git_service"]
        
        logger.info(f"🔍 Sync validation request for workspace: {workspace_path}")
        
        # Ensure workspace path exists
        import os
        if not os.path.exists(workspace_path):
            raise HTTPException(status_code=400, detail="Workspace path does not exist")
        
        # Get repository path
        repo = git_service.get_repository(workspace_path)
        if repo:
            repo_path = str(repo.working_dir)
        else:
            return {
                "valid": False,
                "error": "Not a git repository",
                "recommendations": ["Initialize git repository first"]
            }
        
        # Perform validation
        validation_result = await git_service.validate_sync_operation(repo_path)
        
        logger.info(f"🔍 Sync validation completed: {'✅ Valid' if validation_result['valid'] else '❌ Invalid'}")
        
        return validation_result
        
    except Exception as e:
        logger.error(f"❌ Sync validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/session-init", response_model=GitInitResponse)
async def initialize_session(
    workspace_path: str, services: Dict[str, Any] = Depends(get_services)
) -> GitInitResponse:
    """
    Initialize user session with workspace-level git repository setup.
    
    This endpoint is called when JupyterLab starts up to:
    1. Initialize git repository in workspace if needed
    2. Check if user is registered in remote git server
    3. Sync local repository with remote history if user exists
    4. Provision user and repository as needed
    
    This ensures users start with their remote state synced locally.
    """
    try:
        git_service: GitService = services["git_service"]
        config_service: ConfigService = services["config_service"]

        logger.info(f"🚀 Session initialization request for workspace: {workspace_path}")

        # Handle CREATE_WORK_SUBDIRECTORY configuration with separate git directory structure
        _, work_tree_dir = session_helpers.setup_directory_structure(config_service)
        
        # Use work tree as the actual repo path for git operations
        actual_repo_path = work_tree_dir
        logger.info(f"📁 Work tree path: {actual_repo_path}")
        
        # Step 1: Initialize git repository with separate directory structure
        repo_path = session_helpers.initialize_or_get_repository(git_service, actual_repo_path)

        if not repo_path:
            raise HTTPException(status_code=400, detail="Could not determine work tree root")

        # Step 2: Get user info and check registration status
        user_info = git_service.get_user_info(workspace_path)
        logger.info(f"👤 User info - Name: {user_info.name}, Email: {user_info.email}")
        
        # Determine git server
        git_server = config_service.git_server
        logger.info(f"🌐 Using git server: {git_server}")

        # Step 3: Check if user is already registered
        user_registered = provision_helpers.check_user_registration(git_server, user_info.email, services)
        logger.info(f"📋 User registration status: {'✅ registered' if user_registered else '❌ not registered'}")

        # Step 4: Proceed with repository provisioning FIRST to set up remote connection
        logger.info("🛠️ Proceeding with repository provisioning...")
        
        success, server_name, repository_url, error = await provision_helpers.provision_git_server(git_server, repo_path, services)

        if not success:
            logger.error(f"❌ {server_name} provisioning failed: {error}")
            return GitInitResponse(
                success=False,
                message=f"{server_name} provisioning failed",
                repository_path=repo_path,
                repository_url=None,
                error=error,
            )

        # Step 5: Set up local git remote and perform session sync if user was already registered
        sync_attempted, sync_result = await session_helpers.setup_git_remote_and_sync(
            git_server, repo_path, user_registered, repository_url, services
        )
        
        # Step 6: Push .gitignore commit if user is new (remote was set up during provisioning)
        if not user_registered and repository_url:
            logger.info("🔄 New user - attempting to push .gitignore commit after provisioning...")
            git_service.push_gitignore_commit_if_exists()

        # Build success message including sync information
        success_message = session_helpers.build_session_init_message(server_name, sync_attempted, sync_result)

        # Log successful session initialization
        logger.info(f"✅ {server_name} session initialization completed")
        if repository_url:
            logger.info(f"🌐 Repository URL: {repository_url}")
            logger.info(f"📋 User can access repository at: {repository_url}")

        return GitInitResponse(
            success=True,
            message=success_message,
            repository_path=repo_path,
            repository_url=repository_url,
            error=None,
        )

    except Exception as e:
        logger.error(f"❌ Session initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Session initialization failed: {str(e)}")


@router.post("/file-lifecycle-commit", response_model=CommitResponse)
async def commit_file_lifecycle(
    request: FileLifecycleCommitRequest,
    services: Dict[str, Any] = Depends(get_services),
) -> CommitResponse:
    """Commit file lifecycle events (creation/deletion)."""
    try:
        git_service: GitService = services["git_service"]

        logger.info(
            f"File lifecycle commit request - {request.lifecycle_event}: {request.file_path}"
        )

        # Ensure .gitignore exists for this repository (for existing repos that might not have it)
        # Translate JupyterLab path to sidecar path for .gitignore check
        sidecar_file_path = git_service.translate_jupyterlab_path_to_sidecar(request.file_path)
        git_service.ensure_gitignore_exists(sidecar_file_path)

        # Generate commit message based on lifecycle event
        commit_message = lifecycle_helpers.generate_lifecycle_commit_message(request)
        logger.info(f"Generated lifecycle commit message: {commit_message}")

        # Handle special cases for different lifecycle events
        if request.lifecycle_event == "rename":
            # For rename events, we need to create two commits
            try:
                _, _, commit_result = lifecycle_helpers.handle_file_rename_commits(request, git_service)
            except ValueError as e:
                return CommitResponse(
                    success=False,
                    message=str(e),
                    commit_hash=None,
                    signed=False,
                    debounced=False,
                    metadata=None,
                    content_hash=None,
                    error=str(e),
                )
        else:
            # Normal commit for delete and create events
            # For delete events, stage the deletion first
            if request.lifecycle_event == "delete":
                lifecycle_helpers.handle_file_deletion(request, git_service)
            
            # Now perform the actual commit (for both delete and create events)
            commit_result = git_service.commit_notebook(sidecar_file_path, commit_message)

            if not commit_result.success:
                logger.error(f"Lifecycle commit failed: {commit_result.error}")
                return CommitResponse(
                    success=False,
                    message="Lifecycle commit failed",
                    commit_hash=None,
                    signed=False,
                    debounced=False,
                    metadata=None,
                    content_hash=None,
                    error=commit_result.error,
                )

            logger.info(f"Lifecycle commit successful: {commit_result.commit_hash}")

        # Trigger auto-push if requested (for deletion and rename events)
        await lifecycle_helpers.handle_lifecycle_auto_push(request, sidecar_file_path, services)

        return CommitResponse(
            success=True,
            message=f"File lifecycle commit successful: {request.lifecycle_event}",
            commit_hash=commit_result.commit_hash,
            signed=commit_result.signed,
            debounced=False,
            metadata=commit_result.metadata,
            content_hash=commit_result.content_hash,
            error=None,
        )

    except Exception as e:
        logger.error(f"File lifecycle commit failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"File lifecycle commit failed: {str(e)}"
        )