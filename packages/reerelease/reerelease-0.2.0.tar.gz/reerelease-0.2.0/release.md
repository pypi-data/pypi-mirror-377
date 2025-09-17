# REErelease releases

## 0.2.0
Scalable command structure
*Release date:* 2025-09-16
*Release artifact:* [pypi](https://pypi.org/project/reerelease/0.2.0/)

**Improvement:**
- Improved command structure: added `context` command with subcommands (`list`, `add`, `remove`, `check`) and forwarded aliases `contexts` → `context list`, `new` → `context add`.
- Added skeleton commands for `task`, `problem`, and `milestone` to prepare for future task/problem management features.
- Integrated automatic hooks for linting, formatting, and type checking to run as part of the development workflow.
- Modular templating groundwork laid for later expansion into domain-specific templates and composition (no breaking changes to existing templates).
- Documentation and roadmap updated to reflect planned features and next milestones.


## 0.1.1
Minor metadata correction
*Release date:* 2025-09-08
*Release artifact:* [pypi](https://pypi.org/project/reerelease/0.1.0/)

**Correction:**
- Removed untested python version
- Added classifier for pypi publishing

## 0.1.0
Initial CLI & template creation
*Release date:* 2025-09-08
*Release artifact:* [pypi](https://pypi.org/project/reerelease/0.1.0/)

**New Commands:**
- `reerelease new <context-name> [path]` - Create new context with templates
- `reerelease contexts [path]` - Discover and display existing contexts

**Features:**
- Full Python TDD setup with automated testing and coverage
- Logging system with configurable verbosity levels
- Jinja2 templating engine for document generation
- Safe context creation (no overwriting existing contexts)
- Automatic context detection with name and path extraction
- Basic templates: release.md, roadmap.md, readme.md

**Foundation:**
Establishes the core architecture for template-based project documentation management with CLI interface and context discovery system.

**Known problem:**
- Very basic templating system
- Command structure not scalable
