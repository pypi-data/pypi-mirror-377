import logging

import click
import typer

task_app = typer.Typer()


@task_app.command(help=click.style("[NOT IMPLEMENTED] ", fg="red") + "List all detected tasks")
def list(
    name: str = typer.Argument(
        None, help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Filter tasks by name"
    ),
) -> None:
    """List all detected tasks"""
    logger = logging.getLogger("reerelease")

    logger.debug("Listing tasks...")
    logger.critical("Not yet implemented")


if __name__ == "__main__":
    print("This module is intended to be used as a subcommand group and not run directly")
