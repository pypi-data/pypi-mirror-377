"""Handlers for git lock and sign JupyterLab extension - Sidecar API version."""

import json
import logging
import os
from typing import Any, Dict

from jupyter_server.base.handlers import APIHandler

from .backend_logger_util import backend_default_logger_config
from .services.sidecar_client import SidecarClient

logger = logging.getLogger(__name__)
backend_default_logger_config(logger)


class BaseGitLockSignHandler(APIHandler):
    """Base handler for git lock sign operations using sidecar API."""

    # Disable XSRF protection for internal API endpoints
    xsrf_cookie = False

    def __init__(self, *args, **kwargs):
        """Initialize the base handler."""
        super().__init__(*args, **kwargs)
        self.sidecar_client = SidecarClient()

    def write_json(self, data: Dict[str, Any]):
        """Write JSON response."""
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))

    def write_error_json(self, status_code: int, message: str):
        """Write JSON error response."""
        self.set_status(status_code)
        self.write_json({"error": message})

    def data_received(self, chunk):
        """Handle data received."""

    def check_xsrf_cookie(self):
        """Override XSRF check for internal API endpoints."""
        # Disable XSRF protection for internal API endpoints
        pass


class LockNotebookHandler(BaseGitLockSignHandler):
    """Handler for locking notebooks with git commits via sidecar."""

    async def post(self):
        """Lock a notebook using sidecar API."""
        try:
            logger.info("🚀 Starting lock operation")

            # Get request data
            data = json.loads(self.request.body.decode("utf-8"))
            notebook_path = data.get("notebook_path")
            notebook_content = data.get("notebook_content")
            commit_message = data.get("commit_message")

            if not notebook_path or not notebook_content or not commit_message:
                self.write_error_json(
                    400, "Missing notebook_path, notebook_content, or commit_message"
                )
                return

            # Convert to absolute path
            abs_notebook_path = os.path.abspath(notebook_path)

            # Use sidecar to lock notebook
            (
                success,
                commit_hash,
                metadata,
                error,
                signed,
            ) = await self.sidecar_client.lock_notebook(
                abs_notebook_path, notebook_content, commit_message
            )

            if not success:
                logger.error(f"❌ Lock operation failed: {error}")
                self.write_error_json(500, f"Failed to lock notebook: {error}")
                return

            logger.info("✅ Lock operation completed successfully")
            self.write_json(
                {
                    "success": True,
                    "message": "Notebook locked successfully via sidecar",
                    "metadata": metadata,
                    "commit_hash": commit_hash,
                    "signed": signed,
                }
            )

        except json.JSONDecodeError:
            self.write_error_json(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"❌ Lock operation error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class UnlockNotebookHandler(BaseGitLockSignHandler):
    """Handler for unlocking notebooks via sidecar."""

    async def post(self):
        """Unlock a notebook using sidecar API."""
        try:
            logger.info("🚀 Starting unlock operation")

            # Get request data
            data = json.loads(self.request.body.decode("utf-8"))
            notebook_path = data.get("notebook_path")
            notebook_content = data.get("notebook_content")

            if not notebook_path or not notebook_content:
                self.write_error_json(400, "Missing notebook_path or notebook_content")
                return

            # Convert to absolute path
            abs_notebook_path = os.path.abspath(notebook_path)

            # Use sidecar to unlock notebook
            success, signature_valid, error = await self.sidecar_client.unlock_notebook(
                abs_notebook_path, notebook_content
            )

            if not success:
                logger.error(f"❌ Unlock operation failed: {error}")
                self.write_error_json(500, f"Failed to unlock notebook: {error}")
                return

            logger.info("✅ Unlock operation completed successfully")
            self.write_json(
                {
                    "success": True,
                    "message": "Notebook unlocked successfully via sidecar",
                    "signature_valid": signature_valid,
                }
            )

        except json.JSONDecodeError:
            self.write_error_json(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"❌ Unlock operation error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class CommitNotebookHandler(BaseGitLockSignHandler):
    """Handler for committing notebook changes via sidecar."""

    async def post(self):
        """Commit notebook changes using sidecar API."""
        try:
            logger.info("🚀 Starting commit operation")

            # Get request data
            data = json.loads(self.request.body.decode("utf-8"))
            notebook_path = data.get("notebook_path")
            notebook_content = data.get("notebook_content")
            commit_message = data.get("commit_message")
            auto_commit = data.get("auto_commit", False)

            # For auto-commits, notebook_content and commit_message are optional
            # The sidecar will handle loading content and generating messages
            if not notebook_path:
                self.write_error_json(400, "Missing notebook_path")
                return

            # For manual commits, we still require content and message
            if not auto_commit and (not notebook_content or not commit_message):
                self.write_error_json(
                    400, "Missing notebook_content or commit_message for manual commit"
                )
                return

            # Convert to absolute path
            abs_notebook_path = os.path.abspath(notebook_path)

            # Check environment variable for metadata inclusion (default: true)
            include_metadata = os.getenv("INCLUDE_METADATA", "true").lower() == "true"

            if auto_commit:
                # For auto-commits, use direct sidecar API call with all auto-commit parameters

                # Extract auto-commit specific fields
                cell_content_preview = data.get("cell_content_preview")
                execution_count = data.get("execution_count")
                timestamp = data.get("timestamp")

                # Build request for sidecar auto-commit API
                request_data = {
                    "notebook_path": abs_notebook_path,
                    "auto_commit": True,
                    "cell_content_preview": cell_content_preview,
                    "execution_count": execution_count,
                    "timestamp": timestamp,
                    "include_metadata": include_metadata,
                }

                # Add commit_message if provided
                if commit_message:
                    request_data["commit_message"] = commit_message

                # Add notebook_content if provided
                if notebook_content:
                    request_data["notebook_content"] = notebook_content

                # Make direct request to sidecar
                success, response_data, error = await self.sidecar_client._make_request(
                    "POST", "/commit", request_data
                )

                if not success or not response_data:
                    logger.error(
                        f"CommitNotebookHandler: Sidecar auto-commit failed: {error}"
                    )
                    self.write_error_json(
                        500, f"Failed to auto-commit notebook: {error}"
                    )
                    return

                if not response_data.get("success", False):
                    error_msg = response_data.get("error", "Unknown auto-commit error")
                    logger.error(f"❌ Auto-commit failed: {error_msg}")
                    self.write_error_json(
                        500, f"Failed to auto-commit notebook: {error_msg}"
                    )
                    return

                # Extract response data
                commit_hash = response_data.get("commit_hash")
                metadata = response_data.get("metadata")
                signed = response_data.get("signed", False)

            else:
                # For manual commits, use the existing sidecar client method

                # Use sidecar to commit notebook with configurable metadata
                (
                    success,
                    commit_hash,
                    metadata,
                    error,
                    signed,
                ) = await self.sidecar_client.commit_notebook(
                    abs_notebook_path,
                    notebook_content,
                    commit_message,
                    include_metadata=include_metadata,
                )

                if not success:
                    logger.error(f"❌ Commit operation failed: {error}")
                    self.write_error_json(500, f"Failed to commit notebook: {error}")
                    return

            # Generate response for both auto-commit and manual commit
            logger.info("✅ Commit operation completed successfully")
            response_data = {
                "success": True,
                "message": "Notebook committed successfully via sidecar",
                "commit_hash": commit_hash,
                "signed": signed,
            }

            # Only include metadata in response if it was included in the operation
            if include_metadata and metadata:
                response_data["metadata"] = metadata

            self.write_json(response_data)

        except json.JSONDecodeError:
            self.write_error_json(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"❌ Commit operation error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class UserInfoHandler(BaseGitLockSignHandler):
    """Handler for getting git user information via sidecar."""

    async def get(self):
        """Get git user info using sidecar API."""
        try:
            # Get notebook path from query parameter
            notebook_path = self.get_argument("notebook_path", None)

            if not notebook_path:
                logger.warning(
                    "No notebook_path provided, using current working directory as fallback"
                )
                notebook_path = os.getcwd()
            else:
                logger.info(f"Getting user info for notebook path: {notebook_path}")

            success, user_info, error = await self.sidecar_client.get_user_info(
                notebook_path
            )

            if success and user_info:
                # Return user info fields directly (not nested) to match frontend expectations
                self.write_json(
                    {
                        "success": True,
                        "user_name": user_info.get("name", ""),
                        "user_email": user_info.get("email", ""),
                        "gpg_key_id": user_info.get("gpg_key_id", ""),
                    }
                )
            else:
                self.write_json(
                    {
                        "success": False,
                        "error": error or "Git user configuration not found",
                    }
                )

        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class ProvisionRepositoryHandler(BaseGitLockSignHandler):
    """Handler for provisioning remote repositories via sidecar."""

    async def post(self):
        """Provision a repository using sidecar API."""
        try:
            logger.info(
                "=== ProvisionRepositoryHandler: Starting provision via sidecar ==="
            )

            # Get request data
            data = json.loads(self.request.body.decode("utf-8"))
            notebook_path = data.get("notebook_path")

            if not notebook_path:
                self.write_error_json(400, "Missing notebook_path")
                return

            # Convert to absolute path
            abs_notebook_path = os.path.abspath(notebook_path)
            logger.info(
                f"ProvisionRepositoryHandler: Provisioning for: {abs_notebook_path}"
            )

            # Use sidecar to provision repository
            (
                success,
                repository_url,
                error,
            ) = await self.sidecar_client.provision_repository(abs_notebook_path)

            if not success:
                logger.error(
                    f"ProvisionRepositoryHandler: Sidecar provision failed: {error}"
                )
                self.write_error_json(500, f"Failed to provision repository: {error}")
                return

            logger.info(
                f"ProvisionRepositoryHandler: ✅ Repository provisioned successfully"
            )
            self.write_json(
                {
                    "success": True,
                    "message": "Repository provisioned successfully via sidecar",
                    "push_url": repository_url,  # For compatibility with frontend
                    "repo_url": repository_url,
                }
            )

        except json.JSONDecodeError:
            self.write_error_json(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"ProvisionRepositoryHandler: Error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class PushRepositoryHandler(BaseGitLockSignHandler):
    """Handler for pushing changes to remote repositories via sidecar."""

    async def post(self):
        """Push changes using sidecar API."""
        try:
            logger.info("🚀 Starting push operation")

            # Get request data
            data = json.loads(self.request.body.decode("utf-8"))
            notebook_path = data.get("notebook_path")
            auto_push = data.get("auto_push", False)
            auto_commit_before_push = data.get("auto_commit_before_push", False)

            if not notebook_path:
                self.write_error_json(400, "Missing notebook_path")
                return

            # Convert to absolute path
            abs_notebook_path = os.path.abspath(notebook_path)
            logger.info(f"PushRepositoryHandler: Pushing for: {abs_notebook_path}")
            logger.info(f"PushRepositoryHandler: Auto-push: {auto_push}")
            logger.info(
                f"PushRepositoryHandler: Auto-commit before push: {auto_commit_before_push}"
            )

            # Use sidecar to push to repository with auto-commit flags
            success, repository_url, error = await self.sidecar_client.push_notebook(
                abs_notebook_path,
                auto_push=auto_push,
                auto_commit_before_push=auto_commit_before_push,
            )

            if not success:
                logger.error(f"❌ Push operation failed: {error}")
                self.write_error_json(500, f"Failed to push to repository: {error}")
                return

            logger.info("✅ Push operation completed successfully")
            self.write_json(
                {
                    "success": True,
                    "message": "Push completed successfully via sidecar",
                    "repository_url": repository_url,
                }
            )

        except json.JSONDecodeError:
            self.write_error_json(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"PushRepositoryHandler: Error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class WorkingDirectoryHandler(BaseGitLockSignHandler):
    """Handler for getting the working directory of the Jupyter server."""

    async def get(self):
        """Get the working directory, creating work subdirectory if CREATE_WORK_SUBDIRECTORY is enabled."""
        try:
            base_working_directory = os.getcwd()
            working_directory = base_working_directory
            
            # Check if CREATE_WORK_SUBDIRECTORY is enabled via sidecar config
            try:
                success, config_data, error = await self.sidecar_client.get_config()
                if success and config_data:
                    create_work_subdir = config_data.get("create_work_subdirectory", False)
                    
                    if create_work_subdir:
                        work_dir = os.path.join(base_working_directory, "work")
                        logger.info(f"CREATE_WORK_SUBDIRECTORY enabled - using work directory: {work_dir}")
                        
                        # Create work directory if it doesn't exist
                        if not os.path.exists(work_dir):
                            try:
                                os.makedirs(work_dir, exist_ok=True)
                                logger.info(f"✅ Created work directory: {work_dir}")
                            except Exception as e:
                                logger.error(f"❌ Failed to create work directory: {e}")
                                self.write_error_json(500, f"Failed to create work directory: {e}")
                                return
                        else:
                            logger.info(f"✅ Work directory already exists: {work_dir}")
                        
                        working_directory = work_dir
                    else:
                        logger.info(f"CREATE_WORK_SUBDIRECTORY disabled - using base directory: {base_working_directory}")
                else:
                    logger.warning("Could not get config from sidecar, using base working directory")
            except Exception as e:
                logger.warning(f"Error getting config from sidecar: {e}, using base working directory")
            
            self.write_json({"success": True, "working_directory": working_directory})
        except Exception as e:
            logger.error(f"Error getting working directory: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class GitInitHandler(BaseGitLockSignHandler):
    """Handler for initializing git repositories via sidecar."""

    async def post(self):
        """Initialize git repository using sidecar API."""
        try:
            logger.info("🚀 Starting git init operation")

            # Get request data
            data = json.loads(self.request.body.decode("utf-8"))
            notebook_path = data.get("notebook_path")

            if not notebook_path:
                self.write_error_json(400, "Missing notebook_path")
                return

            # Convert to absolute path
            abs_notebook_path = os.path.abspath(notebook_path)
            logger.info(f"GitInitHandler: Initializing git for: {abs_notebook_path}")

            # Use sidecar to initialize git repository
            (
                success,
                repository_path,
                error,
            ) = await self.sidecar_client.init_git_repository(abs_notebook_path)

            if not success:
                logger.error(f"❌ Git init operation failed: {error}")
                self.write_error_json(
                    500, f"Failed to initialize git repository: {error}"
                )
                return

            logger.info(
                f"GitInitHandler: ✅ Git initialization successful: {repository_path}"
            )
            self.write_json(
                {
                    "success": True,
                    "message": "Git repository initialized successfully via sidecar",
                    "repository_path": repository_path or abs_notebook_path,
                    "repository_url": None,
                    "error": None,
                }
            )

        except json.JSONDecodeError:
            self.write_error_json(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"GitInitHandler: Error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class StatusHandler(BaseGitLockSignHandler):
    """Handler for getting repository and notebook status via sidecar."""

    async def get(self):
        """Get status using sidecar API."""
        try:
            notebook_path = self.get_argument("notebook_path", "")

            if not notebook_path:
                self.write_error_json(400, "Missing notebook_path parameter")
                return

            # Convert to absolute path
            abs_notebook_path = os.path.abspath(notebook_path)
            logger.info(f"StatusHandler: Getting status for: {abs_notebook_path}")

            # Use sidecar to get status
            success, status_data, error = await self.sidecar_client.get_status(
                abs_notebook_path
            )

            if not success:
                logger.error(f"❌ Status operation failed: {error}")
                self.write_error_json(500, f"Failed to get status: {error}")
                return

            logger.info("✅ Status retrieved successfully")
            # Return the status data from sidecar, with fallbacks for missing fields
            status_dict = status_data or {}
            self.write_json(
                {
                    "success": True,
                    "is_git_repository": status_dict.get("is_git_repository", True),
                    "is_locked": status_dict.get("is_locked", False),
                    "repository_path": status_dict.get(
                        "repository_path", abs_notebook_path
                    ),
                    "signature_metadata": status_dict.get("signature_metadata"),
                    "last_commit_hash": status_dict.get("last_commit_hash"),
                    "error": None,
                }
            )

        except Exception as e:
            logger.error(f"StatusHandler: Error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class SidecarUrlHandler(BaseGitLockSignHandler):
    """Handler for getting sidecar URL from environment variables."""

    async def get(self):
        """Get sidecar URL from environment variables."""
        try:
            logger.info("SidecarUrlHandler: Getting sidecar URL from environment variables")

            # Read sidecar connection info from environment variables
            sidecar_host = os.getenv("SIDECAR_HOST", "localhost")
            sidecar_port = os.getenv("SIDECAR_PORT", "8001")
            
            logger.info(f"SidecarUrlHandler: Reading environment variables:")
            logger.info(f"SidecarUrlHandler: SIDECAR_HOST={sidecar_host}")
            logger.info(f"SidecarUrlHandler: SIDECAR_PORT={sidecar_port}")

            # Build response with sidecar connection info
            response_data = {
                "success": True,
                "sidecar_host": sidecar_host,
                "sidecar_port": int(sidecar_port),
                "message": "Sidecar URL retrieved from environment variables",
            }

            logger.info(f"SidecarUrlHandler: ✅ Sidecar URL provided: {sidecar_host}:{sidecar_port}")
            self.write_json(response_data)

        except Exception as e:
            logger.error(f"SidecarUrlHandler: Error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class ConfigHandler(BaseGitLockSignHandler):
    """Handler for getting configuration via sidecar."""

    async def get(self):
        """Get configuration using sidecar API."""
        try:
            logger.info("ConfigHandler: Getting configuration")

            # Use sidecar to get configuration
            success, config_data, error = await self.sidecar_client.get_config()

            if not success:
                logger.error(f"❌ Config operation failed: {error}")
                self.write_error_json(500, f"Failed to get configuration: {error}")
                return

            logger.info("✅ Configuration retrieved successfully")
            # Return the config data from sidecar, with fallbacks for missing fields
            config_dict = config_data or {}

            response_data = {
                "success": True,
                **config_dict,
                "message": "Configuration retrieved successfully from sidecar",
            }

            self.write_json(response_data)

        except Exception as e:
            logger.error(f"ConfigHandler: Error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class SessionInitHandler(BaseGitLockSignHandler):
    """Handler for initializing user session with workspace-level git repository setup via sidecar."""

    async def post(self):
        """Initialize user session using sidecar API."""
        try:
            logger.info("🚀 Starting session initialization")

            # Get request data
            data = json.loads(self.request.body.decode("utf-8"))
            workspace_path = data.get("workspace_path")

            if not workspace_path:
                self.write_error_json(400, "Missing workspace_path")
                return

            # Convert to absolute path
            abs_workspace_path = os.path.abspath(workspace_path)
            logger.info(f"SessionInitHandler: Initializing session for workspace: {abs_workspace_path}")
            logger.info(f"SessionInitHandler: Original workspace_path from request: {workspace_path}")
            logger.info(f"SessionInitHandler: Current working directory: {os.getcwd()}")
            logger.info(f"SessionInitHandler: Workspace path exists check: {os.path.exists(abs_workspace_path)}")
            
            # Additional debugging - check if relative path exists
            if not os.path.isabs(workspace_path):
                logger.info(f"SessionInitHandler: Relative path exists check: {os.path.exists(workspace_path)}")
                
            # List current directory contents for debugging
            try:
                current_dir_contents = os.listdir(os.getcwd())
                logger.info(f"SessionInitHandler: Current directory contents: {current_dir_contents[:10]}")  # Limit to first 10 items
            except Exception as e:
                logger.warning(f"SessionInitHandler: Could not list current directory: {e}")

            # Use sidecar to initialize session
            success, response_data, error = await self.sidecar_client.initialize_session(
                abs_workspace_path
            )

            if not success:
                logger.error(f"❌ Session initialization failed: {error}")
                self.write_error_json(500, f"Failed to initialize session: {error}")
                return

            logger.info("✅ Session initialization completed successfully")
            
            # Return the response data from sidecar
            response_dict = response_data or {}
            self.write_json({
                "success": True,
                "message": response_dict.get("message", "Session initialized successfully"),
                "repository_path": response_dict.get("repository_path"),
                "repository_url": response_dict.get("repository_url"),
            })

        except json.JSONDecodeError:
            self.write_error_json(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"SessionInitHandler: Error: {str(e)}")
            self.write_error_json(500, f"Internal server error: {str(e)}")


class FileLifecycleCommitHandler(BaseGitLockSignHandler):
    """Handler for committing file lifecycle events via sidecar."""

    async def get(self):
        """Test GET method to verify endpoint is reachable."""
        logger.info("🔍 FileLifecycleCommitHandler: GET method called for testing!")
        self.write_json({
            "success": True,
            "message": "FileLifecycleCommitHandler is reachable via GET",
            "test": True
        })

    async def post(self):
        """Commit file lifecycle events using sidecar API."""
        try:
            logger.info("🚀 Starting file lifecycle commit")

            # Get request data
            try:
                data = json.loads(self.request.body.decode("utf-8"))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Raw request body: {self.request.body}")
                self.write_error_json(400, f"Invalid JSON in request body: {str(e)}")
                return
            except Exception as e:
                logger.error(f"Error parsing request body: {e}")
                self.write_error_json(400, f"Error parsing request: {str(e)}")
                return

            file_path = data.get("file_path")
            lifecycle_event = data.get("lifecycle_event")
            trigger_auto_push = data.get("trigger_auto_push", False)

            if not file_path:
                self.write_error_json(400, "file_path is required")
                return

            if not lifecycle_event:
                self.write_error_json(400, "lifecycle_event is required")
                return

            if lifecycle_event not in ["create", "delete", "rename"]:
                self.write_error_json(400, "lifecycle_event must be 'create', 'delete', or 'rename'")
                return

            # For rename events, old_file_path is required
            old_file_path = None
            if lifecycle_event == "rename":
                old_file_path = data.get("old_file_path")
                if not old_file_path:
                    self.write_error_json(400, "old_file_path is required for rename events")
                    return
                logger.info(f"Old file path for rename: {old_file_path}")

            logger.info(f"File lifecycle commit request - {lifecycle_event}: {file_path}")
            logger.info(f"Trigger auto-push: {trigger_auto_push}")
            
            # Debug: Check if file exists and git repository status
            logger.info(f"File exists check: {os.path.exists(file_path)}")
            logger.info(f"File path: {file_path}")
            logger.info(f"Current working directory: {os.getcwd()}")
            
            # For file creation, add a small delay to ensure file exists
            if lifecycle_event == "create":
                logger.info("File creation event - adding small delay to ensure file exists")
                import asyncio
                await asyncio.sleep(0.5)  # 500ms delay
                logger.info(f"After delay - File exists check: {os.path.exists(file_path)}")

            # Use sidecar client to commit lifecycle event
            logger.info(f"Calling sidecar client for lifecycle event: {lifecycle_event}")
            if lifecycle_event == "rename":
                logger.info(f"Calling sidecar client with old_file_path: {old_file_path}")
                success, commit_hash, error_message = await self.sidecar_client.commit_file_lifecycle(
                    file_path, lifecycle_event, trigger_auto_push, old_file_path
                )
            else:
                success, commit_hash, error_message = await self.sidecar_client.commit_file_lifecycle(
                    file_path, lifecycle_event, trigger_auto_push
                )

            if success:
                logger.info(f"File lifecycle commit successful via sidecar: {commit_hash}")
                self.write_json({
                    "success": True,
                    "commit_hash": commit_hash,
                    "message": f"File lifecycle commit successful: {lifecycle_event}"
                })
            else:
                logger.error(f"File lifecycle commit failed via sidecar: {error_message}")
                self.write_error_json(500, f"File lifecycle commit failed: {error_message}")

        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            self.write_error_json(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"File lifecycle commit failed: {str(e)}")
            self.write_error_json(500, f"File lifecycle commit failed: {str(e)}")


class HealthHandler(BaseGitLockSignHandler):
    """Handler for checking sidecar health via backend."""

    async def get(self):
        """Check sidecar health from backend."""
        try:
            logger.info("=== HealthHandler: Checking sidecar health via backend ===")
            
            # Use sidecar client to check health
            success, response_data, error = await self.sidecar_client.check_health()
            
            if success:
                logger.info("HealthHandler: ✅ Sidecar is healthy")
                self.write_json({
                    "success": True,
                    "healthy": True,
                    "message": "Sidecar service is healthy",
                    "sidecar_response": response_data
                })
            else:
                logger.error(f"HealthHandler: ❌ Sidecar health check failed: {error}")
                self.write_json({
                    "success": False,
                    "healthy": False,
                    "error": f"Sidecar health check failed: {error}"
                })
                
        except Exception as e:
            logger.error(f"HealthHandler: 💥 Unexpected error: {str(e)}")
            self.write_error_json(500, f"Health check failed: {str(e)}")
