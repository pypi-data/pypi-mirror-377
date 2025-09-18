"""
Shared data types for git operations.

This module contains the common data structures used across all git services.
"""

from typing import Any, Dict, NamedTuple, Optional


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


class NotebookPushResult(NamedTuple):
    """Result of notebook push operation."""
    success: bool
    message: Optional[str] = None
    repository_url: Optional[str] = None
    error: Optional[str] = None
