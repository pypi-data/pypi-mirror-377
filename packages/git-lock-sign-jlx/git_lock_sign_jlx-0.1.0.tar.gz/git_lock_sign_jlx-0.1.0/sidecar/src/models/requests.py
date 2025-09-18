"""
Request models for CELN Sidecar API

Defines the data structures for all incoming API requests.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class GitInitRequest(BaseModel):
    """Request to initialize git repository."""

    notebook_path: str = Field(..., description="Path to the notebook file")


class CommitRequest(BaseModel):
    """Request to commit notebook changes."""

    notebook_path: str = Field(..., description="Path to the notebook file")
    commit_message: Optional[str] = Field(None, description="Custom commit message")
    auto_commit: bool = Field(False, description="Whether this is an automatic commit")
    cell_content_preview: Optional[str] = Field(
        None, description="Preview of executed cell content"
    )
    execution_count: Optional[int] = Field(None, description="Cell execution count")
    timestamp: Optional[str] = Field(None, description="Timestamp of the operation")
    notebook_content: Optional[Dict[str, Any]] = Field(
        None,
        description="Notebook content as JSON (optional, will be loaded from file if not provided)",
    )
    include_metadata: bool = Field(
        True, description="Whether to include git_lock_sign metadata in the commit"
    )


class PushRequest(BaseModel):
    """Request to push changes to GitLab."""

    notebook_path: str = Field(..., description="Path to the notebook file")
    auto_push: bool = Field(False, description="Whether this is an automatic push")
    auto_commit_before_push: bool = Field(
        False,
        description="Whether to auto-commit any uncommitted changes before pushing",
    )


class LockRequest(BaseModel):
    """Request to lock a notebook."""

    notebook_path: str = Field(..., description="Path to the notebook file")
    notebook_content: Dict[str, Any] = Field(
        ..., description="Notebook content as JSON"
    )
    commit_message: str = Field(
        ..., description="Commit message for the lock operation"
    )


class UnlockRequest(BaseModel):
    """Request to unlock a notebook."""

    notebook_path: str = Field(..., description="Path to the notebook file")
    notebook_content: Dict[str, Any] = Field(
        ..., description="Notebook content as JSON"
    )


class FileLifecycleCommitRequest(BaseModel):
    """Request to commit file lifecycle events (creation/deletion/rename)."""
    
    file_path: str = Field(..., description="Path to the file")
    lifecycle_event: str = Field(..., description="Lifecycle event type: 'create', 'delete', or 'rename'")
    trigger_auto_push: bool = Field(False, description="Whether to trigger auto-push after commit")
    old_file_path: Optional[str] = Field(None, description="Path to the old file (for rename events)")


class StatusRequest(BaseModel):
    """Request to get repository and notebook status."""

    notebook_path: str = Field(..., description="Path to the notebook file")
