"""Context detection and management utilities."""

import logging
import os
import pathlib
from typing import List, Tuple

from ..config import DEFAULTS
from .templates import TemplateManager


def extract_context_name(context_path: pathlib.Path, required_files: List[str]) -> str:
    """Extract context name from a context directory, defaulting to directory name."""
    context_name = context_path.name  # Default to directory name

    # Look for a readme file to extract the context name
    for file in required_files:
        if "readme" in file.lower():
            readme_path = context_path / file
            try:
                content = readme_path.read_text(encoding="utf-8")
                # Simple extraction: look for first # heading
                for line in content.split("\n"):
                    line = line.strip()  # Remove leading/trailing whitespace
                    if line.startswith("#") and len(line) > 1 and line[1].isspace():
                        # Extract everything after '# ' and strip whitespace
                        context_name = line[1:].strip()
                        break
            except Exception as e:
                logger = logging.getLogger("reerelease")
                logger.debug("Could not read context name from %s: %s", readme_path, e)
            break

    return context_name


def find_contexts(
    scan_path: pathlib.Path, max_depth: int = DEFAULTS.search_depth
) -> List[Tuple[str, pathlib.Path]]:
    """Find all contexts in a directory tree."""
    logger = logging.getLogger("reerelease")

    # Get required files from templates
    template_manager = TemplateManager()
    template_files = template_manager.get_templates("context")
    if not template_files:
        logger.warning("No template files found for category context")
        return []

    required_files = [output_name for _, output_name in template_files]
    logger.debug("Looking for contexts with files: %s", required_files)

    # Scan directory and subdirectories for contexts
    detected_contexts = []

    # Pre-resolve base path for relative depth calculations
    base_resolved = scan_path.resolve()

    # Look for directories containing all required context files
    for search_path in [scan_path] + list(scan_path.rglob("*")):  # Include the root path itself
        if not search_path.is_dir():
            continue

        # Compute relative depth under the scan root and skip if deeper than max_depth
        try:
            rel = search_path.resolve().relative_to(base_resolved)
            # depth: number of path segments below base minus one so that
            # base/level1 -> len(parts)=1 -> rel_depth=0
            rel_depth = len(rel.parts) - 1
        except Exception:
            # If it cannot be made relative (e.g., ValueError from patched Path.relative_to),
            # attempt a safe fallback: check whether the resolved path is actually
            # inside the base_resolved using commonpath. If it's outside (for
            # example, a symlink that points outside the scan root), skip it.
            resolved = search_path.resolve()
            try:
                common = os.path.commonpath([str(resolved), str(base_resolved)])
            except Exception:
                # If commonpath cannot be computed for any reason, skip
                continue

            if common != str(base_resolved):
                # Path resolves outside the base scan root (e.g., symlink to external)
                continue

            # Otherwise, the resolved path appears to be inside the base; compute
            # a rel_depth using os.path.relpath as a fallback
            rel = pathlib.Path(os.path.relpath(str(resolved), str(base_resolved)))
            rel_depth = len(rel.parts) - 1

        if max_depth is not None and rel_depth > max_depth:
            # Skip directories deeper than allowed
            continue

        # Check if this directory has all required files
        if all((search_path / file).exists() for file in required_files):
            # Extract context name using helper function
            context_name = extract_context_name(search_path, required_files)

            detected_contexts.append((context_name, search_path.resolve()))
            logger.debug("Found context: %s at %s", context_name, search_path)

    return detected_contexts


def is_valid_context(context_path: pathlib.Path, category: str = "context") -> bool:
    """Check if a directory is a valid context."""
    template_manager = TemplateManager()
    template_files = template_manager.get_templates(category)
    required_files = [output_name for _, output_name in template_files]

    return all((context_path / file).exists() for file in required_files)
