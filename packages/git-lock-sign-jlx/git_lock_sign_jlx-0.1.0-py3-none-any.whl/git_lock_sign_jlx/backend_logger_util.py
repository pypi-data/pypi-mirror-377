"""Logger utility for the git lock and sign JupyterLab extension."""
import logging
import os
import sys


def backend_default_logger_config(logger: logging.Logger) -> None:
    """
    Configure the default logger for the application.

    This function sets up a basic logging configuration that outputs
    logs to the console with a specific format.
    """
    # Allow environment variable to control log level
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    logger.setLevel(numeric_level)

    # Avoid adding duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Add prefix to make extension logs easier to spot
        logger.info(
            "🔧 Git Lock and Sign JupyterLab Extension logger initialized (level: %s)",
            log_level,
        )
        logger.propagate = False
