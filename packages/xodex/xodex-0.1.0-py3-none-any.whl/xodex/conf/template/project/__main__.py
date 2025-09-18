"""{{ project_name_upper }} project Main Game Loop"""

from xodex.game.game import Game

from . import objects
from . import scenes


if __name__ == "__main__":
    game = Game("{{ project_name }}")
    game.main_loop()
