import logging

import click
import typer

from .commands.context import context_app as context
from .commands.contexts import contexts
from .commands.milestone import milestone_app as milestone
from .commands.new import new
from .commands.problem import problem_app as problem
from .commands.task import task_app as task
from .config import DEFAULTS
from .core.logging import configure_logging

app = typer.Typer(name="reerelease", help="A tool to manage development with simple markdown files")

# Add subcommand groups
app.add_typer(context, name="context", help="Manage contexts")
app.add_typer(task, name="task", help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Manage tasks")
app.add_typer(
    milestone,
    name="milestone",
    help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Manage milestones",
)
app.add_typer(
    problem,
    name="problem",
    help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Manage problems",
)


# Add individual deprecated commands
app.command()(new)
app.command()(contexts)


@app.command(hidden=True)
def emit_test_logs() -> None:
    """(test-only) Emit log messages at all levels for testing verbosity."""
    logger = logging.getLogger("reerelease")
    logger.debug("test-DEBUG: emit-test-logs called")
    logger.info("test-INFO: emit-test-logs called")
    logger.warning("test-WARNING: emit-test-logs called")
    logger.error("test-ERROR: emit-test-logs called")
    logger.critical("test-CRITICAL: emit-test-logs called")


# Typer callback to configure logging before running commands
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all logging and console output."
    ),
    verbosity: str = typer.Option(
        DEFAULTS.verbosity,
        "--verbosity",
        "-v",
        help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
    version: bool = typer.Option(
        DEFAULTS.quiet, "--version", help="Show version information and exit."
    ),
) -> None:
    """
    Global options for the reerelease tool.
    """
    if version:
        from reerelease.__about__ import __version__

        typer.echo(f"reerelease {__version__}")
        raise typer.Exit()

    level = getattr(logging, verbosity.upper(), logging.WARNING)
    configure_logging(level=level, quiet=quiet)


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
