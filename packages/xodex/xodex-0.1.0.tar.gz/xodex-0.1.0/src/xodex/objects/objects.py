"""Objects

Defines base classes for game objects:
- LogicalObject: Updatable logic objects.
- DrawableObject: Renderable objects.
- EventfulObject: Objects that handle events.
"""

import time
from typing import Union
from abc import ABC, abstractmethod

from pygame import Surface
from pygame.event import Event

__all__ = ("DrawableObject", "Object", "EventfulObject", "LogicalObject")


class Object:
    """Base class for all game objects."""


class LogicalObject(Object, ABC):
    """
    Abstract base class for logical (updatable) game objects.

    Inherit from this class and implement `perform_update` to define how the object updates its logic.
    Optionally, use `update_enabled` and `update_profile` for advanced update control.

    Provides a three-phase update process:
    - before_update: Pre-update hook (e.g., prepare state)
    - perform_update: Actual update logic (must be implemented)
    - after_update: Post-update hook (e.g., finalize state)

    Features:
    - Enable/disable updating at runtime.
    - Optional update profiling.
    - Update error handling hook.
    """

    update_enabled: bool = True  # Toggle updating on/off
    update_profile: bool = False  # Enable profiling of update time

    def update_xodex_object(self, deltatime: float, *args, **kwargs) -> None:
        """
        Update the instance.

        Args:
            deltatime (float): Time since last update in seconds.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        if not getattr(self, "update_enabled", True):
            return
        start_time = time.perf_counter() if getattr(self, "update_profile", False) else None
        try:
            self.before_update()
            self.perform_update(deltatime, *args, **kwargs)
            self.after_update(*args, **kwargs)
        except Exception as exc:
            self.on_update_error(exc)
        finally:
            if start_time is not None:
                elapsed = time.perf_counter() - start_time
                self.on_update_profile(elapsed, *args, **kwargs)

    @abstractmethod
    def perform_update(self, deltatime: float, *args, **kwargs) -> None:
        """
        Actual update logic. Must be implemented by subclass.

        Args:
            deltatime (float): Time since last update in seconds.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        raise NotImplementedError("`perform_update()` must be implemented.")

    def enable_update(self) -> None:
        """Enable logic updates for this object."""
        self.update_enabled = True

    def disable_update(self) -> None:
        """Disable logic updates for this object."""
        self.update_enabled = False

    def before_update(self) -> None:
        """Hook called before update. Override as needed."""

    def after_update(self) -> None:
        """Hook called after update. Override as needed."""

    def on_update_profile(self, elapsed: float, *args, **kwargs) -> None:
        """
        Hook called with elapsed time if update_profile is enabled.

        Args:
            elapsed (float): Time in seconds spent in update().
        """
        # Override to log or collect update timing.

    def on_update_error(self, exc: Exception):
        """Hook called if an exception occurs during update."""
        # Override to log or handle update errors.


class DrawableObject(Object, ABC):
    """
    Abstract base class for drawable game objects.

    Inherit from this class and implement `perform_draw` to define how the object is rendered.
    Optionally, use `visible`  for advanced rendering control.

    Provides a three-phase draw process:
    - before_draw: Pre-draw hook (e.g., set up state)
    - perform_draw: Actual drawing logic (must be implemented)
    - after_draw: Post-draw hook (e.g., clean up state)

    Features:
    - Enable/disable drawing at runtime.
    - Optional draw profiling.
    - Draw error handling hook.
    - Supports visibility toggling.
    """

    visible: bool = True
    draw_enabled: bool = True  # Toggle drawing on/off
    draw_profile: bool = False  # Enable profiling of draw time

    def draw_xodex_object(self, surface: Surface, *args, **kwargs) -> None:
        """
        Draw the object if visible.

        Args:
            surface (Surface): The Pygame surface to draw on.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """

        if not getattr(self, "draw_enabled", True):
            return
        start_time = time.perf_counter() if getattr(self, "draw_profile", False) else None
        try:
            self.before_draw()
            self.perform_draw(surface, *args, **kwargs)
            self.after_draw()
        except Exception as exc:
            self.on_draw_error(exc)
        finally:
            if start_time is not None:
                elapsed = time.perf_counter() - start_time
                self.on_draw_profile(elapsed, surface, *args, **kwargs)

    @abstractmethod
    def perform_draw(self, surface: Surface, *args, **kwargs) -> None:
        """
        Actual drawing logic. Must be implemented by subclass.

        Args:
            surface (Surface): The Pygame surface to draw on.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        raise NotImplementedError("`perform_draw()` must be implemented.")

    def set_visible(self, visible: bool) -> None:
        """
        Set the visibility of the object.

        Args:
            visible (bool): If False, draw() will do nothing.
        """
        self.visible = visible

    def before_draw(self) -> None:
        """Hook called before drawing. Override as needed."""

    def after_draw(self) -> None:
        """Hook called after drawing. Override as needed."""

    def on_draw_profile(self, elapsed: float, surface: Surface, *args, **kwargs) -> None:
        """
        Hook called with elapsed time if draw_profile is enabled.

        Args:
            elapsed (float): Time in seconds spent in draw().
            surface (Surface): The Pygame surface.
        """
        # Override to log or collect draw timing.

    def on_draw_error(self, exc: Exception):
        """Hook called if an exception occurs during draw."""
        # Override to log or handle draw errors.


class EventfulObject(Object, ABC):
    """
    Abstract base class for eventful game objects.

    Inherit from this class and implement `handle_event` to define how the object responds to events.
    Use event filters and handler binding for advanced event management.

    Provides a three-phase event process:
    - before_event: Pre-event hook (e.g., filter or preprocess event)
    - handle_event: Actual event handling logic (must be implemented)
    - after_event: Post-event hook (e.g., logging or cleanup)

    Features:
    - Supports binding multiple event handlers and event filtering.
    - Event type-based handler registry.
    - Optional event profiling and error handling.
    """

    event_profile: bool = False
    event_enabled: bool = True  # Toggle Interaction on/off

    def handle_xodex_event(self, event: Event, *args, **kwargs) -> None:
        """
        Handle an event.

        Args:
            event (Event): The Pygame event to handle.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        if not getattr(self, "event_enabled", True):
            return

        start_time = time.perf_counter() if getattr(self, "event_profile", False) else None
        try:
            self.before_event()
            self.handle_event(event, *args, **kwargs)
            self.after_event()
        except Exception as exc:
            self.on_event_error(exc)
        finally:
            if start_time is not None:
                elapsed = time.perf_counter() - start_time
                self.on_event_profile(elapsed, event, *args, **kwargs)

    @abstractmethod
    def handle_event(self, event: Event, *args, **kwargs) -> None:
        """
        Main event handler. Must be implemented by subclass.

        Args:
            event (Event): The Pygame event to handle.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        raise NotImplementedError("`handle_event()` must be implemented.")

    def before_event(self) -> None:
        """Hook called before event handling. Override as needed."""

    def after_event(self) -> None:
        """Hook called after event handling. Override as needed."""

    def on_event_profile(self, elapsed: float, event: Event, *args, **kwargs) -> None:
        """
        Hook called with elapsed time if event_profile is enabled.

        Args:
            elapsed (float): Time in seconds spent in event().
            event (Event): The event being handled.
        """
        # Override to log or collect event timing.

    def on_event_error(self, exc: Exception):
        """Hook called if an exception occurs during event handling."""
        # Override to log or handle event errors.

    def enable_event(self):
        """Enable the object for interaction."""
        self.event_enabled = True

    def disable_event(self):
        """Disable the object for interaction."""
        self.event_enabled = False


def make_xodex_object(
    cls=None,
    base_classes: tuple[type, ...] = (),
    register: bool = False,
    name: str = None,
    doc: str = None,
    method_map: dict = None,
    hooks: dict = None,
    **kwargs,
) -> Union[DrawableObject, EventfulObject, LogicalObject]:
    """
    Dynamically create a Xodex-compatible object class from any user class.

    This function adapts a user-defined class to Xodex's object system by:
      - Validating required methods for each selected Xodex base (LogicalObject, DrawableObject, EventfulObject).
      - Optionally renaming user methods to match Xodex's expected method names (via `method_map`).
      - Injecting custom hooks (e.g., before/after draw/update/event).
      - Optionally registering the new class with an object manager.

    Args:
        cls (type, optional): The class to convert. If None, returns a decorator.
        base_classes (tuple[type, ...], optional): Xodex base classes to inherit from.
        register (bool, optional): Whether to register the object with ObjectsManager.
        name (str, optional): Name to register the object as. Defaults to class name.
        doc (str, optional): Docstring to set on the new class.
        method_map (dict, optional): Map of {Xodex method: user method name}.
            Example: {"perform_draw": "draw", "perform_update": "update", "handle_event": "handle"}
        hooks (dict, optional): Map of {hook_name: callable} to override hooks.
        **kwargs: Additional hooks (e.g., before_draw, after_update).

    Returns:
        type: The new Xodex object class, or a decorator if cls is None.

    Raises:
        TypeError: If the class does not implement required methods for the selected base(s).

    Example:
        @make_xodex_object(base_classes=(DrawableObject,))
        class MySprite:
            def draw(self, surface): ...
        # or
        MyObject = make_xodex_object(MyClass, base_classes=(LogicalObject,), method_map={"perform_update": "update"})
    """
    REQUIRED_METHODS = {}

    method_map = method_map or {}
    hooks = hooks or {}

    flags = {
        "is_drawable": False,
        "is_eventful": False,
        "is_logical": False,
    }
    REQUIRED_METHODS.update({LogicalObject: method_map.get("perform_update", "perform_update")})
    REQUIRED_METHODS.update({DrawableObject: method_map.get("perform_draw", "perform_draw")})
    REQUIRED_METHODS.update({EventfulObject: method_map.get("handle_event", "handle_event")})

    def validate_methods(object_cls, base_classes, flags):
        missing = []
        for base in base_classes:
            required = REQUIRED_METHODS.get(base, None)
            if not required or not callable(getattr(object_cls, required, None)):
                missing.append(required)
            if issubclass(base, DrawableObject):
                flags["is_drawable"] = True
            if issubclass(base, EventfulObject):
                flags["is_eventful"] = True
            if issubclass(base, LogicalObject):
                flags["is_logical"] = True
        if missing:
            raise TypeError(f"Class '{object_cls.__name__}' is missing required method(s): {', '.join(missing)}")

    def __rename_method__(object_cls, old_name, new_name):
        """Rename a method in the class dictionary."""
        if hasattr(object_cls, old_name):
            method = getattr(object_cls, old_name)
            setattr(object_cls, new_name, method)
            # if old_name != new_name:
            #     delattr(object_cls, old_name)

    def rename_methods(object_cls):
        # Map user methods to Xodex expected names
        if flags["is_drawable"]:
            user_method = REQUIRED_METHODS.get(DrawableObject)
            __rename_method__(object_cls, user_method, "perform_draw")
        if flags["is_eventful"]:
            user_method = REQUIRED_METHODS.get(EventfulObject)
            __rename_method__(object_cls, user_method, "handle_event")
        if flags["is_logical"]:
            user_method = REQUIRED_METHODS.get(LogicalObject)
            __rename_method__(object_cls, user_method, "perform_update")

    def decorator(object_cls):
        validate_methods(object_cls, base_classes, flags)
        rename_methods(object_cls)

        bases = base_classes + (object_cls,)
        object_name = name or object_cls.__name__
        new_cls_dict = dict(object_cls.__dict__)

        # Attach hooks (before/after, etc.)
        for hook_name, hook_func in {**hooks, **kwargs}.items():
            if callable(hook_func):
                new_cls_dict[hook_name] = hook_func

        new_cls = type(object_name, bases, new_cls_dict)
        new_cls.__doc__ = doc or object_cls.__doc__

        if register:
            # Registration logic can be added here
            pass

        return new_cls

    if cls is None:
        return decorator
    return decorator(cls)
