"""
Xodex Game Engine Command-Line Entrypoint

This module allows you to run Xodex management commands directly from the command line.

Usage Examples:
    python -m xodex startgame MyGame
    python -m xodex run
    python -m xodex help

How it works:
- This script delegates command-line arguments to the Xodex management utility.
- You can use it to scaffold new projects, run your game, or perform other management tasks.

See the Xodex documentation for a full list of available commands and options.

Author: Sackey Ezekiel Etrue (https://github.com/djoezeke) & Xodex Contributors
License: MIT
"""

from xodex.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line()
