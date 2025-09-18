"""
Core git operations service.

This module provides the fundamental git operations using separate git-dir and work-tree.
It handles the low-level git command execution and repository access.
"""

import logging
import os
from typing import Any, Dict, Optional

from git import InvalidGitRepositoryError, Repo

from ..logger_util import default_logger_config
from ..subprocess_util import SubprocessErrorMode, run_git_command
from ..config_service import ConfigService
# GitOperationResult will be used when we add more methods

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitCoreService:
    """Core git operations using separate git-dir and work-tree."""

    def __init__(self, config_service: Optional[ConfigService] = None):
        """Initialize the core git service."""
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
        
        Args:
            file_path: Original file path from any context
            
        Returns:
            Normalized path that can be used with our work tree structure.
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
    
    def translate_jupyterlab_path_to_sidecar(self, file_path: str) -> str:
        """
        Translate file paths from JupyterLab perspective to sidecar perspective.
        
        This handles the path translation between containers:
        - JupyterLab sees files at: /home/jovyan/work/notebook.ipynb
        - Sidecar sees same files at: /tmp/work/notebook.ipynb
        
        Args:
            file_path: Path from JupyterLab perspective
            
        Returns:
            Equivalent path from sidecar perspective
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
            sidecar_file_path = self.translate_jupyterlab_path_to_sidecar(file_path)
            
            # Normalize the file path to work tree path
            work_tree_path = self._normalize_to_work_tree(sidecar_file_path)
            
            # Check if work tree path is valid
            if not work_tree_path.startswith(self.work_tree_base):
                logger.debug("File path not in work tree: %s", file_path)
                return None

            # Check cache first using work tree base as key
            cache_key = self.work_tree_base
            if cache_key in self._repo_cache:
                logger.info("📁 Repo in cache for work tree: %s", cache_key)
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

    def _configure_git_user(self, repo_path: str) -> None:
        """
        Configure git user for the repository with robust fallbacks.
        
        Args:
            repo_path: Path to the git repository
        """
        try:
            # Get user info from config service with fallback to environment variables
            if self.config_service and self.config_service.git_user_email != "NOT_SET":
                usr_email = self.config_service.git_user_email
                usr_name = self.config_service.git_user_name
                logger.info("Configuring git user from config service: %s <%s>", usr_name, usr_email)
            else:
                # Fallback to environment variables (like legacy service)
                usr_email = os.getenv("GIT_USER_EMAIL", "user@example.com")
                usr_name = os.getenv("GIT_USER_NAME", "JupyterLab User")
                logger.info("Configuring git user from environment variables: %s <%s>", usr_name, usr_email)
            
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

            if name_result.success and email_result.success:
                actual_name = name_result.stdout.strip()
                actual_email = email_result.stdout.strip()
                logger.info(f"Verified git config for repository {repo_path}: {actual_name} <{actual_email}>")
                
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
