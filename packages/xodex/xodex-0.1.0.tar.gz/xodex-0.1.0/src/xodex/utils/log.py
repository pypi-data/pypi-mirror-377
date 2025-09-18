"""
Xodex Logging Utilities

Provides a robust, extensible logging setup for the Xodex engine, including:
- Per-module loggers with colored console output and rotating file logging.
- Django-style filters for debug/production mode.
- Utility for custom logging configuration and handler extension.
- Callback-based filter for advanced log filtering.
- Easy integration with settings and environment.
- Optional JSON and syslog/Windows Event Log support.
- Environment variable overrides for log level and log file.
- Runtime addition of filters/formatters/handlers.

Usage:
    from xodex.utils.logging import get_xodex_logger
    logger = get_xodex_logger(__name__)
    logger.info("Hello, Xodex logging!")

    # Advanced: Add a custom filter at runtime
    from xodex.utils.logging import add_filter
    add_filter(logger, lambda r: "special" in r.getMessage())

    # Advanced: Enable JSON logging
    from xodex.utils.logging import enable_json_logging
    enable_json_logging(logger)

Author: djoezeke
License: See LICENSE file.
"""

import sys
import os
import logging
import logging.config
import json
from importlib import import_module
from logging.handlers import RotatingFileHandler

from xodex.conf import settings

# --- Django-style Filters ---


class RequireDebugFalse(logging.Filter):
    """
    Filter that only passes records when settings.DEBUG is False.
    """

    def filter(self, record):
        return not settings.DEBUG


class RequireDebugTrue(logging.Filter):
    """
    Filter that only passes records when settings.DEBUG is True.
    """

    def filter(self, record):
        return settings.DEBUG


class CallbackFilter(logging.Filter):
    """
    A logging filter that checks the return value of a given callable (which
    takes the record-to-be-logged as its only parameter) to decide whether to
    log a record.
    """

    def __init__(self, callback):
        self.callback = callback

    def filter(self, record):
        return 1 if self.callback(record) else 0


# --- Colored Formatter ---


class ColoredFormatter(logging.Formatter):
    """
    Formatter that adds ANSI color codes to log output for terminals.
    Colors can be disabled by setting use_color=False.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def __init__(self, fmt=None, datefmt=None, style="%", use_color=True):
        super().__init__(fmt, datefmt, style)
        self.use_color = use_color

    def format(self, record):
        message = super().format(record)
        if self.use_color and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, self.RESET)
            message = f"{color}{message}{self.RESET}"
        return message


# --- JSON Formatter ---


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs logs in JSON format for structured logging.
    """

    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


# --- Syslog/Windows Event Log Handler Utility ---


def get_platform_handler():
    """
    Returns a syslog handler (Linux/macOS) or Windows Event Log handler.
    """
    if os.name == "nt":
        try:
            from logging.handlers import NTEventLogHandler

            return NTEventLogHandler("Xodex")
        except Exception:
            return None
    else:
        try:
            from logging.handlers import SysLogHandler

            return SysLogHandler(address="/dev/log")
        except Exception:
            return None


# --- Logging Configuration Defaults ---

LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
LOG_LEVEL = os.environ.get("XODEX_LOG_LEVEL", "DEBUG").upper()
LOG_FILE = os.environ.get("XODEX_LOG_FILE", "xodex.log")

LOG_FORMATTT = "[%(asctime)s] %(levelname)s %(name)s: %(lineno)d %(message)s"

# --- Logger Factory and Utilities ---


def get_xodex_logger(module_name=None, level=None, use_color=True, json_logs=False, propagate=False):
    """
    Get a per-module logger for Xodex, with colored console output and rotating file logging.

    Args:
        module_name (str, optional): The module name (e.g., __name__).
        level (int|str, optional): Override the default log level.
        use_color (bool): Enable or disable colored console output.
        json_logs (bool): Enable JSON log formatting.
        propagate (bool): Set logger.propagate.

    Returns:
        logging.Logger: Configured logger instance.
    """
    name = f"xodex{'.' + module_name if module_name else ''}"
    logger = logging.getLogger(name)
    log_level = level or LOG_LEVEL
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.DEBUG)
    logger.setLevel(log_level)
    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        if json_logs:
            ch.setFormatter(JSONFormatter())
        else:
            ch.setFormatter(ColoredFormatter(LOG_FORMAT, use_color=use_color))
        logger.addHandler(ch)
        # Rotating file handler (no color)
        fh = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
        fh.setFormatter(JSONFormatter() if json_logs else logging.Formatter(LOG_FORMAT))
        logger.addHandler(fh)
         # Optional: Add syslog/Windows Event Log handler
        # platform_handler = get_platform_handler()
        # if platform_handler:
        #     platform_handler.setLevel(logging.ERROR)
        #     platform_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        #     logger.addHandler(platform_handler)
    logger.propagate = propagate
    return logger


def add_handler(logger, handler):
    """
    Add an extra handler to a logger (e.g., email, file, etc.).

    Args:
        logger (logging.Logger): The logger to extend.
        handler (logging.Handler): The handler to add.
    """
    logger.addHandler(handler)


def add_filter(logger, filter_func):
    """
    Add a custom filter (callable or Filter instance) to a logger.

    Args:
        logger (logging.Logger): The logger to extend.
        filter_func (callable|logging.Filter): The filter to add.
    """
    if callable(filter_func) and not isinstance(filter_func, logging.Filter):
        logger.addFilter(CallbackFilter(filter_func))
    else:
        logger.addFilter(filter_func)


def enable_json_logging(logger):
    """
    Switch all handlers of a logger to use JSONFormatter.
    """
    for handler in logger.handlers:
        handler.setFormatter(JSONFormatter())


def configure_logging(logging_config, logging_settings):
    """
    Configure logging using a config function and settings dict.

    Args:
        logging_config (str): Import path to a logging config function.
        logging_settings (dict): Settings to pass to the config function.
    """
    if logging_config:
        try:
            module_path, class_name = logging_config.rsplit(".", 1)
        except ValueError as err:
            raise ImportError(f"{logging_config} doesn't look like a module path") from err
        try:
            module = import_module(module_path)
            logging_config_func = getattr(module, class_name)
        except AttributeError as err:
            raise ImportError(f"Module {module_path} does not define a {class_name} attribute/class") from err

        logging.config.dictConfig(DEFAULT_LOGGING)
        if logging_settings:
            logging_config_func(logging_settings)


# --- Example logging config dict (for reference) ---
DEFAULT_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": RequireDebugFalse,
        },
        "require_debug_true": {
            "()": RequireDebugTrue,
        },
    },
    "formatters": {
        "xodex": {
            " ()": ColoredFormatter,
            "format": LOG_FORMAT,
        },
        "json": {
            "()": JSONFormatter,
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "xodex",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 1_000_000,
            "backupCount": 3,
            "formatter": "xodex",
        },
        "json_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE + ".json",
            "maxBytes": 1_000_000,
            "backupCount": 3,
            "formatter": "json",
        },
    },
    "loggers": {
        "xodex": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}

# Example usage for this module:
# logger = get_xodex_logger(__name__)
# logger.info("Logging system initialized.")
# add_filter(logger, lambda r: "special" in r.getMessage())
# enable_json_logging(logger)
