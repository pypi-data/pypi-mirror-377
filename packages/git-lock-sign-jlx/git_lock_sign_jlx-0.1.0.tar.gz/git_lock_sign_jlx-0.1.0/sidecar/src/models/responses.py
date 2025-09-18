"""
Response models for CELN Sidecar API

Defines the data structures for all API responses.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class GitInitResponse(BaseModel):
    """Response from git repository initialization."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    repository_path: Optional[str] = Field(
        None, description="Path to the git repository root"
    )
    repository_url: Optional[str] = Field(None, description="Git repository URL (GitLab/Gitea)")
    error: Optional[str] = Field(None, description="Error message if operation failed")



class CommitResponse(BaseModel):
    """Response from commit operation."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    commit_hash: Optional[str] = Field(None, description="Git commit hash")
    signed: bool = Field(False, description="Whether the commit was GPG signed")
    debounced: bool = Field(False, description="Whether the commit was debounced")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Metadata that was saved to the notebook"
    )
    content_hash: Optional[str] = Field(
        None, description="Hash of the notebook content"
    )
    error: Optional[str] = Field(None, description="Error message if operation failed")


class PushResponse(BaseModel):
    """Response from push operation."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    repository_url: Optional[str] = Field(None, description="GitLab repository URL")
    debounced: bool = Field(False, description="Whether the push was debounced")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class LockResponse(BaseModel):
    """Response from lock operation."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Lock metadata stored in notebook"
    )
    commit_hash: Optional[str] = Field(None, description="Git commit hash")
    signed: bool = Field(False, description="Whether the commit was GPG signed")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class UnlockResponse(BaseModel):
    """Response from unlock operation."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    signature_valid: bool = Field(False, description="Whether the signature was valid")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class StatusResponse(BaseModel):
    """Response from status check operation."""

    success: bool = Field(..., description="Whether the operation was successful")
    is_git_repository: bool = Field(
        ..., description="Whether the path is in a git repository"
    )
    is_locked: bool = Field(False, description="Whether the notebook is locked")
    repository_path: Optional[str] = Field(
        None, description="Path to the git repository root"
    )
    signature_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Signature metadata if locked"
    )
    last_commit_hash: Optional[str] = Field(None, description="Hash of the last commit")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class UserInfoResponse(BaseModel):
    """Response from user info request."""

    success: bool = Field(..., description="Whether the operation was successful")
    user_name: Optional[str] = Field(None, description="Git user name")
    user_email: Optional[str] = Field(None, description="Git user email")
    gpg_key_id: Optional[str] = Field(None, description="GPG key ID if available")
    error: Optional[str] = Field(None, description="Error message if operation failed")
