"""Animator

Provides animation logic for a sequence of frames (Image or pygame.Surface).
Supports looping, ping-pong, reverse, and callbacks on finish.
"""

from typing import Callable, Optional, Tuple, List, Union
import pygame

from pygame import Surface

from xodex.objects.image import Image
from xodex.objects.objects import DrawableObject, EventfulObject, LogicalObject


class Animator(DrawableObject, EventfulObject, LogicalObject):
    """
    Handles frame-based animation logic.

    Features:
    - Async frame loading.
    - Loop, ping-pong, reverse, pause/resume.
    - Frame stepping, skipping, and speed scaling.
    - Frame event hooks (on frame, on loop, on pingpong, on finish).
    - State query methods.

    Args:
        frames (List[Surface|Image|str]): List of animation frames.
        frame_duration (int): Duration of each frame in ms.
        loop (bool): Whether to loop the animation.
        pingpong (bool): Whether to ping-pong the animation.
        reverse (bool): Whether to play in reverse.
        on_finish (Optional[Callable]): Callback when animation finishes.

    Attributes:
        _frames (List[Image]): Animation frames.
        _frame_duration (int): Duration per frame in ms.
        _current_frame (int): Current frame index.
        _time_accum (float): Accumulated time for frame switching.
        _loop (bool): Loop flag.
        _pingpong (bool): Ping-pong flag.
        _reverse (bool): Reverse flag.
        _on_finish (Optional[Callable]): Finish callback.
        _on_frame (Optional[Callable]): Frame change callback.
        _on_loop (Optional[Callable]): Loop callback.
        _on_pingpong (Optional[Callable]): Pingpong callback.
        _finished (bool): Animation finished flag.
        _paused (bool): Animation paused flag.
        _direction (int): Animation direction (1 or -1).
        _speed_scale (float): Speed scaling factor.
    """

    def __init__(
        self,
        frames: List[Union[Image, Surface, str]],
        frame_duration: int = 100,
        loop: bool = True,
        pingpong: bool = False,
        reverse: bool = False,
        on_finish: Optional[Callable] = None,
        on_frame: Optional[Callable] = None,
        on_loop: Optional[Callable] = None,
        on_pingpong: Optional[Callable] = None,
        **kwargs,
    ):
        self._frames: List[Image] = []
        for frame in frames:
            if isinstance(frame, Surface):
                self._frames.append(Image(frame))
            elif isinstance(frame, Image):
                self._frames.append(frame)
            elif isinstance(frame, str):
                self._frames.append(Image(frame))
            else:
                raise TypeError("Animator frames must be Image, Surface, or str.")

        self._frame_duration = frame_duration
        self._current_frame = 0
        self._time_accum = 0
        self._loop = loop
        self._pingpong = pingpong
        self._reverse = reverse
        self._on_finish = on_finish
        self._on_frame = on_frame
        self._on_loop = on_loop
        self._on_pingpong = on_pingpong
        self._finished = False
        self._paused = False
        self._direction = -1 if reverse else 1
        self._speed_scale = 1.0
        self._img_rect = self._frames[self._current_frame].rect

        position = kwargs.pop("pos", None)
        if position:
            self._img_rect.x = position[0]
            self._img_rect.y = position[1]

    @classmethod
    async def async_from_paths(cls, paths: List[str], **kwargs) -> "Animator":
        """
        Asynchronously load frames from file paths.

        Args:
            paths (List[str]): List of image file paths.
            **kwargs: Other Animator arguments.

        Returns:
            Animator: New Animator instance.
        """
        frames = []
        for path in paths:
            img = await Image.async_load(path)
            frames.append(img)
        return cls(frames, **kwargs)

    def __iter__(self):
        return iter(self._frames)

    def __contains__(self, frame: Image):
        return frame in self._frames

    def __bool__(self):
        return bool(self._frames)

    def __len__(self):
        """Return number of frames."""
        return len(self._frames)

    def __repr__(self):
        return f"<{self.__class__.__name__}({len(self)} frames)>"

    @property
    def rect(self) -> pygame.Rect:
        """Get the (x, y) position of the image."""
        return self._img_rect

    @rect.setter
    def rect(self, x: int, y: int, width: int, height: int):
        """Set the (x, y) position of the image."""
        self._img_rect = pygame.Rect(x, y, width, height)

    @property
    def position(self) -> Tuple[int, int]:
        """Get the (x, y) position of the image."""
        return (self._img_rect.x, self._img_rect.y)

    @position.setter
    def position(self, pos: Tuple[int, int]):
        """Set the (x, y) position of the image."""
        self._img_rect.x = pos[0]
        self._img_rect.y = pos[1]

    def reset(self):
        """Reset animation to start."""
        self._current_frame = 0 if self._direction == 1 else len(self._frames) - 1
        self._time_accum = 0
        self._finished = False
        self._paused = False

    def get_image(self) -> Optional[Image]:
        """Get the current frame's image."""
        if not self._frames:
            return None
        return self._frames[self._current_frame]

    def is_finished(self) -> bool:
        """Check if animation is finished."""
        return self._finished

    def is_paused(self) -> bool:
        """Check if animation is paused."""
        return self._paused

    def set_reverse(self, reverse: bool = True):
        """Set animation to play in reverse."""
        self._reverse = reverse
        self._direction = -1 if reverse else 1

    def set_loop(self, loop: bool = True):
        """Enable or disable looping."""
        self._loop = loop

    def set_pingpong(self, pingpong: bool = True):
        """Enable or disable ping-pong mode."""
        self._pingpong = pingpong

    def set_on_finish(self, callback: Callable):
        """Set callback for when animation finishes."""
        self._on_finish = callback

    def set_on_frame(self, callback: Callable):
        """Set callback for when frame changes."""
        self._on_frame = callback

    def set_on_loop(self, callback: Callable):
        """Set callback for when animation loops."""
        self._on_loop = callback

    def set_on_pingpong(self, callback: Callable):
        """Set callback for when pingpong direction changes."""
        self._on_pingpong = callback

    def set_frame_duration(self, duration: int):
        """Set duration per frame in ms."""
        self._frame_duration = duration

    def set_frame(self, frame_idx: int):
        """Set the current frame index."""
        if 0 <= frame_idx < len(self._frames):
            self._current_frame = frame_idx

    def get_frame(self) -> int:
        """Get the current frame index."""
        return self._current_frame

    def get_num_frames(self) -> int:
        """Get the total number of frames."""
        return len(self._frames)

    def set_frames(self, frames: List[Union[Image, Surface]]):
        """Set the animation frames and reset."""
        _frames = []
        for frame in frames:
            if isinstance(frame, Surface):
                _frames.append(Image(frame))
            elif isinstance(frame, Image):
                _frames.append(frame)
            else:
                pass
        self._frames = _frames
        self.reset()

    def set_speed(self, fps: int):
        """Set animation speed in frames per second."""
        self._frame_duration = int(1000 / fps)

    def set_speed_scale(self, scale: float):
        """Set a speed scaling factor (e.g., 0.5 for half speed, 2.0 for double speed)."""
        self._speed_scale = max(0.01, scale)

    def play(self):
        """Resume animation."""
        self._finished = False
        self._paused = False

    def pause(self):
        """Pause animation."""
        self._paused = True

    def stop(self):
        """Pause and finish animation."""
        self._finished = True
        self._paused = True

    def goto_and_play(self, frame_idx: int):
        """Jump to frame and play."""
        self.set_frame(frame_idx)
        self.play()

    def goto_and_stop(self, frame_idx: int):
        """Jump to frame and stop."""
        self.set_frame(frame_idx)
        self.stop()

    def step(self, steps: int = 1):
        """Step forward or backward by a number of frames."""
        self._current_frame = (self._current_frame + steps * self._direction) % len(self._frames)

    def skip_to_end(self):
        """Skip to the last frame."""
        self._current_frame = len(self._frames) - 1 if self._direction == 1 else 0

    def toggle_reverse(self):
        """Toggle reverse/forward playback."""
        self.set_reverse(not self._reverse)

    def perform_draw(self, surface: Surface, *args, **kwargs) -> None:
        """
        Draw the current frame onto a surface.

        Args:
            surface (Surface): The target surface.
        """
        image = self.get_image()
        image.rect = self.rect
        image.perform_draw(surface)

    def perform_update(self, deltatime: float, *args, **kwargs) -> None:
        """
        Update the animation state.

        Args:
            deltatime (float): Time since last update in ms.
        """
        if self._finished or self._paused or len(self._frames) == 0:
            return
        self._time_accum += deltatime * self._speed_scale
        frame_changed = False
        while self._time_accum >= self._frame_duration:
            self._time_accum -= self._frame_duration
            prev_frame = self._current_frame
            self._current_frame += self._direction
            frame_changed = True
            if self._pingpong:
                if self._current_frame >= len(self._frames):
                    self._current_frame = len(self._frames) - 2
                    self._direction = -1
                    if self._on_pingpong:
                        self._on_pingpong()
                elif self._current_frame < 0:
                    self._current_frame = 1
                    self._direction = 1
                    if self._on_pingpong:
                        self._on_pingpong()
            else:
                if self._current_frame >= len(self._frames) or self._current_frame < 0:
                    if self._loop:
                        if self._on_loop:
                            self._on_loop()
                        self._current_frame = 0 if self._direction == 1 else len(self._frames) - 1
                    else:
                        self._finished = True
                        if self._on_finish:
                            self._on_finish()
                        self._current_frame = max(0, min(self._current_frame, len(self._frames) - 1))
            if frame_changed and self._on_frame:
                self._on_frame(self._current_frame)

    def handle_event(self, event: pygame.event.Event, *args, **kwargs) -> None:
        """Handle pygame events (stub for extension)."""

    # --- Additional state query methods ---
    def is_looping(self) -> bool:
        """Return True if looping is enabled."""
        return self._loop

    def is_pingpong(self) -> bool:
        """Return True if pingpong is enabled."""
        return self._pingpong

    def is_reversed(self) -> bool:
        """Return True if reverse is enabled."""
        return self._reverse

    def is_playing(self) -> bool:
        """Return True if animation is playing (not paused or finished)."""
        return not self._paused and not self._finished


class Anime(DrawableObject, LogicalObject, EventfulObject):  # dino
    """Anime"""

    def __init__(self, animation: dict[str, Animator] = None, default: str = None):
        self._animations: dict[str, Animator] = {}
        self._current: str = None

        if animation:
            if isinstance(animation, dict):
                self._animations.update(animation)
            else:
                raise TypeError
        if default:
            self._current = default

    def __str__(self):
        """Return a string representation of the Animator."""
        return f"<{self.__class__.__name__}>"

    def __repr__(self):
        """Return a string representation of the Animator."""
        return f"{self.__class__.__name__}()"

    @property
    def current(self) -> Animator:
        """Current Animator."""
        try:
            return self._animations[self._current]
        except KeyError:
            print("Current Animator is null")

    @current.setter
    def current(self, anime) -> str:
        """Current Animator."""
        if anime in self._animations:
            self._current = anime

    @property
    def animators(self):
        """Return Scen"""
        return self._animations

    @property  # flappy
    def rect(self) -> pygame.Rect:
        """Get or Set the rect of the anime."""
        return self.current.rect

    @rect.setter  # flappy
    def rect(self, new_rect: pygame.Rect):
        self.current.rect = new_rect

    @property
    def position(self) -> tuple[int, int]:
        """Get the (x, y) position of the anime."""
        return self.current.position

    @position.setter
    def position(self, pos: tuple[int, int]):
        self.current.position = pos

    def play(self, anime: str = None):
        """play"""
        if anime:
            self.current = anime

    def add(self, name: str, animator: Animator) -> None:
        """add"""
        self._animations[name] = animator

    def pop(self, name: str) -> None:
        """pop"""
        return self._animations.pop(name, None)

    def remove(self, name: str) -> None:
        """remove"""
        self.pop(name)

    def perform_draw(self, surface: pygame.Surface, *args, **kwargs) -> None:
        """
        Draw the current frame onto a surface.

        Args:
            surface (Surface): The target surface.
        """
        self.current.perform_draw(surface, *args, **kwargs)

    def perform_update(self, deltatime: float, *args, **kwargs) -> None:
        """
        Update the animation state.

        Args:
            deltatime (float): Time since last update in ms.
        """
        self.current.perform_update(deltatime, *args, **kwargs)

    def handle_event(self, event: pygame.event.Event, *args, **kwargs) -> None:
        """Handle pygame events (stub for extension)."""
        self.current.handle_event(event, *args, **kwargs)


class SpriteSheetAnimator(Animator):
    """
    Animator subclass for handling sprite sheets.

    Args:
        sheet (Image): The sprite sheet image.
        frame_width (int): Width of each frame.
        frame_height (int): Height of each frame.
        rows (int): Number of rows in the sheet.
        cols (int): Number of columns in the sheet.
        **kwargs: Other Animator arguments.

    Usage:
        sheet = Image("spritesheet.png")
        anim = SpriteSheetAnimator(sheet, 32, 32, rows=4, cols=4, frame_duration=80)
    """

    def __init__(self, sheet: Image, frame_width: int, frame_height: int, rows: int, cols: int, **kwargs):
        frames = []
        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frames.append(sheet.crop(rect))
        super().__init__(frames, **kwargs)


class MultiAnimator(Animator):
    """
    Animator subclass that can switch between multiple named animation sets.

    Usage:
        anims = {"walk": Animator([...]), "jump": Animator([...])}
        multi = MultiAnimator(anims, default="walk")
        multi.set_animation("jump")
    """

    def __init__(self, animations: dict[str, Animator], default: str = None):
        self._animations = animations
        self._current = default or next(iter(animations))
        super().__init__(
            self._animations[self._current]._frames, frame_duration=self._animations[self._current]._frame_duration
        )

    def set_animation(self, name: str):
        """Switch to a different animation set by name."""
        if name in self._animations:
            self._current = name
            self.set_frames(self._animations[name]._frames)
            self.set_frame_duration(self._animations[name]._frame_duration)

    @property
    def current(self) -> Animator:
        """Return the current Animator."""
        return self._animations[self._current]
