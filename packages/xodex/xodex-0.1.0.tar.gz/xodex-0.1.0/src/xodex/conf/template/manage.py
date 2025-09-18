#!/usr/bin/env python3
"""Xodex's command-line tasks utility."""

import os
import sys


def main():
    """Run Utility tasks."""

    os.environ.setdefault("XODEX_SETTINGS_MODULE", "{{ project_name }}.settings")

    try:
        from xodex.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import xodex.") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
