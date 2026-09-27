#!/usr/bin/env python
"""Root entry point for Heroku's Python buildpack and monorepo commands."""

import os
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent / "apps" / "web"
sys.path.insert(0, str(APP_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.management import execute_from_command_line  # noqa: E402

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
