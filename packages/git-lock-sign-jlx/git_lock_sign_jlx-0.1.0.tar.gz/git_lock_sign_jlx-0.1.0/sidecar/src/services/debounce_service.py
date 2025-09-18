"""
Debounce service for CELN Sidecar

Prevents spam operations by implementing debouncing logic for commits and pushes.
"""

import logging
import time
from threading import Lock
from typing import Any, Dict

from .logger_util import default_logger_config

logger = logging.getLogger(__name__)
default_logger_config(logger)


class DebounceService:
    """Service for debouncing git operations to prevent spam."""

    def __init__(self):
        """Initialize the debounce service."""
        self._last_operation_times: Dict[str, float] = {}
        self._lock = Lock()
        logger.info("Debounce service initialized")

    def should_debounce(self, operation_key: str, debounce_seconds: int) -> bool:
        """
        Check if an operation should be debounced.

        Args:
            operation_key: Unique key for the operation (e.g., "commit:/path/to/notebook")
            debounce_seconds: Number of seconds to debounce

        Returns:
            True if the operation should be debounced (skipped), False otherwise
        """
        if debounce_seconds <= 0:
            return False

        current_time = time.time()

        with self._lock:
            last_time = self._last_operation_times.get(operation_key, 0)
            time_since_last = current_time - last_time

            if time_since_last < debounce_seconds:
                logger.debug(
                    f"Debouncing {operation_key}: {time_since_last:.1f}s < {debounce_seconds}s"
                )
                return True

            # Update the last operation time
            self._last_operation_times[operation_key] = current_time
            logger.debug(
                f"Allowing {operation_key}: {time_since_last:.1f}s >= {debounce_seconds}s"
            )
            return False

    def reset_debounce(self, operation_key: str) -> None:
        """
        Reset the debounce timer for a specific operation.

        Args:
            operation_key: Unique key for the operation
        """
        with self._lock:
            if operation_key in self._last_operation_times:
                del self._last_operation_times[operation_key]
                logger.debug(f"Reset debounce for {operation_key}")

    def get_time_until_next_allowed(
        self, operation_key: str, debounce_seconds: int
    ) -> float:
        """
        Get the time in seconds until the next operation is allowed.

        Args:
            operation_key: Unique key for the operation
            debounce_seconds: Number of seconds to debounce

        Returns:
            Time in seconds until next operation is allowed (0 if allowed now)
        """
        if debounce_seconds <= 0:
            return 0.0

        current_time = time.time()

        with self._lock:
            last_time = self._last_operation_times.get(operation_key, 0)
            time_since_last = current_time - last_time

            if time_since_last >= debounce_seconds:
                return 0.0

            return debounce_seconds - time_since_last

    def clear_all_debounces(self) -> None:
        """Clear all debounce timers."""
        with self._lock:
            self._last_operation_times.clear()
            logger.info("Cleared all debounce timers")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current debounce status for debugging.

        Returns:
            Dictionary with current debounce information
        """
        current_time = time.time()

        with self._lock:
            status = {
                "active_debounces": len(self._last_operation_times),
                "operations": {},
            }

            for key, last_time in self._last_operation_times.items():
                time_since = current_time - last_time
                status["operations"][key] = {
                    "last_operation": last_time,
                    "time_since_last": time_since,
                }

            return status
