"""
Git status service.

Handles git status checks, repository status, and change detection.
"""

import logging
import os
from typing import Any, Dict, Optional

from ..config_service import ConfigService
from ..subprocess_util import SubprocessErrorMode
from .core_service import GitCoreService
from .models import GitStatusResult
from ..logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitStatusService:
    """Handles git status and change detection."""

    def __init__(self, core_service: GitCoreService, config_service: Optional[ConfigService] = None):
        """Initialize the status service."""
        self.core = core_service
        self.config_service = config_service

    def get_status(self, notebook_path: str) -> GitStatusResult:
        """
        Get repository and notebook status.

        Args:
            notebook_path: Path to the notebook file

        Returns:
            GitStatusResult with status information
        """
        try:
            # Translate JupyterLab path to sidecar path
            sidecar_path = self.core.translate_jupyterlab_path_to_sidecar(notebook_path)
            
            # Normalize to work tree path
            work_tree_path = self.core._normalize_to_work_tree(sidecar_path)
            
            # Check if in git repository
            repo = self.core.get_repository(work_tree_path)
            if not repo:
                return GitStatusResult(
                    is_git_repository=False,
                    is_locked=False,
                    repository_path=None,
                    signature_metadata=None,
                    last_commit_hash=None
                )

            # Get repository root
            repo_root = repo.working_dir
            if not repo_root:
                return GitStatusResult(
                    is_git_repository=True,
                    is_locked=False,
                    repository_path=None,
                    signature_metadata=None,
                    last_commit_hash=None
                )

            # Get last commit hash
            last_commit_hash = None
            try:
                last_commit_hash = str(repo.head.commit.hexsha)
            except Exception:
                pass  # No commits yet
            
            # TODO: Check if notebook is locked by examining metadata
            is_locked = False
            signature_metadata = None

            return GitStatusResult(
                is_git_repository=True,
                is_locked=is_locked,
                repository_path=str(repo_root),
                signature_metadata=signature_metadata,
                last_commit_hash=last_commit_hash
            )

        except Exception as e:
            logger.error("Error getting git status: %s", str(e))
            return GitStatusResult(
                is_git_repository=False,
                is_locked=False,
                repository_path=None,
                signature_metadata=None,
                last_commit_hash=None
            )

    def has_uncommitted_changes(self, notebook_path: str) -> bool:
        """
        Check if the specified notebook has uncommitted changes.

        Args:
            notebook_path: Path to the notebook file (may be from JupyterLab perspective)

        Returns:
            True if there are uncommitted changes, False otherwise
        """
        try:
            logger.info("Checking for uncommitted changes in: %s", notebook_path)

            # Translate JupyterLab path to sidecar path
            sidecar_notebook_path = self.core.translate_jupyterlab_path_to_sidecar(notebook_path)

            repo = self.core.get_repository(sidecar_notebook_path)
            if not repo:
                logger.debug("Repository not found for path: %s", notebook_path)
                return False

            repo_root = str(repo.working_dir)
            logger.debug("Repository root: %s", repo_root)

            # Get relative path of the notebook from repo root
            notebook_rel_path = os.path.relpath(sidecar_notebook_path, repo_root)
            logger.debug("Relative notebook path: %s", notebook_rel_path)

            # For file deletions, the file won't exist but there may still be uncommitted changes
            # We need to check git status first before making any decisions based on file existence
            file_exists = os.path.exists(sidecar_notebook_path)
            logger.info("File exists check: %s", file_exists)
            
            if not file_exists:
                logger.info("File does not exist: %s - checking if it's a deletion", sidecar_notebook_path)
                # Check git status to see if this is a deletion that needs to be committed
                status_result = self.core.run_git_command_with_separate_dirs(
                    ["status", "--porcelain", notebook_rel_path],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="check git status for file deletion"
                )
                
                if status_result.returncode == 0:
                    status_output = status_result.stdout.strip()
                    # Check if the file is marked as deleted in git status
                    if status_output.startswith("D ") or status_output.startswith(" D"):
                        logger.info("File marked as deleted in git status: %s", status_output)
                        return True  # File is deleted but not committed - this is an uncommitted change
                    elif status_output:
                        logger.info("File has other git status: %s", status_output)
                        return True  # Some other uncommitted change
                
                logger.info("File does not exist and no git status changes - likely never tracked")
                return False

            # Check file modification time and size for debugging (only if file exists)
            if file_exists:
                file_stat = os.stat(sidecar_notebook_path)
                file_mtime = file_stat.st_mtime
                file_size = file_stat.st_size
                logger.debug("File modification time: %s", file_mtime)
                logger.debug("File size: %s bytes", file_size)

                # Read and log a snippet of the actual file content for debugging
                try:
                    with open(sidecar_notebook_path, encoding="utf-8") as f:
                        content = f.read()
                        # Log first 200 chars and look for specific patterns
                        content_snippet = content[:200] + (
                            "..." if len(content) > 200 else ""
                        )
                        logger.debug("File content snippet: %s", content_snippet)

                except Exception as e:
                    logger.warning("Could not read file content: %s", str(e))

            # Check if the file has uncommitted changes using git status
            status_result = self.core.run_git_command_with_separate_dirs(
                ["status", "--porcelain", notebook_rel_path],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check git status for uncommitted changes"
            )

            logger.debug(
                "Git status command: git status --porcelain %s", notebook_rel_path
            )
            logger.debug("Git status return code: %s", status_result.returncode)
            logger.debug("Git status stdout: '%s'", status_result.stdout)
            logger.debug("Git status stderr: '%s'", status_result.stderr)

            if status_result.returncode != 0:
                logger.warning(
                    "Could not check git status for: %s, error: %s",
                    notebook_path,
                    status_result.stderr,
                )
                return False

            # If there's any output, the file has changes
            status_output = status_result.stdout.strip()
            has_changes = bool(status_output)

            if has_changes:
                logger.info("Found uncommitted changes in: %s", notebook_path)
                logger.info("Git status output: '%s'", status_output)

                # Parse the status to understand what kind of changes
                if status_output.startswith("M "):
                    logger.info("File is modified")
                elif status_output.startswith("A "):
                    logger.info("File is added")
                elif status_output.startswith("D ") or status_output.startswith(" D"):
                    logger.info("File is deleted")
                elif status_output.startswith("?? "):
                    logger.info("File is untracked - needs to be added to git")
                elif status_output.startswith("AM "):
                    logger.info("File is added and modified")
                else:
                    logger.info("File has other status: %s", status_output[:2])
            else:
                logger.info("No uncommitted changes found in: %s", notebook_path)
                logger.info("This means the file is clean according to git")

                # Let's also check what git thinks the last committed content was
                try:
                    last_commit_result = self.core.run_git_command_with_separate_dirs(
                        ["show", f"HEAD:{notebook_rel_path}"],
                        error_mode=SubprocessErrorMode.SILENT,
                        timeout=10,
                        operation_name="get last committed content"
                    )

                    if last_commit_result.success:
                        logger.debug("Successfully retrieved last committed content")
                    else:
                        logger.debug("Could not get last committed content")

                except Exception as e:
                    logger.debug("Error checking last committed content: %s", str(e))

            # Additional debugging: run git diff to see if there are any differences
            # even when git status says there are none
            try:
                diff_result = self.core.run_git_command_with_separate_dirs(
                    ["diff", notebook_rel_path],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="check git diff for inconsistencies"
                )

                if diff_result.success:
                    diff_output = diff_result.stdout.strip()
                    if diff_output:
                        logger.warning(
                            "Git diff shows changes even though git status says clean!"
                        )
                        logger.warning(
                            "Git diff output: %s...", diff_output[:500]
                        )  # First 500 chars
                        # If diff shows changes but status doesn't, we might have an issue
                        if not has_changes and diff_output:
                            logger.error(
                                "INCONSISTENCY: git diff shows changes but git status shows clean!"
                            )
                            # Force return True in this case
                            return True
                    else:
                        logger.debug("Git diff confirms no changes")
                else:
                    logger.debug("Git diff failed: %s", diff_result.stderr)

            except Exception as e:
                logger.debug("Error running git diff: %s", str(e))

            return has_changes

        except Exception as e:
            logger.error("Error checking for uncommitted changes: %s", str(e))
            logger.error("Exception details:", exc_info=True)
            return False

    def has_unpushed_commits_from_other_files(self, notebook_path: str) -> bool:
        """
        Check if the repository has unpushed commits from files OTHER than the current notebook.

        This ensures we only trigger auto-push when there are commits from other notebooks
        or files, not when the current notebook has unpushed commits.

        Args:
            notebook_path: Path to the current notebook file

        Returns:
            True if there are unpushed commits from other files, False otherwise
        """
        try:
            # Translate JupyterLab path to sidecar path
            sidecar_notebook_path = self.core.translate_jupyterlab_path_to_sidecar(notebook_path)
            
            repo = self.core.get_repository(sidecar_notebook_path)
            if not repo:
                logger.debug("Repository not found for path: %s", notebook_path)
                return False

            repo_root = str(repo.working_dir)

            # Get relative path of the current notebook from repo root
            current_notebook_rel_path = os.path.relpath(sidecar_notebook_path, repo_root)

            # Check if there's a remote to push to
            remotes_result = self.core.run_git_command_with_separate_dirs(
                ["remote"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="list remotes"
            )

            if not remotes_result.success or not remotes_result.stdout.strip():
                logger.debug("No remotes found for repository: %s", repo_root)
                return False

            # Get the current branch
            branch_result = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get current branch for unpushed commits check"
            )

            if not branch_result.success:
                logger.debug("Could not get current branch for: %s", repo_root)
                return False

            current_branch = branch_result.stdout.strip()

            # Get files changed in unpushed commits
            # This command shows the files that were changed in commits that exist locally but not on remote
            files_changed_result = self.core.run_git_command_with_separate_dirs(
                [
                    "log",
                    f"origin/{current_branch}..HEAD",
                    "--name-only",
                    "--pretty=format:",
                ],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get files changed in unpushed commits"
            )

            # If command succeeds and has output, check which files were changed
            if (
                files_changed_result.success
                and files_changed_result.stdout.strip()
            ):
                changed_files = set()
                for line in files_changed_result.stdout.strip().split("\n"):
                    if line.strip():  # Skip empty lines
                        changed_files.add(line.strip())

                # Remove the current notebook from the changed files
                changed_files.discard(current_notebook_rel_path)

                if changed_files:
                    logger.info(
                        "Found unpushed commits from other files in repository: %s",
                        repo_root,
                    )
                    logger.debug(
                        "Changed files (excluding current notebook): %s",
                        list(changed_files),
                    )
                    return True
                else:
                    logger.debug(
                        "Found unpushed commits but only from current notebook: %s",
                        current_notebook_rel_path,
                    )
                    return False

            # If the above command fails (e.g., no remote branch), try alternative approach
            if not files_changed_result.success:
                # Check if there are any commits at all that aren't from the current file
                all_files_result = self.core.run_git_command_with_separate_dirs(
                    [
                        "log",
                        "--name-only",
                        "--pretty=format:",
                        "-10",
                    ],  # Check last 10 commits
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="get all files in recent commits"
                )

                if all_files_result.success and all_files_result.stdout.strip():
                    changed_files = set()
                    for line in all_files_result.stdout.strip().split("\n"):
                        if line.strip():
                            changed_files.add(line.strip())

                    # Remove current notebook and check if other files exist
                    changed_files.discard(current_notebook_rel_path)

                    if changed_files:
                        logger.info(
                            "Found local commits from other files (no remote tracking): %s",
                            repo_root,
                        )
                        return True

            logger.debug(
                "No unpushed commits from other files found in repository: %s",
                repo_root,
            )
            return False

        except Exception as e:
            logger.error(
                "Error checking for unpushed commits from other files: %s", str(e)
            )
            return False

    def get_repo_root(self, file_path: str) -> Optional[str]:
        """
        Get git repository root for a file path using the worktree setup.
        
        Args:
            file_path: Path to a file within the repository
            
        Returns:
            Repository root path or None if not in a git repository
        """
        try:
            # Translate JupyterLab path to sidecar path if needed
            sidecar_path = self.core.translate_jupyterlab_path_to_sidecar(file_path)
            
            # For our worktree setup, we know the work tree base is the repo root
            if sidecar_path.startswith(self.core.work_tree_base):
                return self.core.work_tree_base
            
            # Fallback: check if the path exists and is under our work tree
            normalized_path = self.core._normalize_to_work_tree(sidecar_path)
            if normalized_path == self.core.work_tree_base:
                return self.core.work_tree_base
                
            return None
            
        except Exception as e:
            logger.error("Error getting repository root: %s", str(e))
            return None

    def _get_last_commit_hash(self) -> Optional[str]:
        """Get the hash of the last commit."""
        try:
            result = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "HEAD"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="get last commit hash"
            )

            if result.success:
                return result.stdout.strip()
            else:
                return None

        except Exception as e:
            logger.error("Error getting last commit hash: %s", str(e))
            return None

    def _get_signature_metadata(self) -> Optional[Dict[str, Any]]:
        """Get signature metadata from the last commit."""
        try:
            # Get commit signature information
            result = self.core.run_git_command_with_separate_dirs(
                ["log", "-1", "--show-signature"],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=30,
                operation_name="get signature metadata"
            )

            if not result.success:
                return None

            # Parse signature information
            signature_metadata = {}
            lines = result.stdout.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('gpg:'):
                    signature_metadata['gpg_info'] = line
                elif line.startswith('Good signature'):
                    signature_metadata['valid'] = True
                elif line.startswith('Bad signature'):
                    signature_metadata['valid'] = False

            return signature_metadata if signature_metadata else None

        except Exception as e:
            logger.error("Error getting signature metadata: %s", str(e))
            return None

    def _get_current_branch(self) -> Optional[str]:
        """Get the current branch name."""
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
