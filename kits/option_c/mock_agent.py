#!/usr/bin/env python3
"""
Mock CLI Agent for testing Option C without real Claude Code.

This script simulates the behavior of a real CLI coding agent by:
1. Reading the guide file passed as argument
2. Printing simulated "thinking" and "action" steps
3. Creating a dummy file modification
4. Exiting with success

Usage:
    python mock_agent.py -p /path/to/guide.md

Set CLI_COMMAND_PATH=mock_agent.py in .env to use this mock.
"""

import argparse
import time
import sys
import os
from pathlib import Path


def simulate_agent(guide_path: str):
    """Simulate agent behavior."""
    print(f"[Mock Agent] Reading guide: {guide_path}")
    time.sleep(0.5)

    # Read the guide
    guide_content = ""
    if Path(guide_path).exists():
        guide_content = Path(guide_path).read_text()
        print(f"[Mock Agent] Guide content ({len(guide_content)} chars)")
    else:
        print(f"[Mock Agent] Warning: Guide file not found, proceeding anyway")

    # Simulate thinking
    print("[Mock Agent] 🤔 Analyzing request...")
    time.sleep(0.3)

    print("[Mock Agent] 📋 Planning steps:")
    steps = [
        "1. Understand the current code structure",
        "2. Identify files to modify",
        "3. Write the implementation",
        "4. Verify changes"
    ]
    for step in steps:
        print(f"    {step}")
        time.sleep(0.2)

    # Simulate action
    print("[Mock Agent] 🛠️ Executing plan...")
    time.sleep(0.5)

    # Create a mock output file to prove it ran
    output_dir = Path(guide_path).parent
    mock_output = output_dir / "mock_agent_output.txt"
    mock_output.write_text(f"""Mock Agent Execution Summary
=============================
Guide: {guide_path}
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
Status: Success

This file was created by the mock agent to verify the pipeline is working.
In a real scenario, this would be actual code changes.
""")

    print(f"[Mock Agent] ✅ Created: {mock_output}")
    print("[Mock Agent] ✅ Task completed successfully!")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Mock CLI Agent for testing")
    parser.add_argument("-p", "--prompt", dest="guide_path", help="Path to the guide/prompt file")
    parser.add_argument("--allowedTools", default="Edit,Write,Bash", help="Allowed tools (ignored in mock)")

    args, _ = parser.parse_known_args()

    if not args.guide_path:
        # Also accept positional argument
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            args.guide_path = sys.argv[1]
        else:
            print("[Mock Agent] Error: No guide path provided")
            print("Usage: python mock_agent.py -p /path/to/guide.md")
            return 1

    return simulate_agent(args.guide_path)


if __name__ == "__main__":
    sys.exit(main())
