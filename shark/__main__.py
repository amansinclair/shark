from pathlib import Path
from .mainwindow import MainWindow


def run():
    game = MainWindow(Path.cwd())
    game.run()


if __name__ == "__main__":
    run()
