# PyPI Publishing Scripts

This directory contains automation scripts for publishing the `git_lock_sign_jlx` JupyterLab extension to PyPI.

## 🚀 Quick Start

1. **First time setup:**
   ```bash
   ./setup.sh
   ```

2. **Build the package:**
   ```bash
   ./build.sh
   ```

3. **Test locally:**
   ```bash
   ./test-local.sh
   ```

4. **Publish to TestPyPI:**
   ```bash
   ./publish-test.sh
   ```

5. **Publish to PyPI:**
   ```bash
   ./publish.sh
   ```

## 📁 Script Reference

| Script | Purpose |
|--------|---------|
| `setup.sh` | Install build tools (build, twine) |
| `build.sh` | Clean and build the package (frontend + backend) |
| `test-local.sh` | Install and test the wheel locally |
| `publish-test.sh` | Upload to TestPyPI for testing |
| `publish.sh` | Upload to production PyPI |
| `check-version.sh` | Check version info and provide update guidance |
| `clean.sh` | Remove all build artifacts |

## 🔧 Prerequisites

### Conda Environment

These scripts expect a conda environment named `jlx`. If you're using a different environment name, update the `conda activate` lines in all scripts.

To check your current environment:
```bash
conda info --envs
```

### PyPI Account Setup

1. Create accounts:
   - [PyPI](https://pypi.org) (production)
   - [TestPyPI](https://test.pypi.org) (testing)

2. Generate API tokens:
   - PyPI: Account Settings → API tokens
   - TestPyPI: Account Settings → API tokens

3. Create `~/.pypirc`:
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   repository = https://upload.pypi.org/legacy/
   username = __token__
   password = pypi-your-api-token-here

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-your-test-api-token-here
   ```

## 📦 Version Management

- Edit version in `package.json`
- `pyproject.toml` syncs automatically via `hatch-nodejs-version`
- Use semantic versioning: `X.Y.Z`

## 🔄 Publishing Workflow

### For New Releases:

1. **Update version** in `package.json`
2. **Clean build**: `./clean.sh`
3. **Build package**: `./build.sh`
4. **Test locally**: `./test-local.sh`
5. **Test on TestPyPI**: `./publish-test.sh`
6. **Verify TestPyPI**: Install and test from TestPyPI
7. **Publish to PyPI**: `./publish.sh`

### For Development:

- Use `./clean.sh` and `./build.sh` to test builds
- Use `./test-local.sh` to verify changes work

## 🎯 After Publishing

Your extension will be available as:
```bash
pip install git-lock-sign-jlx
```

Your Docker installation becomes:
```yaml
- install-git-lock-sign-extension: |
    pip install git-lock-sign-jlx && \
    jupyter labextension list
```

## 🔗 Useful Links

- **PyPI Package**: https://pypi.org/project/git-lock-sign-jlx/
- **TestPyPI Package**: https://test.pypi.org/project/git-lock-sign-jlx/
- **JupyterLab Extension Guide**: https://jupyterlab.readthedocs.io/en/stable/extension/extension_dev.html

## 🐛 Troubleshooting

- **Conda activation fails**: Ensure conda is installed and the `jlx` environment exists
- **Build fails**: Check if `jlpm install` completed successfully in your environment
- **Upload fails**: Verify API tokens in `~/.pypirc`
- **Version conflict**: Update version in `package.json` and rebuild
- **Permission errors**: Make scripts executable: `chmod +x *.sh`
- **Wrong environment**: Update environment name in scripts if not using `jlx`
