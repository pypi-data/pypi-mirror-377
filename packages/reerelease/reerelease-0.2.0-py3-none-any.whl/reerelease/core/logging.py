"""Logging configuration for reerelease."""

import logging
import sys

# Global state for quiet mode
_QUIET_MODE = False


def configure_logging(*, level: int = logging.WARNING, quiet: bool = False) -> None:
    """Configure a simple, blocking console logger."""
    global _QUIET_MODE
    _QUIET_MODE = quiet

    log = logging.getLogger("reerelease")

    # Clear any handlers configured by previous tests
    if log.hasHandlers():
        log.handlers.clear()

    if quiet:
        log.addHandler(logging.NullHandler())
        return

    log.setLevel(level)
    handler: logging.Handler
    try:
        from rich.logging import RichHandler

        # Send logs to stderr (default for RichHandler)
        handler = RichHandler(rich_tracebacks=True, show_path=False, level=level)
        handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
    except ImportError:
        # Explicitly send logs to stderr
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        handler.setLevel(level)

    log.addHandler(handler)
    log.propagate = False  # Prevent passing messages to the root logger


def is_quiet_mode() -> bool:
    """Check if quiet mode is enabled."""
    return _QUIET_MODE
