#!/usr/bin/env bash
# Build script for auto-generated documentation pages.
#
# Activates the dango venv (needed for Python imports) and runs all
# three generator scripts in sequence.
#
# Usage:
#   ./scripts/build.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DANGO_VENV="$DOCS_ROOT/../dango/venv"

# Activate dango venv (required for imports)
if [ ! -f "$DANGO_VENV/bin/activate" ]; then
    echo "ERROR: dango venv not found at $DANGO_VENV" >&2
    echo "Run: cd ../dango && python3.11 -m venv venv && source venv/bin/activate && pip install -e '.[dev]'" >&2
    exit 1
fi

# shellcheck disable=SC1091
source "$DANGO_VENV/bin/activate"

echo "=== Auto-generating documentation ==="
echo ""

# Run generators
FAILED=0

echo "1/3 Generating permissions.md..."
if python "$SCRIPT_DIR/generate_permissions.py"; then
    echo "    OK"
else
    echo "    FAILED"
    FAILED=1
fi

echo "2/3 Generating source-catalog.md..."
if python "$SCRIPT_DIR/generate_source_catalog.py"; then
    echo "    OK"
else
    echo "    FAILED"
    FAILED=1
fi

echo "3/3 Generating cli-reference.md..."
if python "$SCRIPT_DIR/generate_cli_reference.py"; then
    echo "    OK"
else
    echo "    FAILED"
    FAILED=1
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
    echo "=== All generators succeeded ==="
else
    echo "=== Some generators FAILED ==="
    exit 1
fi
