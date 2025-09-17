# REErelease roadmap

## Unassigned

Unschedule but planned development
- [ ] advanced template composition with dependency resolution between sections
- [ ] (MAYBE) bulk section operations (add multiple related sections in single command)
- [ ] capability to release multiple ready *milestone* at the same-time (will still be different commit)
- [ ] (MAYBE) template inheritance chains (base → domain → project-specific customizations)
- [ ] (MAYBE) template variable inheritance system from context to sections to domains


## 0.7.0

Advanced modular template system
*Target release date:*

- [ ] domain-specific template library expansion (embedded systems, web development, data science, etc)
- [ ] template marketplace/registry concept for community-contributed sections
- [ ] intelligent template suggestion based on context analysis and file patterns
- [ ] template validation system to ensure section compatibility and variable consistency
- [ ] automated cross-linking maintenance when sections are added/removed/modified
- [ ] mixed domain support within single context for mono-repo patterns
- [ ] section template composition system for combining multiple sections
- [ ] `milestone` command
  - [ ] `add` `--domain` specify a specific *domain* covered by this *milestone*
- [ ] modular template functionality, `context add CONTEXT --domain DOMAIN1,DOMAIN2,etc`
  - [ ] modular template architecture with base/sections/domains structure
  - [ ] domain-specific template sections (python/pcb/rust/firmware/etc) with explicit selection
  - [ ] smart parsing to detect existing structure and insert sections appropriately
  - [ ] template section insertion mechanism with marker-based parsing (`<!-- reerelease:section_name -->`)
  - [ ] complete release *template*
  - [ ] complete roadmap *template*
  - [ ] complete readme *template*

## 0.6.0

Tasks management improvement
*Target release date:*

- [ ] *subtask* capabilities (parsing, mapping, auto-parent-completion, etc)
- [ ] *problem* to *task* resolution linking
- [ ] *Developper* listing and linking in readme
- [ ] *Tasks* *labels* definition in readme
- [ ] section template versioning and update mechanism
- [ ] `context` command
  - [ ] `add` `--force` skipping overwriting check
  - [ ] `remove` `--force` skipping confirmation check
- [ ] `task` command
  - [ ] `add` `--label` adding a tasks with specified labels from a list (from context)
  - [ ] `add` `--assign` assigning the new task to one of the developper listed (from context)
  - [ ] `remove` `--force` skipping confirmation check
- [ ] `problem` command
  - [ ] `add` `--notask` disabling the auto-creation of a resolving *tasks* for *problems*
  - [ ] `add` `--solve_milestone` determining which milestone the resolving *task* is attached to
  - [ ] `add` `--assign` assigning the resolving task to one of the developper listed (from context)
  - [ ] `add` `--severity` designating a severity to the *problem* and the resolving *task*
  - [ ] `remove` `--force` skipping confirmation check
- [ ] `milestone` command
  - [ ] `remove` `--force` skipping confirmation check


## 0.5.0

Release functionnality
*Target release date:*

- [ ] additional execution hook at pre/post `release` command
- [ ] additional execution hook for documentation at post `update` command
- [ ] cross-reference generation between roadmap and release sections automatically
- [ ] `milestone` `release` command
  - [ ] `--context` and `--path` arguments
  - [ ] `--dry-run` to try the release without doing it
  - [ ] `--message` giving the actual message for the release
  - [ ] release title and message (saved to both release.md and git history)
  - [ ] automatic date tagging
  - [ ] automatic git tagging
  - [ ] automatic update of release file and completed defined *task* for a *milestone*
  - [ ] automatic linking between release and roadmap files


## 0.4.0

Task and problem functionnality
Updated and functionnal templates
*Target release date:*

- [ ] global variable scope per context with conflict-safe naming conventions
- [ ] fixed configuration system for repeating patterns across large mono-repos
- [ ] ignoring mecanism to skip folder under the root context (useful for external lib that would use reerelease)
- [ ] *task* functionality
  - [ ] automatic unique id assigned to each *tasks* (within a context)
- [ ] `task` command
  - [ ] `list` discovers and show all the *task* with `--context` and `--path` arguments
  - [ ] `add` add a *task* to a context with `--context`, `--path` and `--milestone` arguments
  - [ ] `remove` deletes a task with `--context` and `--path` arguments
- [ ] *problem* functionality
  - [ ] automatic unique id assigned to each *problem* (based on root context)
- [ ] `problem` command
  - [ ] `list` discovers and show all the *problems* with `--context` and `--path` arguments
  - [ ] `add` add a *problem* to a context with `--context`, `--path` and `--milestone` arguments
  - [ ] `resolve` completes a problem with `--context`, `--path` and `--comment` arguments
  - [ ] `remove` deletes a problem with `--context` and `--path` arguments


## 0.3.0


Milestone and interactivity
*Target release date:* 2025-10-03

- [ ] documented guideline on the release process
- [ ] documented guideline on the new context creation process
- [ ] introduction of [questionary](https://github.com/tmbo/questionary) for interactive menu and selection
  - [ ] basic interactive prompt system for template section selection when creating a new context
- [ ] `milestone` command
  - [ ] `list` with `--context` and `--path` arguments
  - [ ] `add` with *MILESTONE*, `--context`, `--path`, `--title` and `--date` arguments
  - [ ] `remove` with *MILESTONE*, `--context` and `--path` arguments
- [ ] `context` command
  - [ ] `remove` with `--path` argument
  - [ ] `check` with `--path` argument
- [ ] `status` command mechanism
  - [ ] display of completed vs total *tasks* on console
  - [ ] display of *milestones* timeline on console


## 0.2.0

Command restructuring, modular templating
*Target release date:* 2025-09-19

- [x] automatic hook to run linting, formating and typechecking
- [x] *commands* restructuring and improvement
  - [x] `context` command with subcommand: `list`, `add`, `remove`, `check`
  - [x] skeleton commands: `task`, `problem`, `milestone`
  - [x] `contexts` forwarded to `context list`
  - [x] `new` forwarded to `context add`


## 0.1.0

Initial cli & template creation
*Target release date:* 2025-09-05

- [x] full python tdd setup and workflow
- [x] automatic hook to run tests and coverage
- [x] logging system to stderr
- [x] templating engine creating basic templates at targeted path
- [x] no overwriting of existing *context*
- [x] *context* detection with name and path extraction
- [x] release template
- [x] roadmap template
- [x] readme template

