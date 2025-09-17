import logging

import click
import typer

problem_app = typer.Typer()


@problem_app.command(
    help=click.style("[NOT IMPLEMENTED] ", fg="red") + "List all detected problems"
)
def list(
    name: str = typer.Argument(
        None, help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Filter problems by name"
    ),
) -> None:
    """List all detected problems."""
    logger = logging.getLogger("reerelease")

    logger.debug("Listing problems...")
    logger.critical("Not yet implemented")


if __name__ == "__main__":
    print("This module is intended to be used as a subcommand group and not run directly")
