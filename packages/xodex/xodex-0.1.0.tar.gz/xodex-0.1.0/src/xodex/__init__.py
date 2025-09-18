"""
Xodex Game Engine

This is the top-level package for Xodex. It exposes the version and
provides utility functions for version checking and metadata.

Features:
- Exposes __version__ as a string (from xodex.version.vernum)
- Provides version tuple and comparison utilities
- Includes package metadata for introspection
- Ready for use with __all__ for clean imports
"""

from xodex.version import vernum, get_version, is_version_at_least

__all__ = ("__version__", "get_version", "is_version_at_least")

__version__ = str(vernum)
