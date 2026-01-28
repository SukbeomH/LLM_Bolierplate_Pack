import os
import sys

REQUIRED_FILES = [
    ".github/agents/agent.md",
    ".specs/SPEC.md",
    ".specs/PLAN.md",
]


def validate_project_structure():
    """
    Validates that the current directory has proper project structure.
    """
    print("Validating Project Structure...")
    missing = []

    for file_path in REQUIRED_FILES:
        if not os.path.exists(file_path):
            missing.append(file_path)

    if missing:
        print("Validation Failed! Missing files:")
        for m in missing:
            print(f" - {m}")
        sys.exit(1)

    print("Validation Passed: Project structure is correct.")


if __name__ == "__main__":
    validate_project_structure()
