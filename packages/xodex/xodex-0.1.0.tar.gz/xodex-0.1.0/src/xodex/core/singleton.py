"""Singleton"""

__all__ = ("Singleton", "singleton")


class SingletonMeta(type):
    """Metaclass for Pattern Singleton"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """Easy use of SingletonMeta"""


def singleton(cls):
    """singleton"""

    _instance = None

    def get_instance():
        nonlocal _instance
        if _instance is None:
            _instance = cls()
        return _instance

    return get_instance
