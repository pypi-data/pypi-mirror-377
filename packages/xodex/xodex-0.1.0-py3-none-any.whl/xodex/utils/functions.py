import os
import PIL
import PIL.Image
import json
from typing import Tuple, Union,overload

import pygame
from pygame import Color,Surface
# from xodex.objects.image import Image

# --- GAME WINDOW ---
# region Window


def set_icon(iconfile):
    """Set Game Window Icon"""
    gameicon = pygame.image.load(iconfile)
    pygame.display.set_icon(gameicon)


def set_title(string):
    """Set Game Window Title"""
    pygame.display.set_caption(string)


def exit_game():
    """Quit Game"""
    pygame.quit()
    raise SystemExit

  
def quit():
    """Quit Game"""
    pygame.quit()
    raise SystemExit

# endregion Window


# --- FILE UTILITIES ---
# region File Utils


def loadsound(filename: str) -> pygame.mixer.Sound:
    """loadsound"""

    class NoneSound:
        """NoneSound"""

        def play(self):
            """play"""

    sound = NoneSound()
    if not pygame.mixer.get_init():
        return sound

    if os.path.isfile(filename):
        sound = pygame.mixer.Sound(filename)
    return sound


def loadimage(filename: str,surface=True, scale: int = 1, colorkey: Color = None) -> Surface:
    """
    Load an image with error handling and optional scaling.

    Args:
        image_path (str): Path to the image file
        scale (Tuple[int, int], optional): Target size to scale the image to

    Returns:
        pygame.Surface: Loaded and optionally scaled image
    Raises:
        FileNotFoundError: If the image file doesn't exist
    """

    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Image file not found: {filename}")
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale_by(image, scale)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image # if surface else Image(image)
    except pygame.error as e:
        print(f"Error loading image {filename}: {e}")
        return Surface((100, 100)) # if surface else Image(Surface((0,0)))


def loadgif(filename: str,surface=True) -> list[Surface]:
    """loadgif"""

    if not os.path.isfile(filename):
        raise FileNotFoundError(f"Image file not found: {filename}")

    frames: list[Surface] = []

    image = PIL.Image.open(filename)
    pal = image.getpalette()
    base_palette: list[int] = []
    for i in range(0, len(pal), 3):
        rgb = pal[i : i + 3]
        base_palette.append(rgb)

    all_tiles = []

    try:
        while 1:
            if not image.tile:
                image.seek(0)
            if image.tile:
                all_tiles.append(image.tile[0][3][0])
            image.seek(image.tell() + 1)
    except EOFError:
        image.seek(0)

    all_tiles = tuple(set(all_tiles))

    try:
        while 1:
            try:
                duration: float = image.info["duration"]
            except:
                duration = 100

            duration *= 0.001  # convert to milliseconds!
            cons = False

            x0, y0, x1, y1 = (0, 0) + image.size
            if image.tile:
                tile = image.tile
            else:
                image.seek(0)
                tile = image.tile
            if len(tile) > 0:
                x0, y0, x1, y1 = tile[0][1]

            if all_tiles:
                if all_tiles in ((6,), (7,)):
                    cons = True
                    pal = image.getpalette()
                    palette = []
                    for i in range(0, len(pal), 3):
                        rgb = pal[i : i + 3]
                        palette.append(rgb)
                elif all_tiles in ((7, 8), (8, 7)):
                    pal = image.getpalette()
                    palette = []
                    for i in range(0, len(pal), 3):
                        rgb = pal[i : i + 3]
                        palette.append(rgb)
                else:
                    palette = base_palette
            else:
                palette = base_palette

            pi = pygame.image.frombytes(image.tostring(), image.size, image.mode)
            pi.set_palette(palette)
            if "transparency" in image.info:
                pi.set_colorkey(image.info["transparency"])
            pi2 = pygame.Surface(image.size, pygame.SRCALPHA)
            if cons:
                for i in frames:
                    pi2.blit(i[0], (0, 0))
            pi2.blit(pi, (x0, y0), (x0, y0, x1 - x0, y1 - y0))
            if surface:
                frames.append(pi2)
            else:
                frames.append(Image(pi2))
            image.seek(image.tell() + 1)
    except EOFError:
        pass

    return frames


def loadimages(path: str,surface=True, sort=True):
    """load images in a directory"""
    images: list[Surface] = []
    list_dir = sorted(os.listdir(path)) if sort else os.listdir(path)
    for img_name in list_dir:
        img_path = os.path.join(path, img_name)
        images.append(loadimage(img_path,surface))
    return images


def loadmap(filename: str) -> dict:
    """loadmap"""
    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Map file not found: {filename}")
        with open(filename, "r+", encoding="utf-8") as f:
            _map: dict = json.load(f)
        return _map
    except OSError as e:
        print(f"Error loading tile map {filename}: {e}")
        return {}

def splitsheet(sheet: Union[str, Surface],frame_size: tuple[int,int] = (64, 80),num_frames: int = None):
    """frames"""

    if isinstance(sheet, str):
        sheet = loadimage(sheet)
    elif isinstance(sheet, Surface):
        sheet = sheet

    frames: list = []
    sheet_width, sheet_height =sheet.get_size()

    cols = sheet_width // frame_size[0]
    rows = sheet_height // frame_size[1]
    count = 0

    for y in range(rows):
            for x in range(cols):
                if num_frames is not None and count >= num_frames:
                    break
                rect = pygame.Rect(
                    x * frame_size[0],
                    y * frame_size[1],
                    frame_size[0],
                    frame_size[1],
                )
                frame = sheet.subsurface(rect).copy()
                frames.append(frame)
                count += 1
            if num_frames is not None and count >= num_frames:
                break
    return frames

def fadescreen(screen: pygame.Surface, fade_speed: int = 5) -> None:
    """Create a fade-to-black effect on the screen."""
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 255, fade_speed):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)


# endregion File Utils

# --- INPUTS  ---
# region Inputs

def mouse_x():
    """Return mouse X position"""
    return get_mouse_x()


def mouse_y():
    """Return mouse Y position"""
    return get_mouse_y()

def get_mouse_pos():
    """returns mouse X and Y position"""
    return pygame.mouse.get_pos()


def get_mouse_x():
    """returns mouse X position"""
    return get_mouse_pos()[0]


def get_mouse_y():
    """returns mouse Y position"""
    return get_mouse_pos()[1]


@overload
def set_mouse_pos(x: float, y: float):
    """set mouse X and Y position"""
    pygame.mouse.set_pos(x, y)


@overload
def set_mouse_pos(pos):
    """set mouse X and Y position"""
    pygame.mouse.set_pos(pos)

def mouse_pressed():
    """Return True if any mouse button is pressed else False"""
    pygame.event.clear()
    mouseState = pygame.mouse.get_pressed()
    return True in mouseState

def left_clicked():
    """Return True if mouse left button is pressed else False"""
    pygame.event.clear()
    mouseState = pygame.mouse.get_pressed()
    if mouseState[0]:
        return True
    else:
        return False
    
def right_clicked():
    """Return True if mouse right button is pressed else False"""
    pygame.event.clear()
    mouseState = pygame.mouse.get_pressed()
    if mouseState[2]:
        return True
    else:
        return False
    
def scroll_clicked():
    """Return True if mouse scroll button is pressed else False"""
    pygame.event.clear()
    mouseState = pygame.mouse.get_pressed()
    if mouseState[1]:
        return True
    else:
        return False


def key_pressed(keycheck=""):
  """key pressed"""

# endregion Inputs

def draw_text_centered(surface, text, font, color, center):
    """
    Draws text centered at the given position.

    surface:  The pygame.Surface to draw onto.
    text:     The text string to display.
    font:     The pygame.Font object.
    color:    The color of the text (tuple).
    center:   The (x, y) position to center the text on.
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, text_rect)

def check_collision(rect1: pygame.Rect, rect2: pygame.Rect, buffer: int = 0) -> bool:
    """
    Check for collision between two rectangles with an optional buffer.

    Args:
        rect1 (pygame.Rect): First rectangle
        rect2 (pygame.Rect): Second rectangle
        buffer (int): Additional buffer zone around rectangles

    Returns:
        bool: True if collision detected, False otherwise
    """
    rect1_buffered = rect1.inflate(buffer, buffer)
    rect2_buffered = rect2.inflate(buffer, buffer)
    return rect1_buffered.colliderect(rect2_buffered)


def fade_screen(screen: pygame.Surface, fade_speed: int = 5) -> None:
    """Create a fade-to-black effect on the screen."""
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 255, fade_speed):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)


def render_text(
    screen: pygame.Surface,
    text: str,
    pos: Tuple[int, int],
    font_size: int = 24,
    color: Tuple[int, int, int] = (255, 255, 255),
) -> None:
    """
    Render text on the screen with a specified font size and color.

    Args:
        screen (pygame.Surface): The game screen surface
        text (str): Text to render
        pos (Tuple[int, int]): Position to render the text (x, y)
        font_size (int): Size of the font
        color (Tuple[int, int, int]): Color of the text in RGB
    """
    try:
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, pos)
    except pygame.error as e:
        print(f"Error rendering text: {e}")


def keep_in_bounds(
    rect: pygame.Rect, screen_width: int, screen_height: int
) -> pygame.Rect:
    """
    Keep a rectangle within screen boundaries.

    Args:
        rect (pygame.Rect): Rectangle to constrain
        screen_width (int): Width of the screen
        screen_height (int): Height of the screen
    Returns:
        pygame.Rect: Constrained rectangle
    """
    if rect.left < 0:
        rect.left = 0
    if rect.right > screen_width:
        rect.right = screen_width
    if rect.top < 0:
        rect.top = 0
    if rect.bottom > screen_height:
        rect.bottom = screen_height
    return rect

