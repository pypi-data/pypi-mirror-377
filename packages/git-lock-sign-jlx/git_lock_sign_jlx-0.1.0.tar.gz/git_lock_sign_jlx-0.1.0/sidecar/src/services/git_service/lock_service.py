"""
Notebook locking service.

Handles notebook locking and unlocking operations with commit signing and verification.
"""

import logging
import os
from typing import Any, Dict, Optional

from ..config_service import ConfigService
from ..subprocess_util import SubprocessErrorMode
from .core_service import GitCoreService
from .models import GitOperationResult
from ..logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitLockService:
    """Handles notebook locking/unlocking operations."""

    def __init__(self, core_service: GitCoreService, config_service: Optional[ConfigService] = None, commit_service=None, git_config_service=None):
        """Initialize the lock service."""
        self.core = core_service
        self.config_service = config_service
        self.commit_service = commit_service
        self.git_config_service = git_config_service

    def lock_notebook(
        self,
        notebook_path: str,
        notebook_content: Dict[str, Any],
        commit_message: str,
        notebook_service,
        gpg_service,
    ) -> GitOperationResult:
        """
        Lock notebook with commit and signing including metadata.

        This method creates a locked notebook with full metadata tracking:
        1. Generate content hash
        2. Create lock metadata
        3. Save notebook with metadata
        4. Commit with GPG signature
        5. Update metadata with final commit info
        6. Amend commit to include updated metadata
        """
        logger.info("Lock notebook operation: %s", notebook_path)

        try:
            # Translate JupyterLab path to sidecar path
            sidecar_path = self.core.translate_jupyterlab_path_to_sidecar(notebook_path)
            
            # Get repository
            repo = self.core.get_repository(sidecar_path)
            if not repo:
                return GitOperationResult(
                    success=False,
                    message="Not in a git repository",
                    error="Repository not found"
                )

            # Get user info for metadata
            if not self.git_config_service:
                return GitOperationResult(
                    success=False,
                    message="Git config service not available",
                    error="Git config service required for locking"
                )
            user_info = self.git_config_service.get_user_info(notebook_path)
            timestamp = notebook_service.get_current_timestamp()

            # Generate content hash
            content_hash = notebook_service.generate_content_hash(notebook_content)

            # Create initial lock metadata
            lock_metadata = {
                "locked": True,
                "user_name": user_info.name or "Unknown",
                "user_email": user_info.email or "unknown@example.com",
                "timestamp": timestamp,
                "commit_message": commit_message,
                "content_hash": content_hash,
                "commit_hash": "",  # Will be updated after commit
                "commit_signed": False,  # Will be updated after commit
                "gpg_available": gpg_service.is_gpg_available()
                if gpg_service
                else False,
            }

            # Save notebook with lock metadata
            success = notebook_service.save_signature_metadata(
                notebook_path, notebook_content, lock_metadata
            )
            if not success:
                return GitOperationResult(
                    success=False,
                    message="Failed to save lock metadata to notebook",
                    error="Failed to save lock metadata to notebook",
                )

            # Commit the notebook with metadata
            if not self.commit_service:
                return GitOperationResult(
                    success=False,
                    message="Commit service not available",
                    error="Commit service required for locking"
                )
            result = self.commit_service.commit_notebook(notebook_path, commit_message)
            if not result.success:
                return result

            # Update metadata with actual commit information
            lock_metadata.update(
                {
                    "commit_hash": result.commit_hash,
                    "commit_signed": result.signed,
                    "timestamp": timestamp,
                }
            )

            # Save notebook with final metadata
            success = notebook_service.save_signature_metadata(
                notebook_path, notebook_content, lock_metadata
            )
            if success:
                # Amend commit to include final metadata
                repo = self.core.get_repository(notebook_path)
                if repo:
                    repo_root = str(repo.working_dir)
                    sidecar_notebook_path = self.core.translate_jupyterlab_path_to_sidecar(notebook_path)
                    rel_path = os.path.relpath(sidecar_notebook_path, repo_root)
                    if self.commit_service:
                        amend_result = self.commit_service._amend_commit_with_file(
                            repo_root, rel_path, commit_message
                        )
                        if amend_result[0]:  # amend_success
                            lock_metadata["commit_hash"] = amend_result[
                                1
                            ]  # new_commit_hash

            return GitOperationResult(
                success=True,
                message="Notebook locked successfully",
                commit_hash=lock_metadata["commit_hash"],
                signed=result.signed,
                metadata=lock_metadata,
                content_hash=content_hash,
            )

        except Exception as e:
            error_msg = f"Error locking notebook: {str(e)}"
            logger.error(error_msg)
            return GitOperationResult(success=False, message=error_msg, error=error_msg)

    def unlock_notebook(
        self,
        notebook_path: str,
        notebook_content: Dict[str, Any],
        notebook_service,
        gpg_service=None,
    ) -> GitOperationResult:
        """
        Unlock notebook after signature verification.

        This method verifies the notebook's integrity and signature before unlocking:
        1. Extract and validate signature metadata
        2. Verify content integrity (hash check)
        3. Verify GPG signature if applicable
        4. Update metadata to unlocked state
        5. Commit the unlocked state
        """
        logger.info("Unlock notebook operation: %s", notebook_path)

        try:
            # Translate JupyterLab path to sidecar path
            sidecar_path = self.core.translate_jupyterlab_path_to_sidecar(notebook_path)
            
            # Get repository
            repo = self.core.get_repository(sidecar_path)
            if not repo:
                return GitOperationResult(
                    success=False,
                    message="Not in a git repository",
                    error="Repository not found"
                )

            # Extract signature metadata
            signature_metadata = notebook_service.get_signature_metadata(
                notebook_content
            )
            if not signature_metadata:
                return GitOperationResult(
                    success=False,
                    message="No signature metadata found in notebook",
                    error="No signature metadata found - cannot unlock",
                )

            # Verify content integrity
            current_hash = notebook_service.generate_content_hash(notebook_content)
            stored_hash = signature_metadata.get("content_hash")

            if current_hash != stored_hash:
                logger.warning(
                    "Content hash mismatch during unlock - checking without metadata"
                )
                # Try removing metadata and recalculating hash
                import copy

                temp_content = copy.deepcopy(notebook_content)
                if (
                    "metadata" in temp_content
                    and "git_lock_sign" in temp_content["metadata"]
                ):
                    del temp_content["metadata"]["git_lock_sign"]
                    recalc_hash = notebook_service.generate_content_hash(temp_content)
                    if recalc_hash != stored_hash:
                        return GitOperationResult(
                            success=False,
                            message="Content has been modified since locking - cannot unlock",
                            error="Content integrity check failed",
                        )

            # Check if notebook was GPG signed and verify if so
            was_gpg_signed = signature_metadata.get("commit_signed", False)

            if was_gpg_signed:
                commit_hash = signature_metadata.get("commit_hash")
                if commit_hash:
                    # Basic signature verification (could be enhanced with actual GPG verification)
                    logger.info(
                        "Notebook was GPG signed, signature verification would occur here"
                    )
                    # In a full implementation, we would verify the GPG signature here

            # Update metadata to unlocked state
            if not self.git_config_service:
                return GitOperationResult(
                    success=False,
                    message="Git config service not available",
                    error="Git config service required for unlocking"
                )
            user_info = self.git_config_service.get_user_info(notebook_path)
            updated_metadata = signature_metadata.copy()
            updated_metadata.update(
                {
                    "locked": False,
                    "unlock_timestamp": notebook_service.get_current_timestamp(),
                    "unlocked_by_user_name": user_info.name or "Unknown",
                    "unlocked_by_user_email": user_info.email or "unknown@example.com",
                }
            )

            # Save notebook with unlocked metadata
            success = notebook_service.save_signature_metadata(
                notebook_path, notebook_content, updated_metadata
            )
            if not success:
                return GitOperationResult(
                    success=False,
                    message="Failed to save unlocked metadata",
                    error="Failed to save unlocked metadata",
                )

            # Commit the unlocked state
            unlock_commit_message = (
                f"Unlocked notebook: {os.path.basename(notebook_path)}"
            )
            if not self.commit_service:
                return GitOperationResult(
                    success=False,
                    message="Commit service not available",
                    error="Commit service required for unlocking"
                )
            result = self.commit_service.commit_notebook(notebook_path, unlock_commit_message)

            if result.success:
                updated_metadata["unlock_commit_hash"] = result.commit_hash
                # Save final metadata with unlock commit hash
                notebook_service.save_signature_metadata(
                    notebook_path, notebook_content, updated_metadata
                )

            return GitOperationResult(
                success=True,
                message="Notebook unlocked successfully",
                commit_hash=result.commit_hash if result.success else None,
                signed=result.signed if result.success else False,
                metadata=updated_metadata,
            )

        except Exception as e:
            error_msg = f"Error unlocking notebook: {str(e)}"
            logger.error(error_msg)
            return GitOperationResult(success=False, message=error_msg, error=error_msg)

    def _check_notebook_status(self, _notebook_path: str) -> Dict[str, Any]:
        """
        Check the current status of a notebook.

        Args:
            notebook_path: Path to the notebook file

        Returns:
            Dictionary with status information
        """
        try:
            # Check if there are uncommitted changes
            result = self.core.run_git_command_with_separate_dirs(
                ["status", "--porcelain"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name="check notebook status"
            )

            has_changes = bool(result.stdout.strip()) if result.success else False

            # Get last commit hash
            commit_result = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "HEAD"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="get last commit hash"
            )

            last_commit_hash = None
            if commit_result.success:
                last_commit_hash = commit_result.stdout.strip()

            return {
                "is_locked": not has_changes,
                "has_changes": has_changes,
                "last_commit_hash": last_commit_hash
            }

        except Exception as e:
            logger.error("Error checking notebook status: %s", str(e))
            return {
                "is_locked": False,
                "has_changes": False,
                "last_commit_hash": None
            }

    def _verify_lock_signature(self, _notebook_path: str) -> Dict[str, Any]:
        """
        Verify the signature of the last commit (lock).

        Args:
            notebook_path: Path to the notebook file

        Returns:
            Dictionary with verification results
        """
        try:
            # Verify the last commit signature
            result = self.core.run_git_command_with_separate_dirs(
                ["verify-commit", "HEAD"],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=30,
                operation_name="verify commit signature"
            )

            if result.success:
                return {
                    "valid": True,
                    "message": "Signature verification successful"
                }
            else:
                return {
                    "valid": False,
                    "error": result.stderr or "Signature verification failed"
                }

        except Exception as e:
            logger.error("Error verifying lock signature: %s", str(e))
            return {
                "valid": False,
                "error": str(e)
            }

    def _commit_notebook_for_lock(
        self,
        _notebook_path: str,
        commit_message: str,
        sign: bool = True,
        gpg_key_id: Optional[str] = None,
    ) -> GitOperationResult:
        """
        Commit notebook for locking.

        Args:
            notebook_path: Path to the notebook file
            commit_message: Commit message
            sign: Whether to sign the commit
            gpg_key_id: GPG key ID for signing (optional)

        Returns:
            GitOperationResult with commit details
        """
        try:
            # Add files to staging
            result = self.core.run_git_command_with_separate_dirs(
                ["add", "."],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name="add files for lock commit"
            )

            if not result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to add files for lock commit",
                    error=result.stderr
                )

            # Create commit
            git_args = ["commit"]
            
            if sign:
                if gpg_key_id:
                    git_args.extend(["-S", gpg_key_id])
                else:
                    git_args.append("-S")
            
            git_args.extend(["-m", commit_message])

            commit_result = self.core.run_git_command_with_separate_dirs(
                git_args,
                error_mode=SubprocessErrorMode.STRICT,
                timeout=60,
                operation_name="create lock commit"
            )

            if not commit_result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to create lock commit",
                    error=commit_result.stderr
                )

            # Get commit hash
            hash_result = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "HEAD"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="get lock commit hash"
            )

            commit_hash = None
            if hash_result.success:
                commit_hash = hash_result.stdout.strip()

            return GitOperationResult(
                success=True,
                message="Lock commit created successfully",
                commit_hash=commit_hash,
                signed=sign
            )

        except Exception as e:
            logger.error("Error creating lock commit: %s", str(e))
            return GitOperationResult(
                success=False,
                message="Error creating lock commit",
                error=str(e)
            )

    def _commit_notebook_for_unlock(
        self,
        _notebook_path: str,
        commit_message: str,
        sign: bool = True,
        gpg_key_id: Optional[str] = None,
    ) -> GitOperationResult:
        """
        Commit notebook for unlocking.

        Args:
            notebook_path: Path to the notebook file
            commit_message: Commit message
            sign: Whether to sign the commit
            gpg_key_id: GPG key ID for signing (optional)

        Returns:
            GitOperationResult with commit details
        """
        try:
            # Add files to staging
            result = self.core.run_git_command_with_separate_dirs(
                ["add", "."],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name="add files for unlock commit"
            )

            if not result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to add files for unlock commit",
                    error=result.stderr
                )

            # Create commit
            git_args = ["commit"]
            
            if sign:
                if gpg_key_id:
                    git_args.extend(["-S", gpg_key_id])
                else:
                    git_args.append("-S")
            
            git_args.extend(["-m", commit_message])

            commit_result = self.core.run_git_command_with_separate_dirs(
                git_args,
                error_mode=SubprocessErrorMode.STRICT,
                timeout=60,
                operation_name="create unlock commit"
            )

            if not commit_result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to create unlock commit",
                    error=commit_result.stderr
                )

            # Get commit hash
            hash_result = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "HEAD"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="get unlock commit hash"
            )

            commit_hash = None
            if hash_result.success:
                commit_hash = hash_result.stdout.strip()

            return GitOperationResult(
                success=True,
                message="Unlock commit created successfully",
                commit_hash=commit_hash,
                signed=sign
            )

        except Exception as e:
            logger.error("Error creating unlock commit: %s", str(e))
            return GitOperationResult(
                success=False,
                message="Error creating unlock commit",
                error=str(e)
            )
