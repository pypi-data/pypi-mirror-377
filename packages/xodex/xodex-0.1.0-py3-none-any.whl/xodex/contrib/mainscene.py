"""Main Game Scene"""

from typing import Generator

from xodex.scenes.base_scene import BaseScene

# from xodex.core.localization import localize


class XodexMainScene(BaseScene):
    """XodexMainScene"""

    def __init__(self):
        super().__init__()

    # region Private

    def _generate_objects_(self) -> Generator:
        text = self.get_object(object_name="XodexText")

        yield text("Hello", (100, 100))
        yield text("Hello", (100, 150))
        yield text("Hello", (100, 200))

    # endregion

    # region Public

    # endregion
