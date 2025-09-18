"""
Xodex Custom Exceptions

Defines a hierarchy of custom exceptions for the Xodex engine, providing
clear, descriptive error handling for configuration, registration, scene,
and object management. Includes base error types, enhanced context, and
utility mixins for debugging and error reporting.

Features:
- Rich docstrings for all exceptions.
- Contextual information (name, object, message) for scene/object errors.
- Base error mixins for logging and debug support.
- Utility function for raising with formatted messages.
- Exception chaining and error codes.
- Specialized exceptions for plugin, resource, and validation errors.

Usage:
    raise UnknownScene(name="MainMenu", obj=scene_obj)
    raise NotRegistered("Object not registered: %s" % obj_name)
    raise PluginLoadError(plugin="myplugin", reason="Missing dependency")
"""

import sys
import traceback
from xodex.utils.log import get_xodex_logger


class XodexError(Exception):
    """
    Base class for all Xodex-specific exceptions.

    Args:
        message (str): Human-readable error message.
        code (int|str, optional): Optional error code for programmatic handling.
        **kwargs: Additional context for debugging.
    """

    default_code = "xodex_error"

    def __init__(self, message=None, *args, code=None, **kwargs):
        if message is None:
            message = self.__class__.__doc__ or "XodexError"
        super().__init__(message, *args)
        self.message = message
        self.code = code or self.default_code
        self.extra = kwargs

    def log(self, level="exception"):
        """
        Log this exception using the standard logger.

        Args:
            level (str): Logging level ('exception', 'error', 'warning', etc.)
        """
        logger = get_xodex_logger(__name__)
        log_func = getattr(logger, level, logger.exception)
        log_func(f"{self.__class__.__name__}: {self}", exc_info=True)

    def __str__(self):
        base = super().__str__()
        context = []
        if self.code:
            context.append(f"code={self.code}")
        if self.extra:
            context.append(f"context={self.extra}")
        return f"{base}" + (f" | {'; '.join(context)}" if context else "")

    def as_dict(self):
        """Return a dict representation of the exception for structured logging."""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "extra": self.extra,
        }


class ImproperlyConfigured(XodexError):
    """Xodex is improperly configured (missing or invalid settings)."""

    default_code = "improperly_configured"


class NotRegistered(XodexError):
    """A required object or component is not registered."""

    default_code = "not_registered"


class AlreadyRegistered(XodexError):
    """Attempted to register an object/component that is already registered."""

    default_code = "already_registered"


class SceneError(XodexError):
    """Base error for scene-related issues."""

    default_code = "scene_error"


class ObjectError(XodexError):
    """Base error for object-related issues."""

    default_code = "object_error"


class UnknownScene(SceneError, AttributeError):
    """
    Raised when a requested scene is unknown or not found.

    Args:
        name (str): The name of the missing scene.
        obj (object, optional): The related object, if any.
    """

    default_code = "unknown_scene"

    def __init__(self, *args, name=None, obj=None, **kwargs):
        msg = f"Unknown scene: {name!r}" if name else "Unknown scene"
        super().__init__(msg, *args, name=name, obj=obj, **kwargs)
        self.name = name
        self.obj = obj


class UnknownObject(ObjectError, AttributeError):
    """
    Raised when a requested object is unknown or not found.

    Args:
        name (str): The name of the missing object.
        obj (object, optional): The related object, if any.
    """

    default_code = "unknown_object"

    def __init__(self, *args, name=None, obj=None, **kwargs):
        msg = f"Unknown object: {name!r}" if name else "Unknown object"
        super().__init__(msg, *args, name=name, obj=obj, **kwargs)
        self.name = name
        self.obj = obj


class PluginError(XodexError):
    """Base error for plugin-related issues."""

    default_code = "plugin_error"


class PluginLoadError(PluginError):
    """
    Raised when a plugin fails to load.

    Args:
        plugin (str): The plugin name.
        reason (str): Reason for failure.
    """

    default_code = "plugin_load_error"

    def __init__(self, *args, plugin=None, reason=None, **kwargs):
        msg = f"Failed to load plugin '{plugin}': {reason}" if plugin else "Plugin load error"
        super().__init__(msg, *args, plugin=plugin, reason=reason, **kwargs)
        self.plugin = plugin
        self.reason = reason


class ResourceError(XodexError):
    """Base error for resource-related issues (files, assets, etc)."""

    default_code = "resource_error"


class ResourceNotFound(ResourceError):
    """
    Raised when a required resource is missing.

    Args:
        resource (str): The resource identifier.
    """

    default_code = "resource_not_found"

    def __init__(self, *args, resource=None, **kwargs):
        msg = f"Resource not found: {resource!r}" if resource else "Resource not found"
        super().__init__(msg, *args, resource=resource, **kwargs)
        self.resource = resource


class ValidationError(XodexError, ValueError):
    """
    Raised when a value or configuration is invalid.

    Args:
        field (str): The field or parameter name.
        value: The invalid value.
        reason (str): Reason for invalidity.
    """

    default_code = "validation_error"

    def __init__(self, *args, field=None, value=None, reason=None, **kwargs):
        msg = f"Invalid value for {field!r}: {value!r} ({reason})" if field else "Validation error"
        super().__init__(msg, *args, field=field, value=value, reason=reason, **kwargs)
        self.field = field
        self.value = value
        self.reason = reason


def raise_with_traceback(exc, tb=None):
    """
    Utility to raise an exception with a specific traceback.

    Args:
        exc (Exception): The exception instance.
        tb (traceback, optional): The traceback object.
    """
    if tb is None:
        _, _, tb = sys.exc_info()
    raise exc.with_traceback(tb)


# Example usage:
# try:
#     ...
# except Exception as e:
#     raise UnknownScene(name="Level1", obj=scene) from e
# raise PluginLoadError(plugin="myplugin",
