"""
Xodex Game Engine - Game Core

This module defines the main game application class (`Game`) for the Xodex Pygame-based engine.
It provides the core game loop, window and display management, scene and object registration,
event handling, and robust configuration reloading.

Key Features:
- Main game loop (sync and async) with update/draw hooks.
- Dynamic (re)configuration and hot-reloading support.
- Scene and object module auto-registration.
- Window management: resize, fullscreen, caption, icon, screenshot.
- Debug overlay and FPS display.
- Clean exit and restart handling.
- Extensible via user-defined scenes and objects.
- Detailed logging and error handling.

Classes:
    - Game: The main singleton game application class.

Functions:
    - run(project=None): Entry point to start the game loop.

Typical usage:
    from xodex.game import run
    run("mygame")

Author: djoezeke
License: See LICENSE file.
"""

import os
import sys
import time
import logging
from importlib import import_module

import pygame
from pygame.event import Event

from xodex.conf import settings
from xodex.core.singleton import Singleton
from xodex.scenes.manager import SceneManager

# from xodex.core.localization import localize


class Game(Singleton):
    """
    Main game application class for Xodex.

    This singleton manages the core game loop, window/display, scene and object
    registration, and configuration. It provides both synchronous and asynchronous
    main loops, dynamic (re)configuration, and robust error handling.

    Features:
        - Scene and object auto-registration from user modules.
        - Main game loop with update/draw hooks.
        - Pause, resume, and debug overlay.
        - Window management: resize, fullscreen, caption, icon, screenshot.
        - FPS limiting and display.
        - Async main loop support.
        - Custom event handler injection.
        - Clean exit and restart.
        - Hot-reloading and dynamic setup.
        - Detailed logging and error handling.

    Attributes:
        ready (bool): True if both objects and scenes are registered.
        objects_ready (bool): True if user objects module is loaded.
        scenes_ready (bool): True if user scenes module is loaded.
        _size (tuple): Window size.
        _caption (str): Window title.
        _icon (str): Path to window icon.
        _fps (int): Target frames per second.
        _debug (bool): Debug mode flag.
        _fullscreen (bool): Fullscreen mode flag.
        _mainscene (str): Name of the main scene.
        _show_fps (bool): Show FPS overlay.
        _font (pygame.font.Font): Font for overlays.
        _debug_overlay (bool): Show debug overlay.
        _custom_event_handler (callable): Optional custom event handler.

    Methods:
        setup(on_success=None, on_failure=None): (Re)initialize configuration and modules.
        main_loop(): Start the main game loop.
        async_main_loop(): Start the async main game loop.
        set_caption(caption): Set window caption.
        set_icon(icon_path): Set window icon.
        toggle_fullscreen(): Toggle fullscreen mode.
        save_screenshot(filename=None): Save a screenshot.
        exit_game(): Cleanly exit the game.
        restart_game(): Restart the game process.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the Game singleton.

        Sets up the Pygame environment, loads initial settings, configures the window,
        and prepares the main scene. All key attributes are initialized from the
        current settings module.

        Args:
            **kwargs: Additional keyword arguments for future extensibility.
        """

        super().__init__()
        pygame.init()

        self._size = settings.WINDOW_SIZE
        self._caption = settings.TITLE
        self._icon = settings.ICON_PATH
        self._fps = settings.FPS
        self._debug = settings.DEBUG
        self._fullscreen = settings.FULLSCREEN
        self._mainscene = settings.MAIN_SCENE
        self._show_fps = settings.SHOW_FPS
        self._font = pygame.font.SysFont("Arial", 18)
        self._debug_overlay = False
        self._custom_event_handler = None

        flags = pygame.SCALED | pygame.RESIZABLE
        if self._fullscreen:
            flags |= pygame.FULLSCREEN
        self.__screen = pygame.display.set_mode(self._size, flags=flags)

        self.__clock = pygame.time.Clock()
        self.ready = self.objects_ready = self.scenes_ready = False

        pygame.display.set_caption(self._caption)
        if self._icon:
            self.set_icon(self._icon)

        scene = SceneManager().get_scene_class(self._mainscene)
        SceneManager().reset(scene=scene())

    # region Window/Display

    def set_caption(self, caption: str):
        """
        Set the window caption/title.

        Args:
            caption (str): The new window title.
        """
        self._caption = caption
        pygame.display.set_caption(caption)

    def set_icon(self, icon_path: str):
        """
        Set the window icon from a file.

        Args:
            icon_path (str): Path to the icon image file.
        """
        try:
            icon_surface = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_surface)
        except Exception as e:
            if self._debug:
                print(f"Failed to set icon: {e}")

    def toggle_fullscreen(self):
        """Toggle fullscreen/windowed mode."""
        self._fullscreen = not self._fullscreen
        flags = pygame.SCALED | pygame.RESIZABLE
        if self._fullscreen:
            flags |= pygame.FULLSCREEN
        self.__screen = pygame.display.set_mode(self._size, flags=flags)

    def save_screenshot(self, filename: str = None):
        """
        Save a screenshot of the current screen.

        Args:
            filename (str, optional): The filename to save the screenshot as.
                If not provided, a timestamped filename is generated.
        """
        filename = filename or f"screenshot_{int(time.time())}.png"
        pygame.image.save(self.__screen, filename)
        if self._debug:
            print(f"Screenshot saved to {filename}")

    # endregion

    # region Exit

    def __process_exit_events(self, event: Event) -> None:
        """
        Handle exit-related Pygame events (e.g., window close).

        Args:
            event (pygame.event.Event): The event to process.
        """
        if event.type == pygame.QUIT:
            self.exit_game()

    def exit_game(self) -> None:
        """Cleanly exit the game."""
        pygame.quit()
        raise SystemExit

    def restart_game(self):
        """Restart the game process."""
        pygame.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    # endregion

    def main_loop(self) -> None:
        """
        Start the main (synchronous) game loop.

        Handles event processing, logic updates, and drawing in a continuous loop.
        """
        while True:
            delta = self.__clock.tick(self._fps)
            self.__process_all_events()
            self.__process_all_logic(delta)
            self.__process_all_draw()

    async def async_main_loop(self):
        """
        Start the main asynchronous game loop.

        Handles event processing, logic updates, and drawing using async/await.
        Useful for games with asynchronous logic or networking.
        """
        import asyncio

        while True:
            delta = self.__clock.tick(self._fps)
            await self.__process_all_events()
            await self.__process_all_logic_async(delta)
            await self.__process_all_draw_async()
            await asyncio.sleep(0)

    def __process_all_events(self) -> None:
        """Process all Pygame events for the current frame, including scene and exit events."""
        for event in pygame.event.get():
            SceneManager().current.handle_scene(event)
            self.__process_exit_events(event)
            if event.type == pygame.VIDEORESIZE:
                self._on_resize(event.size)

    def __process_all_logic(self, delta: float) -> None:
        """
        Update the current scene's logic.

        Args:
            delta (float): Time elapsed since the last frame in milliseconds.
        """

        SceneManager().current.update_scene(delta)

    def __process_all_draw(self) -> None:
        """Draw the current scene and overlays to the screen."""
        self.__screen.fill((255, 55, 23))
        self.__screen.blit(SceneManager().current.draw_scene(), (0, 0))
        if self._debug:
            if self._show_fps:
                fps = self.__clock.get_fps()
                fps_surf = self._font.render(f"FPS: {fps:.1f}", True, (0, 0, 0))
                self.__screen.blit(fps_surf, (10, 10))
            if self._debug_overlay:
                self._draw_debug_overlay()
        pygame.display.flip()

    async def __process_all_logic_async(self, delta: float):
        """
        Asynchronously update the current scene's logic.

        Args:
            delta (float): Time elapsed since the last frame in milliseconds.
        """
        SceneManager().current.update_scene(delta)

    async def __process_all_draw_async(self):
        """Asynchronously draw the current scene and overlays to the screen."""
        self.__screen.fill((255, 55, 23))
        self.__screen.blit(SceneManager().current.draw_scene(), (0, 0))
        if self._debug:
            if self._show_fps:
                fps = self.__clock.get_fps()
                fps_surf = self._font.render(f"FPS: {fps:.1f}", True, (0, 0, 0))
                self.__screen.blit(fps_surf, (10, 10))
            if self._debug_overlay:
                self._draw_debug_overlay()
        pygame.display.flip()

    def _draw_debug_overlay(self):
        """Draw a debug information overlay (scene name, object count, etc.) on the screen."""
        info = [
            f"Scene: {type(SceneManager().current).__name__}",
            f"Objects: {len(getattr(SceneManager().current, '_objects', []))}",
        ]
        for i, line in enumerate(info):
            surf = self._font.render(line, True, (0, 0, 0))
            self.__screen.blit(surf, (10, 30 + i * 20))

    def _on_resize(self, size):
        """
        Handle window resize events and update the display surface.

        Args:
            size (tuple): The new window size as (width, height).
        """
        self._size = size
        flags = pygame.SCALED | pygame.RESIZABLE
        if self._fullscreen:
            flags |= pygame.FULLSCREEN
        self.__screen = pygame.display.set_mode(self._size, flags=flags)
        if self._debug:
            print(f"Window resized to: {self._size}")

    # endregion

    # region Private

    def setup(self, on_success=None, on_failure=None):
        """
        Load and (re)initialize game configuration, scenes, and objects.

        This method resets readiness flags and class attributes, reloads settings,
        and attempts to import user-defined objects and scenes modules. It is safe
        to call multiple times, and can be used for hot-reloading or testing.

        Args:
            on_success (callable, optional): Called after successful setup.
            on_failure (callable, optional): Called after failed setup.

        Features:
            - Resets and repopulates readiness flags and key attributes.
            - Reloads settings and updates window properties.
            - Dynamically imports user objects and scenes modules.
            - Logs detailed status for each step.
            - Supports optional callback hooks for success/failure.
        """
        # Reset readiness flags
        self.ready = False
        self.objects_ready = False
        self.scenes_ready = False

        from xodex.conf import settings

        # Reconfigure settings in case of changes
        try:
            settings.configure()
            # Repopulate key attributes from settings
            self._size = settings.WINDOW_SIZE
            self._caption = settings.TITLE
            self._icon = settings.ICON_PATH
            self._fps = settings.FPS
            self._debug = settings.DEBUG
            self._fullscreen = settings.FULLSCREEN
            self._mainscene = settings.MAIN_SCENE
            self._show_fps = settings.SHOW_FPS

            # Update window properties
            flags = pygame.SCALED | pygame.RESIZABLE
            if self._fullscreen:
                flags |= pygame.FULLSCREEN
            self.__screen = pygame.display.set_mode(self._size, flags)
            pygame.display.set_caption(self._caption)
            if self._icon:
                self.set_icon(self._icon)

            # Import the main game module as specified in settings
            game_module = import_module(settings.PROJECT)

            # Import user objects module
            try:
                import_path = f"{game_module.__name__}.objects.objects"
                import_module(import_path)
                logging.info(f"Registered user objects from {import_path}")
                self.objects_ready = True
            except ImportError:
                logging.warning("No user objects module found.")
                self.objects_ready = False

            # Import user scenes module
            try:
                import_path = f"{game_module.__name__}.scenes.scenes"
                import_module(import_path)
                logging.info(f"Registered user scenes from {import_path}")
                self.scenes_ready = True
            except ImportError:
                logging.warning("No user scenes module found.")
                self.scenes_ready = False

            # Reset and initialize the main scene
            try:
                scene_class = SceneManager().get_scene_class(self._mainscene)
                SceneManager().reset(scene=scene_class())
                logging.info(f"Main scene '{self._mainscene}' loaded and reset.")
            except Exception as e:
                logging.warning(f"Failed to load main scene '{self._mainscene}': {e}")

            self.ready = self.objects_ready and self.scenes_ready
            if self.ready:
                logging.info("Game setup completed successfully.")
                if on_success:
                    on_success()
            else:
                logging.warning("Game setup incomplete: objects or scenes not ready.")
                if on_failure:
                    on_failure()
        except Exception as e:
            logging.warning(f"Game setup failed: {e}")
            self.ready = False
            self.objects_ready = False
            self.scenes_ready = False
            if on_failure:
                on_failure()


# endregion


def run(project=None, on_setup_success=None, on_setup_failure=None, async_mode=False):
    """
    Entry point to start the Xodex game loop.

    Args:
        project (str, optional): Python path to the game project (e.g., 'mygame').
            If provided, sets the XODEX_SETTINGS_MODULE environment variable.
        on_setup_success (callable, optional): Called after successful setup.
        on_setup_failure (callable, optional): Called after failed setup.
        async_mode (bool, optional): If True, runs the async main loop.

    Usage:
        run("mygame")
        run(project="mygame", async_mode=True)
    """

    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    if project:
        os.environ.setdefault("XODEX_SETTINGS_MODULE", f"{project}.settings")
    settings.configure()
    game = Game()
    if async_mode:
        import asyncio

        asyncio.run(game.async_main_loop())
    else:
        game.main_loop()
