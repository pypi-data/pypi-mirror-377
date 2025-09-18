"""Logger utility for the git lock and sign JupyterLab extension."""
import logging


def default_logger_config(logger: logging.Logger) -> None:
    """
    Configure the default logger for the application.

    This function sets up a basic logging configuration that outputs
    logs to the console with a specific format.
    """
    logger.setLevel(logging.INFO)  # Or logging.DEBUG for more verbose output
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(lineno)4d - %(levelname)8s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
