"""Client for communicating with the sidecar service."""

import asyncio
import logging
import os
from typing import Any, Dict, Optional, Tuple

import aiohttp

from git_lock_sign_jlx.backend_logger_util import backend_default_logger_config

logger = logging.getLogger(__name__)
backend_default_logger_config(logger)


class SidecarClient:
    """Client for communicating with the sidecar service API."""

    def __init__(self):
        """Initialize the sidecar client."""
        self.base_url = self._build_sidecar_url()
        logger.info(f"Using sidecar url: {self.base_url}")
        self.timeout = aiohttp.ClientTimeout(total=30)

    def _build_sidecar_url(self) -> str:
        """Build sidecar URL from environment variables with proper substitution."""
        host = os.getenv("SIDECAR_HOST", "localhost")
        port = os.getenv("SIDECAR_PORT", "8001")

        # Check if we're running in Docker by looking for Docker-specific hostname
        # or if a specific sidecar service name is provided
        docker_sidecar_host = os.getenv("SIDECAR_SERVICE_NAME")
        
        if docker_sidecar_host:
            host = docker_sidecar_host
        elif host == "0.0.0.0":
            # Try to detect if we're in Docker by checking if 'sidecar' hostname resolves
            import socket
            try:
                socket.gethostbyname("sidecar")
                host = "sidecar"  # Use Docker service name
            except socket.gaierror:
                host = "localhost"  # Fall back to localhost for local development

        fallback_url = f"http://{host}:{port}"
        return fallback_url

    async def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Make an HTTP request to the sidecar API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be prefixed with /sidecar)
            data: Request data (for POST requests)

        Returns:
            Tuple of (success, response_data, error_message)
        """
        # health endpoint is not prefixed with /sidecar
        url = f"{self.base_url}/sidecar{endpoint}" if endpoint!="/health" else f"{self.base_url}{endpoint}"
        logger.info(f"Making {method} request to: {url}")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                if method.upper() == "GET":
                    async with session.get(url, params=data) as response:
                        response_data = await response.json()
                elif method.upper() == "POST":
                    headers = {"Content-Type": "application/json"}
                    async with session.post(
                        url, json=data, headers=headers
                    ) as response:
                        response_data = await response.json()
                else:
                    return False, None, f"Unsupported HTTP method: {method}"

                if response.status == 200:
                    logger.info(f"Sidecar API request successful: {endpoint}")
                    return True, response_data, None
                else:
                    error_msg = f"Sidecar API error {response.status}: {response_data.get('error', 'Unknown error')}"
                    logger.error(error_msg)
                    return False, None, error_msg

        except aiohttp.ClientError as e:
            error_msg = f"Network error connecting to sidecar: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error calling sidecar API: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    async def commit_notebook(
        self,
        notebook_path: str,
        notebook_content: Dict[str, Any],
        commit_message: str,
        include_metadata: bool = True,
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]], Optional[str], bool]:
        """
        Commit notebook using sidecar API.

        Args:
            notebook_path: Path to the notebook file
            notebook_content: Notebook content as dictionary
            commit_message: Commit message
            include_metadata: Whether to include git_lock_sign metadata

        Returns:
            Tuple of (success, commit_hash, metadata, error_message, signed)
        """
        logger.info(f"Committing notebook via sidecar: {notebook_path}")

        request_data = {
            "notebook_path": notebook_path,
            "commit_message": commit_message,
            "notebook_content": notebook_content,
            "include_metadata": include_metadata,
            "auto_commit": False,
        }

        success, response_data, error = await self._make_request(
            "POST", "/commit", request_data
        )

        if not success or not response_data:
            return False, None, None, error, False

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown commit error")
            return False, None, None, error_msg, False

        return (
            True,
            response_data.get("commit_hash"),
            response_data.get("metadata"),
            None,
            response_data.get("signed", False),
        )

    async def push_notebook(
        self,
        notebook_path: str,
        auto_push: bool = False,
        auto_commit_before_push: bool = False,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Push notebook changes using sidecar API.

        Args:
            notebook_path: Path to the notebook file
            auto_push: Whether this is an automatic push
            auto_commit_before_push: Whether to auto-commit before pushing

        Returns:
            Tuple of (success, repository_url, error_message)
        """
        logger.info(f"Pushing notebook via sidecar: {notebook_path}")
        logger.info(
            f"Auto-push: {auto_push}, Auto-commit before push: {auto_commit_before_push}"
        )

        request_data = {
            "notebook_path": notebook_path,
            "auto_push": auto_push,
            "auto_commit_before_push": auto_commit_before_push,
        }

        success, response_data, error = await self._make_request(
            "POST", "/push", request_data
        )

        if not success or not response_data:
            return False, None, error

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown push error")
            return False, None, error_msg

        return True, response_data.get("repository_url"), None

    async def lock_notebook(
        self, notebook_path: str, notebook_content: Dict[str, Any], commit_message: str
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]], Optional[str], bool]:
        """
        Lock notebook using sidecar API.

        Args:
            notebook_path: Path to the notebook file
            notebook_content: Notebook content as dictionary
            commit_message: Commit message for the lock

        Returns:
            Tuple of (success, commit_hash, metadata, error_message, signed)
        """
        logger.info(f"Locking notebook via sidecar: {notebook_path}")

        request_data = {
            "notebook_path": notebook_path,
            "notebook_content": notebook_content,
            "commit_message": commit_message,
        }

        success, response_data, error = await self._make_request(
            "POST", "/lock", request_data
        )

        if not success or not response_data:
            return False, None, None, error, False

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown lock error")
            return False, None, None, error_msg, False

        return (
            True,
            response_data.get("commit_hash"),
            response_data.get("metadata"),
            None,
            response_data.get("signed", False),
        )

    async def unlock_notebook(
        self, notebook_path: str, notebook_content: Dict[str, Any]
    ) -> Tuple[bool, bool, Optional[str]]:
        """
        Unlock notebook using sidecar API.

        Args:
            notebook_path: Path to the notebook file
            notebook_content: Notebook content as dictionary

        Returns:
            Tuple of (success, signature_valid, error_message)
        """
        logger.info(f"Unlocking notebook via sidecar: {notebook_path}")

        request_data = {
            "notebook_path": notebook_path,
            "notebook_content": notebook_content,
        }

        success, response_data, error = await self._make_request(
            "POST", "/unlock", request_data
        )

        if not success or not response_data:
            return False, False, error

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown unlock error")
            return False, False, error_msg

        return True, response_data.get("signature_valid", False), None

    async def get_user_info(
        self, notebook_path: str
    ) -> Tuple[bool, Optional[Dict[str, str]], Optional[str]]:
        """
        Get user info using sidecar API.

        Args:
            notebook_path: Path to the notebook file

        Returns:
            Tuple of (success, user_info_dict, error_message)
        """
        logger.info(f"Getting user info via sidecar for: {notebook_path}")

        params = {"notebook_path": notebook_path}
        success, response_data, error = await self._make_request(
            "GET", "/user-info", params
        )

        if not success or not response_data:
            return False, None, error

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown user info error")
            return False, None, error_msg

        user_info = {
            "name": response_data.get("user_name", "Unknown"),
            "email": response_data.get("user_email", "unknown@example.com"),
            "gpg_key_id": response_data.get("gpg_key_id"),
        }

        return True, user_info, None

    async def provision_repository(
        self, notebook_path: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Provision git repository using sidecar API (supports GitLab and Gitea).

        Args:
            notebook_path: Path to the notebook file

        Returns:
            Tuple of (success, repository_url, error_message)
        """
        logger.info(f"Provisioning repository via sidecar for: {notebook_path}")

        request_data = {"notebook_path": notebook_path}
        success, response_data, error = await self._make_request(
            "POST", "/provision", request_data
        )

        if not success or not response_data:
            return False, None, error

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown provision error")
            return False, None, error_msg

        repository_url = response_data.get("repository_url")
        return True, repository_url, None

    def sync_commit_notebook(
        self,
        notebook_path: str,
        notebook_content: Dict[str, Any],
        commit_message: str,
        include_metadata: bool = True,
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]], Optional[str], bool]:
        """
        Synchronous wrapper for commit_notebook.

        This is needed for compatibility with the existing handler structure.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.commit_notebook(
                    notebook_path, notebook_content, commit_message, include_metadata
                )
            )
        finally:
            loop.close()

    def sync_push_notebook(
        self, notebook_path: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Synchronous wrapper for push_notebook."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.push_notebook(notebook_path))
        finally:
            loop.close()

    def sync_get_user_info(
        self, notebook_path: str
    ) -> Tuple[bool, Optional[Dict[str, str]], Optional[str]]:
        """Synchronous wrapper for get_user_info."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_user_info(notebook_path))
        finally:
            loop.close()

    def sync_lock_notebook(
        self, notebook_path: str, notebook_content: Dict[str, Any], commit_message: str
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]], Optional[str], bool]:
        """Synchronous wrapper for lock_notebook."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.lock_notebook(notebook_path, notebook_content, commit_message)
            )
        finally:
            loop.close()

    def sync_unlock_notebook(
        self, notebook_path: str, notebook_content: Dict[str, Any]
    ) -> Tuple[bool, bool, Optional[str]]:
        """Synchronous wrapper for unlock_notebook."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.unlock_notebook(notebook_path, notebook_content)
            )
        finally:
            loop.close()

    def sync_provision_repository(
        self, notebook_path: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Synchronous wrapper for provision_repository."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.provision_repository(notebook_path))
        finally:
            loop.close()

    async def init_git_repository(
        self, notebook_path: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Initialize git repository using sidecar API.

        Args:
            notebook_path: Path to the notebook file

        Returns:
            Tuple of (success, repository_path, error_message)
        """
        logger.info(f"Initializing git repository via sidecar for: {notebook_path}")

        request_data = {"notebook_path": notebook_path}
        success, response_data, error = await self._make_request(
            "POST", "/git-init", request_data
        )

        if not success or not response_data:
            return False, None, error

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown git init error")
            return False, None, error_msg

        return True, response_data.get("repository_path"), None

    async def get_status(
        self, notebook_path: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get repository and notebook status using sidecar API.

        Args:
            notebook_path: Path to the notebook file

        Returns:
            Tuple of (success, status_dict, error_message)
        """
        logger.info(f"Getting status via sidecar for: {notebook_path}")

        params = {"notebook_path": notebook_path}
        success, response_data, error = await self._make_request(
            "GET", "/status", params
        )

        if not success or not response_data:
            return False, None, error

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown status error")
            return False, None, error_msg

        return True, response_data, None

    async def get_config(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get configuration using sidecar API.

        Returns:
            Tuple of (success, config_dict, error_message)
        """
        logger.info("Getting configuration via sidecar")

        success, response_data, error = await self._make_request("GET", "/config")

        if not success or not response_data:
            return False, None, error

        return True, response_data, None

    async def initialize_session(self, workspace_path: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Initialize session with workspace-level repository setup and sync.
        
        Args:
            workspace_path: Path to the workspace directory
            
        Returns:
            Tuple of (success, response_dict, error_message)
        """
        logger.info(f"Initializing session via sidecar for workspace: {workspace_path}")

        # Import urllib.parse for URL encoding
        from urllib.parse import urlencode
        
        # Send workspace_path as query parameter for this endpoint
        query_params = urlencode({"workspace_path": workspace_path})
        endpoint_with_params = f"/session-init?{query_params}"
        
        success, response_data, error = await self._make_request("POST", endpoint_with_params, {})

        if not success or not response_data:
            return False, None, error

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown session initialization error")
            return False, None, error_msg

        return True, response_data, None

    def sync_init_git_repository(
        self, notebook_path: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Synchronous wrapper for init_git_repository."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.init_git_repository(notebook_path))
        finally:
            loop.close()

    def sync_get_status(
        self, notebook_path: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Synchronous wrapper for get_status."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_status(notebook_path))
        finally:
            loop.close()

    async def commit_file_lifecycle(
        self, file_path: str, lifecycle_event: str, trigger_auto_push: bool = False, old_file_path: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Commit file lifecycle events using sidecar API.

        Args:
            file_path: Path to the file
            lifecycle_event: Lifecycle event type ('create', 'delete', or 'rename')
            trigger_auto_push: Whether to trigger auto-push after commit
            old_file_path: Path to the old file (for rename events)

        Returns:
            Tuple of (success, commit_hash, error_message)
        """
        logger.info(f"Committing file lifecycle via sidecar - {lifecycle_event}: {file_path}")

        request_data = {
            "file_path": file_path,
            "lifecycle_event": lifecycle_event,
            "trigger_auto_push": trigger_auto_push,
        }
        
        # Add old_file_path for rename events
        if lifecycle_event == "rename" and old_file_path:
            request_data["old_file_path"] = old_file_path

        success, response_data, error = await self._make_request(
            "POST", "/file-lifecycle-commit", request_data
        )

        if not success or not response_data:
            return False, None, error

        if not response_data.get("success", False):
            error_msg = response_data.get("error", "Unknown lifecycle commit error")
            return False, None, error_msg

        return True, response_data.get("commit_hash"), None

    def sync_commit_file_lifecycle(
        self, file_path: str, lifecycle_event: str, trigger_auto_push: bool = False, old_file_path: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Synchronous wrapper for commit_file_lifecycle."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.commit_file_lifecycle(file_path, lifecycle_event, trigger_auto_push, old_file_path)
            )
        finally:
            loop.close()

    def sync_get_config(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Synchronous wrapper for get_config."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_config())
        finally:
            loop.close()

    async def check_health(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Check sidecar service health.

        Returns:
            Tuple of (success, response_data, error_message)
        """
        logger.info(f"SidecarClient: Checking sidecar health at: {self.base_url}")
        return await self._make_request("GET", "/health")
