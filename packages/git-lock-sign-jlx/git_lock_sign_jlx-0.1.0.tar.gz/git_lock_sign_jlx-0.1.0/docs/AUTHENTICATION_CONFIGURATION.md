# Git Authentication Configuration

This document explains how git authentication works in the JupyterLab extension.

## Overview

The extension uses **embedded credentials** for all git operations. This means authentication tokens are embedded directly in the remote URLs for git operations.

## How It Works

- **ALL remotes** (origin, gitea-push, gitlab-push, etc.) use URLs with embedded credentials
- Git operations use the embedded credentials directly
- **Credentials are stored in git configuration** - this is the standard approach for git authentication

## Example Remote URLs

```
origin: http://admin:token@localhost:3000/test_user_6/work.git
gitea-push: http://admin:token@localhost:3000/test_user_6/work.git
gitlab-push: https://oauth2:token@gitlab.example.com/user/repo.git
```

## Operations Supported

- ✅ `git fetch` - Uses embedded credentials
- ✅ `git pull` - Uses embedded credentials
- ✅ `git push` - Uses embedded credentials
- ✅ `git status` - Uses embedded credentials

## Security Considerations

- **Credentials are stored in git configuration** - this is standard git behavior
- **Anyone with access to the repository can see credentials** - this is expected in git workflows
- **Higher reliability** - works consistently across all environments

## Provider-Specific Authentication

### Gitea
- Uses admin token with admin username
- Format: `http://admin:token@host/path/repo.git`

### GitLab
- Uses OAuth2 token
- Format: `https://oauth2:token@host/path/repo.git`

### GitHub Enterprise
- Uses installation token with x-access-token username
- Format: `https://x-access-token:token@host/path/repo.git`

## Troubleshooting

### Authentication Failures
- Check that tokens are valid and not expired
- Verify the correct username format for your git provider
- Ensure the token has the necessary permissions

### Token Refresh
- Tokens are automatically refreshed when they expire
- Check sidecar logs for token refresh messages
- Ensure your git provider credentials are properly configured