"""Values

A flexible attribute container with dict-like and object-like access.

Usage:
    v = Values({'foo': 1, 'bar': 2})
    v.baz = 3
    print(v['foo'])      # 1
    print(v.bar)         # 2
    v['qux'] = 4
    print(v.to_dict())   # {'foo': 1, 'bar': 2, 'baz': 3, 'qux': 4}
    for k in v: print(k, v[k])
"""

from typing import Any, Dict, Iterator, Optional, Union


class Values:
    """Flexible attribute container with dict-like and object-like access."""

    def __init__(self, defaults: Optional[dict] = None, **kwargs):
        """
        Initialize with an optional dict or keyword arguments.

        Args:
            defaults (dict, optional): Initial attributes.
            **kwargs: Additional attributes.
        """
        if defaults:
            for attr, val in defaults.items():
                setattr(self, attr, val)
        for attr, val in kwargs.items():
            setattr(self, attr, val)

    def __getitem__(self, key: str) -> Any:
        """Get attribute by key (dict-style)."""
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set attribute by key (dict-style)."""
        setattr(self, key, value)

    def __delitem__(self, key: str) -> None:
        """Delete attribute by key (dict-style)."""
        delattr(self, key)

    def __contains__(self, key: str) -> bool:
        """Check if attribute exists (as key or attribute)."""
        return hasattr(self, key)

    def __iter__(self) -> Iterator[str]:
        """Iterate over attribute names."""
        return (k for k in self.__dict__)

    def __len__(self) -> int:
        """Number of attributes."""
        return len(self.__dict__)

    def __str__(self) -> str:
        """String representation."""
        return str(self.__dict__)

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"<{self.__class__.__name__} {self.__dict__}>"

    def __eq__(self, other: object) -> bool:
        """Equality check with another Values or dict."""
        if isinstance(other, Values):
            return self.__dict__ == other.__dict__
        elif isinstance(other, dict):
            return self.__dict__ == other
        else:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Return a shallow copy of the attributes as a dict."""
        return dict(self.__dict__)

    def update(self, other: Union[dict, "Values"], **kwargs) -> None:
        """
        Update attributes from another dict, Values, or keyword arguments.

        Args:
            other (dict or Values): Source of new attributes.
            **kwargs: Additional attributes.
        """
        if isinstance(other, Values):
            other = other.to_dict()
        for k, v in other.items():
            setattr(self, k, v)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def copy(self) -> "Values":
        """Return a shallow copy of this Values object."""
        return Values(self.to_dict())

    def merge(self, other: Union[dict, "Values"], **kwargs) -> "Values":
        """
        Return a new Values with merged attributes.

        Args:
            other (dict or Values): Source of new attributes.
            **kwargs: Additional attributes.

        Returns:
            Values: New merged Values object.
        """
        merged = self.to_dict()
        if isinstance(other, Values):
            other = other.to_dict()
        merged.update(other)
        merged.update(kwargs)
        return Values(merged)

    def pretty(self, indent: int = 2) -> str:
        """Pretty-print the attributes."""
        import json

        return json.dumps(self.to_dict(), indent=indent)

    def export(self) -> dict:
        """Alias for to_dict()."""
        return self.to_dict()
