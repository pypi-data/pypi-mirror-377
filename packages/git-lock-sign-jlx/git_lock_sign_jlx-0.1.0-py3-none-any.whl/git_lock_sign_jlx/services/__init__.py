"""
Services package for git-based notebook locking and signing.

Note: Git operations have been migrated to the sidecar service.
This package now only contains the sidecar client for API communication.
"""

from .sidecar_client import SidecarClient

# Legacy git services are deprecated - use sidecar_client instead
# from .git_service import GitService          # REMOVED - use sidecar
# from .gpg_service import GPGService          # REMOVED - use sidecar
# from .notebook_service import NotebookService # REMOVED - use sidecar
# from .user_service import UserService        # REMOVED - use sidecar

__all__ = ["SidecarClient"]
