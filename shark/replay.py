import pyglet
import json
from .level import LevelLoader
from .render import Renderer
from pathlib import Path


class Replayer(pyglet.window.Window):
    def __init__(self, app_path, log_file, speed=1, H=480, W=480, show_all=True):
        super().__init__(W, H, fullscreen=False)
        self.app_path = app_path
        self.level_loader = LevelLoader(app_path)
        self.render = Renderer(app_path)
        self.log = self.load_log(log_file)
        self.play()

    def load_log(self, log_path):
        with open(log_path, "r") as log_file:
            log = json.load(log_file)
        return log

    def play(self):
        self.level = self.level_loader[self.log["name"]]
        self.dt = self.log["total_time"] / self.log["n_updates"]
        self.events = self.log["events"]
        self.current_time = 0.0
