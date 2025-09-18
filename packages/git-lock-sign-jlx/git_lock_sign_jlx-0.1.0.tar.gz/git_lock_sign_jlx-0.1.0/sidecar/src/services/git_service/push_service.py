"""
Push operations service for notebooks.

Handles consolidated push operations for all git service providers with 
service-specific callback support for provisioning and authentication.
"""

import logging
from typing import Any, Dict, Optional, Callable, Awaitable, NamedTuple, TYPE_CHECKING

from ..config_service import ConfigService
from ..subprocess_util import SubprocessErrorMode
from .core_service import GitCoreService
from .remote_service import GitRemoteService
from .models import GitOperationResult, NotebookPushResult
from ..logger_util import default_logger_config

if TYPE_CHECKING:
    from ..provider_services import ProviderService

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitPushService:
    """Handles consolidated push operations for all git service providers."""

    def __init__(self, core_service: GitCoreService, remote_service: GitRemoteService, config_service: Optional[ConfigService] = None):
        """Initialize the push service."""
        self.core = core_service
        self.remote = remote_service
        self.config_service = config_service

    async def push_notebook(
        self,
        notebook_path: str,
        provider_service: "ProviderService",
        remote_name: str = "origin"
    ) -> "NotebookPushResult":
        """
        Consolidated notebook push operation using the ProviderService interface.
        
        This method handles the common git operations for pushing notebooks using
        the standardized ProviderService interface for all git providers.
        
        Args:
            notebook_path: Path to the notebook file
            provider_service: ProviderService instance (Gitea, GitLab, GitHub Enterprise)
            remote_name: Name of the remote to use
            
        Returns:
            NotebookPushResult with push details
        """
        try:
            logger.info("🚀 Starting consolidated notebook push: %s", notebook_path)
            
            # Step 1: Get repository root
            repo_root = self._get_repo_root(notebook_path)
            if not repo_root:
                return NotebookPushResult(
                    success=False,
                    error="Not in a git repository"
                )
            
            logger.info("📁 Repository root: %s", repo_root)
            logger.info("🔧 Using provider: %s", type(provider_service).__name__)
            
            # Step 2: Get or provision push URL
            push_url = await self._get_or_provision_push_url(provider_service, repo_root)
            if not push_url:
                return NotebookPushResult(
                    success=False,
                    error="Failed to get or provision push URL"
                )
            
            # Step 3: Attempt push with authentication retry
            push_result = await self._push_with_provider_retry(
                provider_service, push_url, remote_name, repo_root
            )
            
            # Step 4: Build final result
            if push_result["success"]:
                repository_url = provider_service.get_cached_repository_url(repo_root)
                return NotebookPushResult(
                    success=True,
                    message=push_result.get("message", "Successfully pushed notebook"),
                    repository_url=repository_url
                )
            else:
                return NotebookPushResult(
                    success=False,
                    error=push_result.get("error", "Push failed")
                )
                
        except Exception as e:
            logger.error("❌ Error in consolidated notebook push: %s", str(e))
            return NotebookPushResult(
                success=False,
                error=f"Failed to push notebook: {str(e)}"
            )

    async def _get_or_provision_push_url(
        self,
        provider_service: "ProviderService",
        repo_root: str
    ) -> Optional[str]:
        """
        Get cached push URL or provision new repository using ProviderService.
        
        Args:
            provider_service: Provider service instance
            repo_root: Repository root path
            
        Returns:
            Push URL with embedded credentials, or None if failed
        """
        try:
            # Try to get cached URL first
            cached_url = provider_service.get_cached_push_url(repo_root)
            if cached_url:
                logger.info("✅ Using cached push URL")
                return cached_url
            
            # No cached URL, provision new repository
            logger.info("🔧 Provisioning new repository")
            setup_result = await provider_service.setup_repository(repo_root)
            
            if not setup_result.success:
                logger.error("❌ Failed to provision repository: %s", setup_result.error)
                return None
            
            logger.info("✅ Repository provisioned successfully")
            return setup_result.push_url
            
        except Exception as e:
            logger.error("❌ Error getting or provisioning push URL: %s", str(e))
            return None

    async def _push_with_provider_retry(
        self,
        provider_service: "ProviderService",
        push_url: str,
        remote_name: str,
        repo_root: str,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Push with authentication retry using ProviderService interface.
        
        Args:
            provider_service: Provider service instance
            push_url: URL for pushing with embedded token
            remote_name: Name of the remote
            repo_root: Repository root path
            max_retries: Maximum number of retries
            
        Returns:
            Success/error dictionary
        """
        try:
            # Step 1: Set up secure remote
            remote_setup = self._setup_secure_remote(push_url, remote_name)
            if not remote_setup["success"]:
                return remote_setup
            
            # Step 2: Attempt push with retry on auth failure
            for attempt in range(max_retries + 1):
                logger.info("🔄 Push attempt %d/%d", attempt + 1, max_retries + 1)
                
                # Try to push
                push_result = self.push_to_remote_with_retry(remote_name, "HEAD", allow_sync=True)
                
                if push_result.success:
                    logger.info("✅ Push successful on attempt %d", attempt + 1)
                    return {
                        "success": True,
                        "message": push_result.message
                    }
                
                # Check if this is an auth error
                if provider_service._is_auth_error(str(push_result.error)):
                    if attempt < max_retries:
                        logger.info("🔑 Authentication error detected, attempting retry...")
                        
                        # Get fresh push URL
                        fresh_url = await self._get_fresh_push_url(provider_service, repo_root)
                        if fresh_url:
                            # Update remote with fresh credentials
                            remote_setup = self._setup_secure_remote(fresh_url, remote_name)
                            if not remote_setup["success"]:
                                return remote_setup
                            continue
                        else:
                            logger.error("❌ Failed to get fresh push URL for retry")
                    else:
                        logger.error("❌ Max retries reached for authentication failure")
                
                # Non-auth error or max retries reached
                return {
                    "success": False,
                    "error": push_result.error or push_result.message
                }
            
            return {
                "success": False,
                "error": "Push failed after all retry attempts"
            }
            
        except Exception as e:
            logger.error("❌ Error in push with retry: %s", str(e))
            return {
                "success": False,
                "error": f"Push retry failed: {str(e)}"
            }

    async def _get_fresh_push_url(
        self,
        provider_service: "ProviderService", 
        repo_root: str
    ) -> Optional[str]:
        """
        Get a fresh push URL for authentication retry.
        
        Args:
            provider_service: Provider service instance
            repo_root: Repository root path
            
        Returns:
            Fresh push URL or None if failed
        """
        try:
            # Some providers may have session sync methods for fresh URLs
            if hasattr(provider_service, 'get_fresh_push_url_for_sync'):
                method = getattr(provider_service, 'get_fresh_push_url_for_sync')
                fresh_url = await method(repo_root)
                if fresh_url:
                    return fresh_url
            
            # Fallback: try to provision again
            setup_result = await provider_service.setup_repository(repo_root)
            return setup_result.push_url if setup_result.success else None
            
        except Exception as e:
            logger.error("❌ Error getting fresh push URL: %s", str(e))
            return None

    async def _push_with_auth_retry(
        self,
        push_url: str,
        remote_name: str,
        is_auth_error_detector: Callable[[str], bool],
        push_url_provider: Callable[[], Awaitable[Optional[str]]]
    ) -> Dict[str, Any]:
        """
        Attempt push with retry on authentication failure.
        
        Args:
            push_url: URL with embedded token for pushing
            remote_name: Name of the remote to use
            is_auth_error_detector: Callback to detect authentication errors
            push_url_provider: Callback to get fresh push URL on auth failure
            
        Returns:
            Dictionary with push result details
        """
        try:
            # Step 1: Set up secure remote with embedded credentials
            remote_setup_result = self._setup_secure_remote(push_url, remote_name)
            if not remote_setup_result["success"]:
                return remote_setup_result
            
            # Step 2: Initial push attempt
            push_result = self.push_to_remote_with_retry(remote_name, "HEAD", allow_sync=True)
            
            if push_result.success:
                logger.info("✅ Push successful on first attempt")
                return {
                    "success": True,
                    "message": push_result.message
                }
            
            # Step 3: Check if it's an authentication error
            error_msg = push_result.error or ""
            if is_auth_error_detector(error_msg):
                logger.warning("🔑 Authentication error detected - attempting token refresh and retry")
                return await self._retry_push_after_auth_failure(
                    remote_name, push_url_provider
                )
            
            # Step 4: Non-auth error, return as-is
            logger.error("❌ Push failed with non-auth error: %s", error_msg)
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            logger.error("❌ Error in push with auth retry: %s", str(e))
            return {
                "success": False,
                "error": f"Push operation failed: {str(e)}"
            }

    async def _retry_push_after_auth_failure(
        self,
        remote_name: str,
        push_url_provider: Callable[[], Awaitable[Optional[str]]]
    ) -> Dict[str, Any]:
        """
        Retry push after authentication failure by getting fresh push URL.
        
        Args:
            remote_name: Name of the remote to use
            push_url_provider: Callback to get fresh push URL
            
        Returns:
            Dictionary with retry push result
        """
        try:
            # Get fresh push URL (may involve token refresh/re-provisioning)
            fresh_push_url = await push_url_provider()
            if not fresh_push_url:
                return {
                    "success": False,
                    "error": "Failed to get fresh push URL after authentication failure"
                }
            
            # Set up remote with fresh credentials
            remote_setup_result = self._setup_secure_remote(fresh_push_url, remote_name)
            if not remote_setup_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to setup remote with fresh credentials: {remote_setup_result.get('error')}"
                }
            
            # Retry push
            logger.info("🔄 Retrying push with fresh credentials")
            push_result = self.push_to_remote_with_retry(remote_name, "HEAD", allow_sync=True)
            
            if push_result.success:
                logger.info("✅ Push successful after authentication retry")
                return {
                    "success": True,
                    "message": push_result.message
                }
            else:
                logger.error("❌ Push failed even after authentication retry: %s", push_result.error)
                return {
                    "success": False,
                    "error": push_result.error or "Push failed after retry"
                }
                
        except Exception as e:
            logger.error("❌ Error during push retry: %s", str(e))
            return {
                "success": False,
                "error": f"Push retry failed: {str(e)}"
            }

    # Remote add/remove operations delegated to remote_service

    def push_to_remote(self, remote_name: str, branch: str = "HEAD") -> GitOperationResult:
        """
        Push to a remote repository.

        Args:
            remote_name: Name of the remote
            branch: Branch to push (default: HEAD)

        Returns:
            GitOperationResult with operation details
        """
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["push", remote_name, branch],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=120,
                operation_name=f"push to remote {remote_name}"
            )

            if result.success:
                logger.info("Successfully pushed to remote %s", remote_name)
                return GitOperationResult(
                    success=True,
                    message=f"Successfully pushed to remote {remote_name}"
                )
            else:
                # Check if it's a push rejection error
                if self._is_push_rejected_error(result.stderr):
                    logger.warning("Push rejected by remote %s", remote_name)
                    return GitOperationResult(
                        success=False,
                        message=f"Push rejected by remote {remote_name}",
                        error=result.stderr
                    )
                else:
                    return GitOperationResult(
                        success=False,
                        message=f"Failed to push to remote {remote_name}",
                        error=result.stderr
                    )

        except Exception as e:
            logger.error("Error pushing to remote %s: %s", remote_name, str(e))
            return GitOperationResult(
                success=False,
                message=f"Error pushing to remote {remote_name}",
                error=str(e)
            )

    def push_to_remote_with_retry(self, remote_name: str, branch: str = "HEAD", allow_sync: bool = True) -> GitOperationResult:
        """
        Push to remote with automatic retry logic for non-fast-forward errors.
        
        This method attempts a push and if it fails due to remote changes,
        it will fetch, merge, and retry the push.
        
        Args:
            remote_name: Name of the remote to push to
            branch: Branch to push (defaults to HEAD)
            allow_sync: Whether to attempt sync and retry on push rejection
            
        Returns:
            GitOperationResult with push details
        """
        try:
            logger.info("🚀 Starting push with retry to remote '%s'", remote_name)
            
            # Attempt initial push
            push_result = self.push_to_remote(remote_name, branch)
            
            if push_result.success:
                return push_result
            
            # Check if failure is due to push rejection (non-fast-forward)
            if allow_sync and self._is_push_rejected_error(push_result.error or ""):
                logger.warning("Push rejected due to remote changes, attempting sync and retry")
                
                # Sync with remote and retry
                sync_result = self._sync_and_retry_push(remote_name, branch)
                return sync_result
            else:
                # Return original error for non-rejection errors
                return push_result
                
        except Exception as e:
            logger.error("Error in push with retry: %s", str(e))
            return GitOperationResult(
                success=False,
                message=f"Failed to push to remote '{remote_name}' with retry",
                error=str(e)
            )

    def fetch_from_remote(self, remote_name: str, branch: Optional[str] = None) -> GitOperationResult:
        """
        Fetch from a remote repository.

        Args:
            remote_name: Name of the remote
            branch: Optional branch to fetch

        Returns:
            GitOperationResult with operation details
        """
        try:
            git_args = ["fetch", remote_name]
            if branch:
                git_args.append(branch)

            result = self.core.run_git_command_with_separate_dirs(
                git_args,
                error_mode=SubprocessErrorMode.STRICT,
                timeout=60,
                operation_name=f"fetch from remote {remote_name}"
            )

            if result.success:
                logger.info("Successfully fetched from remote %s", remote_name)
                return GitOperationResult(
                    success=True,
                    message=f"Successfully fetched from remote {remote_name}"
                )
            else:
                return GitOperationResult(
                    success=False,
                    message=f"Failed to fetch from remote {remote_name}",
                    error=result.stderr
                )

        except Exception as e:
            logger.error("Error fetching from remote %s: %s", remote_name, str(e))
            return GitOperationResult(
                success=False,
                message=f"Error fetching from remote {remote_name}",
                error=str(e)
            )

    def get_current_branch(self) -> Optional[str]:
        """
        Get the current branch name.

        Returns:
            Current branch name, or None if not available
        """
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["branch", "--show-current"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="get current branch"
            )

            if result.success:
                return result.stdout.strip()
            else:
                return None

        except Exception as e:
            logger.error("Error getting current branch: %s", str(e))
            return None

    def merge_branch(self, branch_name: str, allow_unrelated: bool = True) -> GitOperationResult:
        """
        Merge a branch into the current branch.

        Args:
            branch_name: Name of the branch to merge
            allow_unrelated: Whether to allow unrelated histories

        Returns:
            GitOperationResult with operation details
        """
        try:
            git_args = ["merge", branch_name]
            if allow_unrelated:
                git_args.append("--allow-unrelated-histories")

            result = self.core.run_git_command_with_separate_dirs(
                git_args,
                error_mode=SubprocessErrorMode.STRICT,
                timeout=60,
                operation_name=f"merge branch {branch_name}"
            )

            if result.success:
                logger.info("Successfully merged branch %s", branch_name)
                return GitOperationResult(
                    success=True,
                    message=f"Successfully merged branch {branch_name}"
                )
            else:
                return GitOperationResult(
                    success=False,
                    message=f"Failed to merge branch {branch_name}",
                    error=result.stderr
                )

        except Exception as e:
            logger.error("Error merging branch %s: %s", branch_name, str(e))
            return GitOperationResult(
                success=False,
                message=f"Error merging branch {branch_name}",
                error=str(e)
            )

    def _setup_secure_remote(self, push_url: str, remote_name: str) -> Dict[str, Any]:
        """
        Set up git remote with embedded credentials.
        
        Args:
            push_url: URL with embedded token
            remote_name: Name of the remote to setup
            
        Returns:
            Success/error dictionary
        """
        try:
            logger.info("🔧 Setting up secure remote '%s' with embedded credentials", remote_name)
            
            # Remove existing remote if it exists
            self.remote.remove_remote(remote_name)
            
            # Add remote with embedded credentials
            result = self.remote.add_remote(remote_name, push_url)
            
            if result.success:
                logger.info("✅ Successfully configured git remote '%s'", remote_name)
                return {"success": True}
            else:
                logger.error("❌ Failed to configure git remote '%s': %s", remote_name, result.error)
                return {
                    "success": False,
                    "error": f"Failed to setup remote: {result.error}"
                }
                
        except Exception as e:
            error_msg = f"Failed to setup secure remote: {str(e)}"
            logger.error("❌ %s", error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def _get_repo_root(self, file_path: str) -> Optional[str]:
        """Get git repository root for a file path."""
        # Note: Currently using git rev-parse directly, file_path parameter maintained for future use
        _ = file_path  # Acknowledge unused parameter
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "--show-toplevel"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="get git repository root"
            )
            
            if result.success and result.stdout:
                return result.stdout.strip()
            else:
                return None
                
        except Exception as e:
            logger.error("Error getting repository root: %s", str(e))
            return None

    def _is_push_rejected_error(self, error_output: str) -> bool:
        """
        Check if the push error indicates rejection due to remote changes.
        
        Args:
            error_output: Error output from git push command
            
        Returns:
            True if error indicates push rejection due to remote changes
        """
        rejection_indicators = [
            "rejected",
            "non-fast-forward", 
            "fetch first",
            "updates were rejected",
            "remote contains work that you do not have locally",
        ]
        
        error_lower = error_output.lower()
        return any(
            indicator.lower() in error_lower 
            for indicator in rejection_indicators
        )

    def _sync_and_retry_push(self, remote_name: str, branch: str = "HEAD") -> GitOperationResult:
        """
        Sync with remote repository and retry push.
        
        This method fetches remote changes, merges them with local changes,
        then retries the push operation.
        
        Args:
            remote_name: Name of the git remote
            branch: Branch to push
            
        Returns:
            GitOperationResult with sync and push details
        """
        try:
            logger.info("🔄 Syncing with remote and retrying push...")
            
            # Fetch remote changes
            fetch_result = self.fetch_from_remote(remote_name)
            if not fetch_result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to fetch remote changes during sync",
                    error=fetch_result.error
                )
            
            # Get current branch if HEAD is used
            current_branch = branch
            if branch == "HEAD":
                current_branch = self.get_current_branch()
                if not current_branch:
                    return GitOperationResult(
                        success=False,
                        message="Failed to determine current branch",
                        error="Could not get current branch name"
                    )
            
            # Check if remote branch exists and merge if needed
            remote_branch = f"{remote_name}/{current_branch}"
            merge_result = self._attempt_merge_if_needed(remote_branch)
            
            if not merge_result.success:
                return merge_result
            
            # Retry the push after syncing
            logger.info("🔄 Retrying push after sync...")
            retry_result = self.push_to_remote(remote_name, branch)
            
            if retry_result.success:
                logger.info("✅ Push successful after sync")
                return GitOperationResult(
                    success=True,
                    message="Changes pushed successfully after syncing with remote repository"
                )
            else:
                return GitOperationResult(
                    success=False,
                    message="Push failed even after sync",
                    error=f"Push failed after sync: {retry_result.error}"
                )
                
        except Exception as e:
            logger.error("Error syncing and retrying push: %s", str(e))
            return GitOperationResult(
                success=False,
                message="Failed to sync with remote and retry push",
                error=str(e)
            )

    def _attempt_merge_if_needed(self, remote_branch: str) -> GitOperationResult:
        """
        Attempt to merge remote branch if it exists.
        
        Args:
            remote_branch: Remote branch name (e.g., "origin/main")
            
        Returns:
            GitOperationResult indicating merge success/failure
        """
        try:
            # Check if remote branch exists
            check_result = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "--verify", remote_branch],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name="verify remote branch exists"
            )
            
            if not check_result.success:
                # Remote branch doesn't exist, no merge needed
                logger.info("Remote branch '%s' doesn't exist, no merge needed", remote_branch)
                return GitOperationResult(
                    success=True,
                    message="No remote branch to merge"
                )
            
            # Remote branch exists, attempt merge
            logger.info("🔄 Merging remote branch '%s'...", remote_branch)
            merge_result = self.merge_branch(remote_branch, allow_unrelated=True)
            
            if merge_result.success:
                logger.info("✅ Successfully merged remote changes")
                return merge_result
            else:
                # Check if merge failure is due to conflicts
                if "conflict" in (merge_result.error or "").lower():
                    return GitOperationResult(
                        success=False,
                        message="Merge conflicts detected during sync",
                        error="Merge conflicts require manual resolution"
                    )
                else:
                    return GitOperationResult(
                        success=False, 
                        message="Failed to merge remote changes",
                        error=merge_result.error
                    )
                    
        except Exception as e:
            logger.error("Error attempting merge: %s", str(e))
            return GitOperationResult(
                success=False,
                message="Error during merge attempt",
                error=str(e)
            )
