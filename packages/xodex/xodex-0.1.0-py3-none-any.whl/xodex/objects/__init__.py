"""Objects

Provides:
- Objects: A type-safe, ordered container for game objects.
- ObjectsManager: Scene-based registry for all objects.
- Base object types: DrawableObject, EventfulObject, LogicalObject.
"""

from typing import Iterable

from pygame import Surface
from pygame.event import Event

from xodex.objects.manager import ObjectsManager, register
from xodex.objects.objects import Object, DrawableObject, EventfulObject, LogicalObject

__all__ = (
    "make_xodex_object",
    "ObjectsManager",
    "DrawableObject",
    "EventfulObject",
    "LogicalObject",
    "register",
    "Objects",
    "Object",
)


class Objects(list):
    """A type-safe, ordered container for game objects."""

    _allowed_types_ = (LogicalObject, DrawableObject, EventfulObject)

    def __init__(self):
        list.__init__(self)

    # region Private
    def _check_type_(self, item):
        if not isinstance(item, self._allowed_types_):
            raise ValueError(f"Object type: {type(item)}/{item} is not in {self._allowed_types_}")

    def __iadd__(self, other):
        for item in other:
            self._check_type_(item)
        return super().__iadd__(other)

    # endregion

    # region Public

    def append(self, item) -> None:
        """Append an object, enforcing allowed types or instantiating if class."""
        if isinstance(item, type) and issubclass(item, self._allowed_types_):
            item = item()
        self._check_type_(item)
        super().append(item)

    def insert(self, index, item) -> None:
        """Insert an object at a given index, enforcing allowed types or instantiating if class."""
        if isinstance(item, type) and issubclass(item, self._allowed_types_):
            item = item()
        self._check_type_(item)
        super().insert(index, item)

    def extend(self, iterable: Iterable) -> None:
        """Extend with an iterable, enforcing allowed types or instantiating if class."""
        items = []
        for item in iterable:
            if isinstance(item, type) and issubclass(item, self._allowed_types_):
                item = item()
            self._check_type_(item)
            items.append(item)
        super().extend(items)

    def update_object(self, deltatime: float, *args, **kwargs) -> None:
        """Update all LogicalObjects."""
        filtered: Iterable[LogicalObject] = filter(lambda x: isinstance(x, LogicalObject), self)
        for object in filtered:
            object.update_xodex_object(deltatime, *args, **kwargs)

    def draw_object(self, surface: Surface, *args, **kwargs) -> None:
        """Draw all DrawableObjects, sorted by z_index if present."""
        filtered: Iterable[DrawableObject] = filter(lambda x: isinstance(x, DrawableObject), self)
        sorted_objs = filtered  # sorted(filtered, key=lambda object: getattr(object, "z_index", 0))
        for object in sorted_objs:
            object.draw_xodex_object(surface, *args, **kwargs)

    def handle_object(self, event: Event, *args, **kwargs) -> None:
        """Dispatch event to all EventfulObjects."""
        filtered: Iterable[EventfulObject] = filter(lambda x: isinstance(x, EventfulObject), self)
        for object in filtered:
            object.handle_xodex_event(event, *args, **kwargs)

    # endregion


def make_xodex_object(
    cls=None,
    *,
    base_classes: tuple[type, ...] = (),
    register: bool = False,
    name: str = None,
    doc: str = None,
):
    """
    Create a Xodex object from any class, validating required methods for each base.

    Args:
        cls (type, optional): The class to convert. If None, returns a decorator.
        base_classes (tuple[type, ...], optional): Xodex base classes to inherit from.
        register (bool, optional): Whether to register the object with ObjectsManager.
        name (str, optional): Name to register the object as. Defaults to class name.
        doc (str, optional): Docstring to set on the new class.

    Returns:
        type: The new Xodex object class, or a decorator if cls is None.

    Raises:
        TypeError: If the class does not implement required methods for the selected base(s).

    Usage:
        @makeobject(base_classes=(DrawableObject,), register=True)
        class MySprite:
            ...

        # or
        MyObject = makeobject(MyClass, base_classes=(LogicalObject,), register=True)
    """

    # Map base class to required method(s)
    REQUIRED_METHODS = {
        LogicalObject: ["perform_update"],
        DrawableObject: ["perform_draw"],
        EventfulObject: ["handle_event"],
    }

    def validate_methods(object_cls, bases):
        missing = []
        for base in bases:
            reqs = REQUIRED_METHODS.get(base, [])
            for method in reqs:
                if not callable(getattr(object_cls, method, None)):
                    missing.append(method)
        if missing:
            raise TypeError(f"Class '{object_cls.__name__}' is missing required method(s): {', '.join(missing)}")

    def decorator(object_cls):
        validate_methods(object_cls, base_classes)
        bases = base_classes + (object_cls,)
        object_name = name or object_cls.__name__
        new_cls = type(object_name, bases, dict(object_cls.__dict__))
        if doc:
            new_cls.__doc__ = doc
        if register:
            ObjectsManager().register(new_cls, object_name)
        return new_cls

    if cls is None:
        return decorator
    return decorator(cls)
