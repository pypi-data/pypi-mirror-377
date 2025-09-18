import asyncio
from abc import ABC, abstractmethod
from typing import Union, Generator, Callable, Optional, Any, TYPE_CHECKING

import pygame
from pygame.event import Event

from xodex.conf import settings
from xodex.game.sounds import Sounds
from xodex.utils.log import get_xodex_logger
from xodex.objects.manager import ObjectsManager
from xodex.objects import Objects, DrawableObject, EventfulObject, LogicalObject

logger = get_xodex_logger(__name__)

if TYPE_CHECKING:
    from xodex.scenes.manager import SceneManager


__all__ = ("BaseScene",)


class BaseScene(ABC):
    """
    Abstract base class for all scenes in the Xodex engine.

    Provides a standard interface and utility methods for scene management,
    including object handling, drawing, updating, event processing, lifecycle hooks,
    async support, event queue, filtering, snapshot/export, and debug overlay.

    Attributes:
        setting: The imported settings module (from XODEX_SETTINGS_MODULE).
        _size (tuple[int, int]): The window size for the scene.
        _debug (bool): Debug mode flag.
        _start_time (float): Time when the scene was created (seconds).
        _screen (pygame.Surface): The surface representing the scene.
        _objects (Objects): The collection of drawable/eventful/logical objects.
        _object: The global object manager's objects.
        _paused (bool): Whether the scene is currently paused.
        _background_color (tuple[int, int, int]): Background color for the scene.
        _event_queue (list[Event]): Scene-level event queue.
        _debug_overlay (bool): Whether to draw debug overlay.
        _first_entered (bool): Whether the scene has been entered at least once.
        _height (int): Scene surface height.
        _width (int): Scene surface width.

    Methods:
        elapsed: Elapsed time since scene started (seconds).
        screen: Returns the scene's surface.
        object: Returns the object manager's objects.
        get_object(object_name): Get an object by name from the manager.
        size: Returns the scene's window size.
        draw_scene: Draw all objects to the scene surface.
        update_scene: Update all objects in the scene.
        handle_scene: Handle an event for all objects.
        setup: Clear and regenerate scene objects.
        pause/resume/toggle_pause: Control scene pause state.
        is_paused: Check if the scene is paused.
        set_background_color: Set the background color.
        get_background_color: Get the background color.
        add_event: Add an event to the scene queue.
        dispatch_events: Dispatch all queued events.
        filter_objects: Filter objects by type or predicate.
        snapshot: Return a copy of the scene surface.
        export_image: Save the scene surface to an image file.
        save_state/load_state: Save/load scene state (basic).
        toggle_debug_overlay: Toggle debug overlay.
        draw_debug_overlay: Draw debug info on the scene.
        on_enter/on_exit/on_first_enter/on_last_exit/on_pause/on_resume: Scene lifecycle hooks.

    Usage:
        class MyScene(BaseScene):
            def _generate_objects_(self):
                yield MyPlayer()
                yield MyEnemy()
    """

    def __init__(self, *args, **kwargs) -> "BaseScene":
        """
        Initialize the scene, loading settings and preparing the surface and objects.
        """
        from xodex.scenes.manager import SceneManager

        self._size = settings.WINDOW_SIZE or (560, 480)
        self._debug = settings.DEBUG or True
        self._start_time = pygame.time.get_ticks() / 1000
        self._screen = pygame.Surface(self._size)
        self._object = ObjectsManager().get_objects()
        self._manager = SceneManager()
        self._sounds = Sounds().reload_sounds()
        self._objects = Objects()
        self._paused = False
        self._background_color = (255, 255, 255)
        self._first_entered = False
        self._height = self._size[1]
        self._width = self._size[0]
        self._event_queue: list[Event] = []
        self._debug_overlay = False

    def __str__(self):
        """Return a string representation of the Scene."""
        return f"<{self.__class__.__name__} Scene> elapsed: {self.elapsed:.2f}s paused: {self._paused}"

    def __repr__(self):
        """Return a string representation of the Scene."""
        return f"{self.__class__.__name__}()"

    # region Private

    @abstractmethod
    def _generate_objects_(self) -> Generator:
        """
        Abstract method to generate scene objects.
        Should yield or return objects to be added to the scene.
        """
        raise NotImplementedError

    def _on_resize(self, size):
        """
        Handle window resize event.

        Args:
            size (tuple[int, int]): New window size.
        """
        self._size = size
        self._screen = pygame.Surface(self._size)
        self._height = self._size[1]
        self._width = self._size[0]
        if self._debug:
            logger.info(f"SceneWindow resized to: {self._size}")

    # endregion

    # region Public

    @property
    def elapsed(self) -> float:
        """
        Elapsed time since scene started (seconds).

        Returns:
            float: Seconds since scene was created.
        """
        return pygame.time.get_ticks() / 1000 - self._start_time

    @property
    def height(self) -> int:
        """Return the Scene Surface Height."""
        return self._height

    @property
    def width(self) -> int:
        """Return the Scene Surface Width."""
        return self._width

    @property
    def screen(self) -> pygame.Surface:
        """Return the Scene Surface."""
        return self._screen

    @property
    def object(self) -> ObjectsManager:
        """Return Object Manager's objects."""
        return self._object

    @property
    def objects(self) -> Objects:
        """Return all Scene's objects."""
        return self._objects

    @property
    def manager(self) -> "SceneManager":
        """Return Scene Manager."""
        return self._manager

    @property
    def sounds(self) -> Sounds:
        """Return Sounds."""
        return self._sounds.reload_sounds()

    def get_object(self, object_name: str) -> Union[DrawableObject, EventfulObject, LogicalObject, None]:
        """
        Get an object by name from the global object manager.

        Args:
            object_name (str): The name of the object.

        Returns:
            DrawableObject | EventfulObject | LogicalObject | None: The requested object, or None if not found.
        """
        return ObjectsManager().get_object(object_name=object_name)

    @property
    def size(self) -> tuple[int, int]:
        """Return the Scene Screen Size (width, height)."""
        return self._size

    def draw_scene(self, *args, **kwargs) -> pygame.Surface:
        """
        Draw all objects to the scene surface, and optionally the debug overlay.

        Returns:
            pygame.Surface: The updated scene surface.
        """
        self._screen.fill(self._background_color)
        self._objects.draw_object(self._screen, *args, **kwargs)
        if self._debug_overlay:
            self.draw_debug_overlay()
        return self._screen

    def update_scene(self, deltatime: float, *args, **kwargs) -> None:
        """
        Update all objects in the scene, unless paused.

        Args:
            deltatime (float): Time since last update (ms).
        """
        if not self._paused:
            self._objects.update_object(deltatime, *args, **kwargs)

    async def async_update_scene(self, deltatime: float, *args, **kwargs) -> None:
        """
        Async version of update_scene.
        """
        if not self._paused:
            await asyncio.sleep(0)
            self._objects.update_object(deltatime, *args, **kwargs)

    def handle_scene(self, event: Event, *args, **kwargs) -> None:
        """
        Handle an event for all objects in the scene.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.VIDEORESIZE:
            self._on_resize(event.size)
        if not self._paused:
            self._objects.handle_object(event, *args, **kwargs)

    def add_event(self, event: Event) -> None:
        """
        Add an event to the scene's event queue.

        Args:
            event (pygame.event.Event): The event to queue.
        """
        self._event_queue.append(event)

    def dispatch_events(self) -> None:
        """
        Dispatch all queued events to the scene's objects.
        """
        while self._event_queue:
            event = self._event_queue.pop(0)
            self.handle_scene(event)

    def filter_objects(
        self, predicate: Optional[Callable[[Any], bool]] = None, obj_type: Optional[type] = None
    ) -> list:
        """
        Filter objects in the scene by a predicate or type.

        Args:
            predicate: Callable that returns True for objects to include.
            obj_type: Type to filter by.

        Returns:
            list: Filtered objects.
        """
        objs = list(self._objects)
        if obj_type:
            objs = [o for o in objs if isinstance(o, obj_type)]
        if predicate:
            objs = [o for o in objs if predicate(o)]
        return objs

    def snapshot(self) -> pygame.Surface:
        """
        Return a copy of the current scene surface.

        Returns:
            pygame.Surface: A copy of the scene's surface.
        """
        return self._screen.copy()

    def export_image(self, filename: str) -> None:
        """
        Save the current scene surface to an image file.

        Args:
            filename (str): Path to save the image.
        """
        pygame.image.save(self._screen, filename)
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] Scene exported to {filename}")

    def save_state(self) -> dict:
        """
        Save the scene state (basic example).

        Returns:
            dict: Serializable state.
        """
        return {
            "paused": self._paused,
            "background_color": self._background_color,
            "elapsed": self.elapsed,
        }

    def load_state(self, state: dict) -> None:
        """
        Load the scene state (basic example).

        Args:
            state (dict): State to load.
        """
        self._paused = state.get("paused", self._paused)
        self._background_color = state.get("background_color", self._background_color)

    def toggle_debug_overlay(self) -> None:
        """
        Toggle the debug overlay on/off.
        """
        self._debug_overlay = not self._debug_overlay

    def draw_debug_overlay(self) -> None:
        """
        Draw debug information on the scene surface.
        """
        font = pygame.font.SysFont("consolas", 16)
        info = [
            f"Scene: {self.__class__.__name__}",
            f"Elapsed: {self.elapsed:.2f}s",
            f"Paused: {self._paused}",
            f"Objects: {len(self._objects)}",
            f"Size: {self._size}",
        ]
        for i, line in enumerate(info):
            surf = font.render(line, True, (0, 0, 0))
            self._screen.blit(surf, (8, 8 + i * 18))

    def setup(self):
        """
        Clear and regenerate scene objects by calling _generate_objects_.
        """
        self._objects.clear()
        if objects := self._generate_objects_():
            self._objects.extend(list(objects))
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] Objects after setup: {len(self._objects)}")

    async def async_setup(self):
        """
        Async version of setup.
        """
        self._objects.clear()
        objects = self._generate_objects_()
        if asyncio.iscoroutine(objects):
            objects = await objects
        if objects:
            self._objects.extend(list(objects))
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] Objects after setup: {len(self._objects)}")

    def pause(self):
        """Pause the scene (updates and event handling will be skipped)."""
        if not self._paused:
            self._paused = True
            self.on_pause()
            if self._debug:
                logger.info(f"[{self.__class__.__name__}] Scene paused.")

    def resume(self):
        """Resume the scene (updates and event handling will continue)."""
        if self._paused:
            self._paused = False
            self.on_resume()
            if self._debug:
                logger.info(f"[{self.__class__.__name__}] Scene resumed.")

    def toggle_pause(self):
        """Toggle the pause state of the scene."""
        if self._paused:
            self.resume()
        else:
            self.pause()

    @property
    def is_paused(self) -> bool:
        """Return whether the scene is currently paused."""
        return self._paused

    def set_background_color(self, color: tuple[int, int, int]):
        """
        Set the background color for the scene.

        Args:
            color (tuple[int, int, int]): RGB color.
        """
        self._background_color = color
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] Background color set to: {self._background_color}")

    def get_background_color(self) -> tuple[int, int, int]:
        """
        Get the current background color.

        Returns:
            tuple[int, int, int]: The RGB color.
        """
        return self._background_color

    # endregion

    # region Private

    def _on_scene_exit_(self, *args, **kwargs) -> None:
        """Runs When exiting scene."""
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] on_exit called.")
        self.on_exit(*args, **kwargs)

    def _on_scene_last_exit_(self, *args, **kwargs) -> None:
        """Runs the last time the scene is exited."""
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] on_last_exit called.")
        self.on_last_exit(*args, **kwargs)

    def _on_scene_enter_(self, *args, **kwargs) -> None:
        """Runs when entering Scene."""
        if not self._first_entered:
            self._on_scene_first_enter_(*args, **kwargs)
            self._first_entered = True
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] on_enter called.")
        self.on_enter(*args, **kwargs)

    def _on_scene_first_enter_(self, *args, **kwargs) -> None:
        """Runs the first time the scene is entered."""
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] on_first_enter called.")
        self.on_first_enter(*args, **kwargs)

    # endregion

    # region Hooks

    def on_enter(self, *args, **kwargs) -> None:
        """
        Runs when entering the scene.
        Override in subclasses for custom behavior.
        """

    def on_exit(self, *args, **kwargs) -> None:
        """
        Runs when exiting the scene.
        Override in subclasses for custom behavior.
        """

    def on_first_enter(self, *args, **kwargs) -> None:
        """
        Runs the first time the scene is entered.
        Override in subclasses for custom behavior.
        """

    def on_last_exit(self, *args, **kwargs) -> None:
        """
        Runs the last time the scene is exited.
        Override in subclasses for custom behavior.
        """

    def on_pause(self, *args, **kwargs) -> None:
        """
        Runs when the scene is paused.
        Override in subclasses for custom behavior.
        """
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] on_pause called.")

    def on_resume(self, *args, **kwargs) -> None:
        """
        Runs when the scene is resumed from pause.
        Override in subclasses for custom behavior.
        """
        if self._debug:
            logger.info(f"[{self.__class__.__name__}] on_resume called.")

    # endregion
