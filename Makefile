# Load .env if exists
-include .env
export

.PHONY: status index setup install-deps \
        install-memorygraph init-env check-deps lint lint-fix test typecheck \
        validate clean patch-prompt patch-restore patch-clean help

# ─────────────────────────────────────────────────────
# Prerequisites Check
# ─────────────────────────────────────────────────────

check-deps: ## Check required tools are installed
	@echo "Checking prerequisites..."
	@command -v node    >/dev/null 2>&1 || { echo "  [MISSING] node    — https://nodejs.org/"; exit 1; }
	@command -v npm     >/dev/null 2>&1 || { echo "  [MISSING] npm     — https://nodejs.org/"; exit 1; }
	@command -v uv      >/dev/null 2>&1 || { echo "  [MISSING] uv      — curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	@command -v pipx    >/dev/null 2>&1 || { echo "  [MISSING] pipx    — brew install pipx && pipx ensurepath"; exit 1; }
	@echo "  [OK] node ($$(node --version))"
	@echo "  [OK] npm ($$(npm --version))"
	@echo "  [OK] uv"
	@echo "  [OK] pipx"
	@echo ""
	@echo "Optional:"
	@command -v gh          >/dev/null 2>&1 && echo "  [OK] gh CLI" || echo "  [SKIP] gh — brew install gh (GitHub PR/Issue 관리)"
	@command -v memorygraph >/dev/null 2>&1 && echo "  [OK] memorygraph" || echo "  [SKIP] memorygraph — run: make install-memorygraph"
	@npx -y @er77/code-graph-rag-mcp --version >/dev/null 2>&1 && echo "  [OK] @er77/code-graph-rag-mcp" || echo "  [SKIP] @er77/code-graph-rag-mcp — installed on-demand via npx"

# ─────────────────────────────────────────────────────
# Installation
# ─────────────────────────────────────────────────────

install-memorygraph: ## Install memorygraph MCP server via pipx
	@command -v memorygraph >/dev/null 2>&1 && echo "memorygraph already installed: $$(memorygraph --version)" || \
		{ echo "Installing memorygraph..."; pipx install memorygraphMCP; }

install-deps: check-deps install-memorygraph ## Install all external dependencies
	@echo ""
	@echo "All dependencies installed."
	@echo "Note: @er77/code-graph-rag-mcp is installed on-demand via npx."

# ─────────────────────────────────────────────────────
# Environment Setup
# ─────────────────────────────────────────────────────

init-env: ## Create .env from .env.example (if not exists)
	@if [ -f .env ]; then \
		echo ".env already exists. Skipping."; \
	else \
		cp .env.example .env; \
		echo ".env created. Edit CONTEXT7_API_KEY before running MCP servers."; \
	fi

# ─────────────────────────────────────────────────────
# Status
# ─────────────────────────────────────────────────────

status: ## Show tool status
	@echo "=== MCP Tools ==="
	@command -v memorygraph >/dev/null 2>&1 && echo "  memorygraph: $$(memorygraph --version)" || echo "  memorygraph: not installed"
	@echo "  code-graph-rag: @er77/code-graph-rag-mcp (npx, on-demand)"
	@echo ""
	@echo "=== Environment ==="
	@test -f .env && echo "  .env: exists" || echo "  .env: MISSING (run: make init-env)"

# ─────────────────────────────────────────────────────
# code-graph-rag Indexing
# ─────────────────────────────────────────────────────

index: ## Index codebase with code-graph-rag
	@command -v npx >/dev/null 2>&1 || { echo "ERROR: npx not found. Install Node.js: https://nodejs.org/"; exit 1; }
	npx -y @er77/code-graph-rag-mcp index "$(CURDIR)"
	@echo "Index complete."

# ─────────────────────────────────────────────────────
# Full Setup
# ─────────────────────────────────────────────────────

setup: ## Full initial setup (install deps → env → index)
	@echo "========================================="
	@echo "  Boilerplate Full Setup"
	@echo "========================================="
	@$(MAKE) --no-print-directory install-deps
	@$(MAKE) --no-print-directory init-env
	@echo ""
	@echo "--- Indexing Codebase ---"
	@$(MAKE) --no-print-directory index
	@echo ""
	@echo "========================================="
	@echo "  Setup Complete!"
	@echo "========================================="
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env — set CONTEXT7_API_KEY (optional)"
	@echo "  2. Restart Claude Code to load MCP servers"
	@echo "  3. Run: /new-project to start a GSD workflow"

# ─────────────────────────────────────────────────────
# Code Quality
# ─────────────────────────────────────────────────────

lint: ## Run ruff linter
	uv run ruff check .

lint-fix: ## Run ruff with auto-fix
	uv run ruff check --fix .

test: ## Run pytest
	uv run pytest tests/

typecheck: ## Run mypy type checker
	uv run mypy .

validate: ## Validate SPEC.md project structure
	python scripts/validate_spec.py

# ─────────────────────────────────────────────────────
# System Prompt Patching
# ─────────────────────────────────────────────────────

CLAUDE_CODE_VERSION ?= $(shell claude --version 2>/dev/null | awk '{print $$1}')
PATCH_DIR ?= claude-code-tips/system-prompt

patch-prompt: ## Patch Claude Code system prompt (reduces token usage ~50%)
	@echo "=== System Prompt Patcher ==="
	@command -v node >/dev/null 2>&1 || { echo "[MISSING] node — install Node.js"; exit 1; }
	@echo "Claude Code version: $(CLAUDE_CODE_VERSION)"
	@test -d "$(PATCH_DIR)/$(CLAUDE_CODE_VERSION)" || { echo "[ERROR] No patches for v$(CLAUDE_CODE_VERSION) in $(PATCH_DIR)/"; echo "See: .gsd/GUIDE-system-prompt-patch.md > Version Upgrade"; exit 1; }
	@mkdir -p .patch-workspace
	npm install --prefix .patch-workspace @anthropic-ai/claude-code@$(CLAUDE_CODE_VERSION) --silent
	@cp .patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js /tmp/_claude_cli.js
	@cp .patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js /tmp/_claude_cli.js.backup
	@node "$(PATCH_DIR)/$(CLAUDE_CODE_VERSION)/patch-cli.js" /tmp/_claude_cli.js
	@cp /tmp/_claude_cli.js .patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js
	@cp /tmp/_claude_cli.js.backup .patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js.backup
	@rm -f /tmp/_claude_cli.js /tmp/_claude_cli.js.backup
	@echo ""
	@echo "Patched! Run with:"
	@echo "  DISABLE_AUTOUPDATER=1 npx --prefix .patch-workspace claude"

patch-restore: ## Restore original Claude Code CLI (undo patch)
	@test -f .patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js.backup || { echo "[ERROR] No backup found. Nothing to restore."; exit 1; }
	@cp .patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js.backup \
		.patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js
	@echo "Restored original cli.js from backup."

patch-clean: ## Remove patched Claude Code workspace
	rm -rf .patch-workspace/
	@echo "Removed .patch-workspace/"

# ─────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────

clean: ## Remove index data and patch workspace
	rm -rf .code-graph-rag/ .patch-workspace/

# ─────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
