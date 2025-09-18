"""Scenes"""

from xodex.scenes.base_scene import BaseScene
from xodex.scenes.manager import SceneManager, register
from xodex.scenes.blur_scene import (
    BlurScene,
    BoxBlurScene,
    GaussianBlurScene,
    MaskedBlurScene,
    MotionBlurScene,
)

__all__ = (
    "Scene",
    "register",
    "BlurScene",
    "BlurScene",
    "SceneManager",
    "BoxBlurScene",
    "GaussianBlurScene",
    "MaskedBlurScene",
    "MotionBlurScene",
)


class Scene(BaseScene):
    """Scene"""
