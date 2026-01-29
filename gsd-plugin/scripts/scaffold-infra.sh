#!/usr/bin/env bash
#
# scaffold-infra.sh - Compare project files against GSD references
#
set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

echo "Comparing infrastructure files..."
echo "  Plugin: ${PLUGIN_ROOT}"
echo "  Project: ${PROJECT_DIR}"
echo ""

# Define mappings: reference_file -> project_path
declare -A MAP=(
    ["pyproject.toml"]="pyproject.toml"
    ["Makefile"]="Makefile"
    ["gitignore.txt"]=".gitignore"
    ["ci.yml"]=".github/workflows/ci.yml"
    ["CLAUDE.md"]="CLAUDE.md"
    ["vscode-settings.json"]=".vscode/settings.json"
    ["vscode-extensions.json"]=".vscode/extensions.json"
    ["github-agent.md"]=".github/agents/agent.md"
    ["env.example"]=".env.example"
)

has_diff=0

for ref in "${!MAP[@]}"; do
    ref_path="$PLUGIN_ROOT/references/$ref"
    proj_path="$PROJECT_DIR/${MAP[$ref]}"

    if [ ! -f "$ref_path" ]; then
        continue
    fi

    if [ ! -f "$proj_path" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "[MISSING] ${MAP[$ref]}"
        echo "  Reference available at: $ref_path"
        echo ""
        has_diff=1
    else
        # Check if files differ
        if ! diff -q "$proj_path" "$ref_path" > /dev/null 2>&1; then
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "[DIFFERS] ${MAP[$ref]}"
            echo ""
            diff -u "$proj_path" "$ref_path" | head -50 || true
            echo ""
            has_diff=1
        fi
    fi
done

# Check issue templates
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[Issue Templates]"
for ref in "$PLUGIN_ROOT"/references/issue-templates/*.yml; do
    [ -f "$ref" ] || continue
    tpl_name=$(basename "$ref")
    proj_tpl="$PROJECT_DIR/.github/ISSUE_TEMPLATE/$tpl_name"

    if [ ! -f "$proj_tpl" ]; then
        echo "  [MISSING] .github/ISSUE_TEMPLATE/$tpl_name"
        has_diff=1
    elif ! diff -q "$proj_tpl" "$ref" > /dev/null 2>&1; then
        echo "  [DIFFERS] .github/ISSUE_TEMPLATE/$tpl_name"
        has_diff=1
    else
        echo "  [OK] .github/ISSUE_TEMPLATE/$tpl_name"
    fi
done

echo ""
if [ $has_diff -eq 0 ]; then
    echo "All infrastructure files match references!"
else
    echo "Review the differences above."
    echo "Reference files are in: $PLUGIN_ROOT/references/"
fi
