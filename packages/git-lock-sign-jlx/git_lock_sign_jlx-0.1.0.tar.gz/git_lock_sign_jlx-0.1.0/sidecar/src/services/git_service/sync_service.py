"""
Repository synchronization service.

Handles repository synchronization, validation, and backup operations.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from ..config_service import ConfigService
from ..logger_util import default_logger_config
if TYPE_CHECKING:
    from ..provider_services import ProviderService
from ..subprocess_util import SubprocessErrorMode
from .core_service import GitCoreService
from .models import GitOperationResult

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitSyncService:
    """Handles repository synchronization operations."""

    def __init__(
        self,
        core_service: GitCoreService,
        config_service: Optional[ConfigService] = None,
    ):
        """Initialize the sync service."""
        self.core = core_service
        self.config_service = config_service

    async def sync_with_remote_on_session_start(
        self,
        repo_path: str,
        provider_service: "ProviderService",
        remote_name: str = "origin",
    ) -> GitOperationResult:
        """
        Enhanced session sync with validation and enforced consistency.

        This method ensures that the local repository is identical to the remote when the user
        begins working, with enhanced validation and automatic backup creation.

        Args:
            repo_path: Path to the repository
            provider_service: provider service to refresh remote URL with fresh tokens
            remote_name: Name of the remote

        Returns:
            GitOperationResult with sync details
        """
        try:
            logger.info(
                "🔄 Starting enhanced session sync for repository: %s",
                repo_path,
            )

            # Step 1: Validate sync operation
            logger.info("🔍 Phase 1: Validating sync operation...")
            validation = await self.validate_sync_operation(
                repo_path, remote_name
            )

            if not validation["valid"]:
                logger.error(
                    "❌ Sync validation failed: %s",
                    validation.get("critical_issues", []),
                )
                return GitOperationResult(
                    success=False,
                    message="Sync validation failed",
                    error=f"Critical issues found: {', '.join(validation.get('critical_issues', []))}",
                )

            # Log validation results
            if validation.get("warnings"):
                logger.warning(
                    "⚠️ Validation warnings: %s", len(validation["warnings"])
                )
                for warning in validation["warnings"]:
                    logger.warning("   - %s", warning)

            if validation.get("critical_issues"):
                logger.error(
                    "❌ Validation critical issues: %s",
                    len(validation["critical_issues"]),
                )
                for issue in validation["critical_issues"]:
                    logger.error("   - %s", issue)

            # Step 2: Enforce user config consistency
            logger.info(
                "🔍 Phase 2: Enforcing user configuration consistency..."
            )
            config_updated = self._enforce_environment_user_config(repo_path)
            if config_updated:
                logger.info(
                    "🔧 Updated local git config to match environment variables"
                )
            else:
                logger.info(
                    "✅ Local git config already matches environment variables"
                )

            # Step 3: Create backup if local changes exist
            backup_created = False
            if validation.get("uncommitted_changes") or validation.get(
                "untracked_files"
            ):
                logger.info("📦 Creating backup before destructive sync...")
                backup_created = await self._create_sync_backup(repo_path)
                if backup_created:
                    logger.info("✅ Backup created successfully")
                else:
                    logger.warning(
                        "⚠️ Failed to create backup, proceeding with sync anyway"
                    )

            # Step 4: Perform the actual sync
            logger.info("🔄 Phase 3: Performing force sync...")

            if not self.core.is_git_repository(repo_path):
                return GitOperationResult(
                    success=False,
                    message="Not a git repository",
                    error="Cannot sync - not a git repository",
                )

            repo = self.core.get_repository(repo_path)
            if not repo:
                return GitOperationResult(
                    success=False,
                    message="Could not access repository",
                    error="Failed to access git repository",
                )

            # Check if remote exists
            remote_check = self.core.run_git_command_with_separate_dirs(
                ["remote", "get-url", remote_name],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name="check remote URL",
            )

            if not remote_check.success:
                logger.info(
                    "No remote '%s' found - skipping session sync", remote_name
                )
                return GitOperationResult(
                    success=True,
                    message="No remote found - skipping sync",
                    error=None,
                )

            remote_url = remote_check.stdout.strip()
            logger.info("🔗 Found remote '%s': %s", remote_name, remote_url)

            # Refresh remote URL if provider service provided (for token-based authentication)
            if provider_service:
                try:
                    logger.info(
                        "🔄 Refreshing remote URL with fresh authentication..."
                    )
                    fresh_remote_url = (
                        await provider_service.get_fresh_push_url_for_sync(
                            repo_path
                        )
                    )
                    if fresh_remote_url:
                        # Update the remote URL
                        update_result = self.core.run_git_command_with_separate_dirs(
                            [
                                "remote",
                                "set-url",
                                remote_name,
                                fresh_remote_url,
                            ],
                            error_mode=SubprocessErrorMode.LENIENT,
                            timeout=30,
                            operation_name="update remote URL with fresh authentication",
                        )

                        if update_result.success:
                            logger.info(
                                "✅ Successfully updated remote URL with fresh authentication"
                            )
                        else:
                            logger.warning(
                                "⚠️ Failed to update remote URL: %s",
                                update_result.stderr,
                            )
                            # Continue with old URL
                    else:
                        logger.warning(
                            "⚠️ Failed to get fresh remote URL from provider service"
                        )
                        # Continue with old URL
                except Exception as e:
                    logger.warning("⚠️ Error refreshing remote URL: %s", str(e))
                    # Continue with old URL

            # Fetch remote changes
            logger.info("📥 Fetching remote changes...")
            fetch_result = self.core.run_git_command_with_separate_dirs(
                ["fetch", remote_name],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=60,
                operation_name="fetch remote changes",
            )

            if not fetch_result.success:
                logger.warning(
                    "Failed to fetch from remote: %s", fetch_result.stderr
                )
                return GitOperationResult(
                    success=False,
                    message="Failed to fetch remote changes",
                    error=f"Git fetch failed: {fetch_result.stderr}",
                )

            logger.info("✅ Successfully fetched remote changes")

            # Get current branch (handle case where repository has no commits yet)
            branch_result = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name="get current branch",
            )

            # Handle empty repository case (no HEAD exists yet)
            if not branch_result.success:
                logger.info(
                    "🌱 Local repository has no commits yet - performing initial checkout from remote"
                )
                return self._perform_initial_checkout(remote_name)

            current_branch = branch_result.stdout.strip()
            remote_branch = f"{remote_name}/{current_branch}"

            logger.info("🌿 Current branch: %s", current_branch)
            logger.info("🌿 Remote branch: %s", remote_branch)

            # Force sync with remote (reset to match remote exactly)
            logger.info(
                "🔄 Syncing local branch to match remote '%s'", remote_branch
            )
            reset_result = self.core.run_git_command_with_separate_dirs(
                ["reset", "--hard", remote_branch],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=60,
                operation_name="force sync with remote",
            )

            if not reset_result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to sync with remote",
                    error=f"Git reset failed: {reset_result.stderr}",
                )

            # Clean any untracked files if they exist
            clean_result = self.core.run_git_command_with_separate_dirs(
                ["clean", "-fd"],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=30,
                operation_name="clean untracked files",
            )

            if clean_result.success and clean_result.stdout.strip():
                logger.info(
                    "🧹 Cleaned untracked files: %s",
                    clean_result.stdout.strip(),
                )

            # Step 5: Verify sync success
            logger.info("🔍 Phase 4: Verifying sync success...")
            sync_verified = self._verify_sync_success(repo_path, remote_name)

            if sync_verified:
                logger.info("✅ Enhanced session sync completed successfully")

                # Build success message
                message_parts = [
                    f"Successfully synced with remote {remote_branch}"
                ]
                if backup_created:
                    message_parts.append("Backup created before sync")
                if config_updated:
                    message_parts.append(
                        "User config updated to match environment"
                    )

                return GitOperationResult(
                    success=True, message=". ".join(message_parts), error=None
                )
            else:
                logger.warning("⚠️ Sync completed but verification failed")
                return GitOperationResult(
                    success=True,
                    message="Sync completed with verification warnings",
                    error=None,
                )

        except Exception as e:
            logger.error(
                "Enhanced session sync failed with exception: %s", str(e)
            )
            return GitOperationResult(
                success=False,
                message="Enhanced session sync failed",
                error=f"Unexpected error during sync: {str(e)}",
            )

    async def validate_sync_operation(
        self, repo_path: str, remote_name: str = "origin"
    ) -> Dict[str, Any]:
        """
        Validate sync operation to identify potential issues before proceeding.

        This method enforces that environment variables are the single source of truth
        and identifies any local changes that will be lost during force sync.

        Args:
            repo_path: Path to the git repository
            remote_name: Name of the git remote (default: "origin")

        Returns:
            Dictionary with validation results and recommendations
        """
        try:
            logger.info(
                "🔍 Validating sync operation for repository: %s", repo_path
            )

            if not self.core.is_git_repository(repo_path):
                return {
                    "valid": False,
                    "error": "Not a git repository",
                    "recommendations": ["Initialize git repository first"],
                }

            repo = self.core.get_repository(repo_path)
            if not repo:
                return {
                    "valid": False,
                    "error": "Could not access repository",
                    "recommendations": ["Check repository permissions"],
                }

            validation_results = {
                "valid": True,
                "warnings": [],
                "critical_issues": [],
                "recommendations": [],
                "user_config_mismatch": False,
                "uncommitted_changes": False,
                "untracked_files": False,
                "sync_required": False,
            }

            # 1. Check user configuration mismatch (CRITICAL - must match environment)
            logger.info("🔍 Checking user configuration consistency...")
            local_name = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local user name for validation",
            )

            local_email = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local user email for validation",
            )

            # Get expected configuration from environment/config service
            expected_name = None
            expected_email = None

            if (
                self.config_service
                and self.config_service.git_user_email != "NOT_SET"
            ):
                expected_name = self.config_service.git_user_name
                expected_email = self.config_service.git_user_email

            if expected_name and expected_email:
                local_name_str = (
                    local_name.stdout.strip() if local_name.success else None
                )
                local_email_str = (
                    local_email.stdout.strip() if local_email.success else None
                )

                if (local_name_str and local_name_str != expected_name) or (
                    local_email_str and local_email_str != expected_email
                ):
                    validation_results["user_config_mismatch"] = True
                    validation_results["critical_issues"].append(
                        f"Local git config ({local_name_str} <{local_email_str}>) differs from expected ({expected_name} <{expected_email}>)"
                    )
                    validation_results["recommendations"].append(
                        "Local git config will be automatically updated to match environment variables"
                    )
            else:
                validation_results["critical_issues"].append(
                    "Environment variables GIT_USER_NAME and GIT_USER_EMAIL not set"
                )
                validation_results["recommendations"].append(
                    "Set GIT_USER_NAME and GIT_USER_EMAIL environment variables"
                )

            # 2. Check for uncommitted changes (WARNING - will be lost)
            logger.info("🔍 Checking for uncommitted changes...")
            status_result = self.core.run_git_command_with_separate_dirs(
                ["status", "--porcelain"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check uncommitted changes for validation",
            )

            # Check if repository is empty (no commits yet)
            has_commits = True
            try:
                head_check = self.core.run_git_command_with_separate_dirs(
                    ["rev-parse", "HEAD"],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="check if repository has commits",
                )
                has_commits = head_check.success
            except Exception:
                has_commits = False

            if status_result.success and status_result.stdout.strip():
                validation_results["uncommitted_changes"] = True
                # For empty repositories, allow uncommitted changes (e.g., .gitignore)
                if not has_commits:
                    validation_results["warnings"].append(
                        "Empty repository with uncommitted changes - will be cleaned during initial checkout"
                    )
                else:
                    validation_results["warnings"].append(
                        f"Found uncommitted changes that will be lost during force sync: {status_result.stdout.strip()}"
                    )
                validation_results["recommendations"].append(
                    "Changes will be automatically backed up before sync"
                )

            # 3. Check for untracked files (WARNING - will be deleted)
            logger.info("🔍 Checking for untracked files...")
            untracked_result = self.core.run_git_command_with_separate_dirs(
                ["ls-files", "--others", "--exclude-standard"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check untracked files for validation",
            )

            if untracked_result.success and untracked_result.stdout.strip():
                untracked_files = untracked_result.stdout.strip().split("\n")
                validation_results["untracked_files"] = True
                validation_results["warnings"].append(
                    f"Found {len(untracked_files)} untracked files that will be deleted during sync"
                )
                validation_results["recommendations"].append(
                    "Untracked files will be automatically backed up before sync"
                )

                # Show first few untracked files for user awareness
                if len(untracked_files) <= 5:
                    validation_results["warnings"].append(
                        f"Untracked files: {', '.join(untracked_files)}"
                    )
                else:
                    validation_results["warnings"].append(
                        f"Untracked files: {', '.join(untracked_files[:3])}... and {len(untracked_files) - 3} more"
                    )

            # 4. Check remote connectivity and determine if sync is needed
            logger.info(
                "🔍 Checking remote connectivity and sync requirements..."
            )
            remote_check = self.core.run_git_command_with_separate_dirs(
                ["remote", "get-url", remote_name],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check remote connectivity",
            )

            if remote_check.success:
                # Fetch latest remote info
                fetch_result = self.core.run_git_command_with_separate_dirs(
                    ["fetch", remote_name],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=30,
                    operation_name="fetch for validation",
                )

                if fetch_result.success:
                    # Check if sync is actually needed
                    local_commit = self.core.run_git_command_with_separate_dirs(
                        ["rev-parse", "HEAD"],
                        error_mode=SubprocessErrorMode.SILENT,
                        timeout=10,
                        operation_name="get local commit for validation",
                    )

                    # Try to find remote branch (main or master)
                    remote_branch = None
                    for branch_name in ["main", "master"]:
                        test_branch = f"{remote_name}/{branch_name}"
                        test_result = (
                            self.core.run_git_command_with_separate_dirs(
                                ["rev-parse", test_branch],
                                error_mode=SubprocessErrorMode.SILENT,
                                timeout=10,
                                operation_name="test remote branch existence",
                            )
                        )
                        if test_result.success:
                            remote_branch = test_branch
                            break

                    if remote_branch and local_commit.success:
                        remote_commit = self.core.run_git_command_with_separate_dirs(
                            ["rev-parse", remote_branch],
                            error_mode=SubprocessErrorMode.SILENT,
                            timeout=10,
                            operation_name="get remote commit for validation",
                        )

                        if remote_commit.success:
                            local_hash = local_commit.stdout.strip()
                            remote_hash = remote_commit.stdout.strip()

                            if local_hash != remote_hash:
                                validation_results["sync_required"] = True
                                logger.info(
                                    "🔄 Sync required: local %s != remote %s",
                                    local_hash[:8],
                                    remote_hash[:8],
                                )
                            else:
                                logger.info(
                                    "✅ Local and remote are already in sync"
                                )
                        else:
                            validation_results["warnings"].append(
                                f"Could not access remote branch {remote_branch}"
                            )
                    else:
                        validation_results["warnings"].append(
                            "Could not determine local HEAD or remote branch"
                        )
                else:
                    validation_results["warnings"].append(
                        f"Could not fetch from remote: {fetch_result.stderr}"
                    )
            else:
                validation_results["warnings"].append(
                    f"Remote '{remote_name}' not found"
                )

            # Determine overall validity
            if validation_results["critical_issues"]:
                validation_results["valid"] = False
                validation_results["recommendations"].insert(
                    0, "Review critical issues before proceeding with sync"
                )

            logger.info(
                "🔍 Sync validation completed: %s",
                "✅ Valid" if validation_results["valid"] else "❌ Invalid",
            )
            if validation_results["warnings"]:
                logger.warning(
                    "⚠️ Validation warnings: %s",
                    len(validation_results["warnings"]),
                )
            if validation_results["critical_issues"]:
                logger.error(
                    "❌ Validation critical issues: %s",
                    len(validation_results["critical_issues"]),
                )

            return validation_results

        except Exception as e:
            logger.error("❌ Sync validation failed: %s", str(e))
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}",
                "recommendations": ["Check repository state and try again"],
            }

    def _enforce_environment_user_config(self, _repo_path: str) -> bool:
        """
        Enforces that local git config matches environment variables.
        Returns True if config was updated, False if already correct.

        Args:
            _repo_path: Path to the git repository

        Returns:
            True if config was updated, False if already correct
        """
        try:
            if (
                not self.config_service
                or self.config_service.git_user_email == "NOT_SET"
            ):
                logger.warning(
                    "Cannot enforce user config: environment variables not set"
                )
                return False

            expected_name = self.config_service.git_user_name
            expected_email = self.config_service.git_user_email

            # Check current local config
            current_name_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get current local git name",
            )

            current_email_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get current local git email",
            )

            current_name = (
                current_name_result.stdout.strip()
                if current_name_result.success
                else None
            )
            current_email = (
                current_email_result.stdout.strip()
                if current_email_result.success
                else None
            )

            # If mismatch, force update to environment values
            config_updated = False

            if current_name != expected_name:
                self.core.run_git_command_with_separate_dirs(
                    ["config", "--local", "user.name", expected_name],
                    error_mode=SubprocessErrorMode.STRICT,
                    timeout=10,
                    operation_name="update local git user name",
                )
                logger.info(
                    "🔧 Updated local git user.name: %s -> %s",
                    current_name,
                    expected_name,
                )
                config_updated = True

            if current_email != expected_email:
                self.core.run_git_command_with_separate_dirs(
                    ["config", "--local", "user.email", expected_email],
                    error_mode=SubprocessErrorMode.STRICT,
                    timeout=10,
                    operation_name="update local git user email",
                )
                logger.info(
                    "🔧 Updated local git user.email: %s -> %s",
                    current_email,
                    expected_email,
                )
                config_updated = True

            if config_updated:
                logger.info(
                    "✅ Local git config now matches environment variables"
                )
            else:
                logger.info(
                    "✅ Local git config already matches environment variables"
                )

            return config_updated

        except Exception as e:
            logger.error("Failed to enforce user config: %s", str(e))
            return False

    async def _create_sync_backup(self, _repo_path: str) -> bool:
        """
        Creates a simple timestamped backup branch before destructive sync.

        Args:
            _repo_path: Path to the git repository

        Returns:
            True if backup was created successfully, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_branch = f"backup_before_sync_{timestamp}"

            logger.info("📦 Creating backup branch: %s", backup_branch)

            # Get current branch name
            current_branch_result = (
                self.core.run_git_command_with_separate_dirs(
                    ["rev-parse", "--abbrev-ref", "HEAD"],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="get current branch for backup",
                )
            )

            if not current_branch_result.success:
                logger.warning("Could not determine current branch for backup")
                return False

            current_branch = current_branch_result.stdout.strip()

            # Create backup branch from current state
            backup_result = self.core.run_git_command_with_separate_dirs(
                ["checkout", "-b", backup_branch],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=30,
                operation_name="create backup branch",
            )

            if backup_result.success:
                logger.info("✅ Created backup branch: %s", backup_branch)

                # Return to original branch
                checkout_result = self.core.run_git_command_with_separate_dirs(
                    ["checkout", current_branch],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=30,
                    operation_name="return to original branch",
                )

                if checkout_result.success:
                    logger.info(
                        "✅ Returned to original branch: %s", current_branch
                    )

                    # Create backup metadata file
                    backup_info = {
                        "backup_branch": backup_branch,
                        "original_branch": current_branch,
                        "timestamp": timestamp,
                        "reason": "sync_operation",
                        "created_by": "git_lock_sign_extension",
                    }

                    backup_file = os.path.join(
                        self.core.git_metadata_base, f"backup_{timestamp}.json"
                    )
                    try:
                        import json

                        with open(backup_file, "w", encoding="utf-8") as f:
                            json.dump(backup_info, f, indent=2)
                        logger.info(
                            "📝 Created backup metadata: %s", backup_file
                        )
                    except Exception as e:
                        logger.warning(
                            "Could not create backup metadata: %s", e
                        )

                    return True
                else:
                    logger.warning(
                        "Could not return to original branch: %s",
                        checkout_result.stderr,
                    )
                    return False
            else:
                logger.warning(
                    "Failed to create backup branch: %s", backup_result.stderr
                )
                return False

        except Exception as e:
            logger.error("Failed to create backup branch: %s", str(e))
            return False

    def _verify_sync_success(
        self, repo_path: str, remote_name: str = "origin"
    ) -> bool:
        """
        Verifies that sync was successful by checking if local matches remote.

        Args:
            repo_path: Path to the git repository
            remote_name: Name of the git remote

        Returns:
            True if sync was successful, False otherwise
        """
        try:
            repo = self.core.get_repository(repo_path)
            if not repo:
                logger.warning(
                    "Could not access repository for sync verification"
                )
                return False

            # Get current branch
            current_branch_result = (
                self.core.run_git_command_with_separate_dirs(
                    ["rev-parse", "--abbrev-ref", "HEAD"],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="get current branch for verification",
                )
            )

            if not current_branch_result.success:
                logger.warning(
                    "Could not determine current branch for sync verification"
                )
                return False

            current_branch = current_branch_result.stdout.strip()
            remote_branch = f"{remote_name}/{current_branch}"

            # Check if remote branch exists
            remote_check = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", remote_branch],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="verify remote branch for sync verification",
            )

            if not remote_check.success:
                logger.warning(
                    "Remote branch %s not found for verification", remote_branch
                )
                return False

            # Compare local and remote commits
            local_commit = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "HEAD"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local commit for verification",
            )

            remote_commit = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", remote_branch],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get remote commit for verification",
            )

            if local_commit.success and remote_commit.success:
                local_hash = local_commit.stdout.strip()
                remote_hash = remote_commit.stdout.strip()

                if local_hash == remote_hash:
                    logger.info(
                        "✅ Sync verification successful: local matches remote"
                    )
                    return True
                else:
                    logger.warning(
                        "⚠️ Sync verification failed: local %s != remote %s",
                        local_hash[:8],
                        remote_hash[:8],
                    )
                    return False
            else:
                logger.warning("Could not get commit hashes for verification")
                return False

        except Exception as e:
            logger.error("Sync verification failed: %s", str(e))
            return False

    def _perform_initial_checkout(self, remote_name: str) -> GitOperationResult:
        """
        Perform initial checkout from remote for empty repositories.

        This is the critical missing piece that actually brings files into the work tree.
        Based on the legacy git service implementation.

        Args:
            remote_name: Name of the remote

        Returns:
            GitOperationResult with checkout details
        """
        try:
            logger.info(
                "🌱 Performing initial checkout from remote '%s'", remote_name
            )

            # Find the default branch from remote
            ls_remote_result = self.core.run_git_command_with_separate_dirs(
                ["ls-remote", "--symref", remote_name, "HEAD"],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=30,
                operation_name="find default remote branch",
            )

            default_branch = "main"  # fallback
            if ls_remote_result.success:
                # Parse output like: "ref: refs/heads/main	HEAD"
                for line in ls_remote_result.stdout.split("\n"):
                    if line.startswith("ref: refs/heads/"):
                        default_branch = line.split("/")[-1].split("\t")[0]
                        break

            logger.info("🌿 Detected remote default branch: %s", default_branch)

            # Handle any untracked files that might conflict with checkout
            logger.info(
                "🧹 Cleaning untracked files before checkout to avoid conflicts"
            )
            clean_result = self.core.run_git_command_with_separate_dirs(
                ["clean", "-fd"],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=30,
                operation_name="clean untracked files before checkout",
            )

            if clean_result.success:
                logger.info("✅ Successfully cleaned untracked files")
            else:
                logger.warning(
                    "⚠️ Failed to clean untracked files: %s", clean_result.stderr
                )

            # Create and checkout the default branch tracking the remote
            # This is the KEY operation that actually brings files into the work tree
            checkout_result = self.core.run_git_command_with_separate_dirs(
                [
                    "checkout",
                    "-b",
                    default_branch,
                    f"{remote_name}/{default_branch}",
                ],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=60,
                operation_name="checkout initial branch from remote",
            )

            if checkout_result.success:
                logger.info(
                    "✅ Successfully checked out initial branch '%s' from remote",
                    default_branch,
                )

                # Ensure .gitignore exists after checkout
                gitignore_path = os.path.join(
                    self.core.work_tree_base, ".gitignore"
                )
                if not os.path.exists(gitignore_path):
                    logger.info(
                        "📋 No .gitignore found after checkout - this is normal for initial setup"
                    )
                else:
                    logger.info("📋 .gitignore exists after checkout")

                return GitOperationResult(
                    success=True,
                    message=f"Successfully performed initial checkout from remote branch {default_branch}",
                )
            else:
                logger.error(
                    "❌ Failed to checkout from remote: %s",
                    checkout_result.stderr,
                )
                return GitOperationResult(
                    success=False,
                    message="Failed to perform initial checkout from remote",
                    error=f"Initial checkout failed: {checkout_result.stderr}",
                )

        except Exception as e:
            logger.error("Error performing initial checkout: %s", str(e))
            return GitOperationResult(
                success=False,
                message="Error performing initial checkout",
                error=str(e),
            )

    def _get_current_branch(self) -> Optional[str]:
        """Get the current branch name."""
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["branch", "--show-current"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="get current branch",
            )

            if result.success:
                return result.stdout.strip()
            else:
                return None

        except Exception as e:
            logger.error("Error getting current branch: %s", str(e))
            return None
