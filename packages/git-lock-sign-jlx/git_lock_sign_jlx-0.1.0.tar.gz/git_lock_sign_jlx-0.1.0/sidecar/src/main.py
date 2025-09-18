"""
CELN Sidecar Service - Main application entry point

This service handles all git operations for the JupyterLab extension,
providing a REST API for notebook git operations with GitLab integration.
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load .env file from project root (up two levels from src/main.py)
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env file from: {env_path}")
else:
    print(f"⚠️ No .env file found at: {env_path}")
    # Also try loading from current directory
    load_dotenv()
    print("🔍 Attempted to load .env from current directory")

from .api.routes import router
from .services.auto_save_service import AutoSaveService
from .services.config_service import ConfigService
from .services.debounce_service import DebounceService
from .services.git_service import GitService
from .services.provider_services import GitLabService, GiteaService, GitHubEnterpriseService
from .services.gpg_service import GPGService
from .services.notebook_service import NotebookService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

GIT_SERVER = os.getenv("GIT_SERVER", "gitea")


async def check_git_server_connectivity(config_service) -> bool:
    """
    Check if the git server is reachable on startup.
    
    Args:
        config_service: Configuration service instance
        
    Returns:
        True if git server is reachable, False otherwise
    """
    git_server_url = config_service.git_server_url
    git_server_type = config_service.git_server
    
    logger.info(f"🔍 Checking connectivity to {git_server_type} server at {git_server_url}")
    
    try:
        # Test basic connectivity first
        if git_server_type == "gitea":
            # Try Gitea version endpoint
            test_url = f"{git_server_url}/api/v1/version"
        elif git_server_type == "gitlab":
            # Try GitLab version endpoint  
            test_url = f"{git_server_url}/api/v4/version"
        else:
            # Fallback to basic connectivity
            test_url = git_server_url
            
        response = requests.get(
            test_url,
            timeout=10,
            verify=config_service.git_ssl_verify
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Successfully connected to {git_server_type} server")
            if git_server_type == "gitea":
                try:
                    version_info = response.json()
                    logger.info(f"🎯 Gitea version: {version_info.get('version', 'unknown')}")
                except:
                    logger.info("🎯 Gitea server responded successfully")
            return True
        else:
            logger.warning(f"⚠️ Git server responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        logger.error(f"❌ Connection timeout to {git_server_type} server at {git_server_url}")
        logger.error("   This usually indicates a networking issue between containers")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Failed to connect to {git_server_type} server at {git_server_url}")
        logger.error(f"   Connection error: {e}")
        logger.error("   Check if the git server is running and network connectivity is configured")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error checking {git_server_type} connectivity: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting CELN Sidecar Service...")

    # Initialize services
    config_service = ConfigService()
    
    # Check git server connectivity before proceeding
    git_server_reachable = await check_git_server_connectivity(config_service)
    if not git_server_reachable:
        logger.warning("⚠️ Git server is not reachable - service will start but git operations may fail")
        logger.warning("   Check your network configuration and ensure the git server is running")
    
    notebook_service = NotebookService()
    gpg_service = GPGService()
    git_service = GitService(config_service)
    # Initialize git server services
    gitlab_service = None
    gitea_service = None
    github_enterprise_service = None
    
    if GIT_SERVER == "gitlab":
        gitlab_service = GitLabService(config_service, git_service)
    elif GIT_SERVER == "gitea":
        gitea_service = GiteaService(config_service, git_service)
    elif GIT_SERVER in ["github_enterprise", "github-enterprise"]:
        github_enterprise_service = GitHubEnterpriseService(config_service, git_service)
    else:
        raise ValueError(f"Invalid git server: {GIT_SERVER}")
    
    debounce_service = DebounceService()
    auto_save_service = AutoSaveService(config_service)

    # Store services in app state
    app.state.config_service = config_service
    app.state.notebook_service = notebook_service
    app.state.gpg_service = gpg_service
    app.state.git_service = git_service
    app.state.gitlab_service = gitlab_service
    app.state.gitea_service = gitea_service
    app.state.debounce_service = debounce_service
    app.state.auto_save_service = auto_save_service
    app.state.github_enterprise_service = github_enterprise_service

    # Start auto-save service
    await auto_save_service.start()

    logger.info("Sidecar service started successfully")

    yield

    # Cleanup
    await auto_save_service.stop()
    logger.info("Sidecar service stopped")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="CELN Sidecar Service",
        description="Git operations service for JupyterLab notebooks",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add routes
    app.include_router(router, prefix="/sidecar")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {"status": "healthy", "service": "celn-sidecar"}

    # Error handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code},
        )

    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("SIDECAR_PORT", "8001"))
    host = os.getenv("SIDECAR_HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("SIDECAR_DEBUG", "false").lower() == "true",
    )
