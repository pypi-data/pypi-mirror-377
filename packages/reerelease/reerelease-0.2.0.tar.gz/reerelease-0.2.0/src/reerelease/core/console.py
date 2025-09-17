"""Console output utilities."""

from typing import Any

from rich import print as rprint

from .logging import is_quiet_mode


def quiet_print(*args: Any, **kwargs: Any) -> None:
    """Print only if not in quiet mode."""
    if not is_quiet_mode():
        rprint(*args, **kwargs)
