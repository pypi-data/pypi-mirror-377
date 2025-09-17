import logging
import pathlib as pathlib
from datetime import datetime

import click
import typer
from rich.tree import Tree

from ..config import DEFAULTS
from ..core.console import quiet_print
from ..core.context import find_contexts
from ..core.templates import TemplateManager

context_app = typer.Typer()


@context_app.callback(invoke_without_command=True)
def _context_default(
    ctx: typer.Context, path: str = typer.Option(".", help="Path to search the context")
) -> None:
    """Default behavior when `context` is called without a subcommand: show the list."""
    # If a subcommand was invoked, do nothing here
    if ctx.invoked_subcommand is not None:
        return

    # Otherwise call the list command
    list(path)


@context_app.command(help="List all detected contexts")
def list(
    path: str = typer.Option(".", help="Path to search the context", show_default=True),
    depth: int = typer.Option(
        DEFAULTS.search_depth,
        "--depth",
        "-d",
        help="Depth of context searching and listing",
        show_default=True,
    ),
) -> None:
    """List all detected contexts."""
    logger = logging.getLogger("reerelease")

    # Convert string path to Path object
    path_obj = pathlib.Path(path)
    abs_path = path_obj.resolve()

    logger.debug("Listing contexts %d deep at %s", depth, path_obj)

    # Ensure the path exists
    if not path_obj.exists():
        quiet_print(f"❌ Path does not exist: {path_obj}")
        logger.error("Path does not exist: %s", path_obj)
        raise typer.Exit(1)

    if not path_obj.is_dir():
        quiet_print(f"❌ Path is not a directory: {path_obj}")
        logger.error("Path is not a directory: %s", path_obj)
        raise typer.Exit(1)

    # Find contexts
    detected_contexts = find_contexts(path_obj)

    # Display results in tree format
    if detected_contexts:
        # Sort contexts by path depth to show hierarchy naturally
        detected_contexts.sort(key=lambda x: (len(x[1].parts), str(x[1])))

        # Build a simple hierarchical structure
        nodes = {}  # path -> tree_node

        # Try to find a context that is exactly the resolved path
        root_context = None
        for context_name, context_path in detected_contexts:
            if context_path == abs_path:
                root_context = (context_name, context_path)
                break

        # Determine tree root label. If a root context exists, embed its name
        # in the second line of the title so it doesn't get a tree connector;
        # otherwise show a plain '(.)' on the second line.
        if root_context is None:
            tree = Tree(
                f"📂 Found {len(detected_contexts)} context(s) in [yellow]{abs_path}[/yellow]\n[dim](.)[/dim]"
            )
            root_node = tree
        else:
            root_name, root_path = root_context
            tree = Tree(
                f"📂 Found {len(detected_contexts)} context(s) in [yellow]{abs_path}[/yellow]\n[green]{root_name}[/green] [dim](.)[/dim]"
            )
            root_node = tree
            nodes[str(root_path)] = root_node

        for context_name, context_path in detected_contexts:
            try:
                # Skip the root context itself if we already represented it in the title
                if root_context is not None and context_path == root_context[1]:
                    continue

                rel_path = context_path.relative_to(abs_path)

                # Find the deepest ancestor that is also a context
                parent_node = None
                current_parent = context_path.parent

                while current_parent != abs_path:
                    parent_node = nodes.get(str(current_parent))
                    if parent_node is not None:
                        break
                    current_parent = current_parent.parent

                # Attach to the found parent or the root node
                label = f"[green]{context_name}[/green] [dim]({rel_path})[/dim]"
                if parent_node is None:
                    current_node = root_node.add(label)
                else:
                    current_node = parent_node.add(label)

                nodes[str(context_path)] = current_node

            except ValueError:
                # Fallback to absolute path if relative calculation fails
                tree.add(f"[green]{context_name}[/green] [dim]({context_path})[/dim]")

        quiet_print(tree)
        logger.info("Found %d contexts", len(detected_contexts))
    else:
        # No contexts found at all, show a minimal tree indicating the search path
        tree = Tree(f"📭 Found 0 context(s) in [yellow]{abs_path}[/yellow]")
        tree.add("[dim](.)[/dim]")
        quiet_print(tree)
        logger.info("No contexts found")


@context_app.command(help="Add a new context")
def add(
    name: str = typer.Argument(..., help="Name of the context to add"),
    path: str = typer.Option(".", help="Path to create the context in", show_default=True),
    inplace: bool = typer.Option(
        False, "--inplace", "-i", help="Create context in the specified path without subfolder"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Disable overwriting checks",
    ),
) -> None:
    """Add a new context."""
    logger = logging.getLogger("reerelease")

    # Resolve and validate path
    path_obj = pathlib.Path(path).resolve()

    logger.debug("Adding context: %s at %s, inplace: %b, force: %b", name, path_obj, inplace, force)

    # Validate context name
    if not name or not name.strip():
        logger.error("Context name cannot be empty")
        raise typer.Exit(2)

    if " " in name:
        logger.error("Context name cannot contain spaces")
        raise typer.Exit(2)

    if "/" in name or "\\" in name:
        logger.error("Context name cannot contain path separators")
        raise typer.Exit(2)

    # Implement the actual context creation logic
    # Create template manager
    template_manager = TemplateManager()

    # Create context path
    base_path = pathlib.Path(path)
    # When --inplace is given create files directly in the provided path,
    # otherwise create a subdirectory named after the context.
    context_path = base_path if inplace else (base_path / name)

    # Check if target directory already exists and is not empty
    if context_path.exists() and any(context_path.iterdir()):
        # Log the error for diagnostics and print a quiet, user-facing message
        logger.error("Target directory already exists and is not empty")
        raise typer.Exit(1)

    # Print creation message
    quiet_print(f"➕ Creating files for context: {name} at {context_path}")

    # Prepare template context
    template_context = {
        "context_name": name,
        "context_path": str(context_path.absolute()),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }

    # Create files from templates
    try:
        template_manager.create_files_from_templates("context", template_context, context_path)
        quiet_print(
            f"🎉 [green]Successfully created context[/green] [blue]{name}[/blue] at {context_path}"
        )
    except Exception as e:
        quiet_print(f"❌ [red]Failed to create context:[/red] {e}")
        raise typer.Exit(1) from e


@context_app.command(help="Remove an existing context")
def remove(
    name: str = typer.Argument(..., help="Name of the context to remove"),
    path: str = typer.Option(".", help="Path to search the context", show_default=True),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Disable checks and confirmations",
    ),
) -> None:
    """Remove an existing context."""
    logger = logging.getLogger("reerelease")

    # Resolve and validate path
    path_obj = pathlib.Path(path).resolve()

    logger.debug("Removing context: %s at %s, force: %b", name, path_obj, force)
    pass


@context_app.command(help="Check the status of a context")
def check(
    name: str = typer.Argument("*", help="Name of the context to check"),
    path: str = typer.Option(".", help="Path to search the context", show_default=True),
) -> None:
    """Check the status of a context."""
    logger = logging.getLogger("reerelease")

    # Resolve and validate path
    path_obj = pathlib.Path(path).resolve()

    logger.debug("Checking context: %s at %s", name, path_obj)
    pass


if __name__ == "__main__":
    print("This module is intended to be used as a subcommand group and not run directly")
