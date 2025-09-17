"""Template management for different domains."""

import logging
import pathlib
from datetime import datetime
from typing import Any, List, Tuple, Union

from jinja2 import Environment, PackageLoader, select_autoescape


class TemplateManager:
    """Manages templates for different domains (context, task, milestone)."""

    def __init__(self) -> None:
        """Initialize the template manager with Jinja2 environment."""
        self.env = self._get_jinja_env()
        self.logger = logging.getLogger("reerelease")

    def _get_jinja_env(self) -> Environment:
        """Get Jinja2 environment with custom filters."""
        env = Environment(
            loader=PackageLoader("reerelease", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Add custom filter for date formatting
        def strftime_filter(date_obj: Union[str, datetime], format_str: str) -> str:
            if date_obj == "now":
                return datetime.now().strftime(format_str)
            if isinstance(date_obj, str):
                # If it's a string and not "now", return it as-is or handle as needed
                return date_obj
            return date_obj.strftime(format_str)

        env.filters["strftime"] = strftime_filter
        return env

    def get_templates(self, category: str) -> List[Tuple[str, str]]:
        """Get template files for a category (context, task, milestone)."""
        # Validate category
        valid_categories = {"context", "task", "milestone", "domain"}
        if category not in valid_categories:
            raise ValueError(
                f"Unknown template category: {category}. Valid options: {valid_categories}"
            )

        # Get the templates directory from the package
        package_path = pathlib.Path(__file__).parent.parent
        templates_dir = package_path / "templates" / category

        if not templates_dir.exists():
            self.logger.error(f"No templates directory found for category: {category}")
            return []

        template_files = []
        for template_file in templates_dir.glob("*.j2"):
            # Remove .j2 extension to get output filename
            output_name = template_file.stem
            # Template name includes category path for Jinja2
            template_name = f"{category}/{template_file.name}"
            template_files.append((template_name, output_name))

        return template_files

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with the given context."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def create_files_from_templates(
        self, category: str, context: dict[str, Any], target_path: pathlib.Path
    ) -> None:
        """Create files from templates in the specified category."""
        # Get templates for the category
        template_files = self.get_templates(category)

        if not template_files:
            self.logger.debug(
                f"in get_templates() no template files found for category '{category}'"
            )
            return

        # Ensure target directory exists
        target_path.mkdir(parents=True, exist_ok=True)

        # Create files from templates
        for template_name, output_name in template_files:
            try:
                # Render template
                content = self.render_template(template_name, context)

                # Write file
                output_file = target_path / output_name
                output_file.write_text(content, encoding="utf-8")

                self.logger.debug(f"Created {output_name}")

            except Exception as e:
                self.logger.error(f"Failed to create {output_name}: {e}")
                raise
