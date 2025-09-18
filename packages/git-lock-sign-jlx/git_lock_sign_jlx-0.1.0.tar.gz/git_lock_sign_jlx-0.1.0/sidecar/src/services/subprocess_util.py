"""
Subprocess utility module for CELN Sidecar

Provides consistent subprocess execution with flexible error handling across all services.
This module centralizes subprocess operations to ensure consistent error handling,
logging, and timeout management throughout the codebase.
"""

import logging
import os
import subprocess
from enum import Enum
from typing import Dict, List, NamedTuple, Optional, Union

from .logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class SubprocessErrorMode(Enum):
    """Error handling modes for subprocess operations."""
    STRICT = "strict"      # Raise exceptions on non-zero exit codes (critical operations)
    LENIENT = "lenient"    # Return error info but don't raise (optional operations) 
    SILENT = "silent"      # Log minimal info (status checks, informational)


class SubprocessResult(NamedTuple):
    """Result of a subprocess operation."""
    success: bool
    returncode: int
    stdout: str
    stderr: str
    command: str
    error_message: Optional[str] = None


def run_subprocess(
    command: Union[List[str], str],
    cwd: Optional[str] = None,
    error_mode: SubprocessErrorMode = SubprocessErrorMode.STRICT,
    timeout: Optional[float] = 30,
    env: Optional[Dict[str, str]] = None,
    input_data: Optional[str] = None,
    capture_output: bool = True,
    text: bool = True,
    operation_name: Optional[str] = None
) -> SubprocessResult:
    """
    Flexible subprocess wrapper with consistent error handling.
    
    This function provides a unified interface for all subprocess operations
    across the CELN Sidecar services, ensuring consistent error handling,
    logging, and timeout management.
    
    Args:
        command: Command to execute (list of strings or single string)
        cwd: Working directory for command execution
        error_mode: How to handle errors (STRICT, LENIENT, or SILENT)
        timeout: Command timeout in seconds (None for no timeout)
        env: Environment variables (merged with os.environ if provided)
        input_data: Data to send to stdin
        capture_output: Whether to capture stdout/stderr
        text: Whether to use text mode (vs binary)
        operation_name: Human-readable name for logging (e.g., "git config setup")
        
    Returns:
        SubprocessResult with success status, output, and error information
        
    Raises:
        subprocess.TimeoutExpired: If timeout is exceeded (in all modes)
        subprocess.CalledProcessError: If command fails and error_mode is STRICT
        OSError: If command cannot be found/executed (in all modes)
        
    Error Modes:
        STRICT: For critical operations (git config, auth setup)
            - Raises CalledProcessError on failure
            - Full error logging with command details
            - Use when failure should stop the workflow
            
        LENIENT: For optional operations (safe directory setup, SSL config)
            - Returns error info but doesn't raise exceptions
            - Warning-level logging for failures
            - Use when failure should be logged but workflow continues
            
        SILENT: For informational operations (status checks)
            - Minimal debug-level logging
            - Graceful error handling
            - Use when failure is expected/common
    
    Examples:
        # Critical git configuration - will raise exception on failure
        result = run_subprocess(
            ["git", "config", "--local", "user.name", username],
            cwd=repo_path,
            error_mode=SubprocessErrorMode.STRICT,
            operation_name="configure git user"
        )
        
        # Optional setup - logs warning but continues on failure  
        result = run_subprocess(
            ["git", "config", "--global", "--add", "safe.directory", path],
            error_mode=SubprocessErrorMode.LENIENT,
            operation_name="configure safe directory"
        )
        if not result.success:
            logger.warning("Safe directory setup failed: %s", result.error_message)
            
        # Status check - minimal logging
        result = run_subprocess(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            error_mode=SubprocessErrorMode.SILENT,
            operation_name="check git status"
        )
        if result.success:
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
    """
    # Convert command to list if it's a string
    if isinstance(command, str):
        command = command.split()
    
    # Prepare environment
    final_env = os.environ.copy()
    if env:
        final_env.update(env)
    
    # Create a display name for logging
    cmd_display = " ".join(command) if isinstance(command, list) else str(command)
    op_name = operation_name or "subprocess command"
    
    # Log command execution based on error mode
    if error_mode == SubprocessErrorMode.SILENT:
        logger.debug("[%s] Executing: %s", op_name, cmd_display)
    else:
        cwd_info = f" (cwd: {cwd})" if cwd else ""
        logger.info("[%s] Executing: %s%s", op_name, cmd_display, cwd_info)
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=final_env,
            input=input_data,
            capture_output=capture_output,
            text=text,
            timeout=timeout,
            check=False  # We'll handle return codes ourselves
        )
        
        # Determine success based on return code
        success = result.returncode == 0
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        
        # Log results based on error mode and success
        if success:
            if error_mode != SubprocessErrorMode.SILENT:
                logger.info("[%s] ✅ Command succeeded (exit code: %d)", op_name, result.returncode)
                if stdout.strip() and error_mode == SubprocessErrorMode.STRICT:
                    logger.debug("[%s] stdout: %s", op_name, stdout.strip())
        else:
            error_msg = f"Command failed with exit code {result.returncode}"
            if stderr.strip():
                error_msg += f": {stderr.strip()}"
            elif stdout.strip():
                error_msg += f": {stdout.strip()}"
            
            # Handle errors based on mode
            if error_mode == SubprocessErrorMode.STRICT:
                logger.error("[%s] ❌ %s", op_name, error_msg)
                logger.error("[%s] Command: %s", op_name, cmd_display)
                # Create CalledProcessError for consistency with subprocess.run(check=True)
                raise subprocess.CalledProcessError(result.returncode, command, stdout, stderr)
            elif error_mode == SubprocessErrorMode.LENIENT:
                logger.warning("[%s] ⚠️ %s", op_name, error_msg)
            else:  # SILENT
                logger.debug("[%s] Command failed: %s", op_name, error_msg)
        
        return SubprocessResult(
            success=success,
            returncode=result.returncode,
            stdout=stdout,
            stderr=stderr,
            command=cmd_display,
            error_message=error_msg if not success else None
        )
        
    except subprocess.TimeoutExpired:
        logger.error("[%s] ⏰ Command timed out after %ss: %s", op_name, timeout, cmd_display)
        # Always re-raise timeout errors regardless of mode
        raise
        
    except OSError as e:
        logger.error("[%s] 💥 Command execution failed: %s: %s", op_name, str(e), cmd_display)
        # Always re-raise OS errors (command not found, etc.)
        raise


def run_git_command(
    git_args: List[str],
    cwd: Optional[str] = None,
    error_mode: SubprocessErrorMode = SubprocessErrorMode.STRICT,
    timeout: Optional[float] = 30,
    env: Optional[Dict[str, str]] = None,
    operation_name: Optional[str] = None
) -> SubprocessResult:
    """
    Convenience wrapper for git commands.
    
    Args:
        git_args: Git command arguments (without 'git' prefix)
        cwd: Working directory for git command execution
        error_mode: How to handle errors (STRICT, LENIENT, or SILENT)
        timeout: Command timeout in seconds
        env: Environment variables
        operation_name: Human-readable name for logging
        
    Returns:
        SubprocessResult with command execution details
        
    Examples:
        # Configure git user
        result = run_git_command(
            ["config", "--local", "user.name", "username"],
            cwd=repo_path,
            operation_name="configure git user"
        )
        
        # Check git status
        result = run_git_command(
            ["status", "--porcelain"],
            cwd=repo_path,
            error_mode=SubprocessErrorMode.SILENT,
            operation_name="check repository status"
        )
    """
    command = ["git"] + git_args
    git_operation = operation_name or f"git {git_args[0] if git_args else 'command'}"
    
    return run_subprocess(
        command=command,
        cwd=cwd,
        error_mode=error_mode,
        timeout=timeout,
        env=env,
        operation_name=git_operation
    )
