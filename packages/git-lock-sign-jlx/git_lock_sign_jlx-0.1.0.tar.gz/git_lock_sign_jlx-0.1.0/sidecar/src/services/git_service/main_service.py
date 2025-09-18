"""
Main Git Service - Facade for all git operations.

This module provides the main GitService class that acts as a facade,
coordinating all git operations through specialized services.
"""

import logging
from typing import Any, Dict, Optional

from ..config_service import ConfigService
from ..subprocess_util import SubprocessErrorMode
from .core_service import GitCoreService
from .repository_service import GitRepositoryService
from .commit_service import GitCommitService
from .lock_service import GitLockService
from .status_service import GitStatusService
from .git_config_service import GitConfigService
from .remote_service import GitRemoteService
from .sync_service import GitSyncService
from .push_service import GitPushService
from .models import NotebookPushResult
from .models import GitOperationResult, GitStatusResult, UserInfoResult
from ..provider_services import ProviderService
from ..logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitService:
    """
    Main git service facade that coordinates all git operations.
    
    This class provides a unified interface for all git operations while
    delegating specific functionality to specialized services.
    """

    def __init__(self, config_service: ConfigService):
        """Initialize the git service with all sub-services."""
        self.config_service = config_service
        self.core = GitCoreService(config_service)
        
        # Initialize all specialized services - order matters for dependencies
        self.commit = GitCommitService(self.core, config_service)
        self.remote = GitRemoteService(self.core, config_service)
        self.status = GitStatusService(self.core, config_service)
        self.config = GitConfigService(self.core, config_service)
        self.sync = GitSyncService(self.core, config_service)
        
        # Push service depends on core and remote services
        self.push = GitPushService(self.core, self.remote, config_service)
        
        # Repository service depends on commit, remote, and push services
        self.repository = GitRepositoryService(self.core, config_service, self.commit, self.remote, self.push)
        
        # Lock service needs access to commit and config services
        self.lock = GitLockService(self.core, config_service, self.commit, self.config)

    # Core operations - delegate to core service
    def get_repository(self, file_path: str):
        """Get git repository for a given file path."""
        return self.core.get_repository(file_path)

    def is_git_repository(self, file_path: str) -> bool:
        """Check if file is within a git repository."""
        return self.core.is_git_repository(file_path)

    def run_git_command_with_separate_dirs(self, git_args, error_mode=SubprocessErrorMode.STRICT, timeout=30, operation_name=None, env=None):
        """Run git command with separate git-dir and work-tree."""
        return self.core.run_git_command_with_separate_dirs(git_args, error_mode=error_mode, timeout=timeout, operation_name=operation_name, env=env)

    def translate_jupyterlab_path_to_sidecar(self, file_path: str) -> str:
        """Translate file paths from JupyterLab perspective to sidecar perspective."""
        # Using the public interface through core service for path translation
        return self.core.translate_jupyterlab_path_to_sidecar(file_path)

    # Repository operations - delegate to repository service
    def init_repository(self, notebook_path: str) -> str:
        """Initialize a git repository."""
        return self.repository.init_repository(notebook_path)

    def ensure_gitignore_exists(self, notebook_path: str) -> bool:
        """Ensure .gitignore file exists in the repository."""
        return self.repository.ensure_gitignore_exists(notebook_path)

    def push_gitignore_commit_if_exists(self):
        """Push the .gitignore commit if it exists and remote is configured."""
        return self.repository.push_gitignore_commit_if_exists()

    # Commit operations - delegate to commit service
    def commit_notebook(self, notebook_path: str, commit_message: str) -> GitOperationResult:
        """Commit notebook changes."""
        return self.commit.commit_notebook(notebook_path, commit_message)

    def commit_notebook_with_metadata(self, notebook_path: str, commit_message: str, notebook_service, gpg_service, notebook_content: Optional[Dict[str, Any]] = None) -> GitOperationResult:
        """Commit notebook with metadata operations."""
        return self.commit.commit_notebook_with_metadata(notebook_path, commit_message, notebook_service, gpg_service, notebook_content)

    def commit_gitignore_file(self, repo_path: str) -> GitOperationResult:
        """Commit the .gitignore file with a specific message."""
        return self.commit.commit_gitignore_file(repo_path)

    # Lock operations - delegate to lock service
    def lock_notebook(self, notebook_path: str, notebook_content: Dict[str, Any], commit_message: str, notebook_service, gpg_service) -> GitOperationResult:
        """Lock notebook with commit and signing."""
        return self.lock.lock_notebook(notebook_path, notebook_content, commit_message, notebook_service, gpg_service)

    def unlock_notebook(self, notebook_path: str, notebook_content: Dict[str, Any], notebook_service, gpg_service=None) -> GitOperationResult:
        """Unlock notebook after signature verification."""
        return self.lock.unlock_notebook(notebook_path, notebook_content, notebook_service, gpg_service)

    # Status operations - delegate to status service
    def get_status(self, notebook_path: str) -> GitStatusResult:
        """Get repository and notebook status."""
        return self.status.get_status(notebook_path)

    def has_uncommitted_changes(self, notebook_path: str) -> bool:
        """Check if notebook has uncommitted changes."""
        return self.status.has_uncommitted_changes(notebook_path)

    def has_unpushed_commits_from_other_files(self, notebook_path: str) -> bool:
        """Check if repository has unpushed commits from other files."""
        return self.status.has_unpushed_commits_from_other_files(notebook_path)

    def get_repo_root(self, file_path: str) -> Optional[str]:
        """Get the root directory of the git repository."""
        return self.status.get_repo_root(file_path)

    # Config operations - delegate to config service
    def get_user_info(self, notebook_path: str) -> UserInfoResult:
        """Get git user information."""
        return self.config.get_user_info(notebook_path)

    def get_git_config(self, config_key: str, repo_path: Optional[str] = None) -> Optional[str]:
        """Get a git configuration value."""
        return self.config.get_git_config(config_key, repo_path)

    def set_git_config(self, config_key: str, config_value: str, repo_path: Optional[str] = None) -> GitOperationResult:
        """Set a git configuration value."""
        return self.config.set_git_config(config_key, config_value, repo_path)

    # Remote operations - delegate to remote service
    def add_remote(self, remote_name: str, remote_url: str) -> GitOperationResult:
        """Add a git remote."""
        return self.remote.add_remote(remote_name, remote_url)

    def remove_remote(self, remote_name: str) -> GitOperationResult:
        """Remove a git remote."""
        return self.remote.remove_remote(remote_name)

    def update_remote_url(self, remote_name: str, remote_url: str) -> GitOperationResult:
        """Update the URL of a git remote."""
        return self.remote.update_remote_url(remote_name, remote_url)

    def push_to_remote(self, remote_name: str, branch: str = "HEAD") -> GitOperationResult:
        """Push to a remote repository."""
        return self.push.push_to_remote(remote_name, branch)

    def push_to_remote_with_retry(self, remote_name: str, branch: str = "HEAD", allow_sync: bool = True) -> GitOperationResult:
        """Push to remote with retry logic."""
        return self.push.push_to_remote_with_retry(remote_name, branch, allow_sync)

    def fetch_from_remote(self, remote_name: str, branch: Optional[str] = None) -> GitOperationResult:
        """Fetch from a remote repository."""
        return self.push.fetch_from_remote(remote_name, branch)

    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name."""
        return self.push.get_current_branch()

    def merge_branch(self, branch_name: str, allow_unrelated: bool = True) -> GitOperationResult:
        """Merge a branch into the current branch."""
        return self.push.merge_branch(branch_name, allow_unrelated)

    # Sync operations - delegate to sync service
    async def sync_with_remote_on_session_start(self, repo_path: str,provider_service: ProviderService, remote_name: str = "origin") -> GitOperationResult:
        """Enhanced session sync with validation."""
        return await self.sync.sync_with_remote_on_session_start(repo_path, provider_service, remote_name)

    async def validate_sync_operation(self, repo_path: str, remote_name: str = "origin") -> Dict[str, Any]:
        """Validate sync operation."""
        return await self.sync.validate_sync_operation(repo_path, remote_name)

    # Consolidated notebook push operations - single entry point for all providers
    async def push_notebook_with_provider(
        self,
        notebook_path: str,
        provider_service: ProviderService,
        remote_name: str = "origin"
    ) -> "NotebookPushResult":
        """
        Simplified notebook push operation that works with any provider service.
        
        This method provides a clean interface where the API can call git_service directly
        without needing provider-specific push_notebook methods.
        
        Args:
            notebook_path: Path to the notebook file
            provider_service: The provider service (GitLab, Gitea, GitHub Enterprise) that handles provisioning
            remote_name: Name of the remote to use
            
        Returns:
            NotebookPushResult with push details
        """
        try:
            logger.info("🚀 Starting notebook push with provider: %s", type(provider_service).__name__)
            
            # Use consolidated push service with ProviderService interface
            return await self.push.push_notebook(
                notebook_path, provider_service, remote_name
            )
            
        except Exception as e:
            logger.error("❌ Error in push_notebook_with_provider: %s", str(e))
            return NotebookPushResult(
                success=False,
                error=f"Failed to push notebook: {str(e)}"
            )
