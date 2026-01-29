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

If `.gsd/SPEC.md` is empty or contains only placeholder content:

1. **Read the template**: Read `.gsd/templates/spec.md` to understand the document structure
2. **Collect project information** via AskUserQuestion:
   - Project name and brief description (Vision)
   - Primary programming language(s) and frameworks
   - 2-3 key goals
   - Known constraints (technical, business, timeline)
   - Success criteria (measurable outcomes)
3. **Populate SPEC.md**: Write the collected information using the template structure from `templates/spec.md`
   - Keep `Status: DRAFT` until user finalizes
   - Fill in all sections with collected info
   - Remove placeholder text like `{Goal 1}`

**Important**: The working document must follow the template structure, not just contain raw answers.

## After Initialization

Once initialized, you can use GSD commands:
- `/gsd:plan` - Create implementation plans
- `/gsd:execute` - Execute planned work
- `/gsd:verify` - Verify completed work
- `/gsd:help` - List all available commands
