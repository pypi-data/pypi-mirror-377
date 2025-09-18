import pygame
from xodex.core.localization import localize
from xodex.objects.objects import DrawableObject, EventfulObject, LogicalObject


class XodexText(DrawableObject):
    """Enhanced XodexText with customizable font, color, and dynamic updates."""

    def __init__(
        self,
        text: str,
        position: tuple[int, int] = (0, 0),
        font_name: str = "Arial",
        font_size: int = 30,
        color: tuple[int, int, int] = (255, 0, 0),
        bold: bool = False,
        italic: bool = False,
        antialias: bool = True,
        alpha: int = 255,
    ):
        super().__init__()
        pygame.font.init()
        self._font_name = font_name
        self._font_size = font_size
        self._bold = bold
        self._italic = italic
        self._antialias = antialias
        self._color = color
        self._alpha = alpha
        self._position = position
        self._text = localize(text)
        self._font = pygame.font.SysFont(
            self._font_name, self._font_size, self._bold, self._italic
        )
        self._surface = None
        self._render_text()

    def __str__(self):
        """Return a string representation of the class."""
        return f"<{self.__class__.__name__}>"

    def _render_text(self):
        self._surface = self._font.render(self._text, self._antialias, self._color)
        if self._alpha < 255:
            self._surface.set_alpha(self._alpha)

    def perform_draw(self, surface, *args, **kwargs) -> None:
        surface.blit(self._surface, self._surface.get_rect(topleft=self._position))

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = localize(value)
        self._render_text()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value: tuple[int, int, int]):
        self._color = value
        self._render_text()

    def set_position(self, position: tuple[int, int]):
        self._position = position

    def set_font(
        self,
        font_name: str = None,
        font_size: int = None,
        bold: bool = None,
        italic: bool = None,
    ):
        if font_name is not None:
            self._font_name = font_name
        if font_size is not None:
            self._font_size = font_size
        if bold is not None:
            self._bold = bold
        if italic is not None:
            self._italic = italic
        self._font = pygame.font.SysFont(
            self._font_name, self._font_size, self._bold, self._italic
        )
        self._render_text()

    def set_alpha(self, alpha: int):
        self._alpha = max(0, min(255, alpha))
        self._render_text()
