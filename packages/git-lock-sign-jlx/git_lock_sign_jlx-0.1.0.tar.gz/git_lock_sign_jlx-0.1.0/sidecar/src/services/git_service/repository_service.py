"""
Repository management service.

Handles git repository initialization, configuration, and basic repository operations.
"""

import logging
import os

from typing import Optional

from ..config_service import ConfigService
from ..subprocess_util import SubprocessErrorMode
from .core_service import GitCoreService
from .commit_service import GitCommitService
from .remote_service import GitRemoteService
from .push_service import GitPushService
from ..logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class GitRepositoryService:
    """Handles repository initialization and management."""

    def __init__(
        self,
        core_service: GitCoreService,
        config_service: ConfigService,
        commit_service: GitCommitService,
        remote_service: GitRemoteService,
        push_service: GitPushService,
    ):
        """Initialize the repository service."""
        self.core = core_service
        self.config_service = config_service
        self.commit_service = commit_service
        self.remote_service = remote_service
        self.push_service = push_service

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
        try:
            # Normalize notebook path to work tree
            work_tree_path = self.core._normalize_to_work_tree(notebook_path)

            # Check if git repository already exists
            if self.core.is_git_repository(work_tree_path):
                logger.info(
                    "Git repository already exists for work tree: %s",
                    self.core.work_tree_base,
                )
                return self.core.work_tree_base

            # Create directories if they don't exist
            os.makedirs(self.core.git_metadata_base, exist_ok=True)
            os.makedirs(self.core.work_tree_base, exist_ok=True)

            git_dir = os.path.join(self.core.git_metadata_base, ".git")

            logger.info(
                "Initializing git repository with separate directories:"
            )
            logger.info(f"  Git metadata: {git_dir}")
            logger.info(f"  Work tree: {self.core.work_tree_base}")

            # Initialize the repository
            result = self.core.run_git_command_with_separate_dirs(
                ["init"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name="initialize git repository with separate structure",
            )

            if not result.success:
                raise RuntimeError(
                    f"Failed to initialize git repository: {result.stderr}"
                )

            logger.info(
                "Successfully initialized git repository with separate structure"
            )

            # Verify git directory was created
            if not os.path.exists(git_dir):
                raise Exception(f"Git directory was not created: {git_dir}")

            # Configure repository as safe directory to prevent ownership issues
            self.core._configure_safe_directory(self.core.work_tree_base)

            # Configure git user (will be overridden by ConfigService if available)
            logger.info(
                "📁 Configuring git user for work tree: %s",
                self.core.work_tree_base,
            )
            self._configure_git_user(self.core.work_tree_base)

            # Ensure git configuration is properly set
            self._ensure_git_config(self.core.work_tree_base)

            # Generate .gitignore file for JupyterLab environment
            self._create_jupyterlab_gitignore(self.core.work_tree_base)

            return self.core.work_tree_base

        except Exception as e:
            logger.error("Failed to initialize git repository: %s", str(e))
            raise

    def _configure_git_user(self, repo_path: str) -> None:
        """
        Configure git user for the repository using config service values with fallbacks.

        This function prioritizes config service but falls back to environment variables
        and configures the local git repository accordingly.

        Args:
            repo_path: Path to the git repository
        """
        try:
            # Get user info from config service or environment
            if (
                self.config_service
                and self.config_service.git_user_email != "NOT_SET"
            ):
                usr_email = self.config_service.git_user_email
                usr_name = self.config_service.git_user_name
                logger.info(
                    "Configuring git user from config service: %s <%s>",
                    usr_name,
                    usr_email,
                )
            else:
                # Fallback to environment variables
                usr_email = os.getenv("GIT_USER_EMAIL", "user@example.com")
                usr_name = os.getenv("GIT_USER_NAME", "JupyterLab User")
                logger.info(
                    "Configuring git user from environment: %s <%s>",
                    usr_name,
                    usr_email,
                )

            # Set git user configuration with --local flag to ensure repository-specific config
            result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name", usr_name],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="configure git user name",
            )

            if not result.success:
                logger.error("Failed to set git user name: %s", result.stderr)
                raise RuntimeError(
                    f"Failed to configure git user name: {result.stderr}"
                )

            result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email", usr_email],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=10,
                operation_name="configure git user email",
            )

            if not result.success:
                logger.error("Failed to set git user email: %s", result.stderr)
                raise RuntimeError(
                    f"Failed to configure git user email: {result.stderr}"
                )

            logger.info(
                "Git user configured successfully for repository: %s", repo_path
            )

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
                # Default to disabling SSL verification for development/testing
                logger.info(
                    "Disabling SSL verification for git operations (no config service)"
                )
                result = self.core.run_git_command_with_separate_dirs(
                    ["config", "--local", "http.sslVerify", "false"],
                    error_mode=SubprocessErrorMode.STRICT,
                    timeout=10,
                    operation_name="configure git SSL verification",
                )

                if not result.success:
                    logger.warning(
                        "Failed to configure git SSL verification: %s",
                        result.stderr,
                    )
                else:
                    logger.info(
                        "Git SSL verification disabled for repository: %s",
                        repo_path,
                    )
                return

            if not self.config_service.git_ssl_verify:
                logger.info(
                    "Disabling SSL verification for git operations (development mode)"
                )
                result = self.core.run_git_command_with_separate_dirs(
                    ["config", "--local", "http.sslVerify", "false"],
                    error_mode=SubprocessErrorMode.STRICT,
                    timeout=10,
                    operation_name="configure git SSL verification",
                )

                if not result.success:
                    logger.warning(
                        "Failed to configure git SSL verification: %s",
                        result.stderr,
                    )
                else:
                    logger.info(
                        "Git SSL verification disabled for repository: %s",
                        repo_path,
                    )
            else:
                logger.debug(
                    "Git SSL verification enabled for repository: %s", repo_path
                )

        except Exception as e:
            logger.warning(
                "Failed to configure git SSL verification: %s", str(e)
            )

    def _configure_git_performance(self, repo_path: str) -> None:
        """
        Configure git performance optimizations for faster operations.

        Args:
            repo_path: Path to the git repository
        """
        try:
            logger.info(
                "Configuring git performance optimizations for: %s", repo_path
            )

            # Optimize git operations for speed (comprehensive set matching legacy)
            performance_configs = [
                # Reduce protocol overhead
                ("core.preloadindex", "true"),
                (
                    "core.fscache",
                    "true",
                ),  # Windows optimization, harmless on Linux
                (
                    "gc.auto",
                    "0",
                ),  # Disable automatic garbage collection during operations
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
                (
                    "http.postBuffer",
                    "1048576000",
                ),  # 1GB buffer for large pushes
            ]

            for config_key, config_value in performance_configs:
                try:
                    result = self.core.run_git_command_with_separate_dirs(
                        ["config", "--local", config_key, config_value],
                        error_mode=SubprocessErrorMode.LENIENT,  # Don't fail if some configs aren't supported
                        timeout=10,
                        operation_name=f"configure git performance {config_key}",
                    )

                    if not result.success:
                        logger.debug(
                            f"Could not set {config_key}: {result.stderr}"
                        )
                except Exception as e:
                    logger.debug(f"Could not set {config_key}: {e}")

            logger.info(
                "Git performance optimizations configured for repository: %s",
                repo_path,
            )

        except Exception as e:
            logger.warning(
                "Failed to configure git performance optimizations: %s", str(e)
            )

    def _load_template(self, template_filename: str) -> str:
        """Load a template file from the templates directory."""
        try:
            # Get the directory containing this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to the services directory, then to templates
            templates_dir = os.path.join(current_dir, "..", "..", "templates")
            template_path = os.path.join(templates_dir, template_filename)

            if not os.path.exists(template_path):
                logger.warning("Template file not found: %s", template_path)
                return ""

            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()

        except Exception as e:
            logger.error(
                "Error loading template %s: %s", template_filename, str(e)
            )
            return ""

    def _create_jupyterlab_gitignore(self, repo_path: str):
        """Create a .gitignore file for JupyterLab notebooks."""
        try:
            gitignore_path = os.path.join(repo_path, ".gitignore")

            # Check if .gitignore already exists
            if os.path.exists(gitignore_path):
                logger.info(".gitignore already exists at: %s", gitignore_path)
                return

            # Load template
            gitignore_content = self._load_template("gitignore.template")

            if not gitignore_content:
                # Fallback content if template not found
                gitignore_content = """# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
"""

            # Write .gitignore file
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(gitignore_content)

            logger.info("Created .gitignore file at: %s", gitignore_path)

            # Automatically commit the .gitignore file (push will happen later after remote is configured)
            self._auto_commit_gitignore(repo_path)

        except Exception as e:
            logger.error("Error creating .gitignore file: %s", str(e))

    def _auto_commit_gitignore(self, repo_path: str):
        """Automatically commit the .gitignore file after creation."""
        try:
            # Check if commit service is available
            if not self.commit_service:
                logger.warning(
                    "Commit service not available, skipping auto-commit of .gitignore file"
                )
                return

            # Commit the .gitignore file
            logger.info("Auto-committing .gitignore file...")
            commit_result = self.commit_service.commit_gitignore_file(repo_path)

            if commit_result.success:
                logger.info("Successfully auto-committed .gitignore file")
            else:
                logger.warning(
                    "Failed to auto-commit .gitignore file: %s",
                    commit_result.message,
                )

        except Exception as e:
            logger.warning(
                "Error during auto-commit of .gitignore file: %s", str(e)
            )
            # Don't raise - this is not critical for repository functionality

    def push_gitignore_commit_if_exists(self):
        """Push the .gitignore commit if it exists and remote is configured."""
        try:
            # Try to push any unpushed commits (which should include .gitignore)
            logger.info("Attempting to push .gitignore commit to remote...")
            push_result = self.push_service.push_to_remote("origin", "HEAD")

            if push_result.success:
                logger.info("Successfully pushed .gitignore commit to remote")
            else:
                logger.info(
                    "Could not push .gitignore commit: %s", push_result.message
                )

        except Exception as e:
            logger.warning("Error during push of .gitignore commit: %s", str(e))
            # Don't raise - this is not critical for repository functionality

    def ensure_gitignore_exists(self, notebook_path: str) -> bool:
        """
        Ensure .gitignore file exists in the repository.
        If it doesn't exist, create it and auto-commit it.

        Args:
            notebook_path: Path to the notebook file

        Returns:
            True if .gitignore exists or was created, False otherwise
        """
        try:
            # Get repository path
            repo = self.core.get_repository(notebook_path)
            if not repo:
                logger.warning("Not in a git repository: %s", notebook_path)
                return False

            # Get repository root
            repo_root = repo.working_dir
            if not repo_root:
                logger.warning("Could not determine repository root")
                return False

            gitignore_path = os.path.join(repo_root, ".gitignore")

            if os.path.exists(gitignore_path):
                logger.debug(".gitignore already exists: %s", gitignore_path)
                return True

            # Create .gitignore
            logger.info(
                "Creating missing .gitignore file and auto-committing it..."
            )
            self._create_jupyterlab_gitignore(str(repo_root))
            return True

        except Exception as e:
            logger.error("Error ensuring .gitignore exists: %s", str(e))
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
            name_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check git user name",
            )

            email_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check git user email",
            )

            # If not configured or if we have a config service with environment variables, reconfigure
            if (
                not name_result.success
                or not email_result.success
                or (
                    self.config_service
                    and self.config_service.git_user_email != "NOT_SET"
                    and (
                        name_result.stdout.strip()
                        != self.config_service.git_user_name
                        or email_result.stdout.strip()
                        != self.config_service.git_user_email
                    )
                )
            ):
                logger.info(
                    "Ensuring git configuration is properly set for repository: %s",
                    repo_path,
                )
                self._configure_git_user(repo_path)

                # Verify configuration was set correctly
                self._verify_git_config(repo_path)
            else:
                logger.debug(
                    "Git configuration already properly set for repository: %s",
                    repo_path,
                )

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
            name_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.name"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="verify git user name",
            )

            email_result = self.core.run_git_command_with_separate_dirs(
                ["config", "--local", "user.email"],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="verify git user email",
            )

            if name_result.success and email_result.success:
                actual_name = name_result.stdout.strip()
                actual_email = email_result.stdout.strip()
                logger.info(
                    f"Verified git config for repository {repo_path}: {actual_name} <{actual_email}>"
                )

                # Check if this matches expected values from config service
                if (
                    self.config_service
                    and self.config_service.git_user_email != "NOT_SET"
                ):
                    expected_name = self.config_service.git_user_name
                    expected_email = self.config_service.git_user_email

                    if (
                        actual_name != expected_name
                        or actual_email != expected_email
                    ):
                        logger.warning(
                            f"Git config mismatch in {repo_path}! Expected: {expected_name} <{expected_email}>, Got: {actual_name} <{actual_email}>"
                        )
                        # Try to fix it
                        logger.info("Attempting to fix git config mismatch...")
                        self._configure_git_user(repo_path)

                        # Verify the fix
                        self._verify_git_config(repo_path)
            else:
                logger.error(
                    f"Git configuration verification failed for repository: {repo_path}"
                )
                logger.debug(
                    f"Name result: success={name_result.success}, stdout={name_result.stdout}"
                )
                logger.debug(
                    f"Email result: success={email_result.success}, stdout={email_result.stdout}"
                )
                # Reconfigure
                self._configure_git_user(repo_path)

        except Exception as e:
            logger.warning("Failed to verify git configuration: %s", str(e))
