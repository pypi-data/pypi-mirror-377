# Docker Build Guide (Simplified)

Quick guide to build and run the Git Lock Sign JupyterLab Extension using Docker.

## Quick Start

```bash
cd docker
make build
make up
```

Access JupyterLab at: http://localhost:8888 (token: `test`)

## Architecture

The project uses two containers:

```
┌─────────────────────┐    HTTP/API     ┌─────────────────────┐
│   JupyterLab        │ ◄─────────────► │   Sidecar Service   │
│   Container         │                 │   Container         │
│   Port: 8888        │                 │   Port: 8001        │
└─────────────────────┘                 └─────────────────────┘
```

- **JupyterLab Container**: Runs JupyterLab with the extension pre-installed
- **Sidecar Service**: Handles Git operations, GPG signing, and Git server integration

## Build Commands

```bash
# Build both containers
make build

# Start services (builds if needed)
make up

# Stop services
make down

# Clean up containers and files
make clean
```

## Docker Compose Configuration

### Key Features

- **Shared Workspace**: Both containers access the same work directory
- **Separated Git Metadata**: Git files hidden from JupyterLab users
- **Health Checks**: Sidecar service includes health monitoring
- **Environment Variables**: Extensive configuration via environment

### Volume Mounts

```yaml
# JupyterLab container
volumes:
  - ./workspace/work:/home/jovyan/work:rw     # User workspace (visible)
  
# Sidecar container  
volumes:
  - ./workspace/work:/tmp/work:rw             # Same user files
  - ./workspace/.git-metadata:/tmp/.git-metadata:rw  # Git metadata (hidden)
```

### Environment Configuration

Key environment variables (see [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for full list):

```yaml
# Git Server Configuration
GIT_SERVER: gitea                    # Options: gitea, gitlab, github_enterprise
GIT_SERVER_URL: http://gitea:3000    # Your git server URL
GIT_SERVER_ADMIN_TOKEN: your_token   # API token for user/repo management

# User Configuration
GIT_USER_NAME: dev user
GIT_USER_EMAIL: dev@test.org

# Feature Controls
ENABLE_COMMIT_BUTTON: false         # Disable manual commit button
ENABLE_PUSH_BUTTON: false           # Disable manual push button
AUTO_SAVE_ENABLED: true             # Enable automatic save/push
```

### Service Dependencies

```yaml
jupyterlab:
  depends_on:
    sidecar:
      condition: service_healthy    # JupyterLab waits for sidecar to be ready
```

## Development Workflow

1. **Make code changes**
2. **Rebuild**: `make build`
3. **Restart**: `make up`
4. **Test**: Access JupyterLab at http://localhost:8888
5. **View logs**: `docker compose logs -f`

## Troubleshooting

### Common Issues

- **Permission errors**: Ensure proper file ownership in mounted volumes
- **Extension not loading**: Check if extension was built successfully during container build
- **Sidecar connectivity**: Verify sidecar service is healthy at http://localhost:8001/health

### Debug Commands

```bash
# View container logs
docker compose logs jupyterlab
docker compose logs sidecar

# Rebuild without cache
docker compose build --no-cache

# Check service status
docker compose ps
```

## File Structure

```
docker/
├── docker-compose.yml           # Multi-container orchestration
├── Makefile                     # Build automation commands
├── jupyterlab/
│   ├── Dockerfile              # JupyterLab container definition
│   └── values.yaml             # Package and configuration definitions
├── sidecar/
│   └── Dockerfile              # Sidecar service container definition
└── workspace/                  # Created during build
    ├── work/                   # User files (visible in JupyterLab)
    └── .git-metadata/          # Git metadata (hidden from users)
```

For detailed configuration options, see:
- [Environment Setup Guide](ENVIRONMENT_SETUP.md)
- [Authentication Configuration](AUTHENTICATION_CONFIGURATION.md)
- [API Reference](API_REFERENCE.md)
