# Sidecar Service Test Scripts

This directory contains comprehensive test scripts for validating the sidecar service functionality with different git providers.

## Available Tests

### 1. GitHub Enterprise Integration Test

**Purpose**: Test complete workflow with GitHub Enterprise using GitHub App authentication.

**Files**:
- `test_github_enterprise_workflow.py` - Main test script
- `run_github_enterprise_test.sh` - Shell wrapper script
- `.env.github-enterprise` - Environment configuration

**What it tests**:
1. Launches sidecar server with GitHub Enterprise configuration
2. Creates a test git repository locally  
3. Provisions repository in GitHub Enterprise organization (creates `liuji1031-work`)
4. Tests git operations: init, commit, push
5. Verifies repository creation in GitHub organization

**Usage**:
```bash
cd sidecar/src/test/
./run_github_enterprise_test.sh
```

**Prerequisites**:
- GitHub Enterprise organization with GitHub App configured
- `.env.github-enterprise` file with valid configuration
- GitHub App private key available

**Expected outcome**: Creates repository `https://github.com/YourOrg/liuji1031-work` with test notebook

### 2. GitHub App Authentication Test

**Purpose**: Test GitHub App credentials and permissions without full workflow.

**Files**:
- `test_github_app.py` - Authentication validation script
- `run_github_app_test.sh` - Shell wrapper

**Usage**:
```bash
./run_github_app_test.sh
```

### 3. Gitea Integration Test

**Purpose**: Test complete workflow with self-hosted Gitea server.

**Files**:
- `test_gitea_provision.py` - Main test script
- `run_gitea_test.sh` - Shell wrapper

**Usage**:
```bash
./run_gitea_test.sh
```

### 4. General Sidecar Workflow Test

**Purpose**: Test sidecar service with configurable git server (GitLab/Gitea).

**Files**:
- `test_sidecar_workflow.py` - Configurable workflow test
- `run_sidecar_test.sh` - Shell wrapper

**Usage**:
```bash
./run_sidecar_test.sh
```

## Configuration Files

### `.env.github-enterprise`

Required for GitHub Enterprise tests:

```bash
GIT_SERVER=github_enterprise
GIT_SERVER_URL=https://github.com/YourOrg  
GITHUB_ENTERPRISE_URL=https://github.com/YourOrg
GITHUB_ENTERPRISE_ORG=YourOrg
GITHUB_APP_ID=123456
GITHUB_APP_INSTALLATION_ID=78910
GITHUB_APP_PRIVATE_KEY_PATH=../../../docker/secrets/github-app-private-key.pem
```

## Test Workflow Overview

All test scripts follow this pattern:

1. **Environment Setup**: Load configuration, validate requirements
2. **Server Startup**: Launch sidecar service with uvicorn
3. **Repository Creation**: Create temporary git repository
4. **API Testing**: Test sidecar endpoints (init, provision, commit, push)
5. **Verification**: Confirm repository exists in remote git server
6. **Cleanup**: Stop server, remove temporary files

## Expected Results

### Successful GitHub Enterprise Test

```
🚀 GitHub Enterprise Sidecar Workflow Test
===========================================
📋 Loading configuration from .env.github-enterprise
✅ All required Python packages are available

📊 Configuration Summary:
   GitHub URL: https://github.com/JupyterTestOrg
   Organization: JupyterTestOrg
   App ID: 123456
   Installation ID: 78910
   Test User: liuji1031@live.com
   Expected Repository: JupyterTestOrg/liuji1031-work

🧪 Running GitHub Enterprise workflow test...

✅ Environment configured for GitHub Enterprise
📁 Creating test repository...
✅ Git repository initialized with user: liuji1031 <liuji1031@live.com>
🚀 Starting sidecar server...
✅ Server started successfully at http://localhost:8001

📋 Step 1: Initialize git repository
🌐 POST /sidecar/git-init -> HTTP 200
✅ Git repository initialized successfully

📋 Step 2: Provision repository in GitHub Enterprise
🎯 Expected repository: JupyterTestOrg/liuji1031-work
🌐 POST /sidecar/provision -> HTTP 200
✅ Repository provisioned successfully
🌐 Repository URL: https://github.com/JupyterTestOrg/liuji1031-work

📋 Step 3: Commit notebook file
🌐 POST /sidecar/commit -> HTTP 200
✅ File committed successfully

📋 Step 4: Push to GitHub Enterprise
🌐 POST /sidecar/push -> HTTP 200
✅ Files pushed successfully

📋 Step 5: Verification
🎉 SUCCESS! Repository created at: https://github.com/JupyterTestOrg/liuji1031-work

🎉 GitHub Enterprise test completed successfully!

✅ Next steps:
   1. Check your GitHub organization: https://github.com/JupyterTestOrg
   2. Look for repository: liuji1031-work
   3. Verify the test notebook was uploaded

🚀 You can now test the full JupyterLab extension!
```

## Troubleshooting

### Common Issues

**Authentication Failures**:
- Verify GitHub App ID and Installation ID
- Check private key file exists and has correct permissions
- Confirm GitHub App has required permissions

**Server Startup Failures**:
- Check if port 8001 is available
- Verify Python dependencies are installed
- Check environment configuration

**Repository Creation Failures**:
- Verify GitHub App installation in organization
- Check organization name matches configuration
- Confirm user email domain is allowed

### Debug Mode

For detailed logging, set environment variable:
```bash
export LOG_LEVEL=DEBUG
./run_github_enterprise_test.sh
```

### Manual Cleanup

If tests fail and leave resources:
```bash
# Stop any running sidecar processes
pkill -f "uvicorn.*main:app"

# Remove temporary test directories
rm -rf /tmp/github_enterprise_test_*
```

## Integration with JupyterLab Extension

After successful test completion:

1. **Local Development**: Use test configuration for local JupyterLab testing
2. **Docker Deployment**: Copy test configuration to `docker/.env`
3. **Production**: Adapt configuration for production environment

The test scripts validate the same API endpoints used by the JupyterLab extension frontend. 