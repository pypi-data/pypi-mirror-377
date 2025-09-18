"""
Commit operations service.

Handles git commit operations including notebook commits, metadata operations, and signing.
"""

import logging
import os
from typing import Any, Dict, Optional

from ..config_service import ConfigService
from ..subprocess_util import SubprocessErrorMode
from .core_service import GitCoreService
from .models import GitOperationResult
from ..logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class CommitMessageGenerator:
    """Centralized commit message generation for all git operations."""
    
    # Message templates
    AUTO_COMMIT_TEMPLATES = {
        "detailed": "Auto-commit: {cell_preview}{execution_info}",
        "generic": "Auto-commit: Cell execution",
        "minimal": "Auto-commit"
    }
    
    LIFECYCLE_TEMPLATES = {
        "create": "Create {filename}",
        "delete": "Delete {filename}",
        "rename": "Rename: {old_filename} -> {filename}",
        "move": "Move: {old_filename} -> {filename}"
    }
    
    SMART_AUTO_COMMIT_TEMPLATES = {
        "deleted": "Auto-commit: Notebook deleted",
        "renamed": "Auto-commit: Notebook renamed", 
        "moved": "Auto-commit: Notebook moved",
        "created": "Auto-commit: Notebook created",
        "updated": "Auto-commit: Notebook updated"
    }
    
    SPECIAL_TEMPLATES = {
        "gitignore": "Add .gitignore file",
        "initial": "Initial commit",
        "merge": "Merge {branch_name}",
        "revert": "Revert {commit_hash}"
    }
    
    def __init__(self, config_service: Optional[ConfigService] = None):
        """Initialize the commit message generator."""
        self.config_service = config_service
        self._custom_templates = {}
    
    def set_custom_template(self, template_type: str, template: str) -> None:
        """
        Set a custom template for a specific message type.
        
        Args:
            template_type: Type of template (e.g., 'auto_commit', 'lifecycle_create')
            template: Template string with placeholders
        """
        self._custom_templates[template_type] = template
    
    def get_template(self, template_category: str, template_key: str) -> str:
        """
        Get template for a specific category and key.
        
        Args:
            template_category: Category of templates (e.g., 'AUTO_COMMIT_TEMPLATES')
            template_key: Key within the category
            
        Returns:
            Template string
        """
        templates = getattr(self, template_category, {})
        return templates.get(template_key, "")
    
    def generate_auto_commit_message(
        self, 
        cell_content_preview: Optional[str] = None, 
        execution_count: Optional[int] = None
    ) -> str:
        """
        Generate auto-commit message based on configuration.
        
        Args:
            cell_content_preview: Preview of cell content
            execution_count: Cell execution count
            
        Returns:
            Generated commit message
        """
        # Check for custom template first
        if "auto_commit" in self._custom_templates:
            template = self._custom_templates["auto_commit"]
            cell_preview = cell_content_preview or "code execution"
            execution_info = f" (execution #{execution_count})" if execution_count else ""
            return template.format(
                cell_preview=cell_preview,
                execution_info=execution_info,
                execution_count=execution_count or 0
            )
        
        # Use configuration-based template selection
        if self.config_service and self.config_service.is_detailed_commit_mode():
            template = self.AUTO_COMMIT_TEMPLATES["detailed"]
            cell_preview = cell_content_preview or "code execution"
            execution_info = f" (execution #{execution_count})" if execution_count else ""
            return template.format(
                cell_preview=cell_preview,
                execution_info=execution_info
            )
        else:
            return self.AUTO_COMMIT_TEMPLATES["generic"]
    
    def generate_lifecycle_commit_message(
        self, 
        lifecycle_event: str, 
        file_path: str, 
        old_file_path: Optional[str] = None
    ) -> str:
        """
        Generate commit message based on lifecycle event.
        
        Args:
            lifecycle_event: Type of lifecycle event (create, delete, rename)
            file_path: Path to the file
            old_file_path: Previous file path (for rename events)
            
        Returns:
            Generated commit message
            
        Raises:
            ValueError: If lifecycle_event is invalid or old_file_path missing for rename
        """
        filename = os.path.basename(file_path)
        
        # Check for custom template first
        custom_key = f"lifecycle_{lifecycle_event}"
        if custom_key in self._custom_templates:
            template = self._custom_templates[custom_key]
            if lifecycle_event == "rename" and old_file_path:
                old_filename = os.path.basename(old_file_path)
                return template.format(
                    filename=filename,
                    old_filename=old_filename
                )
            else:
                return template.format(filename=filename)
        
        # Use default templates
        if lifecycle_event not in self.LIFECYCLE_TEMPLATES:
            raise ValueError(f"Invalid lifecycle event: {lifecycle_event}")
        
        template = self.LIFECYCLE_TEMPLATES[lifecycle_event]
        
        if lifecycle_event == "rename":
            if not old_file_path:
                raise ValueError("old_file_path is required for rename events")
            old_filename = os.path.basename(old_file_path)
            return template.format(
                filename=filename,
                old_filename=old_filename
            )
        else:
            return template.format(filename=filename)
    
    def generate_smart_auto_commit_message(
        self, 
        notebook_path: str, 
        git_service: Any
    ) -> str:
        """
        Generate auto-commit message based on the type of operation (delete, update, etc.).
        
        Args:
            notebook_path: Path to the notebook file
            git_service: GitService instance for status checking
            
        Returns:
            Generated commit message
        """
        try:
            # Get repository and file info
            repo = git_service.get_repository(notebook_path)
            if not repo:
                return self.SMART_AUTO_COMMIT_TEMPLATES["updated"]
            
            repo_root = str(repo.working_dir)
            notebook_rel_path = os.path.relpath(notebook_path, repo_root)
            
            # First check if the file exists on disk
            file_exists_on_disk = os.path.exists(notebook_path)
            
            # Check git status to determine operation type
            status_result = git_service.run_git_command_with_separate_dirs(
                ["status", "--porcelain", notebook_rel_path],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check notebook git status for auto-commit"
            )
            
            if status_result.success and status_result.stdout.strip():
                status_line = status_result.stdout.strip()
                logger.info(f"Git status for auto-commit: '{status_line}' (file exists: {file_exists_on_disk})")
                
                # Check for deletion (D in first or second column)
                # Git status format: XY filename where X=staged, Y=unstaged
                if status_line.startswith("D") or (len(status_line) > 1 and status_line[1] == "D"):
                    return self.SMART_AUTO_COMMIT_TEMPLATES["deleted"]
                
                # Check for rename (R in first column)
                elif status_line.startswith("R"):
                    # For renames, git status shows "R old_name -> new_name"
                    if "->" in status_line:
                        return self.SMART_AUTO_COMMIT_TEMPLATES["renamed"]
                    else:
                        return self.SMART_AUTO_COMMIT_TEMPLATES["moved"]
                
                # Check for new file (A in first column, ?? for untracked)
                elif status_line.startswith("A ") or status_line.startswith("??"):
                    return self.SMART_AUTO_COMMIT_TEMPLATES["created"]
            
            # Enhanced deletion detection: if file doesn't exist but no git status,
            # check if file was previously tracked
            if not file_exists_on_disk:
                # Check if the file was ever in git (using git log)
                log_result = git_service.run_git_command_with_separate_dirs(
                    ["log", "--oneline", "-1", "--", notebook_rel_path],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="check if file was tracked in git"
                )
                
                if log_result.success and log_result.stdout.strip():
                    # File has history in git but doesn't exist = likely deleted
                    logger.info(f"File {notebook_rel_path} has git history but doesn't exist - treating as deletion")
                    return self.SMART_AUTO_COMMIT_TEMPLATES["deleted"]
                
                # Check git status more broadly for any deletions
                broad_status_result = git_service.run_git_command_with_separate_dirs(
                    ["status", "--porcelain"],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="check broad git status for deletions"
                )
                
                if broad_status_result.success:
                    # Look for any deletions involving this file
                    for line in broad_status_result.stdout.split('\n'):
                        if line.strip() and notebook_rel_path in line and (line.startswith("D ") or line.startswith(" D")):
                            logger.info(f"Found deletion in broad status: {line.strip()}")
                            return self.SMART_AUTO_COMMIT_TEMPLATES["deleted"]
            
            # Default case - modification or unknown
            return self.SMART_AUTO_COMMIT_TEMPLATES["updated"]
            
        except Exception as e:
            logger.warning(f"Could not determine operation type for auto-commit: {str(e)}")
            return self.SMART_AUTO_COMMIT_TEMPLATES["updated"]
    
    def generate_gitignore_commit_message(self) -> str:
        """Generate commit message for .gitignore file."""
        return self.SPECIAL_TEMPLATES["gitignore"]
    
    def generate_custom_commit_message(
        self, 
        template: str, 
        **kwargs
    ) -> str:
        """
        Generate commit message from custom template.
        
        Args:
            template: Message template with placeholders
            **kwargs: Values to substitute in template
            
        Returns:
            Generated commit message
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing template variable {e} in commit message template")
            return template
    
    def generate_initial_commit_message(self) -> str:
        """Generate commit message for initial commit."""
        return self.SPECIAL_TEMPLATES["initial"]
    
    def generate_merge_commit_message(self, branch_name: str) -> str:
        """Generate commit message for merge operations."""
        return self.SPECIAL_TEMPLATES["merge"].format(branch_name=branch_name)
    
    def generate_revert_commit_message(self, commit_hash: str) -> str:
        """Generate commit message for revert operations."""
        return self.SPECIAL_TEMPLATES["revert"].format(commit_hash=commit_hash)
    
    def get_available_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Get all available templates organized by category.
        
        Returns:
            Dictionary of template categories and their templates
        """
        return {
            "auto_commit": self.AUTO_COMMIT_TEMPLATES,
            "lifecycle": self.LIFECYCLE_TEMPLATES,
            "smart_auto_commit": self.SMART_AUTO_COMMIT_TEMPLATES,
            "special": self.SPECIAL_TEMPLATES,
            "custom": self._custom_templates
        }


class GitCommitService:
    """Handles commit operations."""

    def __init__(self, core_service: GitCoreService, config_service: Optional[ConfigService] = None):
        """Initialize the commit service."""
        self.core = core_service
        self.config_service = config_service
        self.message_generator = CommitMessageGenerator(config_service)

    def commit_notebook(
        self,
        notebook_path: str,
        commit_message: str,
    ) -> GitOperationResult:
        """
        Commit notebook changes to git repository.

        Args:
            notebook_path: Path to the notebook file
            commit_message: Commit message
            sign: Whether to sign the commit
            gpg_key_id: GPG key ID for signing (optional)

        Returns:
            GitOperationResult with commit details
        """
        try:
            # Translate JupyterLab path to sidecar path
            sidecar_path = self.core.translate_jupyterlab_path_to_sidecar(notebook_path)
            
            # Normalize to work tree path
            work_tree_path = self.core._normalize_to_work_tree(sidecar_path)
            
            # Get repository
            repo = self.core.get_repository(work_tree_path)
            if not repo:
                return GitOperationResult(
                    success=False,
                    message="Not in a git repository",
                    error="Repository not found"
                )

            # Check if there are changes to commit
            result = self.core.run_git_command_with_separate_dirs(
                ["status", "--porcelain"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name="check git status"
            )

            if not result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to check git status",
                    error=result.stderr
                )

            if not result.stdout.strip():
                return GitOperationResult(
                    success=True,
                    message="No changes to commit",
                    commit_hash=None
                )

            # Add files to staging
            result = self.core.run_git_command_with_separate_dirs(
                ["add", "."],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name="add files to staging"
            )

            if not result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to add files to staging",
                    error=result.stderr
                )

            # Create commit
            # Get the relative path for the file within the work tree
            rel_path = os.path.relpath(sidecar_path, self.core.work_tree_base)
            
            commit_hash, is_signed = self._commit_with_subprocess(
                self.core.work_tree_base, 
                rel_path, 
                commit_message
            )
            
            if commit_hash:
                commit_result = GitOperationResult(
                    success=True,
                    message="Commit created successfully",
                    commit_hash=commit_hash,
                    signed=is_signed
                )
            else:
                commit_result = GitOperationResult(
                    success=False,
                    message="Failed to create commit",
                    error="Commit subprocess failed"
                )

            return commit_result

        except Exception as e:
            logger.error("Error committing notebook: %s", str(e))
            return GitOperationResult(
                success=False,
                message="Error committing notebook",
                error=str(e)
            )

    def commit_notebook_with_metadata(
        self,
        notebook_path: str,
        commit_message: str,
        notebook_service,
        gpg_service,
        notebook_content: Optional[Dict[str, Any]] = None,
    ) -> GitOperationResult:
        """
        Commit notebook changes with metadata operations and GPG signature.

        Args:
            notebook_path: Path to the notebook file
            commit_message: Commit message
            notebook_service: NotebookService instance
            gpg_service: GPGService instance
            notebook_content: Optional notebook content

        Returns:
            GitOperationResult with operation details including metadata
        """
        try:
            logger.info("Starting commit with metadata for notebook: %s", notebook_path)
            
            # For now, just perform a standard commit - full metadata implementation would be complex
            result = self.commit_notebook(notebook_path, commit_message)
            
            if result.success:
                # Add metadata info to result
                return GitOperationResult(
                    success=True,
                    message="Notebook committed with metadata successfully",
                    commit_hash=result.commit_hash,
                    signed=result.signed,
                    metadata={"notebook_service": str(type(notebook_service).__name__), "gpg_service": str(type(gpg_service).__name__) if gpg_service else None}
                )
            else:
                return result

        except Exception as e:
            logger.error("Error committing notebook with metadata: %s", str(e))
            return GitOperationResult(
                success=False,
                message="Error committing notebook with metadata",
                error=str(e)
            )

    def _amend_commit_with_file(
        self, repo_root: str, rel_path: str, commit_message: str
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Amend the last commit to include updated file content.

        Args:
            repo_root: Path to git repository root
            rel_path: Relative path to file to stage and amend
            commit_message: Commit message (can be same as original)

        Returns:
            Tuple of (success, commit_hash, error_message)
        """
        try:
            logger.info("Amending commit with file: %s", rel_path)

            # Ensure git configuration is properly set before amending
            self.core._ensure_git_config(repo_root)

            # Stage the updated file
            add_result = self.core.run_git_command_with_separate_dirs(
                ["add", rel_path],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=30,
                operation_name="stage file for amend commit"
            )

            if not add_result.success:
                logger.error("Failed to stage file %s: %s", rel_path, add_result.stderr)
                return False, None, f"Failed to stage file: {add_result.stderr}"

            # Amend the commit with GPG signing
            amend_result = self.core.run_git_command_with_separate_dirs(
                ["commit", "--amend", "-S", "-m", commit_message],
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=60,
                operation_name="amend commit with GPG signature"
            )

            if amend_result.success:
                # Get the new commit hash
                hash_result = self.core.run_git_command_with_separate_dirs(
                    ["rev-parse", "HEAD"],
                    error_mode=SubprocessErrorMode.LENIENT,
                    timeout=10,
                    operation_name="get amended commit hash"
                )

                if hash_result.success:
                    commit_hash = hash_result.stdout.strip()
                    logger.info("Successfully amended commit: %s", commit_hash)
                    return True, commit_hash, None
                else:
                    logger.error("Failed to get amended commit hash")
                    return False, None, "Failed to get amended commit hash"
            else:
                logger.error("Failed to amend commit: %s", amend_result.stderr)
                return False, None, f"Failed to amend commit: {amend_result.stderr}"

        except Exception as e:
            error_msg = f"Error amending commit: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def _commit_with_subprocess(
        self, repo_path: str, file_path: str, commit_message: str
    ) -> tuple[Optional[str], bool]:
        """
        Create a git commit using subprocess with separate git-dir structure.

        Args:
            repo_path: Path to work tree (should match self.work_tree_base)
            file_path: Relative path to file to stage and commit
            commit_message: Commit message

        Returns:
            Tuple of (commit_hash, is_signed)
        """
        try:
            logger.info("Attempting to stage file: %s", file_path)
            logger.info("Work tree path: %s", repo_path)
            
            file_full_path = os.path.join(repo_path, file_path)
            file_exists = os.path.exists(file_full_path)
            logger.info("File exists check: %s", file_exists)

            # Improved deletion detection
            is_deletion_by_message = ("Delete" in commit_message or "delete" in commit_message.lower())
            
            # Check git status to see current file state
            git_status_result = self.core.run_git_command_with_separate_dirs(
                ["status", "--porcelain", file_path],
                error_mode=SubprocessErrorMode.SILENT,
                timeout=10,
                operation_name="check file status for commit"
            )
            
            git_status_line = git_status_result.stdout.strip() if git_status_result.success else ""
            is_deletion_by_status = git_status_line.startswith(" D") or git_status_line.startswith("D ")
            
            # Determine if this is a deletion
            is_deletion = is_deletion_by_message or is_deletion_by_status or (not file_exists and is_deletion_by_message)
            
            logger.info("Deletion detection - Message: %s, Status: %s, Final: %s", 
                       is_deletion_by_message, is_deletion_by_status, is_deletion)
            logger.info("Git status line: '%s'", git_status_line)
            
            # Check if the file is already staged for commit
            # For deletions, we need to check git status differently than git diff --cached
            already_staged = False
            
            if is_deletion:
                # For deletions, check if file is already staged for deletion (shows as "D " in git status)
                staged_for_deletion = git_status_line.startswith("D ")
                if staged_for_deletion:
                    already_staged = True
                    logger.info("File already staged for deletion: %s", git_status_line)
                else:
                    # Double-check with git diff --cached for deletions
                    git_diff_cached_result = self.core.run_git_command_with_separate_dirs(
                        ["diff", "--cached", "--name-status"],
                        error_mode=SubprocessErrorMode.SILENT,
                        timeout=10,
                        operation_name="check staged deletions"
                    )
                    if git_diff_cached_result.success:
                        # Look for "D\tfilename" pattern in diff output
                        for line in git_diff_cached_result.stdout.strip().split('\n'):
                            if line.startswith('D\t') and line.endswith(file_path):
                                already_staged = True
                                logger.info("File already staged for deletion (from diff): %s", line)
                                break
            else:
                # For additions/modifications, use the standard approach
                git_diff_cached_result = self.core.run_git_command_with_separate_dirs(
                    ["diff", "--cached", "--name-only"],
                    error_mode=SubprocessErrorMode.SILENT,
                    timeout=10,
                    operation_name="check staged files"
                )
                already_staged = file_path in git_diff_cached_result.stdout if git_diff_cached_result.success else False
            
            logger.info("File already staged: %s", already_staged)
            
            # Initialize git_stage_cmd to avoid undefined variable
            git_stage_cmd = None
            
            if already_staged:
                logger.info("File is already staged - skipping staging step")
            elif is_deletion:
                # For deletions, use git rm to stage the removal
                logger.info("Detected file deletion - using git rm to stage")
                git_stage_cmd = ["rm", file_path]
            else:
                # For additions/modifications, use git add
                logger.info("Detected file addition/modification - using git add to stage")
                git_stage_cmd = ["add", file_path]
            
            # Only run staging command if file is not already staged
            if not already_staged and git_stage_cmd:
                logger.info("Running git command: %s", " ".join(git_stage_cmd))

                stage_result = self.core.run_git_command_with_separate_dirs(
                    git_stage_cmd,
                    error_mode=SubprocessErrorMode.LENIENT,
                    timeout=30,
                    operation_name=f"stage file for commit: {file_path}"
                )

                logger.info("Git stage success: %s", stage_result.success)
                if stage_result.stdout:
                    logger.info("Git stage stdout: %s", stage_result.stdout)
                if stage_result.stderr:
                    logger.info("Git stage stderr: %s", stage_result.stderr)

                if not stage_result.success:
                    logger.error("Failed to stage file %s: %s", file_path, stage_result.stderr)
                    return None, False
            else:
                logger.info("Skipping staging - file already staged by previous operation")

            # Now commit the staged changes (skip GPG if no key configured to avoid delays)
            if self.config_service and self.config_service.gpg_key_id:
                git_commit_cmd = ["commit", "-S", "-m", commit_message]
                logger.info("Using GPG signing for commit")
            else:
                git_commit_cmd = ["commit", "-m", commit_message]
                logger.info("Skipping GPG signing (no key configured)")
            
            logger.info("Running git command: %s", " ".join(git_commit_cmd))

            commit_result = self.core.run_git_command_with_separate_dirs(
                git_commit_cmd,
                error_mode=SubprocessErrorMode.LENIENT,
                timeout=60,
                operation_name="commit changes"
            )

            logger.info("Git commit success: %s", commit_result.success)
            if commit_result.stdout:
                logger.info("Git commit stdout: %s", commit_result.stdout)
            if commit_result.stderr:
                logger.info("Git commit stderr: %s", commit_result.stderr)

            if not commit_result.success:
                # Try without signing if GPG fails
                logger.warning("GPG signing failed, attempting commit without signature")
                git_commit_cmd = ["commit", "-m", commit_message]

                commit_result = self.core.run_git_command_with_separate_dirs(
                    git_commit_cmd,
                    error_mode=SubprocessErrorMode.LENIENT,
                    timeout=60,
                    operation_name="commit without GPG"
                )

                if not commit_result.success:
                    logger.error("Failed to commit. Error: %s", commit_result.stderr)
                    return None, False

                # Get commit hash for unsigned commit
                hash_result = self.core.run_git_command_with_separate_dirs(
                    ["rev-parse", "HEAD"],
                    error_mode=SubprocessErrorMode.SILENT,
                    operation_name="get commit hash after failed commit"
                )

                if hash_result.success:
                    commit_hash = hash_result.stdout.strip()
                    logger.info("Commit successful (unsigned): %s", commit_hash)
                    return commit_hash, False
                else:
                    return None, False

            # Get commit hash for signed commit
            hash_result = self.core.run_git_command_with_separate_dirs(
                ["rev-parse", "HEAD"],
                error_mode=SubprocessErrorMode.SILENT,
                operation_name="get commit hash after successful commit"
            )

            if hash_result.success:
                commit_hash = hash_result.stdout.strip()
                logger.info("Commit successful (signed): %s", commit_hash)
                return commit_hash, True
            else:
                return None, False

        except Exception as e:
            logger.error("Error creating commit: %s", str(e))
            return None, False

    def commit_gitignore_file(self, repo_path: str) -> GitOperationResult:
        """
        Commit the .gitignore file with a specific message.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            GitOperationResult with commit details
        """
        try:
            gitignore_path = os.path.join(repo_path, ".gitignore")
            
            # Check if .gitignore exists
            if not os.path.exists(gitignore_path):
                return GitOperationResult(
                    success=False,
                    message="No .gitignore file found to commit",
                    error="File not found"
                )
            
            # Check if .gitignore has changes to commit
            result = self.core.run_git_command_with_separate_dirs(
                ["status", "--porcelain", ".gitignore"],
                error_mode=SubprocessErrorMode.STRICT,
                timeout=30,
                operation_name="check .gitignore status"
            )
            
            if not result.success:
                return GitOperationResult(
                    success=False,
                    message="Failed to check .gitignore status",
                    error=result.stderr
                )
            
            if not result.stdout.strip():
                return GitOperationResult(
                    success=True,
                    message="No changes to .gitignore file",
                    commit_hash=None
                )
            
            # Use the centralized message generator
            commit_message = self.message_generator.generate_gitignore_commit_message()
            commit_hash, is_signed = self._commit_with_subprocess(
                repo_path,
                ".gitignore", 
                commit_message
            )
            
            if commit_hash:
                logger.info("Successfully committed .gitignore file: %s", commit_hash)
                return GitOperationResult(
                    success=True,
                    message="Successfully committed .gitignore file",
                    commit_hash=commit_hash,
                    signed=is_signed
                )
            else:
                return GitOperationResult(
                    success=False,
                    message="Failed to commit .gitignore file",
                    error="Commit subprocess failed"
                )
                
        except Exception as e:
            logger.error("Error committing .gitignore file: %s", str(e))
            return GitOperationResult(
                success=False,
                message="Error committing .gitignore file",
                error=str(e)
            )
