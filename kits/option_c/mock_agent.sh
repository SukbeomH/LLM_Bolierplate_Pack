#!/bin/bash
# Wrapper script to run mock_agent.py
# This allows CLI_COMMAND_PATH to be a single executable path

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON="/Users/sukbeom/Desktop/workspace/boilerplate/.venv/bin/python"

"$PYTHON" -u "$SCRIPT_DIR/mock_agent.py" "$@"
