# GitHub Enterprise Integration Setup Guide

This guide explains how to set up the JupyterLab Git Extension with GitHub Enterprise using GitHub App authentication.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [GitHub App Setup](#github-app-setup)
3. [Local Development Setup](#local-development-setup)
4. [Production Deployment](#production-deployment)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Access
- **GitHub Enterprise Administrator Access**: Needed to create GitHub App
- **Organization Owner/Admin**: Required for GitHub App installation
- **Docker Environment**: For running the extension

### Technical Requirements
- Docker and Docker Compose
- Python 3.11+ (for testing scripts)
- Access to your GitHub Enterprise instance

## GitHub App Setup

### Step 1: Create GitHub App

1. Navigate to your GitHub Enterprise organization settings:
   ```
   https://github.yourcompany.com/organizations/YOUR_ORG/settings/apps
   ```

2. Click "**New GitHub App**" and configure:

   **Basic Information:**
   ```
   App Name: JupyterLab Git Extension
   Description: Automated git repository management for JupyterLab users
   Homepage URL: https://jupyter.yourcompany.com
   User authorization callback URL: [LEAVE BLANK]
   Webhook URL: [LEAVE BLANK]
   Webhook secret: [LEAVE BLANK]
   ```

   **Permissions (Repository level):**
   ```
   Contents: Read & Write
   Metadata: Read
   Administration: Write (for creating repositories)
   ```

   **Permissions (Organization level):**
   ```
   Members: Read (optional - for email validation)
   ```

   **Where can this GitHub App be installed?**
   ```
   ☑ Only on this account (YOUR_ORG)
   ```

3. Click "**Create GitHub App**"

### Step 2: Collect Credentials

After creating the app, collect these values:

```bash
# From the App settings page
GITHUB_APP_ID=123456                    # App ID
GITHUB_APP_CLIENT_ID=Iv1.abc123         # Client ID
```

**Download Private Key:**
1. Scroll down to "Private keys"
2. Click "**Generate a private key**"
3. Save the downloaded `.pem` file securely

### Step 3: Install the App

1. Go to organization installations:
   ```
   https://github.yourcompany.com/organizations/YOUR_ORG/settings/installations
   ```

2. Click "**Install**" on your new app
3. Choose repository access:
   - **All repositories** (recommended for organizational use)
   - **Selected repositories** (for limited testing)

4. Note the **Installation ID** from the URL:
   ```
   https://github.yourcompany.com/settings/installations/INSTALLATION_ID
   ```

## Local Development Setup

### Step 1: Clone and Prepare Environment

```bash
cd git_lock_sign_jlx/docker/

# Copy environment template
cp env.github-enterprise.template .env

# Create secrets directory
mkdir -p secrets
chmod 700 secrets
```

### Step 2: Configure Environment

Edit `.env` with your GitHub Enterprise details:

```bash
# GitHub Enterprise Configuration
# You can use either approach:

# Option 1: Use GITHUB_ENTERPRISE_URL (recommended for clarity)
GITHUB_ENTERPRISE_URL=https://github.yourcompany.com
GITHUB_ENTERPRISE_ORG=your-research-org

# Option 2: Use GIT_SERVER_URL (works with any git server type)
# GIT_SERVER_URL=https://github.yourcompany.com
# GITHUB_ENTERPRISE_ORG=your-research-org

# If both are set, GITHUB_ENTERPRISE_URL takes precedence
# If only one is set, that value is used for both

# GitHub App Credentials
GITHUB_APP_ID=123456
GITHUB_APP_INSTALLATION_ID=78910

# Repository Settings
DEFAULT_REPO_PRIVATE=true
REPO_TEMPLATE=jupyter-research-template  # Optional
ALLOWED_DOMAINS=yourcompany.com,contractor.com

# Git User Configuration
GIT_USER_NAME=Research User
GIT_USER_EMAIL=user@yourcompany.com
```

### Step 3: Add Private Key

```bash
# Copy your downloaded private key
cp ~/Downloads/your-app-name.private-key.pem secrets/github-app-private-key.pem
chmod 600 secrets/github-app-private-key.pem
```

### Step 4: Run Setup Script

```bash
# Automated setup and validation
./setup-github-enterprise.sh
```

This script will:
- ✅ Validate configuration
- ✅ Check private key format
- ✅ Set proper permissions
- ✅ Provide next steps

## Production Deployment

### Option 1: Docker Compose (Recommended for Small Teams)

```bash
# Start services
docker-compose up -d

# Check logs
docker-compose logs sidecar
docker-compose logs jupyterlab

# Access JupyterLab
open http://localhost:8888
```

### Option 2: Kubernetes (Recommended for Organizations)

See [Kubernetes deployment guide](KUBERNETES_DEPLOYMENT.md) for:
- Helm charts
- Multi-user JupyterHub integration
- Secrets management
- Ingress configuration

## Testing

### Automated Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install PyGithub PyJWT

# Run GitHub App tests
cd scripts/
python test_github_app.py
```

The test will validate:
- ✅ Configuration completeness
- ✅ GitHub App authentication
- ✅ Installation permissions
- ✅ Organization access
- ✅ Repository creation/deletion

### Manual Testing

1. **Start Services:**
   ```bash
   cd docker/
   docker-compose up -d
   ```

2. **Access JupyterLab:**
   ```
   http://localhost:8888
   Token: test
   ```

3. **Create Test Notebook:**
   - Create a new notebook: `test-notebook.ipynb`
   - Add some content and save
   - The extension should automatically:
     - Initialize git repository
     - Create repository in GitHub Enterprise
     - Commit and push content

4. **Verify in GitHub Enterprise:**
   - Check your organization for new repository
   - Verify repository contains notebook content
   - Confirm user has appropriate access

## Repository Template Setup (Optional)

For standardized repository structure:

### Step 1: Create Template Repository

1. Create repository in your organization: `jupyter-research-template`
2. Set as template repository in settings
3. Add standard files:
   ```
   ├── .gitignore          # Python/Jupyter gitignore
   ├── README.md           # Template README
   ├── environment.yml     # Conda environment
   └── notebooks/          # Standard directory
       └── .gitkeep
   ```

### Step 2: Configure Template Usage

In your `.env` file:
```bash
REPO_TEMPLATE=jupyter-research-template
```

New repositories will be created from this template.

## User Workflow

Once deployed, users experience seamless git operations:

### Automatic Setup
1. User opens JupyterLab
2. Creates/opens notebook
3. Extension automatically:
   - Creates personal repository in organization
   - Sets up git configuration
   - Enables git operations

### Daily Workflow
1. **Create Content:** Write notebooks normally
2. **Auto-Save:** Extension auto-commits on save
3. **View History:** Check git history in GitHub Enterprise
4. **Collaborate:** Share repository URL with colleagues

No manual git commands or repository setup required!

## User Management

### Adding New Users

1. **Email Domain:** Ensure user email matches `ALLOWED_DOMAINS`
2. **Repository Access:** Repositories created automatically
3. **Organization Membership:** Users don't need to be org members
4. **Access Control:** Handled through GitHub App permissions

### Repository Structure

**Single Repository Mode** (default):
```
Organization: your-research-org
├── user1-work/          # User 1's workspace
├── user2-work/          # User 2's workspace
└── user3-work/          # User 3's workspace
```

**Multiple Repository Mode:**
```
Organization: your-research-org
├── user1-project-alpha/
├── user1-experiment-2/
├── user2-analysis/
└── user2-modeling/
```

## Security Considerations

### GitHub App Permissions

The GitHub App has minimal required permissions:
- **Repository Contents:** Read/Write for git operations
- **Repository Administration:** Create repositories only
- **Organization Members:** Read-only for user validation

### Private Key Management

**Development:**
- Store in `docker/secrets/` (gitignored)
- Set permissions: `chmod 600`

**Production:**
- Use Kubernetes secrets
- Mount as read-only volume
- Regular key rotation recommended

### Network Security

**Development:**
- Docker internal networking
- Exposed ports: 8888 (JupyterLab), 8001 (Sidecar)

**Production:**
- Use HTTPS with proper certificates
- Configure firewall rules
- Enable authentication (OAuth/LDAP)

## Monitoring and Maintenance

### Health Checks

The system includes built-in health monitoring:

```bash
# Sidecar health
curl http://localhost:8001/health

# Service logs
docker-compose logs -f sidecar
```

### GitHub App Token Rotation

Installation tokens automatically expire and refresh (1-hour lifetime).

Private key rotation:
1. Generate new private key in GitHub App settings
2. Update `secrets/github-app-private-key.pem`
3. Restart services

### Repository Cleanup

Monitor organization for unused repositories:
- Repositories without recent commits
- Test repositories (created by test scripts)
- Abandoned user workspaces

## Troubleshooting

### Common Issues

**Configuration Errors:**
```bash
# Run setup script for validation
./setup-github-enterprise.sh

# Check environment variables
cat .env | grep GITHUB
```

**Authentication Failures:**
```bash
# Test GitHub App authentication
python scripts/test_github_app.py

# Check private key format
head -1 secrets/github-app-private-key.pem
```

**Repository Creation Failures:**
- Verify GitHub App installation
- Check organization permissions
- Confirm repository name uniqueness

**Push/Pull Failures:**
- Check git user configuration
- Verify repository access permissions
- Test network connectivity to GitHub Enterprise

### Debug Mode

Enable detailed logging:

```bash
# In .env file
LOG_LEVEL=DEBUG
SIDECAR_DEBUG=true

# Restart services
docker-compose restart sidecar
docker-compose logs -f sidecar
```

### Support Contacts

**For GitHub App Issues:**
- GitHub Enterprise Administrator
- Organization Owner

**For Extension Issues:**
- Development Team
- System Administrator

## Migration from GitLab/Gitea

If migrating from existing GitLab or Gitea deployment:

1. **Export Existing Data:**
   ```bash
   # Backup existing repositories
   # Export user configurations
   ```

2. **Update Configuration:**
   ```bash
   # Change git server
   GIT_SERVER=github_enterprise
   ```

3. **Migrate Repositories:**
   - Use GitHub's import tools
   - Or manual git clone/push process

4. **Update User Instructions:**
   - New repository URLs
   - Updated access procedures

The extension interface remains identical - only the backend changes.

---

## Quick Start Summary

For experienced administrators:

```bash
# 1. Create GitHub App in organization settings
# 2. Install app and collect credentials
# 3. Setup local environment
cd docker/
cp env.github-enterprise.template .env
# Edit .env with your values
mkdir -p secrets
cp ~/path/to/private-key.pem secrets/github-app-private-key.pem
chmod 600 secrets/github-app-private-key.pem

# 4. Test configuration
python ../scripts/test_github_app.py

# 5. Deploy
docker-compose up -d

# 6. Access JupyterLab
open http://localhost:8888
```

**That's it!** Your users can now create notebooks and the extension will automatically handle all git operations with GitHub Enterprise. 