"""New context creation command."""

import pathlib


def new(
    name: str,
    path: pathlib.Path,
) -> None:
    """Create a new context."""
    import logging

    # Log deprecation warning
    logger = logging.getLogger("reerelease")
    logger.warning(
        "'new' command is deprecated, redirecting to 'add context', Will be removed in v0.3"
    )

    # Delegate to add context functionality
    from .context import add

    # Typer passes path as str, so ensure it's a Path
    path_obj = pathlib.Path(path)
    base_path_str = str(path_obj)
    add(name, base_path_str)
