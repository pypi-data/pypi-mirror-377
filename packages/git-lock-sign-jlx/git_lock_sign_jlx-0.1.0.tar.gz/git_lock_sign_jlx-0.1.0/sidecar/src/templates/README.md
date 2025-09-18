# CELN Sidecar Templates

This directory contains template files used by the CELN sidecar service.

## Templates

### gitignore.template

A comprehensive `.gitignore` template for JupyterLab environments that includes:

- **JupyterLab/Jupyter files**: `.ipynb_checkpoints/`, `.jupyter/`
- **User configuration files**: `.gitconfig`, `.gnupg/`, `.local/`, `.cache/`, etc.
- **Python development files**: `__pycache__/`, `*.py[cod]`, distribution files
- **Development environments**: `.env`, `.venv`, `env/`, etc.
- **IDE files**: `.vscode/`, `.idea/`, editor swap files
- **OS-generated files**: `.DS_Store`, `Thumbs.db`, etc.
- **Multi-language support**: Node.js, R, MATLAB kernel files

## Usage

Templates are automatically loaded by the `GitService._load_template()` method when repositories are initialized.

## Maintenance

To update the `.gitignore` template:

1. Edit `gitignore.template` directly
2. Test with new repositories to ensure patterns work correctly
3. Consider backward compatibility with existing repositories

## Adding New Templates

1. Create a new `.template` file in this directory
2. Update the `GitService._load_template()` method to handle fallbacks
3. Add usage documentation here

## Fallback Behavior

If template files cannot be found, the GitService will use minimal fallback content to ensure functionality continues to work.
