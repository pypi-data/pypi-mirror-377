# git_lock_sign_jlx


A JupyterLab extension to automatically commit and push changes to a remote repository.

## Features

### Auto-commit

Cell execution is detected and the notebook is automatically committed.

### Auto-push

The auto-push is triggered when the user saves the notebook or after a certain amount of time.

## Documentation

See [docs/ENVIRONMENT_SETUP.md](docs/ENVIRONMENT_SETUP.md) for the environment setup.

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for the API reference for the sidecar service.

See [docs/AUTHENTICATION_CONFIGURATION.md](docs/AUTHENTICATION_CONFIGURATION.md) for git authentication configuration.

See [docs/DOCKER_BUILD_GUIDE.md](docs/DOCKER_BUILD_GUIDE.md) for quick Docker setup.

See [docs/SYNC_VALIDATION_IMPLEMENTATION.md](docs/SYNC_VALIDATION_IMPLEMENTATION.md) for sync validation implementation details.

See [docs/GIT_WORKTREE_ARCHITECTURE.md](docs/GIT_WORKTREE_ARCHITECTURE.md) for the git worktree architecture overview.

See [docs/PROGRAM_WORKFLOW.md](docs/PROGRAM_WORKFLOW.md) for the program workflow.

## Installation

1. Create and activate conda environment
```bash
conda create -n jlx --override-channels --strict-channel-priority -c conda-forge -c nodefaults jupyterlab=4 nodejs=18 git copier=7 jinja2-time
conda activate jlx
```

2. Install dependencies
```bash
jlpm install
```

3. Build extension
```bash
jlpm build
```

4. Install the extension
```bash
jupyter labextension develop --overwrite ./
```

5. Confirm installation
```bash
jupyter labextension list
```
