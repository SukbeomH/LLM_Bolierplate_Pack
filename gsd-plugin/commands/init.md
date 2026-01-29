---
description: Initialize GSD document system and compare infrastructure files
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# /gsd:init - GSD Initialization

Initialize the GSD (Get Shit Done) document system in the current project.

## What This Command Does

1. **Scaffold GSD Documents**: Creates `.gsd/` directory with working documents and templates
2. **Compare Infrastructure**: Shows diff between plugin references and project files
3. **Interactive Setup**: If SPEC.md is empty, guides you through project information collection

## Execution Steps

### Step 1: Scaffold GSD Directory

Run the scaffolding script to create the GSD document structure:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/scaffold-gsd.sh"
```

This creates:
- `.gsd/SPEC.md` - Project specification
- `.gsd/DECISIONS.md` - Architecture decision records
- `.gsd/JOURNAL.md` - Development journal
- `.gsd/ROADMAP.md` - Project roadmap
- `.gsd/templates/` - Document templates (22 files)
- `.gsd/examples/` - Usage examples (3 files)

### Step 2: Compare Infrastructure Files

Run the infrastructure comparison script:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/scaffold-infra.sh"
```

This compares your project files against GSD reference configurations:
- `pyproject.toml` - Python project config
- `Makefile` - Build automation
- `.gitignore` - Git ignore patterns
- `CLAUDE.md` - Claude Code instructions
- And more...

### Step 3: Interactive Setup (if needed)

If `.gsd/SPEC.md` is empty or contains only template content, collect project information:

1. Ask for project name and brief description
2. Ask for primary programming language(s)
3. Ask for key dependencies or frameworks
4. Ask for project goals or constraints

Then populate `.gsd/SPEC.md` with the collected information.

## After Initialization

Once initialized, you can use GSD commands:
- `/gsd:plan` - Create implementation plans
- `/gsd:execute` - Execute planned work
- `/gsd:verify` - Verify completed work
- `/gsd:help` - List all available commands
