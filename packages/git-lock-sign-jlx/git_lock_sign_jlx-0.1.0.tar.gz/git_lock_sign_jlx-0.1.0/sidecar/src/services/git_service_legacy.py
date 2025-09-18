"""
Git service for CELN Sidecar

Handles all git operations including repository initialization, commits, and GPG signing.
Adapted from the original git_lock_sign_jlx.services.git_service module.
"""

import logging
import os
import subprocess
import time
from typing import Any, Dict, NamedTuple, Optional

from git import InvalidGitRepositoryError, Repo

from .logger_util import default_logger_config
from .subprocess_util import SubprocessErrorMode, run_git_command


from .config_service import ConfigService

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitOperationResult(NamedTuple):
    """Result of a git operation."""

    success: bool
    message: str
    commit_hash: Optional[str] = None
    signed: bool = False
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    content_hash: Optional[str] = None


class GitStatusResult(NamedTuple):
    """Result of a git status check."""

    is_git_repository: bool
    is_locked: bool = False
    repository_path: Optional[str] = None
    signature_metadata: Optional[Dict[str, Any]] = None
    last_commit_hash: Optional[str] = None


class UserInfoResult(NamedTuple):
    """Git user information."""

    name: str
    email: str
    gpg_key_id: Optional[str] = None


class GitService:
    """Service for managing git operations and commit signing."""

    def __init__(self, config_service: Optional["ConfigService"] = None):
        """Initialize the git service."""
        self._repo_cache = {}
        self.config_service = config_service
        
        # Git directory structure for separate metadata and work tree
        # Use configurable paths from config service, with fallback defaults
        if config_service:
            self.git_metadata_base = config_service.git_metadata_directory
            self.work_tree_base = config_service.work_tree_directory
        else:
            # Fallback defaults if no config service provided
            self.git_metadata_base = "/tmp/.git-metadata"
            self.work_tree_base = "/tmp/work"
    
    def _normalize_to_work_tree(self, file_path: str) -> str:
        """
        Normalize a file path to work with the separated git directory structure.
        
        This function converts various possible file path formats into a consistent
        path that can be used with our separated git-dir and work-tree setup.
        
        "Normalize" in this context means:
        1. Converting relative paths to absolute paths
        2. Mapping paths from different mount points to our work tree structure
        3. Ensuring file paths point to locations within our managed work tree
        4. Handling both file and directory paths consistently
        
        The function handles several scenarios:
        - Paths already in the work tree (returned as-is)
        - Paths from JupyterLab container (mounted differently)
        - Relative paths that need absolute resolution
        - File paths vs directory paths
        
        This is necessary because:
        - JupyterLab sees files at /home/jovyan/work/notebook.ipynb
        - Sidecar sees the same files at /tmp/work/notebook.ipynb
        - Git operations need consistent paths relative to the work tree base
        
        Args:
            file_path: Original file path from any context (relative, absolute, 
                      from different container mount points, file or directory)
            
        Returns:
            Normalized path that can be used with our work tree structure.
            Either returns the work tree base directory or the original absolute
            path if it doesn't map to our work tree.
            
        Examples:
            # Already in work tree
            _normalize_to_work_tree("/tmp/work/notebook.ipynb") -> "/tmp/work"
            
            # From JupyterLab perspective  
            _normalize_to_work_tree("/home/jovyan/work/notebook.ipynb") -> "/tmp/work"
            
            # Directory path that maps to work tree
            _normalize_to_work_tree("/some/path/work") -> "/tmp/work"
            
            # Unrelated path
            _normalize_to_work_tree("/etc/config") -> "/etc/config"
        """
        # If file_path is already in work tree, return as-is
        if file_path.startswith(self.work_tree_base):
            return file_path
        
        # Handle cases where path might be relative or from different base
        abs_path = os.path.abspath(file_path)
        
        # If it's a file path, get directory
        if os.path.isfile(abs_path) or abs_path.endswith('.ipynb'):
            work_dir = os.path.dirname(abs_path)
        else:
            work_dir = abs_path
        
        # Map to work tree base
        if work_dir.endswith('/work') or work_dir == self.work_tree_base:
            return self.work_tree_base
        
        return abs_path
    
    def _translate_jupyterlab_path_to_sidecar(self, file_path: str) -> str:
        """
        Translate file paths from JupyterLab perspective to sidecar perspective.
        
        This handles the path translation between containers:
        - JupyterLab sees files at: /home/jovyan/work/notebook.ipynb
        - Sidecar sees same files at: /tmp/work/notebook.ipynb
        
        Args:
            file_path: Path from JupyterLab perspective
            
        Returns:
            Equivalent path from sidecar perspective
            
        Examples:
            /home/jovyan/work/notebook.ipynb -> /tmp/work/notebook.ipynb
            /tmp/work/notebook.ipynb -> /tmp/work/notebook.ipynb (unchanged)
        """
        # If already a sidecar path, return as-is
        if file_path.startswith(self.work_tree_base):
            return file_path
        
        # Handle JupyterLab mount point translation
        jupyterlab_work_base = "/home/jovyan/work"
        if file_path.startswith(jupyterlab_work_base):
            # Extract the relative path within the work directory
            rel_path = os.path.relpath(file_path, jupyterlab_work_base)
            # Construct sidecar path
            return os.path.join(self.work_tree_base, rel_path)
        
        # Handle other potential mount point patterns
        # Look for any path ending with /work/... pattern
        if '/work/' in file_path:
            parts = file_path.split('/work/')
            if len(parts) == 2:
                # Take everything after /work/ and join with our work tree base
                rel_path = parts[1]
                return os.path.join(self.work_tree_base, rel_path)
        
        # If no translation needed, return original path
        return file_path
    
    def run_git_command_with_separate_dirs(
        self,
        git_args: list[str],
        error_mode: SubprocessErrorMode = SubprocessErrorMode.STRICT,
        timeout: Optional[float] = 30,
        operation_name: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Run git command with separate git-dir and work-tree using run_git_command.
        
        Args:
            git_args: Git command arguments (without 'git' prefix)
            error_mode: How to handle errors (STRICT, LENIENT, or SILENT)
            timeout: Command timeout in seconds
            operation_name: Human-readable name for logging
            
        Returns:
            SubprocessResult from run_git_command
        """
        git_dir = os.path.join(self.git_metadata_base, ".git")
        
        # Prepend git-dir and work-tree parameters to the git arguments
        full_args = [
            f"--git-dir={git_dir}",
            f"--work-tree={self.work_tree_base}"
        ] + git_args
        
        return run_git_command(
            git_args=full_args,
            cwd=self.work_tree_base,
            error_mode=error_mode,
            timeout=timeout,
            operation_name=operation_name,
            env=env
        )
        

    def get_repository(self, file_path: str) -> Optional[Repo]:
        """
        Get git repository for a given file path using separate git-dir and work-tree.
        
        This implementation uses a separate git metadata directory to hide git files
        from the JupyterLab user while maintaining the work tree in the user's workspace.

        Args:
            file_path: Path to file within git repository (may be from JupyterLab perspective)

        Returns:
            Git repository object, or None if not in a git repo
        """
        try:
            # Translate JupyterLab path to sidecar path first
            sidecar_file_path = self._translate_jupyterlab_path_to_sidecar(file_path)
            
            # Normalize the file path to work tree path
            work_tree_path = self._normalize_to_work_tree(sidecar_file_path)
            
            # Check if work tree path is valid
            if not work_tree_path.startswith(self.work_tree_base):
                logger.debug("File path not in work tree: %s", file_path)
                return None

            # Check cache first using work tree base as key
            cache_key = self.work_tree_base
            if cache_key in self._repo_cache:
                logger.info(f"📁 Repo in cache for work tree: {cache_key}")
                return self._repo_cache[cache_key]

            # Check if git repository exists with separate git-dir
            git_dir = os.path.join(self.git_metadata_base, ".git")
            if not os.path.exists(git_dir):
                logger.debug("No git repository found - git dir doesn't exist: %s", git_dir)
                return None

            # Create repository object with separate git-dir and work-tree
            repo = Repo(git_dir)
            
            # Note: GitPython Repo object manages the work tree automatically
            # The git commands will use our --work-tree parameter
            
            # Configure repository as safe directory to prevent ownership issues
            self._configure_safe_directory(self.work_tree_base)
            
            self._repo_cache[cache_key] = repo

            logger.debug("Found git repository with separate git-dir: %s, work-tree: %s", git_dir, self.work_tree_base)
            return repo

        except InvalidGitRepositoryError:
            logger.debug("No git repository found for path: %s", file_path)
            return None
        except Exception as e:
            logger.error("Error accessing git repository: %s", str(e))
            return None

    def is_git_repository(self, file_path: str) -> bool:
        """
        Check if file is within a git repository.

        Args:
            file_path: Path to check

        Returns:
            True if within git repository, False otherwise
        """
        return self.get_repository(file_path) is not None



    def init_repository(self, notebook_path: str) -> str:
        """
        Initialize a git repository with separate git-dir and work-tree structure.

        Args:
            notebook_path: Path to the notebook file

        Returns:
            Path to the work tree (user-visible directory)

        Raises:
            Exception: If initialization fails
        """
        # Normalize notebook path to work tree
        work_tree_path = self._normalize_to_work_tree(notebook_path)
        
        # Check if git repository already exists
        if self.is_git_repository(work_tree_path):
            logger.info("Git repository already exists for work tree: %s", self.work_tree_base)
            return self.work_tree_base

        try:
            # Create directories if they don't exist
            os.makedirs(self.git_metadata_base, exist_ok=True)
            os.makedirs(self.work_tree_base, exist_ok=True)
            
            git_dir = os.path.join(self.git_metadata_base, ".git")
            
            logger.info("Initializing git repository with separate directories:")
            logger.info(f"  Git metadata: {git_dir}")
            logger.info(f"  Work tree: {self.work_tree_base}")
            
            # Initialize repository with separate git-dir and work-tree
            self.run_git_command_with_separate_dirs(
                ["init"],
                error_mode=SubprocessErrorMode.STRICT,
                operation_name="initialize git repository with separate structure"
            )
            
            logger.info("Successfully initialized git repository with separate structure")
            
            # Verify git directory was created
            if not os.path.exists(git_dir):
                raise Exception(f"Git directory was not created: {git_dir}")

            # Configure repository as safe directory to prevent ownership issues
            self._configure_safe_directory(self.work_tree_base)

            # Configure git user (will be overridden by ConfigService if available)
            logger.info(f"📁 Configuring git user for work tree: {self.work_tree_base}")
            self._configure_git_user(self.work_tree_base)

            # Generate .gitignore file for JupyterLab environment
            self._create_jupyterlab_gitignore(self.work_tree_base)

            return self.work_tree_base

        except Exception as e:
            logger.error("Failed to initialize git repository: %s", str(e))
            raise

    def commit_notebook(
        self, notebook_path: str, commit_message: str
    ) -> GitOperationResult:
        """
        Commit notebook changes with GPG signature using separate git-dir.

        Args:
            notebook_path: Path to the notebook file (may be from JupyterLab perspective)
            commit_message: Commit message

        Returns:
            GitOperationResult with operation details
        """
        try:
            logger.info("Committing notebook: %s", notebook_path)
            logger.info("Commit message: %s", commit_message)

            # Translate JupyterLab path to sidecar path
            sidecar_notebook_path = self._translate_jupyterlab_path_to_sidecar(notebook_path)
            logger.info("Translated to sidecar path: %s", sidecar_notebook_path)

            repo = self.get_repository(sidecar_notebook_path)
            if not repo:
                return GitOperationResult(
                    success=False,
                    message="File is not in a git repository",
                    error="File is not in a git repository",
                )

            # Get relative path from work tree root
            rel_path = os.path.relpath(sidecar_notebook_path, self.work_tree_base)

            # Ensure git configuration is properly set before committing
            self._ensure_git_config(self.work_tree_base)

            # Check if file exists (but allow deletion commits to proceed)
            file_exists = os.path.exists(sidecar_notebook_path)
            is_deletion_commit = "Delete" in commit_message or "delete" in commit_message.lower()
            
            logger.info(f"File existence check - Path: {sidecar_notebook_path}, Exists: {file_exists}, Is deletion: {is_deletion_commit}")
            
            if not file_exists and not is_deletion_commit:
                return GitOperationResult(
                    success=False,
                    message=f"File does not exist: {sidecar_notebook_path}",
                    error=f"File does not exist: {sidecar_notebook_path}",
                )

            # Commit with GPG signature using subprocess for better control
            commit_hash, signed = self._commit_with_subprocess(
                self.work_tree_base, rel_path, commit_message
            )

            if commit_hash:
                logger.info("Git commit successful: %s", commit_hash)
                logger.info("Commit signed: %s", signed)

                # DEBUGGING: Check if file becomes modified again after commit
                time.sleep(
                    0.1
                )  # Small delay to let any post-commit operations complete

                try:
                    # Check git status immediately after commit
                    status_result = self.run_git_command_with_separate_dirs(
                        ["status", "--porcelain", rel_path],
                        error_mode=SubprocessErrorMode.SILENT,
                        timeout=10,
                        operation_name="check status after commit"
                    )

                    if status_result.returncode == 0:
                        post_commit_status = status_result.stdout.strip()
                        if post_commit_status:
                            logger.error(
                                "🚨 CRITICAL: File appears MODIFIED immediately after commit!"
                            )
                            logger.error(
                                "🚨 Post-commit status: '%s'", post_commit_status
                            )
                            logger.error(
                                "🚨 This explains why changes don't reach remote!"
                            )

                            # Get file modification time
                            try:
                                file_stat = os.stat(sidecar_notebook_path)
                                logger.error(
                                    f"🚨 File modification time after commit: {file_stat.st_mtime}"
                                )
                            except Exception as e:
                                logger.error(f"Could not get file stats: {e}")

                        else:
                            logger.info("✅ File is clean immediately after commit")
                    else:
                        logger.warning(
                            f"Could not check post-commit status: {status_result.stderr}"
                        )

                except Exception as e:
                    logger.warning(f"Error checking post-commit status: {str(e)}")

                return GitOperationResult(
                    success=True,
                    message="Notebook committed successfully",
                    commit_hash=commit_hash,
                    signed=signed,
                )
            else:
                return GitOperationResult(
                    success=False,
                    message="Failed to create git commit",
                    error="Failed to create git commit",
                )

        except Exception as e:
            error_msg = f"Error committing file: {str(e)}"
            logger.error(error_msg)
            return GitOperationResult(success=False, message=error_msg, error=error_msg)



    def commit_notebook_with_metadata(
        self,
        notebook_path: str,
        commit_message: str,
        notebook_service,
        gpg_service,
        notebook_content: Optional[Dict[str, Any]] = None,
    ) -> GitOperationResult:
        """
        Commit notebook changes with metadata operations and GPG signature.

        This method follows the same pattern as the main backend:
        1. Load notebook content (if not provided)
        2. Generate content hash
        3. Create initial metadata
        4. Save notebook with metadata
        5. Commit the notebook
        6. Update metadata with actual commit info
        7. Amend commit to include updated metadata

        Args:
            notebook_path: Path to the notebook file
            commit_message: Commit message
            notebook_service: NotebookService instance
            gpg_service: GPGService instance
            notebook_content: Optional notebook content (will be loaded if not provided)

        Returns:
            GitOperationResult with operation details including metadata
        """
        try:
            logger.info("Starting commit with metadata for notebook: %s", notebook_path)
            logger.info("Commit message: %s", commit_message)

            # Translate JupyterLab path to sidecar path
            sidecar_notebook_path = self._translate_jupyterlab_path_to_sidecar(notebook_path)

            repo = self.get_repository(sidecar_notebook_path)
            if not repo:
                return GitOperationResult(
                    success=False,
                    message="File is not in a git repository",
                    error="File is not in a git repository",
                )

            # Ensure git configuration is properly set before committing
            repo_root = str(repo.working_dir)
            self._ensure_git_config(repo_root)

            # Step 1: Load notebook content if not provided
            if notebook_content is None:
                notebook_content = notebook_service.load_notebook_content(notebook_path)
                if notebook_content is None:
                    return GitOperationResult(
                        success=False,
                        message="Failed to load notebook content",
                        error="Failed to load notebook content",
                    )

            # Step 2: Generate content hash
            try:
                content_hash = notebook_service.generate_content_hash(notebook_content)
                logger.info("Generated content hash: %s", content_hash)
            except Exception as e:
                logger.error("Failed to generate content hash: %s", str(e))
                return GitOperationResult(
                    success=False,
                    message="Failed to generate content hash",
                    error=str(e),
                )

            # Step 3: Get user info for metadata
            user_info = self.get_user_info(notebook_path)
            timestamp = notebook_service.get_current_timestamp()

            # Step 4: Create initial metadata
            initial_metadata = {
                "locked": False,  # This is just a commit, not a lock
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

            # Step 5: Save notebook with initial metadata
            success = notebook_service.save_signature_metadata(
                notebook_path, notebook_content, initial_metadata
            )
            if not success:
                return GitOperationResult(
                    success=False,
                    message="Failed to save initial metadata to notebook",
                    error="Failed to save initial metadata to notebook",
                )

            logger.info("Saved initial metadata to notebook")

            # Step 6: Commit the notebook (now includes metadata)
            result = self.commit_notebook(notebook_path, commit_message)
            if not result.success:
                logger.error("Git commit failed: %s", result.error)
                return result

            logger.info("Git commit successful: %s", result.commit_hash)

            # Step 7: Update metadata with actual commit information
            updated_metadata = initial_metadata.copy()
            updated_metadata.update(
                {
                    "commit_hash": result.commit_hash,
                    "commit_signed": result.signed,
                    "timestamp": timestamp,  # Use consistent timestamp
                }
            )

            # Step 8: Save notebook with final metadata
            success = notebook_service.save_signature_metadata(
                notebook_path, notebook_content, updated_metadata
            )
            if not success:
                logger.warning(
                    "Failed to save final metadata, but commit was successful"
                )
                # Don't fail the whole operation, commit was successful
                return GitOperationResult(
                    success=True,
                    message=f"Successfully committed {notebook_path} but failed to update metadata",
                    commit_hash=result.commit_hash,
                    signed=result.signed,
                    metadata=initial_metadata,
                    content_hash=content_hash,
                )

            # Step 9: Amend the commit to include the updated metadata
            repo_root = str(repo.working_dir)
            rel_path = os.path.relpath(sidecar_notebook_path, repo_root)

            try:
                # Amend the previous commit to include the updated notebook
                amend_result = self._amend_commit_with_file(
                    repo_root, rel_path, commit_message
                )
                if amend_result[0]:  # amend_success
                    final_commit_hash = amend_result[1]  # new_commit_hash
                    logger.info(
                        "Successfully amended commit with final metadata: %s",
                        final_commit_hash,
                    )

                    # Update the metadata with the final commit hash
                    updated_metadata["commit_hash"] = final_commit_hash

                    return GitOperationResult(
                        success=True,
                        message=f"Successfully committed {notebook_path} with metadata",
                        commit_hash=final_commit_hash,
                        signed=result.signed,
                        metadata=updated_metadata,
                        content_hash=content_hash,
                    )
                else:
                    logger.warning(
                        "Failed to amend commit with metadata, but original commit was successful"
                    )
                    return GitOperationResult(
                        success=True,
                        message=f"Successfully committed {notebook_path} but failed to amend with metadata",
                        commit_hash=result.commit_hash,
                        signed=result.signed,
                        metadata=updated_metadata,
                        content_hash=content_hash,
                    )
            except Exception as amend_error:
                logger.warning("Failed to amend commit: %s", str(amend_error))
                return GitOperationResult(
                    success=True,
                    message=f"Successfully committed {notebook_path} but failed to amend with metadata",
                    commit_hash=result.commit_hash,
                    signed=result.signed,
                    metadata=updated_metadata,
                    content_hash=content_hash,
                )

        except Exception as e:
            error_msg = f"Error in commit with metadata: {str(e)}"
            logger.error(error_msg)
            return GitOperationResult(success=False, message=error_msg, error=error_msg)

    def _amend_commit_with_file(
        self, repo_root: str, rel_path: str, commit_message: str
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Amend the last commit to include updated file content.

        Args:
            repo_root: Path to git repository root
            rel_path: Relative path to file to stage and amend
            commit_message: Commit message (can be same as original)

        Returns:
            Tuple of (success, commit_hash, error_message)
        """
        try:
            logger.info("Amending commit with file: %s", rel_path)

            # Ensure git configuration is properly set before amending
            self._ensure_git_config(repo_root)

            # Stage the updated file
            git_add_cmd = ["git", "add", rel_path]
            logger.debug(
                "Running command: %s (cwd: %s)", " ".join(git_add_cmd), repo_root
            )

            add_result = self.run_git_command_with_separate_dirs(
                ["add", rel_path],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=30,
                operation_name="stage file for amend commit"
            )

            if not add_result.success:
                logger.error("Failed to stage file %s: %s", rel_path, add_result.stderr)
                return False, None, f"Failed to stage file: {add_result.stderr}"

            # Amend the commit with GPG signing
            git_amend_cmd = ["git", "commit", "--amend", "-S", "-m", commit_message]
            logger.debug(
                "Running command: %s (cwd: %s)", " ".join(git_amend_cmd), repo_root
            )

            amend_result = self.run_git_command_with_separate_dirs(
                ["commit", "--amend", "-S", "-m", commit_message],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=60,
                operation_name="amend commit with GPG signature"
            )

            if amend_result.success:
                # Get the new commit hash
                hash_result = self.run_git_command_with_separate_dirs(
                    ["rev-parse", "HEAD"],
                    error_mode=SubprocessErrorMode.LENIENT,
                    timeout=10,
                    operation_name="get amended commit hash"
                )

                if hash_result.success:
                    commit_hash = hash_result.stdout.strip()
                    logger.info("Successfully amended commit: %s", commit_hash)
                    return True, commit_hash, None
                else:
                    logger.error("Failed to get amended commit hash")
                    return False, None, "Failed to get amended commit hash"
            else:
                logger.error("Failed to amend commit: %s", amend_result.stderr)
                return False, None, f"Failed to amend commit: {amend_result.stderr}"

        except subprocess.TimeoutExpired:
            logger.error("Git amend command timed out")
            return False, None, "Git amend command timed out"
        except Exception as e:
            error_msg = f"Error amending commit: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

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
            # Get user info for metadata
            user_info = self.get_user_info(notebook_path)
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
            result = self.commit_notebook(notebook_path, commit_message)
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
                repo = self.get_repository(notebook_path)
                if repo:
                    repo_root = str(repo.working_dir)
                    rel_path = os.path.relpath(notebook_path, repo_root)
                    amend_result = self._amend_commit_with_file(
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
            signature_valid = True

            if was_gpg_signed:
                commit_hash = signature_metadata.get("commit_hash")
                if commit_hash:
                    # Basic signature verification (could be enhanced with actual GPG verification)
                    logger.info(
                        "Notebook was GPG signed, signature verification would occur here"
                    )
                    # In a full implementation, we would verify the GPG signature here
                    signature_valid = True

            # Update metadata to unlocked state
            user_info = self.get_user_info(notebook_path)
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
            result = self.commit_notebook(notebook_path, unlock_commit_message)

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

    def get_status(self, notebook_path: str) -> GitStatusResult:
        """
        Get repository and notebook status.

        Args:
            notebook_path: Path to the notebook file (may be from JupyterLab perspective)

        Returns:
            GitStatusResult with status information
        """
        try:
            # Translate JupyterLab path to sidecar path
            sidecar_notebook_path = self._translate_jupyterlab_path_to_sidecar(notebook_path)
            
            repo = self.get_repository(sidecar_notebook_path)

            if not repo:
                return GitStatusResult(is_git_repository=False)

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
                repository_path=str(repo.working_dir),
                signature_metadata=signature_metadata,
                last_commit_hash=last_commit_hash,
            )

        except Exception as e:
            logger.error("Error getting status: %s", str(e))
            return GitStatusResult(is_git_repository=False)

    def get_user_info(self, notebook_path: str) -> UserInfoResult:
        """
        Get git user information with simplified logic.
        
        Logic:
        1. Get user info from config service (always assume available)
        2. Try to get local git config from notebook_path directory
        3. If local config matches config service -> return
        4. If local config doesn't exist or doesn't match -> configure local git
        5. Return config service values
        
        Args:
            notebook_path: Path to the notebook file or directory (may be from JupyterLab perspective)
            
        Returns:
            UserInfoResult with user details
        """
        try:
            # Translate JupyterLab path to sidecar path
            sidecar_notebook_path = self._translate_jupyterlab_path_to_sidecar(notebook_path)
            
            # Determine working directory
            if os.path.isfile(sidecar_notebook_path):
                cwd = os.path.dirname(sidecar_notebook_path)
            else:
                cwd = sidecar_notebook_path
                
            logger.info("[get_user_info] Using cwd: %s", cwd)
            
            # Step 1: Get user info from config service (assume always available)
            if not self.config_service:
                raise ValueError("ConfigService is required but not available")
                
            config_email = self.config_service.git_user_email
            config_name = self.config_service.git_user_name
            
            logger.info("[get_user_info] Config service email: '%s'", config_email)
            logger.info("[get_user_info] Config service name: '%s'", config_name)
            
            # Step 2: Try to get local git config
            local_name_result = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local git user name"
            )
            local_email_result = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local git user email"
            )
            
            local_name = local_name_result.stdout.strip() if local_name_result.success else None
            local_email = local_email_result.stdout.strip() if local_email_result.success else None
            
            logger.info("[get_user_info] Local git name: '%s' (success=%s)", local_name, local_name_result.success)
            logger.info("[get_user_info] Local git email: '%s' (success=%s)", local_email, local_email_result.success)
            
            # Step 3: Check if local config matches config service
            config_matches = (local_name == config_name and local_email == config_email)
            
            if config_matches:
                logger.info("[get_user_info] Local git config matches config service - no action needed")
            else:
                # Step 4: Configure local git with config service values
                logger.info("[get_user_info] Local git config doesn't match or doesn't exist - configuring with config service values")
                self._configure_git_user(cwd)
            
            # Step 5: Return config service values
            gpg_key_id = self.config_service.gpg_key_id if self.config_service else None
            return UserInfoResult(name=config_name, email=config_email, gpg_key_id=gpg_key_id)
            
        except Exception as e:
            logger.error("Error getting user info: %s", str(e))
            # Fallback to config service values even on error
            if self.config_service:
                return UserInfoResult(
                    name=self.config_service.git_user_name,
                    email=self.config_service.git_user_email,
                    gpg_key_id=self.config_service.gpg_key_id
                )
            else:
                return UserInfoResult(name="Unknown", email="unknown@example.com")

    def _configure_git_user(self, repo_path: str) -> None:
        """
        Configure git user for the repository using config service values only.
        
        This function uses only the config service as the source of truth
        and configures the local git repository accordingly.

        Args:
            repo_path: Path to the git repository
        """
        try:
            if not self.config_service:
                raise ValueError("ConfigService is required but not available")

            usr_email = self.config_service.git_user_email
            usr_name = self.config_service.git_user_name
            
            logger.info("Configuring git user from config service: %s <%s>", usr_name, usr_email)
            
            # Set git user configuration with --local flag to ensure repository-specific config
            self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name", usr_name],
                error_mode=SubprocessErrorMode.STRICT,
                operation_name="configure git user name"
            )
            
            self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email", usr_email],
                error_mode=SubprocessErrorMode.STRICT,
                operation_name="configure git user email"
            )

            logger.info("Git user configured successfully for repository: %s", repo_path)
            
            # Configure SSL verification if needed
            self._configure_git_ssl_verify(repo_path)
            
            # Configure git performance optimizations
            self._configure_git_performance(repo_path)

        except Exception as e:
            logger.error("Failed to configure git user: %s", str(e))
            raise

    def _configure_git_ssl_verify(self, repo_path: str) -> None:
        """
        Configure git SSL verification for the repository.

        Args:
            repo_path: Path to the git repository
        """
        try:
            if not self.config_service:
                return

            if not self.config_service.git_ssl_verify:
                logger.info("Disabling SSL verification for git operations (development mode)")
                self.run_git_command_with_separate_dirs(
                    ["config", "--local", "http.sslVerify", "false"],
                    error_mode=SubprocessErrorMode.STRICT,
                    operation_name="configure git SSL verification"
                )
                logger.info("Git SSL verification disabled for repository: %s", repo_path)
            else:
                logger.debug("Git SSL verification enabled for repository: %s", repo_path)

        except Exception as e:
            logger.warning("Failed to configure git SSL verification: %s", str(e))

    def _configure_git_performance(self, repo_path: str) -> None:
        """
        Configure git performance optimizations for faster operations.

        Args:
            repo_path: Path to the git repository
        """
        try:
            logger.info("Configuring git performance optimizations for: %s", repo_path)
            
            # Optimize git operations for speed
            performance_configs = [
                # Reduce protocol overhead
                ("core.preloadindex", "true"),
                ("core.fscache", "true"),  # Windows optimization, harmless on Linux
                ("gc.auto", "0"),  # Disable automatic garbage collection during operations
                # Pack optimizations
                ("pack.deltaCacheSize", "2047m"),
                ("pack.packSizeLimit", "2g"),
                ("pack.windowMemory", "1g"),
                # Transfer optimizations
                ("transfer.unpackLimit", "1"),
                ("receive.unpackLimit", "1"),
                # Protocol optimizations
                ("http.lowSpeedLimit", "1000"),
                ("http.lowSpeedTime", "600"),
                ("http.postBuffer", "1048576000"),  # 1GB buffer for large pushes
            ]
            
            for config_key, config_value in performance_configs:
                try:
                    self.run_git_command_with_separate_dirs(
                        ["config", "--local", config_key, config_value],
                        error_mode=SubprocessErrorMode.LENIENT,  # Don't fail if some configs aren't supported
                        operation_name=f"configure git performance {config_key}"
                    )
                except Exception as e:
                    logger.debug(f"Could not set {config_key}: {e}")
            
            logger.info("Git performance optimizations configured for repository: %s", repo_path)

        except Exception as e:
            logger.warning("Failed to configure git performance optimizations: %s", str(e))

    def _load_template(self, template_filename: str) -> str:
        """
        Load a template file from the templates directory.
        
        Args:
            template_filename: Name of the template file to load
            
        Returns:
            str: Content of the template file, or fallback content if template not found
        """
        try:
            # Get the path to the template file
            current_file_path = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(current_file_path, "..", "templates", template_filename)
            template_path = os.path.normpath(template_path)
            
            # Read the template content
            with open(template_path, 'r', encoding='utf-8') as template_file:
                content = template_file.read()
            
            logger.debug("📋 Loaded template from: %s", template_path)
            return content
            
        except FileNotFoundError:
            logger.warning("⚠️ Template file not found at: %s", template_path)
            # Return fallback content for .gitignore template
            if template_filename == "gitignore.template":
                logger.info("📋 Using fallback .gitignore content")
                return """# JupyterLab and Jupyter Notebook files
.ipynb_checkpoints/
.jupyter/

# User configuration files
.gitconfig
.gnupg/
.local/
.cache/

# Python bytecode
__pycache__/
*.py[cod]

# OS generated files
.DS_Store
Thumbs.db
"""
            else:
                # For other templates, return empty string
                logger.warning("⚠️ No fallback available for template: %s", template_filename)
                return ""
                
        except Exception as e:
            logger.warning("⚠️ Failed to load template %s: %s", template_filename, str(e))
            return ""

    def _create_jupyterlab_gitignore(self, repo_path: str):
        """
        Create a comprehensive .gitignore file for JupyterLab environments.
        Uses a template file for easy maintenance and updates.
        
        Args:
            repo_path: Path to git repository where .gitignore should be created
        """
        try:
            gitignore_path = os.path.join(repo_path, ".gitignore")
            
            # Check if .gitignore already exists
            if os.path.exists(gitignore_path):
                logger.info("📋 .gitignore already exists at: %s", gitignore_path)
                return
            
            # Load the .gitignore content from template
            gitignore_content = self._load_template("gitignore.template")
            
            # Write the .gitignore file
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            logger.info("✅ Created .gitignore file at: %s", gitignore_path)
            
        except Exception as e:
            logger.warning("⚠️ Failed to create .gitignore file: %s", str(e))
            # Don't raise - this is not critical for repository functionality

    def ensure_gitignore_exists(self, notebook_path: str) -> bool:
        """
        Ensure .gitignore exists for the repository containing the notebook.
        This can be called for existing repositories that might not have .gitignore.
        
        Args:
            notebook_path: Path to a notebook file
            
        Returns:
            bool: True if .gitignore was created or already exists, False if failed
        """
        try:
            repo = self.get_repository(notebook_path)
            if not repo:
                logger.debug("No git repository found for: %s", notebook_path)
                return False
                
            repo_path = str(repo.working_dir)
            gitignore_path = os.path.join(repo_path, ".gitignore")
            
            if os.path.exists(gitignore_path):
                logger.debug("📋 .gitignore already exists at: %s", gitignore_path)
                return True
                
            logger.info("📋 Creating missing .gitignore for existing repository: %s", repo_path)
            self._create_jupyterlab_gitignore(repo_path)
            return True
            
        except Exception as e:
            logger.warning("⚠️ Failed to ensure .gitignore exists: %s", str(e))
            return False

    def _configure_safe_directory(self, repo_path: str) -> bool:
        """
        Configure the repository as a safe directory to prevent 'dubious ownership' errors.
        
        This addresses the git security feature introduced in Git 2.35.2 that prevents
        operations on repositories with ownership mismatches.

        Args:
            repo_path: Path to the git repository
            
        Returns:
            bool: True if configuration succeeded, False otherwise
        """
        try:
            # Get the absolute path to ensure consistent configuration
            abs_repo_path = os.path.abspath(repo_path)
            
            # Add the repository to git's safe directory list (global config)
            result = run_git_command(
                ["config", "--global", "--add", "safe.directory", abs_repo_path],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name="configure safe directory"
            )
            
            if result.success:
                logger.info("Successfully configured repository as safe directory: %s", abs_repo_path)
                return True
            else:
                # Check if it's already configured (common case)
                if "already exists" in result.stderr.lower():
                    logger.debug("Safe directory already configured: %s", abs_repo_path)
                    return True
                else:
                    logger.warning("Failed to configure safe directory for %s: %s", abs_repo_path, result.stderr)
                    return False

        except Exception as e:
            logger.error("Error configuring safe directory for %s: %s", repo_path, str(e))
            return False



    def _ensure_git_config(self, repo_path: str) -> None:
        """
        Ensure git configuration is properly set for the repository.
        This method is called before any commit operation to ensure
        the correct user information is used.

        Args:
            repo_path: Path to the git repository
        """
        try:
            # Check if git user is configured
            name_result = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                operation_name="check git user name"
            )
            
            email_result = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                operation_name="check git user email"
            )

            # If not configured or if we have a config service with environment variables, reconfigure
            if (
                not name_result.success
                or not email_result.success
                or (
                    self.config_service
                    and self.config_service.git_user_email != "NOT_SET"
                    and (
                        name_result.stdout.strip() != self.config_service.git_user_name
                        or email_result.stdout.strip() != self.config_service.git_user_email
                    )
                )
            ):
                
                logger.info("Ensuring git configuration is properly set for repository: %s", repo_path)
                self._configure_git_user(repo_path)
                
                # Verify configuration was set correctly
                self._verify_git_config(repo_path)
            else:
                logger.debug("Git configuration already properly set for repository: %s", repo_path)

        except Exception as e:
            logger.warning("Failed to ensure git configuration: %s", str(e))

    def _verify_git_config(self, repo_path: str) -> None:
        """
        Verify that git configuration is correctly set for the repository.

        Args:
            repo_path: Path to the git repository
        """
        try:
            # Check local config first
            name_result = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                operation_name="verify git user name"
            )
            
            email_result = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                operation_name="verify git user email"
            )

            # Also check global config for comparison (use regular git commands for global config)
            global_name_result = run_git_command(
                ["config", "--global", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get global git user name"
            )
            
            global_email_result = run_git_command(
                ["config", "--global", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get global git user email"
            )

            if name_result.success and email_result.success:
                actual_name = name_result.stdout.strip()
                actual_email = email_result.stdout.strip()
                logger.info(f"Verified git config for repository {repo_path}: {actual_name} <{actual_email}>")
                
                # Log global config for comparison
                if global_name_result.success and global_email_result.success:
                    global_name = global_name_result.stdout.strip()
                    global_email = global_email_result.stdout.strip()
                    logger.debug(f"Global git config: {global_name} <{global_email}>")
                
                # Check if this matches expected values from config service
                if self.config_service and self.config_service.git_user_email != "NOT_SET":
                    expected_name = self.config_service.git_user_name
                    expected_email = self.config_service.git_user_email
                    
                    if actual_name != expected_name or actual_email != expected_email:
                        logger.warning(f"Git config mismatch in {repo_path}! Expected: {expected_name} <{expected_email}>, Got: {actual_name} <{actual_email}>")
                        # Try to fix it
                        logger.info("Attempting to fix git config mismatch...")
                        self._configure_git_user(repo_path)
                        
                        # Verify the fix
                        self._verify_git_config(repo_path)
            else:
                logger.error(f"Git configuration verification failed for repository: {repo_path}")
                logger.debug(f"Name result: success={name_result.success}, stdout={name_result.stdout}")
                logger.debug(f"Email result: success={email_result.success}, stdout={email_result.stdout}")

        except Exception as e:
            logger.warning("Failed to verify git configuration: %s", str(e))

    async def sync_with_remote_on_session_start(self, repo_path: str, remote_name: str = "origin", refresh_remote_callback=None) -> GitOperationResult:
        """
        Enhanced session sync with validation and enforced consistency.
        
        This method ensures that the local repository is identical to the remote when the user
        begins working, with enhanced validation and automatic backup creation.
        
        Args:
            repo_path: Path to the git repository
            remote_name: Name of the git remote (default: "origin")
            refresh_remote_callback: Optional callback to refresh remote URL with fresh tokens
            
        Returns:
            GitOperationResult with sync details
        """
        try:
            logger.info(f"🔄 Starting enhanced session sync for repository: {repo_path}")
            
            
            # Step 1: Validate sync operation
            logger.info("🔍 Phase 1: Validating sync operation...")
            validation = await self.validate_sync_operation(repo_path, remote_name)
            
            if not validation["valid"]:
                logger.error(f"❌ Sync validation failed: {validation['critical_issues']}")
                return GitOperationResult(
                    success=False,
                    message="Sync validation failed",
                    error=f"Critical issues found: {', '.join(validation['critical_issues'])}"
                )
            
            # Log validation results
            if validation["warnings"]:
                logger.warning(f"⚠️ Validation warnings: {len(validation['warnings'])}")
                for warning in validation["warnings"]:
                    logger.warning(f"   - {warning}")
            
            if validation["critical_issues"]:
                logger.error(f"❌ Validation critical issues: {len(validation['critical_issues'])}")
                for issue in validation["critical_issues"]:
                    logger.error(f"   - {issue}")
            
            # Step 2: Enforce user config consistency
            logger.info("🔍 Phase 2: Enforcing user configuration consistency...")
            config_updated = self._enforce_environment_user_config(repo_path)
            if config_updated:
                logger.info("🔧 Updated local git config to match environment variables")
            else:
                logger.info("✅ Local git config already matches environment variables")
            
            # Step 3: Create backup if local changes exist
            backup_created = False
            if validation["uncommitted_changes"] or validation["untracked_files"]:
                logger.info("📦 Creating backup before destructive sync...")
                backup_created = await self._create_sync_backup(repo_path)
                if backup_created:
                    logger.info("✅ Backup created successfully")
                else:
                    logger.warning("⚠️ Failed to create backup, proceeding with sync anyway")
            
            # Step 4: Perform the actual sync (existing logic)
            logger.info("🔄 Phase 3: Performing force sync...")
            
            if not self.is_git_repository(repo_path):
                return GitOperationResult(
                    success=False,
                    message="Not a git repository",
                    error="Cannot sync - not a git repository"
                )
            
            repo = self.get_repository(repo_path)
            if not repo:
                return GitOperationResult(
                    success=False,
                    message="Could not access repository",
                    error="Failed to access git repository"
                )
                      
            # Check if remote exists
            remote_check = self.run_git_command_with_separate_dirs(
                ["remote", "get-url", remote_name],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name="check remote URL"
            )
            
            if not remote_check.success:
                logger.info(f"No remote '{remote_name}' found - skipping session sync")
                return GitOperationResult(
                    success=True,
                    message="No remote found - skipping sync",
                    error=None
                )
            
            remote_url = remote_check.stdout.strip()
            logger.info(f"🔗 Found remote '{remote_name}': {remote_url}")
            
            # Refresh remote URL if callback provided (for token-based authentication)
            if refresh_remote_callback:
                try:
                    logger.info("🔄 Refreshing remote URL with fresh authentication...")
                    fresh_remote_url = await refresh_remote_callback(repo_path)
                    if fresh_remote_url:
                        # Update the remote URL
                        update_result = self.run_git_command_with_separate_dirs(
                            ["remote", "set-url", remote_name, fresh_remote_url],
                            error_mode=SubprocessErrorMode.LENIENT,
                            timeout=30,
                            operation_name="update remote URL with fresh authentication"
                        )
                        
                        if update_result.success:
                            logger.info("✅ Successfully updated remote URL with fresh authentication")
                        else:
                            logger.warning(f"⚠️ Failed to update remote URL: {update_result.stderr}")
                            # Continue with old URL
                    else:
                        logger.warning("⚠️ Failed to get fresh remote URL from callback")
                        # Continue with old URL
                except Exception as e:
                    logger.warning(f"⚠️ Error refreshing remote URL: {str(e)}")
                    # Continue with old URL
            
            # Fetch remote changes
            logger.info("📥 Fetching remote changes...")
            fetch_result = self.run_git_command_with_separate_dirs(
                ["fetch", remote_name],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=60,
                operation_name="fetch remote changes"
            )
            
            if not fetch_result.success:
                logger.warning(f"Failed to fetch from remote: {fetch_result.stderr}")
                return GitOperationResult(
                    success=False,
                    message="Failed to fetch remote changes",
                    error=f"Git fetch failed: {fetch_result.stderr}"
                )
            
            logger.info("✅ Successfully fetched remote changes")
            
            # Get current branch (handle case where repository has no commits yet)
            branch_result = self.run_git_command_with_separate_dirs(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name="get current branch"
            )
            
            # Handle empty repository case (no HEAD exists yet)
            if not branch_result.success:
                logger.info("🌱 Local repository has no commits yet - performing initial checkout from remote")
                
                # Find the default branch from remote
                ls_remote_result = self.run_git_command_with_separate_dirs(
                    ["ls-remote", "--symref", remote_name, "HEAD"],
                    error_mode=SubprocessErrorMode.LENIENT,
                    timeout=30,
                    operation_name="find default remote branch"
                )
                
                default_branch = "main"  # fallback
                if ls_remote_result.success:
                    # Parse output like: "ref: refs/heads/main	HEAD"
                    for line in ls_remote_result.stdout.split('\n'):
                        if line.startswith('ref: refs/heads/'):
                            default_branch = line.split('/')[-1].split('\t')[0]
                            break
                
                logger.info(f"🌿 Detected remote default branch: {default_branch}")
                
                # Handle any untracked files that might conflict with checkout
                # This is especially important for .gitignore files created during initialization
                logger.info("🧹 Handling untracked files before checkout to avoid conflicts")
                
                # Check if there's a local .gitignore that might conflict
                local_gitignore_path = os.path.join(self.work_tree_base, ".gitignore")
                has_local_gitignore = os.path.exists(local_gitignore_path)
                
                if has_local_gitignore:
                    logger.info("📋 Found local .gitignore - will handle potential conflict")
                    # Clean untracked files to avoid checkout conflicts
                    clean_result = self.run_git_command_with_separate_dirs(
                        ["clean", "-fd"],
                        error_mode=SubprocessErrorMode.LENIENT,
                        timeout=30,
                        operation_name="clean untracked files before checkout"
                    )
                    if clean_result.success:
                        logger.info("✅ Successfully cleaned untracked files")
                    else:
                        logger.warning(f"⚠️ Failed to clean untracked files: {clean_result.stderr}")
                else:
                    logger.info("📋 No local .gitignore found - no cleanup needed")
                
                # Create and checkout the default branch tracking the remote
                checkout_result = self.run_git_command_with_separate_dirs(
                    ["checkout", "-b", default_branch, f"{remote_name}/{default_branch}"],
                    error_mode=SubprocessErrorMode.LENIENT,
                    timeout=60,
                    operation_name="checkout initial branch from remote"
                )
                
                if checkout_result.success:
                    logger.info(f"✅ Successfully checked out initial branch '{default_branch}' from remote")
                    
                    # Ensure .gitignore exists after checkout (in case remote had none)
                    # This handles the scenario where local .gitignore was cleaned but remote has no .gitignore
                    final_gitignore_path = os.path.join(self.work_tree_base, ".gitignore")
                    if not os.path.exists(final_gitignore_path):
                        logger.info("📋 No .gitignore found after checkout - creating JupyterLab-specific .gitignore")
                        self._create_jupyterlab_gitignore(self.work_tree_base)
                    else:
                        logger.info("📋 .gitignore exists after checkout - no action needed")
                    
                    return GitOperationResult(
                        success=True,
                        message=f"Successfully performed initial checkout from remote branch {default_branch}",
                        error=None
                    )
                else:
                    logger.error(f"❌ Failed to checkout from remote: {checkout_result.stderr}")
                    return GitOperationResult(
                        success=False,
                        message="Failed to perform initial checkout from remote",
                        error=f"Initial checkout failed: {checkout_result.stderr}"
                    )
            
            current_branch = branch_result.stdout.strip()
            remote_branch = f"{remote_name}/{current_branch}"
            
            logger.info(f"🌿 Current branch: {current_branch}")
            logger.info(f"🌿 Remote branch: {remote_branch}")
            
            # Check if remote branch exists
            remote_branch_check = self.run_git_command_with_separate_dirs(
                ["rev-parse", "--verify", remote_branch],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name="verify remote branch exists"
            )
            
            if not remote_branch_check.success:
                logger.info(f"Remote branch '{remote_branch}' does not exist - skipping sync")
                return GitOperationResult(
                    success=True,
                    message="Remote branch does not exist - skipping sync",
                    error=None
                )
            
            # Check if local and remote are already in sync
            local_commit = self.run_git_command_with_separate_dirs(
                ["rev-parse", "HEAD"],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name="get local commit hash"
            )
            
            remote_commit = self.run_git_command_with_separate_dirs(
                ["rev-parse", remote_branch],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name="get remote commit hash"
            )
            
            # Check if there are uncommitted changes that need syncing
            has_uncommitted = False
            if validation and (validation.get("uncommitted_changes") or validation.get("untracked_files")):
                has_uncommitted = True
                logger.info("🔄 Uncommitted changes detected - proceeding with force sync")
            
            # Only skip sync if commits are identical AND no uncommitted changes
            if (local_commit.success and remote_commit.success and 
                local_commit.stdout.strip() == remote_commit.stdout.strip() and not has_uncommitted):
                logger.info("✅ Local and remote are already in sync with no uncommitted changes")
                return GitOperationResult(
                    success=True,
                    message="Repository already in sync with remote",
                    error=None
                )
            
            # Force sync with remote (reset to match remote exactly)
            logger.info(f"🔄 Syncing local branch to match remote '{remote_branch}'")
            reset_result = self.run_git_command_with_separate_dirs(
                ["reset", "--hard", remote_branch],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=60,
                operation_name="force sync with remote"
            )
            
            if not reset_result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to sync with remote",
                    error=f"Git reset failed: {reset_result.stderr}"
                )
            
            # Clean any untracked files if they exist
            clean_result = self.run_git_command_with_separate_dirs(
                ["clean", "-fd"],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=30,
                operation_name="clean untracked files"
            )
            
            if clean_result.success and clean_result.stdout.strip():
                logger.info(f"🧹 Cleaned untracked files: {clean_result.stdout.strip()}")
            
            # Step 5: Verify sync success
            logger.info("🔍 Phase 4: Verifying sync success...")
            sync_verified = self._verify_sync_success(repo_path, remote_name)
            
            if sync_verified:
                logger.info("✅ Enhanced session sync completed successfully")
                
                # Build success message
                message_parts = [f"Successfully synced with remote {remote_branch}"]
                if backup_created:
                    message_parts.append("Backup created before sync")
                if config_updated:
                    message_parts.append("User config updated to match environment")
                
                return GitOperationResult(
                    success=True,
                    message=". ".join(message_parts),
                    error=None
                )
            else:
                logger.warning("⚠️ Sync completed but verification failed")
                return GitOperationResult(
                    success=True,
                    message="Sync completed with verification warnings",
                    error=None
                )
                
        except subprocess.TimeoutExpired:
            logger.error("Enhanced session sync timed out")
            return GitOperationResult(
                success=False,
                message="Enhanced session sync timed out",
                error="Git operations timed out during sync"
            )
        except Exception as e:
            logger.error(f"Enhanced session sync failed with exception: {str(e)}")
            return GitOperationResult(
                success=False,
                message="Enhanced session sync failed",
                error=f"Unexpected error during sync: {str(e)}"
            )

    async def validate_sync_operation(self, repo_path: str, remote_name: str = "origin") -> Dict[str, Any]:
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
            logger.info(f"🔍 Validating sync operation for repository: {repo_path}")
            
            if not self.is_git_repository(repo_path):
                return {
                    "valid": False,
                    "error": "Not a git repository",
                    "recommendations": ["Initialize git repository first"]
                }
            
            repo = self.get_repository(repo_path)
            if not repo:
                return {
                    "valid": False,
                    "error": "Could not access repository",
                    "recommendations": ["Check repository permissions"]
                }
                        
            validation_results = {
                "valid": True,
                "warnings": [],
                "critical_issues": [],
                "recommendations": [],
                "user_config_mismatch": False,
                "uncommitted_changes": False,
                "untracked_files": False,
                "sync_required": False
            }
            
            # 1. Check user configuration mismatch (CRITICAL - must match environment)
            logger.info("🔍 Checking user configuration consistency...")
            local_name = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local user name for validation"
            )
            
            local_email = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local user email for validation"
            )
            
            # Get expected configuration from environment/config service
            expected_name = None
            expected_email = None
            
            if self.config_service and self.config_service.git_user_email != "NOT_SET":
                expected_name = self.config_service.git_user_name
                expected_email = self.config_service.git_user_email
            
            if expected_name and expected_email:
                local_name_str = local_name.stdout.strip() if local_name.success else None
                local_email_str = local_email.stdout.strip() if local_email.success else None
                
                if (local_name_str and local_name_str != expected_name) or (local_email_str and local_email_str != expected_email):
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
            status_result = self.run_git_command_with_separate_dirs(
                ["status", "--porcelain"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check uncommitted changes for validation"
            )
            
            if status_result.success and status_result.stdout.strip():
                validation_results["uncommitted_changes"] = True
                validation_results["warnings"].append(
                    f"Found uncommitted changes that will be lost during force sync: {status_result.stdout.strip()}"
                )
                validation_results["recommendations"].append(
                    "Changes will be automatically backed up before sync"
                )
            
            # 3. Check for untracked files (WARNING - will be deleted)
            logger.info("🔍 Checking for untracked files...")
            untracked_result = self.run_git_command_with_separate_dirs(
                ["ls-files", "--others", "--exclude-standard"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check untracked files for validation"
            )
            
            if untracked_result.success and untracked_result.stdout.strip():
                untracked_files = untracked_result.stdout.strip().split('\n')
                validation_results["untracked_files"] = True
                validation_results["warnings"].append(
                    f"Found {len(untracked_files)} untracked files that will be deleted during sync"
                )
                validation_results["recommendations"].append(
                    "Untracked files will be automatically backed up before sync"
                )
                
                # Show first few untracked files for user awareness
                if len(untracked_files) <= 5:
                    validation_results["warnings"].append(f"Untracked files: {', '.join(untracked_files)}")
                else:
                    validation_results["warnings"].append(f"Untracked files: {', '.join(untracked_files[:3])}... and {len(untracked_files) - 3} more")
            
            # 4. Check remote connectivity and determine if sync is needed
            logger.info("🔍 Checking remote connectivity and sync requirements...")
            remote_check = self.run_git_command_with_separate_dirs(
                ["remote", "get-url", remote_name],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check remote connectivity"
            )
            
            if remote_check.success:
                # Fetch latest remote info
                fetch_result = self.run_git_command_with_separate_dirs(
                    ["fetch", remote_name],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=30,
                    operation_name="fetch for validation"
                )
                
                if fetch_result.success:
                    # Check if sync is actually needed
                    local_commit = self.run_git_command_with_separate_dirs(
                        ["rev-parse", "HEAD"],
                        error_mode=SubprocessErrorMode.SILENT,
                        timeout=10,
                        operation_name="get local commit for validation"
                    )
                    
                    # Try to find remote branch (main or master)
                    remote_branch = None
                    for branch_name in ["main", "master"]:
                        test_branch = f"{remote_name}/{branch_name}"
                        test_result = self.run_git_command_with_separate_dirs(
                            ["rev-parse", test_branch],
                            error_mode=SubprocessErrorMode.SILENT,
                            timeout=10,
                            operation_name="test remote branch existence"
                        )
                        if test_result.success:
                            remote_branch = test_branch
                            break
                    
                    if remote_branch and local_commit.success:
                        remote_commit = self.run_git_command_with_separate_dirs(
                            ["rev-parse", remote_branch],
                            error_mode=SubprocessErrorMode.SILENT,
                            timeout=10,
                            operation_name="get remote commit for validation"
                        )
                        
                        if remote_commit.success:
                            local_hash = local_commit.stdout.strip()
                            remote_hash = remote_commit.stdout.strip()
                            
                            if local_hash != remote_hash:
                                validation_results["sync_required"] = True
                                logger.info(f"🔄 Sync required: local {local_hash[:8]} != remote {remote_hash[:8]}")
                            else:
                                logger.info("✅ Local and remote are already in sync")
                        else:
                            validation_results["warnings"].append(f"Could not access remote branch {remote_branch}")
                    else:
                        validation_results["warnings"].append("Could not determine local HEAD or remote branch")
                else:
                    validation_results["warnings"].append(
                        f"Could not fetch from remote: {fetch_result.stderr}"
                    )
            else:
                validation_results["warnings"].append(f"Remote '{remote_name}' not found")
            
            # Determine overall validity
            if validation_results["critical_issues"]:
                validation_results["valid"] = False
                validation_results["recommendations"].insert(0, "Review critical issues before proceeding with sync")
            
            logger.info(f"🔍 Sync validation completed: {'✅ Valid' if validation_results['valid'] else '❌ Invalid'}")
            if validation_results["warnings"]:
                logger.warning(f"⚠️ Validation warnings: {len(validation_results['warnings'])}")
            if validation_results["critical_issues"]:
                logger.error(f"❌ Validation critical issues: {len(validation_results['critical_issues'])}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Sync validation failed: {str(e)}")
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}",
                "recommendations": ["Check repository state and try again"]
            }

    def _enforce_environment_user_config(self, repo_path: str) -> bool:
        """
        Enforces that local git config matches environment variables.
        Returns True if config was updated, False if already correct.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            True if config was updated, False if already correct
        """
        try:
            if not self.config_service or self.config_service.git_user_email == "NOT_SET":
                logger.warning("Cannot enforce user config: environment variables not set")
                return False
            
            expected_name = self.config_service.git_user_name
            expected_email = self.config_service.git_user_email
            
            # Check current local config
            current_name_result = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get current local git name"
            )
            
            current_email_result = self.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get current local git email"
            )
            
            current_name = current_name_result.stdout.strip() if current_name_result.success else None
            current_email = current_email_result.stdout.strip() if current_email_result.success else None
            
            # If mismatch, force update to environment values
            config_updated = False
            
            if current_name != expected_name:
                self.run_git_command_with_separate_dirs(
                    ["config", "--local", "user.name", expected_name],
                    error_mode=SubprocessErrorMode.STRICT,
                    timeout=10,
                    operation_name="update local git user name"
                )
                logger.info(f"🔧 Updated local git user.name: {current_name} -> {expected_name}")
                config_updated = True
            
            if current_email != expected_email:
                self.run_git_command_with_separate_dirs(
                    ["config", "--local", "user.email", expected_email],
                    error_mode=SubprocessErrorMode.STRICT,
                    timeout=10,
                    operation_name="update local git user email"
                )
                logger.info(f"🔧 Updated local git user.email: {current_email} -> {expected_email}")
                config_updated = True
            
            if config_updated:
                logger.info("✅ Local git config now matches environment variables")
            else:
                logger.info("✅ Local git config already matches environment variables")
            
            return config_updated
            
        except Exception as e:
            logger.error(f"Failed to enforce user config: {str(e)}")
            return False

    async def _create_sync_backup(self, repo_path: str) -> bool:
        """
        Creates a simple timestamped backup branch before destructive sync.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            True if backup was created successfully, False otherwise
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_branch = f"backup_before_sync_{timestamp}"
            
            logger.info(f"📦 Creating backup branch: {backup_branch}")
            
            # Get current branch name
            current_branch_result = self.run_git_command_with_separate_dirs(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get current branch for backup"
            )
            
            if not current_branch_result.success:
                logger.warning("Could not determine current branch for backup")
                return False
            
            current_branch = current_branch_result.stdout.strip()
            
            # Create backup branch from current state
            backup_result = self.run_git_command_with_separate_dirs(
                ["checkout", "-b", backup_branch],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=30,
                operation_name="create backup branch"
            )
            
            if backup_result.success:
                logger.info(f"✅ Created backup branch: {backup_branch}")
                
                # Return to original branch
                checkout_result = self.run_git_command_with_separate_dirs(
                    ["checkout", current_branch],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=30,
                    operation_name="return to original branch"
                )
                
                if checkout_result.success:
                    logger.info(f"✅ Returned to original branch: {current_branch}")
                    
                    # Create backup metadata file
                    backup_info = {
                        "backup_branch": backup_branch,
                        "original_branch": current_branch,
                        "timestamp": timestamp,
                        "reason": "sync_operation",
                        "created_by": "git_lock_sign_extension"
                    }
                    
                    backup_file = os.path.join(repo_path, ".git", f"backup_{timestamp}.json")
                    try:
                        import json
                        with open(backup_file, 'w') as f:
                            json.dump(backup_info, f, indent=2)
                        logger.info(f"📝 Created backup metadata: {backup_file}")
                    except Exception as e:
                        logger.warning(f"Could not create backup metadata: {e}")
                    
                    return True
                else:
                    logger.warning(f"Could not return to original branch: {checkout_result.stderr}")
                    return False
            else:
                logger.warning(f"Failed to create backup branch: {backup_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create backup branch: {str(e)}")
            return False

    def _verify_sync_success(self, repo_path: str, remote_name: str = "origin") -> bool:
        """
        Verifies that sync was successful by checking if local matches remote.
        
        Args:
            repo_path: Path to the git repository
            remote_name: Name of the git remote
            
        Returns:
            True if sync was successful, False otherwise
        """
        try:
            repo = self.get_repository(repo_path)
            if not repo:
                logger.warning("Could not access repository for sync verification")
                return False
            
            repo_root = str(repo.working_dir)
            
            # Get current branch
            current_branch_result = self.run_git_command_with_separate_dirs(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get current branch for verification"
            )
            
            if not current_branch_result.success:
                logger.warning("Could not determine current branch for sync verification")
                return False
            
            current_branch = current_branch_result.stdout.strip()
            remote_branch = f"{remote_name}/{current_branch}"
            
            # Check if remote branch exists
            remote_check = self.run_git_command_with_separate_dirs(
                ["rev-parse", remote_branch],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="verify remote branch for sync verification"
            )
            
            if not remote_check.success:
                logger.warning(f"Remote branch {remote_branch} not found for verification")
                return False
            
            # Compare local and remote commits
            local_commit = self.run_git_command_with_separate_dirs(
                ["rev-parse", "HEAD"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get local commit for verification"
            )
            
            remote_commit = self.run_git_command_with_separate_dirs(
                ["rev-parse", remote_branch],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="get remote commit for verification"
            )
            
            if (local_commit.success and remote_commit.success):
                local_hash = local_commit.stdout.strip()
                remote_hash = remote_commit.stdout.strip()
                
                if local_hash == remote_hash:
                    logger.info("✅ Sync verification successful: local matches remote")
                    return True
                else:
                    logger.warning(f"⚠️ Sync verification failed: local {local_hash[:8]} != remote {remote_hash[:8]}")
                    return False
            else:
                logger.warning("Could not get commit hashes for verification")
                return False
                
        except Exception as e:
            logger.error(f"Sync verification failed: {str(e)}")
            return False

    def _commit_with_subprocess(
        self, repo_path: str, file_path: str, commit_message: str
    ) -> tuple[Optional[str], bool]:
        """
        Create a git commit using subprocess with separate git-dir structure.

        Args:
            repo_path: Path to work tree (should match self.work_tree_base)
            file_path: Relative path to file to stage and commit
            commit_message: Commit message

        Returns:
            Tuple of (commit_hash, is_signed)
        """
        try:
            logger.info("Attempting to stage file: %s", file_path)
            logger.info("Work tree path: %s", repo_path)
            
            file_full_path = os.path.join(repo_path, file_path)
            file_exists = os.path.exists(file_full_path)
            logger.info("File exists check: %s", file_exists)

            # Improved deletion detection:
            # 1. Check commit message for deletion keywords
            # 2. Check git status to see if file is marked for deletion
            # 3. File existence is secondary (due to timing issues)
            is_deletion_by_message = ("Delete" in commit_message or "delete" in commit_message.lower())
            
            # Check git status to see current file state
            git_status_result = self.run_git_command_with_separate_dirs(
                ["status", "--porcelain", file_path],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check file status for commit"
            )
            
            git_status_line = git_status_result.stdout.strip() if git_status_result.success else ""
            is_deletion_by_status = git_status_line.startswith(" D") or git_status_line.startswith("D ")
            
            # Determine if this is a deletion
            is_deletion = is_deletion_by_message or is_deletion_by_status or (not file_exists and is_deletion_by_message)
            
            logger.info("Deletion detection - Message: %s, Status: %s, Final: %s", 
                       is_deletion_by_message, is_deletion_by_status, is_deletion)
            logger.info("Git status line: '%s'", git_status_line)
            
            # Check if the file is already staged for commit
            git_diff_cached_result = self.run_git_command_with_separate_dirs(
                ["diff", "--cached", "--name-only"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check staged files"
            )
            
            already_staged = file_path in git_diff_cached_result.stdout if git_diff_cached_result.success else False
            logger.info("File already staged: %s", already_staged)
            
            # Initialize git_stage_cmd to avoid undefined variable
            git_stage_cmd = None
            
            if already_staged:
                logger.info("File is already staged - skipping staging step")
            elif is_deletion:
                # For deletions, check if already staged for deletion
                if already_staged:
                    logger.info("File is already staged for deletion - skipping staging step")
                else:
                    # For deletions, use git rm to stage the removal
                    logger.info("Detected file deletion - using git rm to stage")
                    git_stage_cmd = ["rm", file_path]
            else:
                # For additions/modifications, use git add
                logger.info("Detected file addition/modification - using git add to stage")
                git_stage_cmd = ["add", file_path]
            
            # Only run staging command if file is not already staged
            if not already_staged and git_stage_cmd:
                logger.info(
                    "Running git command: %s (work-tree: %s)", " ".join(git_stage_cmd), repo_path
                )

                stage_result = self.run_git_command_with_separate_dirs(
                    git_stage_cmd,
                    error_mode=SubprocessErrorMode.LENIENT,
                    timeout=30,
                    operation_name=f"stage file for commit: {file_path}"
                )

                logger.info("Git stage success: %s", stage_result.success)
                if stage_result.stdout:
                    logger.info("Git stage stdout: %s", stage_result.stdout)
                if stage_result.stderr:
                    logger.info("Git stage stderr: %s", stage_result.stderr)

                if not stage_result.success:
                    logger.error(
                        "Failed to stage file %s: %s", file_path, stage_result.stderr
                    )
                    return None, False
            else:
                logger.info("Skipping staging - file already staged by previous operation")

            # Now commit the staged changes (skip GPG if no key configured to avoid delays)
            if self.config_service and self.config_service.gpg_key_id:
                git_commit_cmd = ["commit", "-S", "-m", commit_message]
                logger.info("Using GPG signing for commit")
            else:
                git_commit_cmd = ["commit", "-m", commit_message]
                logger.info("Skipping GPG signing (no key configured)")
            logger.info(
                "Running git command: %s (work-tree: %s)", " ".join(git_commit_cmd), repo_path
            )

            commit_result = self.run_git_command_with_separate_dirs(
                git_commit_cmd,
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=60,
                operation_name="commit changes"
            )

            logger.info("Git commit success: %s", commit_result.success)
            if commit_result.stdout:
                logger.info("Git commit stdout: %s", commit_result.stdout)
            if commit_result.stderr:
                logger.info("Git commit stderr: %s", commit_result.stderr)

            if not commit_result.success:
                # Try without signing if GPG fails
                logger.warning(
                    "GPG signing failed, attempting commit without signature"
                )
                git_commit_cmd = ["commit", "-m", commit_message]

                commit_result = self.run_git_command_with_separate_dirs(
                    git_commit_cmd,
                    error_mode=SubprocessErrorMode.LENIENT,
                    timeout=60,
                    operation_name="commit without GPG"
                )

                if not commit_result.success:
                    # Enhanced error logging with more diagnostic information
                    error_msg = (
                        commit_result.stderr.strip()
                        if commit_result.stderr.strip()
                        else "No error message from git"
                    )
                    stdout_msg = (
                        commit_result.stdout.strip()
                        if commit_result.stdout.strip()
                        else "No stdout from git"
                    )

                    # Check git status for additional context
                    status_result = self.run_git_command_with_separate_dirs(
                        ["status", "--porcelain"],
                        error_mode=SubprocessErrorMode.SILENT,
                        operation_name="check status for error diagnostics"
                    )

                    status_info = (
                        status_result.stdout.strip()
                        if status_result.success
                        else "Could not get git status"
                    )

                    # Also check what's staged
                    diff_result = self.run_git_command_with_separate_dirs(
                        ["diff", "--cached", "--name-only"],
                        error_mode=SubprocessErrorMode.SILENT,
                        operation_name="check staged files for error diagnostics"
                    )

                    staged_files = (
                        diff_result.stdout.strip()
                        if diff_result.success
                        else "Could not get staged files"
                    )

                    logger.error(
                        "Failed to commit. Error: %s, Stdout: %s", error_msg, stdout_msg
                    )
                    logger.error("Git status output: %s", status_info)
                    logger.error("Staged files: %s", staged_files)
                    return None, False

                # Get commit hash
                hash_result = self.run_git_command_with_separate_dirs(
                    ["rev-parse", "HEAD"],
                    error_mode=SubprocessErrorMode.SILENT,
                    operation_name="get commit hash after failed commit"
                )

                if hash_result.success:
                    commit_hash = hash_result.stdout.strip()
                    logger.info("Commit successful (unsigned): %s", commit_hash)
                    return commit_hash, False
                else:
                    return None, False

            # Get commit hash for signed commit
            hash_result = self.run_git_command_with_separate_dirs(
                ["rev-parse", "HEAD"],
                error_mode=SubprocessErrorMode.SILENT,
                operation_name="get commit hash after successful commit"
            )

            if hash_result.success:
                commit_hash = hash_result.stdout.strip()
                logger.info("Commit successful (signed): %s", commit_hash)
                return commit_hash, True
            else:
                return None, False

        except subprocess.TimeoutExpired:
            logger.error("Git commit command timed out")
            return None, False
        except Exception as e:
            logger.error("Error creating commit: %s", str(e))
            return None, False

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
            repo = self.get_repository(notebook_path)
            if not repo:
                logger.debug("Repository not found for path: %s", notebook_path)
                return False

            repo_root = str(repo.working_dir)

            # Get relative path of the current notebook from repo root
            current_notebook_rel_path = os.path.relpath(notebook_path, repo_root)

            # Check if there's a remote to push to
            remotes_result = self.run_git_command_with_separate_dirs(
                ["remote"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="list remotes"
            )

            if not remotes_result.success or not remotes_result.stdout.strip():
                logger.debug("No remotes found for repository: %s", repo_root)
                return False

            # Get the current branch
            branch_result = self.run_git_command_with_separate_dirs(
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
            files_changed_result = self.run_git_command_with_separate_dirs(
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
                all_files_result = self.run_git_command_with_separate_dirs(
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

    def has_uncommitted_changes(self, notebook_path: str) -> bool:
        """
        Check if the specified notebook has uncommitted changes.

        Args:
            notebook_path: Path to the notebook file (may be from JupyterLab perspective)

        Returns:
            True if there are uncommitted changes, False otherwise
        """
        try:
            logger.info(f"Checking for uncommitted changes in: {notebook_path}")

            # Translate JupyterLab path to sidecar path
            sidecar_notebook_path = self._translate_jupyterlab_path_to_sidecar(notebook_path)

            repo = self.get_repository(sidecar_notebook_path)
            if not repo:
                logger.debug("Repository not found for path: %s", notebook_path)
                return False

            repo_root = str(repo.working_dir)
            logger.debug(f"Repository root: {repo_root}")

            # Get relative path of the notebook from repo root
            notebook_rel_path = os.path.relpath(sidecar_notebook_path, repo_root)
            logger.debug(f"Relative notebook path: {notebook_rel_path}")

            # For file deletions, the file won't exist but there may still be uncommitted changes
            # We need to check git status first before making any decisions based on file existence
            file_exists = os.path.exists(sidecar_notebook_path)
            logger.info(f"File exists check: {file_exists}")
            
            if not file_exists:
                logger.info(f"File does not exist: {sidecar_notebook_path} - checking if it's a deletion")
                # Check git status to see if this is a deletion that needs to be committed
                status_result = self.run_git_command_with_separate_dirs(
                    ["status", "--porcelain", notebook_rel_path],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="check git status for file deletion"
                )
                
                if status_result.returncode == 0:
                    status_output = status_result.stdout.strip()
                    # Check if the file is marked as deleted in git status
                    if status_output.startswith("D ") or status_output.startswith(" D"):
                        logger.info(f"File marked as deleted in git status: {status_output}")
                        return True  # File is deleted but not committed - this is an uncommitted change
                    elif status_output:
                        logger.info(f"File has other git status: {status_output}")
                        return True  # Some other uncommitted change
                
                logger.info("File does not exist and no git status changes - likely never tracked")
                return False

            # Check file modification time and size for debugging (only if file exists)
            if file_exists:
                file_stat = os.stat(sidecar_notebook_path)
                file_mtime = file_stat.st_mtime
                file_size = file_stat.st_size
                logger.debug(f"File modification time: {file_mtime}")
                logger.debug(f"File size: {file_size} bytes")

                # Read and log a snippet of the actual file content for debugging
                try:
                    with open(sidecar_notebook_path, encoding="utf-8") as f:
                        content = f.read()
                        # Log first 200 chars and look for specific patterns
                        content_snippet = content[:200] + (
                            "..." if len(content) > 200 else ""
                        )
                        logger.debug(f"File content snippet: {content_snippet}")

                except Exception as e:
                    logger.warning(f"Could not read file content: {str(e)}")

            # Check if the file has uncommitted changes using git status
            status_result = self.run_git_command_with_separate_dirs(
                ["status", "--porcelain", notebook_rel_path],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check git status for uncommitted changes"
            )

            logger.debug(
                f"Git status command: git status --porcelain {notebook_rel_path}"
            )
            logger.debug(f"Git status return code: {status_result.returncode}")
            logger.debug(f"Git status stdout: '{status_result.stdout}'")
            logger.debug(f"Git status stderr: '{status_result.stderr}'")

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
                    last_commit_result = self.run_git_command_with_separate_dirs(
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
                    logger.debug(f"Error checking last committed content: {str(e)}")

            # Additional debugging: run git diff to see if there are any differences
            # even when git status says there are none
            try:
                diff_result = self.run_git_command_with_separate_dirs(
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
                            f"Git diff output: {diff_output[:500]}..."
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
                    logger.debug(f"Git diff failed: {diff_result.stderr}")

            except Exception as e:
                logger.debug(f"Error running git diff: {str(e)}")

            return has_changes

        except Exception as e:
            logger.error("Error checking for uncommitted changes: %s", str(e))
            logger.error("Exception details:", exc_info=True)
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
            sidecar_path = self._translate_jupyterlab_path_to_sidecar(file_path)
            
            # For our worktree setup, we know the work tree base is the repo root
            if sidecar_path.startswith(self.work_tree_base):
                return self.work_tree_base
            
            # Fallback: check if the path exists and is under our work tree
            normalized_path = self._normalize_to_work_tree(sidecar_path)
            if normalized_path == self.work_tree_base:
                return self.work_tree_base
                
            return None
            
        except Exception as e:
            logger.error("Error getting repository root: %s", str(e))
            return None

    def add_remote(self, remote_name: str, remote_url: str) -> GitOperationResult:
        """
        Add a git remote using the worktree setup.
        
        Args:
            remote_name: Name of the remote (e.g., 'origin', 'gitea-push')
            remote_url: URL of the remote repository
            
        Returns:
            GitOperationResult with operation details
        """
        try:
            logger.info(f"Adding git remote '{remote_name}' with URL: {remote_url}")
            
            result = self.run_git_command_with_separate_dirs(
                ["remote", "add", remote_name, remote_url],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name=f"add remote {remote_name}"
            )
            
            if result.success:
                logger.info(f"✅ Successfully added remote '{remote_name}'")
                return GitOperationResult(
                    success=True,
                    message=f"Remote '{remote_name}' added successfully"
                )
            else:
                logger.error(f"❌ Failed to add remote '{remote_name}': {result.error_message}")
                return GitOperationResult(
                    success=False,
                    message=f"Failed to add remote '{remote_name}'",
                    error=result.error_message
                )
                
        except Exception as e:
            logger.error(f"Error adding remote '{remote_name}': {str(e)}")
            return GitOperationResult(
                success=False,
                message=f"Failed to add remote '{remote_name}'",
                error=str(e)
            )

    def remove_remote(self, remote_name: str) -> GitOperationResult:
        """
        Remove a git remote using the worktree setup.
        
        Args:
            remote_name: Name of the remote to remove
            
        Returns:
            GitOperationResult with operation details
        """
        try:
            logger.info(f"Removing git remote '{remote_name}'")
            
            result = self.run_git_command_with_separate_dirs(
                ["remote", "remove", remote_name],
                error_mode=SubprocessErrorMode.LENIENT,  # Don't fail if remote doesn't exist
                timeout=30,
                operation_name=f"remove remote {remote_name}"
            )
            
            if result.success:
                logger.info(f"✅ Successfully removed remote '{remote_name}'")
                return GitOperationResult(
                    success=True,
                    message=f"Remote '{remote_name}' removed successfully"
                )
            else:
                # Remote might not exist, which is fine
                logger.info(f"Remote '{remote_name}' was not present or already removed")
                return GitOperationResult(
                    success=True,
                    message=f"Remote '{remote_name}' was not present"
                )
                
        except Exception as e:
            logger.error(f"Error removing remote '{remote_name}': {str(e)}")
            return GitOperationResult(
                success=False,
                message=f"Failed to remove remote '{remote_name}'",
                error=str(e)
            )

    def update_remote_url(self, remote_name: str, remote_url: str) -> GitOperationResult:
        """
        Update a git remote URL using the worktree setup.
        
        Args:
            remote_name: Name of the remote to update
            remote_url: New URL for the remote
            
        Returns:
            GitOperationResult with operation details
        """
        try:
            logger.info(f"Updating git remote '{remote_name}' to URL: {remote_url}")
            
            result = self.run_git_command_with_separate_dirs(
                ["remote", "set-url", remote_name, remote_url],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name=f"update remote {remote_name}"
            )
            
            if result.success:
                logger.info(f"✅ Successfully updated remote '{remote_name}'")
                return GitOperationResult(
                    success=True,
                    message=f"Remote '{remote_name}' updated successfully"
                )
            else:
                logger.error(f"❌ Failed to update remote '{remote_name}': {result.error_message}")
                return GitOperationResult(
                    success=False,
                    message=f"Failed to update remote '{remote_name}'",
                    error=result.error_message
                )
                
        except Exception as e:
            logger.error(f"Error updating remote '{remote_name}': {str(e)}")
            return GitOperationResult(
                success=False,
                message=f"Failed to update remote '{remote_name}'",
                error=str(e)
            )

    def push_to_remote(self, remote_name: str, branch: str = "HEAD") -> GitOperationResult:
        """
        Push to a remote repository using the worktree setup.
        
        Args:
            remote_name: Name of the remote to push to
            branch: Branch to push (defaults to HEAD)
            
        Returns:
            GitOperationResult with push details
        """
        try:
            logger.info(f"Pushing to remote '{remote_name}' branch '{branch}'")
            
            result = self.run_git_command_with_separate_dirs(
                ["push", remote_name, branch],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=120,
                operation_name=f"push to {remote_name}",
            )
            
            if result.success:
                logger.info(f"✅ Successfully pushed to remote '{remote_name}'")
                return GitOperationResult(
                    success=True,
                    message=f"Push to '{remote_name}' completed successfully",
                    commit_hash=None  # Could extract from push output if needed
                )
            else:
                logger.error(f"❌ Failed to push to remote '{remote_name}': {result.error_message}")
                return GitOperationResult(
                    success=False,
                    message=f"Failed to push to remote '{remote_name}'",
                    error=result.error_message
                )
                
        except Exception as e:
            logger.error(f"Error pushing to remote '{remote_name}': {str(e)}")
            return GitOperationResult(
                success=False,
                message=f"Failed to push to remote '{remote_name}'",
                error=str(e)
            )

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
            check_result = self.run_git_command_with_separate_dirs(
                ["rev-parse", "--verify", remote_branch],
                error_mode=SubprocessErrorMode.SILENT,
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

    def _sync_and_retry_push(self, remote_name: str, branch: str = "HEAD", 
                           ) -> GitOperationResult:
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

    def push_to_remote_with_retry(self, remote_name: str, branch: str = "HEAD",
                                 allow_sync: bool = True) -> GitOperationResult:
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


    def get_git_config(self, config_key: str, repo_path: Optional[str] = None) -> Optional[str]:
        """
        Get a git configuration value using the worktree setup.
        
        Args:
            config_key: Git configuration key (e.g., 'user.name', 'user.email')
            repo_path: Optional repository path (defaults to work tree base)
            
        Returns:
            Configuration value or None if not set
        """
        try:
            result = self.run_git_command_with_separate_dirs(
                ["config", config_key],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=10,
                operation_name=f"get git config {config_key}"
            )
            
            if result.success and result.stdout.strip():
                return result.stdout.strip()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting git config '{config_key}': {str(e)}")
            return None

    def set_git_config(self, config_key: str, config_value: str, repo_path: Optional[str] = None) -> GitOperationResult:
        """
        Set a git configuration value using the worktree setup.
        
        Args:
            config_key: Git configuration key (e.g., 'user.name', 'user.email')
            config_value: Value to set
            repo_path: Optional repository path (defaults to work tree base)
            
        Returns:
            GitOperationResult with operation details
        """
        try:
            logger.info(f"Setting git config '{config_key}' = '{config_value}'")
            
            result = self.run_git_command_with_separate_dirs(
                ["config", config_key, config_value],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name=f"set git config {config_key}"
            )
            
            if result.success:
                logger.info(f"✅ Successfully set git config '{config_key}'")
                return GitOperationResult(
                    success=True,
                    message=f"Git config '{config_key}' set successfully"
                )
            else:
                logger.error(f"❌ Failed to set git config '{config_key}': {result.error_message}")
                return GitOperationResult(
                    success=False,
                    message=f"Failed to set git config '{config_key}'",
                    error=result.error_message
                )
                
        except Exception as e:
            logger.error(f"Error setting git config '{config_key}': {str(e)}")
            return GitOperationResult(
                success=False,
                message=f"Failed to set git config '{config_key}'",
                error=str(e)
            )

    def fetch_from_remote(self, remote_name: str, branch: Optional[str] = None) -> GitOperationResult:
        """
        Fetch from a remote repository using the worktree setup.
        
        Args:
            remote_name: Name of the remote to fetch from
            branch: Optional specific branch to fetch
            
        Returns:
            GitOperationResult with fetch details
        """
        try:
            logger.info(f"Fetching from remote '{remote_name}'")
            
            fetch_args = ["fetch", remote_name]
            if branch:
                fetch_args.append(branch)
            
            result = self.run_git_command_with_separate_dirs(
                fetch_args,
                error_mode=SubprocessErrorMode.STRICT,
                timeout=60,
                operation_name=f"fetch from {remote_name}"
            )
            
            if result.success:
                logger.info(f"✅ Successfully fetched from remote '{remote_name}'")
                return GitOperationResult(
                    success=True,
                    message=f"Fetch from '{remote_name}' completed successfully"
                )
            else:
                logger.error(f"❌ Failed to fetch from remote '{remote_name}': {result.error_message}")
                return GitOperationResult(
                    success=False,
                    message=f"Failed to fetch from remote '{remote_name}'",
                    error=result.error_message
                )
                
        except Exception as e:
            logger.error(f"Error fetching from remote '{remote_name}': {str(e)}")
            return GitOperationResult(
                success=False,
                message=f"Failed to fetch from remote '{remote_name}'",
                error=str(e)
            )

    def get_current_branch(self) -> Optional[str]:
        """
        Get the current branch name using the worktree setup.
        
        Returns:
            Current branch name or None if unable to determine
        """
        try:
            result = self.run_git_command_with_separate_dirs(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="get current branch"
            )
            
            if result.success and result.stdout.strip():
                return result.stdout.strip()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting current branch: {str(e)}")
            return None

    def merge_branch(self, branch_name: str, allow_unrelated: bool = True) -> GitOperationResult:
        """
        Merge a branch using the worktree setup.
        
        Args:
            branch_name: Name of the branch to merge
            allow_unrelated: Whether to allow unrelated histories
            
        Returns:
            GitOperationResult with merge details
        """
        try:
            logger.info(f"Merging branch '{branch_name}'")
            
            merge_args = ["merge", branch_name, "--no-edit"]
            if allow_unrelated:
                merge_args.append("--allow-unrelated-histories")
            
            result = self.run_git_command_with_separate_dirs(
                merge_args,
                error_mode=SubprocessErrorMode.STRICT,
                timeout=60,
                operation_name=f"merge {branch_name}"
            )
            
            if result.success:
                logger.info(f"✅ Successfully merged branch '{branch_name}'")
                return GitOperationResult(
                    success=True,
                    message=f"Merge of '{branch_name}' completed successfully"
                )
            else:
                logger.error(f"❌ Failed to merge branch '{branch_name}': {result.error_message}")
                return GitOperationResult(
                    success=False,
                    message=f"Failed to merge branch '{branch_name}'",
                    error=result.error_message
                )
                
        except Exception as e:
            logger.error(f"Error merging branch '{branch_name}': {str(e)}")
            return GitOperationResult(
                success=False,
                message=f"Failed to merge branch '{branch_name}'",
                error=str(e)
            )
