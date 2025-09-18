# CELN Sidecar Service API Reference

This document provides a comprehensive reference for the CELN Sidecar Service API, which handles all git operations for JupyterLab notebooks including initialization, auto-commit on cell execution, auto-push on notebook save, and manual git operations.

## Overview

The CELN Sidecar Service is a FastAPI-based backend service that provides git automation capabilities for Jupyter notebooks. It runs as a separate service (typically on port 8001) and is called by the JupyterLab extension to perform git operations.

### Base URL

- **Development**: `http://localhost:8001`
- **Production**: Configured via `SIDECAR_HOST` and `SIDECAR_PORT` environment variables

### Service Architecture

The service consists of several key components:
- **Git Service**: Core git operations (init, commit, push, status)
- **GitLab Service**: GitLab integration and repository provisioning
- **Debounce Service**: Prevents spam operations during rapid cell execution
- **Notebook Service**: Handles notebook content processing and metadata
- **GPG Service**: Handles commit signing when configured
- **Config Service**: Manages environment-based configuration

## Authentication

The sidecar service currently operates without authentication, as it's designed to run locally or within a secure network environment. Future versions may include token-based authentication.

## API Endpoints

### 1. Repository Provisioning

#### POST `/provision`

Provision a GitLab repository using the provision API. This is typically called after git-init to set up GitLab integration.

**Request Body:**
```json
{
  "notebook_path": "/path/to/notebook.ipynb"
}
```

**Response Format:**
```json
{
  "success": true,
  "message": "GitLab repository provisioned successfully",
  "repository_path": "/path/to/repo",
  "repository_url": "https://gitlab.server.com/researchers/username/work.git",
  "error": null
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8001/provision" \
  -H "Content-Type: application/json" \
  -d '{"notebook_path": "/home/user/notebook.ipynb"}'
```

**Notes:**
- Requires the repository to already be a git repository (use `/git-init` first)
- Uses GitLab provision API to create user and repository structure
- Repository path follows pattern: `researchers/{username}/work`

### 2. Git Repository Initialization

#### POST `/git-init`

Initialize a git repository if it doesn't exist and set up basic configuration.

**Request Body:**
```json
{
  "notebook_path": "/path/to/notebook.ipynb"
}
```

**Response Format:**
```json
{
  "success": true,
  "message": "Git repository initialized successfully. Call /provision to set up GitLab integration.",
  "repository_path": "/path/to/repo",
  "repository_url": null,
  "error": null
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8001/git-init" \
  -H "Content-Type: application/json" \
  -d '{"notebook_path": "/home/user/notebook.ipynb"}'
```

**Notes:**
- Safe to call multiple times - returns success if repository already exists
- Sets up git user configuration from environment variables
- Does not set up GitLab integration (use `/provision` for that)

### 3. Commit Operations

#### POST `/commit`

Commit notebook changes with optional metadata and content processing.

**Request Body:**
```json
{
  "notebook_path": "/path/to/notebook.ipynb",
  "commit_message": "Manual commit: Updated analysis",
  "notebook_content": "{\"cells\": [...], \"metadata\": {...}}",
  "auto_commit": false,
  "include_metadata": true,
  "cell_content_preview": "print('Hello World')",
  "execution_count": 5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response Format:**
```json
{
  "success": true,
  "message": "Notebook committed successfully",
  "commit_hash": "abc123def456",
  "signed": true,
  "debounced": false,
  "metadata": {
    "notebook_hash": "sha256:...",
    "execution_count": 5,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "content_hash": "sha256:...",
  "error": null
}
```

**Auto-commit Behavior:**
- If `auto_commit` is true and no `commit_message` is provided, generates automatic message
- Message generation depends on `COMMIT_MESSAGE_MODE` environment variable:
  - `generic`: Simple "Auto-commit: Cell execution" messages
  - `detailed`: Includes cell content preview and execution info

**Debouncing:**
- Respects `COMMIT_DEBOUNCE_SECONDS` environment variable
- Returns `debounced: true` if operation is skipped due to debouncing

**Metadata Inclusion:**
- Controlled by `include_metadata` parameter or `INCLUDE_METADATA` environment variable
- When enabled, includes notebook hashing, timestamps, and execution metadata
- When disabled, performs faster simple commits

**Example Usage:**
```bash
# Manual commit with metadata
curl -X POST "http://localhost:8001/commit" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook_path": "/home/user/notebook.ipynb",
    "commit_message": "Updated data analysis",
    "include_metadata": true
  }'

# Auto-commit from cell execution
curl -X POST "http://localhost:8001/commit" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook_path": "/home/user/notebook.ipynb",
    "auto_commit": true,
    "cell_content_preview": "data.head()",
    "execution_count": 10,
    "notebook_content": "{...}"
  }'
```

### 4. Push Operations

#### POST `/push`

Push committed changes to GitLab repository with optional auto-commit before push.

**Request Body:**
```json
{
  "notebook_path": "/path/to/notebook.ipynb",
  "auto_push": true,
  "auto_commit_before_push": true
}
```

**Response Format:**
```json
{
  "success": true,
  "message": "Push operation completed",
  "repository_url": "https://gitlab.server.com/researchers/username/work.git",
  "debounced": false,
  "error": null
}
```

**Auto-commit Before Push:**
- When `auto_commit_before_push` is true, checks for uncommitted changes
- Automatically commits any saved changes before pushing
- Uses timestamp-based commit messages for auto-commits
- Includes extensive debugging for content verification

**Debouncing:**
- Auto-pushes respect `PUSH_DEBOUNCE_SECONDS` environment variable
- Manual pushes execute immediately
- Debounced operations return `debounced: true` and execute in background

**Example Usage:**
```bash
# Manual push
curl -X POST "http://localhost:8001/push" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook_path": "/home/user/notebook.ipynb",
    "auto_push": false
  }'

# Auto-push with auto-commit
curl -X POST "http://localhost:8001/push" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook_path": "/home/user/notebook.ipynb",
    "auto_push": true,
    "auto_commit_before_push": true
  }'
```

### 5. Notebook Locking

#### POST `/lock`

Lock notebook with commit and optional GPG signing.

**Request Body:**
```json
{
  "notebook_path": "/path/to/notebook.ipynb",
  "notebook_content": "{\"cells\": [...], \"metadata\": {...}}",
  "commit_message": "Locking notebook after analysis completion"
}
```

**Response Format:**
```json
{
  "success": true,
  "message": "Notebook locked successfully",
  "metadata": {
    "locked_at": "2024-01-15T10:30:00Z",
    "signature": "gpg_signature_data",
    "content_hash": "sha256:..."
  },
  "commit_hash": "abc123def456",
  "signed": true,
  "error": null
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8001/lock" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook_path": "/home/user/notebook.ipynb",
    "commit_message": "Final analysis - locking notebook",
    "notebook_content": "{...}"
  }'
```

### 6. Notebook Unlocking

#### POST `/unlock`

Unlock notebook after signature verification.

**Request Body:**
```json
{
  "notebook_path": "/path/to/notebook.ipynb",
  "notebook_content": "{\"cells\": [...], \"metadata\": {...}}"
}
```

**Response Format:**
```json
{
  "success": true,
  "message": "Notebook unlocked successfully",
  "signature_valid": true,
  "error": null
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8001/unlock" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook_path": "/home/user/notebook.ipynb",
    "notebook_content": "{...}"
  }'
```

### 7. Repository Status

#### GET `/status`

Get comprehensive repository and notebook status information.

**Query Parameters:**
- `notebook_path` (required): Path to the notebook file

**Response Format:**
```json
{
  "success": true,
  "is_git_repository": true,
  "is_locked": false,
  "repository_path": "/path/to/repo",
  "signature_metadata": {
    "signed": true,
    "signature_valid": true,
    "signer": "user@example.com"
  },
  "last_commit_hash": "abc123def456",
  "error": null
}
```

**Example Usage:**
```bash
curl "http://localhost:8001/status?notebook_path=/home/user/notebook.ipynb"
```

### 8. User Information

#### GET `/user-info`

Get git user information for a specific notebook path.

**Query Parameters:**
- `notebook_path` (required): Path to the notebook file

**Response Format:**
```json
{
  "success": true,
  "user_name": "John Doe",
  "user_email": "john.doe@example.com",
  "gpg_key_id": "ABC123DEF456",
  "error": null
}
```

**Example Usage:**
```bash
curl "http://localhost:8001/user-info?notebook_path=/home/user/notebook.ipynb"
```

### 9. Configuration

#### GET `/config`

Get current sidecar configuration including all environment-based settings.

**Response Format:**
```json
{
  "include_metadata": true,
  "commit_debounce_seconds": 0,
  "push_debounce_seconds": 0,
  "cell_execution_detection_delay_ms": 1000,
  "auto_save_interval_minutes": 5,
  "message": "Configuration loaded from environment variables with fallbacks"
}
```

**Example Usage:**
```bash
curl "http://localhost:8001/config"
```

**Configuration Details:**
- `include_metadata`: Processed boolean value for metadata inclusion
- `commit_debounce_seconds`: Debouncing delay for commit operations
- `push_debounce_seconds`: Debouncing delay for push operations
- `cell_execution_detection_delay_ms`: Frontend delay before detecting cell execution
- `auto_save_interval_minutes`: Interval for automatic save operations

## Error Handling

### Standard Error Response Format

```json
{
  "success": false,
  "message": "Operation failed",
  "error": "Detailed error message",
  "...": null
}
```

### Common HTTP Status Codes

- **200 OK**: Operation completed successfully
- **400 Bad Request**: Invalid request parameters or missing required fields
- **500 Internal Server Error**: Server-side error during operation

### Common Error Scenarios

1. **Not a git repository**: Repository must be initialized first
2. **GitLab provisioning failed**: Check GitLab server configuration and API token
3. **Commit failed**: Usually due to git configuration issues or file access problems
4. **Push failed**: Network connectivity or GitLab authentication issues
5. **File not found**: Notebook path doesn't exist or is inaccessible

## Background Tasks

The service uses FastAPI's background tasks for debounced operations:

### Debounced Commits
- Triggered when commit debouncing is enabled (`COMMIT_DEBOUNCE_SECONDS` > 0)
- Waits for the debounce period before executing the actual commit
- Prevents spam commits during rapid cell execution

### Debounced Pushes
- Triggered when push debouncing is enabled (`PUSH_DEBOUNCE_SECONDS` > 0)
- Can include auto-commit before push if configured
- Prevents spam pushes during rapid notebook saves

## Environment Integration

The API behavior is heavily influenced by environment variables:

### Git Configuration
- `GIT_USER_NAME`, `GIT_USER_EMAIL`: User identity for commits
- `GPG_KEY_ID`: GPG key for commit signing

### Operation Control
- `INCLUDE_METADATA`: Default metadata inclusion behavior
- `COMMIT_DEBOUNCE_SECONDS`: Debouncing for commits
- `PUSH_DEBOUNCE_SECONDS`: Debouncing for pushes
- `COMMIT_MESSAGE_MODE`: Style of auto-generated commit messages

### GitLab Integration
- `GITLAB_TOKEN`: API authentication token

### Performance Tuning
- `CELL_EXECUTION_DETECTION_DELAY_MS`: Frontend execution detection delay
- `AUTO_SAVE_INTERVAL_MINUTES`: Automatic save frequency

## Integration Examples

### JupyterLab Extension Integration

The typical workflow from the JupyterLab extension:

1. **Initialize Repository**:
   ```javascript
   // Check status first
   const status = await fetch(`http://${SIDECAR_HOST}:${SIDECAR_PORT}/status?notebook_path=${path}`);
   
   // Initialize if needed
   if (!status.is_git_repository) {
     await fetch(`http://${SIDECAR_HOST}:${SIDECAR_PORT}/git-init`, {
       method: 'POST',
       body: JSON.stringify({notebook_path: path})
     });
     
     // Set up GitLab integration
     await fetch(`http://${SIDECAR_HOST}:${SIDECAR_PORT}/provision`, {
       method: 'POST', 
       body: JSON.stringify({notebook_path: path})
     });
   }
   ```

2. **Auto-commit on Cell Execution**:
   ```javascript
   await fetch(`http://${SIDECAR_HOST}:${SIDECAR_PORT}/commit`, {
     method: 'POST',
     body: JSON.stringify({
       notebook_path: path,
       auto_commit: true,
       cell_content_preview: cellCode,
       execution_count: executionCount,
       notebook_content: JSON.stringify(notebookContent)
     })
   });
   ```

3. **Auto-push on Save**:
   ```javascript
   await fetch(`http://${SIDECAR_HOST}:${SIDECAR_PORT}/push`, {
     method: 'POST',
     body: JSON.stringify({
       notebook_path: path,
       auto_push: true,
       auto_commit_before_push: true
     })
   });
   ```

### Manual Operations

For manual git operations through the UI:

```javascript
// Manual commit
const commitResponse = await fetch(`http://${SIDECAR_HOST}:${SIDECAR_PORT}/commit`, {
  method: 'POST',
  body: JSON.stringify({
    notebook_path: path,
    commit_message: userCommitMessage,
    include_metadata: true
  })
});

// Manual push
const pushResponse = await fetch(`http://${SIDECAR_HOST}:${SIDECAR_PORT}/push`, {
  method: 'POST', 
  body: JSON.stringify({
    notebook_path: path,
    auto_push: false
  })
});
```

## Development and Testing

### Running the Sidecar Service

```bash
# Set environment variables
export SIDECAR_HOST=0.0.0.0
export SIDECAR_PORT=8001
export SIDECAR_DEBUG=true

# Start the service
cd sidecar
python -m src.main
```

### Testing API Endpoints

Use the provided curl examples or tools like Postman to test individual endpoints. The service includes extensive logging when `SIDECAR_DEBUG=true` is set.

### Health Check

The service runs on FastAPI, so you can access:
- API documentation: `http://localhost:8001/docs`
- OpenAPI schema: `http://localhost:8001/openapi.json`

## Security Considerations

1. **Network Security**: The sidecar service should run on localhost or within a secure network
2. **File Access**: The service requires read/write access to notebook directories
3. **Git Configuration**: Ensure proper git user configuration to avoid attribution issues
4. **GitLab Integration**: Use appropriate API token scopes and secure token storage
5. **Content Validation**: The service processes notebook content - ensure trusted input sources

## Troubleshooting

### Common Issues

1. **Service not responding**: Check if sidecar service is running on correct port
2. **Git operations failing**: Verify git configuration and repository initialization
3. **GitLab integration issues**: Check network connectivity and API token validity
4. **Debouncing not working**: Verify environment variable configuration
5. **Content loss**: Check auto-commit and auto-push settings

### Debug Logging

Enable debug logging for detailed operation traces:

```bash
export SIDECAR_DEBUG=true
export LOG_LEVEL=DEBUG
```

This will provide extensive logging including:
- API request/response details
- Git operation commands and output
- Content verification during commits
- Background task execution status
- Environment variable loading details 