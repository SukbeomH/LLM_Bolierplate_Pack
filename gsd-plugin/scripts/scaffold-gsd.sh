#!/usr/bin/env bash
#
# scaffold-gsd.sh - Initialize GSD document structure in a project
#
set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
TARGET="$PROJECT_DIR/.gsd"

echo "Scaffolding GSD documents..."
echo "  Plugin: ${PLUGIN_ROOT}"
echo "  Target: ${TARGET}"
echo ""

# Create directories
mkdir -p "$TARGET" "$TARGET/templates" "$TARGET/examples"

# Copy working documents (SPEC, DECISIONS, JOURNAL, ROADMAP)
for f in "$PLUGIN_ROOT"/templates/gsd/*.md; do
    [ -f "$f" ] || continue
    dst="$TARGET/$(basename "$f")"
    if [ -f "$dst" ]; then
        echo "[SKIP] $(basename "$f") - already exists"
    else
        cp "$f" "$dst"
        echo "[CREATED] $(basename "$f")"
    fi
done

# Copy templates
for f in "$PLUGIN_ROOT"/templates/gsd/templates/*.md; do
    [ -f "$f" ] || continue
    dst="$TARGET/templates/$(basename "$f")"
    if [ -f "$dst" ]; then
        echo "[SKIP] templates/$(basename "$f") - already exists"
    else
        cp "$f" "$dst"
        echo "[CREATED] templates/$(basename "$f")"
    fi
done

# Copy examples
for f in "$PLUGIN_ROOT"/templates/gsd/examples/*.md; do
    [ -f "$f" ] || continue
    dst="$TARGET/examples/$(basename "$f")"
    if [ -f "$dst" ]; then
        echo "[SKIP] examples/$(basename "$f") - already exists"
    else
        cp "$f" "$dst"
        echo "[CREATED] examples/$(basename "$f")"
    fi
done

echo ""
echo "GSD scaffolding complete!"
echo "  Working docs: .gsd/{SPEC,DECISIONS,JOURNAL,ROADMAP}.md"
echo "  Templates:    .gsd/templates/"
echo "  Examples:     .gsd/examples/"
