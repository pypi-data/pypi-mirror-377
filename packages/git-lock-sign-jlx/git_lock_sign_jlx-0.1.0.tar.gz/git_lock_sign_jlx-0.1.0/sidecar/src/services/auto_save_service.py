"""
Auto-save service for CELN Sidecar

Handles periodic auto-saving of notebooks and triggering of push operations.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Set

from .config_service import ConfigService
from .logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class AutoSaveService:
    """Service for automatic periodic notebook saving and pushing."""

    def __init__(self, config_service: ConfigService):
        """
        Initialize the auto-save service.

        Args:
            config_service: Configuration service instance
        """
        self.config = config_service
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._watched_notebooks: Set[str] = set()
        logger.info(
            f"Auto-save service initialized (interval: {self.config.auto_save_interval_minutes}min)"
        )

    async def start(self) -> None:
        """Start the auto-save service."""
        if self._running:
            logger.warning("Auto-save service is already running")
            return

        if not self.config.auto_save_enabled:
            logger.info("Auto-save is disabled in configuration")
            return

        self._running = True
        self._task = asyncio.create_task(self._auto_save_loop())
        logger.info("Auto-save service started")

    async def stop(self) -> None:
        """Stop the auto-save service."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("Auto-save service stopped")

    def add_notebook(self, notebook_path: str) -> None:
        """
        Add a notebook to the auto-save watch list.

        Args:
            notebook_path: Path to the notebook file
        """
        abs_path = os.path.abspath(notebook_path)
        self._watched_notebooks.add(abs_path)
        logger.debug(f"Added notebook to auto-save watch: {abs_path}")

    def remove_notebook(self, notebook_path: str) -> None:
        """
        Remove a notebook from the auto-save watch list.

        Args:
            notebook_path: Path to the notebook file
        """
        abs_path = os.path.abspath(notebook_path)
        self._watched_notebooks.discard(abs_path)
        logger.debug(f"Removed notebook from auto-save watch: {abs_path}")

    def clear_notebooks(self) -> None:
        """Clear all notebooks from the auto-save watch list."""
        self._watched_notebooks.clear()
        logger.debug("Cleared all notebooks from auto-save watch")

    async def _auto_save_loop(self) -> None:
        """Main auto-save loop that runs periodically."""
        logger.info(
            f"Starting auto-save loop (interval: {self.config.auto_save_interval_seconds}s)"
        )

        while self._running:
            try:
                await asyncio.sleep(self.config.auto_save_interval_seconds)

                if not self._running:
                    break

                await self._perform_auto_save()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-save loop: {str(e)}")
                # Continue running even if there's an error
                await asyncio.sleep(10)  # Wait a bit before retrying

    async def _perform_auto_save(self) -> None:
        """Perform auto-save for all watched notebooks."""
        if not self._watched_notebooks:
            logger.debug("No notebooks to auto-save")
            return

        logger.info(
            f"Performing auto-save for {len(self._watched_notebooks)} notebooks"
        )

        # Discover all notebooks in the notebook root if no specific notebooks are watched
        notebooks_to_save = self._watched_notebooks.copy()

        if not notebooks_to_save:
            notebooks_to_save = self._discover_notebooks()

        for notebook_path in notebooks_to_save:
            try:
                await self._auto_save_notebook(notebook_path)
            except Exception as e:
                logger.error(f"Failed to auto-save {notebook_path}: {str(e)}")

    async def _auto_save_notebook(self, notebook_path: str) -> None:
        """
        Auto-save a specific notebook.

        Args:
            notebook_path: Path to the notebook file
        """
        # Check if the notebook file exists and has been modified
        if not os.path.exists(notebook_path):
            logger.debug(
                f"Notebook no longer exists, removing from watch: {notebook_path}"
            )
            self.remove_notebook(notebook_path)
            return

        # Check if the notebook is in a git repository
        if not self._is_in_git_repo(notebook_path):
            logger.debug(
                f"Notebook not in git repo, skipping auto-save: {notebook_path}"
            )
            return

        # Check if the notebook has been modified recently
        if not self._has_recent_changes(notebook_path):
            logger.debug(f"No recent changes, skipping auto-save: {notebook_path}")
            return

        logger.info(f"Auto-saving and pushing notebook: {notebook_path}")

        try:
            # First save the notebook (this would typically be done by JupyterLab)
            # For now, we'll just trigger a push since the notebook should already be saved
            await self._trigger_auto_push(notebook_path)

        except Exception as e:
            logger.error(f"Auto-save failed for {notebook_path}: {str(e)}")

    async def _trigger_auto_push(self, notebook_path: str) -> None:
        """
        Trigger an auto-push for a notebook.

        This would typically make an API call to the push endpoint.
        For now, we'll log the action.

        Args:
            notebook_path: Path to the notebook file
        """
        # TODO: Make actual API call to the push endpoint
        # For now, just log the action
        logger.info(f"Triggering auto-push for: {notebook_path}")

        # In a real implementation, this would be:
        # await self._make_push_request(notebook_path, auto_push=True)

    def _discover_notebooks(self) -> Set[str]:
        """
        Discover notebooks - now only returns explicitly watched notebooks.

        Auto-discovery has been removed since notebook_root is no longer used.
        Notebooks are added to the watch list when the frontend makes API calls.

        Returns:
            Set of notebook file paths that have been explicitly added
        """
        return self._watched_notebooks.copy()

    def _is_in_git_repo(self, notebook_path: str) -> bool:
        """
        Check if a notebook is in a git repository.

        Args:
            notebook_path: Path to the notebook file

        Returns:
            True if the notebook is in a git repository
        """
        try:
            # Walk up the directory tree looking for .git
            path = Path(notebook_path).parent
            while path != path.parent:
                if (path / ".git").exists():
                    return True
                path = path.parent
            return False
        except Exception:
            return False

    def _has_recent_changes(self, notebook_path: str) -> bool:
        """
        Check if a notebook has been modified recently.

        Args:
            notebook_path: Path to the notebook file

        Returns:
            True if the notebook has recent changes
        """
        try:
            # For now, assume all notebooks have recent changes
            # In a real implementation, this could check:
            # - File modification time
            # - Git status (uncommitted changes)
            # - Last push time vs modification time
            return True
        except Exception:
            return False

    def get_status(self) -> dict:
        """
        Get current auto-save service status.

        Returns:
            Dictionary with service status information
        """
        return {
            "running": self._running,
            "enabled": self.config.auto_save_enabled,
            "interval_minutes": self.config.auto_save_interval_minutes,
            "watched_notebooks": len(self._watched_notebooks),
            "notebook_paths": list(self._watched_notebooks),
        }
