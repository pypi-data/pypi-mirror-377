from dataclasses import dataclass


@dataclass(frozen=True)
class Defaults:
    """Configuration defaults for reerelease."""

    verbosity: str = "WARNING"
    quiet: bool = False
    search_depth: int = 10
    milestone: str = "backlog"
    task_priority: str = "medium"
    problem_severity: str = "major"


DEFAULTS = Defaults()
