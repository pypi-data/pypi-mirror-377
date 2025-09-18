"""
Settings and configuration for Xodex.

- Reads from XODEX_SETTINGS_MODULE environment variable.
- Supports dynamic and manual configuration, validation, and runtime overrides.
- Caches settings for fast access.
- Provides explicit settings tracking and validation utilities.
- Supports reloading and resetting configuration at runtime.
- Warns on missing or invalid settings.
- Singleton pattern ensures only one configuration instance.

Usage:
    from xodex.conf import settings
    print(settings.DEBUG)
    settings.configure(DEBUG=True, CUSTOM_SETTING=123)
    settings.reload()
    settings.validate("DEBUG", lambda v: isinstance(v, bool))
"""

import os
import importlib
import warnings
from types import ModuleType
from xodex.core.singleton import Singleton
# from xodex.conf import configuration

ENVIRONMENT_VARIABLE = "XODEX_SETTINGS_MODULE"


class Configuration(Singleton):
    """
    Xodex Configuration Singleton

    Loads settings from a Python module specified by the XODEX_SETTINGS_MODULE
    environment variable, or from the default configuration module. Supports
    runtime overrides, validation, and explicit settings tracking.
    """

    def __init__(self):
        super().__init__()
        self._explicit_settings = set()
        self._settings_cache = {}
        self.settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        self._load_defaults()
        self._configure()

    def _load_defaults(self):
        """Load default settings from the base configuration module."""
        # for setting in dir(configuration):
        #     if setting.isupper():
        #         setattr(self, setting, getattr(configuration, setting))

    def __repr__(self):
        return f"<{self.__class__.__name__} module={self.settings_module!r}>"

    def __getattr__(self, name):
        """Return the value of a setting and cache it in self._settings_cache."""
        if name in self._settings_cache:
            return self._settings_cache[name]
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"Setting '{name}' not found.")

    def __setattr__(self, name, value):
        """Set the value of a setting and cache it in self._settings_cache."""
        if name.isupper():
            self._settings_cache[name] = value
            self._explicit_settings.add(name)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        """Delete a setting and clear it from cache if needed."""
        self._settings_cache.pop(name, None)
        self._explicit_settings.discard(name)
        super().__delattr__(name)

    @property
    def configured(self):
        """Return True if the settings have already been configured."""
        return self.settings_module is not None

    def configure(self, **options):
        """
        Manually configure the settings at runtime.

        Args:
            **options: Setting names and values to override.
        """
        if not self.settings_module:
            self._configure()
        for name, value in options.items():
            if not name.isupper():
                raise TypeError(f"Setting {name} must be uppercase.")
            setattr(self, name, value)
        self._explicit_settings.update(options.keys())

    def _configure(self):
        """Load settings from the module specified in the environment variable."""
        try:
            self.settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
            if not self.settings_module:
                return
            mod = importlib.import_module(self.settings_module)
            tuple_settings = ("SUPPORTED_LANGUAGES", "WINDOW_SIZE")
            dict_settings = ("CUSTOM_SETTINGS", "KEY_BINDINGS", "LOGGING")
            for setting in dir(mod):
                if setting.isupper():
                    setting_value = getattr(mod, setting)
                    if setting in tuple_settings and not isinstance(setting_value, (list, tuple)):
                        warnings.warn(f"The {setting} setting must be a list or a tuple.")
                        continue
                    if setting in dict_settings and not isinstance(setting_value, dict):
                        warnings.warn(f"The {setting} setting must be a dict.")
                        continue
                    setattr(self, setting, setting_value)
                    self._explicit_settings.add(setting)
        except Exception as e:
            warnings.warn(f"Failed to configure settings: {e}")

    def validate(self, setting, validator, warn=True):
        """
        Validate a setting using a custom validator function.

        Args:
            setting (str): The setting name.
            validator (callable): Function that takes the value and returns True/False.
            warn (bool): If True, issue a warning on failure.
        Returns:
            bool: True if valid, False otherwise.
        """
        value = getattr(self, setting, None)
        valid = validator(value)
        if not valid and warn:
            warnings.warn(f"Validation failed for setting '{setting}': {value!r}")
        return valid

    def reload(self):
        """
        Reload settings from the environment module, discarding runtime overrides.
        """
        self._settings_cache.clear()
        self._explicit_settings.clear()
        self._load_defaults()
        self._configure()

    def reset(self):
        """
        Reset all settings to defaults (from base configuration).
        """
        self._settings_cache.clear()
        self._explicit_settings.clear()
        self._load_defaults()

    def as_dict(self):
        """
        Return all current settings as a dictionary.
        """
        result = {k: v for k, v in self.__dict__.items() if k.isupper()}
        result.update(self._settings_cache)
        return result

    def is_explicit(self, name):
        """
        Check if a setting was explicitly set (not just from defaults).

        Args:
            name (str): The setting name.
        Returns:
            bool: True if explicitly set, False otherwise.
        """
        return name in self._explicit_settings

    def warn_if_missing(self, *settings):
        """
        Warn if any of the given settings are missing.

        Args:
            *settings: Setting names to check.
        """
        for name in settings:
            if not hasattr(self, name):
                warnings.warn(f"Required setting '{name}' is missing.")


settings = Configuration()

# Example usage:
# from xodex.conf import settings
# print(settings.DEBUG)
# settings.configure(DEBUG=False, CUSTOM_SETTING=123)
# settings.validate("DEBUG", lambda v: isinstance(v, bool))
# settings.warn_if_missing("DATABASE_URL", "SECRET_KEY")
# settings.reload()
# print(settings.as_dict())
