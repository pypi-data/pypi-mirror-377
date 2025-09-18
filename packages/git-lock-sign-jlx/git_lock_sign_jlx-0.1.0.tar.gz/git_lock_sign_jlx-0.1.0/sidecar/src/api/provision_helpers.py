"""
Helper functions for the provision endpoint.

This module contains all helper functions related to repository provisioning,
including user registration checks, session sync, and git server provisioning.
"""

import logging
from typing import Any, Dict, Optional, Tuple

from ..services.git_service import GitService
from ..services.provider_services import ProviderService
from ..services.logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


def check_user_registration(git_server: str, user_email: str, services: Dict[str, Any]) -> bool:
    """Check if user is registered in the git server."""
    logger.info("🔍 Checking user registration status...")
    
    try:
        provider_service: ProviderService = services[f"{git_server}_service"]
        return provider_service.check_user_registration(user_email)
    except Exception as e:
        logger.warning(f"⚠️ User registration check failed: {str(e)}")
        return False


async def attempt_session_sync(git_server: str, repo_path: str, services: Dict[str, Any]) -> Optional[Any]:
    """Attempt to sync with remote history if user is registered."""
    logger.info("🔄 Attempting session sync with remote history...")
    
    try:
        # Get provider service for token-based git servers
        provider_service: ProviderService = services[f"{git_server}_service"]
        
        git_service: GitService = services["git_service"]
        sync_result = await git_service.sync_with_remote_on_session_start(
            repo_path,
            provider_service=provider_service
        )
        
        if not sync_result.success:
            logger.warning(f"⚠️ Session sync failed: {sync_result.error}")
        
        return sync_result
    except Exception as e:
        logger.warning(f"⚠️ Session sync error: {str(e)}")
        return None


async def provision_git_server(git_server: str, repo_path: str, services: Dict[str, Any]) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """Provision repository on the specified git server."""
    logger.info(f"🛠️ Provisioning repository on {git_server}...")
    
    server_name = git_server.capitalize().replace("_", " ")

    provider_service: ProviderService = services[f"{git_server}_service"]
    result = await provider_service.setup_repository(repo_path)

    return result.success, server_name, result.repository_url, result.error


def build_provision_message(server_name: str, sync_attempted: bool, sync_result: Optional[Any]) -> str:
    """Build success message for provision operation."""
    message_parts = [f"{server_name} repository provisioned successfully"]
    
    if sync_attempted:
        if sync_result and sync_result.success:
            message_parts.append("Repository synced with remote history")
        else:
            message_parts.append("Repository provisioned but sync had warnings")
    
    return ". ".join(message_parts)
