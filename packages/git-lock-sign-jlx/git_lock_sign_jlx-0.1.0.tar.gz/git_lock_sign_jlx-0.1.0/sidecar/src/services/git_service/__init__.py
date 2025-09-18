"""
Git Service Package for CELN Sidecar

This package provides modular git operations for the JupyterLab extension.
It replaces the monolithic GitService with a more maintainable architecture.
"""

from .models import GitOperationResult, GitStatusResult, UserInfoResult, NotebookPushResult
from .core_service import GitCoreService
from .main_service import GitService

__all__ = [
    "GitOperationResult",
    "GitStatusResult", 
    "UserInfoResult",
    "GitCoreService",
    "GitService",
    "NotebookPushResult"
]

