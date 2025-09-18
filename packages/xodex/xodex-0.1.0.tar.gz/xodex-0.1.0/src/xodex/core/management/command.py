"""
Base classes for writing management commands (named commands which can
be executed through ``xodex`` or ``manage.py``).
"""

import os
import sys
import argparse

from xodex.version import vernum


def handle_default_options(options):
    """
    Include any default options that all commands should accept here
    so that ManagementUtility can handle them before searching for
    user commands.
    """
    if options.settings:
        os.environ["XODEX_SETTINGS_MODULE"] = options.settings
    if options.pythonpath:
        sys.path.insert(0, options.pythonpath)


class BaseCommand:
    """
    Several attributes affect behavior at various steps along the way:

    ``help``
        A short description of the command, which will be printed in
        help messages.
    """

    def __init__(self, description, usage=None):
        self.description = description
        self.version = str(vernum)
        self.usage = usage or "%(prog)s <command> [options] [args]"

    def parser(self, prog_name, **kwargs):
        """Create and return the ``ArgumentParser`` which will be used toparse the arguments to this command."""

        parser = argparse.ArgumentParser(
            prog=os.path.basename(prog_name),
            usage=self.usage,
            description="Xodex Management Utility",
        )

        parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[1, 2, 3], help="Verbosity level (1-3).")
        parser.add_argument(
            "--version",
            action="version",
            version=self.version,
            help="Show program's version number and exit.",
        )
        parser.add_argument(
            "--settings",
            help=(
                "The Python path to a settings module, e.g. "
                '"myproject.settings". If this isn\'t provided, the '
                "XODEX_SETTINGS_MODULE environment variable will be used."
            ),
        )
        parser.add_argument(
            "--pythonpath",
            help=("A directory to add to the Python path, e.g. " '"/home/python3/bin".'),
        )
        parser.add_argument(
            "--traceback",
            action="store_true",
            help="Raise on ArgumentError exceptions.",
        )
        parser.add_argument(
            "--no-color",
            action="store_true",
            help="Don't colorize the command output.",
        )
        self.add_arguments(parser)
        return parser

    def print_help(self, prog_name):
        """Print the help message for this command."""
        parser = self.parser(prog_name)
        parser.print_help()

    def execute(self, argv):
        """execute"""
        parser = self.parser(argv[0])
        options, _ = parser.parse_known_args(argv[2:])
        handle_default_options(options)
        try:
            print(options)
            self.handle(options)
        except argparse.ArgumentError as e:
            if options.traceback:
                raise
            print(e)
            sys.exit(1)

    def add_arguments(self, parser):
        """Entry point for subclassed commands to add custom arguments."""
        raise NotImplementedError("subclasses of BaseCommand must provide a add_arguments() method")

    def handle(self, options):
        """The actual logic of the command. Subclasses must implementthis method."""
        raise NotImplementedError("subclasses of BaseCommand must provide a handle() method")
