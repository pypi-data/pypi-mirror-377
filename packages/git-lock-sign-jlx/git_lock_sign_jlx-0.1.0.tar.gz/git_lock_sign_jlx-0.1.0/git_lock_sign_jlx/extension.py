"""Jupyter server extension for git-based notebook locking and signing."""

import logging
from jupyter_server.utils import url_path_join

from .handlers import (
    CommitNotebookHandler,
    ConfigHandler,
    FileLifecycleCommitHandler,
    GitInitHandler,
    HealthHandler,
    LockNotebookHandler,
    ProvisionRepositoryHandler,
    PushRepositoryHandler,
    SidecarUrlHandler,
    StatusHandler,
    UnlockNotebookHandler,
    UserInfoHandler,
    WorkingDirectoryHandler,
    SessionInitHandler,
)

logger = logging.getLogger(__name__)


def setup_handlers(web_app):
    """Set up the API handlers for git-lock-sign extension."""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    # Define all handlers with their URL patterns
    handlers = [
        # Working directory handler - needed to determine absolute paths for sidecar
        (url_path_join(base_url, "git-lock-sign", "working-directory"), WorkingDirectoryHandler),
        # Sidecar URL handler - provides sidecar connection info from environment variables
        (url_path_join(base_url, "git-lock-sign", "sidecar-url"), SidecarUrlHandler),
        # Health check handler - check sidecar health via backend
        (url_path_join(base_url, "git-lock-sign", "health"), HealthHandler),
        # Enable handlers that use SidecarClient for logging visibility
        (url_path_join(base_url, "git-lock-sign", "lock"), LockNotebookHandler),
        (url_path_join(base_url, "git-lock-sign", "unlock"), UnlockNotebookHandler),
        (url_path_join(base_url, "git-lock-sign", "commit"), CommitNotebookHandler),
        (url_path_join(base_url, "git-lock-sign", "user-info"), UserInfoHandler),
        (url_path_join(base_url, "git-lock-sign", "provision"), ProvisionRepositoryHandler),
        (url_path_join(base_url, "git-lock-sign", "push"), PushRepositoryHandler),
        (url_path_join(base_url, "git-lock-sign", "git-init"), GitInitHandler),
        (url_path_join(base_url, "git-lock-sign", "status"), StatusHandler),
        (url_path_join(base_url, "git-lock-sign", "config"), ConfigHandler),
        (url_path_join(base_url, "git-lock-sign", "file-lifecycle-commit"), FileLifecycleCommitHandler),
        # Session initialization handler - for workspace-level setup and sync
        (url_path_join(base_url, "git-lock-sign", "session-init"), SessionInitHandler),
    ]
    
    # Register each handler with the web app
    for pattern, handler_class in handlers:
        web_app.add_handlers(host_pattern, [(pattern, handler_class)])
        # Use print for startup visibility since logger might be filtered
        print(f"🔧 Registered git-lock-sign handler: {pattern}")
    
    # Log successful setup with print statements for visibility
    print(f"✅ Git-lock-sign extension setup complete. Base URL: {base_url}")
    print("🚀 CELN Extension: Using sidecar architecture for git operations")
    print("   Sidecar should be available at http://localhost:8001 (or the sidecar URL from the environment variables)")
    print("   Most git operations will be handled by the sidecar service")
    print(f"📊 Registered {len(handlers)} git-lock-sign handlers total")
    
    # Also log with logger for proper logging
    logger.info(f"Git-lock-sign extension setup complete. Base URL: {base_url}")
    logger.info("🚀 CELN Extension: Using sidecar architecture for git operations")
    logger.info(f"Registered {len(handlers)} git-lock-sign handlers total")
