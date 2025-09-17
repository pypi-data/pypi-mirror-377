"""Contexts listing command."""

import pathlib

import typer


def contexts(
    path: str = typer.Argument(
        ".", help="Path to scan for contexts (defaults to current directory)"
    ),
) -> None:
    """List all detected contexts."""
    import logging

    # Log deprecation warning
    logger = logging.getLogger("reerelease")
    logger.warning(
        "'contexts' command is deprecated, redirecting to 'list context', Will be removed in v0.3"
    )

    # Import and call the list context command
    from .context import list

    # Convert string path to Path object
    path_obj = pathlib.Path(path)

    # Call the list context command
    list(str(path_obj))
