from abc import ABC
from typing import Callable, Optional, Literal
from PIL import Image, ImageFilter, ImageChops

import pygame
from pygame import Surface, time, image, Rect

from xodex.scenes.base_scene import BaseScene

__all__ = (
    "BlurScene",
    "GaussianBlurScene",
    "BoxBlurScene",
    "MotionBlurScene",
    "MaskedBlurScene",
)


class BlurScene(BaseScene, ABC):
    """
    Scene with animated blur effect.

    Features:
        - Supports multiple blur types (gaussian, box, motion, custom)
        - Adjustable blur region (full, rect, mask)
        - Async blur support
        - Pause/resume/toggle for blur effect
        - Event/callback hooks for blur start, progress, and complete

    Args:
        blur_surface: Surface to blur.
        blur_count: Blur intensity/steps.
        blur_duration: Duration of blur animation (seconds).
        blur_type: Type of blur ("gaussian", "box", "motion", "custom").
        blur_region: Optional region (rect) or mask to blur.
        on_blur_start: Callback when blur starts.
        on_blur_progress: Callback on blur progress.
        on_blur_complete: Callback when blur completes.

    Usage:
        scene = GaussianBlurScene(surface, blur_count=3, blur_duration=1.5)
    """

    def __init__(
        self,
        blur_surface: Surface,
        *args,
        blur_count: int = 1,
        blur_duration: float = 1.0,
        blur_type: Literal["gaussian", "box", "motion", "custom"] = "gaussian",
        blur_region: Optional[Rect] = None,
        blur_mask: Optional[Surface] = None,
        on_blur_start: Optional[Callable] = None,
        on_blur_progress: Optional[Callable[[float], None]] = None,
        on_blur_complete: Optional[Callable] = None,
        **kwargs,
    ) -> "BlurScene":
        super().__init__(*args, **kwargs)
        self._blur_count = blur_count
        self._blur_duration = blur_duration
        self._blur_type = blur_type
        self._blur_region = blur_region
        self._blur_mask = blur_mask
        self._blur_finished = False
        self._on_blur_start = on_blur_start
        self._on_blur_progress = on_blur_progress
        self._on_blur_complete = on_blur_complete
        self._blur_surface = blur_surface
        self._blur_paused = False
        self._blur_started = False

    def update_scene(self, deltatime: float, *args, **kwargs) -> None:
        """
        Update all objects in the scene, and animate blur if not finished.

        Args:
            deltatime (float): Time since last update (ms).
        """
        if not self._blur_finished and not self._blur_paused:
            if not self._blur_started and self._on_blur_start:
                self._on_blur_start()
                self._blur_started = True
            blur_time = time.get_ticks() / 1000
            min_blur = min(
                (blur_time - self._start_time) * self._blur_count / self._blur_duration,
                self._blur_count,
            )
            self._blur_surface = self.blur(min_blur)
            if self._on_blur_progress:
                self._on_blur_progress(min_blur / self._blur_count)
            self._blur_finished = min_blur == self._blur_count
            if self._blur_finished and self._on_blur_complete:
                self._on_blur_complete()
        super().update_scene(deltatime, *args, **kwargs)

    async def async_update_scene(self, deltatime: float, *args, **kwargs) -> None:
        """
        Async version of update_scene.
        """
        if not self._blur_finished and not self._blur_paused:
            blur_time = time.get_ticks() / 1000
            min_blur = min(
                (blur_time - self._start_time) * self._blur_count / self._blur_duration,
                self._blur_count,
            )
            self._blur_surface = await self.async_blur(min_blur)
            if self._on_blur_progress:
                self._on_blur_progress(min_blur / self._blur_count)
            self._blur_finished = min_blur == self._blur_count
            if self._blur_finished and self._on_blur_complete:
                self._on_blur_complete()
        await super().async_update_scene(deltatime, *args, **kwargs)

    def draw_scene(self, *args, **kwargs) -> pygame.Surface:
        """
        Draw the blurred surface and all objects to the scene surface.

        Returns:
            pygame.Surface: The updated scene surface.
        """
        self._screen.blit(self._blur_surface, self._screen.get_rect())
        self._objects.draw_object(self._screen, *args, **kwargs)
        return self._screen

    def reset_blur(self):
        """Restart the blur effect."""
        self._start_time = time.get_ticks() / 1000
        self._blur_finished = False
        self._blur_started = False

    def is_blur_finished(self) -> bool:
        """Return True if blurring finished."""
        return self._blur_finished

    def pause_blur(self):
        """Pause the blur animation."""
        self._blur_paused = True

    def resume_blur(self):
        """Resume the blur animation."""
        self._blur_paused = False

    def toggle_blur(self):
        """Toggle the blur animation pause state."""
        self._blur_paused = not self._blur_paused

    # region Private

    def blur(self, blur_count: int = 5) -> Surface:
        """
        Apply blur to the surface using the selected blur type.

        Args:
            blur_count: Blur intensity.

        Returns:
            Surface: Blurred surface.
        """
        mode = "RGBA"
        size = self._blur_surface.get_size()
        raw = image.tostring(self._blur_surface, mode)
        impil = Image.frombytes(mode, size, raw)

        if self._blur_region:
            # Only blur a region
            region = impil.crop(self._blur_region)
            region = self._apply_blur(region, blur_count)
            impil.paste(region, self._blur_region)
        elif self._blur_mask:
            # Only blur where mask is nonzero
            mask_img = Image.frombytes("L", self._blur_mask.get_size(), image.tostring(self._blur_mask, "L"))
            blurred = self._apply_blur(impil.copy(), blur_count)
            impil = Image.composite(blurred, impil, mask_img)
        else:
            impil = self._apply_blur(impil, blur_count)

        surf = image.fromstring(impil.tobytes(), impil.size, mode).convert()
        return surf

    async def async_blur(self, blur_count: int = 5) -> Surface:
        """
        Async version of blur.
        """
        return self.blur(blur_count)

    def _apply_blur(self, img: Image.Image, blur_count: int) -> Image.Image:
        """Apply the selected blur type to a PIL image."""
        if self._blur_type == "gaussian":
            return img.filter(ImageFilter.GaussianBlur(radius=blur_count))
        elif self._blur_type == "box":
            return img.filter(ImageFilter.BoxBlur(radius=blur_count))
        elif self._blur_type == "motion":
            # Simulate motion blur by blending shifted images
            result = img.copy()
            for i in range(1, int(blur_count) + 1):
                shifted = img.transform(img.size, Image.AFFINE, (1, 0, i, 0, 1, 0), resample=Image.BILINEAR)
                result = ImageChops.add(result, shifted, scale=2.0)
            return result
        elif self._blur_type == "custom":
            # User can override this method for custom blur
            return img
        else:
            return img

    # endregion


# --- Subclasses for different blur types ---


class GaussianBlurScene(BlurScene):
    """
    Scene with animated Gaussian blur effect.

    Usage:
        scene = GaussianBlurScene(surface, blur_count=3, blur_duration=1.5)
    """

    def __init__(self, blur_surface: Surface, *args, **kwargs):
        super().__init__(blur_surface, *args, blur_type="gaussian", **kwargs)


class BoxBlurScene(BlurScene):
    """
    Scene with animated Box blur effect.

    Usage:
        scene = BoxBlurScene(surface, blur_count=2, blur_duration=1.0)
    """

    def __init__(self, blur_surface: Surface, *args, **kwargs):
        super().__init__(blur_surface, *args, blur_type="box", **kwargs)


class MotionBlurScene(BlurScene):
    """
    Scene with animated Motion blur effect.

    Usage:
        scene = MotionBlurScene(surface, blur_count=4, blur_duration=2.0)
    """

    def __init__(self, blur_surface: Surface, *args, **kwargs):
        super().__init__(blur_surface, *args, blur_type="motion", **kwargs)


class MaskedBlurScene(BlurScene):
    """
    Scene with animated blur effect applied only to a mask or region.

    Usage:
        scene = MaskedBlurScene(surface, blur_mask=my_mask_surface, blur_count=3)
    """

    def __init__(self, blur_surface: Surface, *args, blur_mask: Surface = None, **kwargs):
        super().__init__(blur_surface, *args, blur_type="gaussian", blur_mask=blur_mask, **kwargs)
