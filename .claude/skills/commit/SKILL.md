---
name: commit
description: Analyzes diffs, splits logical changes, creates conventional emoji commits aligned with GSD atomic commit protocol
---

# GSD Commit Skill

<role>
You create well-structured git commits following conventional commit format with emoji.
You analyze diffs to detect multiple logical changes and suggest splitting into separate commits.

This skill is the shipping mechanism for GSD executor's atomic commit requirement.
</role>

---

## Workflow

### Step 1: Pre-Commit Checks

Run quality checks before committing:

```bash
uv run ruff check .              # Lint
uv run mypy .                    # Type check
uv run pytest tests/ -x -q       # Quick test (fail-fast)
```

If checks fail, report failures and ask whether to:
1. Fix issues first (recommended)
2. Proceed anyway (`--no-verify` flag)

### Step 2: Analyze Staged Changes

```bash
git status                        # Check staged/unstaged files
git diff --cached --stat          # Staged changes overview
git diff --cached                 # Full staged diff
```

If no files are staged, stage all modified files:
```bash
git add -A
```

### Step 3: Detect Logical Splits

Analyze the diff for multiple distinct concerns:

**Split signals:**
- Changes to unrelated modules (e.g., `src/auth/` + `src/billing/`)
- Mixed change types (feature code + test code + config)
- Different file categories (source vs docs vs config)
- Independent bug fixes bundled with features

If multiple concerns detected, suggest splitting:
```
Detected 3 logical changes:
1. feat: add user validation in src/auth/
2. test: add validation tests
3. chore: update pyproject.toml dependencies

Split into separate commits? [Y/n]
```

### Step 4: Create Commit

Use conventional commit format with emoji:

```bash
git commit -m "$(cat <<'EOF'
<emoji> <type>(<scope>): <description>

<optional body>

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Commit Types

| Emoji | Type | Description |
|-------|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Formatting, no logic change |
| `refactor` | Code restructuring |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `chore` | Tooling, config, dependencies |
| `ci` | CI/CD changes |

### GSD-Specific Scopes

When executing GSD plans, use phase-plan scope:

```
feat(phase-1.2): implement login endpoint with JWT
fix(phase-2.1): resolve bcrypt comparison error
test(phase-1.3): add integration tests for auth flow
```

---

## Commit Message Rules

- **Imperative mood**: "add feature" not "added feature"
- **First line**: max 72 characters
- **Scope**: module or phase-plan reference
- **Body**: explain WHY, not WHAT (the diff shows WHAT)
- **No period** at the end of the subject line

---

## Examples

### Single Commit
```
feat(auth): add JWT-based login endpoint

Implements POST /api/auth/login with bcrypt password verification
and httpOnly cookie response. Uses jose library for Edge runtime
compatibility.
```

### Split Commits (from single diff)
```bash
# Commit 1: Feature code
git add src/auth/
git commit -m "feat(auth): add JWT-based login endpoint"

# Commit 2: Tests
git add tests/auth/
git commit -m "test(auth): add login endpoint integration tests"

# Commit 3: Config
git add pyproject.toml uv.lock
git commit -m "chore(deps): add jose and bcrypt dependencies"
```
