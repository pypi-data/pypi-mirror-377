"""Management"""

import os
import sys
import pkgutil
import argparse
import importlib

from xodex.version import vernum
from xodex.core.management.command import BaseCommand, handle_default_options

try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init()
    COLOR_ENABLED = True
except ImportError:
    COLOR_ENABLED = False


__all__ = ("ManagementUtility",)


def cprint(text, color=None):
    """cprint"""
    if COLOR_ENABLED and color:
        print(getattr(Fore, color.upper(), "") + text + Style.RESET_ALL)
    else:
        print(text)


class ManagementUtility:
    """Discovers and runs management commands for Xodex.

    Encapsulate the logic of the manage.py utilities.
    """

    def __init__(self, argv=None, commands_package="xodex.core.management.commands"):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        if self.prog_name == "__main__.py":
            self.prog_name = "python -m xodex"
        self.commands_package = commands_package
        self.commands: dict[str, BaseCommand] = self.discover_commands()
        self.settings_exception = None

    def discover_commands(self):
        """
        Discover all command modules in the commands package.
        Returns a dict: {command_name: CommandClass}
        """
        commands = {}
        try:
            package = importlib.import_module(self.commands_package)
        except ImportError:
            print(f"Could not import commands package: {self.commands_package}")
            return commands

        package_path = package.__path__
        for _, name, is_pkg in pkgutil.iter_modules(package_path):
            if is_pkg:
                continue
            module_name = f"{self.commands_package}.{name}"
            try:
                module = importlib.import_module(module_name)
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and issubclass(obj, BaseCommand) and obj is not BaseCommand:
                        commands[name] = obj
            except Exception as e:
                print(f"Error importing command '{name}': {e}")
        return commands

    def main_help(self):
        """
        Print help for all available commands.
        """
        print("Type 'xodex help <subcommand>' for help on a specific subcommand.\n")
        print("Available commands:")
        for name, cmd in self.commands.items():
            desc = getattr(cmd, "description", "")
            print(f"  {name:15} {desc}")

    def fetch_command(self, name) -> BaseCommand:
        """
        Return the command class for the given name.
        """
        if name in self.commands:
            return self.commands[name]()

    def execute(self):
        """Given the command-line arguments, figure out which command and run it."""

        parser = argparse.ArgumentParser(
            prog=self.prog_name,
            usage="%(prog)s <subcommand> [options] [args]",
            description="Xodex Management Utility",
            add_help=False,
        )

        parser.add_argument("--settings")
        parser.add_argument("--pythonpath")
        parser.add_argument("command", nargs="?")

        try:
            options, args = parser.parse_known_args(self.argv[2:])
            handle_default_options(options)
        except argparse.ArgumentError:
            pass

        try:
            command = self.argv[1]
        except IndexError:
            command = "help"

        if command in ["--help", "-h", "help"]:
            if options.command:
                command = self.fetch_command(options.command)
                if command:
                    command.print_help(self.argv[0])
            else:
                self.main_help()
        elif command in ["--version", "-v"]:
            print(str(vernum))
        else:
            command = self.fetch_command(command)
            if command:
                command.execute(self.argv)


def execute_from_command_line(argv=None):
    """Run Management Utility."""
    os.environ["XODEX_VERSION"] = str(vernum)
    utility = ManagementUtility(argv)
    utility.execute()
