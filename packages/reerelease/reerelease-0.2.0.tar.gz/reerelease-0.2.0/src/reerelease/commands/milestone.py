import logging

import click
import typer

milestone_app = typer.Typer()


@milestone_app.command(
    help=click.style("[NOT IMPLEMENTED] ", fg="red") + "List all detected milestones"
)
def list(
    name: str = typer.Argument(
        None, help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Filter milestones by name"
    ),
) -> None:
    """List all detected milestones."""
    logger = logging.getLogger("reerelease")

    logger.debug("Listing milestones...")
    logger.critical("Not yet implemented")


if __name__ == "__main__":
    print("This module is intended to be used as a subcommand group and not run directly")
