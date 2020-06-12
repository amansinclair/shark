from pathlib import Path
from .app import App


def run():
    game = App(Path.cwd())
    game.run()


if __name__ == "__main__":
    run()
