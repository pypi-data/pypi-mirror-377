# Environment Setup for git_lock_sign_jlx JupyterLab Extension

This document describes how to configure the environment variables required for the git_lock_sign_jlx JupyterLab extension. The extension supports various features including automatic git operations, GitLab integration, sidecar services, and extensive customization options.

## Quick Start

1. Copy the environment template:
   ```bash
   cp environment.env.template .env
   ```

2. Edit `.env` with your actual values

3. Source the environment and start JupyterLab:
   ```bash
   source .env
   conda activate jlx
   jupyter lab --log-level=INFO --ServerApp.jpserver_extensions="{'git_lock_sign_jlx': True}" 
   ```

## Configuration Architecture

All configuration values are centralized through the sidecar's `/config` endpoint. The frontend automatically fetches configuration from the backend at startup, ensuring consistency across all components. Environment variables are read by the sidecar service and provided to the frontend through this centralized configuration system.

## Configuration Categories

### Sidecar Service Configuration

The extension uses a sidecar service for backend operations:

- **SIDECAR_HOST**: Host address for the sidecar service
  - Default: `0.0.0.0`
  - Example: `localhost` for local development
  - **Note**: In Kubernetes deployments, this should be the service name

- **SIDECAR_PORT**: Port for the sidecar service
  - Default: `8001`
  - Example: `8001`

- **SIDECAR_DEBUG**: Enable debug mode for sidecar service
  - Default: `false`
  - Options: `true` | `false`

- **SIDECAR_SERVICE_NAME**: If set, it will override the SIDECAR_HOST setting, signaling a containerized deployment.

### Workspace Configuration

Controls workspace directory structure and initialization behavior:

- **CREATE_WORK_SUBDIRECTORY**: Automatically create and use a 'work' subdirectory for git operations
  - Default: `false`
  - Options: `true` | `false`
  - **Use Case**: For Kubernetes deployments where JupyterLab starts in `/home/jovyan` but you want git operations to occur in `/home/jovyan/work`
  - **Behavior When Enabled**: 
    - Creates `/home/jovyan/work` directory if it doesn't exist
    - All git operations (repository initialization, commits, etc.) use the work subdirectory
    - Frontend automatically uses the work directory as the effective working directory
  - **Behavior When Disabled**: Uses the current JupyterLab working directory directly
  - **Note**: This provides clean workspace isolation in containerized environments

### Git Configuration

The extension provides flexible git user configuration with environment variable precedence:

#### Priority Order:
1. Environment variables (`GIT_USER_EMAIL`, `GIT_USER_NAME`) - if `GIT_USER_EMAIL` is set
2. Local git config in the repository directory  
3. Global git config (fallback)

#### Configuration Variables:

- **GIT_USER_NAME**: Git user name for commits
  - Default: None
  - Example: `john_doe`

- **GIT_USER_EMAIL**: Git user email for commits
  - Default: None
  - Example: `john_doe@test.org`
  - **Note**: If provided, triggers automatic git repository initialization and user configuration

- **GPG_KEY_ID** (Optional): GPG key ID for signing commits
  - Default: None
  - Example: `your_gpg_key_id_here`

- **GIT_SSL_VERIFY**: Enable/disable git SSL verification
  - Default: `true`
  - Options: `true` | `false`
  - **Note**: Set to `false` for development where ssl is self-signed

#### Git Authentication:
The extension uses **embedded credentials** for all git operations. Authentication tokens are embedded directly in the remote URLs, which is the standard approach for git authentication. This means:

- **Credentials are stored in git configuration** - this is standard git behavior
- **Anyone with access to the repository can see credentials** - this is expected in git workflows
- **Higher reliability** - works consistently across all environments
- **No additional setup required** - no credential helpers or external authentication systems needed

The system automatically handles authentication for different git providers:
- **Gitea**: Uses admin token with admin username
- **GitLab**: Uses OAuth2 token  
- **GitHub Enterprise**: Uses installation token with x-access-token username

#### Containerized Development Notes:
When running in containers where git config may not be available, these environment variables take precedence. If `GIT_USER_EMAIL` is provided:
- The git repository will be automatically initialized if needed
- Git user configuration will be set using these environment variables
- If `GIT_USER_NAME` is not provided, the username will be extracted from the email (part before @ symbol)

### Self-hosted Git Server Configuration

Choose your git server backend and configure the connection:

- **GIT_SERVER**: Git server type
- Default: None
  - Options: `gitea` | `gitlab` | `github_enterprise`

- **GIT_SERVER_URL**: URL of your git server (for gitea and gitlab)
  - Default: `http://localhost:3000` (Gitea) | `https://localhost:8443` (GitLab)

- **GIT_SERVER_ADMIN_TOKEN**: API token for user and repository management
  - Required for repository provisioning and user operations
  - Example: See token generation instructions below

- **SINGLE_REPO_PER_USER**: Use single repository per user
  - Default: `true`
  - Options: `true` | `false`
  - **Note**: When true, creates `<username>/work` structure

- **ALLOWED_DOMAINS**: Comma separated allowed domains for user authentication. If set, the user email must be in one of the allowed domains.
  - Default: None
  - Example: `test.org,test.com`

#### How to Generate Git Server Tokens:

**For GitLab:**
1. Go to GitLab → User Settings → Access Tokens
2. Create a new token with `api`, `read_user`, `write_repository` scopes
3. Copy the generated token

**For Gitea:**
1. Go to Gitea → User Settings → Applications → Manage Access Tokens
2. Create a new token with appropriate permissions
3. Copy the generated token

### GitHub Enterprise Configuration:
When using GitHub Enterprise, you need to set the following environment variables:

- **GIT_SERVER**: `github_enterprise`
- **GITHUB_ENTERPRISE_URL**: URL of your git server
  - Default: None
  - Example: `https://github.com/JupyterTestOrg`
- **GITHUB_ENTERPRISE_ORG**: Organization name
  - Default: None
  - Example: `JupyterTestOrg`
- **GITHUB_APP_ID**: GitHub App ID
  - Default: None
  - Example: `1234567`
  - How to find it (note this is different from the installation id): 
    - Navigate to your GitHub App settings:
    - Sign in to your GitHub account.
    - In the upper-right corner of any page, click your profile picture.
      - For an app owned by a personal account, click Settings.
      - For an app owned by an organization:
        - Click Your organizations.
        - To the right of the organization, click Settings.
        - In the left sidebar, under "Developer settings," click GitHub Apps.
        - Select your App: Find the desired GitHub App in the list and click its name.
    - Locate the App ID: On the settings page for your GitHub App, the App ID will be prominently displayed, typically in the "About" section or near the top of the "General" tab. 
- **GITHUB_APP_INSTALLATION_ID**: GitHub App Installation ID
  - Default: None
  - Example: `12345678`
  - How to find it: [link](https://stackoverflow.com/questions/74462420/where-can-we-find-github-apps-installation-id)
- **GITHUB_APP_PRIVATE_KEY_PATH**: Path to the GitHub App private key
  - Default: None
  - Example: `/app/secrets/github-app-private-key.pem`
  - How to get it: 
    - Navigate to GitHub App Settings:
      - Click your profile picture in the upper-right corner of any GitHub page.
      - Go to your account settings. For personal accounts, click "Settings." For apps owned by an organization, click "Your organizations," then "Settings" next to the relevant organization.
      - In the left sidebar, click "Developer settings."
      - Select "GitHub Apps" from the left sidebar.
      - Locate the desired GitHub App and click "Edit" next to its name.
    - Generate Private Key:
      - On the GitHub App's settings page, scroll down to the "Private keys" section.
      - Click the "Generate a private key" button.
    - Download the Key:
      - A private key in PEM format will automatically download to your computer. This file contains the private key in a format suitable for authentication with the GitHub API. 

- **DEFAULT_REPO_PRIVATE**: Whether the default repository should be private
  - Default: `true`
  - Options: `true` | `false`
  - **Note**: If set to `true`, the default repository will be private.
- **REPO_TEMPLATE**: Template for the repository
  - Default: None





### Commit Message Configuration

- **COMMIT_MESSAGE_MODE**: Type of commit messages to generate
  - Default: `detailed`
  - Options: `generic` | `detailed`
  - **Note**: Detailed mode provides more descriptive commit messages

- **INCLUDE_METADATA**: Controls whether commit operations include notebook metadata
  - Default: `false`
  - Options: `true` | `false`
  - **Note**: Set to `false` for faster commits during development

- **ENABLE_FILE_CREATION_TRACKING**: Enable file creation tracking in the commit message.
  - Default: `false`

### Operation Debouncing

Prevents spam operations when cells are executed or notebooks are saved rapidly:

- **COMMIT_DEBOUNCE_SECONDS**: Delay before commit operations
  - Default: `30`
  - Example: `2` (wait 2 seconds)
  - **Note**: Set to 0 for immediate operation

- **PUSH_DEBOUNCE_SECONDS**: Delay before push operations
  - Default: `120`
  - Example: `5` (wait 5 seconds)
  - **Note**: Set to 0 for immediate operation

### Auto-save Configuration

- **AUTO_SAVE_ENABLED**: Enable automatic periodic saving and pushing
  - Default: `true`
  - Options: `true` | `false`

- **AUTO_SAVE_INTERVAL_MINUTES**: How often to auto-save and push
  - Default: `5`
  - Example: `10` (every 10 minutes)

### Frontend Configuration

- **CELL_EXECUTION_DETECTION_DELAY_MS**: Delay before enabling cell execution detection
  - Default: `1000` (1 second)
  - Example: `2000` (2 seconds)

- **HEALTH_CHECK_INTERVAL_MS**: How often to check sidecar health
  - Default: `30000` (30 seconds)
  - Example: `15000` (15 seconds)

- **HEALTH_CHECK_TIMEOUT_MS**: Timeout for individual health check requests
  - Default: `5000` (5 seconds)
  - Example: `3000` (3 seconds)

- **API_REQUEST_TIMEOUT_MS**: Timeout for API requests to backend/sidecar
  - Default: `30000` (30 seconds)
  - Example: `60000` (60 seconds for slower operations)

- **NOTIFICATION_AUTO_DISMISS_MS**: How long notifications stay visible
  - Default: `5000` (5 seconds)
  - Example: `10000` (10 seconds)

### UI Button Control

Enable or disable specific UI buttons (when disabled, buttons appear grayed out and are not clickable):

- **ENABLE_COMMIT_BUTTON**: Enable/disable the Commit button
  - Default: `false`
  - Options: `true` | `false`

- **ENABLE_PUSH_BUTTON**: Enable/disable the Push button
  - Default: `false`
  - Options: `true` | `false`

- **ENABLE_LOCK_BUTTON**: Enable/disable the Lock button
  - Default: `false`
  - Options: `true` | `false`

### Real-Time Collaboration (RTC) Configuration

Controls frontend handling of RTC (Real-Time Collaboration) features:

- **ENABLE_RTC_HANDLING**: Enable/disable frontend RTC prefix handling
  - Default: `false`
  - Options: `true` | `false`
  - **Important**: When RTC is disabled at the server level (`YDocExtension.disable_rtc=True`), this should also be set to `false` to prevent path conflicts between frontend and backend
  - **Note**: If RTC is enabled at the server level, set this to `true` to enable proper RTC prefix stripping in the frontend

#### RTC Configuration Notes:
- **Server-side RTC disabled**: Use `ENABLE_RTC_HANDLING=false` (recommended for most deployments)
- **Server-side RTC enabled**: Use `ENABLE_RTC_HANDLING=true` to handle `RTC:` prefixes properly
- **Path conflicts**: Mismatched RTC settings between frontend and backend can cause file operation errors



### Logging Configuration

- **LOG_LEVEL**: Logging verbosity level
  - Default: `INFO`
  - Options: `DEBUG` | `INFO` | `WARNING` | `ERROR`
  - **Note**: DEBUG shows verbose output including environment loading details


