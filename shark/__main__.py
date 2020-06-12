from pathlib import Path
from .mainwindow import App


def run():
    game = App(Path.cwd())
    game.run()


if __name__ == "__main__":
    run()
