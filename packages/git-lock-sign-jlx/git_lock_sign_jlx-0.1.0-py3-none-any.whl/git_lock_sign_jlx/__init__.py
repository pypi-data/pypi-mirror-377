"""Git Lock Sign JupyterLab Extension."""
try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode:
    # https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings

    warnings.warn("Importing 'git_lock_sign_jlx' outside a proper installation.")
    __version__ = "dev"

from .extension import setup_handlers


def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "git_lock_sign_jlx"
    }]


def _jupyter_server_extension_points():
    """Entry point for the server extension."""
    return [{
        "module": "git_lock_sign_jlx"
    }]


def _load_jupyter_server_extension(server_app):
    """Registers the API handlers to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_handlers(server_app.web_app)
    name = "git_lock_sign_jlx"
    server_app.log.info(f"Registered {name} server extension")


# For backward compatibility
_jupyter_server_extension_paths = _jupyter_server_extension_points
