import asyncio
from typing import Union, Callable, Optional, Any, Type
from pygame import Surface

from xodex.utils.log import get_xodex_logger

from xodex.utils.values import Values
from xodex.core.singleton import Singleton
from xodex.scenes.base_scene import BaseScene
from xodex.contrib.mainscene import XodexMainScene
from xodex.core.exceptions import NotRegistered, AlreadyRegistered, SceneError

try:
    import pygameui

    HAS_PYGAMEUI = True
except ImportError:
    HAS_PYGAMEUI = False

if HAS_PYGAMEUI:
    from xodex.contrib.pygameui.uiscene import XodexUIScene

__all__ = ("SceneManager", "register")

logger = get_xodex_logger(__name__)


class SceneManager(Singleton):
    """
    Scene Manager with stack navigation, transitions, scene lookup, and hooks.

    Features:
        - Stack-based scene navigation (push, pop, replace, clear, swap, jump)
        - Scene registration and lookup by name, class, or index
        - Transition effects (fade, slide, custom)
        - Async support for transitions and hooks
        - Scene hooks: before/after enter/exit, user callbacks
        - Logging for key actions

    Usage:
        manager = SceneManager()
        manager.append("XodexMainScene")
        manager.transition_to("MyScene", transition_type="fade", duration=1.0)
        manager.pop()
        manager.reset("AnotherScene")
    """

    def __init__(self):
        self.__scene_classes: dict[str, Type[BaseScene]] = {}
        self.__scenes: list[BaseScene] = []
        self._user_hooks: dict[str, list[Callable]] = {}

        # Register default scenes
        self.register(XodexMainScene, "XodexMainScene")
        if HAS_PYGAMEUI:
            self.register(XodexUIScene, "XodexUIScene")

    # region Properties

    @property
    def scene(self) -> Values:
        """Return all registered scene classes as a Values object."""
        return self.get_scenes()

    @property
    def current(self) -> Optional[BaseScene]:
        """Return the current (top) scene, or None if stack is empty."""
        try:
            return self.__scenes[-1]
        except IndexError:
            logger.warning("Scene stack is empty.")
            return None

    @property
    def previous(self) -> Optional[BaseScene]:
        """Return the previous scene, or None if not available."""
        if len(self.__scenes) > 1:
            return self.__scenes[-2]
        return None

    @property
    def all(self) -> list[BaseScene]:
        """Return a copy of the current scene stack."""
        return list(self.__scenes)

    @property
    def count(self) -> int:
        """Return the number of scenes in the stack."""
        return len(self.__scenes)

    # endregion

    # region Scene Registration

    def register(self, scene_class: Type[BaseScene], scene_name: str) -> None:
        """
        Register a scene class with a given name.

        Raises:
            AlreadyRegistered: If the scene is already registered.
            SceneError: If the class is not a subclass of BaseScene.
        """
        if not issubclass(scene_class, BaseScene):
            raise SceneError(f"{scene_class} is not a subclass of BaseScene.")
        if self.is_registered(scene_name):
            raise AlreadyRegistered(f"The Scene '{scene_name}' is already registered.")
        self.__scene_classes[scene_name] = scene_class
        logger.info(f"Registered scene '{scene_name}'.")

    def unregister(self, scene_name: str) -> None:
        """
        Unregister a scene class by name.

        Raises:
            NotRegistered: If the scene is not registered.
        """
        if not self.is_registered(scene_name):
            raise NotRegistered(f"The Scene '{scene_name}' is not registered.")
        del self.__scene_classes[scene_name]
        logger.info(f"Unregistered scene '{scene_name}'.")

    def is_registered(self, scene_name: str) -> bool:
        """Return True if a scene is registered by name."""
        return scene_name in self.__scene_classes

    # endregion

    # region Registry Lookup

    def get_scene_class(self, scene_name: str) -> Type[BaseScene]:
        """
        Get a registered scene class by name.

        Raises:
            KeyError: If the scene is not registered.
        """
        scene = self.__scene_classes.get(scene_name)
        if scene is not None:
            return scene
        raise KeyError(f"{scene_name} is not a valid Scene")

    def get_scenes(self) -> Values:
        """Get all registered scene classes as a Values object."""
        return Values(self.__scene_classes)

    def list_registered_scene_classes(self) -> list[str]:
        """List all registered scene class names."""
        return list(self.__scene_classes.keys())

    # endregion

    # region Stack Navigation

    def append(self, scene: Union[str, BaseScene], *args, **kwargs) -> None:
        """
        Push a new scene onto the stack.

        Args:
            scene: Scene name (str) or instance (BaseScene).
        """
        self._run_hook("before_exit")
        if isinstance(scene, str):
            scene = self.get_scene_class(scene)(*args, **kwargs)
        elif not isinstance(scene, BaseScene):
            raise SceneError("Scene must be a subclass of BaseScene or a string name.")
        self.__scenes.append(scene)
        self._setup_scene_()
        self._run_hook("after_enter")
        logger.info(f"Appended scene: {scene}")

    def pop(self) -> Optional[BaseScene]:
        """
        Pop the current scene and return it.

        Returns:
            The popped scene, or None if stack is empty.
        """
        if not self.__scenes:
            logger.warning("Cannot pop: scene stack is empty.")
            return None
        self._run_hook("before_exit")
        pop_scene = self.__scenes.pop()
        self._run_hook("after_enter")
        logger.info(f"Popped scene: {pop_scene}")
        return pop_scene

    def clear(self) -> None:
        """Remove all scenes and clear the stack."""
        for s in self.__scenes:
            s.on_last_exit()
        self.__scenes.clear()
        logger.info("Cleared all scenes from stack.")

    def reset(self, scene: Union[str, BaseScene], *args, **kwargs) -> None:
        """
        Replace all scenes with a new one.

        Args:
            scene: Scene name (str) or instance (BaseScene).
        """
        for s in self.__scenes:
            s.on_last_exit()
        if isinstance(scene, str):
            scene = self.get_scene_class(scene)(*args, **kwargs)
        elif not isinstance(scene, BaseScene):
            raise SceneError("Scene must be a subclass of BaseScene or a string name.")
        self.__scenes = [scene]
        self._setup_scene_()
        self._run_hook("after_enter")
        logger.info(f"Reset scene stack with: {scene}")

    def swap(self, scene: Union[str, BaseScene], *args, **kwargs) -> None:
        """
        Swap the current scene with a new one.

        Args:
            scene: Scene name (str) or instance (BaseScene).
        """
        if self.__scenes:
            self.pop()
        self.append(scene, *args, **kwargs)
        logger.info(f"Swapped to scene: {scene}")

    def jump(self, index: int) -> None:
        """
        Jump to a scene at a specific index in the stack.

        Args:
            index: Index of the scene in the stack.
        """
        if not (0 <= index < len(self.__scenes)):
            raise IndexError("Scene index out of range.")
        while len(self.__scenes) > index + 1:
            self.pop()
        logger.info(f"Jumped to scene at index {index}.")

    # endregion

    # region Stack Lookup

    def get_scene(self, scene_name: str) -> Optional[BaseScene]:
        """
        Get a scene instance from the stack by name.

        Args:
            scene_name: Name of the scene.

        Returns:
            The scene instance, or None if not found.
        """
        for scene in self.__scenes:
            if getattr(scene, "name", None) == scene_name or scene.__class__.__name__ == scene_name:
                return scene
        logger.warning(f"Scene '{scene_name}' not found in stack.")
        return None

    def get_scene_by_index(self, index: int) -> Optional[BaseScene]:
        """
        Get a scene instance by index in the stack.

        Args:
            index: Index of the scene.

        Returns:
            The scene instance, or None if out of range.
        """
        if 0 <= index < len(self.__scenes):
            return self.__scenes[index]
        logger.warning(f"Scene index {index} out of range.")
        return None

    def list_scenes(self) -> list[str]:
        """List all scene names currently in the stack."""
        return [scene.__class__.__name__ for scene in self.__scenes]

    # endregion

    # region Scene Processing

    def process_update(self) -> None:
        """Update the current scene."""
        if self.current:
            self.current.update()

    def process_event(self, event: Any) -> None:
        """Send an event to the current scene."""
        if self.current:
            self.current.handle(event)

    def process_draw(self) -> Optional[Surface]:
        """Draw the current scene and return the surface."""
        if self.current:
            return self.current.draw()
        return None

    # endregion

    # region Transitions

    def transition_to(
        self,
        new_scene: Union[str, BaseScene],
        transition_type: str = "fade",
        duration: float = 1.0,
        on_complete: Optional[Callable] = None,
    ) -> None:
        """
        Transition to a new scene with an effect.

        Args:
            new_scene: Scene name or instance.
            transition_type: "fade", "slide", or "none".
            duration: Duration of the transition in seconds.
            on_complete: Optional callback after transition.
        """
        if isinstance(new_scene, str):
            new_scene = self.get_scene_class(new_scene)()
        if transition_type == "fade":
            self._fade_transition(new_scene, duration, on_complete)
        elif transition_type == "slide":
            self._slide_transition(new_scene, duration, on_complete)
        else:
            self.append(new_scene)
            if on_complete:
                on_complete()

    def _fade_transition(self, new_scene: BaseScene, duration: float, on_complete: Optional[Callable] = None):
        """Fade out, switch scene, fade in."""
        import pygame

        screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        alpha_surface = pygame.Surface(screen.get_size())
        alpha_surface.fill((0, 0, 0))
        for alpha in range(0, 255, max(1, int(255 / (duration * 60)))):
            self.process_draw()
            alpha_surface.set_alpha(alpha)
            screen.blit(alpha_surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)
        self.append(new_scene)
        if on_complete:
            on_complete()

    def _slide_transition(self, new_scene: BaseScene, duration: float, on_complete: Optional[Callable] = None):
        """Slide transition (left to right)."""
        import pygame

        screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        width, height = screen.get_size()
        for offset in range(0, width + 1, max(1, int(width / (duration * 60)))):
            self.process_draw()
            temp_surface = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(temp_surface, (offset, 0))
            pygame.display.flip()
            clock.tick(60)
        self.append(new_scene)
        if on_complete:
            on_complete()

    async def async_transition_to(
        self,
        new_scene: Union[str, BaseScene],
        transition_type: str = "fade",
        duration: float = 1.0,
        on_complete: Optional[Callable] = None,
    ) -> None:
        """
        Async version of transition_to.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self.transition_to(new_scene, transition_type, duration, on_complete))

    # endregion

    # region Hooks

    def add_hook(self, event: str, callback: Callable) -> None:
        """
        Add a user callback for a scene event.

        Args:
            event: "before_exit", "after_enter", etc.
            callback: Callable to run.
        """
        self._user_hooks.setdefault(event, []).append(callback)

    def _run_hook(self, event: str) -> None:
        """Run user and internal hooks for a given event."""
        # User hooks
        for cb in self._user_hooks.get(event, []):
            try:
                cb(self)
            except Exception as e:
                logger.error(f"Error in user hook '{event}': {e}")
        # Internal hooks
        method = getattr(self, f"_{event}_", None)
        if callable(method):
            method()

    # endregion

    # region Private/Internal

    def _setup_scene_(self, *args, **kwargs) -> None:
        """Call setup on the current scene."""
        if self.current:
            self.current.setup(*args, **kwargs)

    def _before_exit_(self, *args, **kwargs) -> None:
        """Internal: call on_exit on current scene."""
        if self.current:
            self.current._on_scene_exit_(*args, **kwargs)

    def _after_enter_(self, *args, **kwargs) -> None:
        """Internal: call on_first_enter on current scene."""
        if self.current:
            self.current._on_scene_first_enter_(*args, **kwargs)

    # endregion

    def __contains__(self, key: str) -> bool:
        """Check if a scene is registered by name."""
        return key in self.__scene_classes

    def __len__(self) -> int:
        """Return the number of scenes in the stack."""
        return len(self.__scenes)


def register(cls=None, *, name: str = None):
    """
    Decorator for registering scene classes with the SceneManager.

    Usage:
        @register
        class MyScene(BaseScene): ...
    or:
        @register(name="custom_name")
        class MyScene(BaseScene): ...
    or:
        @register(BaseScene, name="custom_name")
    """

    def decorator(scene_cls):
        scene_name = name or scene_cls.__name__
        SceneManager().register(scene_cls, scene_name)
        return scene_cls

    if cls is None:
        return decorator
    return decorator(cls)
