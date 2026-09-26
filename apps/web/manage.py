#!/usr/bin/env python
"""Django command-line entry point for the GrowthTwin web application."""

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is not installed in the active Python environment. "
            "Install the dependencies declared in pyproject.toml first."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
