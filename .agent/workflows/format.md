---
description: Format source files using project formatters (ruff, prettier, gofmt)
---

# /format Workflow

Format source files using the project's configured formatters.

## Usage

```
/format              # Format all modified files
/format <file>       # Format specific file
/format --all        # Format all source files
```

## Process

1. **Check for Qlty** (if `.qlty/qlty.toml` exists)
   ```bash
   qlty fmt <file>
   ```

2. **Language-specific formatters**

### Python
```bash
uv run ruff format <file>
uv run ruff check --fix <file>
```

### JavaScript/TypeScript
```bash
npx prettier --write <file>
```

### Go
```bash
gofmt -w <file>
```

### Rust
```bash
rustfmt <file>
```

## Auto-format on Save

For auto-formatting, configure in Antigravity Settings:
- Settings > Editor > Format On Save: **Enabled**

Or use the project's editorconfig and extension settings.

## Related

- `/clean` - Run linting and type checking
- Safety rules in `.agent/rules/code-style.md`
