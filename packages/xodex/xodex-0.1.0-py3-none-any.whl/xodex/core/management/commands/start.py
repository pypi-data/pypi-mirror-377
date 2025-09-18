"""Management command for generating Xodex projects from templates."""

import os
import re
import pathlib
from importlib.util import find_spec

from xodex.core.management.command import BaseCommand

try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init()
    COLOR_ENABLED = True
except ImportError:
    COLOR_ENABLED = False

__all__ = ("XodexGenerator", "StartCommand")


def cprint(text, color=None):
    """cprint"""
    if COLOR_ENABLED and color:
        print(getattr(Fore, color.upper(), "") + text + Style.RESET_ALL)
    else:
        print(text)


class XodexGenerator:
    """
    XodexGenerator handles rendering and copying a project template with variable substitution and extra features.

    Features:
    - Renders template files with {{ variable }} placeholders.
    - Supports skipping, overwriting, renaming, or force-overwriting existing files.
    - Allows custom context variables.
    - Excludes unwanted files/directories, with customizable patterns.
    - Can add a .gitignore and README.md automatically.
    - Supports file renaming via a mapping.
    - Supports template file extension (e.g., .tpl) and output renaming.
    - Interactive mode for conflict resolution.
    - Dry-run mode to preview changes.
    - Hooks for pre/post file copy.
    - Optionally copies binary files.
    - Custom file permissions.
    - Verbosity and logging improvements.
    """

    def __init__(
        self,
        name,
        target=None,
        template=None,
        context=None,
        extra_files=True,
        rename_map=None,
        template_ext=".tpl",
        interactive=False,
        dry_run=False,
        force=False,
        exclude_patterns=None,
        include_patterns=None,
        file_permissions=None,
        verbosity=1,
    ):
        """
        Initialize the XodexGenerator.

        :param name: Project name.
        :param target: Target directory for the new project.
        :param template: Template directory or identifier.
        :param context: Dictionary of variables for template rendering.
        :param extra_files: Whether to add extra files like .gitignore.
        :param rename_map: Mapping for renaming files.
        :param template_ext: Extension for template files.
        :param interactive: Whether to prompt on file conflicts.
        :param dry_run: If True, only print actions without making changes.
        :param force: If True, overwrite files without prompting.
        :param exclude_patterns: List of glob patterns to exclude.
        :param include_patterns: List of glob patterns to include.
        :param file_permissions: Dict of {filename: mode} for chmod.
        :param verbosity: Verbosity level (0=silent, 1=normal, 2=debug).
        """
        self.name = name
        self.template = template
        self.target = target
        self.context = context or {}
        self.extra_files = extra_files
        self.rename_map = rename_map or {}
        self.template_ext = template_ext
        self.interactive = interactive
        self.dry_run = dry_run
        self.force = force
        self.verbosity = verbosity

        self.context.setdefault("project_name", name)
        self.exclude_patterns = exclude_patterns or []
        self.include_patterns = include_patterns or []
        self.file_permissions = file_permissions or {}
        self.exclude_patterns.extend([".git", "__pycache__", ".pyo", ".pyc", ".py.class"])

        self.cwd = os.getcwd()
        self.main_dir = os.path.join(self.cwd, name) if not target else os.path.join(os.path.abspath(target), name)
        self.xodex_dir = pathlib.Path(__file__).parent.parent.parent.parent
        self.template_dir = os.path.join(self.xodex_dir, "conf", "template")

    def log(self, message, color=None, level=1):
        """Log a message if verbosity is high enough."""
        if self.verbosity >= level:
            cprint(message, color)

    def render_template(self, content):
        """
        Render {{ var }} placeholders in the template content.

        :param content: The template file content as a string.
        :return: Rendered string with variables replaced.
        """

        def replacer(match):
            key = match.group(1).strip()
            return str(self.context.get(key, match.group(0)))

        return re.sub(r"\{\{\s*(\w+)\s*\}\}", replacer, content)

    def resolve_filename(self, filename):
        """
        Rename files based on mapping or remove template extension.

        :param filename: The original filename.
        :return: The resolved filename.
        """
        if filename in self.rename_map:
            return self.rename_map[filename]
        if self.template_ext and filename.endswith(self.template_ext):
            return filename[: -len(self.template_ext)]
        return filename

    def should_exclude(self, path):
        """
        Determine if a file or directory should be excluded.

        :param path: The file or directory path.
        :return: True if excluded, False otherwise.
        """
        for pattern in self.exclude_patterns:
            if pathlib.PurePath(path).match(pattern):
                return True
        return False

    def should_include(self, path):
        """
        Determine if a file or directory should be included (if include_patterns is set).

        :param path: The file or directory path.
        :return: True if included, False otherwise.
        """
        if not self.include_patterns:
            return True
        for pattern in self.include_patterns:
            if pathlib.PurePath(path).match(pattern):
                return True
        return False

    def pre_copy_hook(self, src, dst):
        """
        Hook called before copying a file. Override for custom behavior.

        :param src: Source file path.
        :param dst: Destination file path.
        """

    def post_copy_hook(self, src, dst):
        """
        Hook called after copying a file. Override for custom behavior.

        :param src: Source file path.
        :param dst: Destination file path.
        """

    def copy_template(self):
        """
        Copy and render the template directory structure.

        Handles text and binary files, applies renaming, permissions, and hooks.
        """
        prefix_length = len(self.template_dir) + 1

        for root, dirs, files in os.walk(self.template_dir):
            path_rest = root[prefix_length:]
            relative_dir = path_rest
            if relative_dir:
                target_dir = os.path.join(self.main_dir, relative_dir)
                if not self.dry_run:
                    os.makedirs(target_dir, exist_ok=True)
            else:
                target_dir = self.main_dir

            # Exclude unwanted directories
            for dirname in dirs[:]:
                if dirname.startswith(".") or self.should_exclude(dirname):
                    dirs.remove(dirname)

            for filename in files:
                if self.should_exclude(filename) or not self.should_include(filename):
                    continue
                old_path = os.path.join(root, filename)
                new_filename = self.resolve_filename(filename)
                new_path = os.path.join(target_dir, new_filename)

                if os.path.exists(new_path):
                    if self.force:
                        self.log(f"Overwriting {new_path} (force mode)", "YELLOW", 2)
                    elif self.interactive:
                        resp = input(f"{new_path} exists. Overwrite [y/N/rename]? ").strip().lower()
                        if resp == "y":
                            pass
                        elif resp == "rename":
                            new_path = input("Enter new filename: ").strip()
                        else:
                            self.log(f"Skipped {new_path}", "YELLOW")
                            continue
                    else:
                        self.log(f"{new_path} already exists. Skipping.", "YELLOW")
                        continue

                self.pre_copy_hook(old_path, new_path)

                # Detect binary files by extension (simple heuristic)
                is_binary = any(
                    old_path.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".exe", ".dll"]
                )
                try:
                    if is_binary:
                        with open(old_path, "rb") as src_file:
                            content = src_file.read()
                        if self.dry_run:
                            self.log(f"[DRY RUN] Would copy binary: {new_path}", "CYAN")
                        else:
                            with open(new_path, "wb") as dst_file:
                                dst_file.write(content)
                    else:
                        with open(old_path, encoding="utf-8") as template_file:
                            content = template_file.read()
                        rendered = self.render_template(content)
                        if self.dry_run:
                            self.log(f"[DRY RUN] Would create: {new_path}", "CYAN")
                        else:
                            with open(new_path, "w", encoding="utf-8") as new_file:
                                new_file.write(rendered)
                    # Set file permissions if specified
                    if not self.dry_run and new_filename in self.file_permissions:
                        os.chmod(new_path, self.file_permissions[new_filename])
                except Exception as e:
                    self.log(f"Error copying {old_path} to {new_path}: {e}", "RED")
                    continue

                self.post_copy_hook(old_path, new_path)

    def post_process(self):
        """
        Rename 'project' dir to project name and add extra files if needed.

        Also cleans up temporary files and directories.
        """
        project_dir = os.path.join(self.main_dir, "project")
        if os.path.exists(project_dir):
            try:
                os.renames(project_dir, os.path.join(self.main_dir, self.name))
                # self.log(f"Renamed 'project' dir to '{self.name}'", "CYAN", 2)
            except Exception as e:
                self.log(f"Failed to rename 'project' dir: {e}", "RED")

        if self.extra_files:
            # Add a .gitignore if not present
            gitignore_path = os.path.join(self.main_dir, ".gitignore")
            if not os.path.exists(gitignore_path):
                if self.dry_run:
                    self.log(f"[DRY RUN] Would create: {gitignore_path}", "CYAN")
                else:
                    with open(gitignore_path, "w", encoding="utf-8") as f:
                        f.write("__pycache__/\n*.pyc\n*.pyo\n*.log\nsave/\n")
                    self.log("Added .gitignore", "CYAN", 2)

    def generate(self):
        """
        Main entry: generate the project.

        Creates the main directory, validates the name, handles the template,
        copies files, and runs post-processing.
        """
        self.validate_name()
        try:
            if not os.path.exists(self.main_dir):
                if not self.dry_run:
                    os.makedirs(self.main_dir)
                # self.log(f"Created directory: {self.main_dir}", "CYAN")
            else:
                self.log(f"'{self.main_dir}' already exists", "YELLOW")
        except Exception as e:
            self.log(f"Failed to create directory '{self.main_dir}': {e}", "RED")
            return

        self.copy_template()
        self.post_process()
        self.log(f"App '{self.name}' created successfully!", "GREEN")

    def validate_name(self):
        """
        Validate the project name.

        Checks for valid identifier and module name conflicts.
        """
        if self.name is None:
            self.log("you must provide a project name", "YELLOW")

        # Check it's a valid directory name.
        if not self.name.isidentifier():
            self.log(
                f"'{self.name}' is not a valid a project name. \nPlease make sure {self.name} is a valid identifier.",
                "YELLOW",
            )

        # Check that __spec__ doesn't exist.
        if find_spec(self.name) is not None:
            self.log(
                f"'{self.name}' conflicts with the name of an existing Python "
                "module and cannot be used as a project name. Please try "
                "another name.",
                "YELLOW",
            )


class StartCommand(BaseCommand):
    """
    Command to generate files or directories from templates with advanced options.

    Features:
    - List available templates
    - Interactive mode for file conflicts
    - Dry-run mode to preview changes
    - Force overwrite mode
    - Custom context variables for template rendering
    - Exclude/include patterns for files
    - Custom file permissions
    - Verbosity and logging control
    """

    def __init__(self):
        super().__init__(
            description="Generate files or projects from templates with advanced options.",
            usage="%(prog)s start [options]",
        )

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, nargs="?", help="Project name to generate.")
        parser.add_argument("-t", "--template", default=None, help="Template directory or identifier.")
        parser.add_argument("-o", "--output", default=None, help="Output directory for the new project.")
        parser.add_argument("-l", "--list", action="store_true", help="List available templates.")
        parser.add_argument("--interactive", action="store_true", help="Prompt on file conflicts.")
        parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files.")
        parser.add_argument("--force", action="store_true", help="Force overwrite of existing files.")
        parser.add_argument("--extra-files", action="store_true", default=True, help="Add extra files like .gitignore.")
        parser.add_argument(
            "--no-extra-files", dest="extra_files", action="store_false", help="Do not add extra files."
        )
        parser.add_argument("--exclude", nargs="*", default=None, help="Glob patterns to exclude.")
        parser.add_argument("--include", nargs="*", default=None, help="Glob patterns to include.")
        parser.add_argument("--rename", nargs="*", default=None, help="File renaming mapping: src=dest.")
        parser.add_argument("--template-ext", default=".tpl", help="Template file extension (default: .tpl).")
        parser.add_argument("--file-perm", nargs="*", default=None, help="File permissions: filename=mode (octal).")
        parser.add_argument("-c", "--context", nargs="*", help="Extra context variables: key=value.")

    def handle(self, options):
        """
        Handle the template generation logic.
        """
        # List templates if requested
        if options.list:
            self.list_templates()
            return

        name = options.name
        if not name:
            name = input("Enter the name for your game: ").strip()
        if not name:
            cprint("Error: Game name is required.", "RED")
            return

        # Parse context variables
        context = self.parse_key_value_list(options.context)
        context["project_name_upper"] = name.upper()
        context["pygameui_version"] = self.version
        context["pygame_version"] = "2.6.1"
        context["xodex_version"] = self.version
        context["xodex_argv"] = "start"
        context["author"] = os.getenv("USERNAME") or os.getenv("USER") or "Unknown"
        context["year"] = "2025"

        # Parse rename map
        rename_map = self.parse_key_value_list(options.rename)

        # Parse file permissions
        file_permissions = self.parse_permissions(options.file_perm)

        # Exclude/include patterns
        exclude_patterns = options.exclude
        include_patterns = options.include

        # Output directory
        target = options.output

        # Create and run the template generator
        generator = XodexGenerator(
            name=name,
            target=target,
            template=options.template,
            context=context,
            extra_files=options.extra_files,
            rename_map=rename_map,
            template_ext=options.template_ext,
            interactive=options.interactive,
            dry_run=options.dry_run,
            force=options.force,
            exclude_patterns=exclude_patterns,
            include_patterns=include_patterns,
            file_permissions=file_permissions,
            verbosity=options.verbosity,
        )
        generator.generate()

    def list_templates(self):
        """
        List available templates in the default template directory.
        """
        # You may want to customize this path
        from pathlib import Path

        template_dir = Path(__file__).parent.parent.parent.parent / "conf" / "template"
        if not template_dir.exists():
            print(f"No templates directory found at '{template_dir}'.")
            return
        print("Available templates:")
        for name in os.listdir(template_dir):
            if name != "assets" and os.path.isdir(template_dir / name):
                print(f"  - {name}")

    @staticmethod
    def parse_key_value_list(items):
        """
        Parse a list of key=value strings into a dictionary.
        """
        result = {}
        if items:
            for item in items:
                if "=" in item:
                    key, value = item.split("=", 1)
                    result[key] = value
        return result

    @staticmethod
    def parse_permissions(items):
        """
        Parse a list of filename=mode strings into a dictionary.
        """
        perms = {}
        if items:
            for item in items:
                if "=" in item:
                    filename, mode = item.split("=", 1)
                    try:
                        perms[filename] = int(mode, 8)
                    except Exception:
                        continue
        return perms
