"""
Abstract base class for git provider services.

This module defines the common interface that all git provider services 
(Gitea, GitLab, GitHub Enterprise) must implement.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, NamedTuple, Optional, TYPE_CHECKING

from ..config_service import ConfigService
from ..logger_util import default_logger_config
from ..git_service.models import NotebookPushResult

if TYPE_CHECKING:
    from ..git_service import GitService

logger = logging.getLogger(__name__)
default_logger_config(logger)


class ProviderSetupResult(NamedTuple):
    """Generic result for provider repository setup operations."""
    
    success: bool
    repository_url: Optional[str] = None
    push_url: Optional[str] = None
    error: Optional[str] = None


class ProviderService(ABC):
    """
    Abstract base class for all git provider services.
    
    This class defines the common interface and shared functionality that all
    provider services (Gitea, GitLab, GitHub Enterprise) must implement.
    """

    def __init__(self, config_service: ConfigService, git_service: "GitService"):
        """
        Initialize the provider service.
        
        Args:
            config_service: Configuration service instance
            git_service: Git service instance
        """
        self.config_service = config_service
        self.git_service = git_service
        self._push_url_cache = {}  # Cache push URLs by repo path

    # Abstract methods that must be implemented by each provider
    
    @abstractmethod
    async def setup_repository(self, repo_path: str) -> ProviderSetupResult:
        """
        Set up a repository for the given path.
        
        This should handle user/repo provisioning and return setup results.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            ProviderSetupResult with setup details
        """
        raise NotImplementedError("Subclasses must implement setup_repository")

    @abstractmethod
    def provision_repository(self, user_name: str, user_email: str) -> Dict[str, Any]:
        """
        Provision user and repository via provider API.
        
        Args:
            user_name: Git user name
            user_email: Git user email
            
        Returns:
            Dictionary with provision results
        """
        raise NotImplementedError("Subclasses must implement provision_repository")

    @abstractmethod
    def _is_auth_error(self, error_msg: str) -> bool:
        """
        Detect if an error message indicates an authentication failure.
        
        Each provider has different error message patterns.
        
        Args:
            error_msg: Error message to check
            
        Returns:
            True if the error indicates authentication failure
        """
        raise NotImplementedError("Subclasses must implement _is_auth_error")

    @abstractmethod
    def check_user_registration(self, user_email: str) -> bool:
        """
        Check if a user is registered/has access to the provider.
        
        Args:
            user_email: User email to check
            
        Returns:
            True if user is registered and has access
        """
        raise NotImplementedError("Subclasses must implement check_user_registration")

    @abstractmethod
    async def get_fresh_push_url_for_sync(self, repo_path: str) -> Optional[str]:
        """
        Get fresh push URL with current authentication for sync operations.
        
        This method refreshes authentication tokens if needed and returns
        a push URL suitable for git operations.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Fresh push URL with embedded credentials, or None if failed
        """
        raise NotImplementedError("Subclasses must implement get_fresh_push_url_for_sync")

    @abstractmethod
    async def push_notebook(self, notebook_path: str) -> NotebookPushResult:
        """
        Push a notebook to the provider.
        
        Args:
            notebook_path: Path to the notebook file
            
        Returns:
            NotebookPushResult with push details
        """
        raise NotImplementedError("Subclasses must implement push_notebook")    

    # Concrete methods with shared implementation

    def get_cached_push_url(self, repo_path: str) -> Optional[str]:
        """
        Get cached push URL for repository.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            Cached push URL if available, None otherwise
        """
        return self._push_url_cache.get(repo_path)

    def get_cached_repository_url(self, repo_path: str) -> Optional[str]:
        """
        Get cached repository URL for repository.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            Cached repository URL if available, None otherwise
        """
        return self._push_url_cache.get(f"{repo_path}_repo_url")

    def _get_repo_root(self, file_path: str) -> Optional[str]:
        """
        Get git repository root for a file path.
        
        Args:
            file_path: Path to check
            
        Returns:
            Repository root path if found, None otherwise
        """
        return self.git_service.get_repo_root(file_path)

    def _cache_urls(self, repo_path: str, push_url: str, repository_url: Optional[str] = None):
        """
        Cache URLs for future use.
        
        Args:
            repo_path: Repository path (cache key)
            push_url: Push URL with embedded credentials
            repository_url: Clean repository URL (optional)
        """
        self._push_url_cache[repo_path] = push_url
        if repository_url:
            self._push_url_cache[f"{repo_path}_repo_url"] = repository_url

    # Optional methods that providers can override if needed

    def get_session_sync_push_url(self, repo_path: str) -> Optional[str]:
        """
        Get push URL for session sync operations.
        
        Default implementation returns cached URL. Providers can override
        if they need special logic for session sync.
        
        Args:
            repo_path: Repository path
            
        Returns:
            Push URL for session sync, or None if not available
        """
        cached_url = self._push_url_cache.get(repo_path)
        if cached_url:
            logger.info("✅ Using cached push URL for session sync")
            return cached_url
        else:
            logger.warning("⚠️ No cached push URL found for session sync")
            return None

    def get_git_user_info(self, repo_path: str) -> Dict[str, Optional[str]]:
        """
        Get git user information.
        
        Default implementation checks environment variables first,
        then falls back to git config. Providers can override if needed.
        
        Args:
            repo_path: Repository path
            
        Returns:
            Dictionary with 'name' and 'email' keys
        """
        # Try environment variables first (for containerized environments)
        env_name = self.config_service.git_user_name
        env_email = self.config_service.git_user_email
        
        if env_name != "NOT_SET" and env_email != "NOT_SET":
            logger.info("Using git user info from environment")
            return {"name": env_name, "email": env_email}
        
        # Fallback to git config using GitService
        name = self.git_service.get_git_config("user.name", repo_path)
        email = self.git_service.get_git_config("user.email", repo_path)
        
        logger.info("Git user info - Name: %s, Email: %s", name, email)
        return {"name": name, "email": email}
    
    