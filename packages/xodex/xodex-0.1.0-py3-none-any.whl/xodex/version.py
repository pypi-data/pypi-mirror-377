"""Xodex version."""

__all__ = ["Version", "vernum"]


class Version(tuple):
    """Version class."""

    __slots__ = ()
    fields = "major", "minor", "patch"

    def __new__(cls, major, minor, patch) -> "Version":
        return tuple.__new__(cls, (major, minor, patch))

    def __repr__(self) -> str:
        fields = (f"{fld}={val}" for fld, val in zip(self.fields, self))
        return f'{self.__class__.__name__}({", ".join(fields)})'

    def __str__(self) -> str:
        return f"{self[0]}.{self[1]}.{self[2]}"

    major = property(lambda self: self[0])
    minor = property(lambda self: self[1])
    patch = property(lambda self: self[2])


vernum = Version(25, 6, 27)


def get_version():
    """
    Return the version as a tuple and string.

    Returns:
        tuple: (major, minor, patch)
        str: version string
    """
    if isinstance(vernum, (tuple, list)):
        return tuple(vernum), ".".join(map(str, vernum))
    return (vernum,), str(vernum)


def is_version_at_least(version):
    """
    Check if the current version is at least the given version.

    Args:
        version (str|tuple): Version string or tuple, e.g. "1.2.3" or (1,2,3)
    Returns:
        bool: True if current version >= version
    """

    def parse(v):
        if isinstance(v, str):
            return tuple(int(x) for x in v.split("."))
        return tuple(v)

    current = parse(vernum)
    target = parse(version)
    return current >= target
