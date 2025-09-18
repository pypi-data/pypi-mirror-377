"""Image

A wrapper for pygame.Surface that provides additional image manipulation
and drawing utilities, such as scaling, flipping, blurring, color swapping,
and rotation. Integrates with the DrawableObject interface for rendering.
"""

from typing import Tuple, Union

from pygame import Surface, Color
import PIL.ImageFilter
import PIL.ImageOps
import PIL.Image
import pygame

from xodex.objects.objects import DrawableObject
from xodex.utils.functions import loadimage


class Image(DrawableObject):
    """
    Image wrapper for pygame.Surface with utility methods.

    Args:
        image (Union[str, Surface], optional): Path to image file or a pygame.Surface.
        pos (Tuple[int, int], optional): Initial position (x, y) of the image.

    Attributes:
        _image (Surface): The underlying pygame surface.
        _img_rect (pygame.Rect): The rectangle representing the image's position and size.
    """

    def __init__(
        self,
        image: Union[str, Surface] = None,
        pos: Tuple[int, int] = (0, 0),
        alpha: int = None,
        colorkey: Color = None,
    ) -> None:
        """
        Initialize the Image.

        Args:
            image: Path to image file or pygame.Surface.
            pos: Initial (x, y) position.
            alpha: Optional alpha value (0-255).
            colorkey: Optional color key for transparency.
        """
        if isinstance(image, str):
            self._image = loadimage(image)
        elif isinstance(image, Surface):
            self._image = image.copy()
        else:
            raise ValueError("Image must be initialized with a file path or pygame.Surface.")

        if alpha is not None:
            self._image.set_alpha(alpha)
        if colorkey is not None:
            self._image.set_colorkey(colorkey)

        self._img_rect = self._image.get_rect()
        self._img_rect.x, self._img_rect.y = pos

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._image})>"

    def __copy__(self) -> "Image":
        return Image(self._image.copy(), self.position)

    def __deepcopy__(self, memo) -> "Image":
        return Image(self._image.copy(), self.position)

    @property
    def image(self) -> Surface:
        """Return the underlying pygame.Surface."""
        return self._image

    @property
    def rect(self) -> pygame.Rect:
        """Get or Set the rect of the image."""
        return self._img_rect

    @rect.setter
    def rect(self, new_rect: pygame.Rect) -> None:
        self._img_rect = new_rect

    @property
    def position(self) -> Tuple[int, int]:
        """Get or Set the (x, y) position of the image."""
        return (self._img_rect.x, self._img_rect.y)

    @position.setter
    def position(self, pos: Tuple[int, int]):
        self._img_rect.x, self._img_rect.y = pos

    def pos(self, pos: Tuple[int, int]):
        """Set the (x, y) position."""
        self._img_rect.x, self._img_rect.y = pos

    def size(self) -> Tuple[int, int]:
        """Return the (width, height) of the image."""
        return self._img_rect.size

    @classmethod
    async def async_load(
        cls, path: str, pos: Tuple[int, int] = (0, 0), alpha: int = None, colorkey: Color = None
    ) -> "Image":
        """
        Asynchronously load an image from disk.

        Args:
            path (str): Path to the image file.
            pos (Tuple[int, int]): Initial position.
            alpha (int): Optional alpha value.
            colorkey (Color): Optional color key.

        Returns:
            Image: Loaded Image instance.
        """

    def scale(self, x: float, y: float) -> "Image":
        """
        Scale the image to (x, y) size.

        Args:
            x (float): New width.
            y (float): New height.

        Returns:
            Image: Self for chaining.
        """
        self._image = pygame.transform.scale(self._image, (int(x), int(y)))
        topleft = self._img_rect.topleft
        self._img_rect = self._image.get_rect()
        self._img_rect.topleft = topleft
        return self

    def smoothscale(self, x: float, y: float) -> "Image":
        """
        Smoothly scale the image to (x, y) size.

        Args:
            x (float): New width.
            y (float): New height.

        Returns:
            Image: Self for chaining.
        """
        self._image = pygame.transform.smoothscale(self._image, (int(x), int(y)))
        topleft = self._img_rect.topleft
        self._img_rect = self._image.get_rect()
        self._img_rect.topleft = topleft
        return self

    def flip(self, flip_x: bool, flip_y: bool) -> "Image":
        """
        Flip the image horizontally and/or vertically.

        Args:
            flip_x (bool): Flip horizontally.
            flip_y (bool): Flip vertically.

        Returns:
            Image: Self for chaining.
        """
        self._image = pygame.transform.flip(self._image, flip_x, flip_y)
        topleft = self._img_rect.topleft
        self._img_rect = self._image.get_rect()
        self._img_rect.topleft = topleft
        return self

    def blur(self, blur_count: float = 5) -> "Image":
        """
        Apply a Gaussian blur to the image.

        Args:
            blur_count (float): Blur radius.

        Returns:
            Image: Self for chaining.
        """
        impil = PIL.Image.frombytes("RGBA", self._img_rect.size, pygame.image.tobytes(self._image, "RGBA"))
        impil = impil.filter(PIL.ImageFilter.GaussianBlur(radius=blur_count))
        self._image = pygame.image.frombytes(impil.tobytes(), impil.size, "RGBA").convert()
        return self

    def crop(self, rect: pygame.Rect) -> "Image":
        """
        Crop the image to the given rectangle.

        Args:
            rect (pygame.Rect): Rectangle to crop.

        Returns:
            Image: New cropped Image.
        """
        cropped_surface = self._image.subsurface(rect).copy()
        return Image(cropped_surface, (rect.x, rect.y))

    def subimage(self, x: int, y: int, w: int, h: int) -> "Image":
        """
        Extract a subimage from the image.

        Args:
            x, y: Top-left corner.
            w, h: Width and height.

        Returns:
            Image: New subimage.
        """
        rect = pygame.Rect(x, y, w, h)
        return self.crop(rect)

    def swap_color(self, from_color: Color, to_color: Color) -> "Image":
        """
        Replace all pixels of a given color with another color.

        Args:
            from_color (Color): Color to replace.
            to_color (Color): Replacement color.

        Returns:
            Image: Self for chaining.
        """
        arr = pygame.surfarray.pixels3d(self._image)
        r1, g1, b1 = from_color.r, from_color.g, from_color.b
        r2, g2, b2 = to_color.r, to_color.g, to_color.b
        mask = (arr[:, :, 0] == r1) & (arr[:, :, 1] == g1) & (arr[:, :, 2] == b1)
        arr[:, :, 0][mask] = r2
        arr[:, :, 1][mask] = g2
        arr[:, :, 2][mask] = b2
        del arr
        return self

    def tint(self, color: Color, alpha: int = 128) -> "Image":
        """
        Tint the image with a color.

        Args:
            color (Color): Tint color.
            alpha (int): Alpha value for blending.

        Returns:
            Image: Self for chaining.
        """
        tint_surface = pygame.Surface(self._image.get_size(), pygame.SRCALPHA)
        tint_surface.fill((*color, alpha))
        self._image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return self

    def rotate(self, angle: float) -> "Image":
        """
        Rotate the image by a given angle.

        Args:
            angle (float): Angle in degrees.

        Returns:
            Image: Self for chaining.
        """
        self._image = pygame.transform.rotate(self._image, angle)
        topleft = self._img_rect.topleft
        self._img_rect = self._image.get_rect()
        self._img_rect.topleft = topleft
        return self

    def set_alpha(self, alpha: int) -> "Image":
        """
        Set the alpha transparency of the image.

        Args:
            alpha (int): Alpha value (0-255).

        Returns:
            Image: Self for chaining.
        """
        self._image.set_alpha(alpha)
        return self

    def set_colorkey(self, colorkey: Color) -> "Image":
        """
        Set the color key (transparent color) for the image.

        Args:
            colorkey (Color): Color to be transparent.

        Returns:
            Image: Self for chaining.
        """
        self._image.set_colorkey(colorkey)
        return self

    def get_pixel(self, x: int, y: int) -> Color:
        """
        Get the color of a pixel.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            Color: The color at (x, y).
        """
        return self._image.get_at((x, y))

    def set_pixel(self, x: int, y: int, color: Color):
        """
        Set the color of a pixel.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            color (Color): Color to set.
        """
        self._image.set_at((x, y), color)

    def save(self, filename: str):
        """
        Save the image to a file.

        Args:
            filename (str): Path to save the image.
        """
        pygame.image.save(self._image, filename)

    def filter_grayscale(self) -> "Image":
        """
        Convert the image to grayscale.

        Returns:
            Image: Self for chaining.
        """
        pil_img = PIL.Image.frombytes("RGBA", self._img_rect.size, pygame.image.tobytes(self._image, "RGBA"))
        pil_img = PIL.ImageOps.grayscale(pil_img).convert("RGBA")
        self._image = pygame.image.frombytes(pil_img.tobytes(), pil_img.size, "RGBA").convert()
        return self

    def filter_invert(self) -> "Image":
        """
        Invert the image colors.

        Returns:
            Image: Self for chaining.
        """
        pil_img = PIL.Image.frombytes("RGBA", self._img_rect.size, pygame.image.tobytes(self._image, "RGBA"))
        pil_img = PIL.ImageOps.invert(pil_img.convert("RGB")).convert("RGBA")
        self._image = pygame.image.frombytes(pil_img.tobytes(), pil_img.size, "RGBA").convert()
        return self

    def filter_sharpen(self) -> "Image":
        """
        Sharpen the image.

        Returns:
            Image: Self for chaining.
        """
        pil_img = PIL.Image.frombytes("RGBA", self._img_rect.size, pygame.image.tobytes(self._image, "RGBA"))
        pil_img = pil_img.filter(PIL.ImageFilter.SHARPEN)
        self._image = pygame.image.frombytes(pil_img.tobytes(), pil_img.size, "RGBA").convert()
        return self

    def filter_edge_enhance(self) -> "Image":
        """
        Enhance edges in the image.

        Returns:
            Image: Self for chaining.
        """
        pil_img = PIL.Image.frombytes("RGBA", self._img_rect.size, pygame.image.tobytes(self._image, "RGBA"))
        pil_img = pil_img.filter(PIL.ImageFilter.EDGE_ENHANCE)
        self._image = pygame.image.frombytes(pil_img.tobytes(), pil_img.size, "RGBA").convert()
        return self

    def perform_draw(self, surface: Surface, *args, **kwargs) -> None:
        """
        Draw the image onto a surface.

        Args:
            surface (Surface): The target surface.
        """
        surface.blit(self.image, self._img_rect)


class MovingImage(Image):
    """
    Image that moves automatically within window bounds.

    Args:
        image: Path or Surface.
        pos: Initial position.
        win_width: Window width.
        win_height: Window height.
        speed: Initial speed.

    Features:
    - Bounces off window edges.
    - Supports toggling movement in X/Y.
    - Speed and direction control.
    """

    def __init__(
        self, image: Union[str, Surface], pos: Tuple[int, int], win_width: int, win_height: int, speed: int = 3
    ):
        super().__init__(image, pos)
        self.move_x = True
        self.move_y = True
        self.vel_x = speed
        self.vel_y = speed
        self.win_width = win_width
        self.win_height = win_height

    def perform_draw(self, surface, *args, **kwargs):
        # Move and bounce off edges
        if self.move_x:
            self._img_rect.x += self.vel_x
            if self._img_rect.left < 0 or self._img_rect.right > self.win_width:
                self.vel_x = -self.vel_x
                self._img_rect.x += self.vel_x
        if self.move_y:
            self._img_rect.y += self.vel_y
            if self._img_rect.top < 0 or self._img_rect.bottom > self.win_height:
                self.vel_y = -self.vel_y
                self._img_rect.y += self.vel_y
        return super().perform_draw(surface, *args, **kwargs)

    @property
    def rect(self):
        return self._img_rect

    @property
    def allow_x(self):
        """Allow X Movement"""
        return self.move_x

    @allow_x.setter
    def allow_x(self, allow: bool):
        self.move_x = allow

    @property
    def speed_x(self):
        """X Movement Speed"""
        return self.vel_x

    @speed_x.setter
    def speed_x(self, speed: int):
        self.vel_x = speed

    @property
    def allow_y(self):
        """Allow Y Movement"""
        return self.move_y

    @allow_y.setter
    def allow_y(self, allow: bool):
        self.move_y = allow

    @property
    def speed_y(self):
        """Y Movement Speed"""
        return self.vel_y

    @speed_y.setter
    def speed_y(self, speed: int):
        self.vel_y = speed


class SpriteSheet(Image):
    """
    Image subclass for handling sprite sheets.

    Args:
        image: Path or Surface.
        frame_width: Width of each frame.
        frame_height: Height of each frame.

    Usage:
        sheet = SpriteSheet("spritesheet.png", 32, 32)
        frame = sheet.get_frame(0, 1)
    """

    def __init__(
        self, image: Union[str, Surface], frame_width: int, frame_height: int, pos: Tuple[int, int] = (0, 0), **kwargs
    ):
        super().__init__(image, pos, **kwargs)
        self.frame_width = frame_width
        self.frame_height = frame_height

    def get_frame(self, col: int, row: int) -> Image:
        """
        Extract a frame from the sprite sheet.

        Args:
            col: Column index.
            row: Row index.

        Returns:
            Image: The extracted frame as an Image.
        """
        x = col * self.frame_width
        y = row * self.frame_height
        rect = pygame.Rect(x, y, self.frame_width, self.frame_height)
        return self.crop(rect)

    def get_all_frames(self) -> list:
        """
        Extract all frames from the sprite sheet.

        Returns:
            list: List of Image frames.
        """
        frames = []
        sheet_width, sheet_height = self.size()
        for y in range(0, sheet_height, self.frame_height):
            for x in range(0, sheet_width, self.frame_width):
                rect = pygame.Rect(x, y, self.frame_width, self.frame_height)
                frames.append(self.crop(rect))
        return frames
