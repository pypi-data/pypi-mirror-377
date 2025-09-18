import json
import pickle
import os
import shutil
from typing import Any, Optional

from xodex.core.singleton import Singleton
from xodex.utils.storage import JsonSerializer, JsonDeserializer, BinarySerializer, BinaryDeserializer


class BaseStorage(JsonSerializer, JsonDeserializer, BinarySerializer, BinaryDeserializer):
    """
    Persistent storage manager for game data.

    Supports both JSON and binary (pickle) serialization formats.
    Inherit and override `serialize`/`deserialize` and/or `serialize_binary`/`deserialize_binary`
    for custom object state handling.

    Features:
    - Autosave/autoload support.
    - Backup and restore.
    - File existence and integrity checks.
    - Customizable file extension and directory.
    - Clear/reset storage.
    - Pre/post save/load hooks.
    - Error logging and robust exception handling.

    Attributes:
        data_path (str): Directory for storing data files.
        filename (str): Name of the file for saving/loading.
        binary (bool): Use binary (pickle) format if True, else JSON.
        autosave (bool): Automatically save on changes.
        autoload (bool): Automatically load on init.
    """

    data_path: str = "."
    binary: bool = False
    autosave: bool = False
    autoload: bool = True

    def __init__(self, filename: Optional[str] = None, data_path: Optional[str] = None, binary: Optional[bool] = None):
        """
        Initialize the storage.

        Args:
            filename: Custom filename (optional).
            data_path: Custom data directory (optional).
            binary: Use binary format (optional).
        """
        self.filename = (
            filename
            or f"{self.__class__.__name__.lower()}{'.xox' if (binary if binary is not None else self.binary) else '.json'}"
        )
        if data_path:
            self.data_path = data_path
        if binary is not None:
            self.binary = binary
        if self.autoload:
            self.load()

    def get_filepath(self) -> str:
        """Return the full path to the storage file."""
        return os.path.join(self.data_path, self.filename)

    def file_exists(self) -> bool:
        """Check if the storage file exists."""
        return os.path.isfile(self.get_filepath())

    def backup(self, backup_path: Optional[str] = None) -> Optional[str]:
        """
        Create a backup of the storage file.

        Args:
            backup_path: Path to save the backup (optional).
        Returns:
            Path to the backup file, or None if failed.
        """
        src = self.get_filepath()
        if not os.path.exists(src):
            return None
        backup_path = backup_path or (src + ".bak")
        try:
            shutil.copy2(src, backup_path)
            return backup_path
        except Exception as e:
            print(f"Backup failed: {e}")
            return None

    def restore(self, backup_path: Optional[str] = None) -> bool:
        """
        Restore storage from a backup file.

        Args:
            backup_path: Path to the backup file (optional).
        Returns:
            True if successful, False otherwise.
        """
        dst = self.get_filepath()
        backup_path = backup_path or (dst + ".bak")
        if not os.path.exists(backup_path):
            print(f"Backup file not found: {backup_path}")
            return False
        try:
            shutil.copy2(backup_path, dst)
            self.load()
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False

    def clear(self) -> None:
        """Clear the storage file and reset state."""
        try:
            os.remove(self.get_filepath())
        except FileNotFoundError:
            pass
        self.reset()
        if self.autosave:
            self.save()

    def reset(self) -> None:
        """Reset the in-memory state (override in subclass as needed)."""

    def pre_save(self):
        """Hook called before saving (override for custom behavior)."""

    def post_save(self):
        """Hook called after saving (override for custom behavior)."""

    def pre_load(self):
        """Hook called before loading (override for custom behavior)."""

    def post_load(self):
        """Hook called after loading (override for custom behavior)."""

    def load(self) -> None:
        """
        Load data from file (JSON or binary).

        If file is missing or corrupt, calls save() to create a new file.
        """
        self.pre_load()
        if not hasattr(self, "filename"):
            self.filename = f"{self.__class__.__name__.lower()}{'.bxox' if self.binary else '.jxox'}"
        try:
            mode = "rb" if self.binary else "r"
            with open(self.get_filepath(), mode) as f:
                if self.binary:
                    self.deserialize_binary(f.read())
                else:
                    self.deserialize(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError, pickle.UnpicklingError):
            self.save()
        except Exception as e:
            print(f"Error loading storage: {e}")
        self.post_load()

    def save(self) -> None:
        """
        Save data to file (JSON or binary).

        If directory does not exist, it is created.
        """
        self.pre_save()
        if not hasattr(self, "filename"):
            self.filename = f"{self.__class__.__name__.lower()}{'.bxox' if self.binary else '.jxox'}"
        os.makedirs(self.data_path, exist_ok=True)
        try:
            mode = "wb" if self.binary else "w"
            with open(self.get_filepath(), mode) as f:
                if self.binary:
                    f.write(self.serialize_binary())
                else:
                    json.dump(self.serialize(), f, indent=2)
        except Exception as e:
            print(f"Error saving storage: {e}")
        self.post_save()

    def event_handler(self, event: Any):
        """
        Handle events related to storage (stub for extension).

        Args:
            event: Event object.
        """


class Storage(Singleton, BaseStorage):
    """
    Singleton persistent storage for game data.

    Inherit and extend for custom game state management.
    """
