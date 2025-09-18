"""
Configuration service for CELN Sidecar

Manages environment variables and configuration settings.
"""

import logging
import os
from typing import Optional

from .logger_util import default_logger_config

# get full path of the current file
logger = logging.getLogger(__name__)
default_logger_config(logger)


VALID_GIT_SERVERS = ["gitlab","gitea","github_enterprise"]


class ConfigService:
    """Service for managing configuration from environment variables."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self._load_config()

    def _print_config_values(self) -> None:
        """Cycle through all member variables and print their values."""
        for name, value in self.__dict__.items():
            if name == "git_server_admin_token":
                if isinstance(value, str) and len(value) > 0:
                    value = value[:4] + "*" * (len(value) - 4)
                else:
                    value = "NOT_SET"
            logger.info("[ConfigService] %s: %s", name, value)

    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        # current options: gitea (default), gitlab, github_enterprise
        self.git_server = os.getenv("GIT_SERVER", "gitea")
        
        # Normalize git server value (support both github-enterprise and github_enterprise)
        if self.git_server == "github-enterprise":
            self.git_server = "github_enterprise"

        assert self.git_server in VALID_GIT_SERVERS, f"Invalid git server: {self.git_server}"
            
        # Git server URL configuration
        if self.git_server in ["gitlab","gitea"]:
            self.git_server_url = os.getenv("GIT_SERVER_URL", "http://localhost:3000" if self.git_server == "gitea" else "https://localhost:8443")
        elif self.git_server == "github_enterprise":
            self.git_server_url = os.getenv("GITHUB_ENTERPRISE_URL")
        else:
            pass
            
        # this is the admin token for the git server, used for user creation,
        # repository creation, etc.
        self.git_server_admin_token = os.getenv("GIT_SERVER_ADMIN_TOKEN")

        # GitHub Enterprise specific configuration
        if self.git_server == "github_enterprise":
            # Use GITHUB_ENTERPRISE_URL if explicitly set, otherwise fall back to GIT_SERVER_URL
            self.github_enterprise_url = os.getenv("GITHUB_ENTERPRISE_URL") or self.git_server_url
            self.github_enterprise_org = os.getenv("GITHUB_ENTERPRISE_ORG", "")
            self.github_app_id = os.getenv("GITHUB_APP_ID")
            installation_id_env = os.getenv("GITHUB_APP_INSTALLATION_ID")
            if installation_id_env is None:
                logger.error("GITHUB_APP_INSTALLATION_ID not set")
                raise ValueError("GITHUB_APP_INSTALLATION_ID not set")
            self.github_app_installation_id = int(installation_id_env)
            self.github_app_private_key_path = os.getenv(
                "GITHUB_APP_PRIVATE_KEY_PATH", 
                "/app/secrets/github-app-private-key.pem"
            )
            self.github_auth_mode = os.getenv("GITHUB_AUTH_MODE", "app")
            self.repo_template = os.getenv("REPO_TEMPLATE", "")
            self.default_repo_private = os.getenv("DEFAULT_REPO_PRIVATE", "true").lower() == "true"            
        else:
            # Set defaults for non-GitHub Enterprise configurations
            self.github_enterprise_url = None
            self.github_enterprise_org = None
            self.github_app_id = None
            self.github_app_installation_id = None
            self.github_app_private_key_path = None
            self.github_auth_mode = None
            self.repo_template = None
            self.default_repo_private = True

        # Git configuration
        self.git_user_name = os.getenv("GIT_USER_NAME", "NOT_SET")
        self.git_user_email = os.getenv("GIT_USER_EMAIL", "")
        if not self.git_user_email:
            logger.error("GIT_USER_EMAIL not set")
            raise ValueError("GIT_USER_EMAIL not set")
        else:
            if '@' not in self.git_user_email:
                logger.error("GIT_USER_EMAIL is invalid, must contain @")
                raise ValueError("GIT_USER_EMAIL is invalid, must contain @")
            
        self.gpg_key_id = os.getenv("GPG_KEY_ID")


        # If GIT_USER_NAME is not provided in env, extract from email
        if self.git_user_name == "NOT_SET" and self.git_user_email != "NOT_SET":
            self.git_user_name = (
                self.git_user_email.split("@")[0]
                if "@" in self.git_user_email
                else self.git_user_email
            )


        # Git SSL verification (for development with self-signed certificates)
        git_ssl_verify_env = os.getenv("GIT_SSL_VERIFY", "true")
        self.git_ssl_verify = git_ssl_verify_env.lower() == "true"

        # allowed domains for git user email
        self.allowed_domains = os.getenv("ALLOWED_DOMAINS", "")

        # include metadata in the commit message
        self.include_metadata = os.getenv("INCLUDE_METADATA", "false").lower() == "true"

        # whether to use a single repo for each user. if so the repo path would be
        # /repos/<user_name>/work (gitea)
        self.single_repo_per_user = (
            os.getenv("SINGLE_REPO_PER_USER", "true").lower() == "true"
        )

        # Commit message configuration
        self.commit_message_mode = os.getenv(
            "COMMIT_MESSAGE_MODE", "detailed"
        )  # generic | detailed

        # Debouncing configuration (in seconds)
        self.commit_debounce_seconds = int(
            os.getenv("COMMIT_DEBOUNCE_SECONDS", "30")
        )
        self.push_debounce_seconds = int(
            os.getenv("PUSH_DEBOUNCE_SECONDS", "120")
        )

        # Auto-save configuration
        self.auto_save_enabled = (
            os.getenv("AUTO_SAVE_ENABLED", "true").lower() == "true"
        )
        self.auto_save_interval_minutes = int(
            os.getenv("AUTO_SAVE_INTERVAL_MINUTES", "5")
        )


        # Frontend configuration
        self.cell_execution_detection_delay_ms = int(
            os.getenv("CELL_EXECUTION_DETECTION_DELAY_MS", "1000")
        )

        # Frontend timeout configuration
        self.health_check_interval_ms = int(
            os.getenv("HEALTH_CHECK_INTERVAL_MS", "30000")
        )
        self.health_check_timeout_ms = int(
            os.getenv("HEALTH_CHECK_TIMEOUT_MS", "5000")
        )
        self.api_request_timeout_ms = int(
            os.getenv("API_REQUEST_TIMEOUT_MS", "180000")  # Default 3 minutes for git operations
        )
        self.notification_auto_dismiss_ms = int(
            os.getenv("NOTIFICATION_AUTO_DISMISS_MS", "5000")
        )

        # Workspace configuration - CREATE_WORK_SUBDIRECTORY for K8s deployments
        self.create_work_subdirectory = (
            os.getenv("CREATE_WORK_SUBDIRECTORY", "false").lower() == "true"
        )

        # Git directory structure configuration for separated git-dir and work-tree
        self.git_metadata_directory = os.getenv("GIT_METADATA_DIRECTORY", "/tmp/.git-metadata")
        self.work_tree_directory = os.getenv("WORK_TREE_DIRECTORY", "/tmp/work")

        self.debug_mode = os.getenv("SIDECAR_DEBUG", "false").lower() == "true"

        # Button configuration
        self.enable_commit_button = (
            os.getenv("ENABLE_COMMIT_BUTTON", "false").lower() == "true"
        )
        self.enable_push_button = (
            os.getenv("ENABLE_PUSH_BUTTON", "false").lower() == "true"
        )
        self.enable_lock_button = (
            os.getenv("ENABLE_LOCK_BUTTON", "false").lower() == "true"
        )

        # File lifecycle tracking configuration
        self.enable_file_creation_tracking = (
            os.getenv("ENABLE_FILE_CREATION_TRACKING", "false").lower() == "true"
        )

        self._print_config_values()

        # Validation
        self._validate_config()


    def _validate_config(self) -> tuple[bool, list[str]]:
        """Validate required configuration."""
        errors = []
        if not self.git_server_admin_token:
            errors.append(
                "GIT_SERVER_ADMIN_TOKEN not set - Git operations may fail"
            )

        # Only validate the token for the configured git server
        git_server = os.getenv("GIT_SERVER", "gitlab").lower()
        if git_server == "gitea":
            if not self.git_server_admin_token:
                errors.append(
                    "GITEA_ADMIN_TOKEN not set - Gitea operations will fail"
                )
        elif git_server == "gitlab":
            # Default to GitLab
            if not self.git_server_admin_token:
                errors.append(
                    "GITLAB_ADMIN_TOKEN not set - GitLab operations will fail"
                )
        elif git_server == "github_enterprise":
            pass
        else:
            errors.append(f"Invalid GIT_SERVER: {git_server}")

        if self.commit_message_mode not in ["generic", "detailed"]:
            errors.append(
                f"Invalid COMMIT_MESSAGE_MODE: {self.commit_message_mode}, defaulting to 'generic'"
            )
            self.commit_message_mode = "generic"

        if self.commit_debounce_seconds < 0:
            errors.append(
                "COMMIT_DEBOUNCE_SECONDS cannot be negative, setting to 0"
            )
            self.commit_debounce_seconds = 0

        if self.push_debounce_seconds < 0:
            errors.append(
                "PUSH_DEBOUNCE_SECONDS cannot be negative, setting to 0"
            )
            self.push_debounce_seconds = 0

        if self.auto_save_interval_minutes < 1:
            errors.append(
                "AUTO_SAVE_INTERVAL_MINUTES cannot be less than 1, setting to 1"
            )
            self.auto_save_interval_minutes = 1

        if len(errors) > 0:
            logger.error(f"Configuration errors: {errors}")
            return False, errors
        return True, []

    @property
    def auto_save_interval_seconds(self) -> int:
        """Get auto-save interval in seconds."""
        return self.auto_save_interval_minutes * 60

    def get_gitlab_config(self) -> dict:
        """Get GitLab configuration as dictionary."""
        return {
            "url": self.git_server_url,
            # "token": self.gitlab_token,
            "admin_token": self.git_server_admin_token,
        }

    def get_gitea_config(self) -> dict:
        """Get Gitea configuration as dictionary."""
        return {
            "url": self.git_server_url,
            "admin_token": self.git_server_admin_token,
        }

    def get_github_enterprise_config(self) -> dict:
        """Get GitHub Enterprise configuration as dictionary."""
        return {
            "url": self.github_enterprise_url,
            "org": self.github_enterprise_org,
            "app_id": self.github_app_id,
            "installation_id": self.github_app_installation_id,
            "private_key_path": self.github_app_private_key_path,
            "auth_mode": self.github_auth_mode,
            "repo_template": self.repo_template,
            "default_repo_private": self.default_repo_private,
        }

    def get_git_config(self) -> dict:
        """Get git configuration as dictionary."""
        return {
            "user_name": self.git_user_name,
            "user_email": self.git_user_email,
            "gpg_key_id": self.gpg_key_id,
            "ssl_verify": self.git_ssl_verify,
        }

    def is_detailed_commit_mode(self) -> bool:
        """Check if detailed commit message mode is enabled."""
        return self.commit_message_mode == "detailed"

    def reload_config(self) -> None:
        """Reload configuration from environment variables."""
        logger.info("Reloading configuration from environment")
        self._load_config()

    def get_git_server_api_token(self) -> Optional[str]:
        """
        Get Git server API token from environment.

        Returns:
            Git server API token if set, None otherwise
        """
        return os.getenv("GIT_SERVER_API_TOKEN")
