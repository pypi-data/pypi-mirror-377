"""SpriteSheet and SheetAnimator

SpriteSheet: Utility for splitting a sprite sheet into frames.
SheetAnimator: Animator for sprite sheets.
"""

from typing import Tuple, Union, List, Optional, overload
import pygame
from xodex.objects.image import Image
from xodex.objects.animator import Animator
from xodex.utils.functions import splitsheet

class SpriteSheet:
    """
    Splits a sprite sheet image into individual frames.

    Args:
        image (Union[str, pygame.Surface]): Path or surface of the sprite sheet.
        frame_size (Tuple[int, int]): Size (width, height) of each frame.
        num_frames (Optional[int]): Number of frames to extract.

    Attributes:
        _frames (List[Image]): List of extracted frames as Image objects.
    """

    @overload
    def __init__(self, image: Union[str, pygame.Surface], frame_width: int = 64, frame_height: int = 80, num_frames: int = None): ...

    def __init__(self, image: Union[str, pygame.Surface], frame_size: Tuple[int, int] = (64, 80), num_frames: int = None):
        self._frames: List[Image] = [Image(img) for img in splitsheet(image, frame_size, num_frames)]

    def __call__(self):
        return iter(self._frames)

    def __iter__(self):
        return iter(self._frames)

    def __setitem__(self, frame_idx: int, frame: Image):
        if frame_idx >= len(self):
            raise IndexError("Frame index out of range.")
        self._frames[frame_idx] = frame

    def __getitem__(self, frame_idx: int) -> Image:
        if frame_idx >= len(self):
            raise IndexError("Frame index out of range.")
        return self._frames[frame_idx]

    def __delitem__(self, frame_idx: int):
        if frame_idx >= len(self):
            raise IndexError("Frame index out of range.")
        return self._frames.pop(frame_idx)

    def __contains__(self, frame: Image) -> bool:
        return frame in self._frames

    def __bool__(self) -> bool:
        return bool(self._frames)

    def __len__(self) -> int:
        return len(self._frames)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({len(self)} frames)>"

    def get_frame(self, i: int) -> Image:
        """Get frame at index (wraps around if out of range)."""
        return self.frames()[i % len(self.frames())]

    def addframe(
        self,
        sheet: Union[str, pygame.Surface],
        frame_width: int = 64,
        frame_height: int = 80,
        num_frames: int = 1,
    ):
        """
        Add frames from another sheet to this sprite sheet.

        Args:
            sheet (Union[str, pygame.Surface]): Source sheet.
            frame_width (int): Frame width.
            frame_height (int): Frame height.
            num_frames (int): Number of frames to add.
        """
        new_sheet = SpriteSheet(sheet, (frame_width, frame_height), num_frames)
        frames = new_sheet.frames()
        self._frames.extend(frames)

    def removeframe(self, frame_idx: int) -> Image:
        """
        Remove and return the frame at the given index.

        Args:
            frame_idx (int): Index of frame to remove.

        Returns:
            Image: The removed frame.
        """
        return self.frames().pop(frame_idx)

    def getframe(self, frame_idx: int) -> Image:
        """
        Get the frame at the given index.

        Args:
            frame_idx (int): Index of frame.

        Returns:
            Image: The frame at the index.
        """
        return self.frames()[frame_idx]

    def getimage(self, frame_idx: int) -> pygame.Surface:
        """
        Get the pygame.Surface of the frame at the given index.

        Args:
            frame_idx (int): Index of frame.

        Returns:
            pygame.Surface: The surface of the frame.
        """
        return self.images()[frame_idx]

    def frames(self) -> List[Image]:
        """Return all frames as Image objects."""
        return self._frames

    def images(self) -> List[pygame.Surface]:
        """Return all frames as pygame.Surface objects."""
        return [frame.image for frame in self._frames]

class SheetAnimator(Animator):
    """
    Animator for sprite sheets.

    Args:
        sheet (Union[str, pygame.Surface]): Sprite sheet image or path.
        frame_width (int): Width of each frame.
        frame_height (int): Height of each frame.
        num_frames (Optional[int]): Number of frames.
        frame_duration (int): Duration per frame in ms.
        loop (bool): Whether to loop animation.
        pingpong (bool): Whether to ping-pong animation.
        reverse (bool): Whether to play in reverse.
        on_finish (Optional[callable]): Callback on finish.
    """

    def __init__(
        self,
        sheet: Union[str, pygame.Surface],
        frame_width: int = 64,
        frame_height: int = 80,
        num_frames: int = None,
        frame_duration: int = 100,
        loop: bool = True,
        pingpong: bool = False,
        reverse: bool = False,
        on_finish: Optional[callable] = None,
        **kwargs
    ):
        super().__init__(
            SpriteSheet(sheet, (frame_width, frame_height), num_frames).frames(),
            frame_duration,
            loop,
            pingpong,
            reverse,
            on_finish,
            **kwargs
        )
